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

    def test_real_source_typo_prefixes_keep_exact_chapter_numbers(self):
        # Published ReadNovelFull catalogue links, not fabricated URL repairs.
        samples = (
            ("godly-student", "chapters-121-delivering-the-immortal-frui", 121),
            ("heavenly-star", "chatper-202-the-heaven-and-earth-split-open-the-god-of-war-dies-part-i", 202),
            ("the-alchemist-god", "charter-140-falling-over-on-another", 140),
            ("the-mightiest-leveling-system", "chapter233-meet-nangong-yan-again", 233),
            ("world-domination-system", "c-1-power-levels-and-abbreviations", 0),
        )
        for book, fragment, chapter in samples:
            url = f"https://readnovelfull.com/{book}/{fragment}.html"
            with self.subTest(url=url):
                canonical, observed, prefix = validate_chapter_url(url, book_prefix=book)
                self.assertEqual(canonical, url)
                self.assertEqual(observed, chapter)
                self.assertEqual(prefix, book)
        with self.assertRaisesRegex(SourceError, "Invalid"):
            validate_chapter_url("https://readnovelfull.com/heavenly-star/chatper-intro.html")
        with self.assertRaisesRegex(SourceError, "Invalid"):
            validate_chapter_url("https://readnovelfull.com/heavenly-star/chapterz-202.html")
        with self.assertRaisesRegex(SourceError, "another novel"):
            validate_chapter_url("https://readnovelfull.com/heavenly-star/chatper-202.html",
                                 book_prefix="godly-student")

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

    def test_genuine_prologue_is_saved_before_numbered_chapters(self):
        # ReadNovelFull publishes books with a /prologue.html that precedes
        # its Chapter 1. It must not overwrite Chapter 1 or be dropped.
        prologue = "https://readnovelfull.com/cultivation-online/prologue.html"
        self.assertEqual(validate_chapter_url(prologue)[1], 0)
        prologue_link = (
            '<li><a href="/cultivation-online/prologue.html">Prologue</a></li>'
        )
        page = PAGE.replace(
            '<ul class="list-chapter">',
            '<ul class="list-chapter">' + prologue_link,
        )
        index = INDEX.replace(
            '<ul class="list-chapter">',
            '<ul class="list-chapter">' + prologue_link,
        )
        pages = {
            BOOK: page,
            AJAX: index,
            prologue: ('<html><title>Prologue</title><h2>Prologue</h2>'
                       '<div id="chr-content"><p>' + TEXT +
                       ' The genuine prologue appears first.</p></div></html>'),
            CH1: html_chapter(1),
            CH2: html_chapter(2),
        }
        discovered = discover(BOOK, fetcher=pages.__getitem__)
        self.assertEqual(discovered["numChapters"], 3)
        self.assertEqual([row["position"] for row in discovered["chapters"]],
                         [1, 2, 3])
        self.assertEqual([row["chapter_number"] for row in discovered["chapters"]],
                         [0, 1, 2])
        self.assertEqual([row["url"] for row in discovered["chapters"]],
                         [prologue, CH1, CH2])
        with TemporaryDirectory() as tmp:
            result = download_range(
                BOOK, 1, 3, Path(tmp), confirm_rights=True,
                fetcher=pages.__getitem__, sleeper=lambda _: None,
            )
            book = Path(result["output_dir"])
            rows = json.loads((book / "chapters.json").read_text())
            self.assertEqual([row["chapter_number"] for row in rows], [0, 1, 2])
            self.assertEqual([row["position"] for row in rows], [1, 2, 3])
            self.assertEqual(len(epub_chapters(book / "source.epub")[1]), 3)
        with self.assertRaisesRegex(SourceError, "prologue heading"):
            extract_chapter(html_chapter(1), number=0, title="Prologue")
        with self.assertRaisesRegex(SourceError, "Invalid"):
            validate_chapter_url(
                "https://readnovelfull.com/cultivation-online/intro.html"
            )

    def test_verified_world_domination_front_matter_is_not_chapter_one(self):
        book = "https://readnovelfull.com/world-domination-system-v1.html"
        intro = "https://readnovelfull.com/world-domination-system/c-1-power-levels-and-abbreviations.html"
        first = "https://readnovelfull.com/world-domination-system/chapter-1-daneel.html"
        second = "https://readnovelfull.com/world-domination-system/chapter-2-intro.html"
        self.assertEqual(validate_chapter_url(intro)[1], 0)
        index = ('<ul class="list-chapter">'
                 f'<li><a href="{intro}">Chapter c-1 Power Levels And Abbreviations</a></li>'
                 f'<li><a href="{first}">Chapter 1 Daneel</a></li>'
                 f'<li><a href="{second}">Chapter 2 Intro</a></li></ul>')
        rows = chapter_index(index, book)
        self.assertEqual([x["chapter_number"] for x in rows], [0, 1, 2])
        self.assertEqual([x["position"] for x in rows], [1, 2, 3])
        self.assertEqual([x["url"] for x in rows], [intro, first, second])
        page = ('<html><h2>C-1: Power Levels And Abbreviations</h2>'
                f'<div id="chr-content"><p>{TEXT}</p></div></html>')
        self.assertIn("traveller", extract_chapter(
            page, number=0, title="Chapter c-1 Power Levels And Abbreviations")["text"])
        with self.assertRaisesRegex(SourceError, "verified front-matter"):
            extract_chapter(page.replace("Power Levels And Abbreviations", "Unknown Heading"),
                            number=0, title="Chapter c-1 Power Levels And Abbreviations")
        with self.assertRaisesRegex(SourceError, "another novel"):
            validate_chapter_url(intro, book_prefix="other-novel")

    def test_only_exact_verified_path_to_heaven_152_2_is_preserved(self):
        book = "https://readnovelfull.com/path-to-heaven-v1.html"
        primary = "https://readnovelfull.com/path-to-heaven/chapter-152-unique-spirit-root-physique.html"
        split = "https://readnovelfull.com/path-to-heaven/chapter-152-2-toying-with-me-on-purpose.html"
        anchors = [
            f'<li><a href="/path-to-heaven/chapter-{n}.html">Chapter {n}</a></li>'
            for n in range(1, 154) if n != 152
        ]
        anchors += [
            f'<li><a href="{primary}">Chapter 152 Unique Spirit Root Physique</a></li>',
            f'<li><a href="{split}">Chapter 152-2: Toying with me on purpose?</a></li>',
        ]
        rows = chapter_index('<ul class="list-chapter">' +
                             ''.join(anchors) + '</ul>', book)
        self.assertEqual(len(rows), 154)
        self.assertEqual([x["url"] for x in rows[151:153]], [primary, split])
        self.assertEqual([x["chapter_number"] for x in rows[151:153]], [152, 152])
        self.assertEqual([x["position"] for x in rows], list(range(1, 155)))
        wrong = split.replace("toying-with-me-on-purpose", "another-story")
        with self.assertRaisesRegex(SourceError, "Duplicate Chapter 152"):
            chapter_index(('<ul class="list-chapter">' + ''.join(anchors) +
                           f'<li><a href="{wrong}">Chapter 152-2</a></li></ul>'), book)

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

    def test_invalid_archive_href_is_reported_without_rewriting(self):
        bad_href = "/cultivation-online/intro.html?source=archive"
        archive = INDEX.replace(
            "</ul>",
            f'<li><a href="{bad_href}">Unexpected intro</a></li></ul>',
        )
        with self.assertRaises(SourceError) as caught:
            chapter_index(archive, BOOK)
        self.assertIn(bad_href, str(caught.exception))
        self.assertIn(BOOK, str(caught.exception))

    def test_duplicate_archive_error_reports_both_exact_urls(self):
        duplicate = "/cultivation-online/chapter-2-alt.html"
        archive = INDEX + (
            f'<ul class="list-chapter"><li><a href="{duplicate}">'
            'Chapter 2 duplicate</a></li></ul>'
        )
        with self.assertRaises(SourceError) as caught:
            chapter_index(archive, BOOK)
        self.assertIn(CH2, str(caught.exception))
        self.assertIn(duplicate, str(caught.exception))

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
                              {"version": 1, "novels": []}, "", BOOK, "ReadNovelFull", "1-2",
                              confirm_rights=True)
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
