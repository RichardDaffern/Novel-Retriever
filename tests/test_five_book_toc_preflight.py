"""Offline, synthetic checks of the five-book source-only index preflight."""
from __future__ import annotations

import unittest

from tools.five_book_toc_preflight import review
from tools.readnovelfull_source import SourceError

BOOKS = [
    {"title": "Book %s" % n, "tier": "Yup" if n < 4 else "Idk",
     "url": "https://readnovelfull.com/book-%s.html" % n}
    for n in range(1, 6)
]


class FiveBookPreflightTests(unittest.TestCase):
    def test_all_five_indexes_pass_without_reading_chapters(self):
        seen = []
        def index(url):
            seen.append(url)
            return {"title": "Book " + url.split("-")[-1].split(".")[0],
                    "author": "Synthetic Author", "numChapters": 101}
        result = review(BOOKS, discoverer=index, sleeper=lambda _: None)
        self.assertEqual(result["checked"], 5)
        self.assertEqual(result["index_passed"], 5)
        self.assertEqual(result["title_confirmed"], 5)
        self.assertEqual(result["full_chapter_downloads"], 0)
        self.assertFalse(result["rights_verified"])
        self.assertEqual(len(seen), 5)

    def test_one_bad_book_is_held_and_later_books_checked(self):
        def index(url):
            if "book-3.html" in url:
                raise SourceError("Archive contains duplicate chapter link")
            return {"title": "Book " + url.split("-")[-1].split(".")[0],
                    "author": "Synthetic Author", "numChapters": 5}
        result = review(BOOKS, discoverer=index, sleeper=lambda _: None)
        self.assertEqual(result["index_passed"], 4)
        self.assertEqual(result["results"][2]["state"], "index_failed")
        self.assertEqual(result["results"][4]["state"], "index_passed_title_match")

    def test_matching_book_url_wrong_title_holds_identity(self):
        result = review(BOOKS, discoverer=lambda url: {
            "title": "Different Book", "numChapters": 42,
        }, sleeper=lambda _: None)
        self.assertEqual(result["title_confirmed"], 0)
        self.assertTrue(all(x["state"] == "identity_requires_review"
                            for x in result["results"]))

    def test_duplicate_urls_and_unsupported_host_fail_closed(self):
        duplicated = [dict(row) for row in BOOKS]
        duplicated[1]["url"] = duplicated[0]["url"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            review(duplicated, discoverer=lambda url: {}, sleeper=lambda _: None)
        bad = [dict(row) for row in BOOKS]
        bad[0]["url"] = "https://example.com/book.html"
        with self.assertRaises(SourceError):
            review(bad, discoverer=lambda url: {}, sleeper=lambda _: None)


if __name__ == "__main__":
    unittest.main()
