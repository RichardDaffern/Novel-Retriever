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
import tempfile

from tools.cover_pipeline import finalise_archive
from tools.novel_dedupe import consolidate
import time
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED, BadZipFile

import requests

REPO = "RichardDaffern/Novel-Retriever"
CAMPAIGN_RUN_IDS = (
    43734388839, 43734393507, 43734398943,
    43734404117, 43734410920, 43734417289, 43819213500,
)
ARTIFACT_NAME = re.compile(r"^novel-([0-9]+)-([a-f0-9]{20}|scribblehub-[0-9]+)$")
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
    raw = name.replace("\\", "/")
    parts = raw.split("/")
    path = PurePosixPath(raw)
    # Check raw components: PurePosixPath collapses './' and repeated slashes.
    # Colons, trailing dots/spaces and control characters alias on Windows.
    return bool(name and not path.is_absolute() and all(
        part and part not in (".", "..") and ":" not in part and
        part.rstrip(" .") == part and all(ord(char) >= 32 for char in part)
        for part in parts
    ))


def index_registry(path: Path, *, include_historical: bool = True):
    data = json.loads(path.read_text(encoding="utf-8"))
    books = data.get("novels", [])
    indexed = {}
    known_runs = set(CAMPAIGN_RUN_IDS) if include_historical else set()
    for book in books:
        url = book.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            continue
        series = re.match(r"^/series/([0-9]+)(?:/|$)", urlsplit(url).path)
        host = (urlsplit(url).hostname or "").lower().removeprefix("www.")
        key = ("scribblehub-" + series.group(1)
               if host == "scribblehub.com" and series else source_key(url))
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
            "User-Agent": "Novel-Retriever-Export/1.0",
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
        # Keep any existing verified cache entry intact if the network fails.
        target.parent.mkdir(parents=True, exist_ok=True)
        staged = None
        try:
            with tempfile.NamedTemporaryFile(prefix=".artifact-", suffix=".zip",
                                             dir=target.parent, delete=False) as handle:
                staged = Path(handle.name)
                with requests.get(location, timeout=(25, 180), stream=True,
                                  headers={"User-Agent": "Novel-Retriever-Export/1.0"}) as stream:
                    stream.raise_for_status()
                    written = 0
                    for chunk in stream.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        written += len(chunk)
                        if written > MAX_ARTIFACT_BYTES:
                            raise ValueError("Downloaded artefact exceeds safety limit")
                        handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
            staged.replace(target)
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)


def check_archive(path: Path):
    with ZipFile(path) as archive:
        items = [x for x in archive.infolist() if not x.is_dir()]
        if not items or len(items) > MAX_ENTRIES:
            raise ValueError("Artefact ZIP is empty or contains too many entries")
        if any(not safe_member(x.filename) for x in items):
            raise ValueError("Artefact ZIP contains an unsafe path")
        canonical = [x.filename.replace("\\", "/").casefold() for x in items]
        if len(set(canonical)) != len(canonical):
            raise ValueError("Artefact ZIP contains duplicate or case-aliased members")
        if any(((x.external_attr >> 16) & 0o170000) in
               (0o120000, 0o020000, 0o060000) for x in items):
            raise ValueError("Artefact ZIP contains a link or device entry")
        if any(x.file_size > max(x.compress_size, 1) * 10000 for x in items):
            raise ValueError("Artefact ZIP contains a suspicious compression ratio")
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
    parser.add_argument("--only-listed", action="store_true",
                        help="Export only completed books in the supplied registry snapshot")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN must be supplied with actions:read")
    target = Path(args.output)
    if target.exists() and any(target.iterdir()):
        raise SystemExit("Export output directory is not empty; use a new --output path "
                         "to prevent mixing snapshots or overwriting earlier ZIPs")
    novel_folder = target / "novels"
    novel_folder.mkdir(parents=True, exist_ok=True)
    cache = target.parent / ".novel-export-cache"
    cache.mkdir(parents=True, exist_ok=True)

    indexed, run_ids = index_registry(Path(args.registry),
                                     include_historical=not args.only_listed)
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
                if args.only_listed and match.group(2) not in indexed:
                    continue
                candidates.setdefault(match.group(2), []).append(item)
            scanned += len(artifacts)
            print(f"Scanned {run_id}: {len(artifacts)} live complete-book artefacts", flush=True)
        except Exception as exc:
            failures.append({"run": run_id, "reason": str(exc)[:280]})
            print(f"WARNING: failed to list run {run_id}: {exc}", flush=True)
    export_rows = []
    successfully_exported_keys = set()
    for key, options in sorted(candidates.items()):
        options.sort(key=lambda x: (x.get("created_at", ""), x["id"]), reverse=True)
        for item in options:
            temporary = cache / f"{item['id']}.zip"
            path = None
            try:
                if item.get("size_in_bytes", 0) > MAX_ARTIFACT_BYTES:
                    raise ValueError("Source artifact too large")
                if not temporary.exists():
                    github.download(item, temporary)
                metadata, chapter_count = check_archive(temporary)
                source_url = metadata.get("source_url", "")
                expected = indexed.get(key, {})
                matched = (source_key(source_url.rstrip("/")) == key)
                if key.startswith("scribblehub-"):
                    series = key.partition("-")[2]
                    p = urlsplit(source_url)
                    matched = (p.hostname or "").lower().removeprefix("www.") == "scribblehub.com" and bool(
                        re.match(r"^/series/" + re.escape(series) + r"(?:/|$)", p.path))
                if source_url and not matched:
                    if not expected or source_url.rstrip("/") != expected["source_url"].rstrip("/"):
                        raise ValueError("Novel metadata URL does not match artefact key")
                title = str(metadata.get("title") or expected.get("title") or "Untitled")
                name = safe_title(title) + "__" + key + "__" + str(item["id"]) + ".zip"
                path = novel_folder / name
                package_novel(temporary, path)
                finalise_archive(path, cache_dir=cache / "covers")
                if path.stat().st_size > MAX_INNER_ZIP_BYTES:
                    raise ValueError("Cover-enriched ZIP exceeds 120 MiB safety limit")
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
                    "original_github_artifact": item["name"],
                })
                successfully_exported_keys.add(key)
                print(f"EXPORTED {len(export_rows):3d}: {title} ({chapter_count} chapters)", flush=True)
                # Inspect all available editions; deduplication decides
                # whether an older completed artefact is equivalent or differs.
            except (Exception,) as exc:
                failures.append({"artifact_id": item["id"], "name": item["name"],
                                 "reason": str(exc)[:280]})
                if path is not None:
                    path.unlink(missing_ok=True)
                temporary.unlink(missing_ok=True)
                print(f"WARNING {item['name']}: {exc}", flush=True)
    missing_registry = [
        {"title": meta.get("title", ""), "source_url": meta.get("source_url", "")}
        for key, meta in indexed.items() if key not in successfully_exported_keys
    ]
    # Compare every downloaded complete edition before publishing the final
    # upload directory. The original ZIPs survive in the local cache.
    dedupe = {"unique": 0, "duplicates": 0, "conflicts": 0,
              "invalid": 0, "novels": [], "review_conflicts": []}
    if export_rows:
        provenance = {Path(row["file"]).name: row["original_github_artifact"]
                      for row in export_rows}
        staged = target / "_selected"
        dedupe = consolidate(list(novel_folder.glob("*.zip")), staged,
                             provenance=provenance)
        backup = cache / "unfiltered-novels"
        if backup.exists():
            shutil.rmtree(backup)
        novel_folder.rename(backup)
        try:
            (staged / "novels").rename(novel_folder)
        except BaseException:
            backup.rename(novel_folder)
            raise
        if (staged / "review-conflicts").is_dir():
            (staged / "review-conflicts").rename(target / "review-conflicts")
        shutil.rmtree(staged)
    manifest = {
        "exported_novels": dedupe["unique"],
        "registry_books": len(indexed),
        "scanned_live_artifacts": scanned,
        "unique_live_book_keys": len(candidates),
        "historical_runs_checked": run_ids,
        "novels": dedupe["novels"],
        "duplicates_skipped": dedupe["duplicates"],
        "conflicting_editions": dedupe["review_conflicts"],
        "invalid_archives": dedupe["invalid_archives"] if export_rows else [],
        "unavailable_registry_books": missing_registry,
        "warnings": failures,
        "note": ("Snapshot of completed-book artefacts, not unfinished chapter batches. "
                 "Later completions require another export. ZIPs are suitable for "
                 "the HF controller after extracting this outer bundle."),
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (target / "SHA256SUMS.txt").open("w", encoding="utf-8") as hashes:
        for book in dedupe["novels"]:
            hashes.write(f"{book['zip_sha256']}  {book['file']}\n")
    (target / "README.txt").write_text(
        "Novel Retriever - completed EPUB export for Taiyou's library\n"
        "Extract this outer ZIP first. Individual ready-to-import book ZIPs are "
        "inside the novels folder.\n"
        "Review review-conflicts/ before choosing among different editions.\n"
        "Move individual ZIPs into the Storage Controller's novels folder and "
        "choose Windows menu option 12 for the opt-in duplicate-aware preview.\n"
        "Review manifest.json for counts, excluded/unavailable books, SHA256 "
        "and artefact provenance.\n"
        "Do not upload the outer ZIP as one novel.\n"
        "Old and new ZIPs may be previewed together with --dedupe-local; "
        "conflicting editions block all writes.\n"
        "The six original campaigns may continue running after this snapshot.\n",
        encoding="utf-8",
    )
    print(f"EXPORT_RESULT {dedupe['unique']} unique books, {dedupe['duplicates']} duplicates, "
          f"{dedupe['conflicts']} conflicts; {len(missing_registry)} registry entries "
          f"unavailable; {len(failures)} warnings", flush=True)
    if not export_rows:
        raise SystemExit("No importable novel artefacts were found")


if __name__ == "__main__":
    main()
