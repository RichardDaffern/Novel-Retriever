"""ReadNovelFull bulk campaign source-validation tests (no public network)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import readnovelfull_remaining_bulk as b


class ReadNovelFullCampaignTests(unittest.TestCase):
    def test_exact_matches_not_generic_sidebars(self):
        html="""<a href="/heavenly-star.html">Heavenly Star</a>
        <a href="/godly-student.html">Godly Student</a>
        <a href="/heavenly-star/chapter-2.html">Chapter 2</a>
        <a href="https://other.site/book.html">Heavenly Star</a>"""
        self.assertEqual(b.links(html),[
            ("Heavenly Star","https://readnovelfull.com/heavenly-star.html"),
            ("Godly Student","https://readnovelfull.com/godly-student.html"),
        ])

    def test_all_71_pending_titles_are_separate_from_completed_candidates(self):
        source=json.loads(b.TARGETS.read_text(encoding="utf-8"))["titles"]
        self.assertEqual(len(source),100)
        skip={b.old.canon(x) for x in b.SKIP_NOVELFULL}
        self.assertEqual(len(skip),29)
        self.assertEqual(len([x for x in source if b.old.canon(x) not in skip]),71)

    def test_colon_suffix_match_preserves_title_identity(self):
        self.assertEqual(b.old.similarity(
            "Skirt Chasing Monarch : City Lady Killer", "City Lady Killer"),1)
        self.assertEqual(b.old.similarity("I Can Extract Everything",
                                         "I Can Track Everything"),0)


if __name__=="__main__":
    unittest.main()
