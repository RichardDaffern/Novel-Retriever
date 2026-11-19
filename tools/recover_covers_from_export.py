"""Recover cover-only upload ZIP from previously exported complete novel archives.

Offline: no novel websites, HF access, chapters or EPUB modification.
All matches use the exact source URL in the verified 104-book snapshot.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import urlsplit
from zipfile import ZipFile, BadZipFile

from tools.novel_covers import CoverError, validate_image, extract_epub_cover
from novel_downloader import slugify

MAX_EPUB = 120 * 1024 * 1024
MAX_COVER = 8 * 1024 * 1024
MAX_META = 12 * 1024 * 1024
EXPECTED = 104


def snapshot(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("novels")
    if not isinstance(entries, list) or len(entries) != EXPECTED:
        raise ValueError("Expected exactly 104 previously completed novel records")
    selected = {}
    for item in entries:
        url, title = item.get("url"), item.get("title")
        if (not isinstance(url, str) or not isinstance(title, str)
                or not url.startswith("https://")
                or not title or url in selected
                or not item.get("downloads")
                or any(d.get("status") != "complete" or d.get("range") != "all"
                       for d in item["downloads"])):
            raise ValueError("Untrusted or duplicate completed novel registry item")
        selected[url] = {"title": title, "url": url}
    return selected


def _member(files: list, basename: str):
    hits = [i for i in files if PurePosixPath(i.filename).name == basename]
    return hits[0] if len(hits) == 1 else None


def _read_existing(z: ZipFile, files: list, prefix: str):
    for filename in ("cover.jpg", "cover.png", "cover.webp"):
        info = next((i for i in files if i.filename == prefix + filename), None)
        if info is None or not 0 < info.file_size <= MAX_COVER:
            continue
        try:
            data, ext = validate_image(z.read(info))
            if ext == Path(filename).suffix or (filename.endswith(".webp") and ext == ".jpg"):
                return data, ext, "standalone"
        except (CoverError, OSError, ValueError):
            pass
    return None


def inspect_archive(path: Path) -> tuple[str, tuple[bytes, str, str] | None]:
    with ZipFile(path) as z:
        items = [i for i in z.infolist() if not i.is_dir()]
        if len(items) > 20000:
            raise ValueError("Too many ZIP entries")
        meta_entry = _member(items, "metadata.json")
        epub_entry = _member(items, "source.epub")
        if (meta_entry is None or epub_entry is None
                or meta_entry.file_size > MAX_META
                or not 0 < epub_entry.file_size <= MAX_EPUB):
            raise ValueError("Novel ZIP lacks unique, safe metadata/EPUB")
        prefix = str(PurePosixPath(meta_entry.filename).parent)
        prefix = "" if prefix == "." else prefix + "/"
        if epub_entry.filename != prefix + "source.epub":
            raise ValueError("EPUB and metadata must belong to one novel")
        meta = json.loads(z.read(meta_entry).decode("utf-8-sig"))
        url = meta.get("source_url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError("Novel source URL missing")
        existing = _read_existing(z, items, prefix)
        if existing:
            return url, existing
        # Read only the EPUB when no validated standalone cover exists.
        with tempfile.TemporaryDirectory(prefix="cover-epub-") as folder:
            epub = Path(folder) / "source.epub"
            with z.open(epub_entry) as source, epub.open("wb") as output:
                import shutil
                shutil.copyfileobj(source, output, 1024 * 1024)
            try:
                cover = extract_epub_cover(epub)
            except (BadZipFile, OSError, KeyError, ValueError, CoverError):
                cover = None
            if cover:
                return url, (*cover, "embedded_epub")
        return url, None


def recover(input_dir: Path, registry_file: Path, output_dir: Path) -> dict:
    expected = snapshot(registry_file)
    files = sorted(input_dir.glob("*.zip"))
    if not files:
        raise ValueError("Export contains no individual novel ZIPs")
    output_dir.mkdir(parents=True, exist_ok=True)
    found = set()
    entries = []
    unresolved = []
    for path in files:
        try:
            url, cover = inspect_archive(path)
            if url not in expected:
                raise ValueError("Archive source URL absent from the approved snapshot")
            if url in found:
                raise ValueError("Two ZIP files claim the same completed novel URL")
            found.add(url)
            if not cover:
                unresolved.append({"title": expected[url]["title"], "source_url": url,
                                   "reason": "No validated standalone or embedded EPUB cover"})
                continue
            data, extension, method = cover
            host = urlsplit(url).hostname or ""
            website = {"novelfull.com": "NovelFull",
                       "freewebnovel.com": "FreeWebNovel"}.get(host)
            if website is None:
                raise ValueError("Source website not supported for this cover hand-off")
            title = expected[url]["title"]
            key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
            name = f"{website}/{slugify(title)[:78]}-{key}{extension}"
            target = output_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entries.append({"title": title, "source_url": url, "website": website,
                            "cover_file": name, "method": method})
        except (BadZipFile, OSError, KeyError, ValueError, CoverError) as exc:
            unresolved.append({"archive": path.name, "reason": str(exc)[:180]})
    for url, item in expected.items():
        if url not in found:
            unresolved.append({"title": item["title"], "source_url": url,
                               "reason": "Complete book missing from export"})
    result = {"version": 1, "covers": entries,
              "summary": {"snapshot_books": len(expected), "archive_files": len(files),
                          "covers_recovered": len(entries),
                          "unresolved": len(unresolved), "no_network_fetches": True}}
    if entries:
        (output_dir / "covers_manifest.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "cover-recovery-report.json").write_text(
        json.dumps({"summary": result["summary"], "unresolved": unresolved},
                   indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--novels", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)
    result = recover(args.novels, args.registry, args.output)
    print(json.dumps(result["summary"], sort_keys=True), flush=True)
    if not result["covers"]:
        raise SystemExit("No valid existing covers found; no upload ZIP created")


if __name__ == "__main__":
    main()
