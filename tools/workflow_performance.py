#!/usr/bin/env python3
"""Read-only GitHub Actions timing report.

Step times are summed across parallel jobs; they are NOT overall elapsed
workflow time. Reports include the elapsed window of completed jobs and
never make requests to novel websites.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

MAX_PAGES = 40
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
PHASES = (
    "setup", "discovery_and_planning", "chapter_download_or_reuse",
    "assembly_and_validation", "artifact_transfer", "registry_publication",
    "recovery", "other",
)


def _seconds(start, end):
    if not start or not end:
        return None
    try:
        a = datetime.fromisoformat(start.replace("Z", "+00:00"))
        b = datetime.fromisoformat(end.replace("Z", "+00:00"))
        elapsed = (b - a).total_seconds()
    except (ValueError, AttributeError, TypeError):
        return None
    return elapsed if elapsed >= 0 else None


def classify_step(name: str) -> str:
    low = name.casefold()
    if ("set up job" in low or "checkout" in low or "setup-python" in low or
            "install " in low or low.startswith("post run ")):
        return "setup"
    if ("download and verify author cross-post" in low or
            "recover previous complete batch or download range" in low):
        return "chapter_download_or_reuse"
    if "assemble and validate" in low or "prepare standard novel" in low:
        return "assembly_and_validation"
    if ("regenerate registry" in low or
            "metadata-only download registry" in low or
            "publish registry" in low):
        return "registry_publication"
    if ("validate and package all completed" in low or
            "collect successful per-novel" in low):
        return "recovery"
    if ("upload" in low or "retrieve " in low or "restore chapter plan" in low
            or "fetch previous small recovery" in low or
            "download-artifact" in low):
        return "artifact_transfer"
    if ("plan" in low or "index chapter" in low or
            "check registry" in low or "check completed-download" in low or
            "validate and normalise" in low or "resolve selected names" in low):
        return "discovery_and_planning"
    return "other"


def fetch_jobs(repository: str, run_id: str, token: str, *, get_json=None) -> list[dict]:
    if not REPOSITORY.fullmatch(repository):
        raise ValueError("Expected an owner/repository name")
    if not run_id.isdecimal() or not int(run_id):
        raise ValueError("Expected a positive numeric workflow run ID")
    if not token:
        raise ValueError("Missing read-only GitHub Actions API token")

    def default_request(request: Request) -> dict:
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    getter = get_json or default_request
    results = []
    for page in range(1, MAX_PAGES + 1):
        req = Request(
            f"https://api.github.com/repos/{repository}/actions/runs/"
            f"{run_id}/jobs?per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "Novel-Library-Performance-Report",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        result = getter(req)
        if (not isinstance(result, dict) or
                type(result.get("total_count")) is not int or
                not isinstance(result.get("jobs"), list)):
            raise ValueError("Invalid GitHub Actions jobs API response")
        total = result["total_count"]
        if total < 0:
            raise ValueError("Invalid GitHub Actions job count")
        if total and not result["jobs"]:
            raise ValueError("Incomplete GitHub Actions jobs API pagination")
        results.extend(result["jobs"])
        if len(results) >= total:
            if len(results) != total:
                raise ValueError("Duplicate or inconsistent jobs API pages")
            return results
    raise ValueError(f"Run contains over {MAX_PAGES * 100} jobs; incomplete metrics refused")


def performance_report(jobs: list[dict], *, run_id: str, repository: str = "") -> dict:
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("No GitHub Actions jobs available for measurement")
    totals = {name: {"steps": 0, "sum_step_seconds": 0.0} for name in PHASES}
    finished = failed = running = timed_steps = 0
    job_bounds = []
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError("Invalid GitHub Actions job record")
        if job.get("status") == "completed":
            finished += 1
            failed += int(job.get("conclusion") in ("failure", "cancelled"))
            if _seconds(job.get("started_at"), job.get("completed_at")) is not None:
                job_bounds.append((job["started_at"], job["completed_at"]))
        else:
            running += 1
        for step in job.get("steps") or []:
            if not isinstance(step, dict):
                continue
            duration = _seconds(step.get("started_at"), step.get("completed_at"))
            if duration is None or step.get("status") != "completed":
                continue
            timed_steps += 1
            bucket = totals[classify_step(str(step.get("name", "")))]
            bucket["steps"] += 1
            bucket["sum_step_seconds"] += duration
    for name in PHASES:
        totals[name]["sum_step_seconds"] = round(totals[name]["sum_step_seconds"], 2)
    if job_bounds:
        first = min(datetime.fromisoformat(a.replace("Z", "+00:00")) for a, _ in job_bounds)
        last = max(datetime.fromisoformat(b.replace("Z", "+00:00")) for _, b in job_bounds)
        completed_window = round((last - first).total_seconds(), 2)
    else:
        completed_window = None
    return {
        "version": 1, "source": "GitHub Actions jobs API",
        "repository": repository, "run_id": str(run_id),
        "completed_jobs": finished, "incomplete_jobs": running,
        "failed_or_cancelled_jobs": failed, "timed_steps": timed_steps,
        "completed_jobs_window_seconds": completed_window,
        "phase_totals": totals,
        "notes": [
            "Phase times sum completed steps across parallel jobs; they are not elapsed workflow time.",
            "The completed-jobs window is not full end-to-end duration when a summary job is still running.",
            "Download/reuse steps may restore cached chapters without visiting the source site.",
            "GitHub step timestamps have whole-second granularity.",
        ],
    }


def markdown_summary(report: dict) -> str:
    lines = [
        "## Bulk download timings", "",
        f"Completed jobs: **{report['completed_jobs']}**; "
        f"incomplete jobs: **{report['incomplete_jobs']}**; "
        f"failed/cancelled: **{report['failed_or_cancelled_jobs']}**.",
        "", "| Phase | Summed step time (seconds) | Completed steps |",
        "|---|---:|---:|",
    ]
    for phase, data in report["phase_totals"].items():
        if data["steps"]:
            lines.append(
                f"| {phase.replace('_', ' ').title()} | "
                f"{data['sum_step_seconds']:.1f} | {data['steps']} |"
            )
    elapsed = report["completed_jobs_window_seconds"]
    if elapsed is not None:
        lines.extend(["", f"Completed-jobs elapsed window: **{elapsed:.1f} seconds**."])
    lines.extend([
        "", "Step times overlap across parallel jobs and cannot be summed to",
        "estimate full-workflow wall time. The summary job may still be running.",
    ])
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    p.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--summary", type=Path)
    args = p.parse_args(argv)
    try:
        jobs = fetch_jobs(args.repository, args.run_id, os.environ.get("GH_TOKEN", ""))
        report = performance_report(jobs, run_id=args.run_id, repository=args.repository)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        summary = markdown_summary(report)
        if args.summary:
            with args.summary.open("a", encoding="utf-8") as handle:
                handle.write(summary)
        print(summary)
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"Performance report unavailable: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
