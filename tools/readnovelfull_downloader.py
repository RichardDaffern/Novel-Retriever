#!/usr/bin/env python3
"""Download authorised ReadNovelFull chapters into verified EPUB/TXT artefacts.

One sequential chapter request per second per batch; no proxy, login, challenge
bypass or automatic retries. Full books are split by the Actions workflow.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from http.client import RemoteDisconnected, IncompleteRead
import json
from pathlib import Path
import re
import sys
import time

from novel_downloader import epub_chapters, slugify
from tools.chunked_download import _epub
from tools.freewebnovel_downloader import _write_json, _validate_saved_row
from tools.readnovelfull_source import (
    SourceError, discover, extract_chapter, validate_book_url, fetch_public_html,
)

MAX_PER_RUN = 100


class DownloadError(ValueError):
    """A chapter batch cannot be safely completed."""


# Network retry is narrowly scoped to transient transport interruptions.
# Never retry 403/429, anti-bot challenges, access restrictions, wrong chapter
# identity or catalogue inconsistencies.
TRANSIENT_TRANSPORT_TEXT = (
    "connection reset", "connection aborted", "timed out",
    "remote end closed connection", "broken pipe",
)


def _transient_transport_error(exc: Exception) -> bool:
    if isinstance(exc, (RemoteDisconnected, IncompleteRead, ConnectionResetError,
                        ConnectionAbortedError, TimeoutError, BrokenPipeError)):
        return True
    if isinstance(exc, SourceError):
        message = str(exc).casefold()
        return message.startswith("readnovelfull not reachable:") and any(
            marker in message for marker in TRANSIENT_TRANSPORT_TEXT
        )
    return False


def fetch_chapter_with_retry(url: str, *, fetcher, sleeper, attempts=3) -> str:
    """Boundedly retry only network drops for this exact chapter URL.

    A successful chapter still passes extract_chapter and SHA-256 validation.
    Retries have 5s/15s back-off and never change URL or bypass any restriction.
    """
    if not 1 <= attempts <= 3:
        raise ValueError("Transport retry attempts must be within 1..3")
    delays = (5, 15)
    for attempt in range(attempts):
        try:
            return fetcher(url)
        except (RemoteDisconnected, IncompleteRead, ConnectionResetError,
                ConnectionAbortedError, TimeoutError, BrokenPipeError, SourceError) as exc:
            if not _transient_transport_error(exc) or attempt == attempts - 1:
                raise
            print(f"ReadNovelFull transient network interruption on the exact URL "
                  f"(attempt {attempt + 1}/{attempts}): {type(exc).__name__}; "
                  f"backing off {delays[attempt]}s", flush=True)
            sleeper(delays[attempt])
    raise AssertionError("Unreachable retry state")


def download_range(url: str, first: int, last: int, output_dir: Path, *,
                   confirm_rights=False, fetcher=fetch_public_html,
                   sleeper=time.sleep, image_fetcher=None) -> dict:
    if not confirm_rights:
        raise DownloadError("--confirm-rights is required before any website request")
    url = validate_book_url(url)
    if first < 1 or last < first or last - first + 1 > MAX_PER_RUN:
        raise DownloadError("A batch must contain 1 to 100 consecutive chapters")
    details = discover(url, fetcher=fetcher, allow_verified_prefix=True)
    if last > details["numChapters"]:
        raise DownloadError(f"Chapter {last} exceeds the discovered book index")
    expected = details["chapters"][first - 1:last]
    if [r["position"] for r in expected] != list(range(first, last + 1)):
        raise DownloadError("Selected chapters do not form a continuous range")

    folder = Path(output_dir) / (
        slugify(details["title"]) + f"-chapters-{first:05d}-{last:05d}")
    folder.mkdir(parents=True, exist_ok=True)
    cover_name = next((n for n in ("cover.jpg", "cover.png")
                       if (folder / n).is_file()), "")
    if not cover_name:
        from tools.novel_covers import (
            CoverError, download_site_cover, fetch_image, write_cover,
        )
        try:
            data, ext, _ = download_site_cover(
                url, html=fetcher(url), image_fetcher=image_fetcher or fetch_image)
            cover_name = write_cover(folder, data, ext)
        except CoverError as exc:
            print(f"WARNING: ReadNovelFull cover unavailable: {exc}", flush=True)

    checkpoint = folder / ".progress.json"
    prior = {}
    if checkpoint.is_file():
        old = json.loads(checkpoint.read_text(encoding="utf-8"))
        if (old.get("url"), old.get("first"), old.get("last")) != (url, first, last):
            raise DownloadError("Saved checkpoint has a different novel identity")
        prior = {row["position"]: row for row in old.get("chapters", [])}
    elif (folder / "chapters.json").exists():
        rows = json.loads((folder / "chapters.json").read_text(encoding="utf-8"))
        if (len(rows) == len(expected)
                and all(_validate_saved_row(folder, row, position)
                        for row, position in zip(rows, range(first, last + 1)))
                and (folder / "source.epub").is_file()):
            _, ebook_chapters = epub_chapters(folder / "source.epub")
            if len(ebook_chapters) == len(expected):
                return {"title": details["title"], "author": details["author"],
                        "chapter_count": len(rows), "source_url": url,
                        "output_dir": str(folder)}

    written = {}
    for chapter in expected:
        position = chapter["position"]
        if position in prior and _validate_saved_row(folder, prior[position], position):
            written[position] = prior[position]
            continue
        sleeper(1)
        item = extract_chapter(fetch_chapter_with_retry(
                                   chapter["url"], fetcher=fetcher, sleeper=sleeper),
                               number=chapter.get("chapter_number", position),
                               title=chapter["title"],
                               printed_label=chapter.get("printed_label"))
        content = f"{item['title']}\n\n{item['text'].strip()}\n"
        digest = sha256(content.encode("utf-8")).hexdigest()
        if any(row["sha256"] == digest for row in written.values()):
            raise DownloadError(f"Chapter {position} repeats earlier content")
        name = f"chapter_{position:05d}.txt"
        (folder / name).write_bytes(content.encode("utf-8"))
        written[position] = {
            "position": position,
            "chapter_number": chapter.get("chapter_number", position),
            "title": item["title"], "file": name,
            "word_count": len(item["text"].split()), "sha256": digest,
        }
        _write_json(checkpoint, {
            "url": url, "first": first, "last": last,
            "chapters": [written[k] for k in sorted(written)],
        })
        print(f"VERIFIED ReadNovelFull Chapter {position}", flush=True)

    rows = [written[n] for n in range(first, last + 1)]
    if not all(_validate_saved_row(folder, row, n)
               for row, n in zip(rows, range(first, last + 1))):
        raise DownloadError("Chapter checksums failed; no EPUB published")
    _epub(folder, rows, details["title"], details["author"], "en", url,
          description=details["description"], genres=details["genres"],
          status=details["status"],
          cover_path=(folder / cover_name if cover_name else None))
    _, actual = epub_chapters(folder / "source.epub")
    if len(actual) != len(rows):
        raise DownloadError("EPUB has a different chapter count; stopped")
    metadata = {
        "title": details["title"], "author": details["author"],
        "description": details["description"], "genres": details["genres"],
        "status": details["status"], "language": "en", "source_url": url,
        "chapter_count": len(rows), "format": "epub",
        "chapter_files": "UTF-8 TXT", "cover_pipeline_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if cover_name:
        metadata["cover_image"] = cover_name
    _write_json(folder / "chapters.json", rows)
    _write_json(folder / "metadata.json", metadata)
    checkpoint.unlink(missing_ok=True)
    return {
        "title": details["title"], "author": details["author"],
        "chapter_count": len(rows), "source_url": url, "output_dir": str(folder),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--chapter-range", default="")
    parser.add_argument("--output-dir", type=Path, default=Path("downloads"))
    parser.add_argument("--confirm-rights", action="store_true")
    args = parser.parse_args(argv)
    try:
        url = validate_book_url(args.url)
        if not args.confirm_rights:
            raise DownloadError("--confirm-rights is required")
        if args.list_only:
            details = discover(url)
            # Avoid dumping 20k chapter links in Actions logs.
            for field in ("chapters", "novel_id"):
                details.pop(field, None)
            print(json.dumps(details, ensure_ascii=False, indent=2))
            return 0
        match = re.fullmatch(r"([1-9][0-9]*)-([1-9][0-9]*)", args.chapter_range)
        if not match:
            raise DownloadError("Use --chapter-range 1-50 or the full-book workflow")
        first, last = map(int, match.groups())
        print(json.dumps(download_range(
            url, first, last, args.output_dir, confirm_rights=True
        ), ensure_ascii=False, indent=2))
        return 0
    except (DownloadError, SourceError, OSError, ValueError) as exc:
        print(f"ReadNovelFull download stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
