"""Offline, synthetic regression suite for the overnight source-check queue."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import overnight_queue as q


class OvernightQueueTests(unittest.TestCase):
    def test_all_82_idk_and_90_exclusions_are_preserved(self):
        yup, idk, denied, known = q.manifests()
        self.assertEqual(len(denied), 90)
        self.assertEqual(len(q.read_json(q.IDK)["entries"]), 82)
        self.assertEqual(len(q.read_json(q.YUP)["entries"]), 163)
        self.assertEqual(len([x for x in q.read_json(q.YUP)["entries"]
                              if x["state"] == "needs_source_verification"]), 157)
        self.assertNotIn(q.norm("The First Order"), {q.norm(x) for x in yup + idk})
        self.assertNotIn(q.norm("Devil’s Son-in-Law"), {q.norm(x) for x in yup + idk})
        self.assertNotIn(q.norm("Fantasy Simulator"), {q.norm(x) for x in yup + idk})
        self.assertNotIn(q.norm("A Thought Through Eternity"),
                         {q.norm(x) for x in idk})  # A Will Eternal already queued
        self.assertTrue(all(q.norm(x) not in denied for x in yup + idk))
        self.assertLessEqual(len(idk), 82)
        self.assertLessEqual(len(yup), 157)

    def test_dispatch_script_imports_without_third_party_source_parser(self):
        # The discovery job installs bs4, but the separate dispatcher does
        # not. Keep this import safe on a clean Python stdlib-only runner.
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-S", "-c", "import tools.overnight_queue"],
            cwd=q.ROOT, capture_output=True, text=True,
            timeout=20, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_generated_candidates_never_count_as_verified(self):
        self.assertEqual(q.candidate_urls("The Great Storyteller"), [
            "https://novelfull.com/the-great-storyteller.html",
            "https://freewebnovel.com/novel/the-great-storyteller",
        ])
        self.assertFalse(q.matches_public_book_page(
            "The Great Storyteller",
            "<html><title>Just a moment...</title><h1>The Great Storyteller</h1></html>"
        ))
        self.assertFalse(q.matches_public_book_page(
            "The Great Storyteller", "<h1>Not Found</h1>"
        ))
        self.assertFalse(q.matches_public_book_page(
            "The Great Storyteller", "<h1>The Great Storyteller II</h1>"
        ))
        self.assertTrue(q.matches_public_book_page(
            "The Great Storyteller", "<h1>The Great Storyteller</h1>"
        ))

    def test_discovery_prefers_verified_novelfull_without_fallback_request(self):
        title = "Preferred Novel"
        calls = []

        def fetch(url):
            calls.append(url)
            return "<h1>Preferred Novel</h1>", "ok"

        with patch.object(q, "manifests", return_value=(
            [title], [], set(), set()
        )):
            result = q.discover(fetcher=fetch, sleeper=lambda _: None)
        self.assertEqual(calls, [q.candidate_urls(title)[0]])
        self.assertEqual(result["verified"][0]["url"], q.candidate_urls(title)[0])

    def test_discovery_prioritises_yup_and_respects_host_denials(self):
        calls = []
        def fetch(url):
            calls.append(url)
            if url == q.candidate_urls("First Yup")[0]:
                return None, "HTTP_403"
            if "freewebnovel.com" in url and "first-yup" in url:
                return "<h1>First Yup</h1>", "ok"
            if "freewebnovel.com" in url and "Only Idk" in url.replace("-", " "):
                raise AssertionError("Unexpected URL")
            if "freewebnovel.com" in url and "only-idk" in url:
                return "<h1>Only Idk</h1>", "ok"
            return "<h1>Different book</h1>", "ok"
        with patch.object(q, "manifests", return_value=(
            ["First Yup", "Second Yup"], ["Only Idk"],
            {q.norm("Forbidden Book")}, set()
        )):
            result = q.discover(fetcher=fetch, sleeper=lambda _: None)
        self.assertEqual([x["title"] for x in result["verified"]],
                         ["First Yup", "Only Idk"])
        self.assertEqual(result["summary"]["eligible_yup"], 2)
        self.assertEqual(result["summary"]["eligible_idk"], 1)
        self.assertEqual(result["summary"]["source_hosts_blocked"],
                         ["novelfull.com"])
        self.assertEqual(result["summary"]["public_book_requests"], 4)
        self.assertTrue(all("novelfull.com" not in url for url in calls[2:]))

    def test_discovery_never_uses_unsupported_or_locked_html(self):
        with patch.object(q, "manifests", return_value=(
            ["A Safe Title"], [], set(), set()
        )):
            result = q.discover(
                fetcher=lambda url: (
                    "<title>Just a moment...</title><h1>A Safe Title</h1>", "ok"
                ),
                sleeper=lambda _: None
            )
        self.assertEqual(result["verified"], [])
        self.assertEqual(result["summary"]["unresolved"], 1)

    def test_dispatch_exact_allowlist_no_force_and_limited_batches(self):
        synthetic = {
            "version": 1, "campaign": q.CAMPAIGN,
            "verified": [
                {"title": title, "url": q.candidate_urls(title)[0],
                 "tier": "Yup", "evidence": "public_listing_exact_title"}
                for title in ("A Novel", "B Novel", "C Novel")
            ]
        }
        commands, sleeps = [], []
        def runner(cmd, **kwargs):
            commands.append(cmd)
            if cmd[:2] == ["gh", "api"]:
                return SimpleNamespace(stdout=json.dumps({"workflow_runs": []}))
            return SimpleNamespace(stdout="")
        with patch.object(q, "manifests", return_value=(
            ["A Novel", "B Novel", "C Novel"], [],
            {q.norm("The First Order")}, set()
        )), patch.dict(os.environ, {"GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever"}):
            result = q.dispatch(
                synthetic, "Yup", runner=runner,
                sleeper=sleeps.append, clock=lambda: 1.0
            )
        workflow_commands = [cmd for cmd in commands
                             if cmd[:3] == ["gh", "workflow", "run"]]
        self.assertEqual(len(workflow_commands), 2)
        self.assertEqual([len(x["titles"]) for x in result["submitted"]], [2, 1])
        self.assertEqual(result["held"], [])
        self.assertTrue(all("force=false" in cmd for cmd in workflow_commands))
        self.assertTrue(all("chapter_range=" in cmd for cmd in workflow_commands))
        self.assertEqual(sleeps, [q.RUN_DELAY])

    def test_dispatch_rejects_unverified_urls_and_red_titles(self):
        badcases = [
            ("The First Order", q.candidate_urls("The First Order")[0]),
            ("Safe Book", "https://novelfull.com/other-book.html"),
            ("Unknown", q.candidate_urls("Unknown")[0]),
        ]
        with patch.object(q, "manifests", return_value=(
            ["Safe Book", "The First Order"], [],
            {q.norm("The First Order")}, set()
        )):
            for title, url in badcases:
                with self.subTest(title=title), self.assertRaises(q.QueueError):
                    q.dispatch({"version": 1, "campaign": q.CAMPAIGN,
                                "verified": [{
                                    "title": title, "url": url, "tier": "Yup",
                                    "evidence": "public_listing_exact_title"
                                }]}, "Yup", clock=lambda: 1)

    def test_rerun_does_not_create_duplicate_downloads(self):
        with patch.object(q, "manifests", return_value=(
            ["A Novel"], [], set(), set()
        )), patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "2"}):
            result = q.dispatch(
                {"version": 1, "campaign": q.CAMPAIGN,
                 "verified": [{
                     "title": "A Novel",
                     "url": q.candidate_urls("A Novel")[0],
                     "tier": "Yup", "evidence": "public_listing_exact_title"
                 }]}, "Yup", runner=lambda *args, **kwargs:
                    (_ for _ in ()).throw(AssertionError("Should not run"))
            )
        self.assertEqual(result["submitted"], [])
        self.assertEqual(len(result["held"]), 1)

    def test_strict_file_schemas_and_page_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "book.json"
            p.write_text(json.dumps({"a": 1}), encoding="utf-8")
            self.assertEqual(q.read_json(p), {"a": 1})
            with self.assertRaises(q.QueueError):
                q._unique_titles(["Same Novel", "Same-novel"])
        self.assertEqual(q.page_titles("<h1>Actual Name</h1>"), ["Actual Name"])


if __name__ == "__main__":
    unittest.main()
