"""Offline tests for the read-only GitHub chapter artefact inventory."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import subprocess
import unittest
from unittest.mock import patch

from tools.chapter_artifact_inventory import (
    fetch_pages, intervals_difference, intervals_union, inventory,
)

URL = "https://freewebnovel.com/novel/omega-summoner"
KEY = sha256(URL.encode()).hexdigest()[:20]
NOW = datetime(2026, 11, 23, tzinfo=timezone.utc)


def batch(start, end, *, kind="chapter-batch", run=100, expired=False, artifact_id=1):
    prefix = f"chapter-batch-{KEY}" if kind == "chapter-batch" else f"partial-batch-{run}-{KEY}"
    return {"name": f"{prefix}-{start:05d}-{end:05d}", "id": artifact_id,
            "expires_at": "2027-02-17T00:00:00Z", "expired": expired}


def job(start, end):
    return {"name": f"freewebnovel ({URL}, false) / chapter-batches ({start}, {end}, chapter-batch-{KEY}-{start:05d}-{end:05d})"}


class InventoryTests(unittest.TestCase):
    def test_inclusive_union_and_difference(self):
        self.assertEqual(intervals_union([(3, 4), (1, 2), (4, 9), (15, 20)]), [[1, 9], [15, 20]])
        self.assertEqual(intervals_difference([[1, 100]], [[1, 50], [81, 100]]), [[51, 80]])
        self.assertEqual(intervals_difference([[100, 120]], []), [[100, 120]])
        with self.assertRaises(ValueError):
            intervals_union([(4, 3)])

    def test_complete_vs_partial_and_missing_range(self):
        runs = [{"run_id": 100, "artifacts": [batch(1, 50),
                 batch(51, 100, kind="partial-batch", artifact_id=2),
                 batch(101, 120, artifact_id=3)],
                 "jobs": [job(1, 50), job(51, 100), job(101, 120)]}]
        source = inventory("owner/repo", runs, now=NOW)["sources"][0]
        self.assertEqual(source["source_url"], URL)
        self.assertEqual(source["unexpired_complete_batches"], 2)
        self.assertEqual(source["unexpired_partial_checkpoints"], 1)
        self.assertEqual(source["artifact_name_coverage"], [[1, 50], [101, 120]])
        self.assertEqual(source["uncovered_planned_ranges"], [[51, 100]])
        self.assertFalse(source["coverage_is_content_verified"])

    def test_multiple_runs_duplicates_and_expiry(self):
        runs = [{"run_id": 100, "artifacts": [batch(1, 50), batch(51, 100, expired=True)],
                 "jobs": [job(1, 50), job(51, 100)]},
                {"run_id": 101, "artifacts": [batch(51, 100, run=101)],
                 "jobs": [job(51, 100)]}]
        source = inventory("owner/repo", runs, now=NOW)["sources"][0]
        self.assertEqual(source["artifact_name_coverage"], [[1, 100]])
        self.assertEqual(source["uncovered_planned_ranges"], [])
        self.assertEqual(source["unexpired_complete_batches"], 2)

    def test_reject_cross_run_checkpoint_and_duplicate_run(self):
        source = inventory("owner/repo", [{"run_id": 100,
                "artifacts": [batch(51, 100, kind="partial-batch", run=99)],
                "jobs": [job(51, 100)]}], now=NOW)["sources"][0]
        self.assertEqual(source["unexpired_partial_checkpoints"], 0)
        self.assertEqual(source["uncovered_planned_ranges"], [[51, 100]])
        with self.assertRaises(ValueError):
            inventory("owner/repo", [{"run_id": 1}, {"run_id": 1}], now=NOW)

    @patch("tools.chapter_artifact_inventory.subprocess.run")
    def test_fetch_pages_paginates(self, invoke):
        invoke.side_effect = [
            subprocess.CompletedProcess([], 0, json.dumps({"artifacts": [{}] * 100}), ""),
            subprocess.CompletedProcess([], 0, json.dumps({"artifacts": [{"name": "last"}]}), ""),
        ]
        self.assertEqual(len(fetch_pages("owner/repo", 100, "artifacts")), 101)
        self.assertIn("page=2", invoke.call_args_list[1].args[0][2])


if __name__ == "__main__":
    unittest.main()
