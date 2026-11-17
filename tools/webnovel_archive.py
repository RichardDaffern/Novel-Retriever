#!/usr/bin/env python3
"""Offline, fail-closed Storage Controller ZIP packaging of saved WebNovel pages.

Requires the completed output of tools.webnovel_bulk_import. Does not make
network requests or collect chapter text from WebNovel.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from tools.novel_covers import CoverError, validate_image
from tools.webnovel_bulk_import import STATE_NAME
from tools.webnovel_probe import validate_book_url

MAX_ZIP_BYTES = 120 * 1024 * 1024
MAX_EPUB_BYTES = 100 * 1024 * 1024
MAX_CHAPTER_BYTES = 5 * 1024 * 1024
OPF_NS = "http://www.idpf.org/2007/opf"


class WebNovelArchiveError(ValueError):
    """Saved content is incomplete, modified or unsafe to publish."""


def _load_json(path: Path):
    if not path.is_file() or path.stat().st_size > 12 * 1024 * 1024:
        raise WebNovelArchiveError(f"Missing or oversized local file: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise WebNovelArchiveError(f"Invalid local JSON: {path.name}") from exc


def _hash(data: bytes) -> str:
    return sha256(data).hexdigest()


def _book_source(url: str) -> tuple[str, str]:
    try:
        valid = validate_book_url(url)
    except ValueError as exc:
        raise WebNovelArchiveError(str(exc)) from exc
    book_id = re.search(r"([0-9]{6,})/?$", valid)
    if not book_id:
        raise WebNovelArchiveError("Invalid WebNovel book ID")
    return f"https://www.webnovel.com/book/{book_id.group(1)}", book_id.group(1)


def _epub_bytes(path: Path, cover: bytes | None, extension: str | None) -> bytes:
    if not path.is_file() or path.stat().st_size > MAX_EPUB_BYTES:
        raise WebNovelArchiveError("Missing or oversized generated EPUB")
    try:
        with ZipFile(path) as source:
            if source.testzip() is not None:
                raise WebNovelArchiveError("Generated EPUB CRC check failed")
            names = source.namelist()
            if len(names) != len(set(names)) or "OEBPS/content.opf" not in names:
                raise WebNovelArchiveError("Generated EPUB is malformed")
            if names[0] != "mimetype" or source.read("mimetype") != b"application/epub+zip":
                raise WebNovelArchiveError("Generated EPUB is malformed")
            opf = ET.fromstring(source.read("OEBPS/content.opf"))
            if cover is not None:
                metadata = opf.find(f"{{{OPF_NS}}}metadata")
                manifest = opf.find(f"{{{OPF_NS}}}manifest")
                if metadata is None or manifest is None:
                    raise WebNovelArchiveError("EPUB cover metadata cannot be added")
                ET.SubElement(metadata, f"{{{OPF_NS}}}meta",
                              {"name": "cover", "content": "cover-image"})
                media = "image/jpeg" if extension == ".jpg" else "image/png"
                ET.SubElement(manifest, f"{{{OPF_NS}}}item", {
                    "id": "cover-image", "href": "cover" + extension, "media-type": media,
                })
            buf = BytesIO()
            with ZipFile(buf, "w") as target:
                for info in source.infolist():
                    if info.is_dir():
                        continue
                    data = (ET.tostring(opf, encoding="utf-8", xml_declaration=True)
                            if cover is not None and info.filename == "OEBPS/content.opf"
                            else source.read(info))
                    target.writestr(info.filename, data, compress_type=(
                        ZIP_STORED if info.filename == "mimetype" else ZIP_DEFLATED))
                if cover is not None:
                    target.writestr("OEBPS/cover" + extension, cover, compress_type=ZIP_DEFLATED)
            return buf.getvalue()
    except (KeyError, OSError, ET.ParseError) as exc:
        raise WebNovelArchiveError("Generated EPUB could not be verified") from exc


def archive_saved_pages(import_dir: Path, source_url: str, *,
                        output_dir: Path | None = None, cover_path: Path | None = None,
                        confirm_rights: bool = False) -> Path:
    """Verify an existing saved-page import and atomically publish one novel ZIP."""
    if not confirm_rights:
        raise WebNovelArchiveError("Explicit --confirm-rights is required")
    source_url, book_id = _book_source(source_url)
    import_dir = Path(import_dir).resolve()
    output_dir = (Path(output_dir) if output_dir is not None
                  else import_dir.parent / "Downloaded_Novels").resolve()
    if import_dir == output_dir or import_dir in output_dir.parents:
        raise WebNovelArchiveError("Archive output must be outside the import folder")
    metadata = _load_json(import_dir / "metadata.json")
    state = _load_json(import_dir / STATE_NAME)
    if not isinstance(metadata, dict) or not isinstance(state, dict):
        raise WebNovelArchiveError("Import metadata/state must be JSON objects")
    if metadata.get("source") != "user-supplied-authorised":
        raise WebNovelArchiveError("Input is not from the local saved-page importer")
    title, author = metadata.get("title"), metadata.get("author")
    entries, done = metadata.get("chapters"), state.get("completed")
    if (not isinstance(title, str) or not title.strip() or not isinstance(author, str)
            or not author.strip() or not isinstance(entries, list) or not entries
            or len(entries) > 10000 or not isinstance(done, dict)
            or len(entries) != metadata.get("chapter_count")
            or title != state.get("title") or author != state.get("author")):
        raise WebNovelArchiveError("Import metadata/state incomplete or inconsistent")
    chapters = []
    members = []
    seen_bodies = set()
    for i, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise WebNovelArchiveError("Invalid saved-page chapter manifest")
        number = entry.get("position")
        expected_file = f"chapter-{number:06d}.txt" if type(number) is int and number > 0 else ""
        if (entry.get("file") != expected_file or not expected_file
                or not isinstance(entry.get("title"), str) or not entry["title"].strip()
                or (i > 1 and number != entries[i - 2]["position"] + 1)):
            raise WebNovelArchiveError("Saved-page chapters are missing or unordered")
        checkpoint = done.get(str(number))
        source_name = entry.get("source_file")
        input_directory = state.get("input_dir")
        if (not isinstance(source_name, str) or Path(source_name).name != source_name
                or not isinstance(input_directory, str)
                or not isinstance(checkpoint, dict)):
            raise WebNovelArchiveError(f"Chapter {number} has invalid source provenance")
        source_file = Path(input_directory) / source_name
        if not source_file.is_file() or _hash(source_file.read_bytes()) != checkpoint.get("source_sha256"):
            raise WebNovelArchiveError(f"Chapter {number} source changed since import")
        file = import_dir / expected_file
        if not file.is_file() or file.stat().st_size > MAX_CHAPTER_BYTES:
            raise WebNovelArchiveError(f"Chapter {number} is missing or not checkpointed")
        original = file.read_bytes()
        if _hash(original) != checkpoint.get("output_sha256"):
            raise WebNovelArchiveError(f"Chapter {number} failed checkpoint hash validation")
        content = original.replace(b"\r\n", b"\n")
        prefix = (entry["title"] + "\n\n").encode("utf-8")
        if not content.startswith(prefix) or len(content) - len(prefix) < 100:
            raise WebNovelArchiveError(f"Chapter {number} has invalid or incomplete content")
        body_digest = _hash(content[len(prefix):].strip())
        if body_digest in seen_bodies:
            raise WebNovelArchiveError(f"Chapter {number} duplicates an earlier chapter body")
        seen_bodies.add(body_digest)
        dest = f"chapter_{i:05d}.txt"
        members.append((dest, content))
        chapters.append({"position": i, "chapter_number": number, "title": entry["title"],
                         "file": dest, "word_count": len(content.decode("utf-8").split()),
                         "sha256": _hash(content)})
    if set(done) != {str(e["position"]) for e in entries}:
        raise WebNovelArchiveError("Checkpoint contains missing or extra chapters")
    cover = None
    extension = None
    if cover_path is not None:
        cover_path = Path(cover_path).resolve()
        if not cover_path.is_file() or cover_path.stat().st_size > 8 * 1024 * 1024:
            raise WebNovelArchiveError("Cover file missing or oversized")
        try:
            cover, extension = validate_image(cover_path.read_bytes())
        except CoverError as exc:
            raise WebNovelArchiveError(f"Invalid user-supplied cover: {exc}") from exc
        from PIL import Image
        with Image.open(BytesIO(cover)) as image:
            if image.width >= image.height:
                raise WebNovelArchiveError("Cover must be a portrait image")
    epub = _epub_bytes(import_dir / "book.epub", cover, extension)
    with ZipFile(BytesIO(epub)) as check:
        if check.testzip() is not None or len([n for n in check.namelist() if n.endswith(".xhtml")]) != len(entries):
            raise WebNovelArchiveError("EPUB does not contain the expected chapter count")
        for chapter, (_filename, txt_bytes) in zip(entries, members):
            page = f'OEBPS/chapter-{chapter["position"]:06d}.xhtml'
            if page not in check.namelist():
                raise WebNovelArchiveError("EPUB chapter is missing: " + page)
            try:
                xml = ET.fromstring(check.read(page))
            except ET.ParseError as exc:
                raise WebNovelArchiveError("EPUB chapter markup is malformed") from exc
            rendered = "".join("".join(node.itertext()) for node in xml.iter()
                               if node.tag.rsplit("}", 1)[-1] == "p")
            body = txt_bytes.decode("utf-8").partition("\n\n")[2].strip()
            if not rendered or "".join(rendered.split()) != "".join(body.split()):
                raise WebNovelArchiveError("EPUB chapter content differs from verified TXT")
    identity = sha256(source_url.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:80] or f"webnovel-{book_id}"
    package_metadata = {"title": title, "author": author, "language": "en",
                        "source_url": source_url, "chapter_count": len(chapters),
                        "source_chapter_range": [chapters[0]["chapter_number"], chapters[-1]["chapter_number"]],
                        "chapter_files": "UTF-8 TXT", "format": "epub",
                        "acquisition": "authorised-user-saved-pages",
                        "created_at_utc": datetime.now(timezone.utc).isoformat()}
    if cover is not None:
        package_metadata["cover_image"] = "cover" + extension
        package_metadata["cover_provenance"] = "user-supplied; authenticity not independently verified"
    payloads = [("metadata.json", (json.dumps(package_metadata, indent=2, ensure_ascii=False) + "\n").encode("utf-8")),
                ("chapters.json", (json.dumps(chapters, indent=2, ensure_ascii=False) + "\n").encode("utf-8")),
                ("source.epub", epub), *members]
    if cover is not None:
        payloads.append(("cover" + extension, cover))
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"novel-{identity}.zip"
    if target.exists():
        raise WebNovelArchiveError("Completed ZIP already exists; no overwrite attempted")
    staged = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".webnovel-", suffix=".zip",
                                         dir=output_dir, delete=False) as temporary:
            staged = Path(temporary.name)
        with ZipFile(staged, "w", compression=ZIP_DEFLATED, compresslevel=6) as out:
            for name, data in payloads:
                out.writestr(f"{slug}/{name}", data)
        if staged.stat().st_size > MAX_ZIP_BYTES:
            raise WebNovelArchiveError("Storage Controller limit exceeded: ZIP must be at most 120 MiB")
        with ZipFile(staged) as check:
            if check.testzip() is not None or len(check.infolist()) != len(payloads):
                raise WebNovelArchiveError("Final archive failed ZIP integrity checks")
            for row in chapters:
                if _hash(check.read(f'{slug}/{row["file"]}')) != row["sha256"]:
                    raise WebNovelArchiveError("Final chapter SHA-256 verification failed")
            if check.read(f"{slug}/source.epub") != epub:
                raise WebNovelArchiveError("Final EPUB integrity verification failed")
        # Atomic no-clobber publication, including concurrent packagers.
        os.link(staged, target)
    except FileExistsError as exc:
        raise WebNovelArchiveError("Completed ZIP appeared concurrently; refusing to overwrite") from exc
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--import-dir", type=Path, required=True)
    parser.add_argument("--source-url", required=True,
                        help="WebNovel HTTPS book page (provenance only; not fetched)")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--cover", type=Path, help="Optional user-supplied cover (JPEG/PNG/WebP/GIF)")
    parser.add_argument("--confirm-rights", action="store_true")
    args = parser.parse_args(argv)
    try:
        output = archive_saved_pages(args.import_dir, args.source_url,
                                     output_dir=args.output_dir, cover_path=args.cover,
                                     confirm_rights=args.confirm_rights)
        print(f"Validated Storage Controller ZIP: {output}")
        return 0
    except (WebNovelArchiveError, OSError, ValueError) as exc:
        print(f"WebNovel archive failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
