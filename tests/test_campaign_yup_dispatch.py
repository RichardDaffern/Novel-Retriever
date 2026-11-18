"""Offline safety tests for the explicitly verified Yup pilot download campaign."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import campaign_yup_dispatch as tool


class SmallYupPilotTests(unittest.TestCase):
    def setUp(self):
        self.entries = tool.manifest_entries(tool._read_json(tool.MANIFEST))
        self.registry = tool._read_json(tool.REGISTRY)
        self.paths = [
            f"campaigns/yup-pilot/requests/batch-{i:02d}.json"
            for i in (1, 2, 3)
        ]

    def test_only_six_explicitly_allowlisted_yup_books(self):
        self.assertEqual(len(self.entries), 6)
        self.assertNotIn("The First Order", self.entries)
        self.assertNotIn("Nine Sun God King", self.entries)
        self.assertNotIn("Devil’s Son-in-Law", self.entries)
        self.assertEqual(
            set(self.entries),
            {"Before I Died, I Forcibly Kissed The Heroine",
             "Desolate Era",
             "A Record Of Mortal’s Journey To Immortality",
             "Archean Eon Art",
             "All My Disciples Suck!",
             "Ancient Godly Monarch"},
        )

    def test_three_independent_two_book_requests_preflight(self):
        # The live registry is updated by successful jobs throughout this
        # campaign; this structural test must not depend on current downloads.
        groups = tool.prepare_batches(
            self.paths, tool._read_json(tool.MANIFEST), {"novels": []}
        )
        self.assertEqual([len(urls) for _, urls in groups], [2, 2, 2])
        self.assertEqual(len({url for _, urls in groups for url in urls}), 6)

    def test_source_urls_must_be_direct_https_book_links(self):
        for bad in (
            "http://novelfull.com/test.html",
            "https://novelfull.com.evil.test/book.html",
            "https://freewebnovel.com/novel/book/chapter-10",
            "https://freewebnovel.com/novel/book?token=123",
            "https://freewebnovel.com/novel/book#chapter-1",
            "https://wuxia.click/book/1",
        ):
            with self.subTest(url=bad), self.assertRaises(tool.CampaignError):
                tool._book_url(bad)

    def test_registry_complete_urls_skipped_and_forcing_never_sent(self):
        manifest = tool._read_json(tool.MANIFEST)
        url = self.entries["Desolate Era"]
        registry = {"novels": [
            {"url": url, "downloads": [{"range": "all", "status": "complete"}]}
        ]}
        groups = tool.prepare_batches(self.paths, manifest, registry)
        self.assertEqual([len(urls) for _, urls in groups], [1, 2, 2])
        seen = []
        count = tool.dispatch(groups, runner=lambda *args, **kwargs: seen.append((args, kwargs)),
                              sleeper=lambda seconds: None)
        self.assertEqual(count, 3)
        self.assertEqual(len(seen), 3)
        for (args, kwargs) in seen:
            self.assertEqual(args[0][0:3], ["gh", "workflow", "run"])
            self.assertIn("force=false", args[0])
            self.assertNotIn(url, " ".join(args[0]))
            self.assertTrue(kwargs["check"])

    def test_unapproved_dropped_title_and_duplicate_batch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "campaigns/yup-pilot/requests").mkdir(parents=True)
            bad = {"campaign": tool.CAMPAIGN, "titles": ["The First Order"]}
            path = root / "campaigns/yup-pilot/requests/batch-99.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with patch.object(tool, "ROOT", root):
                with self.assertRaisesRegex(tool.CampaignError, "absent"):
                    tool.prepare_batches(["campaigns/yup-pilot/requests/batch-99.json"],
                                         tool._read_json(tool.MANIFEST), {"novels": []})
            with self.assertRaisesRegex(tool.CampaignError, "distinct"):
                tool.prepare_batches([self.paths[0], self.paths[0]],
                                     tool._read_json(tool.MANIFEST), self.registry)

    def test_no_new_batch_files_never_dispatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "changed.txt"
            path.write_text("", encoding="utf-8")
            self.assertEqual(tool.main(["--paths-file", str(path)]), 0)

    def test_rerun_guard_prevents_duplicate_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "changed.txt"
            path.write_text("\n".join(self.paths), encoding="utf-8")
            with patch.dict("os.environ", {"GITHUB_ACTIONS": "true",
                                          "GITHUB_RUN_ATTEMPT": "2"}):
                self.assertEqual(tool.main(["--paths-file", str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
