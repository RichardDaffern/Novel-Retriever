#!/usr/bin/env python3
"""Read-only, local Chromium check of a few ordinary public WebNovel pages.

Makes at most one book navigation and three explicitly supplied chapter
navigations. It does NOT save HTML, story text, cookies, screenshots or EPUBs.
The browser uses a fresh, unmodified, temporary context. No login, cookies
from a user's profile, challenges, proxies, retries or hidden APIs.
This tool does not establish archiving permission or complete-book access.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from tools.webnovel_access_check import AccessProbeError, _validate_samples
from tools.webnovel_browser_probe import (
    BrowserProbeError, PAGE_TIMEOUT_MS, _checked_page,
)
from tools.webnovel_probe import (
    WebNovelProbeError, parse_public_book_metadata, validate_book_url,
)
from tools.webnovel_public_two_chapter import PublicChapterError, parse_public_chapter

MAX_SAMPLES = 3
MIN_CHAPTER_WORDS = 20


def _safe_reason(error: Exception) -> str:
    """Do not log page content, traces or URLs from third-party exceptions."""
    message = str(error).lower()
    if "http 403" in message or "403" in message:
        return "http_403_access_denied"
    if "http 401" in message or "401" in message:
        return "http_401_access_denied"
    if "http 429" in message or "429" in message:
        return "http_429_rate_limited"
    if "challenge" in message or "verify you are human" in message:
        return "browser_access_challenge"
    if "redirect" in message:
        return "redirected_to_another_page"
    if "locked" in message or "unlock" in message:
        return "locked_chapter"
    if "timeout" in message or "timed out" in message:
        return "navigation_timeout"
    if "browser" in message or "navigation" in message or "net::" in message:
        return "browser_navigation_failed"
    return "chapter_body_unavailable_or_unrecognised"


def diagnose_in_browser(book_url: str, samples: list[tuple[int, str]], *, chromium) -> dict:
    """Inspect only the selected pages, returning facts, never source text.

    All URLs are validated *before* launching the browser, so malformed or
    different-book URLs cannot produce network requests.
    """
    book_url = validate_book_url(book_url)
    if len(samples) > MAX_SAMPLES:
        raise AccessProbeError("Local browser check allows up to three sample chapters")
    checked = _validate_samples(book_url, samples)
    report = {
        "book_url": book_url,
        "outcome": "unverified",
        "requested_samples": len(checked),
        "samples": [],
        "complete_novel_download_verified": False,
        "chapter_text_saved": False,
        "archive_permission_verified": False,
    }
    # Headed browser, ordinary default context. No shared Chrome user profile.
    # All website requests are normal navigation through Chromium.
    try:
        browser = chromium.launch(headless=False, timeout=PAGE_TIMEOUT_MS)
    except Exception as exc:
        report["outcome"] = "browser_setup_failed"
        report["reason"] = _safe_reason(exc)
        return report
    try:
        context = browser.new_context()
        try:
            page = context.new_page()
            try:
                book_html = _checked_page(page, book_url)
            except BrowserProbeError as exc:
                report["outcome"] = "blocked"
                report["reason"] = _safe_reason(exc)
                return report

            try:
                metadata = parse_public_book_metadata(book_html, book_url)
            except WebNovelProbeError:
                report["reason"] = "public_book_metadata_unrecognised"
                return report
            report.update({
                "title": metadata["title"],
                "author": metadata["author"],
                "listed_chapters": metadata["listed_chapters"],
            })
            count = metadata["listed_chapters"]
            if count is not None and any(number > count for number, _ in checked):
                report["reason"] = "sample_beyond_listed_chapters"
                return report

            for number, url in checked:
                try:
                    html = _checked_page(page, url)
                    text = parse_public_chapter(html, url, f"Chapter {number}")
                    words = len(text.split())
                    if words < MIN_CHAPTER_WORDS:
                        raise PublicChapterError("Chapter body unexpectedly short")
                except (BrowserProbeError, PublicChapterError) as exc:
                    report["samples"].append({
                        "chapter": number, "status": "unavailable",
                        "reason": _safe_reason(exc),
                    })
                    report["outcome"] = "blocked"
                    return report
                report["samples"].append({
                    "chapter": number,
                    "status": "public_readable",
                    "words": words,
                    "characters": len(text),
                })
                del html, text
            report["outcome"] = "sampled_public_readable"
            report["reason"] = (
                "Only the sampled chapter pages were readable in a temporary "
                "local browser. No content was saved. This does not verify "
                "full-book access or permission to export."
            )
            return report
        finally:
            context.close()
    finally:
        browser.close()


def _sample(raw: str) -> tuple[int, str]:
    number, separator, url = raw.partition("=")
    if not separator or not number.isdecimal() or not url:
        raise argparse.ArgumentTypeError(
            "Format: CHAPTER_NUMBER=https://www.webnovel.com/book/<book-id>/<chapter-id>"
        )
    return int(number), url


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-url", required=True, help="Public WebNovel book URL")
    parser.add_argument(
        "--sample", action="append", type=_sample, required=True,
        help="Repeat up to three times: NUMBER=https://www.webnovel.com/book/...",
    )
    args = parser.parse_args(argv)
    # Validate everything before importing or launching Playwright.
    try:
        book_url = validate_book_url(args.book_url)
        if len(args.sample) > MAX_SAMPLES:
            raise AccessProbeError("At most three sample chapters are allowed")
        _validate_samples(book_url, args.sample)
    except (AccessProbeError, WebNovelProbeError) as exc:
        parser.error(str(exc))
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright is not installed. Run: "
            "py -m pip install playwright && py -m playwright install chromium",
            file=sys.stderr,
        )
        return 2
    try:
        with sync_playwright() as playwright:
            report = diagnose_in_browser(book_url, args.sample, chromium=playwright.chromium)
    except Exception as exc:
        print("Local browser check failed: " + _safe_reason(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["outcome"] == "sampled_public_readable" else 1


if __name__ == "__main__":
    raise SystemExit(main())
