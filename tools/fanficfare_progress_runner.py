#!/usr/bin/env python3
"""Run FanFicFare CLI while reporting chapter counts and percentages.

FanFicFare's --progressbar outputs a dot per network fetch, not per chapter.
This wrapper uses FanFicFare's chapter-completion notification callback.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from bs4 import BeautifulSoup


# The original author never published ISSTH Chapter 690. The public page
# explicitly labels it "The Chapter that Never Was" and says 689 jumps to 691.
# Only this exact, publicly verified missing-number entry may be represented by
# a transparent editorial note when FanFicFare returns genuinely blank HTML.
# Do not introduce generic empty-chapter tolerance.
VERIFIED_SKIP_URL = "https://novelfull.com/i-shall-seal-the-heavens/chapter-690.html"
VERIFIED_SKIP_NOTE = (
    "<p>Editorial numbering note: The original author deliberately omitted "
    "Chapter 690, moving directly from Chapter 689 to Chapter 691. "
    "No story text was published for this numbered chapter.</p>"
)


def _preserve_verified_editorial_skip(url: str, index: int, title: str,
                                      html: str | bytes) -> str | bytes:
    if index != 689 or not re.search(r"\bchapter\s+690\b", title, re.I):
        return html
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in
            ("novelfull.com", "www.novelfull.com") or parsed.port is not None
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path != "/i-shall-seal-the-heavens/chapter-690.html"):
        return html
    if BeautifulSoup(html, "html.parser").get_text(" ", strip=True):
        return html
    print("Verified author-omitted ISSTH Chapter 690: preserving editorial note",
          flush=True)
    return VERIFIED_SKIP_NOTE


def _diagnostic_source_url(url: str | None) -> str:
    """Return a chapter URL without credentials or query-string values."""
    if not url:
        return "<unknown source URL>"
    try:
        parsed = urlsplit(url)
        if not parsed.scheme or not parsed.hostname:
            return "<unparseable source URL>"
        host = parsed.hostname
        if parsed.port is not None:
            host = f"{host}:{parsed.port}"
        query_keys = parse_qsl(parsed.query, keep_blank_values=True)
        safe_query = "&".join(f"{key}=[redacted]" for key, _ in query_keys)
        return urlunsplit((parsed.scheme, host, parsed.path, safe_query, ""))
    except ValueError:
        return "<unparseable source URL>"


def _checkpoint_chapter(folder: Path, index: int, title: str, html: str | bytes,
                      source_url: str | None = None) -> Path:
    """Save a successfully fetched chapter before EPUB creation."""
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select("script, style"):
        el.decompose()
    lines = [p.get_text(" ", strip=True) for p in soup.find_all(("p", "blockquote", "pre", "li"))]
    lines = [p for p in lines if p]
    body = "\n\n".join(lines) if lines else soup.get_text("\n", strip=True)
    if not body.strip():
        raise ValueError(
            f"Downloaded chapter {index+1} ({str(title)[:160]!r}) was empty at "
            f"{_diagnostic_source_url(source_url)}"
        )
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"chapter_{index+1:05d}.txt"
    temporary = destination.with_suffix(".txt.tmp")
    temporary.write_text(f"{title}\n\n{body.strip()}\n", encoding="utf-8")
    temporary.replace(destination)
    return destination


def progress_reporter(writer):
    """Return a callback reporting progress for the selected chapter range."""
    adapter = writer.adapter
    count = len(adapter.chapterInfos)
    first = adapter.chapterFirst if adapter.chapterFirst is not None else 0
    last = adapter.chapterLast if adapter.chapterLast is not None else count - 1
    first = max(0, first)
    last = min(count - 1, last)
    total = max(0, last - first + 1)
    completed = 0
    print(f"Chapter range: {total} selected of {count} chapters", flush=True)

    # Chapter content is saved as soon as FanFicFare returns it.
    # This runs before the EPUB is written, so an interrupted job leaves files.
    if hasattr(adapter, "getChapterTextNum"):
        original_fetch = adapter.getChapterTextNum
        checkpoint_dir = Path.cwd() / "chapters_in_progress"
        def checkpointing_fetch(url, index):
            html = original_fetch(url, index)
            if first <= index <= last:
                heading = adapter.chapterInfos[index].get("title", f"Chapter {index+1}")
                html = _preserve_verified_editorial_skip(url, index, heading, html)
                file = _checkpoint_chapter(checkpoint_dir, index, heading, html, source_url=url)
                print(f"Saved checkpoint: {file.name}", flush=True)
            return html
        adapter.getChapterTextNum = checkpointing_fetch

    def notify(_fraction, _url):
        nonlocal completed
        completed += 1
        if total:
            print(f"Chapters processed: {completed}/{total} ({100 * completed / total:.1f}%)", flush=True)

    return notify


def main(argv: list[str] | None = None):
    """Delegate site access, configuration and EPUB creation to FanFicFare."""
    from fanficfare import cli
    from fanficfare.writers.base_writer import BaseStoryWriter
    try:
        from tools import novelfull_http
    except ModuleNotFoundError:
        # Invoked as a file from another working directory by the EPUB CLI.
        import novelfull_http


    # Only the NovelFull host uses the bounded stdlib HTTPS fetcher.
    novelfull_http.enable()
    original = BaseStoryWriter.writeStory

    def patched(self, *args, **kwargs):
        if not kwargs.get("metaonly", False) and "notification" not in kwargs and len(args) < 5:
            kwargs["notification"] = progress_reporter(self)
        return original(self, *args, **kwargs)

    BaseStoryWriter.writeStory = patched
    try:
        cli.main(argv if argv is not None else sys.argv[1:])
    finally:
        BaseStoryWriter.writeStory = original
        novelfull_http.disable()


if __name__ == "__main__":
    main()
