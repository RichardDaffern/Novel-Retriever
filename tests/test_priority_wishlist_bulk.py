"""Offline regression tests for the priority NF/RNF wishlist campaign."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import priority_wishlist_bulk as w


class PriorityWishlistTests(unittest.TestCase):
    def test_current_manifest_filters_completed_excluded_and_repair_holds(self):
        rows, audit = w.pending_titles()
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), 245)
        self.assertEqual(audit["wishlist_yup"], 163)
        self.assertEqual(audit["wishlist_idk"], 82)
        self.assertNotIn("Past Life Returner", [row["title"] for row in rows])
        self.assertNotIn("Doom Lord", [row["title"] for row in rows]
                         if row["title"] == "A Thought Through Eternity")

    def test_only_two_easier_hosts_and_reviewed_alias_candidate(self):
        urls = w.source_candidates("Apotheosis", {
            "books": [{"title": "Apotheosis", "url":
                       "https://readnovelfull.com/apotheosis-ascension-to-godhood-v1.html"}]})
        self.assertTrue(all("freewebnovel.com" not in url for url in urls))
        self.assertTrue(urls[0].startswith("https://novelfull.com/"))
        self.assertIn("https://readnovelfull.com/apotheosis-ascension-to-godhood-v1.html", urls)

    def test_source_verification_never_claims_invalid_book(self):
        with tempfile.TemporaryDirectory() as td:
            def fake_fetch(url):
                if url == "https://novelfull.com/apotheosis.html":
                    return "<html><h1>Completely Unrelated Book</h1></html>", "ok"
                return None, "HTTP_404"
            with patch.object(w, "pending_titles", return_value=(
                [{"title": "Apotheosis", "tier": "Yup"}],
                {"selected_for_source_search": 1, "completed_urls": []},
            )), patch.object(w.q, "read_json", return_value={"books": []}):
                report = w.discover(Path(td) / "scan.json", fetcher=fake_fetch,
                                    sleeper=lambda _: None,
                                    reader_discover=lambda _: {})
            self.assertEqual(report["verified"], [])
            self.assertEqual(len(report["unresolved"]), 1)

    def test_dispatch_sends_rights_and_avoids_forcing_completed(self):
        calls = []
        with tempfile.TemporaryDirectory() as td:
            src = {"version": 1, "campaign": w.MAIN_CAMPAIGN,
                   "verified": [{"title": "Apotheosis", "tier": "Yup",
                                 "url": "https://novelfull.com/apotheosis.html",
                                 "site": "NovelFull", "source_verified": True}]}
            with patch.object(w, "pending_titles", return_value=(
                [{"title": "Apotheosis", "tier": "Yup"}], {}
            )), patch.object(w.q, "active_workflows", return_value=0), \
                 patch.dict("os.environ", {"GITHUB_REPOSITORY":
                            "RichardDaffern/Novel-Retriever",
                            "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1"}):
                out = w.dispatch(src, Path(td) / "queued.json",
                                 runner=lambda cmd, **kw: calls.append(cmd))
            self.assertEqual(len(out["submitted"]), 1)
            self.assertEqual(out["remaining"], 0)
            self.assertIn("confirm_rights=true", calls[0])
            self.assertIn("force=false", calls[0])
            self.assertNotIn("force=true", calls[0])
            self.assertEqual(out["rights_attestation"], "user_confirmed_in_chat")

    def test_campaign_does_not_allow_unknown_source(self):
        with tempfile.TemporaryDirectory() as td:
            src = {"version": 1, "campaign": w.MAIN_CAMPAIGN,
                   "verified": [{"title": "Apotheosis", "tier": "Yup",
                                 "url": "https://some-other-host.example/book",
                                 "source_verified": True}]}
            with patch.object(w, "pending_titles", return_value=(
                [{"title": "Apotheosis", "tier": "Yup"}], {}
            )), patch.dict("os.environ", {"GITHUB_REPOSITORY":
                            "RichardDaffern/Novel-Retriever"}):
                with self.assertRaises(ValueError):
                    w.dispatch(src, Path(td) / "queued.json")


if __name__ == "__main__":
    unittest.main()
