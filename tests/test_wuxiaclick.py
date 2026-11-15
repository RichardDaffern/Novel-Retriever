"""Synthetic WuxiaClick index, EPUB, checkpoint and bulk routing tests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from novel_downloader import epub_chapters
from tools.library_bulk import selection_plan
from tools.download_registry import website_name
from tools.wuxiaclick_source import SourceError, discover, extract_chapter, validate_book_url
from tools.wuxiaclick_downloader import DownloadError, download_range
from tools.wuxiaclick_chunks import plan_download

URL = "https://wuxia.click/novel/test-sun"
WORDS = ("A traveller reached the forest after sunrise. "
         "The merchant had brought tales from the ancient ruins. ") * 8
EMPTY = {"version": 1, "novels": []}


def book(rows, total=2, pages=True):
    links = "".join(
        f'<li><a href="/chapter/test-sun-{n}">Chapter {n} , {title} Nov 18, 2021</a></li>'
        for n, title in rows)
    nav = "".join(
        f'<a href="/novel/test-sun?page={n}#chapters">Page {n}</a>'
        for n in range(2, (total + 99) // 100 + 1)) if pages else ""
    return ('<html><title>Test Sun</title><h1>Test Sun</h1><p>by Test Author</p>'
            '<h2>Synopsis</h2><p>An invented synopsis.</p>'
            f'<section id="chapters"><h2>Chapters {total}</h2>'
            f'<p>{total} chapters, numbered 1–{total+1}</p>'
            f'<ol>{links}</ol>{nav}</section></html>')


def chapter(heading, words=WORDS):
    return f'<html><h1>{heading}</h1><div id="chapter-content"><p>{words}</p></div></html>'


class SourceTests(unittest.TestCase):
    def test_strict_urls(self):
        self.assertEqual(validate_book_url(URL), URL)
        for bad in ("http://wuxia.click/novel/test-sun",
                    URL + "?page=2", URL + "#chapters",
                    "https://wuxia.click.evil.test/novel/test-sun",
                    "https://wuxia.click/chapter/test-sun-1"):
            with self.subTest(bad=bad), self.assertRaises(SourceError):
                validate_book_url(bad)

    def test_paginated_index_and_number_discrepancy(self):
        rows = [(n if n < 3 else n + 1, f"Title {n}") for n in range(1, 102)]
        pages = {URL: book(rows[:100], 101),
                 URL+"?page=2": book(rows[100:], 101)}
        details = discover(URL, fetcher=pages.__getitem__, sleeper=lambda _: None)
        self.assertEqual(details["numChapters"], 101)
        self.assertEqual(details["author"], "Test Author")
        self.assertEqual(details["chapters"][2]["source_number"], 4)
        self.assertEqual(details["chapters"][-1]["position"], 101)
        with self.assertRaisesRegex(SourceError, "pagination"):
            discover(URL, fetcher=lambda _: book(rows[:100], 101, False),
                     sleeper=lambda _: None)
        pages[URL+"?page=2"] = book([(100, "Duplicate")], 101)
        with self.assertRaises(SourceError):
            discover(URL, fetcher=pages.__getitem__, sleeper=lambda _: None)

    def test_readable_chapter_validation(self):
        self.assertTrue(len(extract_chapter(chapter("Chapter 0 - Magic Cube"),
                      source_number=1, title="Chapter 0 - Magic Cube")["text"]) > 300)
        with self.assertRaisesRegex(SourceError, "identity"):
            extract_chapter(chapter("Wrong Book"), source_number=1, title="Chapter 0")
        with self.assertRaisesRegex(SourceError, "only"):
            extract_chapter(chapter("Chapter 0", "short"),
                            source_number=1, title="Chapter 0")
        with self.assertRaisesRegex(SourceError, "Locked"):
            extract_chapter(chapter("Chapter 0", "unlock this chapter " + WORDS),
                            source_number=1, title="Chapter 0")

    def test_epub_checkpoint_and_limits(self):
        rows = [(1, "Chapter 0 - Magic Cube"), (2, "Chapter 1 - Lin Ming")]
        fixtures = {URL: book(rows)}
        for n, title in rows:
            fixtures[f"https://wuxia.click/chapter/test-sun-{n}"] = chapter(title)
        with TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(DownloadError, "confirm-rights"):
                download_range(URL, 1, 2, root, fetcher=fixtures.__getitem__,
                               sleeper=lambda _: None)
            def fails(url):
                if url.endswith("-2"): raise SourceError("sample failure")
                return fixtures[url]
            with self.assertRaisesRegex(SourceError, "sample failure"):
                download_range(URL, 1, 2, root, confirm_rights=True,
                               fetcher=fails, sleeper=lambda _: None)
            checkpoint = next(root.rglob(".progress.json"))
            self.assertEqual(len(json.loads(checkpoint.read_text())["chapters"]), 1)
            done = download_range(URL, 1, 2, root, confirm_rights=True,
                                  fetcher=fixtures.__getitem__, sleeper=lambda _: None)
            novel = Path(done["output_dir"])
            self.assertFalse(checkpoint.exists())
            self.assertEqual(len(epub_chapters(novel/"source.epub")[1]), 2)
            with self.assertRaisesRegex(DownloadError, "20"):
                download_range(URL, 1, 21, root, confirm_rights=True,
                               fetcher=fixtures.__getitem__, sleeper=lambda _: None)

    def test_bulk_mixed_urls_and_limit(self):
        self.assertEqual(website_name(URL), "WuxiaClick")
        with TemporaryDirectory() as folder:
            output = Path(folder)/"plan.json"
            discovery = lambda _: {"title": "Test Sun", "numChapters": 101}
            with self.assertRaisesRegex(ValueError, "whole-book"):
                plan_download(URL, "", 20, output, discoverer=discovery)
            with self.assertRaisesRegex(ValueError, "at most 20"):
                plan_download(URL, "1-21", 20, output, discoverer=discovery)
            plan = plan_download(URL, "21-40", 20, output, discoverer=discovery)
            self.assertEqual(plan["parallelism"], 1)
            self.assertEqual(len(plan["pieces"]), 1)
        with self.assertRaisesRegex(ValueError, "permission"):
            selection_plan(EMPTY, EMPTY, "", URL, chapter_range="1-2")
        with self.assertRaisesRegex(ValueError, "explicit inclusive"):
            selection_plan(EMPTY, EMPTY, "", URL, confirm_rights=True)
        mixed = ("https://novelfull.com/the-world-online.html "
                 "https://freewebnovel.com/novel/the-first-order " + URL)
        result = selection_plan(EMPTY, EMPTY, "", mixed, chapter_range="1-2",
                                confirm_rights=True)
        self.assertEqual(result["selected_count"], 3)
        self.assertEqual(len(result["groups"]["WuxiaClick"]), 1)
        with self.assertRaisesRegex(ValueError, "allowance"):
            selection_plan(EMPTY, EMPTY, "",
                           URL + " https://wuxia.click/novel/second-book",
                           chapter_range="1-20", confirm_rights=True)

    def test_single_and_bulk_workflows(self):
        bulk = Path(".github/workflows/library-bulk-download.yml").read_text()
        single = Path(".github/workflows/wuxiaclick-download.yml").read_text()
        self.assertIn("wuxiaclick_matrix", bulk)
        self.assertIn("wuxiaclick-download.yml", bulk)
        self.assertNotIn("      website:", bulk)
        self.assertIn("--chunk-size 20 --confirm-rights", single)
        self.assertIn("Preserve checkpoint", single)
        self.assertIn("Regenerate registry", single)


if __name__ == "__main__":
    unittest.main()
