"""Offline guards for FreeWebNovel real public-search bulk campaign."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import fwn_search_verified_bulk as f


class FreeWebNovelSearchTests(unittest.TestCase):
    def test_search_only_book_pages_not_chapters_or_unrelated_hosts(self):
        html='''<a href="/novel/beauty-and-the-bodyguard">Beauty and the Bodyguard</a>
        <a href="/novel/beauty-and-the-bodyguard/chapter-11506">Full 11,506 Chapters</a>
        <a href="/novel/the-first-infinite-weapon-master">The First Infinite Weapon Master</a>
        <a href="https://other-host.example/novel/beauty-and-the-bodyguard">Beauty and the Bodyguard</a>'''
        self.assertEqual(f.book_links(html), [
            ("Beauty and the Bodyguard", "https://freewebnovel.com/novel/beauty-and-the-bodyguard"),
            ("The First Infinite Weapon Master", "https://freewebnovel.com/novel/the-first-infinite-weapon-master"),
        ])

    def test_strict_title_matching_and_colon_suffix(self):
        self.assertEqual(f.score("Skirt Chasing Monarch: City Lady Killer","City Lady Killer"),1.0)
        self.assertEqual(f.score("Weapon Master","The First Infinite Weapon Master"),0)
        self.assertEqual(f.score("Apotheosis","Apotheosis Begins with Tai Chi"),0)
        self.assertEqual(f.score("I Can Extract Everything","I Can Track Everything"),0)
        self.assertIn("The Conglomerate’s Little Wife",
                      f.queries("Hidden Marriage Sweet Pampering: The Conglomerate’s Little Wife"))

    def test_canonical_wishlist_targets_unmodified(self):
        data=json.loads(f.TARGETS.read_text(encoding="utf-8"))["titles"]
        self.assertEqual(len(data),100)
        self.assertEqual(len({f.q.norm(t) for t in data}),100)

    def test_dispatch_requires_explicit_authorisation_and_nonexcluded_book(self):
        example={"title":"Beauty And The Bodyguard",
                 "url":"https://freewebnovel.com/novel/beauty-and-the-bodyguard",
                 "chapters":11506,"status":"Ongoing"}
        def doc(path):
            if path==f.q.REGISTRY:return {"novels":[]}
            if path==f.q.DENY:return {"excluded":[]}
            raise AssertionError(str(path))
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(f.q,"read_json",side_effect=doc), \
             patch.object(f.q,"active_workflows",return_value=0), \
             patch.dict("os.environ",{
                 "GITHUB_ACTIONS":"true",
                 "GITHUB_REPOSITORY":"RichardDaffern/Novel-Retriever",
                 "GITHUB_RUN_ATTEMPT":"1",
             }):
            commands=[]
            report=f.dispatch({"version":1,"campaign":f.CAMPAIGN,
                               "verified":[example]},Path(temp)/"queue.json",
                              runner=lambda cmd,**kwargs:commands.append(cmd))
            self.assertEqual(report["remaining"],0)
            self.assertEqual(len(commands),1)
            self.assertIn("force=false",commands[0])
            self.assertIn("confirm_rights=true",commands[0])
            self.assertIn("novel_urls="+example["url"],commands[0])

    def test_dispatch_refuses_red_exclusions_and_duplicate_urls(self):
        example={"title":"Beauty And The Bodyguard",
                 "url":"https://freewebnovel.com/novel/beauty-and-the-bodyguard",
                 "chapters":11506,"status":"Ongoing"}
        def doc(path):
            if path==f.q.REGISTRY:return {"novels":[]}
            if path==f.q.DENY:return {"excluded":["Beauty And The Bodyguard"]}
            raise AssertionError(str(path))
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(f.q,"read_json",side_effect=doc), \
             patch.dict("os.environ",{
                 "GITHUB_ACTIONS":"true",
                 "GITHUB_REPOSITORY":"RichardDaffern/Novel-Retriever",
                 "GITHUB_RUN_ATTEMPT":"1",
             }):
            with self.assertRaises(ValueError):
                f.dispatch({"version":1,"campaign":f.CAMPAIGN,
                            "verified":[example]},Path(temp)/"queue.json")
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(f.q,"read_json",side_effect=lambda path:
                 {"novels":[{"url":example["url"],
                              "downloads":[{"status":"complete","range":"all"}]}]}
                 if path==f.q.REGISTRY else {"excluded":[]}), \
             patch.dict("os.environ",{
                 "GITHUB_ACTIONS":"true",
                 "GITHUB_REPOSITORY":"RichardDaffern/Novel-Retriever",
                 "GITHUB_RUN_ATTEMPT":"1",
             }):
            with self.assertRaises(ValueError):
                f.dispatch({"version":1,"campaign":f.CAMPAIGN,
                            "verified":[example]},Path(temp)/"queue.json")


if __name__=="__main__":
    unittest.main()
