"""Secondary bulk pass over every remaining historical wishlist title.

First prefer NovelFull/ReadNovelFull (separate primary campaign). This module
checks the FreeWebNovel fallback only, using title and available full-edition
metadata, before requesting the repository's existing validated downloader.

No novel content is fetched during discovery. Private HF data is not touched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

from tools import overnight_queue as q
from tools.priority_wishlist_bulk import pending_titles
from tools.freewebnovel_downloader import book_details
from tools.freewebnovel_source import fetch_public_html

CAMPAIGN = "broad-fallback-wishlist-20261124"
MAX_IN_FLIGHT = 2
BATCH_SIZE = 6
REQUEST_DELAY = 2
POLL_SECONDS = 75
DISPATCH_DELAY = 90

# Two verified book-index matches were dispatched in #45244706019, and the
# existing incomplete repair campaign must not be silently repeated.
RESERVED_TITLES = {
    "Beautiful Time With You",
    "Attack Of The Adorable Kid: President Daddy's Infinite Pampering",
}

# Original-edition chapter counts already documented by source research.
# For other titles, a completed source catalogue and consistent chapter links
# are required; actual chapter integrity is enforced by the downstream jobs.
HISTORICAL_MINIMUM = {
    "Doom Lord": 856,
    "Girl, I’ll Teach You Cultivation": 812,
    "Beast Piercing The Heavens": 1445,
    "Apotheosis": 3913,
    "The Military Female Soldier With Unwavering Stubbornness": 5707,
    "Godly Student": 2783,
    "I'm In Hollywood": 1000,
}


def _normalise_map(values: dict) -> dict:
    return {q.norm(k): v for k, v in values.items()}


def discover(out: Path, *, fetcher=fetch_public_html, sleeper=time.sleep) -> dict:
    pending, audit = pending_titles()
    registered = set(audit.pop("completed_urls"))
    denied = {q.norm(t) for t in q.read_json(q.DENY)["excluded"]}
    reserved = {q.norm(t) for t in RESERVED_TITLES}
    minimums = _normalise_map(HISTORICAL_MINIMUM)
    complete, held, requested, seen = [], [], 0, set()
    for row in pending:
        title = row["title"]
        key = q.norm(title)
        if key in reserved or key in denied:
            held.append({"title": title, "reason": "already_dispatched_or_excluded"})
            continue
        url = q.candidate_urls(title)[3]
        if url in registered or url in seen:
            held.append({"title": title, "reason": "completed_or_duplicate_source_url"})
            continue
        seen.add(url)
        if requested:
            sleeper(REQUEST_DELAY)
        requested += 1
        try:
            details = book_details(fetcher(url), url)
            source_title = details["title"]
            if q.norm(source_title) != key and q.norm(source_title) != q.norm("The " + title):
                raise ValueError("Source title is not the requested novel")
            count = details["numChapters"]
            if count < minimums.get(key, 2):
                raise ValueError("Source edition is shorter than verified original")
            if details.get("status") != "Completed":
                raise ValueError("Source edition is not marked completed")
            candidate = {
                "title": title,
                "source_title": source_title,
                "url": url,
                "chapters": count,
                "edition_status": details["status"],
                "catalogue": "verified_chapter_mapping",
            }
            complete.append(candidate)
            print("VERIFIED_FALLBACK", title, count, flush=True)
        except (ValueError, OSError, KeyError) as error:
            held.append({"title": title, "reason": str(error)[:240]})
            print("UNRESOLVED_FALLBACK", title, str(error)[:240], flush=True)
    result = {"version": 1, "campaign": CAMPAIGN,
              "scope": "historical_not_private_HF_Excel",
              "historical_queue_considered": len(pending),
              "requests": requested,
              "verified": complete,
              "held": held,
              "no_chapter_bodies_downloaded_in_discovery": True}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"FALLBACK_DISCOVERY_COMPLETE {len(complete)} candidate(s), "
          f"{len(held)} held, {requested} public book pages", flush=True)
    return result


def dispatch(source: dict, out: Path, *,
             runner=subprocess.run, sleeper=time.sleep,
             clock=time.monotonic, minutes=265) -> dict:
    if (source.get("version") != 1 or source.get("campaign") != CAMPAIGN
            or not isinstance(source.get("verified"), list)):
        raise ValueError("Invalid secondary-source verification report")
    if (os.getenv("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever"
            or os.getenv("GITHUB_ACTIONS") != "true"
            or os.getenv("GITHUB_RUN_ATTEMPT") != "1"):
        raise ValueError("Live secondary dispatch is allowed only in first GitHub Actions attempt")
    pending, audit = pending_titles()
    allowed = {q.norm(x["title"]) for x in pending}
    registered = set(audit["completed_urls"])
    reserved = {q.norm(x) for x in RESERVED_TITLES}
    selected, names = [], set()
    for row in source["verified"]:
        title, url = row["title"], row["url"]
        key = q.norm(title)
        if (key not in allowed or key in reserved or key in names or
                url != q.candidate_urls(title)[3] or url in registered or
                row.get("catalogue") != "verified_chapter_mapping"
                or row.get("edition_status") != "Completed"
                or int(row.get("chapters", 0)) < 2):
            raise ValueError(f"Unapproved or duplicate secondary candidate: {title}")
        names.add(key)
        selected.append(row)
    selected.sort(key=lambda r: q.norm(r["title"]))
    report = {"version": 1, "campaign": CAMPAIGN,
              "verified": len(selected), "submitted": [],
              "held": selected[:], "force": False, "remaining": len(selected)}
    def save():
        tmp = out.with_suffix(out.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(out)
    save()
    expires_at = clock() + minutes * 60
    while selected:
        if clock() >= expires_at:
            report["reason"] = "dispatcher_time_budget_exhausted"
            break
        try:
            active = q.active_workflows(runner=runner)
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            report["reason"] = f"cannot_verify_active_bulk_runs:{type(error).__name__}"
            break
        if active >= MAX_IN_FLIGHT:
            sleeper(POLL_SECONDS)
            continue
        batch = selected[:BATCH_SIZE]
        urls = ",".join(row["url"] for row in batch)
        try:
            runner(["gh", "workflow", "run", "library-bulk-download.yml",
                    "--ref", "main", "--raw-field", f"novel_urls={urls}",
                    "--raw-field", "chapter_range=",
                    "--raw-field", "force=false",
                    "--raw-field", "confirm_rights=true"],
                   check=True, timeout=45)
        except (OSError, subprocess.SubprocessError) as error:
            report["reason"] = f"dispatch_rejected:{type(error).__name__}"
            break
        report["submitted"].append({"titles": [x["title"] for x in batch],
                                    "urls": [x["url"] for x in batch]})
        del selected[:len(batch)]
        report["held"] = selected[:]
        report["remaining"] = len(selected)
        save()
        print(f"DISPATCHED_FALLBACK {len(batch)} titles; {len(selected)} pending", flush=True)
        if selected:
            sleeper(DISPATCH_DELAY)
    save()
    return report


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("discover", "dispatch"))
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "discover":
            discover(args.out)
        else:
            if not args.source:
                parser.error("dispatch requires --source")
            report = dispatch(json.loads(args.source.read_text(encoding="utf-8")), args.out)
            print("FALLBACK_DISPATCH_SUMMARY",
                  sum(len(x["titles"]) for x in report["submitted"]),
                  "submitted, ", report["remaining"], "held", flush=True)
            return 1 if report.get("reason") else 0
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print("Secondary campaign failed:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
