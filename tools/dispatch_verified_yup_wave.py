"""Dispatch one reviewed seven-title Yup wave using the existing bulk workflow.

Only source pages explicitly reviewed in a committed JSON are accepted.
Do not bypass chapter checks, force complete books or re-run this activation.
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

CAMPAIGN = "verified-yup-overnight-20261120"
MAX_BOOKS = 10
MAX_ACTIVE_BULK_RUNS = 2
EXPECTED_SOURCE = "novelfull.com"


def prepare(*, manifest: dict, registry: dict, backlog: dict, verified: dict,
            denied: dict, blocked: dict) -> dict:
    if (manifest.get("version") != 1 or manifest.get("campaign") != CAMPAIGN
            or manifest.get("one_time") is not True
            or not isinstance(manifest.get("books"), list)
            or not 1 <= len(manifest["books"]) <= MAX_BOOKS):
        raise ValueError("Expected a single reviewed 1-10-book campaign")
    if not isinstance(registry.get("novels"), list):
        raise ValueError("Invalid completed-book registry")
    if len(denied.get("excluded", [])) != 90:
        raise ValueError("90 red/Dropped exclusions must be preserved")
    if len(blocked.get("titles", [])) != 14:
        raise ValueError("Known unrepaired 14-book exclusion list changed")
    if len(backlog.get("entries", [])) != 163 or not verified.get("entries"):
        raise ValueError("Reviewed Yup campaign lists are missing")
    allowed = {q.norm(r["title"]) for r in backlog["entries"]}
    allowed.update(q.norm(r["title"]) for r in verified["entries"])
    excluded = {q.norm(x) for x in denied["excluded"]}
    excluded.update(q.norm(x) for x in blocked["titles"])
    completed = [r for r in registry["novels"] if isinstance(r, dict)
                 and any(d.get("status") == "complete" and d.get("range") == "all"
                         for d in r.get("downloads", []) if isinstance(d, dict))]
    complete_urls = {r.get("url") for r in completed}
    complete_titles = {q.norm(r.get("title")) for r in completed}
    urls, titles = set(), set()
    selected, skipped = [], []
    for row in manifest["books"]:
        if not isinstance(row, dict) or set(row) != {
                "title", "source_title", "url", "basis"}:
            raise ValueError("Unexpected reviewed source-entry fields")
        title, actual, url, basis = (row["title"], row["source_title"],
                                    row["url"], row["basis"])
        if not all(isinstance(v, str) and 4 <= len(v) <= 240
                   for v in (title, actual, url, basis)):
            raise ValueError("Invalid reviewed book fields")
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname != EXPECTED_SOURCE
                or parsed.username or parsed.password or parsed.port
                or parsed.query or parsed.fragment or not parsed.path.endswith(".html")
                or any(s in parsed.path for s in ("/chapter-", "/chapter/"))):
            raise ValueError("Not a direct approved NovelFull book listing")
        if (q.norm(title) not in allowed or q.norm(title) in excluded
                or q.norm(actual) in excluded):
            raise ValueError("Title absent from Yup or present in dropped/blocked exclusions")
        if (url in urls or q.norm(title) in titles):
            raise ValueError("Duplicate canonical source or requested title")
        urls.add(url)
        titles.add(q.norm(title))
        if (url in complete_urls or q.norm(title) in complete_titles
                or q.norm(actual) in complete_titles):
            skipped.append({"title": title, "reason": "already_complete"})
        else:
            selected.append(row)
    return {"selected": selected, "skipped": skipped, "source_reviewed": len(urls)}


def dispatch(plan: dict, *, runner=subprocess.run, sleeper=time.sleep,
             clock=time.monotonic, deadline_seconds=7200) -> dict:
    if os.environ.get("GITHUB_REPOSITORY") != "RichardDaffern/Novel-Retriever":
        raise ValueError("Wrong repository")
    if (os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("GITHUB_RUN_ATTEMPT", "1") != "1"):
        raise ValueError("Refusing duplicate one-shot workflow run")
    report = {"version": 1, "campaign": CAMPAIGN,
              "skipped": plan["skipped"],
              "selected": [r["title"] for r in plan["selected"]],
              "dispatched": False}
    if not plan["selected"]:
        report["reason"] = "Every reviewed title already complete"
        return report
    until = clock() + deadline_seconds
    while q.active_workflows(runner=runner) >= MAX_ACTIVE_BULK_RUNS:
        if clock() >= until:
            raise ValueError("Global two-active-run limit did not free before deadline")
        sleeper(75)
    urls = ",".join(r["url"] for r in plan["selected"])
    runner(["gh", "workflow", "run", "library-bulk-download.yml", "--ref", "main",
            "--field", "novel_urls=" + urls,
            "--field", "chapter_range=", "--field", "force=false"],
           check=True, timeout=45)
    report["dispatched"] = True
    report["book_count"] = len(plan["selected"])
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        def read(name):
            return json.loads((root / name).read_text(encoding="utf-8"))
        plan = prepare(
            manifest=json.loads(args.manifest.read_text(encoding="utf-8")),
            registry=read("downloaded_novels.json"),
            backlog=read("campaigns/yup-pilot/backlog-163.json"),
            verified=read("campaigns/yup-pilot/verified-urls.json"),
            denied=read("campaigns/overnight/excluded-90.json"),
            blocked=read("campaigns/overnight/blocked-full-retries-20261120.json"),
        )
        print("Reviewed source/registry preflight:",
              {"reviewed": plan["source_reviewed"],
               "eligible": len(plan["selected"]),
               "already_complete": len(plan["skipped"])}, flush=True)
        report = dispatch(plan)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Curated Yup bulk download:",
              {"dispatched": report["dispatched"],
               "books": len(report["selected"])}, flush=True)
        return 0
    except (ValueError, OSError, json.JSONDecodeError,
            subprocess.SubprocessError) as exc:
        print("Curated Yup launch stopped safely:", str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
