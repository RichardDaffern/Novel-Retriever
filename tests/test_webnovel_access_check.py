"""Offline synthetic tests for read-only, bounded WebNovel access diagnostics."""
import json
import unittest
from unittest.mock import patch

from tools.webnovel_access_check import (
    AccessProbeError, check_public_samples, main,
)

BOOK = "https://www.webnovel.com/book/33422293300201205"
CH1 = BOOK + "/89735050081387238"
CH400 = BOOK + "/94052948610440202"
CH844 = BOOK + "/98111515671985466"
CATALOGUE = (
    "<html><h1>Synthetic Test Novel</h1>"
    "<div>Author: Test Writer 884 Chapters</div></html>"
)


def readable(n):
    return ('<html><nav>Unlock this chapter</nav>'
            '<div class="cha-content">'
            f'<p>A fictional chapter {n} about a morning walk through the misty '
            'harbour, where a traveller discovers an old observatory and meets '
            'some remarkable new friends.</p>'
            '<p>That meeting changes the plans of everybody involved, and their '
            'journey continues with a long conversation through the afternoon.</p>'
            '</div></html>')


class ReadOnlyAccessTests(unittest.TestCase):
    def fake(self, **overrides):
        pages = {BOOK: CATALOGUE, CH1: readable(1), CH400: readable(400),
                 CH844: readable(844)}
        pages.update(overrides)
        called = []

        def fetch(url):
            called.append(url)
            value = pages[url]
            if isinstance(value, Exception):
                raise value
            return value

        return called, fetch

    def test_three_samples_report_counts_without_story_text(self):
        called, fetch = self.fake()
        result = check_public_samples(BOOK, [(1, CH1), (400, CH400), (844, CH844)],
                                      fetcher=fetch)
        self.assertEqual(result["outcome"], "sampled_public_readable")
        self.assertEqual(result["listed_chapters"], 884)
        self.assertEqual([x["chapter"] for x in result["samples"]], [1, 400, 844])
        self.assertEqual(called, [BOOK, CH1, CH400, CH844])
        self.assertNotIn("observatory", json.dumps(result))
        self.assertFalse(result["complete_novel_download_verified"])

    def test_blocked_catalogue_stops_immediately(self):
        called, fetch = self.fake(**{BOOK: AccessProbeError("HTTP_403_access_denied")})
        result = check_public_samples(BOOK, [(1, CH1)], fetcher=fetch)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["reason"], "HTTP_403_access_denied")
        self.assertEqual(called, [BOOK])

    def test_second_sample_blocked_never_fetches_third(self):
        called, fetch = self.fake(**{CH400: AccessProbeError("access_challenge")})
        result = check_public_samples(BOOK, [(1, CH1), (400, CH400), (844, CH844)],
                                      fetcher=fetch)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(len(result["samples"]), 2)
        self.assertEqual(called, [BOOK, CH1, CH400])

    def test_locked_chapter_does_not_report_publicly_readable(self):
        called, fetch = self.fake(**{
            CH1: '<div class="cha-content">Unlock this chapter to continue reading.</div>'
        })
        result = check_public_samples(BOOK, [(1, CH1)], fetcher=fetch)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["samples"][0]["reason"], "locked_chapter")

    def test_incomplete_chapter_fails_closed(self):
        called, fetch = self.fake(**{CH1: "<div class='cha-content'>Too short</div>"})
        result = check_public_samples(BOOK, [(1, CH1)], fetcher=fetch)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["samples"][0]["status"], "unavailable")

    def test_bad_urls_rejected_without_network(self):
        bad = CH1.replace("www.webnovel.com", "webnovel.com.evil.test")
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            with self.assertRaisesRegex(AccessProbeError, "Unsafe chapter URL"):
                check_public_samples(BOOK, [(1, bad)])

    def test_wrong_book_rejected(self):
        with self.assertRaisesRegex(AccessProbeError, "Unsafe chapter URL"):
            check_public_samples(BOOK, [(1, CH1.replace("33422293300201205", "11111111111111111"))])

    def test_duplicate_urls_and_numbers_rejected(self):
        for samples in ([(1, CH1), (1, CH400)], [(1, CH1), (2, CH1)]):
            with self.subTest(samples=samples), self.assertRaisesRegex(AccessProbeError, "Duplicate"):
                check_public_samples(BOOK, samples)

    def test_sample_count_limited(self):
        with self.assertRaisesRegex(AccessProbeError, "1 to 5"):
            check_public_samples(BOOK, [])
        with self.assertRaisesRegex(AccessProbeError, "1 to 5"):
            check_public_samples(BOOK, [(i, BOOK + f"/{i:014d}") for i in range(1, 7)])

    def test_wrong_reported_catalogue_count_fails_without_sample_fetch(self):
        called, fetch = self.fake(**{BOOK: CATALOGUE.replace("884 Chapters", "10 Chapters")})
        result = check_public_samples(BOOK, [(400, CH400)], fetcher=fetch)
        self.assertEqual(result["outcome"], "unverified")
        self.assertEqual(called, [BOOK])

    def test_invalid_metadata_fails_closed(self):
        called, fetch = self.fake(**{BOOK: "<html></html>"})
        result = check_public_samples(BOOK, [(1, CH1)], fetcher=fetch)
        self.assertEqual(result["outcome"], "unverified")
        self.assertEqual(called, [BOOK])

    def test_main_sample_format_error_no_network(self):
        with self.assertRaises(SystemExit):
            main(["--book-url", BOOK, "--sample", "not-a-valid-sample"])


if __name__ == "__main__":
    unittest.main()
