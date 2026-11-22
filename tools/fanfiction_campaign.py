"""One-shot, concurrency-aware download queue for user-selected fanfictions.

Only already reviewed, exact source-book URLs are eligible. Never fetch
WebNovel chapters, infer URLs for truncated screenshots or force redownloads.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "campaigns" / "fanfiction" / "webnovel-favourites-43.json"
REGISTRY = ROOT / "downloaded_novels.json"
WORKFLOW = "library-bulk-download.yml"
CAMPAIGN = "hp-naruto-webnovel-fanfics-20261119"
MAX_ACTIVE_BULK = 2
MAX_PER_BATCH = 10
POLL_SECONDS = 75
DISPATCH_SPACING_SECONDS = 150


class FanficQueueError(ValueError):
    """Unsafe or ambiguous fanfiction download request."""


def read_json(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise FanficQueueError("Missing/oversized catalogue or registry")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise FanficQueueError("Expected JSON object")
    return data


def eligible_entries(catalogue: dict, registry: dict) -> tuple[list[dict], list[dict]]:
    """Fail closed if counts, title identities, host or duplicates change."""
    entries = catalogue.get("entries")
    records = registry.get("novels")
    if (catalogue.get("version") != 1 or catalogue.get("campaign") != CAMPAIGN
            or catalogue.get("entry_count") != 43
            or catalogue.get("screenshot_count") != 11
            or not isinstance(entries, list) or len(entries) != 43
            or not isinstance(records, list)):
        raise FanficQueueError("Original 43-title campaign audit must not change silently")
    seen_title, seen_url = set(), set()
    eligible, held = [], []
    completed = {
        r["url"] for r in records
        if isinstance(r, dict) and isinstance(r.get("url"), str)
        and any(
            isinstance(d, dict) and d.get("range") == "all"
            and d.get("status") == "complete"
            for d in r.get("downloads", [])
        )
    }
    known_registry = {
        (r.get("title") or "").casefold().strip()
        for r in records if isinstance(r, dict)
    }
    for row in entries:
        if not isinstance(row, dict):
            raise FanficQueueError("Entry must be an object")
        title = row.get("title_as_shown")
        if (not isinstance(title, str) or not title.strip()
                or title in seen_title
                or row.get("franchise") not in {"Naruto", "Harry Potter"}
                or not row.get("webnovel_author")):
            raise FanficQueueError("Invalid/duplicate fanfiction title or author")
        seen_title.add(title)
        status = row.get("review_state")
        if status != "public_source_listing_matched":
            if status not in {"already_downloaded", "needs_source_verification"}:
                raise FanficQueueError("Unrecognised research state")
            if row.get("source_url"):
                raise FanficQueueError("Unverified entry must not claim an approved source URL")
            held.append({"title": title, "reason": status})
            continue
        url = row.get("source_url")
        matched_title = row.get("matched_title")
        if (not isinstance(url, str) or not isinstance(matched_title, str)
                or not matched_title.strip() or not url.startswith("https://")
                or urlsplit(url).hostname != "freewebnovel.com"
                or not urlsplit(url).path.startswith("/novel/")
                or urlsplit(url).query or urlsplit(url).fragment
                or url in seen_url):
            raise FanficQueueError("Invalid/duplicated approved source URL")
        seen_url.add(url)
        if (url in completed or matched_title.casefold().strip() in known_registry
                or title.casefold().strip() in known_registry):
            held.append({"title": title, "reason": "already_in_complete_registry"})
        elif (row.get("rights_verified") is not True
              or row.get("public_distribution_verified") is not True):
            held.append({"title": title, "reason": "rights_not_verified"})
        else:
            eligible.append({"title": title, "matched_title": matched_title, "url": url})
    matched_count = sum(
        isinstance(row, dict) and row.get("review_state") == "public_source_listing_matched"
        for row in entries
    )
    reconciled_matches = len(eligible) + sum(
        item["reason"] in {"already_in_complete_registry", "rights_not_verified"}
        for item in held
    )
    if reconciled_matches != matched_count:
        raise FanficQueueError("Source-matched fanfiction entries did not reconcile")
    if len(held) + len(eligible) != 43:
        raise FanficQueueError("Fanfiction catalogue count mismatch")
    return eligible, held


def active_bulk_runs(runner=subprocess.run) -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo or "/" not in repo:
        raise FanficQueueError("GitHub repository environment unavailable")
    reply = runner([
        "gh", "api", f"repos/{repo}/actions/workflows/{WORKFLOW}/runs?per_page=80"
    ], capture_output=True, text=True, check=True, timeout=40)
    parsed = json.loads(reply.stdout)
    runs = parsed.get("workflow_runs")
    if not isinstance(runs, list):
        raise FanficQueueError("Malformed GitHub Actions state response")
    return sum(isinstance(run, dict) and run.get("status") != "completed"
               for run in runs)


def dispatch(*, runner=subprocess.run, sleeper=time.sleep,
             clock=time.monotonic, minutes=275) -> dict:
    pending, held = eligible_entries(read_json(CATALOGUE), read_json(REGISTRY))
    report = {
        "version": 1, "campaign": CAMPAIGN, "found_source_urls": len(pending),
        "submitted": [], "held": list(held),
        "mode": "one_shot_fanfiction_download_queue",
    }
    if (os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1"):
        report["held"].extend({"title": x["title"], "reason": "rerun_not_allowed"}
                              for x in pending)
        report["reason"] = "GitHub Actions re-runs do not dispatch"
        return report
    deadline = clock() + minutes * 60
    while pending:
        if clock() >= deadline:
            report["reason"] = "bounded_dispatch_time_exhausted"
            break
        if active_bulk_runs(runner) >= MAX_ACTIVE_BULK:
            sleeper(POLL_SECONDS)
            continue
        batch = pending[:MAX_PER_BATCH]
        urls = [item["url"] for item in batch]
        try:
            runner([
                "gh", "workflow", "run", WORKFLOW, "--ref", "main",
                "--field", "novel_urls=" + ",".join(urls),
                "--field", "chapter_range=", "--field", "force=false",
                "--field", "confirm_rights=true",
            ], check=True, timeout=45)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            report["reason"] = "GitHub Actions dispatch failed"
            break
        report["submitted"].append({
            "titles": [item["title"] for item in batch], "urls": urls
        })
        del pending[:len(batch)]
        print(f"Fanfiction batch queued: {len(batch)} books; "
              f"{len(pending)} approved candidates remain", flush=True)
        if pending:
            sleeper(DISPATCH_SPACING_SECONDS)
    report["held"].extend({"title": x["title"], "reason": "still_queued"}
                          for x in pending)
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--minutes", type=int, default=275)
    args = p.parse_args(argv)
    if not 1 <= args.minutes <= 285:
        raise SystemExit("Time budget must be 1–285 minutes")
    try:
        if args.dry_run:
            pending, held = eligible_entries(read_json(CATALOGUE), read_json(REGISTRY))
            report = {
                "mode": "DRY RUN", "eligible": len(pending),
                "held": len(held), "expected_batches": (
                    len(pending) + MAX_PER_BATCH - 1
                ) // MAX_PER_BATCH
            }
        else:
            report = dispatch(minutes=args.minutes)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)
                               + "\n", encoding="utf-8")
        print(json.dumps(report if args.dry_run else {
            "submitted_batches": len(report["submitted"]),
            "held_titles": len(report["held"]),
            "reason": report.get("reason", ""),
        }), flush=True)
        return 0
    except (FanficQueueError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print("Fanfiction queue stopped:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
