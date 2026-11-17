"""Offline-only tests for the local WebNovel browser diagnostic.

No test makes a real website request or writes novel prose to disk.
"""
import json
import unittest

from tools.webnovel_local_browser_diagnostic import (
    AccessProbeError, diagnose_in_browser, _safe_reason, _sample,
)
from tests.test_webnovel_browser_probe import FakeChromium

BOOK = "https://www.webnovel.com/book/33422293300201205"
CH1 = BOOK + "/89735050081387238"
CH400 = BOOK + "/94052948610440202"
CH844 = BOOK + "/98111515671985466"
CATALOGUE = (
    "<html><h1>Invented Novel</h1>"
    "<p>Author: Imaginary Author 884 Chapters</p></html>"
)
BODY = (
    '<html><div class="cha-content"><p>'
    "This invented chapter is set near a village library on a rainy morning. "
    "Several friends investigate a mysterious letter and talk for hours before "
    "deciding to begin a long journey together. Nobody knows what awaits them."
    '</p></div></html>'
)


class LocalBrowserCheckTests(unittest.TestCase):
    def make_browser(self, **changes):
        pages = {BOOK: CATALOGUE, CH1: BODY, CH400: BODY, CH844: BODY}
        pages.update(changes)
        return FakeChromium(pages)

    def test_three_samples_no_prose_in_report_and_no_exports(self):
        chromium = self.make_browser()
        result = diagnose_in_browser(
            BOOK, [(1, CH1), (400, CH400), (844, CH844)], chromium=chromium
        )
        self.assertEqual(result["outcome"], "sampled_public_readable")
        self.assertEqual(result["listed_chapters"], 884)
        self.assertEqual(result["title"], "Invented Novel")
        self.assertEqual(result["author"], "Imaginary Author")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK, CH1, CH400, CH844])
        self.assertFalse(chromium.launch_args["headless"])
        self.assertFalse(result["complete_novel_download_verified"])
        self.assertFalse(result["chapter_text_saved"])
        self.assertFalse(result["archive_permission_verified"])
        self.assertNotIn("mysterious letter", json.dumps(result))
        self.assertTrue(chromium.browser.context.closed)
        self.assertTrue(chromium.browser.closed)

    def test_blocked_book_page_stops_without_chapter_requests(self):
        chromium = self.make_browser(**{BOOK: ("<html>Access denied</html>", 403, None)})
        result = diagnose_in_browser(BOOK, [(1, CH1)], chromium=chromium)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["reason"], "http_403_access_denied")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK])
        self.assertTrue(chromium.browser.closed)

    def test_header_challenge_stops(self):
        chromium = self.make_browser(**{
            BOOK: (CATALOGUE, 200, None, {"cf-mitigated": "challenge"})
        })
        result = diagnose_in_browser(BOOK, [(1, CH1)], chromium=chromium)
        self.assertEqual(result["reason"], "browser_access_challenge")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK])

    def test_chapter_denial_aborts_subsequent_requests(self):
        chromium = self.make_browser(**{CH400: ("<html>Forbidden</html>", 403, None)})
        result = diagnose_in_browser(
            BOOK, [(1, CH1), (400, CH400), (844, CH844)], chromium=chromium
        )
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["samples"][-1]["reason"], "http_403_access_denied")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK, CH1, CH400])

    def test_locked_chapter_never_passes(self):
        chromium = self.make_browser(**{
            CH1: '<html><div class="cha-content">Unlock this chapter to read it.</div></html>'
        })
        result = diagnose_in_browser(BOOK, [(1, CH1)], chromium=chromium)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["samples"][0]["reason"], "locked_chapter")

    def test_short_chapter_is_unverified(self):
        chromium = self.make_browser(**{
            CH1: '<html><div class="cha-content"><p>Short</p></div></html>'
        })
        result = diagnose_in_browser(BOOK, [(1, CH1)], chromium=chromium)
        self.assertEqual(result["outcome"], "blocked")
        self.assertEqual(result["samples"][0]["status"], "unavailable")

    def test_unknown_catalogue_layout_stops_before_chapters(self):
        chromium = self.make_browser(**{BOOK: "<html><p>No heading present.</p></html>"})
        result = diagnose_in_browser(BOOK, [(1, CH1)], chromium=chromium)
        self.assertEqual(result["reason"], "public_book_metadata_unrecognised")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK])

    def test_wrong_book_url_is_rejected_prelaunch(self):
        chromium = self.make_browser()
        bad = CH1.replace("33422293300201205", "33333333333333333")
        with self.assertRaisesRegex(AccessProbeError, "Unsafe chapter URL"):
            diagnose_in_browser(BOOK, [(1, bad)], chromium=chromium)
        self.assertIsNone(chromium.launch_args)

    def test_too_many_samples_is_rejected_prelaunch(self):
        chromium = self.make_browser()
        with self.assertRaisesRegex(AccessProbeError, "up to three"):
            diagnose_in_browser(BOOK, [(1, CH1), (2, CH400),
                                       (3, CH844), (4, CH1)], chromium=chromium)
        self.assertIsNone(chromium.launch_args)

    def test_duplicate_samples_rejected_prelaunch(self):
        chromium = self.make_browser()
        with self.assertRaisesRegex(AccessProbeError, "Duplicate"):
            diagnose_in_browser(BOOK, [(1, CH1), (2, CH1)], chromium=chromium)
        self.assertIsNone(chromium.launch_args)

    def test_out_of_range_chapter_no_chapter_request(self):
        chromium = self.make_browser(**{BOOK: CATALOGUE.replace("884 Chapters", "10 Chapters")})
        result = diagnose_in_browser(BOOK, [(400, CH400)], chromium=chromium)
        self.assertEqual(result["outcome"], "unverified")
        self.assertEqual(result["reason"], "sample_beyond_listed_chapters")
        self.assertEqual(chromium.browser.context.page.visited, [BOOK])

    def test_safe_error_never_emits_page_text(self):
        self.assertEqual(_safe_reason(ValueError("A private novel secret excerpt")),
                         "chapter_body_unavailable_or_unrecognised")

    def test_malformed_sample_rejected(self):
        with self.assertRaises(Exception):
            _sample("wrong_sample")


if __name__ == "__main__":
    unittest.main()
