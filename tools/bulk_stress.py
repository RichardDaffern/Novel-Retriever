"""Network-free stress checks for 20, 50 and 100 grouped bulk selections.

No real novel sites are contacted, no chapter text is downloaded, and no
production registry is modified. Exercises deduplication, cached skips,
per-site matrix output and GitHub's true 256-job planning ceiling.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import tempfile
import time
from unittest.mock import patch

from tools.library_bulk import MAX_MATRIX_JOBS, selection_plan, write_actions


def synthetic_urls(n: int) -> list[str]:
    return [
        (f"https://novelfull.com/synthetic-stress-{i:04d}.html"
         if i % 2 == 0
         else f"https://freewebnovel.com/novel/synthetic-stress-{i:04d}")
        for i in range(n)
    ]


def run_stress(sizes: tuple[int, ...] = (20, 50, 100)) -> list[dict]:
    results = []
    for requested in sizes:
        if requested <= 0 or requested > MAX_MATRIX_JOBS:
            raise ValueError("Stress size must be between 1 and 256")
        urls = synthetic_urls(requested)
        # Deliberate repeat of the first four URLs simulates duplicate input.
        raw = ";\n".join(urls + urls[:4])
        registry = {"version": 1, "novels": [
            {
                "url": url,
                "title": f"Cached Synthetic Novel {index}",
                "downloads": [{
                    "range": "all", "status": "complete",
                    "expires_at_utc": "2099-12-31T23:59:59Z",
                }],
            }
            for index, url in enumerate(urls[:3])
        ]}
        curated = {"version": 1, "novels": []}
        started = time.monotonic()
        plan = selection_plan(registry, curated, "", raw, "All")
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "output"
            summary = Path(folder) / "summary.md"
            with patch.dict(os.environ, {
                "GITHUB_OUTPUT": str(out), "GITHUB_STEP_SUMMARY": str(summary),
            }), redirect_stdout(StringIO()):
                write_actions(plan)
            records = dict(line.split("=", 1) for line in out.read_text().splitlines())
            matrices = [
                json.loads(records[f"{site}_matrix"])["include"]
                for site in ("novelfull", "freewebnovel", "scribblehub")
            ]
            combined = [row["novel_url"] for matrix in matrices for row in matrix]
            assert plan["selected_count"] == requested
            assert len(plan["skipped"]) == 3
            assert len(combined) == requested - 3
            assert len(set(combined)) == len(combined)
            assert records["has_scribblehub"] == "false"
            assert not matrices[2]
            assert "skipped (artifact available): 3" in summary.read_text()
        elapsed = round(time.monotonic() - started, 3)
        results.append({
            "requested": requested, "cached_skipped": len(plan["skipped"]),
            "scheduled": len(combined), "distinct": len(set(combined)),
            "elapsed_seconds": elapsed, "status": "passed",
        })
    # Boundary test: 256 jobs accepted; 257 rejected *before* publishing output.
    upper = selection_plan({"version": 1, "novels": []},
                           {"version": 1, "novels": []}, "",
                           "\n".join(synthetic_urls(256)), "All")
    assert sum(len(v) for v in upper["groups"].values()) == 256
    try:
        selection_plan({"version": 1, "novels": []},
                       {"version": 1, "novels": []}, "",
                       "\n".join(synthetic_urls(257)), "All")
    except ValueError as exc:
        assert "256 matrix jobs" in str(exc)
    else:
        raise AssertionError("257 scheduled downloads did not fail")
    results.append({"requested": 257, "status": "correctly_rejected"})
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-output", type=Path)
    args = ap.parse_args(argv)
    reports = run_stress()
    output = json.dumps({"network_requests": 0, "results": reports}, indent=2)
    print(output)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
