#!/usr/bin/env python3
"""Bounded, read-only check of ordinary unauthenticated WebNovel chapter access.

This is NOT a novel downloader. Makes at most one book-page request and five
explicit chapter-page requests. Saves no response HTML or chapter text. Stops
on access restrictions, unexpected layout, incomplete content or rate limits.
"""
from __future__ import annotations

import argparse
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from bs4 import BeautifulSoup

from tools.webnovel_probe import parse_public_book_metadata, validate_book_url
from tools.webnovel_public_two_chapter import (
    PublicChapterError, _chapter_url, parse_public_chapter,
)

MAX_HTML_BYTES = 4 * 1024 * 1024
MAX_SAMPLES = 5
USER_AGENT = "NovelLibraryPublicFeasibility/0.1"


class AccessProbeError(ValueError):
    """Requested public page was unavailable or unsuitable."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Refuse redirects, including non-WebNovel destinations.


def fetch_public_html(url: str) -> str:
    """Single normal HTTP GET. No cookies, proxy configuration or retry loop."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    try:
        with build_opener(NoRedirect()).open(request, timeout=12) as response:
            if response.geturl() != url:
                raise AccessProbeError("redirected")
            if response.headers.get("cf-mitigated", "").lower() == "challenge":
                raise AccessProbeError("access_challenge")
            if response.headers.get_content_type() not in ("text/html", "application/xhtml+xml"):
                raise AccessProbeError("unexpected_content_type")
            body = response.read(MAX_HTML_BYTES + 1)
            if len(body) > MAX_HTML_BYTES:
                raise AccessProbeError("oversized_response")
    except HTTPError as exc:
        code = exc.code
        exc.close()
        if code in (401, 403, 429):
            raise AccessProbeError(f"HTTP_{code}_access_denied") from None
        raise AccessProbeError(f"HTTP_{code}") from None
    except (URLError, TimeoutError, OSError):
        raise AccessProbeError("network_error") from None
    html = body.decode("utf-8-sig", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True).lower() if soup.title else ""
    if "just a moment" in title or "attention required" in title:
        raise AccessProbeError("access_challenge")
    if not soup.select_one("h1, .cha-content, #chapter-content, .chapter-content"):
        visible = soup.get_text(" ", strip=True).lower()
        if any(v in visible for v in ("verify you are human", "checking your browser")):
            raise AccessProbeError("access_challenge")
    return html


def _validate_samples(book_url: str, samples: list[tuple[int, str]]) -> list[tuple[int, str]]:
    book_id = re.search(r"([0-9]{6,})/?$", book_url).group(1)
    if not isinstance(samples, list) or not 1 <= len(samples) <= MAX_SAMPLES:
        raise AccessProbeError("Supply 1 to 5 explicit public chapter samples")
    seen_numbers, seen_urls, checked = set(), set(), []
    for number, link in samples:
        if type(number) is not int or number < 1 or number > 10000:
            raise AccessProbeError("Invalid chapter number")
        try:
            canonical = _chapter_url(link, book_id)
        except (PublicChapterError, ValueError) as exc:
            raise AccessProbeError("Unsafe chapter URL for selected book") from exc
        if number in seen_numbers or canonical in seen_urls:
            raise AccessProbeError("Duplicate chapter number or URL")
        seen_numbers.add(number)
        seen_urls.add(canonical)
        checked.append((number, canonical))
    return checked


def check_public_samples(book_url: str, samples: list[tuple[int, str]],
                         *, fetcher=fetch_public_html) -> dict:
    """Return metadata and evidence only; no chapter prose or pages."""
    book_url = validate_book_url(book_url)
    checked = _validate_samples(book_url, samples)  # Validate all URLs before network.
    report = {"book_url": book_url, "outcome": "unverified",
              "requested_samples": len(checked), "samples": [],
              "complete_novel_download_verified": False}
    try:
        book = fetcher(book_url)
        meta = parse_public_book_metadata(book, book_url)
    except AccessProbeError as exc:
        report["outcome"] = "blocked"
        report["reason"] = str(exc)
        return report
    except ValueError:
        report["outcome"] = "unverified"
        report["reason"] = "book_metadata_layout_unrecognised"
        return report
    report["title"] = meta["title"]
    report["author"] = meta["author"]
    report["listed_chapters"] = meta["listed_chapters"]
    if meta["listed_chapters"] is not None and any(
        n > meta["listed_chapters"] for n, _ in checked
    ):
        report["reason"] = "sample_exceeds_listed_chapters"
        return report
    for number, url in checked:
        try:
            html = fetcher(url)
            body = parse_public_chapter(html, url, f"Chapter {number}")
            if len(body) < 100 or len(body.split()) < 20:
                raise AccessProbeError("chapter_body_too_short")
        except (AccessProbeError, PublicChapterError) as exc:
            reason = str(exc)
            # Do not include arbitrary chapter text in the report.
            if "locked" in reason.lower():
                reason = "locked_chapter"
            elif reason not in {
                "access_challenge", "redirected", "oversized_response",
                "unexpected_content_type", "network_error", "chapter_body_too_short"
            } and not re.fullmatch(r"HTTP_\d+(?:_access_denied)?", reason):
                reason = "unrecognised_or_incomplete_chapter"
            report["samples"].append({"chapter": number, "status": "unavailable",
                                      "reason": reason})
            report["outcome"] = "blocked"
            return report  # No further requests after a denial or unreadable body.
        report["samples"].append({"chapter": number, "status": "public_readable",
                                  "characters": len(body), "words": len(body.split())})
    report["outcome"] = "sampled_public_readable"
    report["reason"] = ("Sampled chapters are readable; this does not establish all "
                        "chapters are free or that their text may be archived.")
    return report


def _sample(raw: str) -> tuple[int, str]:
    number, separator, url = raw.partition("=")
    if not separator or not number.isdecimal() or not url:
        raise argparse.ArgumentTypeError("Sample format: CHAPTER=HTTPS_WEBNOVEL_URL")
    return int(number), url


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-url", required=True)
    parser.add_argument("--sample", type=_sample, action="append", required=True,
                        help="Chapter position and its public link, e.g. 1=https://...")
    args = parser.parse_args(argv)
    try:
        report = check_public_samples(args.book_url, args.sample)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # A successful diagnostic execution is NOT proof that the website is accessible.
    # Callers must inspect the explicit "outcome" and "reason" fields.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
