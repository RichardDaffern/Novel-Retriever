"""Offline fanfiction campaign regression tests; never touch public chapters."""
from __future__ import annotations

import json
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import fanfiction_campaign as fanfic


class FanfictionCampaignTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = fanfic.read_json(fanfic.CATALOGUE)
        self.registry = fanfic.read_json(fanfic.REGISTRY)

    def test_all_screenshots_preserved_and_only_public_source_matches_eligible(self):
        chosen, held = fanfic.eligible_entries(self.catalogue, {"novels": []})
        entries = self.catalogue["entries"]
        self.assertEqual(len(entries), 43)
        self.assertEqual(sum(x["franchise"] == "Naruto" for x in entries), 24)
        self.assertEqual(sum(x["franchise"] == "Harry Potter" for x in entries), 19)
        self.assertEqual(len(chosen), 10)
        self.assertEqual(len(held), 33)
        self.assertTrue(all(x["url"].startswith("https://freewebnovel.com/novel/")
                            for x in chosen))
        self.assertIn("Naruto: The Wind Calamity",
                      [x["matched_title"] for x in chosen])
        self.assertIn("HP: A Magical Journey",
                      [x["matched_title"] for x in chosen])

    def test_already_downloaded_gamer_ninja_not_rescheduled(self):
        chosen, held = fanfic.eligible_entries(self.catalogue, self.registry)
        self.assertEqual(len(chosen), 10)
        self.assertIn(
            ("The Adventurous Gamer Ninja - Daichi Hekima", "already_downloaded"),
            [(x["title"], x["reason"]) for x in held]
        )

    def test_registry_completion_prevents_duplicate_fetch(self):
        candidate = next(x for x in self.catalogue["entries"]
                         if x.get("matched_title") == "Naruto: The Wind Calamity")
        registry = {"novels": [{"url": candidate["source_url"],
                               "title": "Naruto: The Wind Calamity",
                               "downloads": [{"range": "all", "status": "complete"}]}]}
        chosen, held = fanfic.eligible_entries(self.catalogue, registry)
        self.assertEqual(len(chosen), 9)
        self.assertIn(
            ("Naruto: The Wind Calamity", "already_in_complete_registry"),
            [(x["title"], x["reason"]) for x in held]
        )

    def test_unverified_titles_cannot_smuggle_url_into_queue(self):
        import copy
        catalogue = copy.deepcopy(self.catalogue)
        row = next(x for x in catalogue["entries"]
                   if x["review_state"] == "needs_source_verification")
        row["source_url"] = "https://freewebnovel.com/novel/made-up"
        with self.assertRaisesRegex(fanfic.FanficQueueError, "Unverified"):
            fanfic.eligible_entries(catalogue, {"novels": []})

    def test_duplicate_and_external_source_url_rejected(self):
        import copy
        for bad_url in ("https://www.webnovel.com/book/123",
                        "https://freewebnovel.com/novel/something?token=x",
                        "http://freewebnovel.com/novel/book"):
            catalogue = copy.deepcopy(self.catalogue)
            row = next(x for x in catalogue["entries"] if x.get("source_url"))
            row["source_url"] = bad_url
            with self.subTest(bad_url=bad_url), self.assertRaises(
                    fanfic.FanficQueueError):
                fanfic.eligible_entries(catalogue, {"novels": []})

    def test_run_sends_two_books_only_with_force_false_and_rate_spacing(self):
        sent = []
        slept = []
        def runner(cmd, **kwargs):
            sent.append(cmd)
            if cmd[:2] == ["gh", "api"]:
                return SimpleNamespace(stdout=json.dumps({"workflow_runs": []}))
            return SimpleNamespace()
        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
                                     "GITHUB_ACTIONS": "false"}):
            report = fanfic.dispatch(runner=runner, sleeper=slept.append,
                                     clock=lambda: 0, minutes=1)
        actions = [row for row in sent if row[:3] == ["gh", "workflow", "run"]]
        self.assertEqual(len(actions), 5)
        self.assertEqual([len(batch["titles"]) for batch in report["submitted"]],
                         [2, 2, 2, 2, 2])
        self.assertEqual(slept, [150, 150, 150, 150])
        for call in actions:
            self.assertIn("force=false", call)
            self.assertIn("chapter_range=", call)
            self.assertEqual(call[call.index("--ref") + 1], "main")
            self.assertTrue(all("webnovel.com/book" not in arg for arg in call))

    def test_capacity_limit_prevents_burst(self):
        counts = iter([4, 3])
        slept = []
        sent = []
        def fake_active(_runner):
            return next(counts)
        def runner(cmd, **kwargs):
            sent.append(cmd)
            return SimpleNamespace()
        with patch.object(fanfic, "active_bulk_runs", side_effect=fake_active):
            # one published slot after first polling pause, then stop the
            # subsequent cycle at the bounded deadline
            now = iter([0, 0, 0, 10000])
            report = fanfic.dispatch(runner=runner, sleeper=slept.append,
                                     clock=lambda: next(now, 10000), minutes=1)
        self.assertEqual(len(report["submitted"]), 1)
        self.assertEqual(len(report["held"]), 41)
        self.assertEqual(slept, [fanfic.POLL_SECONDS,
                                 fanfic.DISPATCH_SPACING_SECONDS])

    def test_reruns_do_not_duplicate_pipeline_dispatches(self):
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true",
                                     "GITHUB_RUN_ATTEMPT": "2"}):
            report = fanfic.dispatch(
                runner=lambda *_args, **_kwargs:
                    (_ for _ in ()).throw(AssertionError("Unexpected CLI action"))
            )
        self.assertEqual(report["submitted"], [])
        self.assertEqual(len(report["held"]), 43)
        self.assertEqual(report["reason"], "GitHub Actions re-runs do not dispatch")


if __name__ == "__main__":
    unittest.main()
