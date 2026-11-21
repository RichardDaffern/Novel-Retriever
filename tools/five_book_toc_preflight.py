"""Read-only chapter-catalogue preflight for five newly sourced Yup/Idk books.

Fetch only each public book information page and its ordinary AJAX chapter index.
Never fetch or persist chapter prose. An index pass is not archival authorisation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from tools.overnight_queue import norm
from tools.readnovelfull_source import SourceError, discover, validate_book_url

MAX_BOOKS = 5


def review(rows: list[dict], *, discoverer=discover, sleeper=time.sleep) -> dict:
    if not isinstance(rows, list) or len(rows) != MAX_BOOKS:
        raise ValueError("Exactly five approved book-page entries required")
    seen = set()
    result = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"title", "url", "tier"}:
            raise ValueError("Malformed book review entry")
        title, url, tier = row["title"], row["url"], row["tier"]
        if (not isinstance(title, str) or not 3 <= len(title) <= 240
                or tier not in ("Yup", "Idk") or not isinstance(url, str)):
            raise ValueError("Invalid reviewed source identity")
        canonical = validate_book_url(url)
        if canonical in seen:
            raise ValueError("Duplicate book URL")
        seen.add(canonical)
        if index:
            sleeper(3)
        entry = {"title": title, "tier": tier, "url": canonical}
        try:
            info = discoverer(canonical)
            detected_title = info.get("title", "")
            count = info.get("numChapters", 0)
            if not isinstance(count, int) or count < 1:
                raise SourceError("No valid chapter count")
            entry.update(
                source_title=detected_title,
                author=info.get("author", "Unknown"),
                chapter_count=count,
                index_validated=True,
                title_exact=norm(detected_title) == norm(title),
                state=("index_passed_title_match" if norm(detected_title) == norm(title)
                       else "identity_requires_review"),
            )
        except (SourceError, OSError, TimeoutError) as error:
            entry.update(index_validated=False, state="index_failed",
                         reason=str(error)[:250])
        result.append(entry)
    return {
        "version": 1, "mode": "PUBLIC_BOOK_INDEX_ONLY",
        "full_chapter_downloads": 0,
        "rights_verified": False,
        "checked": len(result),
        "index_passed": sum(x["index_validated"] for x in result),
        "title_confirmed": sum(x["state"] == "index_passed_title_match" for x in result),
        "results": result,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    source = json.loads(args.manifest.read_text(encoding="utf-8"))
    if (not isinstance(source, dict)
            or set(source) != {"version", "purpose", "books"}
            or source["version"] != 1 or source["purpose"] != "toc-preflight-read-only"):
        raise ValueError("Invalid reviewed source manifest")
    result = review(source["books"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    for item in result["results"]:
        print(item["tier"], item["title"], item["state"],
              item.get("chapter_count", item.get("reason", "")), flush=True)
    print("Public chapter index checks passed:", result["index_passed"],
          "of", result["checked"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
