"""Offline tests for the reviewed single-run Yup bulk download."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import dispatch_verified_yup_wave as tool


def sample():
    return {
        "version": 1, "campaign": tool.CAMPAIGN, "one_time": True,
        "source_reviewed_at": "2026-11-20",
        "books": [
            {"title": "Dungeon Defence", "source_title": "Dungeon Defense",
             "url": "https://novelfull.com/dungeon-defense.html",
             "basis": "Reviewed alternative spelling"},
            {"title": "Soul Land", "source_title": "Douluo Dalu",
             "url": "https://novelfull.com/douluo-dalu.html",
             "basis": "Explicit alias on source page"},
        ],
    }


def plan(doc=None, novels=None, excluded=None, blocked=None):
    doc = doc or sample()
    return tool.prepare(
        manifest=doc, registry={"novels": novels or []},
        backlog={"entries": [
            {"title": "Dungeon Defence", "state": "needs_source_verification"},
            {"title": "Soul Land", "state": "needs_source_verification"}
        ] + [{"title": f"Other {n}", "state": "needs_source_verification"}
             for n in range(161)]},
        verified={"entries": [{"title": "I Shall Seal The Heavens",
                               "url": "https://novelfull.com/i-shall-seal-the-heavens.html"}]},
        denied={"excluded": (excluded or ["Disallowed"] +
                              [f"Red {n}" for n in range(89)])},
        blocked={"titles": (blocked or ["Known Failure"] +
                            [f"Failure {n}" for n in range(13)])}
    )


class CuratedWaveTests(unittest.TestCase):
    def test_selects_reviewed_alternative_names_and_skips_completed(self):
        selected = plan()
        self.assertEqual(len(selected["selected"]), 2)
        after = plan(novels=[{
            "title": "Douluo Dalu", "url": "https://novelfull.com/douluo-dalu.html",
            "downloads": [{"status": "complete", "range": "all"}]
        }])
        self.assertEqual([r["title"] for r in after["selected"]],
                         ["Dungeon Defence"])
        self.assertEqual(len(after["skipped"]), 1)

    def test_refuses_unreviewed_or_duplicate_or_dropped(self):
        cases = [
            lambda d: d["books"][0].update(
                {"url": "https://novelfull.com.evil.test/dungeon-defense.html"}),
            lambda d: d["books"][1].update(
                {"url": "https://novelfull.com/dungeon-defense.html"}),
            lambda d: d["books"][0].update(
                {"title": "Something Unapproved"}),
            lambda d: d["books"][0].update(
                {"title": "Disallowed"}),
        ]
        for edit in cases:
            data = sample()
            edit(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                plan(doc=data)

    def test_dispatch_sends_seven_book_capable_unforced_workflow(self):
        urls = [{"title": f"Novel {n}", "url":
                f"https://novelfull.com/novel-{n}.html"} for n in range(7)]
        commands = []
        with patch.dict(os.environ, {"GITHUB_REPOSITORY":
                                    "RichardDaffern/Novel-Retriever",
                                    "GITHUB_ACTIONS": "true",
                                    "GITHUB_RUN_ATTEMPT": "1"}), patch.object(
                                    tool.q, "active_workflows", return_value=0):
            result = tool.dispatch(
                {"selected": urls, "skipped": []},
                runner=lambda cmd, **kwargs: commands.append(cmd))
        self.assertTrue(result["dispatched"])
        self.assertEqual(result["book_count"], 7)
        self.assertEqual(len(commands), 1)
        self.assertIn("force=false", commands[0])
        self.assertIn("chapter_range=", commands[0])

    def test_refuses_action_reruns_and_dangerous_concurrency(self):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY":
                                    "RichardDaffern/Novel-Retriever",
                                    "GITHUB_ACTIONS": "true",
                                    "GITHUB_RUN_ATTEMPT": "2"}), self.assertRaises(ValueError):
            tool.dispatch({"selected": [], "skipped": []})


if __name__ == "__main__":
    unittest.main()
