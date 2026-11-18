"""Conservative FreeWebNovel book-page metadata extraction.

Read only the already-fetched public book catalogue, never unrelated navigation,
recommended titles, chapter prose or user comments. Missing fields remain
missing: do not synthesise genres, status or a synopsis.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

from tools.epub_source_metadata import clean_genres

MAX_SYNOPSIS = 8000
MAX_HEADER_NODES = 180
GENRE_PATH = re.compile(r"^/genres?/[^/]+/?$", re.IGNORECASE)
STATUS = {
    "completed": "Completed",
    "complete": "Completed",
    "ongoing": "Ongoing",
    "in progress": "Ongoing",
    "in-progress": "Ongoing",
}
SUMMARY_LABELS = {"summary", "synopsis"}
STOP_LABELS = {"chapter list", "latest chapters", "comments", "related novels", "same author"}


def _label(node: Tag) -> str:
    return " ".join(node.get_text(" ", strip=True).split())


def _find_summary(soup: BeautifulSoup, title_heading: Tag | None) -> str:
    """Find a dedicated synopsis block without falling through to chapters."""
    headings = [tag for tag in soup.select("h2,h3,h4,h5,h6")
                if _label(tag).casefold().strip(":") in SUMMARY_LABELS]
    if title_heading is not None and headings:
        nodes = soup.find_all(True)
        positions = {id(node): i for i, node in enumerate(nodes)}
        after = positions[id(title_heading)]
        headings = [tag for tag in headings if positions[id(tag)] > after]
    for heading in headings[:2]:
        pieces = []
        # The website's "SUMMARY" heading is followed by its description,
        # then a "See all" link and the chapter list. Stay within that area.
        for sibling in heading.next_siblings:
            if not isinstance(sibling, Tag):
                if isinstance(sibling, str) and sibling.strip():
                    pieces.append(sibling.strip())
                continue
            if sibling.name in {"h1", "h2", "h3", "h4", "h5", "h6", "nav", "footer"}:
                break
            text = _label(sibling)
            if text.casefold() in STOP_LABELS:
                break
            if sibling.name == "a" and text.casefold() in {"see all", "read first", "chapter list"}:
                break
            if sibling.select_one("a[href*='/chapter-']"):
                break
            if text:
                pieces.append(text)
            if len(" ".join(pieces)) > MAX_SYNOPSIS:
                break
        if not pieces:
            # Some layouts place summary paragraphs in a shared wrapper.
            parent = heading.parent
            if parent and parent.name in ("section", "div", "article") and (
                "summary" in " ".join(parent.get("class", [])).lower()
                or "synopsis" in " ".join(parent.get("class", [])).lower()
            ):
                clone = BeautifulSoup(str(parent), "html.parser")
                for item in clone.select("h2,h3,h4,h5,h6,a,script,style"):
                    item.decompose()
                pieces = [_label(clone)]
        text = " ".join(pieces).strip()
        text = re.split(r"\bSee all\b|\bChapter List\b", text, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        if 35 <= len(text) <= MAX_SYNOPSIS:
            return text
    # Site variants without an actual heading use an explicit synopsis node.
    for node in soup.select("[itemprop='description'], .novel-summary, .book-summary, #novel-summary"):
        text = _label(node)
        text = re.sub(r"^(?:summary|synopsis)\s*:?\s*", "", text, flags=re.IGNORECASE)
        if 35 <= len(text) <= MAX_SYNOPSIS and not node.select_one("a[href*='/chapter-']"):
            return text
    return ""


def _book_header_nodes(soup: BeautifulSoup, title_heading: Tag | None, title: str) -> list[Tag]:
    """Bound genre/status links to the selected book rather than global menus.

    On the current site the book's author and genre links precede its H1 and
    SUMMARY. Other templates group them under a book-info/detail container.
    """
    all_nodes = soup.find_all(True)
    positions = {id(node): i for i, node in enumerate(all_nodes)}
    if title_heading is not None:
        end = positions[id(title_heading)]
        authors = [tag for tag in soup.select("a[href*='/author/']")
                   if positions[id(tag)] < end]
        if authors:
            start = positions[id(authors[-1])]
            if end - start <= MAX_HEADER_NODES:
                return all_nodes[start:end]
        # Some layouts have a title in H3 above the author/genre metadata.
        earlier = [tag for tag in soup.select("h2,h3,h4")
                   if _label(tag).casefold() == title.casefold()
                   and positions[id(tag)] < end]
        if earlier:
            start = positions[id(earlier[-1])]
            if end - start <= MAX_HEADER_NODES:
                return all_nodes[start:end]
    # Explicitly named, title-matching book detail sections are safe fallbacks.
    for node in soup.select(
        ".novel-detail, .novel-info, .book-detail, .book-info, "
        ".novel-header, .book-header, .detail-info, .detail-header"
    ):
        if len(node.find_all("a", href=re.compile(r"/novel/"))) > 2:
            continue
        if title.casefold() not in _label(node).casefold():
            continue
        descendants = node.find_all(True)
        if len(descendants) <= MAX_HEADER_NODES:
            return descendants
    return []


def extract_book_metadata(html: str, title: str) -> dict:
    """Return a subset of description/genres/status for a specific book page."""
    if not isinstance(title, str) or not title.strip():
        return {}
    soup = BeautifulSoup(html, "html.parser")
    heading = next((tag for tag in soup.select("h1")
                    if _label(tag).casefold() == title.strip().casefold()), None)
    result = {}
    synopsis = _find_summary(soup, heading)
    if synopsis:
        result["description"] = synopsis
        result["synopsis"] = synopsis
    header = _book_header_nodes(soup, heading, title.strip())
    genres = []
    for node in header:
        if node.name != "a":
            continue
        path = urlsplit(node.get("href", "")).path
        if GENRE_PATH.fullmatch(path):
            genres.append(_label(node))
    cleaned = clean_genres(genres)
    if cleaned:
        result["genres"] = cleaned[:25]
    for node in header:
        if node.name not in {"a", "span", "div", "strong", "b", "li"}:
            continue
        # A div wrapping the entire header must not match incidental prose.
        if len(node.find_all(True)) > 2:
            continue
        status = STATUS.get(_label(node).casefold())
        if status:
            result["status"] = status
            break
    return result
