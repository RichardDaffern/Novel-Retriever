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
        self.assertEqual(chosen, [])
        self.assertEqual(len(held), 43)
        matched = [x for x in entries
                   if x["review_state"] == "public_source_listing_matched"]
        self.assertEqual(
            sum(x["reason"] == "rights_not_verified" for x in held),
            len(matched),
        )
        self.assertIn(
            ("Naruto: The Wind Calamity", "rights_not_verified"),
            [(x["title"], x["reason"]) for x in held],
        )

    def test_already_downloaded_gamer_ninja_not_rescheduled(self):
        chosen, held = fanfic.eligible_entries(self.catalogue, self.registry)
        # The production registry grows as downloads finish. Test its current
        # deduplication behaviour rather than assuming all ten are pending.
        completed = {
            record["url"] for record in self.registry["novels"]
            if any(d.get("range") == "all" and d.get("status") == "complete"
                   for d in record.get("downloads", []))
        }
        self.assertEqual(chosen, [])
        self.assertEqual(len(held), 43)
        self.assertTrue(all(item["url"] not in completed for item in chosen))
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
        self.assertEqual(chosen, [])
        self.assertIn(
            ("Naruto: The Wind Calamity", "already_in_complete_registry"),
            [(x["title"], x["reason"]) for x in held]
        )

    def test_explicit_rights_flags_are_required_for_fanfiction_queueing(self):
        import copy
        catalogue = copy.deepcopy(self.catalogue)
        matched = [row for row in catalogue["entries"]
                   if row["review_state"] == "public_source_listing_matched"]
        self.assertGreater(len(matched), 0)
        matched[0]["rights_verified"] = True
        matched[0]["public_distribution_verified"] = True
        chosen, held = fanfic.eligible_entries(catalogue, {"novels": []})
        self.assertEqual(len(chosen), 1)
        self.assertEqual(chosen[0]["title"], matched[0]["title_as_shown"])
        self.assertEqual(
            sum(row["reason"] == "rights_not_verified" for row in held),
            len(matched) - 1,
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
        # A synthetic rights-reviewed catalogue proves the queue remains
        # usable only when every dispatched title has explicit archive and
        # public-distribution evidence.
        import copy
        approved = copy.deepcopy(self.catalogue)
        for row in approved["entries"]:
            if row["review_state"] == "public_source_listing_matched":
                row["rights_verified"] = True
                row["public_distribution_verified"] = True
        pending, _ = fanfic.eligible_entries(approved, {"novels": []})
        with patch.object(fanfic, "read_json", side_effect=lambda path: (
            {"novels": []} if path == fanfic.REGISTRY else approved
        )), patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
            "GITHUB_ACTIONS": "false",
        }):
            report = fanfic.dispatch(runner=runner, sleeper=slept.append,
                                     clock=lambda: 0, minutes=1)
        actions = [row for row in sent if row[:3] == ["gh", "workflow", "run"]]
        expected_batches = (len(pending) + fanfic.MAX_PER_BATCH - 1) // fanfic.MAX_PER_BATCH
        self.assertEqual(len(actions), expected_batches)
        self.assertEqual(
            [len(batch["titles"]) for batch in report["submitted"]],
            [min(fanfic.MAX_PER_BATCH, len(pending) - i * fanfic.MAX_PER_BATCH)
             for i in range(expected_batches)],
        )
        self.assertEqual(slept, [fanfic.DISPATCH_SPACING_SECONDS] * max(0, expected_batches - 1))
        for call in actions:
            self.assertIn("force=false", call)
            self.assertIn("chapter_range=", call)
            self.assertIn("confirm_rights=true", call)
            self.assertEqual(call[call.index("--ref") + 1], "main")
            self.assertTrue(all("webnovel.com/book" not in arg for arg in call))

    def test_capacity_limit_prevents_burst(self):
        counts = iter([2])
        slept = []
        sent = []
        def fake_active(_runner):
            return next(counts)
        def runner(cmd, **kwargs):
            sent.append(cmd)
            return SimpleNamespace()
        # Two already-active bulk workflows block the next batch.
        approved = __import__("copy").deepcopy(self.catalogue)
        for row in approved["entries"]:
            if row["review_state"] == "public_source_listing_matched":
                row["rights_verified"] = True
                row["public_distribution_verified"] = True
        with patch.object(fanfic, "read_json", side_effect=lambda path: (
            {"novels": []} if path == fanfic.REGISTRY else approved
        )), patch.object(fanfic, "active_bulk_runs", side_effect=fake_active), patch.dict(
            os.environ, {"GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
                         "GITHUB_ACTIONS": "false"}
        ):
            now = iter([0, 0, 61])
            report = fanfic.dispatch(runner=runner, sleeper=slept.append,
                                     clock=lambda: next(now, 61), minutes=1)
        self.assertEqual(report["submitted"], [])
        self.assertEqual(len(report["held"]), 43)
        self.assertEqual(slept, [fanfic.POLL_SECONDS])

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
