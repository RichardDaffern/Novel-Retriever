"""Curated bulk URLs: no auto-discovery, precise ownership, exclusions and dedupe."""
import os
from unittest.mock import patch
import unittest

from tools import dispatch_curated_bulk as d


def manifest():
    return {
        "schema_version": 1, "campaign": d.CAMPAIGN,
        "method": "operator-reviewed-book-pages-no-runtime-website-search",
        "priority": list(d.SOURCE_PRIORITY),
        "max_parallel_bulk_runs": 2,
        "books": [
            {"title": "Path to Heaven", "source_title": "Path to Heaven",
             "site": "ReadNovelFull",
             "url": "https://readnovelfull.com/path-to-heaven-v1.html",
             "evidence": "Verified real book page and author"},
            {"title": "Invincible Dragon Emperor",
             "source_title": "The Invincible Dragon Emperor",
             "site": "NovelFull",
             "url": "https://novelfull.com/the-invincible-dragon-emperor.html",
             "evidence": "Verified real book page and author"},
        ],
    }


def plan(manifest_data=None, existing=None, exclude=None):
    return d.prepare_queue(
        manifest_data or manifest(),
        registry={"novels": existing or []},
        yup={"entries": [{"title": "Path to Heaven"},
                         {"title": "Invincible Dragon Emperor"}] +
             [{"title": f"Other Book {n}"} for n in range(161)]},
        verified={"entries": []}, idk={"entries": []},
        denied={"excluded": exclude or [f"Dropped {n}" for n in range(90)]},
        known_failures={"titles": [f"Known issue {n}" for n in range(14)]})


class CuratedMultiSourceTests(unittest.TestCase):
    def test_no_discovery_and_prefers_novelfull_then_rnf(self):
        selected = plan()
        self.assertEqual(selected["reviewed"], 2)
        self.assertEqual(selected["unverified_sites_searched"], 0)
        self.assertEqual([x["site"] for x in selected["eligible"]],
                         ["NovelFull", "ReadNovelFull"])

    def test_deduplicates_by_source_or_title_and_drops_completed(self):
        existing = [{"url": "https://novelfull.com/the-invincible-dragon-emperor.html",
                     "title": "The Invincible Dragon Emperor",
                     "downloads": [{"status": "complete", "range": "all"}]}]
        x = plan(existing=existing)
        self.assertEqual([i["title"] for i in x["eligible"]], ["Path to Heaven"])
        self.assertEqual(len(x["already_complete"]), 1)
        for mutate in [
            lambda m: m["books"].append(dict(m["books"][0])),
            lambda m: m["books"][0].update(
                {"url": "https://readnovelfull.com.other.test/path-to-heaven-v1.html"}),
            lambda m: m["books"][0].update({"site": "NovelFull"}),
            lambda m: m["books"][0].update(
                {"url": "https://readnovelfull.com/path-to-heaven-v1.html?chapter=1"}),
            lambda m: m["books"][0].update({"title": "Not on approved lists"}),
        ]:
            m = manifest()
            mutate(m)
            with self.assertRaises(ValueError):
                plan(m)

    def test_never_enqueues_red_titles(self):
        m = manifest()
        with self.assertRaises(ValueError):
            plan(m, exclude=["Path to Heaven"] + [f"Dropped {n}" for n in range(89)])

    def test_direct_bulk_links_with_force_false_and_no_search(self):
        selected = plan()
        commands = []
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
            "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1"
        }), patch.object(d.q, "active_workflows", return_value=0):
            result = d.dispatch_queue(selected, runner=lambda cmd, **kwargs:
                                      commands.append(cmd))
        self.assertTrue(result["dispatched"])
        self.assertEqual(result["searches_performed_by_dispatcher"], 0)
        self.assertEqual(len(commands), 1)
        self.assertIn("force=false", commands[0])
        self.assertTrue(any(x.startswith("novel_urls=") and
                            "novelfull.com" in x and "readnovelfull.com" in x
                            for x in commands[0]))

    def test_waits_when_two_bulk_runs_active_and_refuses_reruns(self):
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
            "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "2"
        }), self.assertRaises(ValueError):
            d.dispatch_queue(plan(), runner=lambda *a, **k: None)
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "RichardDaffern/Novel-Retriever",
            "GITHUB_ACTIONS": "true", "GITHUB_RUN_ATTEMPT": "1"
        }), patch.object(d.q, "active_workflows", return_value=2), self.assertRaises(TimeoutError):
            d.dispatch_queue(plan(), runner=lambda *a, **k: None,
                             wait_seconds=0)


if __name__ == "__main__":
    unittest.main()
