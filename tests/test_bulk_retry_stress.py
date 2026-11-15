"""Retry-only plan tests, including exact range and prior-run safety."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools.library_bulk import main, retry_selection_plan
from tools.bulk_stress import run_stress


NF = "https://novelfull.com/retry-fully.html"
FW = "https://freewebnovel.com/novel/retry-missing"
SH = "https://www.scribblehub.com/series/445037/the-adventurous-gamer-ninja--daichi-hekima/"


def recovery_manifest(*, urls=(NF, FW), chapter_range="1-2"):
    return {
        "version": 1, "run_id": "123456", "selected": 3,
        "recovered": [{"url": "https://novelfull.com/completed.html"}],
        "missing_or_failed": [
            {"url": url, "site": "NovelFull" if "novelfull" in url else
                "FreeWebNovel" if "freewebnovel" in url else "Scribble Hub",
             "title": f"Example {i}", "chapter_range": chapter_range,
             "force": True}
            for i, url in enumerate(urls)
        ],
        "already_available": [],
        "rejected_artifacts": [],
    }


def registry_with_cached(url):
    return {"version": 1, "novels": [{
        "url": url, "title": "Already finished elsewhere",
        "downloads": [{
            "status": "complete", "range": "1-2",
            "expires_at_utc": "2099-12-01T00:00:00Z",
        }],
    }]}


class RetryAndLoadTests(unittest.TestCase):
    def test_only_missing_with_exact_chapter_range_and_never_force(self):
        plan = retry_selection_plan(
            {"version": 1, "novels": []}, {"version": 1, "novels": []},
            recovery_manifest(), expected_run_id="123456",
        )
        self.assertEqual(plan["retry_from_run_id"], "123456")
        self.assertEqual(plan["selected_count"], 2)
        self.assertEqual(plan["range"], "1-2")
        self.assertEqual(plan["groups"]["NovelFull"][0]["novel_url"], NF)
        self.assertEqual(plan["groups"]["FreeWebNovel"][0]["novel_url"], FW)
        self.assertFalse(plan["groups"]["NovelFull"][0]["force"])
        self.assertTrue(all(
            item["chapter_range"] == "1-2"
            for group in plan["groups"].values() for item in group
        ))

    def test_skip_missing_book_if_another_run_already_completed_it(self):
        plan = retry_selection_plan(
            registry_with_cached(NF), {"version": 1, "novels": []},
            recovery_manifest(), expected_run_id="123456",
        )
        self.assertEqual(len(plan["skipped"]), 1)
        self.assertEqual(plan["skipped"][0]["novel_url"], NF)
        self.assertFalse(plan["groups"]["NovelFull"])
        self.assertEqual(plan["groups"]["FreeWebNovel"][0]["novel_url"], FW)

    def test_reject_old_range_less_manifest_or_wrong_run(self):
        invalid = recovery_manifest()
        del invalid["missing_or_failed"][0]["chapter_range"]
        with self.assertRaisesRegex(ValueError, "predates range-aware"):
            retry_selection_plan({"version": 1, "novels": []},
                                 {"version": 1, "novels": []}, invalid)
        with self.assertRaisesRegex(ValueError, "does not match"):
            retry_selection_plan({"version": 1, "novels": []},
                                 {"version": 1, "novels": []},
                                 recovery_manifest(), expected_run_id="444")

    def test_reject_wrong_site_duplicates_and_mixed_ranges(self):
        reg = {"version": 1, "novels": []}
        cat = {"version": 1, "novels": []}
        wrong = recovery_manifest()
        wrong["missing_or_failed"][0]["site"] = "Scribble Hub"
        with self.assertRaisesRegex(ValueError, "site identity"):
            retry_selection_plan(reg, cat, wrong)
        dup = recovery_manifest(urls=(NF, NF))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            retry_selection_plan(reg, cat, dup)
        mixed = recovery_manifest()
        mixed["missing_or_failed"][1]["chapter_range"] = "2-3"
        with self.assertRaisesRegex(ValueError, "different chapter ranges"):
            retry_selection_plan(reg, cat, mixed)

    def test_scribblehub_retry_requires_permission_and_whole_book(self):
        manifest = recovery_manifest(urls=(SH,), chapter_range="")
        with self.assertRaisesRegex(ValueError, "permission"):
            retry_selection_plan({"version": 1, "novels": []},
                                 {"version": 1, "novels": []}, manifest)
        plan = retry_selection_plan(
            {"version": 1, "novels": []}, {"version": 1, "novels": []},
            manifest, confirm_rights=True,
        )
        self.assertEqual(len(plan["groups"]["Scribble Hub"]), 1)
        self.assertEqual(plan["range"], "all")

    def test_no_failed_titles_is_an_actionable_error(self):
        empty = recovery_manifest(urls=())
        with self.assertRaisesRegex(ValueError, "No failed or missing"):
            retry_selection_plan({"version": 1, "novels": []},
                                 {"version": 1, "novels": []}, empty)

    def test_cli_retry_writes_only_failed_matrices(self):
        with TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "prior.json").write_text(json.dumps(recovery_manifest()))
            (path / "registry.json").write_text(json.dumps(registry_with_cached(NF)))
            (path / "catalogue.json").write_text(json.dumps({
                "version": 1, "novels": [],
            }))
            rc = main([
                "plan", "--registry", str(path / "registry.json"),
                "--catalogue", str(path / "catalogue.json"),
                "--retry-manifest", str(path / "prior.json"),
                "--retry-run-id", "123456", "--plan-file", str(path / "plan.json"),
            ])
            self.assertEqual(rc, 0)
            result = json.loads((path / "plan.json").read_text())
            self.assertEqual(len(result["groups"]["FreeWebNovel"]), 1)
            self.assertFalse(result["groups"]["NovelFull"])
            self.assertEqual(len(result["skipped"]), 1)

    def test_synthetic_20_50_100_and_maximum_boundary(self):
        results = run_stress()
        self.assertEqual([r["requested"] for r in results], [20, 50, 100, 257])
        self.assertTrue(all(r["status"] == "passed" for r in results[:3]))
        self.assertEqual(results[-1]["status"], "correctly_rejected")


if __name__ == "__main__":
    unittest.main()
