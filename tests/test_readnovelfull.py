"""Offline validation of ReadNovelFull chapter discovery, packaging, and bulk routing."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from novel_downloader import epub_chapters
from tools import chunked_download as batches
from tools.download_registry import website_name
from tools.mixed_source_bulk import selection_plan
from tools.readnovelfull_source import (
    SourceError, archive_url, chapter_index, discover,
    extract_chapter, validate_book_url, validate_chapter_url,
)
from tools.readnovelfull_downloader import DownloadError, download_range
from tools.readnovelfull_chunks import plan_download, fetch_batch

BOOK = "https://readnovelfull.com/cultivation-online-v3.html"
CH1 = "https://readnovelfull.com/cultivation-online/chapter-1-cultivation-online.html"
CH2 = "https://readnovelfull.com/cultivation-online/chapter-2-mysterious-girl.html"
AJAX = archive_url("2572")
PAGE = f"""<html><h3 class="title">Cultivation Online</h3>
<div id="rating" data-novel-id="2572"></div><ul class="info-meta">
<li>Genre: <a>Action</a><a>Romance</a></li>
<li>Author: Mylittlebrother</li><li>Status: Ongoing</li></ul>
<div class="desc">Cultivation Online</div>
<div class="desc-text">An invented synopsis for offline tests.</div>
<ul class="list-chapter"><li><a href="{CH1}">Chapter 1</a></li>
<li><a href="{CH2}">Chapter 2</a></li></ul></html>"""
INDEX = """<ul class="list-chapter">
<li><a title="Chapter 2 - Girl" href="/cultivation-online/chapter-2-mysterious-girl.html">Chapter 2</a></li>
<li><a title="Chapter 1 - Online" href="/cultivation-online/chapter-1-cultivation-online.html">Chapter 1</a></li>
</ul>"""
TEXT = ("The traveller followed the merchant to the mountain at dawn. "
        "The busy market was full of people describing their adventures. "
        "The traveller studied a map of a distant forest on the hill. ") * 4


def html_chapter(number):
    return (f'<html><title>Chapter {number}</title><h1>Chapter {number}</h1>'
            '<div id="chr-content"><div class="ads">ADVERTISEMENT</div>'
            f'<p>{TEXT} Chapter {number}</p></div></html>')


class ReadNovelFullTests(unittest.TestCase):
    def test_strict_book_and_chapter_urls(self):
        self.assertEqual(validate_book_url(BOOK), BOOK)
        self.assertEqual(validate_book_url(BOOK.replace("https://", "https://www.")), BOOK)
        self.assertEqual(validate_chapter_url(CH1)[1], 1)
        # A real public chapter archive contains this unusual but valid slug.
        special = "https://readnovelfull.com/cultivation-online/chapter-1131sword-pagoda4.html"
        self.assertEqual(validate_chapter_url(special)[1], 1131)
        for bad in (
            "https://readnovelfull.com/",
            BOOK + "?session=1",
            "http://readnovelfull.com/book.html",
            "https://readnovelfull.com.evil.test/book.html",
            "https://readnovelfull.com:8080/book.html",
            "https://u:p@readnovelfull.com/book.html",
        ):
            with self.subTest(bad=bad), self.assertRaises(SourceError):
                validate_book_url(bad)
        with self.assertRaises(SourceError):
            validate_chapter_url(CH1, book_prefix="another")

    def test_archive_is_full_and_ordered(self):
        seen = []
        def fetch(url):
            seen.append(url)
            return {BOOK: PAGE, AJAX: INDEX}[url]
        details = discover(BOOK, fetcher=fetch)
        self.assertEqual(seen, [BOOK, AJAX])
        self.assertEqual(details["numChapters"], 2)
        self.assertEqual([x["url"] for x in details["chapters"]], [CH1, CH2])
        self.assertEqual(details["genres"], ["Action", "Romance"])
        self.assertEqual(details["status"], "Ongoing")
        self.assertEqual(details["description"], "An invented synopsis for offline tests.")

    def test_refuse_invalid_archive_or_wrong_identity(self):
        with self.assertRaisesRegex(SourceError, "missing"):
            chapter_index(INDEX.replace("chapter-1-cultivation-online", "chapter-3-cultivation-online"), BOOK)
        with self.assertRaisesRegex(SourceError, "another novel"):
            chapter_index(INDEX.replace("cultivation-online/chapter-2", "other-book/chapter-2"), BOOK)
        with self.assertRaisesRegex(SourceError, "Duplicate"):
            chapter_index(INDEX + '<ul class="list-chapter"><li><a href="/cultivation-online/chapter-2-extra.html">Chapter 2</a></li></ul>', BOOK)
        with self.assertRaisesRegex(SourceError, "disagree"):
            discover(BOOK, fetcher={
                BOOK: PAGE.replace("chapter-1-cultivation-online", "chapter-1-wrong"),
                AJAX: INDEX,
            }.__getitem__)

    def test_extract_rejects_ads_short_challenges_and_wrong_numbers(self):
        found = extract_chapter(html_chapter(1), number=1, title="Chapter 1")
        self.assertNotIn("ADVERTISEMENT", found["text"])
        with self.assertRaisesRegex(SourceError, "Expected Chapter 2"):
            extract_chapter(html_chapter(1), number=2, title="Chapter 2")
        # Real chapter pages show the book title in h1 and chapter number in h2.
        with self.assertRaisesRegex(SourceError, "Expected Chapter 2"):
            extract_chapter(
                '<h1>Cultivation Online</h1><h2>Chapter 1: Prologue</h2>'
                '<div id="chr-content"><p>' + TEXT + '</p></div>',
                number=2, title="Chapter 2")
        with self.assertRaisesRegex(SourceError, "locked"):
            extract_chapter('<div id="chr-content">Unlock this chapter</div>', number=1, title="Chapter 1")
        with self.assertRaises(SourceError):
            extract_chapter("<title>Just a moment...</title>", number=1, title="Chapter 1")

    def test_rights_and_range_checked_before_network(self):
        calls = []
        with self.assertRaises(DownloadError):
            download_range(BOOK, 1, 2, Path("unused"), fetcher=calls.append)
        with self.assertRaises(DownloadError):
            download_range(BOOK, 1, 101, Path("unused"), confirm_rights=True,
                           fetcher=calls.append)
        self.assertEqual(calls, [])

    def test_epub_checksums_checkpoint_and_resume(self):
        pages = {BOOK: PAGE, AJAX: INDEX, CH1: html_chapter(1), CH2: html_chapter(2)}
        with TemporaryDirectory() as tmp:
            def fail(url):
                if url == CH2:
                    raise DownloadError("HTTP 404")
                return pages[url]
            with self.assertRaisesRegex(DownloadError, "404"):
                download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                               fetcher=fail, sleeper=lambda _: None)
            self.assertEqual(len(list(Path(tmp).rglob(".progress.json"))), 1)
            self.assertFalse(list(Path(tmp).rglob("source.epub")))
            calls, pauses = [], []
            def fetch(url):
                calls.append(url)
                return pages[url]
            result = download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                                    fetcher=fetch, sleeper=pauses.append)
            self.assertNotIn(CH1, calls)
            self.assertIn(CH2, calls)
            self.assertEqual(pauses, [1])
            book = Path(result["output_dir"])
            rows = json.loads((book / "chapters.json").read_text(encoding="utf-8"))
            self.assertEqual([x["position"] for x in rows], [1, 2])
            self.assertEqual(len(epub_chapters(book / "source.epub")[1]), 2)
            self.assertFalse((book / ".progress.json").exists())

    def test_plan_batch_and_bulk_routing(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = plan_download(BOOK, "1-2", 1, root / "plan.json",
                                 discoverer=lambda _: {"title": "Cultivation Online", "numChapters": 2})
            self.assertEqual(len(plan["pieces"]), 2)
            pages = {BOOK: PAGE, AJAX: INDEX, CH1: html_chapter(1), CH2: html_chapter(2)}
            import shutil
            for n in (1, 2):
                part, scratch = root / f"part{n}", root / f"scratch{n}"
                def runner(command, **kwargs):
                    self.assertIn("tools.readnovelfull_downloader", command)
                    download_range(BOOK, n, n, scratch, confirm_rights=True,
                                   fetcher=pages.__getitem__, sleeper=lambda _: None)
                fetch_batch(BOOK, batches.identity(BOOK), n, n, part, scratch, runner=runner)
                dest = root / "combined" / f"chapter-batch-{batches.identity(BOOK)}-{n:05d}-{n:05d}"
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(part, dest)
            final = batches.assemble(plan, root / "combined", root / "out")
            self.assertEqual(len(epub_chapters(final / "source.epub")[1]), 2)
        self.assertEqual(website_name(BOOK), "ReadNovelFull")
        bulk = selection_plan({"version": 1, "novels": []},
                              {"version": 1, "novels": []}, "", BOOK, "ReadNovelFull", "1-2")
        self.assertEqual(len(bulk["groups"]["ReadNovelFull"]), 1)

    def test_github_workflows_have_source_and_recovery(self):
        single = Path(".github/workflows/readnovelfull-download.yml").read_text()
        bulk = Path(".github/workflows/library-bulk-download.yml").read_text()
        self.assertIn("tools.readnovelfull_chunks", single)
        self.assertIn("tools.publish_registry", single)
        self.assertIn("uses: ./.github/workflows/readnovelfull-download.yml", bulk)
        self.assertIn('"$READNOVELFULL" == "failure"', bulk)
        self.assertIn('"$READNOVELFULL" == "cancelled"', bulk)


if __name__ == "__main__":
    unittest.main()
