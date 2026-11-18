"""Offline FreeWebNovel catalogue-metadata regressions for single and bulk flows."""
from pathlib import Path
import json
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from novel_downloader import epub_chapters
from tools.chunked_download import assemble, cache_has_synopsis_support, identity, validate_piece
from tools.freewebnovel_downloader import book_details, download_range
from tools.freewebnovel_metadata import extract_book_metadata
from tools.freewebnovel_chunks import fetch_batch, plan_download

TEST_BODY = (
    "An entirely invented story about a quiet village and its local bookshop. "
    "One morning the protagonist meets a visitor bearing a mysterious letter, "
    "and they discuss a voyage while the sky changes colours outside. "
) * 4


def chapter_html(number: int) -> str:
    return (f'<html><title>Chapter {number} - An Example</title>'
            f'<h1>Chapter {number} - An Example</h1>'
            f'<div class="txt"><p>{TEST_BODY} Chapter {number}.</p>'
            f'<p>{TEST_BODY[::-1]}</p></div></html>')

BOOK = "https://freewebnovel.com/novel/big-life"
SYNOPSIS = (
    "A struggling writer finds his life changed after receiving an unusual gift. "
    "His career improves, yet he must overcome rivalry, financial pressure "
    "and complicated relationships while pursuing his literary ambitions."
)
HTML = f"""<html><head><title>Big Life</title></head><body>
<nav><a href="/genre/Yaoi">Sitewide navigation tag</a>
<a href="/genre/Sports">Sitewide navigation tag 2</a></nav>
<div class="breadcrumbs"><a href="/genre/Adventure">Adventure Novels</a>
<a href="/novel/big-life">Big Life</a></div>
<div class="novel-detail">
<h3>Big Life</h3><span>빅 라이프</span>
<a href="/author/jiho">JIHO</a>
<div class="genres">
<a href="/genre/Adventure">Adventure</a>,
<a href="/genre/Comedy">Comedy</a>,
<a href="/genre/Drama">Drama</a>,
<a href="/genre/Fantasy">Fantasy</a>,
<a href="/genre/Romance">Romance</a>,
<a href="/genre/Seinen">Seinen</a>,
<a href="/genre/Supernatural">Supernatural</a></div>
<a href="/sort/completed-novel">Completed</a>
<h1>Big Life</h1><h4>SUMMARY</h4>
<p>{SYNOPSIS}</p><a href="#more">See all</a>
<h3>Chapter List</h3><a href="/novel/big-life/chapter-1">Chapter 1</a>
<a href="/novel/big-life/chapter-2">Chapter 2</a>
<a href="/novel/big-life/chapter-304">Chapter 304</a></div>
<aside><h3>Related Novels</h3><a href="/genre/Xianxia">Xianxia</a>
<a href="/sort/ongoing-novel">Ongoing</a></aside>
</body></html>"""
GENRES = ["Adventure", "Comedy", "Drama", "Fantasy", "Romance", "Seinen", "Supernatural"]


class SourceMetadataTests(unittest.TestCase):
    def test_book_details_reads_exact_source_fields(self):
        details = book_details(HTML, BOOK)
        self.assertEqual(details["title"], "Big Life")
        self.assertEqual(details["author"], "JIHO")
        self.assertEqual(details["numChapters"], 304)
        self.assertEqual(details["genres"], GENRES)
        self.assertEqual(details["description"], SYNOPSIS)
        self.assertEqual(details["synopsis"], SYNOPSIS)
        self.assertEqual(details["status"], "Completed")

    def test_global_navigation_and_recommendations_never_become_tags(self):
        metadata = extract_book_metadata(HTML, "Big Life")
        self.assertNotIn("Yaoi", metadata["genres"])
        self.assertNotIn("Sports", metadata["genres"])
        self.assertNotIn("Xianxia", metadata["genres"])
        self.assertEqual(metadata["status"], "Completed")
        self.assertNotIn("Chapter List", metadata["description"])

    def test_missing_source_metadata_stays_missing(self):
        html = (f'<html><nav><a href="/genre/Romance">Romance</a></nav>'
                '<h1>Big Life</h1><a href="/novel/big-life/chapter-1">Chapter 1</a>'
                '<a href="/novel/big-life/chapter-2">Chapter 2</a>'
                '<aside><a href="/genre/Xianxia">Xianxia</a></aside></html>')
        details = book_details(html, BOOK)
        for key in ("genres", "description", "synopsis", "status"):
            self.assertNotIn(key, details)

    def test_ongoing_and_unnamed_status_are_not_guessed_from_story(self):
        ongoing = HTML.replace(">Completed</a>", ">Ongoing</a>")
        self.assertEqual(extract_book_metadata(ongoing, "Big Life")["status"], "Ongoing")
        unknown = HTML.replace(">Completed</a>", ">Recently Updated</a>")
        self.assertNotIn("status", extract_book_metadata(unknown, "Big Life"))

    def test_explicit_summary_fallback_without_heading(self):
        html = ('<html><h1>Big Life</h1><div id="novel-summary">'
                + SYNOPSIS + '</div></html>')
        self.assertEqual(extract_book_metadata(html, "Big Life")["description"], SYNOPSIS)

    def test_local_single_download_embeds_fields_in_epub_and_json(self):
        pages = {BOOK: HTML, BOOK+"/chapter-1": chapter_html(1),
                 BOOK+"/chapter-2": chapter_html(2)}
        with TemporaryDirectory() as tmp:
            calls = []
            def fetch(url):
                calls.append(url)
                return pages[url]
            result = download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                                    fetcher=fetch, sleeper=lambda _: None)
            folder = Path(result["output_dir"])
            metadata = json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["genres"], GENRES)
            self.assertEqual(metadata["description"], SYNOPSIS)
            self.assertEqual(metadata["synopsis"], SYNOPSIS)
            self.assertEqual(metadata["status"], "Completed")
            self.assertEqual(metadata["source_metadata_pipeline_version"], 1)
            epub_meta, chapters = epub_chapters(folder/"source.epub")
            self.assertEqual(epub_meta["description"], SYNOPSIS)
            self.assertEqual(epub_meta["genres"], GENRES)
            self.assertEqual(epub_meta["status"], "Completed")
            self.assertEqual(len(chapters), 2)
            self.assertEqual(calls, [BOOK, BOOK+"/chapter-1", BOOK+"/chapter-2"])

    def test_batched_download_and_shared_assembly_preserve_metadata(self):
        pages = {BOOK: HTML, BOOK+"/chapter-1": chapter_html(1),
                 BOOK+"/chapter-2": chapter_html(2)}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            planned = plan_download(BOOK, "1-2", 1, root/"plan.json",
                                    fetcher=pages.__getitem__)
            self.assertEqual(len(planned["pieces"]), 2)
            for piece in planned["pieces"]:
                start,end=piece["start"],piece["end"]
                folder = root/"parts"/piece["name"]
                scratch = root/f"scratch-{start}"
                def runner(command, **kwargs):
                    self.assertIn("tools.freewebnovel_downloader", command)
                    download_range(BOOK, start, end, scratch, confirm_rights=True,
                                   fetcher=pages.__getitem__, sleeper=lambda _: None)
                fetch_batch(BOOK, identity(BOOK), start, end, folder, scratch,
                            runner=runner)
                validated = validate_piece(folder, BOOK, identity(BOOK), start, end)
                self.assertEqual(validated["metadata"]["genres"], GENRES)
            final = assemble(planned, root/"parts", root/"result")
            final_data = json.loads((final/"metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(final_data["genres"], GENRES)
            self.assertEqual(final_data["description"], SYNOPSIS)
            self.assertEqual(final_data["status"], "Completed")
            final_epub, chapters = epub_chapters(final/"source.epub")
            self.assertEqual(final_epub["description"], SYNOPSIS)
            self.assertEqual(final_epub["genres"], GENRES)
            self.assertEqual(final_epub["status"], "Completed")
            self.assertEqual(len(chapters), 2)

    def test_old_batches_are_not_reused_by_new_bulk_download(self):
        old = {"cover_pipeline_version": 1}
        self.assertFalse(cache_has_synopsis_support(old, BOOK))
        fresh = {**old, "source_metadata_pipeline_version": 1}
        self.assertTrue(cache_has_synopsis_support(fresh, BOOK))
        # A supported parser cannot invent fields absent at the source.
        self.assertTrue(cache_has_synopsis_support(fresh, BOOK))


if __name__ == "__main__":
    unittest.main()
