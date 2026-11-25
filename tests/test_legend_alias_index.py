"""Offline checks for verified Legend of Swordsman public chapter-index anomalies.

No external requests, source chapter prose, guessed links or global relaxation.
"""
import unittest
from tools.readnovelfull_source import (
    LEGEND_BOOK, LEGEND_REAL_5333, LEGEND_TYPO_5247,
    LEGEND_CANONICAL_5247, SourceError, chapter_index,
    validate_chapter_url,
)

HOST = "https://readnovelfull.com"


def index_for_legend(*, canonical=True, alias=True, stranger=False):
    anchors = []
    for n in range(1, 5334):
        if n == 5247:
            if canonical:
                anchors.append(
                    '<li><a href="{}">Chapter 5247 A Suitable Treasure</a></li>'.format(
                        LEGEND_CANONICAL_5247))
            if alias:
                anchors.append(
                    '<li><a href="{}{}">Chapter Chhapter 5247</a></li>'.format(
                        HOST, LEGEND_TYPO_5247))
            if stranger:
                anchors.append(
                    '<li><a href="/legend-of-swordsman/chapter-5247-unrelated.html">'
                    'Chapter 5247 unrelated</a></li>')
        elif n == 5333:
            anchors.append(
                '<li><a href="{}{}">Home Chapter 5333</a></li>'.format(
                    HOST, LEGEND_REAL_5333))
        else:
            anchors.append(
                '<li><a href="/legend-of-swordsman/chapter-{}.html">'
                'Chapter {}</a></li>'.format(n, n))
    return '<ul class="list-chapter">' + "".join(anchors) + '</ul>'


class LegendSourceAliasesTests(unittest.TestCase):
    def test_accept_only_publisher_verified_home_chapter(self):
        self.assertEqual(validate_chapter_url(HOST + LEGEND_REAL_5333), (
            HOST + LEGEND_REAL_5333, 5333, "legend-of-swordsman"))
        for invalid in [
            HOST + "/legend-of-swordsman/home-chapter-5332.html",
            HOST + "/other/home-chapter-5333.html",
            HOST + LEGEND_REAL_5333 + "?track=1",
        ]:
            with self.subTest(invalid=invalid), self.assertRaises(SourceError):
                validate_chapter_url(invalid)
        with self.assertRaisesRegex(SourceError, "another novel"):
            validate_chapter_url(HOST + LEGEND_REAL_5333, book_prefix="other")

    def test_keep_6492_chapter_semantics_on_synthetic_5333_prefix(self):
        result = chapter_index(index_for_legend(), LEGEND_BOOK)
        self.assertEqual(len(result), 5333)
        self.assertEqual(result[5246]["url"], LEGEND_CANONICAL_5247)
        self.assertEqual(result[5246]["chapter_number"], 5247)
        self.assertEqual(result[5332]["url"], HOST + LEGEND_REAL_5333)
        self.assertEqual(result[5332]["chapter_number"], 5333)
        self.assertEqual([r["position"] for r in result],
                         list(range(1, 5334)))

    def test_refuse_unverified_or_missing_canonical_chapter(self):
        with self.assertRaisesRegex(SourceError, "missing verified canonical"):
            chapter_index(index_for_legend(canonical=False), LEGEND_BOOK)
        with self.assertRaisesRegex(SourceError, "Duplicate Chapter 5247"):
            chapter_index(index_for_legend(stranger=True), LEGEND_BOOK)

    def test_typo_alias_not_ignored_for_any_other_book(self):
        with self.assertRaisesRegex(SourceError, "Invalid ReadNovelFull"):
            chapter_index(
                '<ul class="list-chapter"><li><a href="' + HOST +
                LEGEND_TYPO_5247 + '">Typo</a></li></ul>',
                "https://readnovelfull.com/some-other-book.html")


if __name__ == "__main__":
    unittest.main()
