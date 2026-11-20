"""Dispatch manually verified exact novel links through the existing bulk workflow.

This module **does not search websites** or construct book URLs. Operators
research supported sources first and commit a reviewed JSON source-link queue.
It checks the approved campaigns, exclusions and registry before dispatch.
The child bulk workflow performs final, live registry deduplication and strict
chapter and EPUB validation. No forced or automatic repeat downloads.
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

from tools import overnight_queue as q
from tools.mixed_source_bulk import _validated_url

CAMPAIGN = "manual-source-curated-yup-20261120-night"
SOURCE_PRIORITY = ("NovelFull", "ReadNovelFull", "FreeWebNovel")
MAX_BOOKS = 24
MAX_ACTIVE = 2
CHECK_DELAY = 75
DEFAULT_WAIT_SECONDS = 5 * 60 * 60


def prepare_queue(manifest: dict, *, registry: dict, yup: dict,
                  verified: dict, idk: dict, denied: dict,
                  known_failures: dict) -> dict:
    if (manifest.get("schema_version") != 1
            or manifest.get("campaign") != CAMPAIGN
            or manifest.get("method") !=
                "operator-reviewed-book-pages-no-runtime-website-search"
            or manifest.get("priority") != list(SOURCE_PRIORITY)
            or manifest.get("max_parallel_bulk_runs") != MAX_ACTIVE
            or not isinstance(manifest.get("books"), list)
            or not 1 <= len(manifest["books"]) <= MAX_BOOKS):
        raise ValueError("Unexpected curated, no-search campaign contract")
    if (len(denied.get("excluded", [])) != 90
            or len(known_failures.get("titles", [])) != 14):
        raise ValueError("Required exclusion lists incomplete")
    if (not isinstance(registry.get("novels"), list)
            or len(yup.get("entries", [])) != 163
            or not isinstance(idk.get("entries"), list)
            or not isinstance(verified.get("entries"), list)):
        raise ValueError("Approved backlog/registry lists missing")
    allowed = {q.norm(x["title"]) for x in (
        yup["entries"] + idk["entries"] + verified["entries"])}
    banned = {q.norm(x) for x in (
        denied["excluded"] + known_failures["titles"])}
    complete_records = [
        row for row in registry["novels"]
        if isinstance(row, dict) and any(
            d.get("status") == "complete" and d.get("range") == "all"
            for d in row.get("downloads", []) if isinstance(d, dict))
    ]
    complete_urls = {x.get("url") for x in complete_records}
    complete_titles = {q.norm(x.get("title")) for x in complete_records}
    seen_urls, seen_titles = set(), set()
    eligible, already_complete = [], []
    for row in manifest["books"]:
        if not isinstance(row, dict) or set(row) != {
                "title", "source_title", "site", "url", "evidence"}:
            raise ValueError("Unexpected or incomplete hand-reviewed source entry")
        title, source_title, site, url, evidence = (
            row["title"], row["source_title"], row["site"],
            row["url"], row["evidence"])
        if not all(isinstance(x, str) and 3 <= len(x.strip()) <= 320
                   for x in (title, source_title, site, url, evidence)):
            raise ValueError("Invalid reviewed source fields")
        if (q.norm(title) not in allowed or
                q.norm(title) in banned or q.norm(source_title) in banned):
            raise ValueError("Title not approved or in global red/known-failure exclusions")
        detected, clean_url = _validated_url(url)
        if detected not in SOURCE_PRIORITY or detected != site or clean_url != url:
            raise ValueError("URL is not a canonical book page from the reviewed source")
        parts = urlsplit(url)
        if parts.username or parts.password or parts.port or parts.query or parts.fragment:
            raise ValueError("Unsafe or non-canonical source URL")
        if url in seen_urls or q.norm(title) in seen_titles:
            raise ValueError("Duplicate queued source/book")
        seen_urls.add(url)
        seen_titles.add(q.norm(title))
        if (url in complete_urls or q.norm(title) in complete_titles
                or q.norm(source_title) in complete_titles):
            already_complete.append({"title": title, "reason": "already complete"})
        else:
            eligible.append(row)
    eligible.sort(key=lambda row: SOURCE_PRIORITY.index(row["site"]))
    return {"eligible": eligible, "already_complete": already_complete,
            "reviewed": len(manifest["books"]), "unverified_sites_searched": 0}


def dispatch_queue(plan: dict, *, runner=subprocess.run,
                   clock=time.monotonic, sleeper=time.sleep,
                   wait_seconds=DEFAULT_WAIT_SECONDS) -> dict:
    if os.getenv("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever":
        raise ValueError("Refusing dispatch outside the canonical repository")
    if (os.getenv("GITHUB_ACTIONS") == "true"
            and os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1"):
        raise ValueError("One-shot activation may not be rerun")
    report = {"version": 1, "campaign": CAMPAIGN,
              "reviewed": plan["reviewed"],
              "selected": [{"title": x["title"], "site": x["site"], "url": x["url"]}
                           for x in plan["eligible"]],
              "already_complete": plan["already_complete"],
              "searches_performed_by_dispatcher": 0,
              "dispatched": False}
    if not plan["eligible"]:
        report["reason"] = "All reviewed books already complete; no run created"
        return report
    deadline = clock() + wait_seconds
    while q.active_workflows(runner=runner) >= MAX_ACTIVE:
        if clock() >= deadline:
            raise TimeoutError("Two active bulk runs remained busy; no duplicate launch")
        sleeper(CHECK_DELAY)
    urls = ",".join(x["url"] for x in plan["eligible"])
    command = ["gh", "workflow", "run", "library-bulk-download.yml",
               "--repo", "RichardDaffern/Novel-Retriever", "--ref", "main",
               "--field", "novel_urls=" + urls,
               "--field", "chapter_range=", "--field", "force=false"]
    runner(command, check=True, timeout=90)
    report["dispatched"] = True
    report["selected_count"] = len(plan["eligible"])
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    base = Path(__file__).resolve().parent.parent

    def load(relative: str):
        return json.loads((base / relative).read_text(encoding="utf-8"))
    try:
        plan = prepare_queue(
            load(args.manifest.as_posix()), registry=load("downloaded_novels.json"),
            yup=load("campaigns/yup-pilot/backlog-163.json"),
            verified=load("campaigns/yup-pilot/verified-urls.json"),
            idk=load("campaigns/overnight/idk-82.json"),
            denied=load("campaigns/overnight/excluded-90.json"),
            known_failures=load("campaigns/overnight/blocked-full-retries-20261120.json"),
        )
        print("Curated, no-site-search preflight:", {
            "reviewed": plan["reviewed"], "eligible": len(plan["eligible"]),
            "already_complete": len(plan["already_complete"]),
            "sites": sorted({x["site"] for x in plan["eligible"]})}, flush=True)
        report = dispatch_queue(plan)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Reviewed direct-link bulk dispatch:", {
            "dispatched": report["dispatched"],
            "selected_count": len(plan["eligible"])}, flush=True)
        return 0
    except (ValueError, OSError, TimeoutError, subprocess.SubprocessError,
            json.JSONDecodeError) as exc:
        print(f"Curated dispatch stopped safely: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
