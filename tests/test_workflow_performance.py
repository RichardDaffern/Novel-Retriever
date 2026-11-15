"""Offline regression tests for read-only GitHub Actions timing metrics."""
from pathlib import Path
import unittest
from urllib.request import Request

from tools.workflow_performance import (
    classify_step, fetch_jobs, markdown_summary, performance_report,
)


def step(name, start, end, *, status="completed"):
    return {
        "name": name, "status": status,
        "started_at": f"2026-11-15T09:00:{start:02d}Z",
        "completed_at": f"2026-11-15T09:00:{end:02d}Z",
    }


class PerformanceTests(unittest.TestCase):
    def test_parallel_step_sums_are_not_mistaken_for_elapsed_time(self):
        jobs = [
            {
                "status": "completed", "conclusion": "success",
                "started_at": "2026-11-15T09:00:00Z",
                "completed_at": "2026-11-15T09:00:12Z",
                "steps": [
                    step("Install downloader dependencies", 0, 2),
                    step("Recover previous complete batch or download range", 2, 12),
                ],
            },
            {
                "status": "completed", "conclusion": "success",
                "started_at": "2026-11-15T09:00:01Z",
                "completed_at": "2026-11-15T09:00:11Z",
                "steps": [step("Recover previous complete batch or download range", 1, 11)],
            },
            {
                "status": "in_progress", "conclusion": None,
                "started_at": "2026-11-15T09:00:12Z",
                "completed_at": None, "steps": [
                    step("Validate and package all completed novels separately", 12, 14)
                ],
            },
        ]
        report = performance_report(jobs, run_id="123", repository="Owner/Repo")
        self.assertEqual(report["completed_jobs"], 2)
        self.assertEqual(report["incomplete_jobs"], 1)
        self.assertEqual(report["completed_jobs_window_seconds"], 12)
        self.assertEqual(
            report["phase_totals"]["chapter_download_or_reuse"]["sum_step_seconds"], 20)
        self.assertEqual(report["phase_totals"]["setup"]["sum_step_seconds"], 2)
        self.assertEqual(report["phase_totals"]["recovery"]["sum_step_seconds"], 2)
        self.assertEqual(report["timed_steps"], 4)
        self.assertIn("parallel jobs", markdown_summary(report))

    def test_classifies_major_workflow_phases(self):
        cases = {
            "Run actions/checkout@xx": "setup",
            "Run actions/setup-python@yy": "setup",
            "Install pinned dependencies": "setup",
            "Index chapters and calculate batches": "discovery_and_planning",
            "Download and verify author cross-post": "chapter_download_or_reuse",
            "Assemble and validate combined EPUB and TXT chapters": "assembly_and_validation",
            "Prepare standard novel artefact folder": "assembly_and_validation",
            "Upload complete novel archive": "artifact_transfer",
            "Retrieve every complete chapter batch": "artifact_transfer",
            "Regenerate registry from latest main and automatically merge PR": "registry_publication",
            "Update metadata-only download registry": "registry_publication",
            "Validate and package all completed novels separately": "recovery",
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                self.assertEqual(classify_step(name), value)

    def test_paginated_jobs_api_is_restricted_to_github(self):
        requests = []

        def provider(req: Request):
            requests.append(req)
            page = int(req.full_url.rsplit("=", 1)[-1])
            return {
                "total_count": 101,
                "jobs": [{"status": "completed", "steps": []}] *
                        (100 if page == 1 else 1),
            }

        jobs = fetch_jobs("Owner/Repo", "123", "fake-read-token", get_json=provider)
        self.assertEqual(len(jobs), 101)
        self.assertEqual(len(requests), 2)
        self.assertTrue(all(req.full_url.startswith(
            "https://api.github.com/repos/Owner/Repo/") for req in requests))
        self.assertTrue(all(req.get_header("Authorization") == "Bearer fake-read-token"
                            for req in requests))
        with self.assertRaisesRegex(ValueError, "owner/repository"):
            fetch_jobs("other/third/fourth", "123", "token", get_json=provider)
        with self.assertRaisesRegex(ValueError, "positive numeric"):
            fetch_jobs("Owner/Repo", "0", "token", get_json=provider)

    def test_incomplete_pagination_refused(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            fetch_jobs(
                "Owner/Repo", "123", "token",
                get_json=lambda _: {"total_count": 101, "jobs": []},
            )

    def test_bad_timestamps_are_skipped(self):
        report = performance_report([{
            "status": "completed", "conclusion": "failure",
            "started_at": "2026-11-15T09:00:05Z",
            "completed_at": "2026-11-15T09:00:03Z",
            "steps": [{"name": "Install dependencies", "status": "completed",
                       "started_at": None, "completed_at": None}],
        }], run_id="22")
        self.assertEqual(report["failed_or_cancelled_jobs"], 1)
        self.assertEqual(report["timed_steps"], 0)
        self.assertIsNone(report["completed_jobs_window_seconds"])

    def test_existing_batch_artifact_scope_is_retained(self):
        key = "needs.prepare.outputs.key"
        for filename in ("download-novel.yml", "freewebnovel-download.yml"):
            src = Path(".github/workflows", filename).read_text(encoding="utf-8")
            expected = "pattern: chapter-batch-$" + "{{ " + key + " }}-*"
            self.assertIn(expected, src)
            self.assertIn("merge-multiple: false", src)
        bulk = Path(".github/workflows/library-bulk-download.yml").read_text(
            encoding="utf-8")
        self.assertIn("tools.workflow_performance", bulk)
        self.assertIn("compression-level: 0", bulk)
        self.assertIn("bulk-performance-$" + "{{ github.run_id }}", bulk)


if __name__ == "__main__":
    unittest.main()
