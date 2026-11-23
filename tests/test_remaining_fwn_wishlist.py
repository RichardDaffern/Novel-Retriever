"""Offline checks for the bounded secondary-source campaign."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import remaining_fwn_wishlist as w


class FallbackTests(unittest.TestCase):
    def test_fully_indexed_source_is_candidate(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(w, "pending_titles", return_value=(
                [{"title": "Example Book", "tier": "Idk"}], {"completed_urls": []}
             )), patch.object(w.q, "read_json", return_value={"excluded": []}), \
             patch.object(w, "book_details", return_value={
                "title": "Example Book", "numChapters": 123, "status": "Completed"
             }):
            result = w.discover(Path(td) / "sources.json",
                                fetcher=lambda _: "<html/>", sleeper=lambda _: None)
            self.assertEqual(len(result["verified"]), 1)
            self.assertEqual(result["verified"][0]["chapters"], 123)

    def test_historically_short_source_is_not_downloaded(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(w, "pending_titles", return_value=(
                [{"title": "Doom Lord", "tier": "Yup"}], {"completed_urls": []}
             )), patch.object(w.q, "read_json", return_value={"excluded": []}), \
             patch.object(w, "book_details", return_value={
                "title": "Doom Lord", "numChapters": 155, "status": "Completed"
             }):
            result = w.discover(Path(td) / "sources.json",
                                fetcher=lambda _: "<html/>", sleeper=lambda _: None)
            self.assertEqual(result["verified"], [])
            self.assertIn("shorter", result["held"][0]["reason"])

    def test_recently_queued_books_are_not_redownloaded(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(w, "pending_titles", return_value=(
                [{"title": "Beautiful Time With You", "tier": "Idk"}],
                {"completed_urls": []}
             )), patch.object(w.q, "read_json", return_value={"excluded": []}):
            result = w.discover(Path(td) / "sources.json",
                                fetcher=lambda _: self.fail("Must not fetch reserved book"))
            self.assertEqual(result["verified"], [])
            self.assertEqual(result["requests"], 0)

    def test_dispatch_uses_existing_workflow_without_force(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(w, "pending_titles", return_value=(
                [{"title": "Example Book", "tier": "Idk"}], {"completed_urls": []}
             )), patch.object(w.q, "active_workflows", return_value=0), \
             patch.dict("os.environ", {
                 "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
                 "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1"
             }):
            calls = []
            report = w.dispatch({
                "version": 1, "campaign": w.CAMPAIGN,
                "verified": [{
                    "title": "Example Book",
                    "url": "https://freewebnovel.com/novel/example-book",
                    "chapters": 123,
                    "catalogue": "verified_chapter_mapping",
                    "edition_status": "Completed",
                }],
            }, Path(td) / "report.json", runner=lambda args, **kw: calls.append(args))
            self.assertEqual(report["remaining"], 0)
            self.assertEqual(len(calls), 1)
            self.assertIn("confirm_rights=true", calls[0])
            self.assertIn("force=false", calls[0])


if __name__ == "__main__":
    unittest.main()
