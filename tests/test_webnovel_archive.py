"""Synthetic, offline compatibility checks for saved WebNovel archive packaging."""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from PIL import Image

from tools.webnovel_archive import archive_saved_pages, WebNovelArchiveError
from tools.webnovel_bulk_import import bulk_import

BOOK = "https://www.webnovel.com/book/example-story_33422293300201205"


def page(number, *, same=False):
    body = "same" if same else str(number)
    return (f'<html><nav>Unlock another chapter</nav><div class="cha-content">'
            f'<p>This invented original story has a chapter identifier {body}, '
            'and enough words to make a meaningful synthetic example. '
            'The characters discover a hilltop observatory during a foggy morning.</p>'
            '<p>A second paragraph describes a safe, invented expedition across '
            'the nearby harbour and a distant mountain range.</p></div></html>')


class WebNovelArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / "saved"
        self.input.mkdir()
        self.out = self.root / "import"
        for n in (1, 2, 3):
            (self.input / f"Chapter {n}.html").write_text(page(n), encoding="utf-8")
        bulk_import(self.input, self.out, "An Example Novel", "An Author",
                    confirm_rights=True, progress=lambda _msg: None)

    def package(self, **kwargs):
        return archive_saved_pages(self.out, BOOK, confirm_rights=True, **kwargs)

    def test_storage_controller_zip_contract_and_epub_chapter_order(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("Network call")):
            result = self.package()
        self.assertTrue(result.exists())
        with ZipFile(result) as z:
            self.assertIsNone(z.testzip())
            names = z.namelist()
            prefix = names[0].rsplit("/", 1)[0] + "/"
            self.assertEqual(len(names), 6)
            self.assertIn(prefix + "source.epub", names)
            metadata = json.loads(z.read(prefix + "metadata.json"))
            chapters = json.loads(z.read(prefix + "chapters.json"))
            self.assertEqual(metadata["source_url"], "https://www.webnovel.com/book/33422293300201205")
            self.assertEqual(metadata["chapter_count"], 3)
            self.assertEqual(metadata["source_chapter_range"], [1, 3])
            self.assertEqual([row["position"] for row in chapters], [1, 2, 3])
            self.assertEqual([row["chapter_number"] for row in chapters], [1, 2, 3])
            from hashlib import sha256
            for row in chapters:
                raw = z.read(prefix + row["file"])
                self.assertEqual(sha256(raw).hexdigest(), row["sha256"])
                self.assertIn(str(row["chapter_number"]).encode(), raw)
            with ZipFile(BytesIO(z.read(prefix + "source.epub"))) as epub:
                self.assertEqual(len([n for n in epub.namelist() if n.endswith(".xhtml")]), 3)
                self.assertEqual(epub.testzip(), None)

    def test_original_cover_embedded_and_validated(self):
        image = self.root / "my-verified-cover.png"
        Image.new("RGB", (120, 180), color="navy").save(image, "PNG")
        result = self.package(cover_path=image)
        with ZipFile(result) as z:
            prefix = z.namelist()[0].split("/")[0] + "/"
            info = json.loads(z.read(prefix + "metadata.json"))
            self.assertEqual(info["cover_image"], "cover.png")
            self.assertIn("user-supplied", info["cover_provenance"])
            self.assertEqual(z.read(prefix + "cover.png"), image.read_bytes())
            with ZipFile(BytesIO(z.read(prefix + "source.epub"))) as epub:
                self.assertEqual(epub.read("OEBPS/cover.png"), image.read_bytes())
                xml = ET.fromstring(epub.read("OEBPS/content.opf"))
                self.assertTrue(any(x.get("name") == "cover" for x in xml.iter()))

    def test_invalid_image_is_rejected_without_fallback_cover(self):
        image = self.root / "not-an-image.png"
        image.write_text("not a genuine cover")
        with self.assertRaisesRegex(WebNovelArchiveError, "Invalid user-supplied cover"):
            self.package(cover_path=image)

    def test_source_changed_after_import_refuses_publication(self):
        (self.input / "Chapter 2.html").write_text(page(2) + "changed", encoding="utf-8")
        with self.assertRaisesRegex(WebNovelArchiveError, "source changed"):
            self.package()
        self.assertFalse((self.root / "Downloaded_Novels").exists())

    def test_tampered_output_refuses_publication(self):
        (self.out / "chapter-000002.txt").write_text("wrong text", encoding="utf-8")
        with self.assertRaisesRegex(WebNovelArchiveError, "checkpoint hash"):
            self.package()

    def test_duplicate_body_is_detected(self):
        for n in (1, 2):
            (self.input / f"Chapter {n}.html").write_text(page(n, same=True), encoding="utf-8")
        second = self.root / "duplicate-import"
        bulk_import(self.input, second, "An Example Novel", "An Author",
                    confirm_rights=True, progress=lambda _msg: None)
        with self.assertRaisesRegex(WebNovelArchiveError, "duplicates"):
            archive_saved_pages(second, BOOK, confirm_rights=True)

    def test_incomplete_manifest_fails_closed(self):
        data = json.loads((self.out / "metadata.json").read_text())
        data["chapters"].pop()
        (self.out / "metadata.json").write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(WebNovelArchiveError, "incomplete or inconsistent"):
            self.package()

    def test_existing_zip_not_overwritten(self):
        zip_path = self.package()
        before = zip_path.read_bytes()
        with self.assertRaisesRegex(WebNovelArchiveError, "already exists"):
            self.package()
        self.assertEqual(zip_path.read_bytes(), before)

    def test_invalid_site_and_rights_checks(self):
        with self.assertRaisesRegex(WebNovelArchiveError, "confirm-rights"):
            archive_saved_pages(self.out, BOOK)
        with self.assertRaises(WebNovelArchiveError):
            archive_saved_pages(self.out, "https://evil.example/book/33422293300201205", confirm_rights=True)
        self.assertFalse((self.root / "Downloaded_Novels").exists())

    def test_tampered_epub_text_rejected_even_when_crc_valid(self):
        file = self.out / "book.epub"
        target = self.out / "changed.epub"
        with ZipFile(file) as original, ZipFile(target, "w") as changed:
            for info in original.infolist():
                data = original.read(info)
                if info.filename == "OEBPS/chapter-000002.xhtml":
                    data = data.replace(b"chapter identifier 2", b"chapter identifier 3")
                changed.writestr(info, data)
        target.replace(file)
        with self.assertRaisesRegex(WebNovelArchiveError, "content differs"):
            self.package()


if __name__ == "__main__":
    unittest.main()
