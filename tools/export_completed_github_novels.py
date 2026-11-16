#!/usr/bin/env python3
"""Export unexpired, complete GitHub Actions novel artefacts into HF-ready ZIPs.

One ZIP is produced for each unique downloader book key (SHA-256 of source URL).
Each inner ZIP is directly accepted by Taiyou's Smart Bulk Upload after the
outer GitHub Actions export is extracted. Incomplete chapter batches are ignored.
The script performs read-only GitHub API calls; it does not fetch novel websites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import time
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED, BadZipFile

import requests

REPO = "RichardDaffern/Novel_Library"
CAMPAIGN_RUN_IDS = (
    43734388839, 43734393507, 43734398943,
    43734404117, 43734410920, 43734417289, 43819213500,
)
ARTIFACT_NAME = re.compile(r"^novel-([0-9]+)-([a-f0-9]{20})$")
MAX_ARTIFACT_BYTES = 140 * 1024 * 1024
MAX_INNER_ZIP_BYTES = 120 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 600 * 1024 * 1024
MAX_ENTRIES = 20000


def source_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]


def safe_title(title: str) -> str:
    clean = re.sub(r"[^\w .()\-]+", "_", title, flags=re.UNICODE)
    return re.sub(r"\s+", " ", clean).strip(" ._")[:85] or "Untitled"


def safe_member(name: str) -> bool:
    path = PurePosixPath(name.replace("\\", "/"))
    return not (
        path.is_absolute()
        or not path.parts
        or any(part in ("..", ".", "") for part in path.parts)
        or name.startswith("/")
    )


def index_registry(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    books = data.get("novels", [])
    indexed = {}
    known_runs = set(CAMPAIGN_RUN_IDS)
    for book in books:
        url = book.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        key = source_key(url)
        indexed[key] = {"title": book.get("title", ""), "source_url": url}
        for record in book.get("downloads", []):
            if record.get("status") != "complete":
                continue
            try:
                known_runs.add(int(record["run_id"]))
            except (TypeError, ValueError, KeyError):
                continue
    return indexed, sorted(known_runs)


class GitHub:
    def __init__(self, token: str):
        self.api = requests.Session()
        self.api.headers.update({
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Novel-Library-Export/1.0",
        })

    def get_json(self, url: str) -> dict:
        for attempt in range(3):
            try:
                response = self.api.get(url, timeout=40, allow_redirects=False)
                if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue
                response.raise_for_status()
                return response.json()
            except (requests.Timeout, requests.ConnectionError):
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        raise RuntimeError("API request retry exhausted")

    def run_artifacts(self, run_id: int):
        output = []
        page = 1
        while True:
            url = (f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/artifacts"
                   f"?per_page=100&page={page}")
            payload = self.get_json(url)
            items = payload.get("artifacts", [])
            output.extend(a for a in items if
                          ARTIFACT_NAME.fullmatch(str(a.get("name", "")))
                          and not a.get("expired"))
            if page * 100 >= payload.get("total_count", 0):
                return output
            page += 1
            if page > 25:
                raise RuntimeError("Too many artefact listing pages for one run")

    def download(self, artifact: dict, target: Path):
        """Exchange authenticated GitHub API URL for a signed, unauthenticated CDN URL."""
        url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{artifact['id']}/zip"
        response = self.api.get(url, timeout=45, allow_redirects=False)
        if response.status_code not in (301, 302, 303, 307, 308):
            response.raise_for_status()
            raise RuntimeError("GitHub did not supply an artefact download redirect")
        location = response.headers.get("Location", "")
        parts = urlsplit(location)
        if parts.scheme != "https" or not parts.hostname:
            raise RuntimeError("GitHub provided an invalid artefact download location")
        # Do not forward the GITHUB_TOKEN to the signed CDN.
        with requests.get(location, timeout=(25, 180), stream=True,
                          headers={"User-Agent": "Novel-Library-Export/1.0"}) as stream:
            stream.raise_for_status()
            written = 0
            with target.open("wb") as handle:
                for chunk in stream.iter_content(chunk_size=1024 * 1024):
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > MAX_ARTIFACT_BYTES:
                        raise ValueError("Downloaded artefact exceeds safety limit")
                    handle.write(chunk)


def check_archive(path: Path):
    with ZipFile(path) as archive:
        items = [x for x in archive.infolist() if not x.is_dir()]
        if not items or len(items) > MAX_ENTRIES:
            raise ValueError("Artefact ZIP is empty or contains too many entries")
        if any(not safe_member(x.filename) for x in items):
            raise ValueError("Artefact ZIP contains an unsafe path")
        if sum(x.file_size for x in items) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("Artefact ZIP expanded size exceeds limit")
        epubs = [x for x in items if x.filename.rsplit("/", 1)[-1] == "source.epub"]
        metadatas = [x for x in items if x.filename.rsplit("/", 1)[-1] == "metadata.json"]
        if len(epubs) != 1 or epubs[0].file_size < 100:
            raise ValueError("Artefact does not contain exactly one valid-size source.epub")
        if len(metadatas) != 1 or metadatas[0].file_size > 12 * 1024 * 1024:
            raise ValueError("Artefact missing valid-size metadata.json")
        if archive.testzip() is not None:
            raise ValueError("Artefact ZIP failed CRC check")
        meta = json.loads(archive.read(metadatas[0]).decode("utf-8-sig"))
        if not isinstance(meta, dict):
            raise ValueError("Artefact metadata is not an object")
        epub = archive.read(epubs[0])
        with ZipFile(__import__("io").BytesIO(epub)) as book:
            if "mimetype" not in book.namelist() or "META-INF/container.xml" not in book.namelist():
                raise ValueError("Embedded EPUB lacks required structure")
            if book.testzip() is not None:
                raise ValueError("Embedded EPUB failed CRC validation")
        chapter_manifest = [x for x in items if x.filename.rsplit("/", 1)[-1] == "chapters.json"]
        if chapter_manifest:
            if len(chapter_manifest) != 1:
                raise ValueError("Ambiguous chapter manifest")
            chapters = json.loads(archive.read(chapter_manifest[0]))
            if not isinstance(chapters, list) or not chapters:
                raise ValueError("Chapter manifest is incomplete")
            chapter_count = len(chapters)
        else:
            chapter_count = meta.get("chapter_count")
        return meta, chapter_count


def package_novel(original: Path, target: Path):
    # Retain the original per-novel directory structure and metadata so that
    # the Storage Controller can consume each archive directly.
    with ZipFile(original) as source, ZipFile(target, "w", allowZip64=True) as dest:
        for member in source.infolist():
            if member.is_dir():
                continue
            name = member.filename.replace("\\", "/")
            if not safe_member(name):
                raise ValueError("Unsafe path in source archive")
            compression = ZIP_STORED if name.lower().endswith((".epub", ".zip")) else ZIP_DEFLATED
            info = __import__("zipfile").ZipInfo(name)
            info.compress_type = compression
            with source.open(member) as inp, dest.open(info, "w", force_zip64=True) as out:
                shutil.copyfileobj(inp, out, 1024 * 1024)
    if target.stat().st_size > MAX_INNER_ZIP_BYTES:
        raise ValueError("Per-novel ZIP exceeds HF controller's 120 MiB limit")
    with ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("Created per-novel ZIP failed CRC check")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="downloaded_novels.json")
    parser.add_argument("--output", default="export")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN must be supplied with actions:read")
    target = Path(args.output)
    novel_folder = target / "novels"
    novel_folder.mkdir(parents=True, exist_ok=True)
    cache = target.parent / ".novel-export-cache"
    cache.mkdir(parents=True, exist_ok=True)

    indexed, run_ids = index_registry(Path(args.registry))
    print(f"Registry: {len(indexed)} unique books; checking {len(run_ids)} historical/current runs",
          flush=True)
    github = GitHub(token)
    candidates = {}
    failures = []
    scanned = 0
    for run_id in run_ids:
        try:
            artifacts = github.run_artifacts(run_id)
            for item in artifacts:
                match = ARTIFACT_NAME.fullmatch(item["name"])
                if int(match.group(1)) != run_id:
                    failures.append({"run": run_id, "reason": "Artefact run-name mismatch",
                                     "artifact_id": item["id"]})
                    continue
                candidates.setdefault(match.group(2), []).append(item)
            scanned += len(artifacts)
            print(f"Scanned {run_id}: {len(artifacts)} live complete-book artefacts", flush=True)
        except Exception as exc:
            failures.append({"run": run_id, "reason": str(exc)[:280]})
            print(f"WARNING: failed to list run {run_id}: {exc}", flush=True)
    export_rows = []
    for key, options in sorted(candidates.items()):
        options.sort(key=lambda x: (x.get("created_at", ""), x["id"]), reverse=True)
        for item in options:
            temporary = cache / f"{item['id']}.zip"
            path = None
            try:
                if item.get("size_in_bytes", 0) > MAX_ARTIFACT_BYTES:
                    raise ValueError("Source artifact too large")
                github.download(item, temporary)
                metadata, chapter_count = check_archive(temporary)
                source_url = metadata.get("source_url", "")
                expected = indexed.get(key, {})
                if source_url and source_key(source_url.rstrip("/")) != key:
                    # Historic source URL normalisation varies; accept the
                    # registry's exact URL only if it identifies this key.
                    if not expected or source_url.rstrip("/") != expected["source_url"].rstrip("/"):
                        raise ValueError("Novel metadata URL does not match artefact key")
                title = str(metadata.get("title") or expected.get("title") or "Untitled")
                name = safe_title(title) + "__" + key + ".zip"
                path = novel_folder / name
                package_novel(temporary, path)
                checksum = hashlib.sha256()
                with path.open("rb") as archive:
                    for chunk in iter(lambda: archive.read(1024 * 1024), b""):
                        checksum.update(chunk)
                export_rows.append({
                    "title": title, "source_url": source_url or expected.get("source_url", ""),
                    "chapters": chapter_count, "file": "novels/" + name,
                    "sha256": checksum.hexdigest(),
                    "bytes": path.stat().st_size,
                    "github_run_id": int(item["name"].split("-")[1]),
                    "github_artifact_id": item["id"],
                })
                print(f"EXPORTED {len(export_rows):3d}: {title} ({chapter_count} chapters)", flush=True)
                break
            except (Exception,) as exc:
                failures.append({"artifact_id": item["id"], "name": item["name"],
                                 "reason": str(exc)[:280]})
                if path is not None:
                    path.unlink(missing_ok=True)
                print(f"WARNING {item['name']}: {exc}", flush=True)
            finally:
                temporary.unlink(missing_ok=True)

    missing_registry = [
        {"title": meta.get("title", ""), "source_url": meta.get("source_url", "")}
        for key, meta in indexed.items() if key not in candidates
    ]
    manifest = {
        "exported_novels": len(export_rows),
        "registry_books": len(indexed),
        "scanned_live_artifacts": scanned,
        "unique_live_book_keys": len(candidates),
        "historical_runs_checked": run_ids,
        "novels": export_rows,
        "unavailable_registry_books": missing_registry,
        "warnings": failures,
        "note": ("Snapshot of completed-book artefacts, not unfinished chapter batches. "
                 "Later completions require another export. ZIPs are suitable for "
                 "the HF controller after extracting this outer bundle."),
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (target / "SHA256SUMS.txt").open("w", encoding="utf-8") as hashes:
        for book in export_rows:
            hashes.write(f"{book['sha256']}  {book['file']}\n")
    (target / "README.txt").write_text(
        "Taiyou's Novel Library - GitHub completed EPUB export\n"
        "Extract this outer ZIP first. Individual ready-to-import book ZIPs are "
        "inside the novels folder.\n"
        "Move the ZIPs into your Storage Controller upload folder and use "
        "01_bulk_upload.cmd in preview mode before applying.\n"
        "Review manifest.json for counts, excluded/unavailable books, SHA256 "
        "and artefact provenance.\n"
        "Do not upload the outer ZIP as one novel.\n"
        "The six original campaigns may continue running after this snapshot.\n",
        encoding="utf-8",
    )
    print(f"EXPORT_RESULT {len(export_rows)} books; {len(missing_registry)} registry entries "
          f"unavailable; {len(failures)} warnings", flush=True)
    if not export_rows:
        raise SystemExit("No importable novel artefacts were found")


if __name__ == "__main__":
    main()
