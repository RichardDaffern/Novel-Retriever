"""Offline unit and integration tests for FreeWebNovel's isolated archive flow."""
from hashlib import sha256
from http.client import RemoteDisconnected
from urllib.error import HTTPError, URLError
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from tools.freewebnovel_downloader import (
    DownloadError, book_details, download_range, extract_chapter,
)
from tools.freewebnovel_chunks import plan_download, fetch_batch, plan_bulk
from tools.freewebnovel_source import (
    ProbeError, TransientFetchError, fetch_public_html
)
from tools.chunked_download import (
    identity, validate_piece, assemble,
)
from novel_downloader import epub_chapters

BOOK = "https://freewebnovel.com/novel/the-first-order"
CH1 = BOOK + "/chapter-1"
CH2 = BOOK + "/chapter-2"
CATALOG = f"""<html><h1>The First Order</h1>
<a href="/author/the-speaking-pork-trotter">The Speaking Pork Trotter</a>
<h3>Latest Chapters</h3>
<a href="{BOOK}/chapter-1260">Chapter 1260 - Final</a>
<a href="{BOOK}/chapter-1259">Chapter 1259</a>
<h3>Chapter List</h3>
<a href="{CH1}">Chapter 1 - Opening</a>
<a href="{CH2}">Chapter 2 - Arrival</a></html>
"""
TEXT = (
    "A completely invented chapter describes a peaceful village before sunrise. "
    "The main character walks towards a trading post and meets an old merchant. "
    "A distant mountain is visible beyond the wooden gates, while the busy "
    "street fills with people returning from their morning errands. "
)
def chapter_html(number):
    title = f"Chapter {number} - Original test chapter"
    body = (TEXT + f" Number {number} begins here. ") * 2
    return (f'<html><title>{title} - Read Online</title><h1>{title}</h1>'
            f'<div class="txt"><div class="advertisement">ADVERTISEMENT</div>'
            f'<p>{body}</p><p>{body[::-1]}</p></div></html>')


class FreeWebNovelDownloaderTests(unittest.TestCase):
    def test_count_based_on_latest_chapter_not_first_page_40(self):
        meta = book_details(CATALOG, BOOK)
        self.assertEqual(meta["numChapters"], 1260)
        self.assertEqual(meta["title"], "The First Order")
        self.assertEqual(meta["author"], "The Speaking Pork Trotter")
        self.assertEqual(meta["first_two_links"][0]["position"], 1)

    def test_book_details_maps_auxiliary_links_and_uses_displayed_count(self):
        offset_catalogue = """<html><h1>HP: The Arcane Thief</h1>
<a href="/author/snollygoster">Snollygoster</a>
<a href="/novel/the-first-order/chapter-255">Chapter 254: Latest</a>
<a href="/novel/the-first-order/chapter-1">Auxiliary Chapter (Read First)</a>
<a href="/novel/the-first-order/chapter-2">Chapter 1: Opening</a>
<a href="/novel/the-first-order/chapter-3">Chapter 2: Arrival</a>
</html>"""
        meta = book_details(offset_catalogue, BOOK)
        self.assertEqual(meta["numChapters"], 254)
        self.assertEqual(meta["chapter_url_offset"], 1)
        self.assertEqual(
            [x["url"] for x in meta["first_two_links"]],
            [BOOK + "/chapter-2", BOOK + "/chapter-3"],
        )

    def test_book_details_stops_on_non_linear_source_index(self):
        non_linear = """<html><h1>Naruto: The Wind Calamity</h1>
<a href="/novel/the-first-order/chapter-4">Chapter 1: Opening</a>
<a href="/novel/the-first-order/chapter-5">Chapter 2: Orphanage</a>
<a href="/novel/the-first-order/chapter-950">Chapter 948 - 941: Latest</a>
</html>"""
        with self.assertRaisesRegex(ProbeError, "Non-linear chapter URL mapping"):
            book_details(non_linear, BOOK)

    def test_download_uses_catalogue_url_offset_not_chapter_number_as_slug(self):
        offset_catalogue = """<html><h1>HP: The Arcane Thief</h1>
<a href="/author/snollygoster">Snollygoster</a>
<a href="/novel/the-first-order/chapter-255">Chapter 254: Latest</a>
<a href="/novel/the-first-order/chapter-1">Auxiliary Chapter (Read First)</a>
<a href="/novel/the-first-order/chapter-2">Chapter 1: Opening</a>
<a href="/novel/the-first-order/chapter-3">Chapter 2: Arrival</a>
</html>"""
        pages = {
            BOOK: offset_catalogue,
            BOOK + "/chapter-2": chapter_html(1),
            BOOK + "/chapter-3": chapter_html(2),
        }
        calls = []
        def fetch(url):
            calls.append(url)
            return pages[url]
        with TemporaryDirectory() as tmp:
            result = download_range(
                BOOK, 1, 2, Path(tmp), confirm_rights=True,
                fetcher=fetch, sleeper=lambda _: None,
            )
        self.assertEqual(result["chapter_count"], 2)
        self.assertEqual(calls, [
            BOOK, BOOK + "/chapter-2", BOOK + "/chapter-3",
        ])

    def test_chapter_title_and_body_number_match(self):
        value = extract_chapter(chapter_html(2), 2)
        self.assertIn("Chapter 2", value["title"])
        self.assertIn("peaceful village", value["text"])
        self.assertNotIn("ADVERTISEMENT", value["text"])
        with self.assertRaisesRegex(DownloadError, "Expected Chapter 1"):
            extract_chapter(chapter_html(2), 1)

    def test_short_and_locked_chapters_rejected(self):
        for page in (
            '<div class="txt">short</div>',
            '<div class="txt">Unlock this chapter to continue reading.</div>',
        ):
            with self.subTest(page=page), self.assertRaises(DownloadError):
                extract_chapter(page, 1)

    def test_two_chapter_txt_epub_manifest_and_hashes(self):
        calls = []
        pauses = []
        pages = {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}
        def fetch(url):
            calls.append(url)
            return pages[url]
        with TemporaryDirectory() as tmp:
            result = download_range(
                BOOK, 1, 2, Path(tmp),
                confirm_rights=True, fetcher=fetch, sleeper=pauses.append,
            )
            self.assertEqual(calls, [BOOK, CH1, CH2])
            self.assertEqual(pauses, [1, 1])
            self.assertEqual(result["chapter_count"], 2)
            folder = Path(result["output_dir"])
            self.assertTrue((folder / "source.epub").is_file())
            self.assertEqual(
                [r["position"] for r in json.loads((folder / "chapters.json").read_text())],
                [1, 2],
            )
            self.assertFalse((folder / ".progress.json").exists())
            # SHA-256 is defined over the actual ZIP/TXT bytes, not text
            # normalised by Python's read_text() on Windows.
            for row in json.loads((folder / "chapters.json").read_text()):
                chapter_bytes = (folder / row["file"]).read_bytes()
                self.assertEqual(sha256(chapter_bytes).hexdigest(), row["sha256"])
                self.assertNotIn(b"\r\n", chapter_bytes)
            with ZipFile(folder / "source.epub") as archive:
                self.assertIsNone(archive.testzip())
            book, chapters = epub_chapters(folder / "source.epub")
            self.assertEqual(len(chapters), 2)
            self.assertEqual(book["title"], "The First Order")
            self.assertEqual(book["author"], "The Speaking Pork Trotter")

    def test_interruption_saves_verified_checkpoint_and_resumes(self):
        with TemporaryDirectory() as tmp:
            seen = []
            def first_fetch(url):
                seen.append(url)
                if url == CH2:
                    raise DownloadError("network interrupted")
                return {BOOK: CATALOG, CH1: chapter_html(1)}[url]
            with self.assertRaisesRegex(DownloadError, "interrupted"):
                download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                               fetcher=first_fetch, sleeper=lambda _: None)
            paths = list(Path(tmp).rglob(".progress.json"))
            self.assertEqual(len(paths), 1)
            self.assertEqual(
                len(json.loads(paths[0].read_text())["chapters"]), 1
            )
            resumed = []
            def second_fetch(url):
                resumed.append(url)
                return {BOOK: CATALOG, CH2: chapter_html(2)}[url]
            result = download_range(
                BOOK, 1, 2, Path(tmp), confirm_rights=True,
                fetcher=second_fetch, sleeper=lambda _: None)
            self.assertEqual(resumed, [BOOK, CH2])
            self.assertEqual(result["chapter_count"], 2)

    def test_temporary_remote_disconnect_retries_only_failed_chapter(self):
        with TemporaryDirectory() as tmp:
            calls, pauses = [], []
            fails = 0

            def fetch(url):
                nonlocal fails
                calls.append(url)
                if url == CH2 and fails < 2:
                    fails += 1
                    raise TransientFetchError("Remote end closed connection")
                return {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}[url]

            result = download_range(
                BOOK, 1, 2, Path(tmp), confirm_rights=True,
                fetcher=fetch, sleeper=pauses.append,
            )
            self.assertEqual(result["chapter_count"], 2)
            self.assertEqual(calls, [BOOK, CH1, CH2, CH2, CH2])
            self.assertEqual(pauses, [1, 1, 4, 12])
            self.assertFalse(list(Path(tmp).rglob(".progress.json")))
            self.assertEqual(len(list(Path(tmp).rglob("source.epub"))), 1)

    def test_retry_exhaustion_saves_checkpoint_and_resume_skips_valid_chapter(self):
        with TemporaryDirectory() as tmp:
            calls = []

            def drops(url):
                calls.append(url)
                if url == CH2:
                    raise TransientFetchError("Temporary network disconnection")
                return {BOOK: CATALOG, CH1: chapter_html(1)}[url]

            with self.assertRaisesRegex(TransientFetchError, "after 3 attempts"):
                download_range(
                    BOOK, 1, 2, Path(tmp), confirm_rights=True,
                    fetcher=drops, sleeper=lambda _: None,
                )
            self.assertEqual(calls, [BOOK, CH1, CH2, CH2, CH2])
            self.assertEqual(len(list(Path(tmp).rglob(".progress.json"))), 1)
            self.assertEqual(list(Path(tmp).rglob("source.epub")), [])

            resumed = []

            def resumed_fetch(url):
                resumed.append(url)
                return {BOOK: CATALOG, CH2: chapter_html(2)}[url]

            repaired = download_range(
                BOOK, 1, 2, Path(tmp), confirm_rights=True,
                fetcher=resumed_fetch, sleeper=lambda _: None,
            )
            self.assertEqual(resumed, [BOOK, CH2])
            self.assertEqual(repaired["chapter_count"], 2)

    def test_403_404_429_and_wrong_chapter_never_retry(self):
        for error in (
            ProbeError("Site returned HTTP 403; stopped"),
            ProbeError("Site returned HTTP 404; stopped"),
            ProbeError("Site returned HTTP 429; stopped"),
        ):
            with self.subTest(error=str(error)), TemporaryDirectory() as tmp:
                calls = []

                def fetch(url):
                    calls.append(url)
                    if url == CH2:
                        raise error
                    return {BOOK: CATALOG, CH1: chapter_html(1)}[url]

                with self.assertRaises(ProbeError):
                    download_range(
                        BOOK, 1, 2, Path(tmp), confirm_rights=True,
                        fetcher=fetch, sleeper=lambda _: None,
                    )
                self.assertEqual(calls, [BOOK, CH1, CH2])
                self.assertEqual(len(list(Path(tmp).rglob(".progress.json"))), 1)

        with TemporaryDirectory() as tmp:
            calls = []

            def wrong_page(url):
                calls.append(url)
                return {BOOK: CATALOG, CH1: chapter_html(1),
                        CH2: chapter_html(3)}[url]

            with self.assertRaisesRegex(DownloadError, "Expected Chapter 2"):
                download_range(
                    BOOK, 1, 2, Path(tmp), confirm_rights=True,
                    fetcher=wrong_page, sleeper=lambda _: None,
                )
            self.assertEqual(calls, [BOOK, CH1, CH2])

    def test_temporary_catalogue_failure_is_paced(self):
        with TemporaryDirectory() as tmp:
            calls, pauses = [], []

            def fetch(url):
                calls.append(url)
                if url == BOOK and calls.count(BOOK) == 1:
                    raise TransientFetchError("Temporary HTTP 503")
                return {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}[url]

            result = download_range(
                BOOK, 1, 2, Path(tmp), confirm_rights=True,
                fetcher=fetch, sleeper=pauses.append,
            )
            self.assertEqual(result["chapter_count"], 2)
            self.assertEqual(calls, [BOOK, BOOK, CH1, CH2])
            self.assertEqual(pauses, [4, 1, 1])

    def test_transport_exception_classification_does_not_retry_in_probe(self):
        from unittest.mock import Mock
        for error, transient in (
            (RemoteDisconnected("Remote end closed connection without response"), True),
            (TimeoutError("The read operation timed out"), True),
            (ConnectionResetError("Connection reset by peer"), True),
            (HTTPError(BOOK, 503, "Unavailable", {}, None), True),
            (HTTPError(BOOK, 502, "Bad gateway", {}, None), True),
            (HTTPError(BOOK, 429, "Too many requests", {}, None), False),
            (HTTPError(BOOK, 404, "Not found", {}, None), False),
            (HTTPError(BOOK, 403, "Forbidden", {}, None), False),
            (URLError(ConnectionResetError("reset")), True),
            (URLError("Name or service not known"), False),
        ):
            with self.subTest(error=str(error)):
                opener = SimpleNamespace(open=Mock(side_effect=error))
                with patch("tools.freewebnovel_source.build_opener",
                           return_value=opener):
                    if transient:
                        with self.assertRaises(TransientFetchError):
                            fetch_public_html(BOOK)
                    else:
                        with self.assertRaises(ProbeError) as ctx:
                            fetch_public_html(BOOK)
                        self.assertNotIsInstance(ctx.exception, TransientFetchError)
                opener.open.assert_called_once()

    def test_existing_archive_skips_chapter_downloads(self):
        with TemporaryDirectory() as tmp:
            pages = {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}
            download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                           fetcher=pages.__getitem__, sleeper=lambda _: None)
            requests = []
            def fetch(url):
                requests.append(url)
                return pages[url]
            download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                           fetcher=fetch, sleeper=lambda _: None)
            self.assertEqual(requests, [BOOK])

    def test_bad_checkpoint_chapter_is_refetched(self):
        with TemporaryDirectory() as tmp:
            calls = []
            def first_fetch(url):
                if url == CH2:
                    raise DownloadError("temporary loss")
                return {BOOK: CATALOG, CH1: chapter_html(1)}[url]
            with self.assertRaises(DownloadError):
                download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                               fetcher=first_fetch, sleeper=lambda _: None)
            one = next(Path(tmp).rglob("chapter_00001.txt"))
            one.write_text("corrupted", encoding="utf-8")
            def second_fetch(url):
                calls.append(url)
                return {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}[url]
            download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                           fetcher=second_fetch, sleeper=lambda _: None)
            self.assertEqual(calls, [BOOK, CH1, CH2])

    def test_rights_and_range_validation_before_network(self):
        calls = []
        for first, last, confirmed in ((1,2,False),(0,2,True),(1,101,True),(2,1,True)):
            with self.subTest(first=first,last=last,confirmed=confirmed):
                with self.assertRaises(DownloadError):
                    download_range(BOOK, first, last, Path("unused"),
                                   confirm_rights=confirmed,
                                   fetcher=lambda url: calls.append(url))
        self.assertEqual(calls, [])

    def test_missing_chapter_does_not_produce_complete_epub(self):
        def fetch(url):
            if url == CH2:
                raise DownloadError("HTTP 404")
            return {BOOK: CATALOG, CH1: chapter_html(1)}[url]
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(DownloadError, "404"):
                download_range(BOOK, 1, 2, Path(tmp), confirm_rights=True,
                               fetcher=fetch, sleeper=lambda _: None)
            self.assertEqual(list(Path(tmp).rglob("source.epub")), [])
            self.assertEqual(len(list(Path(tmp).rglob(".progress.json"))), 1)

    def test_plan_full_book_uses_conservative_batch_parallelism(self):
        with TemporaryDirectory() as tmp:
            plan = plan_download(BOOK, "", 50, Path(tmp)/"plan.json",
                                 fetcher=lambda url: CATALOG)
            self.assertEqual(plan["total_chapters"], 1260)
            self.assertEqual(plan["pieces"][0]["start"], 1)
            self.assertEqual(plan["pieces"][-1]["end"], 1260)
            self.assertEqual(plan["parallelism"], 2)
            self.assertEqual(len(plan["pieces"]), 26)

    def test_plan_rejects_more_than_100_chapters_per_batch(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                plan_download(BOOK, "", 200, Path(tmp)/"plan.json",
                              fetcher=lambda url: CATALOG)

    def test_site_specific_bulk_plan_rejects_unrelated_urls(self):
        with TemporaryDirectory() as tmp:
            registry = Path(tmp)/"registry.json"
            registry.write_text('{"version":1,"novels":[]}')
            with self.assertRaises(ValueError):
                plan_bulk("https://novelfull.com/another-novel.html", "", False,
                          registry=registry)
            result = plan_bulk(BOOK+" "+BOOK, "1-2", False, registry=registry)
            self.assertEqual(len(result["planned"]), 1)

    def test_reusable_batch_fetch_validate_and_assemble(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "first-batch"
            scratch = root / "scratch"
            pages = {BOOK: CATALOG, CH1: chapter_html(1), CH2: chapter_html(2)}
            def runner(command, **kwargs):
                assert command[0] and "tools.freewebnovel_downloader" in command
                download_range(BOOK, 1, 2, scratch, confirm_rights=True,
                               fetcher=pages.__getitem__, sleeper=lambda _: None)
            fetch_batch(BOOK, identity(BOOK), 1, 2, folder, scratch, runner=runner)
            validated = validate_piece(folder, BOOK, identity(BOOK), 1, 2)
            self.assertEqual(len(validated["chapters"]), 2)
            name = f"chapter-batch-{identity(BOOK)}-00001-00002"
            complete = root / "completed" / name
            complete.parent.mkdir(parents=True)
            import shutil
            shutil.copytree(folder, complete)
            plan = {
                "url": BOOK, "key": identity(BOOK), "first": 1, "last": 2,
                "pieces": [{"start":1,"end":2}],
            }
            final = assemble(plan, root / "completed", root / "downloaded")
            self.assertTrue((final / "source.epub").is_file())
            self.assertEqual(len(epub_chapters(final / "source.epub")[1]), 2)


if __name__ == "__main__":
    unittest.main()
