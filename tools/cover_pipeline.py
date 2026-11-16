#!/usr/bin/env python3
"""Shared, non-fatal cover resolution for completed book folders and portable ZIPs.

Cover identity is always taken from the downloaded book's own source URL.
Never search by a guessed title. No missing cover can invalidate chapter data.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import tempfile
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED, BadZipFile

from tools import novel_covers as covers
from tools.download_registry import canonical_url

COVER_FILES = ("cover.jpg", "cover.png")
MAX_ZIP_BYTES = 950 * 1024 * 1024
MAX_FILES = 25000


def _image_in_folder(folder: Path):
    for name in COVER_FILES:
        candidate = folder / name
        if candidate.is_file() and not candidate.is_symlink():
            try:
                data, ext = covers.validate_image(candidate.read_bytes())
                if ext == candidate.suffix.lower():
                    return data, ext
            except (OSError, covers.CoverError):
                pass
    return None


def _epub_cover(path: Path):
    try:
        return covers.extract_epub_cover(path)
    except (BadZipFile, OSError, KeyError, ET.ParseError, covers.CoverError):
        return None


def embed_cover(epub: Path, data: bytes, ext: str) -> bool:
    """Embed a manifest-declared cover in EPUB2 or EPUB3 without losing chapters.

    A valid existing embedded cover is left untouched. A failed operation
    leaves the original EPUB intact; the standalone cover remains available.
    """
    if _epub_cover(epub) is not None:
        return True
    content, extension = covers.validate_image(data)
    if ext != extension:
        raise covers.CoverError("Cover type differs from its extension")
    with ZipFile(epub) as book:
        if book.testzip() is not None:
            raise covers.CoverError("EPUB CRC verification failed")
        container = ET.fromstring(book.read("META-INF/container.xml"))
        rootfile = next((el for el in container.iter()
                         if el.tag.rsplit("}", 1)[-1] == "rootfile"), None)
        if rootfile is None or not rootfile.get("full-path"):
            raise covers.CoverError("EPUB missing OPF package")
        opf = rootfile.get("full-path")
        if opf.startswith("/") or ".." in PurePosixPath(opf).parts:
            raise covers.CoverError("Unsafe EPUB package path")
        root = ET.fromstring(book.read(opf))
        xmlns = root.tag.split("}")[0].removeprefix("{") if "}" in root.tag else ""
        def q(name):
            return f"{{{xmlns}}}{name}" if xmlns else name
        manifest = root.find(q("manifest"))
        metadata = root.find(q("metadata"))
        if manifest is None or metadata is None:
            raise covers.CoverError("EPUB has no metadata or manifest")
        target = posixpath.normpath(posixpath.join(posixpath.dirname(opf), "cover" + ext))
        if target in book.namelist():
            # This cover is not OPF-declared; do not replace unknown EPUB content.
            raise covers.CoverError("EPUB already contains unrecognised cover entry")
        ids = {item.get("id") for item in manifest}
        cover_id = "retriever-cover"
        suffix = 1
        while cover_id in ids:
            suffix += 1
            cover_id = f"retriever-cover-{suffix}"
        version = root.get("version", "2")
        attrs = {"id": cover_id, "href": "cover" + ext,
                 "media-type": "image/png" if ext == ".png" else "image/jpeg"}
        if version.startswith("3"):
            attrs["properties"] = "cover-image"
        ET.SubElement(manifest, q("item"), attrs)
        if not any(el.get("name") == "cover" for el in metadata):
            ET.SubElement(metadata, q("meta"), {"name": "cover", "content": cover_id})
        opf_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with tempfile.NamedTemporaryFile(prefix=".cover-", suffix=".epub",
                                         dir=epub.parent, delete=False) as handle:
            staged = Path(handle.name)
        try:
            with ZipFile(staged, "w", allowZip64=True) as output:
                for item in book.infolist():
                    if item.is_dir():
                        output.writestr(item, b"")
                    else:
                        output.writestr(item, opf_bytes if item.filename == opf
                                        else book.read(item))
                output.writestr(target, content, compress_type=ZIP_STORED)
            if _epub_cover(staged) != (content, extension):
                raise covers.CoverError("Embedded EPUB cover failed verification")
        except BaseException:
            staged.unlink(missing_ok=True)
            raise
    try:
        staged.replace(epub)
    finally:
        staged.unlink(missing_ok=True)
    return True


def _verified_alternative(meta: dict, mapping: dict) -> str | None:
    """Only an explicitly registered exact book match may use another site."""
    try:
        key = canonical_url(meta["source_url"])
    except (KeyError, ValueError, TypeError):
        return None
    item = mapping.get(key)
    if not isinstance(item, dict):
        return None
    normal = lambda x: " ".join(str(x or "").casefold().split())
    if not meta.get("title") or not meta.get("author"):
        return None
    if (normal(meta["title"]) != normal(item.get("title")) or
            normal(meta["author"]) != normal(item.get("author"))):
        return None
    other = item.get("url", "")
    try:
        covers.validate_book_url(other)
    except (ValueError, TypeError):
        return None
    return other


def finalise_book(folder: Path, *, allow_network: bool = True,
                  cache_dir: Path | None = None,
                  verified_sources: dict | None = None) -> dict:
    """Resolve EPUB, existing, cached, exact source page, verified alternative.

    The book's manifest and text files are preserved. The only modified book
    members are cover, source.epub if embedding succeeds, and metadata.json.
    """
    folder = Path(folder)
    meta_path, epub = folder / "metadata.json", folder / "source.epub"
    if not meta_path.is_file() or not epub.is_file():
        raise ValueError("Expected metadata.json and source.epub")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(meta, dict):
        raise ValueError("Invalid novel metadata")
    url = str(meta.get("source_url", ""))
    try:
        identity = canonical_url(url)
    except ValueError:
        identity = ""
    result, method, image_url, warnings = None, "", "", []
    result = _epub_cover(epub)
    if result:
        method = "embedded_epub"
    if not result:
        result = _image_in_folder(folder)
        if result:
            method = "existing_file"
    if not result and cache_dir and identity:
        key = sha256(identity.encode("utf-8")).hexdigest()
        for name in COVER_FILES:
            path = Path(cache_dir) / (key + Path(name).suffix)
            if path.is_file():
                try:
                    data, ext = covers.validate_image(path.read_bytes())
                    if ext == path.suffix:
                        result, method = (data, ext), "verified_cache"
                        break
                except (OSError, covers.CoverError):
                    pass
    if not result and allow_network and identity:
        urls = [(url, "source_page")]
        alternative = _verified_alternative(meta, verified_sources or {})
        if alternative and canonical_url(alternative) != identity:
            urls.append((alternative, "verified_cross_source"))
        for candidate, label in urls:
            try:
                data, ext, image_url = covers.download_site_cover(candidate)
                result, method = (data, ext), label
                break
            except (covers.CoverError, OSError, ValueError) as exc:
                warnings.append(f"{label}: {exc}")
    if result:
        data, ext = result
        name = covers.write_cover(folder, data, ext)
        meta["cover_image"] = name
        if cache_dir and identity:
            cache = Path(cache_dir) / (sha256(identity.encode("utf-8")).hexdigest() + ext)
            cache.parent.mkdir(parents=True, exist_ok=True)
            if not cache.exists():
                cache.write_bytes(data)
        try:
            embedded = embed_cover(epub, data, ext)
        except (OSError, BadZipFile, ET.ParseError, covers.CoverError, KeyError) as exc:
            embedded = False
            warnings.append(f"EPUB embedding: {exc}")
        meta["cover_status"] = "available"
        meta["cover_provenance"] = {
            "method": method, "image_url": image_url or None,
            "sha256": sha256(data).hexdigest(), "embedded": embedded,
        }
    else:
        meta.pop("cover_image", None)
        meta["cover_status"] = "missing"
        meta["cover_provenance"] = {"method": "unavailable", "embedded": False}
    meta["cover_pipeline_version"] = 2
    if warnings:
        meta["cover_warnings"] = warnings[:4]
    else:
        meta.pop("cover_warnings", None)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    return meta


def finalise_archive(path: Path, *, allow_network: bool = True,
                     cache_dir: Path | None = None,
                     verified_sources: dict | None = None) -> dict:
    """Upgrade a portable novel ZIP atomically; do not change filename/layout."""
    path = Path(path)
    with tempfile.TemporaryDirectory(prefix="novel-cover-") as tmp:
        folder = Path(tmp)
        with ZipFile(path) as archive:
            entries = [item for item in archive.infolist() if not item.is_dir()]
            if len(entries) > MAX_FILES or sum(x.file_size for x in entries) > MAX_ZIP_BYTES:
                raise ValueError("ZIP extraction budget exceeded")
            # Reject duplicate names and aliasing before extracting anything.
            # On Windows, case-insensitive paths would otherwise overwrite
            # previously validated files or their provenance metadata.
            names_seen = set()
            for item in entries:
                raw_name = item.filename.replace("\\", "/")
                raw_parts = raw_name.split("/")
                part = PurePosixPath(raw_name)
                if (part.is_absolute() or not part.parts or
                        any(component in ("", ".", "..") or ":" in component
                            for component in raw_parts)):
                    raise ValueError("Unsafe ZIP member")
                key = part.as_posix().casefold()
                if key in names_seen:
                    raise ValueError("Duplicate ZIP member path")
                names_seen.add(key)
                if item.file_size > max(item.compress_size, 1) * 10000:
                    raise ValueError("Suspicious ZIP compression ratio")
            if archive.testzip() is not None:
                raise ValueError("Original ZIP failed CRC verification")
            for item in entries:
                part = PurePosixPath(item.filename.replace("\\", "/"))
                # Refuse Unix symbolic links and device entries.
                if ((item.external_attr >> 16) & 0o170000) == 0o120000:
                    raise ValueError("ZIP contains a symbolic link")
                dest = folder.joinpath(*part.parts)
                dest.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as source, dest.open("wb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
        metas = list(folder.rglob("metadata.json"))
        if len(metas) != 1:
            raise ValueError("Expected exactly one novel metadata.json in ZIP")
        book = metas[0].parent
        if not (book / "chapters.json").is_file():
            raise ValueError("ZIP lacks chapters.json")
        meta = finalise_book(book, allow_network=allow_network,
                             cache_dir=cache_dir, verified_sources=verified_sources)
        with tempfile.NamedTemporaryFile(prefix=".novel-", suffix=".zip",
                                         dir=path.parent, delete=False) as handle:
            staged = Path(handle.name)
        try:
            with ZipFile(staged, "w", allowZip64=True) as dest:
                for member in sorted(folder.rglob("*")):
                    if not member.is_file():
                        continue
                    relative = member.relative_to(folder).as_posix()
                    dest.write(member, arcname=relative,
                               compress_type=ZIP_STORED if relative.endswith(
                                   (".epub", ".png", ".jpg", ".webp")) else ZIP_DEFLATED)
            with ZipFile(staged) as verify:
                if verify.testzip() is not None:
                    raise ValueError("Updated ZIP CRC verification failed")
            staged.replace(path)
        finally:
            staged.unlink(missing_ok=True)
        return meta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--directory", type=Path, help="Root of completed novel folders")
    group.add_argument("--zip", type=Path, help="One existing portable ZIP")
    parser.add_argument("--offline", action="store_true", help="Only reuse local/EPUB covers")
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--verified-sources", type=Path,
                        default=Path("tools/verified_cover_sources.json"))
    args = parser.parse_args(argv)
    mapping = {}
    if args.verified_sources.is_file():
        mapping = json.loads(args.verified_sources.read_text(encoding="utf-8"))
    if args.zip:
        books = [args.zip]
    else:
        books = sorted(set(p.parent for p in args.directory.rglob("metadata.json")
                           if (p.parent / "source.epub").is_file()))
    if not books:
        parser.error("No complete novel folders or ZIPs found")
    for book in books:
        result = (finalise_archive(book, allow_network=not args.offline,
                                  cache_dir=args.cache_dir, verified_sources=mapping)
                  if args.zip else
                  finalise_book(book, allow_network=not args.offline,
                                cache_dir=args.cache_dir, verified_sources=mapping))
        print(f"COVER {result.get('cover_status')} {result.get('title', '')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
