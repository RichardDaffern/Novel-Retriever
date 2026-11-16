#!/usr/bin/env python3
"""Conservative portable-novel ZIP deduplication, independent of filenames.

Identical EPUBs and chapter-hash-equivalent books are duplicates. Differing
editions for one identity are retained for manual review, never overwritten.
The tool does not write to Hugging Face or delete its input ZIP files.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from urllib.parse import urlsplit, urlunsplit
from zipfile import ZipFile, BadZipFile

MAX_ZIP_BYTES = 950 * 1024 * 1024
MAX_EPUB_BYTES = 120 * 1024 * 1024
MAX_ENTRIES = 25000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity_url(value: str) -> str:
    try:
        p = urlsplit(value.strip())
        if p.scheme.lower() != "https" or not p.hostname or p.username or p.password:
            return ""
        host = p.hostname.casefold().removeprefix("www.")
        if p.port not in (None, 443):
            return ""
        path = p.path.rstrip("/") or "/"
        return urlunsplit(("https", host, path, p.query, ""))
    except (ValueError, AttributeError):
        return ""


def normalise(value: str) -> str:
    return " ".join(re.sub(r"[^\w]+", " ", str(value or "").casefold()).split())


def _safe_members(archive: ZipFile):
    members = [item for item in archive.infolist() if not item.is_dir()]
    if (not members or len(members) > MAX_ENTRIES or
            sum(item.file_size for item in members) > MAX_ZIP_BYTES):
        raise ValueError("Unsafe archive size or entry count")
    paths = []
    for item in members:
        p = PurePosixPath(item.filename.replace("\\", "/"))
        if (p.is_absolute() or ".." in p.parts or "." in p.parts or
                ((item.external_attr >> 16) & 0o170000) == 0o120000):
            raise ValueError("Unsafe ZIP member")
        paths.append(p)
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate ZIP members")
    return members


def inspect(path: Path, *, original_artifact: str = "") -> dict:
    """Verify one book ZIP and calculate chapter-content and EPUB fingerprints."""
    path = Path(path)
    with ZipFile(path) as archive:
        members = _safe_members(archive)
        names = [item.filename for item in members]
        metadata = [n for n in names if n.rsplit("/", 1)[-1] == "metadata.json"]
        epub_files = [n for n in names if n.rsplit("/", 1)[-1] == "source.epub"]
        chapter_files = [n for n in names if n.rsplit("/", 1)[-1] == "chapters.json"]
        if len(metadata) != 1 or len(epub_files) != 1 or len(chapter_files) != 1:
            raise ValueError("Not a complete single-novel ZIP")
        parent = metadata[0].rsplit("/", 1)[0] if "/" in metadata[0] else ""
        if any((n.rsplit("/", 1)[0] if "/" in n else "") != parent
               for n in (*epub_files, *chapter_files)):
            raise ValueError("Novel files have inconsistent ZIP prefixes")
        meta = json.loads(archive.read(metadata[0]))
        rows = json.loads(archive.read(chapter_files[0]))
        if not isinstance(meta, dict) or not isinstance(rows, list) or not rows:
            raise ValueError("Incomplete book manifests")
        if meta.get("chapter_count") != len(rows):
            raise ValueError("Inconsistent number of chapters")
        order = []
        chapter_hashes = []
        for item in rows:
            if not isinstance(item, dict) or type(item.get("position")) is not int:
                raise ValueError("Invalid chapter position")
            filename = item.get("file")
            if (not isinstance(filename, str) or
                    not re.fullmatch(r"chapter_[A-Za-z0-9_-]+\.txt", filename)):
                raise ValueError("Unsafe chapter filename")
            chapter_path = parent + "/" + filename if parent else filename
            if chapter_path not in names:
                raise ValueError("Chapter TXT missing")
            hashed = digest(archive.read(chapter_path))
            if item.get("sha256") and item["sha256"] != hashed:
                raise ValueError("Chapter checksum mismatch")
            order.append(item["position"])
            chapter_hashes.append(hashed)
        if len(set(order)) != len(order) or order != sorted(order):
            raise ValueError("Duplicate or unordered chapter positions")
        epub_info = archive.getinfo(epub_files[0])
        if epub_info.file_size <= 100 or epub_info.file_size > MAX_EPUB_BYTES:
            raise ValueError("Missing or oversized EPUB")
        epub = archive.read(epub_files[0])
        with ZipFile(BytesIO(epub)) as ebook:
            if ("META-INF/container.xml" not in ebook.namelist() or
                    ebook.testzip() is not None):
                raise ValueError("Invalid EPUB")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
        book_url = identity_url(meta.get("source_url", ""))
        title, author = str(meta.get("title") or ""), str(meta.get("author") or "")
        if not book_url and (not normalise(title) or not normalise(author)):
            raise ValueError("Novel identity requires source URL or title and author")
        cover = meta.get("cover_image", "")
        has_cover = bool(cover and (parent + "/" + cover if parent else cover) in names
                         and cover in ("cover.jpg", "cover.png"))
        content_hash = digest(json.dumps(list(zip(order, chapter_hashes)),
                                         separators=(",", ":")).encode("utf-8"))
        book_id = "url:" + book_url if book_url else "title:" + normalise(title) + "|author:" + normalise(author)
        return {
            "path": str(path), "title": title, "author": author, "source_url": book_url,
            "identity": book_id, "chapter_count": len(rows), "positions": order,
            "chapter_hashes": chapter_hashes, "chapter_sha256": content_hash,
            "epub_sha256": digest(epub), "zip_sha256": digest(path.read_bytes()),
            "cover_status": "available" if has_cover else "missing",
            "created_at_utc": str(meta.get("created_at_utc") or ""),
            "original_github_artifact": original_artifact,
        }


def equivalent(left: dict, right: dict) -> bool:
    return (left["epub_sha256"] == right["epub_sha256"] or
            (left["positions"] == right["positions"] and
             left["chapter_hashes"] == right["chapter_hashes"]))


def compatible_subset(short: dict, long: dict) -> bool:
    a = dict(zip(short["positions"], short["chapter_hashes"]))
    b = dict(zip(long["positions"], long["chapter_hashes"]))
    return bool(a and len(a) < len(b) and all(b.get(k) == v for k, v in a.items()))


def _freshness(row: dict):
    raw = row.get("created_at_utc", "")
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError, OverflowError):
        return 0


def _rank(row: dict):
    return (row["chapter_count"], _freshness(row),
            row["cover_status"] == "available", row["zip_sha256"])


def _copy_if_needed(src: Path, dest: Path) -> bool:
    if dest.is_file():
        if digest(dest.read_bytes()) == digest(src.read_bytes()):
            return False
        raise ValueError(f"Refusing to replace existing different output: {dest}")
    shutil.copy2(src, dest)
    return True


def consolidate(paths: list[Path], output: Path, *, provenance: dict | None = None) -> dict:
    """Return report and publish one preferred copy per identity plus review copies.

    Conflicting editions are kept under review-conflicts/; no input is changed.
    A second invocation against an existing output is idempotent.
    """
    output = Path(output)
    source_paths = sorted(set(Path(p).resolve() for p in paths if Path(p).is_file()))
    if output.resolve() in source_paths:
        raise ValueError("Output cannot be an input ZIP")
    books, invalid = [], []
    for path in source_paths:
        try:
            row = inspect(path, original_artifact=(provenance or {}).get(path.name, ""))
            books.append(row)
        except (ValueError, KeyError, OSError, BadZipFile, TypeError) as exc:
            invalid.append({"file": str(path), "reason": str(exc)})
    if not books:
        raise ValueError("No verified novels available to consolidate")
    # URL identity takes precedence. A name-only book may match exactly one
    # URL-identified book by title and author, but ambiguities remain separate.
    url_names = defaultdict(set)
    for row in books:
        if row["source_url"] and normalise(row["title"]) and normalise(row["author"]):
            url_names[(normalise(row["title"]), normalise(row["author"]))].add(row["identity"])
    for row in books:
        if not row["source_url"]:
            choices = url_names.get((normalise(row["title"]), normalise(row["author"])), set())
            if len(choices) == 1:
                row["identity"] = next(iter(choices))
    # Cross-site duplication is only automatic with identical verified
    # EPUB/chapter content AND matching title and author, never title alone.
    fingerprints = defaultdict(list)
    for row in books:
        name = (normalise(row["title"]), normalise(row["author"]))
        if all(name):
            fingerprints[(name, row["chapter_sha256"])].append(row)
    for matching in fingerprints.values():
        urls = sorted({row["identity"] for row in matching
                       if row["identity"].startswith("url:")})
        if urls:
            for row in matching:
                row["identity"] = urls[0]
    groups = defaultdict(list)
    for row in books:
        groups[row["identity"]].append(row)
    novels, duplicates, conflicts = [], [], []
    used_names = set()
    (output / "novels").mkdir(parents=True, exist_ok=True)
    (output / "review-conflicts").mkdir(parents=True, exist_ok=True)
    for book_id, group in sorted(groups.items()):
        # If two sources share identical EPUB bytes they are the same book,
        # but unlike a title match no silent cross-source merge is performed.
        preferred = sorted(group, key=_rank, reverse=True)[0]
        for row in group:
            if row is preferred:
                continue
            if equivalent(row, preferred) or compatible_subset(row, preferred):
                duplicates.append({"file": row["path"], "preferred": preferred["path"],
                                   "reason": "equivalent_or_contained"})
            else:
                conflicts.append({"file": row["path"], "preferred": preferred["path"],
                                  "reason": "different_chapters_or_edition",
                                  "title": row["title"], "source_url": row["source_url"]})
        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", preferred["title"]).strip("-")[:60] or "novel"
        short_id = digest(book_id.encode("utf-8"))[:12]
        name = f"{slug}-{short_id}.zip"
        if name in used_names:
            raise ValueError("Novel output naming collision")
        used_names.add(name)
        destination = output / "novels" / name
        _copy_if_needed(Path(preferred["path"]), destination)
        novels.append({key: preferred[key] for key in
                       ("title", "author", "source_url", "chapter_count",
                        "chapter_sha256", "epub_sha256", "zip_sha256",
                        "cover_status", "original_github_artifact")} |
                      {"file": "novels/" + name, "identity": book_id})
        for conflict in conflicts:
            if conflict["preferred"] != preferred["path"]:
                continue
            alternative = next(x for x in group if x["path"] == conflict["file"])
            conflict_name = f"{slug}-{short_id}-{alternative['zip_sha256'][:12]}.zip"
            _copy_if_needed(Path(alternative["path"]),
                            output / "review-conflicts" / conflict_name)
            conflict["review_file"] = "review-conflicts/" + conflict_name
    report = {"version": 1, "unique": len(novels), "duplicates": len(duplicates),
              "conflicts": len(conflicts), "invalid": len(invalid),
              "novels": novels, "skipped_duplicates": duplicates,
              "review_conflicts": conflicts, "invalid_archives": invalid}
    (output / "manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="Directory containing old and new individual ZIPs")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    inputs = sorted(args.input.rglob("*.zip"))
    if not inputs:
        parser.error("No ZIP files found in input directory")
    result = consolidate(inputs, args.output)
    print(f"Unique: {result['unique']}; duplicate: {result['duplicates']}; "
          f"conflicting: {result['conflicts']}; invalid: {result['invalid']}")
    return 2 if result["conflicts"] or result["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
