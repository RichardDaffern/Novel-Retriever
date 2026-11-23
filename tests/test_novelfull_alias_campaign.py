"""Offline safety tests: search-result parsing, subtitle matching, duplicate gates."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import novelfull_alias_campaign as c


class SearchTests(unittest.TestCase):
    def test_subtitle_after_colon_and_spelling_variants(self):
        full="Hidden Marriage Sweet Pampering : The Conglomerate’s Little Wife"
        self.assertIn("The Conglomerate’s Little Wife",c.queries(full))
        self.assertIn("Invincible Leveling King",c.queries("Invincible Levelling King"))

    def test_only_canonical_book_pages_not_chapters_or_sidebar(self):
        html="""<a href="/legend-of-swordsman.html">Legend of Swordsman</a>
        <a href="/legend-of-swordsman/chapter-1.html">Chapter 1</a>
        <a href="https://elsewhere.example/book.html">Legend of Swordsman</a>
        <a href="/martial-peak.html">Martial Peak</a>"""
        self.assertEqual(c.search_links(html),[
            ("Legend of Swordsman","https://novelfull.com/legend-of-swordsman.html"),
            ("Martial Peak","https://novelfull.com/martial-peak.html")])

    def test_fuzzy_is_conservative(self):
        self.assertEqual(c.similarity("Tomb Raider King","Martial Peak"),0)
        self.assertEqual(c.similarity("Apotheosis","Apotheosis Begins with Tai Chi"),0)
        self.assertEqual(c.similarity("Invincible Levelling King","Invincible Leveling King"),1)
        self.assertEqual(c.similarity("City Lady Killer","City Lady Killer"),1)

    def test_verify_real_book_page_title(self):
        getter=lambda url:"<html><h3 class='title'>Legend of Swordsman</h3></html>"
        self.assertEqual(c.verify_title_page("https://novelfull.com/legend-of-swordsman.html",
                         "Legend of Swordsman",getter=getter)[0],True)
        self.assertEqual(c.verify_title_page("https://novelfull.com/legend-of-swordsman.html",
                         "Tomb Raider King",getter=getter)[0],False)

    def test_100_target_uniqueness(self):
        data=json.loads(c.TARGETS.read_text(encoding="utf-8"))
        self.assertEqual(len(data["titles"]),100)
        self.assertEqual(len({c.canon(t) for t in data["titles"]}),100)


if __name__ == "__main__":
    unittest.main()
