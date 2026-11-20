"""One-time large, paced, source-verified Yup/Idk download dispatcher.

Reuses strict public-listing discovery: never downloads guessed URLs, repeats
completed archives, retries known integrity failures or bypasses source blocks.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from tools import overnight_queue as q

WORKFLOW = "library-bulk-download.yml"
MAX_TOTAL = 48
MAX_BATCH_SIZE = 12
MAX_IN_FLIGHT = 2
DISPATCH_DELAY = 90
POLL_DELAY = 75


def prepare(source: dict, blocked: dict, *, max_books: int = 40) -> tuple[list[dict], dict]:
    if not 1 <= max_books <= MAX_TOTAL:
        raise q.QueueError("Requested batch total exceeds 48")
    if (source.get("version") != 1 or source.get("campaign") != q.CAMPAIGN
            or not isinstance(source.get("verified"), list)):
        raise q.QueueError("Invalid exact-title source-verification results")
    if (blocked.get("version") != 1 or not isinstance(blocked.get("titles"), list)):
        raise q.QueueError("Invalid known-failure exclusion list")
    if len(blocked["titles"]) != len({q.norm(x) for x in blocked["titles"]}):
        raise q.QueueError("Duplicate blocked titles")
    yup, idk, denied, known = q.manifests()
    eligible = {"Yup": {q.norm(x) for x in yup}, "Idk": {q.norm(x) for x in idk}}
    excluded = {q.norm(x) for x in blocked["titles"]}
    matched, seen, skipped = [], set(), {"blocked": 0, "known": 0, "unmatched": 0}
    for row in source["verified"]:
        if not isinstance(row, dict):
            raise q.QueueError("Invalid discovery item")
        title, url, tier = row.get("title"), row.get("url"), row.get("tier")
        k = q.norm(title)
        if (tier not in eligible or k not in eligible[tier] or
                k in denied or row.get("evidence") != "public_listing_exact_title" or
                url not in q.candidate_urls(title)):
            raise q.QueueError("Source verification does not match an approved Yup/Idk book")
        if k in seen:
            raise q.QueueError("Duplicate discovered book")
        seen.add(k)
        if k in known:
            skipped["known"] += 1
            continue
        if k in excluded:
            skipped["blocked"] += 1
            continue
        matched.append({"title": title, "url": url, "tier": tier})
    matched.sort(key=lambda x: (0 if x["tier"] == "Yup" else 1, q.norm(x["title"])))
    overflow = max(0, len(matched) - max_books)
    selected = matched[:max_books]
    return selected, {"verified_candidates": len(matched), "selected": len(selected),
                      "held_for_next_campaign": overflow, **skipped}


def run(selected: list[dict], out: Path, *, batch_size=10,
        max_active=MAX_IN_FLIGHT, minutes=265, runner=subprocess.run,
        sleeper=time.sleep, clock=time.monotonic) -> dict:
    if not 1 <= batch_size <= MAX_BATCH_SIZE or max_active != MAX_IN_FLIGHT:
        raise q.QueueError("Only 1-12 books/batch and two in-flight workflows are permitted")
    if not 1 <= minutes <= 275:
        raise q.QueueError("Invalid dispatcher time budget")
    if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise q.QueueError("GitHub Actions rerun would duplicate live downloads")
    if os.getenv("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever":
        raise q.QueueError("Unexpected repository: refusing live dispatch")
    report = {"version": 1, "selected": len(selected), "submitted": [],
              "held": selected[:], "batch_size": batch_size,
              "max_active_bulk_workflows": max_active, "force": False}
    def persist():
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(out.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        tmp.replace(out)
    persist()
    deadline = clock() + minutes * 60
    pending = selected[:]
    while pending:
        if clock() >= deadline:
            report["reason"] = "Time budget exceeded; unqueued novels safely held"
            break
        if q.active_workflows(runner=runner) >= max_active:
            sleeper(POLL_DELAY)
            continue
        group = pending[:batch_size]
        urls = ",".join(x["url"] for x in group)
        try:
            runner(["gh", "workflow", "run", WORKFLOW, "--ref", "main",
                    "--field", "novel_urls=" + urls, "--field", "chapter_range=",
                    "--field", "force=false"], check=True, timeout=45)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            report["reason"] = "GitHub refused dispatch: " + type(exc).__name__
            break
        report["submitted"].append({"books": len(group),
                                    "titles": [x["title"] for x in group],
                                    "urls": [x["url"] for x in group]})
        del pending[:len(group)]
        report["held"] = pending[:]
        persist()
        print(f"Submitted one large verified batch: {len(group)} titles; "
              f"{len(pending)} still queued for dispatch", flush=True)
        if pending:
            sleeper(DISPATCH_DELAY)
    persist()
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--blocked", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-books", type=int, default=40)
    p.add_argument("--batch-size", type=int, default=10)
    p.add_argument("--minutes", type=int, default=265)
    args = p.parse_args(argv)
    try:
        selected, counts = prepare(q.read_json(args.source),
                                   q.read_json(args.blocked),
                                   max_books=args.max_books)
        print("Large campaign source-verified selection:", counts, flush=True)
        report = run(selected, args.out, batch_size=args.batch_size,
                     minutes=args.minutes)
        print("Large batch campaign dispatch result:",
              {"submitted_batches": len(report["submitted"]),
               "submitted_books": sum(x["books"] for x in report["submitted"]),
               "held_books": len(report["held"])}, flush=True)
        if report.get("reason"):
            print("Dispatch stopped safely:", report["reason"], file=sys.stderr)
            return 1
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print("Large campaign stopped:", str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
