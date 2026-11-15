#!/usr/bin/env python3
"""Strict, public-page ReadNovelFull adapter (no login or challenge bypass).

The public book page shows only a few chapters. The ordinary AJAX chapter
archive supplies the complete ordered URL catalogue. No chapter URL is guessed.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOST = "readnovelfull.com"
BOOK = re.compile(r"/([a-z0-9][a-z0-9_-]*)\.html\Z")
CHAPTER = re.compile(r"/([a-z0-9][a-z0-9_-]*)/chapter-([1-9][0-9]*)(?:-[a-z0-9_-]+)?\.html\Z")
ARCHIVE = "/ajax/chapter-archive"
MAX_HTML = 12 * 1024 * 1024
MAX_CHAPTERS = 20000
MIN_CHAPTER_CHARS = 200
LOCK_MARKERS = ("unlock this chapter", "purchase this chapter", "subscribe to unlock",
                "this chapter is locked", "verify you are human")
BODY_SELECTORS = ("#chr-content", ".chr-c")


class SourceError(ValueError):
    """Invalid source URL, chapter catalogue, or inaccessible public content."""


def _parts(value: str):
    try:
        p = urlsplit(value)
        port = p.port
    except ValueError as exc:
        raise SourceError("Malformed ReadNovelFull URL") from exc
    if (p.scheme != "https" or p.hostname not in (HOST, "www." + HOST)
            or port is not None or p.username or p.password or p.fragment):
        raise SourceError("Only public HTTPS readnovelfull.com URLs are supported")
    return p


def validate_book_url(url: str) -> str:
    p = _parts(url)
    if p.query or not BOOK.fullmatch(p.path):
        raise SourceError("Expected https://readnovelfull.com/book-slug.html")
    return "https://" + HOST + p.path


def validate_chapter_url(url: str, *, book_prefix: str = "") -> tuple[str, int, str]:
    p = _parts(url)
    matched = CHAPTER.fullmatch(p.path)
    if not matched or p.query:
        raise SourceError("Invalid ReadNovelFull chapter URL")
    if book_prefix and matched.group(1) != book_prefix:
        raise SourceError("Chapter link belongs to another novel")
    return "https://" + HOST + p.path, int(matched.group(2)), matched.group(1)


def archive_url(novel_id: str) -> str:
    if not re.fullmatch(r"[1-9][0-9]{0,11}", str(novel_id)):
        raise SourceError("Invalid public novel identifier")
    return f"https://{HOST}{ARCHIVE}?novelId={novel_id}"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SourceError("Unexpected redirect; no access workaround attempted")


def fetch_public_html(url: str) -> str:
    p = _parts(url)
    is_archive = p.path == ARCHIVE
    if is_archive:
        qs = parse_qs(p.query, strict_parsing=True)
        if set(qs) != {"novelId"} or len(qs["novelId"]) != 1:
            raise SourceError("Unexpected AJAX query parameters")
        archive_url(qs["novelId"][0])
    elif p.query or (not BOOK.fullmatch(p.path) and not CHAPTER.fullmatch(p.path)):
        raise SourceError("Refusing non-novel ReadNovelFull URL")
    headers = {"User-Agent": "NovelLibraryReadNovelFull/1.0", "Accept": "text/html"}
    if is_archive:
        headers["X-Requested-With"] = "XMLHttpRequest"
    try:
        with build_opener(NoRedirect()).open(Request(url, headers=headers),
                                               timeout=25) as res:
            if res.status != 200 or res.headers.get("cf-mitigated", "").lower() == "challenge":
                raise SourceError("Access challenge or unexpected HTTP response")
            if res.headers.get_content_type() not in ("text/html", "application/xhtml+xml"):
                raise SourceError("Source response was not HTML")
            raw = res.read(MAX_HTML + 1)
            if len(raw) > MAX_HTML:
                raise SourceError("ReadNovelFull HTML exceeds 12 MiB limit")
    except HTTPError as exc:
        raise SourceError(f"ReadNovelFull returned HTTP {exc.code}; stopped") from exc
    except URLError as exc:
        raise SourceError(f"ReadNovelFull not reachable: {exc.reason}") from exc
    html = raw.decode("utf-8-sig", errors="replace")
    title = BeautifulSoup(html, "html.parser").title
    if title and any(s in title.get_text(" ", strip=True).casefold()
                     for s in ("just a moment", "attention required", "access denied")):
        raise SourceError("Source access challenge; stopped")
    return html


def book_metadata(page: str, url: str) -> dict:
    url = validate_book_url(url)
    soup = BeautifulSoup(page, "html.parser")
    title_node = soup.select_one("h3.title, .book .title, h1.title, h1")
    title = title_node.get_text(" ", strip=True) if title_node else ""
    if not title or len(title) > 250:
        raise SourceError("Book title missing or implausible")
    id_node = soup.select_one("#rating[data-novel-id], [data-novel-id]")
    novel_id = id_node.get("data-novel-id", "") if id_node else ""
    archive_url(novel_id)
    author = "Unknown"
    for line in soup.select(".info-meta li"):
        raw = line.get_text(" ", strip=True)
        if raw.lower().startswith("author"):
            author = raw.split(":", 1)[-1].strip()[:240] or "Unknown"
            break
    description_node = soup.select_one(".desc-text, .desc, [itemprop='description']")
    description = description_node.get_text(" ", strip=True) if description_node else ""
    genres: list[str] = []
    status = ""
    for line in soup.select(".info-meta li"):
        raw = line.get_text(" ", strip=True)
        if raw.lower().startswith("genre"):
            genres = [a.get_text(" ", strip=True) for a in line.select("a")][:30]
        elif raw.lower().startswith("status"):
            value = raw.split(":", 1)[-1].strip().casefold()
            if "complet" in value:
                status = "Completed"
            elif "ongoing" in value:
                status = "Ongoing"
    return {
        "title": title, "author": author,
        "description": description[:16000], "genres": genres, "status": status,
        "source_url": url, "novel_id": novel_id,
    }


def chapter_index(page: str, book_url: str) -> list[dict]:
    """Use the actual full AJAX chapter list, never invent slug or chapter URLs."""
    validate_book_url(book_url)
    soup = BeautifulSoup(page, "html.parser")
    anchors = soup.select("ul.list-chapter li a[href], .list-chapter li a[href]")
    if not anchors:
        raise SourceError("AJAX chapter archive did not contain a chapter list")
    seen: dict[int, dict] = {}
    chapter_prefix = ""
    for anchor in anchors:
        url = urljoin("https://" + HOST + "/", anchor["href"])
        canonical, position, prefix = validate_chapter_url(
            url, book_prefix=chapter_prefix)
        if not chapter_prefix:
            chapter_prefix = prefix
        title = anchor.get("title") or anchor.get_text(" ", strip=True)
        title = title.strip()[:240] or f"Chapter {position}"
        if position in seen:
            if seen[position]["url"] != canonical:
                raise SourceError(f"Duplicate Chapter {position} links in archive")
            continue
        seen[position] = {"position": position, "title": title, "url": canonical}
        if len(seen) > MAX_CHAPTERS:
            raise SourceError("Chapter archive exceeds 20,000-chapter limit")
    if not seen or sorted(seen) != list(range(1, max(seen) + 1)):
        raise SourceError("Chapter archive is missing or misnumbering chapters")
    return [seen[n] for n in sorted(seen)]


def discover(book_url: str, *, fetcher=fetch_public_html) -> dict:
    book_url = validate_book_url(book_url)
    page = fetcher(book_url)
    metadata = book_metadata(page, book_url)
    rows = chapter_index(fetcher(archive_url(metadata["novel_id"])), book_url)
    # The visible first chapters must agree with the AJAX archive to guard
    # against a valid but unrelated novelId in an altered book page.
    soup = BeautifulSoup(page, "html.parser")
    visible = {}
    for a in soup.select(".list-chapter a[href], #list-chapter a[href]"):
        try:
            canonical, pos, _ = validate_chapter_url(urljoin(book_url, a["href"]))
        except SourceError:
            continue
        if pos in (1, 2):
            visible[pos] = canonical
    for pos, candidate in visible.items():
        if pos > len(rows) or rows[pos - 1]["url"] != candidate:
            raise SourceError("Book page and AJAX archive chapter links disagree")
    metadata["numChapters"] = len(rows)
    metadata["chapters"] = rows
    return metadata


def extract_chapter(page: str, *, number: int, title: str) -> dict:
    soup = BeautifulSoup(page, "html.parser")
    page_title = soup.title.get_text(" ", strip=True).casefold() if soup.title else ""
    if any(x in page_title for x in ("just a moment", "attention required", "access denied")):
        raise SourceError("Access challenge returned instead of chapter")
    header = soup.select_one(".chapter-title, h1, h2, h3")
    heading = header.get_text(" ", strip=True) if header else ""
    m = re.search(r"\bchapter\s+([1-9][0-9]*)\b", heading, re.I)
    if m and int(m.group(1)) != number:
        raise SourceError(f"Expected Chapter {number}, received Chapter {m.group(1)}")
    node = next((soup.select_one(selector) for selector in BODY_SELECTORS
                 if soup.select_one(selector)), None)
    if node is None:
        raise SourceError("Recognised chapter text container not found")
    for unwanted in node.select(
        "script,style,iframe,nav,button,aside,form,"
        ".ads,.adv,.advertisement,[id*='advert'],[class*='advert']"
    ):
        unwanted.decompose()
    paragraphs = [x.get_text(" ", strip=True) for x in node.select("p")]
    text = "\n\n".join(filter(None, paragraphs)) if paragraphs else (
        "\n\n".join(x.strip() for x in node.stripped_strings if x.strip()))
    if any(marker in text.casefold() for marker in LOCK_MARKERS):
        raise SourceError("Chapter locked or access restricted; stopped")
    if len(text) < MIN_CHAPTER_CHARS:
        raise SourceError(f"Chapter {number} has only {len(text)} text characters")
    return {"title": title, "text": text}
