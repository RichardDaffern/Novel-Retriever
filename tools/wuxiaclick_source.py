#!/usr/bin/env python3
"""Strict WuxiaClick book/page adapter for authorised, bounded requests.

The catalogue is server-rendered and paginated. Every chapter URL must be
present in the actual book-specific index. URL suffixes are source identifiers,
NOT chapter positions (e.g. Chapter 0 can be URL -1). No guessed chapter links,
login, redirects, CAPTCHA bypass, undocumented endpoints or automatic retries.
"""
from __future__ import annotations

import re
import time
from functools import lru_cache
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

HOST = "wuxia.click"
BOOK = re.compile(r"^/novel/([a-z0-9]+(?:-[a-z0-9]+)*)$")
CHAPTER = re.compile(r"^/chapter/([a-z0-9]+(?:-[a-z0-9]+)*)-([1-9][0-9]*)$")
USER_AGENT = "NovelLibraryWuxiaClick/1.0 (github.com/RichardDaffern/Novel_Library)"
MAX_HTML = 3 * 1024 * 1024
MAX_PAGES = 250
MAX_CHAPTERS = 20000
MIN_CHAPTER_CHARS = 200
LOCK_MARKERS = (
    "unlock this chapter", "purchase this chapter", "subscribe to unlock",
    "this chapter is locked", "verify you are human", "captcha",
    "please enable javascript", "just a moment", "too many requests",
    "download allowance", "daily limit",
)


class SourceError(ValueError):
    """Invalid source URL, incomplete index, access challenge or unsafe content."""


def _parts(url: str):
    try:
        p = urlsplit(url)
        port = p.port
    except ValueError as exc:
        raise SourceError("Malformed WuxiaClick URL") from exc
    if (p.scheme != "https" or p.hostname not in (HOST, "www." + HOST)
            or p.username or p.password or port is not None or p.fragment):
        raise SourceError("Only public HTTPS WuxiaClick novel URLs are supported")
    return p


def validate_book_url(url: str) -> str:
    p = _parts(url.strip())
    if p.query or not BOOK.fullmatch(p.path):
        raise SourceError("Expected https://wuxia.click/novel/book-slug")
    return "https://" + HOST + p.path


def validate_chapter_url(url: str, slug: str = "") -> tuple[str, int]:
    p = _parts(url)
    match = CHAPTER.fullmatch(p.path)
    if not match or p.query:
        raise SourceError("Unrecognised WuxiaClick chapter URL")
    if slug and match.group(1) != slug:
        raise SourceError("Chapter link belongs to a different novel")
    return "https://" + HOST + p.path, int(match.group(2))


def catalogue_page_url(book_url: str, page: int) -> str:
    book_url = validate_book_url(book_url)
    if type(page) is not int or not 1 <= page <= MAX_PAGES:
        raise SourceError("Invalid catalogue page number")
    return book_url if page == 1 else f"{book_url}?page={page}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError("Unexpected redirect; no access workaround attempted")


@lru_cache(maxsize=1)
def _robots() -> RobotFileParser:
    """Fail closed if the site's current robots rules cannot be verified."""
    try:
        with build_opener(NoRedirect()).open(Request(
            "https://" + HOST + "/robots.txt",
            headers={"User-Agent": USER_AGENT, "Accept": "text/plain"},
        ), timeout=15) as response:
            if response.status != 200 or response.headers.get_content_type() not in (
                    "text/plain", "text/html"):
                raise SourceError("Unable to verify WuxiaClick robots rules")
            raw = response.read(128001)
            if len(raw) > 128000:
                raise SourceError("Robots policy exceeds size limit")
    except (HTTPError, URLError) as exc:
        raise SourceError("WuxiaClick robots policy unavailable; stopped") from exc
    rules = RobotFileParser()
    rules.parse(raw.decode("utf-8-sig", errors="replace").splitlines())
    return rules


def fetch_public_html(url: str) -> str:
    p = _parts(url)
    if BOOK.fullmatch(p.path):
        if p.query:
            q = parse_qs(p.query, strict_parsing=True)
            if set(q) != {"page"} or len(q["page"]) != 1:
                raise SourceError("Unrecognised book page query")
            value = q["page"][0]
            if not value.isascii() or not value.isdecimal():
                raise SourceError("Invalid book page number")
            if catalogue_page_url("https://" + HOST + p.path, int(value)) != url:
                raise SourceError("Unexpected book page query syntax")
    elif CHAPTER.fullmatch(p.path) and not p.query:
        pass
    else:
        raise SourceError("Refusing non-book/non-chapter URL")
    if not _robots().can_fetch(USER_AGENT, url):
        raise SourceError("Site robots policy does not permit this URL; stopped")
    try:
        with build_opener(NoRedirect()).open(Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html",
        }), timeout=25) as response:
            if response.status != 200 or response.headers.get(
                    "cf-mitigated", "").lower() == "challenge":
                raise SourceError("Access challenge or unexpected HTTP status")
            if response.headers.get_content_type() not in (
                    "text/html", "application/xhtml+xml"):
                raise SourceError("WuxiaClick response was not HTML")
            data = response.read(MAX_HTML + 1)
            if len(data) > MAX_HTML:
                raise SourceError("WuxiaClick HTML exceeds the 3 MiB limit")
    except HTTPError as exc:
        raise SourceError(f"WuxiaClick returned HTTP {exc.code}; stopped") from exc
    except URLError as exc:
        raise SourceError(f"WuxiaClick is not reachable: {exc.reason}") from exc
    content = data.decode("utf-8-sig", errors="replace")
    title = BeautifulSoup(content, "html.parser").title
    if title and any(x in title.get_text(" ", strip=True).casefold()
                     for x in ("just a moment", "access denied", "attention required")):
        raise SourceError("Access challenge returned instead of a novel")
    return content


def _catalogue_section(page: str, book_url: str):
    soup = BeautifulSoup(page, "html.parser")
    section = soup.select_one("section#chapters")
    if not section:
        raise SourceError("Recognised chapter index section is missing")
    book_title = soup.select_one("h1")
    if book_title is None or not book_title.get_text(" ", strip=True):
        raise SourceError("Book identity is missing")
    # The site places first/latest navigation above this section. Its chapter
    # rows are in an ordered list; never mix other site navigation into the TOC.
    return soup, section, book_title.get_text(" ", strip=True)


def book_metadata(page: str, url: str) -> dict:
    url = validate_book_url(url)
    soup, section, title = _catalogue_section(page, url)
    if len(title) > 260:
        raise SourceError("Implausibly long book title")
    visible = soup.get_text(" ", strip=True)
    header = re.search(r"(?i)\b([\d,]+)\s+chapters?,\s+numbered\b",
                       section.get_text(" ", strip=True))
    if not header:
        raise SourceError("Authoritative chapter count was not found")
    count = int(header.group(1).replace(",", ""))
    if not 1 <= count <= MAX_CHAPTERS:
        raise SourceError("Implausible chapter count")
    author = "Unknown"
    # Site displays a short 'by <author>' label next to the book name.
    for tag in soup.select("a,span,p,div"):
        label = tag.get_text(" ", strip=True)
        if label.lower().startswith("by ") and 3 <= len(label) <= 110:
            author = label[3:].strip() or "Unknown"
            break
    description = ""
    # A styled heading may contain child spans/icons, so matching its direct
    # .string is too strict for the live WuxiaClick page.
    heading = next(
        (node for node in soup.find_all(["h2", "h3", "h4"])
         if node.get_text(" ", strip=True).casefold() == "synopsis"), None)
    if heading:
        node = heading.find_next(["p", "div"])
        if node:
            description = node.get_text(" ", strip=True)[:16000]
    genres = []
    for a in soup.select("a[href*='/category/']"):
        word = a.get_text(" ", strip=True)
        if word and word not in genres:
            genres.append(word)
    status = "Completed" if re.search(
        r"\bCompleted\b", visible[:4500]) else ""
    return {
        "title": title, "author": author,
        "description": description, "genres": genres[:30], "status": status,
        "source_url": url, "numChapters": count,
    }


def _index_rows(page: str, book_url: str) -> tuple[str, list[dict], set[int]]:
    book_url = validate_book_url(book_url)
    slug = BOOK.fullmatch(urlsplit(book_url).path).group(1)
    soup, section, book_title = _catalogue_section(page, book_url)
    result = []
    used = set()
    for anchor in section.select("ol li a[href]"):
        absolute = urljoin(book_url, anchor["href"])
        canonical, source_number = validate_chapter_url(absolute, slug)
        if canonical in used:
            raise SourceError("Duplicate chapter link on one index page")
        used.add(canonical)
        label = anchor.get_text(" ", strip=True)
        if not label:
            raise SourceError("Empty chapter label")
        # The public TOC renders 'Chapter <source-id> , <actual title> DATE'.
        # Chapter 0 may be source URL -1, and an afterword may be unnumbered.
        title = re.sub(r"(?i)^chapter\s+[\d,]+\s*[,;:]\s*", "", label).strip()
        title = re.sub(
            r"\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"\s+[0-9]{1,2},\s+[0-9]{4}$", "", title, flags=re.I).strip()
        if not title or len(title) > 260:
            raise SourceError("Invalid chapter title in index")
        result.append({"source_number": source_number, "url": canonical, "title": title})
    if not result or len(result) > 100:
        raise SourceError("Chapter page has no entries or unexpectedly many")
    links: set[int] = set()
    for a in section.select("a[href]"):
        target = urljoin(book_url, a["href"])
        p = urlsplit(target)
        if (p.scheme != "https" or p.hostname != HOST or
                p.path != urlsplit(book_url).path or not p.query):
            continue
        try:
            q = parse_qs(p.query, strict_parsing=True)
        except ValueError:
            continue
        if set(q) == {"page"} and len(q["page"]) == 1 and q["page"][0].isascii() and q["page"][0].isdecimal():
            number = int(q["page"][0])
            if 2 <= number <= MAX_PAGES:
                links.add(number)
    return book_title, result, links


def discover(book_url: str, *, fetcher=fetch_public_html,
             sleeper=time.sleep) -> dict:
    book_url = validate_book_url(book_url)
    book_html = fetcher(book_url)
    meta = book_metadata(book_html, book_url)
    title, first, pages = _index_rows(book_html, book_url)
    expected_pages = (meta["numChapters"] + 99) // 100
    if (title != meta["title"] or
            pages != set(range(2, expected_pages + 1))):
        raise SourceError("Incomplete or unexpected catalogue pagination")
    rows = first[:]
    for page_number in range(2, expected_pages + 1):
        sleeper(1)
        got_title, group, _ = _index_rows(
            fetcher(catalogue_page_url(book_url, page_number)), book_url)
        if got_title != title:
            raise SourceError("Catalogue page belongs to a different book")
        rows.extend(group)
    if len(rows) != meta["numChapters"]:
        raise SourceError(
            f"Catalogue incomplete: reported {meta['numChapters']}, "
            f"collected {len(rows)} chapter entries")
    sources = [r["source_number"] for r in rows]
    if len(set(sources)) != len(sources) or sources != sorted(sources):
        raise SourceError("Duplicate or out-of-order source chapter links")
    for position, row in enumerate(rows, 1):
        row["position"] = position
    meta["chapters"] = rows
    return meta


def extract_chapter(page: str, *, title: str, source_number: int) -> dict:
    soup = BeautifulSoup(page, "html.parser")
    pagetitle = soup.title.get_text(" ", strip=True).casefold() if soup.title else ""
    if any(x in pagetitle for x in ("just a moment", "access denied", "attention required")):
        raise SourceError("Access challenge returned instead of chapter")
    heading = soup.select_one("h1") or soup.select_one("h2")
    if not heading:
        raise SourceError("Chapter title is missing")
    observed = heading.get_text(" ", strip=True)
    # A title can be Chapter 0 while its URL suffix is -1: do not compare
    # the heading numeral to the URL suffix or reading-position ordinal.
    def norm(text: str) -> str:
        return re.sub(r"\W+", "", text.casefold())
    def without_chapter_number(text: str) -> str:
        return re.sub(r"(?i)^chapter\s+[\d,]+\s*[-:\u2013\u2014]\s*", "", text).strip()
    # Some TOC labels omit the in-text "Chapter N -" prefix while the page
    # heading retains it. Normalise only this prefix, not arbitrary words.
    if (norm(observed) != norm(title)
            and norm(without_chapter_number(observed)) != norm(title)
            and norm(observed) != norm(without_chapter_number(title))):
        raise SourceError(
            f"Chapter identity mismatch for source chapter {source_number}")
    node = soup.select_one("#chapter-content")
    if node is None:
        raise SourceError("Recognised chapter body not found")
    for junk in node.select(
        "script,style,iframe,nav,button,aside,form,"
        ".ads,.advertisement,[id*='advert'],[class*='advert']"
    ):
        junk.decompose()
    paragraphs = [p.get_text(" ", strip=True) for p in node.select("p")]
    prose = "\n\n".join(filter(None, paragraphs)) if paragraphs else "\n\n".join(
        value.strip() for value in node.stripped_strings if value.strip())
    if any(marker in prose.casefold() for marker in LOCK_MARKERS):
        raise SourceError("Locked content or access challenge; stopped")
    if len(prose) < MIN_CHAPTER_CHARS:
        raise SourceError(f"Chapter has only {len(prose)} characters")
    return {"title": observed, "text": prose}
