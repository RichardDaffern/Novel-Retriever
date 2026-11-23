#!/usr/bin/env python3
"""Read-only inventory of GitHub Actions chapter-batch and checkpoint artefacts.

This command does not download story content, dispatch jobs, alter registry
records or regard an artefact name as proof of valid chapter contents.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
ARTIFACT = re.compile(
    r"^(chapter-batch|partial-batch)-(?:([0-9]+)-)?([0-9a-f]{20})-([0-9]+)-([0-9]+)$"
)
JOB_BATCH = re.compile(r"chapter-batch-([0-9a-f]{20})-([0-9]+)-([0-9]+)")
SOURCE_URL = re.compile(r"https?://[^\s,)]+")


def intervals_union(ranges: list[tuple[int, int]]) -> list[list[int]]:
    """Merge overlapping or touching inclusive chapter intervals."""
    merged: list[list[int]] = []
    for start, end in sorted(set(ranges)):
        if start < 1 or end < start:
            raise ValueError(f"Invalid chapter interval: {start}-{end}")
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(end, merged[-1][1])
        else:
            merged.append([start, end])
    return merged


def intervals_difference(planned: list[list[int]], complete: list[list[int]]) -> list[list[int]]:
    """Planned chapter intervals without complete-batch artefact coverage."""
    output: list[tuple[int, int]] = []
    for start, end in planned:
        cursor = start
        for good_start, good_end in complete:
            if good_end < cursor:
                continue
            if good_start > end:
                break
            if good_start > cursor:
                output.append((cursor, min(end, good_start - 1)))
            cursor = max(cursor, good_end + 1)
            if cursor > end:
                break
        if cursor <= end:
            output.append((cursor, end))
    return intervals_union(output)


def inventory(repo: str, runs: list[dict[str, Any]], *, now: datetime | None = None) -> dict[str, Any]:
    """Summarise metadata only: saved names are not chapter validation."""
    if not REPOSITORY.fullmatch(repo):
        raise ValueError("Repository must have owner/name syntax")
    now = now or datetime.now(timezone.utc)
    sources: dict[str, dict[str, Any]] = {}
    seen_runs: set[int] = set()
    run_summaries = []

    def entry(key: str) -> dict[str, Any]:
        return sources.setdefault(key, {"key": key, "source_url": None,
                                        "complete_batch_artifacts": [],
                                        "partial_checkpoint_artifacts": [],
                                        "planned": set(), "possible_urls": set()})

    for run in runs:
        run_id = int(run["run_id"])
        if run_id < 1 or run_id in seen_runs:
            raise ValueError("Run IDs must be unique positive integers")
        seen_runs.add(run_id)
        artifacts = run.get("artifacts", [])
        jobs = run.get("jobs", [])
        run_summaries.append({"run_id": run_id, "artifacts_seen": len(artifacts),
                              "jobs_seen": len(jobs)})
        for artifact in artifacts:
            name = artifact.get("name", "")
            match = ARTIFACT.fullmatch(name)
            if not match:
                continue
            kind, embedded_run, key, first, last = match.groups()
            if kind == "partial-batch" and embedded_run != str(run_id):
                continue  # A cross-run checkpoint name is not trustworthy.
            if kind == "chapter-batch" and embedded_run is not None:
                continue
            first, last = int(first), int(last)
            if first < 1 or last < first:
                continue
            expiration = artifact.get("expires_at")
            expired = bool(artifact.get("expired", False))
            if expiration:
                expires = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
                expired = expired or expires <= now
            record = {"artifact_id": artifact.get("id"), "run_id": run_id,
                      "name": name, "start": first, "end": last,
                      "expires_at": expiration, "expired": expired}
            field = "complete_batch_artifacts" if kind == "chapter-batch" else "partial_checkpoint_artifacts"
            entry(key)[field].append(record)

        for job in jobs:
            name = job.get("name", "")
            match = JOB_BATCH.search(name)
            if not match:
                continue
            key, first, last = match.groups()
            first, last = int(first), int(last)
            if first < 1 or last < first:
                continue
            group = entry(key)
            group["planned"].add((first, last))
            for url_match in SOURCE_URL.finditer(name):
                url = url_match.group(0)
                if sha256(url.encode("utf-8")).hexdigest()[:20] == key:
                    group["possible_urls"].add(url)

    result_sources = []
    for key, group in sorted(sources.items()):
        valid_complete = [a for a in group["complete_batch_artifacts"] if not a["expired"]]
        valid_partial = [a for a in group["partial_checkpoint_artifacts"] if not a["expired"]]
        coverage = intervals_union([(a["start"], a["end"]) for a in valid_complete])
        planned = intervals_union(list(group["planned"]))
        gap = intervals_difference(planned, coverage)
        urls = sorted(group.pop("possible_urls"))
        group["source_url"] = urls[0] if len(urls) == 1 else None
        group.pop("planned")
        group["complete_batch_artifacts"].sort(key=lambda a: (a["start"], a["end"], a["run_id"]))
        group["partial_checkpoint_artifacts"].sort(key=lambda a: (a["start"], a["end"], a["run_id"]))
        group.update({"planned_ranges": planned,
                      "artifact_name_coverage": coverage,
                      "uncovered_planned_ranges": gap,
                      "unexpired_complete_batches": len(valid_complete),
                      "unexpired_partial_checkpoints": len(valid_partial),
                      "source_identity_ambiguous": len(urls) > 1,
                      "coverage_is_content_verified": False})
        result_sources.append(group)
    return {"version": 1, "repository": repo, "checked_at": now.isoformat(),
            "read_only": True, "runs": run_summaries, "sources": result_sources}


def fetch_pages(repo: str, run_id: int, collection: str) -> list[dict[str, Any]]:
    """Fetch all pages, never silently truncate the first hundred artefacts."""
    if collection not in {"artifacts", "jobs"}:
        raise ValueError("Unsupported GitHub collection")
    path = f"repos/{repo}/actions/runs/{run_id}/{collection}"
    rows: list[dict[str, Any]] = []
    for page in range(1, 1001):
        completed = subprocess.run(
            ["gh", "api", f"{path}?per_page=100&page={page}"],
            text=True, capture_output=True, check=True, timeout=60,
        )
        data = json.loads(completed.stdout)
        items = data.get(collection)
        if not isinstance(items, list):
            raise ValueError(f"Unexpected {collection} API response for {run_id}")
        rows.extend(items)
        if len(items) < 100:
            return rows
    raise ValueError("GitHub API pagination exceeded safety limit")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""),
                        help="Repository owner/name")
    parser.add_argument("--run", type=int, action="append", required=True,
                        help="Existing GitHub Actions run ID (repeatable)")
    parser.add_argument("--output", type=Path, required=True,
                        help="JSON metadata inventory output")
    opts = parser.parse_args(argv)
    if not REPOSITORY.fullmatch(opts.repo):
        parser.error("--repo must be owner/name")
    if any(run < 1 for run in opts.run) or len(set(opts.run)) != len(opts.run):
        parser.error("--run values must be unique positive IDs")
    if opts.output.exists():
        parser.error("Output already exists; choose a new path")
    runs = [{"run_id": rid, "artifacts": fetch_pages(opts.repo, rid, "artifacts"),
             "jobs": fetch_pages(opts.repo, rid, "jobs")} for rid in opts.run]
    result = inventory(opts.repo, runs)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Inventoried {len(runs)} runs and {len(result['sources'])} source keys; metadata only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
