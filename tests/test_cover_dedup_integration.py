"""Offline contract tests for the shared cover and archive deduplication pipeline."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
import warnings
import sys
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from PIL import Image

from tools.cover_pipeline import finalise_archive, finalise_book
from tools.novel_covers import CoverError, extract_epub_cover
from tools.novel_dedupe import consolidate, inspect


CONTAINER = '''<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
 version="1.0"><rootfiles><rootfile full-path="OEBPS/content.opf"
 media-type="application/oebps-package+xml"/></rootfiles></container>'''
OPF = '''<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Example Novel</dc:title><dc:creator>Example Author</dc:creator>
</metadata><manifest><item id="c" href="chapter.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine><itemref idref="c"/></spine></package>'''


def jpeg():
    output = BytesIO()
    Image.new("RGB", (160, 240), (110, 64, 34)).save(output, "JPEG")
    return output.getvalue()


def fixture(book: Path, *, text="Chapter one", source="https://novelfull.com/example.html",
            created="2026-11-15T12:00:00Z"):
    book.mkdir(parents=True, exist_ok=True)
    with ZipFile(book / "source.epub", "w") as epub:
        epub.writestr("mimetype", "application/epub+zip")
        epub.writestr("META-INF/container.xml", CONTAINER)
        epub.writestr("OEBPS/content.opf", OPF)
        epub.writestr("OEBPS/chapter.xhtml", "<html><body>Story</body></html>")
    name = "chapter_0001.txt"
    (book / name).write_text(text, encoding="utf-8")
    rows = [{"position": 1, "file": name,
             "sha256": sha256(text.encode("utf-8")).hexdigest()}]
    (book / "chapters.json").write_text(json.dumps(rows), encoding="utf-8")
    (book / "metadata.json").write_text(json.dumps({
        "title": "Example Novel", "author": "Example Author", "source_url": source,
        "chapter_count": 1, "created_at_utc": created}), encoding="utf-8")


def make_zip(path: Path, book: Path):
    with ZipFile(path, "w") as archive:
        for item in sorted(book.iterdir()):
            archive.write(item, "example/" + item.name)
    return path


class CoverPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.book = self.root / "book"
        fixture(self.book)

    def test_external_cover_embeds_and_records_provenance(self):
        data = jpeg()
        with patch("tools.cover_pipeline.covers.download_site_cover",
                   return_value=(data, ".jpg", "https://novelfull.com/cover.jpg")) as fetch:
            meta = finalise_book(self.book)
        self.assertEqual(meta["cover_status"], "available")
        self.assertEqual(meta["cover_image"], "cover.jpg")
        self.assertEqual(meta["cover_provenance"]["method"], "source_page")
        self.assertTrue(meta["cover_provenance"]["embedded"])
        self.assertEqual(extract_epub_cover(self.book / "source.epub"), (data, ".jpg"))
        fetch.assert_called_once_with("https://novelfull.com/example.html")

    def test_missing_cover_does_not_lose_book(self):
        original = (self.book / "chapter_0001.txt").read_bytes()
        with patch("tools.cover_pipeline.covers.download_site_cover",
                   side_effect=CoverError("unavailable")):
            meta = finalise_book(self.book)
        self.assertEqual(meta["cover_status"], "missing")
        self.assertNotIn("cover_image", meta)
        self.assertEqual((self.book / "chapter_0001.txt").read_bytes(), original)
        self.assertTrue((self.book / "source.epub").exists())

    def test_existing_cover_reused_without_network(self):
        (self.book / "cover.jpg").write_bytes(jpeg())
        with patch("tools.cover_pipeline.covers.download_site_cover") as fetch:
            meta = finalise_book(self.book)
        self.assertEqual(meta["cover_provenance"]["method"], "existing_file")
        fetch.assert_not_called()

    def test_only_verified_exact_cross_site_match_is_allowed(self):
        alt = "https://novelfull.com/example.html"
        url = "https://freewebnovel.com/novel/example"
        fixture(self.book, source=url)
        verified = {url: {"url": alt, "title": "Example Novel",
                          "author": "Example Author"}}
        def fetch(target):
            if target == url:
                raise CoverError("no cover")
            self.assertEqual(target, alt)
            return jpeg(), ".jpg", alt + "/cover.jpg"
        with patch("tools.cover_pipeline.covers.download_site_cover", side_effect=fetch) as remote:
            meta = finalise_book(self.book, verified_sources=verified)
        self.assertEqual(remote.call_count, 2)
        self.assertEqual(meta["cover_provenance"]["method"], "verified_cross_source")

    def test_wrong_cross_site_author_not_used(self):
        url = "https://freewebnovel.com/novel/example"
        fixture(self.book, source=url)
        verified = {url: {"url": "https://novelfull.com/example.html",
                          "title": "Example Novel", "author": "Different"}}
        with patch("tools.cover_pipeline.covers.download_site_cover",
                   side_effect=CoverError("unavailable")) as remote:
            finalise_book(self.book, verified_sources=verified)
        self.assertEqual(remote.call_count, 1)

    def test_cover_enrichment_rejects_duplicate_member_paths(self):
        path = make_zip(self.root / "ambiguous.zip", self.book)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(path, "a") as archive:
                archive.writestr("example/metadata.json", b'{"title":"forged"}')
        with self.assertRaisesRegex(ValueError, "Duplicate ZIP member"):
            finalise_archive(path, allow_network=False)
        self.assertTrue(path.is_file(), "Invalid source ZIP must remain unchanged")

    def test_cover_enrichment_rejects_unsafe_member_aliases(self):
        path = make_zip(self.root / "unsafe.zip", self.book)
        with ZipFile(path, "a") as archive:
            archive.writestr("example/../forged.json", b'{"title":"forged"}')
        with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
            finalise_archive(path, allow_network=False)

    def test_portable_zip_receives_cover_and_no_new_book_members(self):
        original = make_zip(self.root / "old-book.zip", self.book)
        with patch("tools.cover_pipeline.covers.download_site_cover",
                   return_value=(jpeg(), ".jpg", "https://novelfull.com/c.jpg")):
            meta = finalise_archive(original)
        self.assertEqual(meta["cover_status"], "available")
        with ZipFile(original) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn("example/cover.jpg", archive.namelist())
            self.assertIn("example/chapters.json", archive.namelist())


class DedupeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, name, **kwargs):
        folder = self.root / ("source-" + name)
        fixture(folder, **kwargs)
        return make_zip(self.root / (name + ".zip"), folder)

    def test_same_book_differently_named_archives_are_deduplicated(self):
        one = self.archive("old-copy")
        two = self.archive("new-copy", created="2026-11-16T12:00:00Z")
        report = consolidate([one, two], self.root / "output")
        self.assertEqual(report["unique"], 1)
        self.assertEqual(report["duplicates"], 1)
        self.assertEqual(report["conflicts"], 0)
        self.assertEqual(len(list((self.root / "output/novels").glob("*.zip"))), 1)
        self.assertEqual(inspect(one)["epub_sha256"], inspect(two)["epub_sha256"])
        self.assertEqual(consolidate([one, two], self.root / "output")["duplicates"], 1)

    def test_different_chapters_preserved_for_manual_review(self):
        original = self.archive("old")
        changed = self.archive("changed", text="A materially different chapter")
        report = consolidate([original, changed], self.root / "out")
        self.assertEqual(report["unique"], 1)
        self.assertEqual(report["conflicts"], 1)
        self.assertEqual(len(list((self.root / "out/review-conflicts").glob("*.zip"))), 1)
        self.assertTrue(original.exists())
        self.assertTrue(changed.exists())

    def test_different_novels_not_merged_on_title_alone(self):
        original = self.archive("first")
        other = self.archive("second", source="https://novelfull.com/another.html",
                             text="A different book sharing a common title")
        report = consolidate([original, other], self.root / "out")
        self.assertEqual(report["unique"], 2)

    def test_same_url_with_wrong_author_requires_review(self):
        first = self.archive("original")
        other_folder = self.root / "wrong-author-source"
        fixture(other_folder)
        metadata_path = other_folder / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["author"] = "A Different Author"
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        other = make_zip(self.root / "wrong-author.zip", other_folder)
        result = consolidate([first, other], self.root / "review")
        self.assertEqual(result["unique"], 1)
        self.assertEqual(result["conflicts"], 1)
        self.assertEqual(result["duplicates"], 0)

    def test_covered_equivalent_preferred_over_newer_missing_cover(self):
        old_book = self.root / "covered"
        fixture(old_book, created="2026-11-01T12:00:00Z")
        (old_book / "cover.jpg").write_bytes(jpeg())
        meta_path = old_book / "metadata.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["cover_image"] = "cover.jpg"
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        old = make_zip(self.root / "covered-old.zip", old_book)
        newer = self.archive("newer-uncovered", created="2026-11-16T12:00:00Z")
        report = consolidate([old, newer], self.root / "preferred")
        self.assertEqual(report["novels"][0]["zip_sha256"], inspect(old)["zip_sha256"])
        self.assertEqual(report["duplicates"], 1)

    def test_repeated_dedupe_does_not_treat_output_as_input(self):
        from tools import novel_dedupe
        input_dir = self.root / "mixed"
        input_dir.mkdir()
        folder = self.root / "novel-input"
        fixture(folder)
        make_zip(input_dir / "original.zip", folder)
        output = input_dir / "deduplicated"
        with patch.object(sys, "argv", ["dedupe", "--input", str(input_dir),
                                        "--output", str(output)]):
            self.assertEqual(novel_dedupe.main(), 0)
            self.assertEqual(novel_dedupe.main(), 0)
        self.assertEqual(len(list((output / "novels").glob("*.zip"))), 1)

    def test_corrupt_zip_is_reported_without_erasing_valid(self):
        good = self.archive("good")
        bad = self.root / "bad.zip"
        bad.write_bytes(b"not a zip")
        report = consolidate([good, bad], self.root / "out")
        self.assertEqual(report["unique"], 1)
        self.assertEqual(report["invalid"], 1)


class WorkflowIntegrationTests(unittest.TestCase):
    def test_every_site_runs_shared_finaliser(self):
        root = Path(__file__).resolve().parents[1]
        sites = ("download-novel", "freewebnovel-download",
                 "readnovelfull-download", "wuxiaclick-download",
                 "scribblehub-download")
        for site in sites:
            with self.subTest(site=site):
                data = (root / ".github/workflows" / (site + ".yml")).read_text()
                self.assertIn("python -u -m tools.cover_pipeline --directory downloads", data)
        bulk = (root / ".github/workflows/library-bulk-download.yml").read_text()
        self.assertIn("--resolve-covers", bulk)


if __name__ == "__main__":
    unittest.main()
