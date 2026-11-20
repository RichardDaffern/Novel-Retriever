"""Offline tests for larger source-verified download batches and strict exclusions."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import large_batch_dispatch as d
from tools import overnight_queue as q


def verified(title, tier="Yup"):
    return {"title": title, "tier": tier, "url": q.candidate_urls(title)[0],
            "evidence": "public_listing_exact_title"}


class LargeBatchTests(unittest.TestCase):
    def test_prioritises_yup_and_never_requeues_known_failures(self):
        source = {"version": 1, "campaign": q.CAMPAIGN, "verified": [
            verified("Fresh B", "Idk"), verified("Blocked Novel"),
            verified("Fresh A"), verified("Already Archived"),
            verified("Fresh C", "Idk"),
        ]}
        blocked = {"version": 1, "titles": ["Blocked Novel"]}
        with patch.object(q, "manifests", return_value=(
            ["Blocked Novel", "Fresh A", "Already Archived"],
            ["Fresh B", "Fresh C"], set(), {q.norm("Already Archived")}
        )):
            selected, counts = d.prepare(source, blocked, max_books=3)
        self.assertEqual([x["title"] for x in selected],
                         ["Fresh A", "Fresh B", "Fresh C"])
        self.assertEqual(counts["blocked"], 1)
        self.assertEqual(counts["known"], 1)

    def test_requires_exact_public_listing_without_guessing_urls(self):
        for bad in (
            {"version": 1, "campaign": q.CAMPAIGN, "verified": [
                {**verified("Fresh A"), "url": "https://novelfull.com/some-other.html"}]},
            {"version": 1, "campaign": q.CAMPAIGN, "verified": [
                {**verified("Fresh A"), "evidence": "guess"}]},
            {"version": 1, "campaign": q.CAMPAIGN, "verified": [
                {**verified("Fresh A"), "tier": "Idk"}]},
        ):
            with patch.object(q, "manifests", return_value=(
                ["Fresh A"], [], set(), set()
            )), self.assertRaises(q.QueueError):
                d.prepare(bad, {"version": 1, "titles": []})
        with self.assertRaises(q.QueueError):
            d.prepare({"version": 1, "campaign": q.CAMPAIGN, "verified": []},
                      {"version": 1, "titles": []}, max_books=49)

    def test_dispatches_two_large_groups_without_force_or_unsupported_args(self):
        selected = [
            {"title": f"Novel {n}", "tier": "Yup",
             "url": q.candidate_urls(f"Novel {n}")[0]} for n in range(24)
        ]
        seen, naps = [], []
        def fake_runner(cmd, **kwargs):
            seen.append(cmd)
            return None
        with TemporaryDirectory() as folder, patch.object(
            q, "active_workflows", return_value=0
        ), patch.dict("os.environ", {
            "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
            "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1",
        }):
            result = d.run(selected, Path(folder) / "report.json",
                           batch_size=12, runner=fake_runner,
                           sleeper=naps.append)
            self.assertEqual([row["books"] for row in result["submitted"]], [12, 12])
            self.assertEqual(result["held"], [])
            self.assertEqual(naps, [d.DISPATCH_DELAY])
            self.assertEqual(len(seen), 2)
            self.assertTrue(all("force=false" in command for command in seen))
            self.assertTrue(all(command[0:3] == ["gh", "workflow", "run"]
                                for command in seen))
            self.assertEqual(json.loads((Path(folder)/"report.json").read_text("utf-8"))["held"], [])

    def test_global_cap_and_rerun_guard(self):
        with TemporaryDirectory() as folder:
            with patch.dict("os.environ", {
                "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
                "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "2",
            }), self.assertRaises(q.QueueError):
                d.run([], Path(folder) / "out.json")
            with patch.dict("os.environ", {
                "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
                "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1",
            }), self.assertRaises(q.QueueError):
                d.run([], Path(folder) / "out.json", max_active=4)


if __name__ == "__main__":
    unittest.main()
