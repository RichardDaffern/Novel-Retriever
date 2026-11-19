"""Offline checks: cover recovery never fetches source sites or changes novels."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_STORED

from PIL import Image

from tools import recover_covers_from_export as recovery


URL = "https://novelfull.com/novel-test.html"


def png_image():
    out = io.BytesIO()
    Image.new("RGB", (90, 140), "blue").save(out, "PNG")
    return out.getvalue()


def epub_with_cover(image):
    content = io.BytesIO()
    with ZipFile(content, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        archive.writestr("META-INF/container.xml", (
            '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>'
        ))
        archive.writestr("OEBPS/content.opf", (
            '<package xmlns="http://www.idpf.org/2007/opf"><metadata>'
            '<meta name="cover" content="front"/></metadata>'
            '<manifest><item id="front" href="cover.png" media-type="image/png"/></manifest>'
            '</package>'
        ))
        archive.writestr("OEBPS/cover.png", image)
    return content.getvalue()


def novel_zip(path, url=URL, cover=None, epub=None):
    with ZipFile(path, "w") as archive:
        archive.writestr("the-book/metadata.json", json.dumps({"title": "Novel Test",
                         "source_url": url, "chapter_count": 1}))
        archive.writestr("the-book/source.epub", epub or epub_with_cover(png_image()))
        if cover is not None:
            archive.writestr("the-book/cover.png", cover)


class CoverRecoveryTests(unittest.TestCase):
    def test_strict_completed_registry_requires_104_unique_full_books(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "registry.json"
            books = [{"url": f"https://novelfull.com/test-{n}.html",
                      "title": f"Test {n}", "downloads": [{"status": "complete",
                       "range": "all", "artifact_id": n + 1, "run_id": 1}]}
                     for n in range(104)]
            path.write_text(json.dumps({"novels": books}), encoding="utf-8")
            self.assertEqual(len(recovery.snapshot(path)), 104)
            books[0]["downloads"][0]["status"] = "failed"
            path.write_text(json.dumps({"novels": books}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Untrusted"):
                recovery.snapshot(path)

    def test_existing_cover_is_selected_without_looking_at_epub(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "example.zip"
            novel_zip(path, cover=png_image(), epub=b"not-an-epub")
            url, selected = recovery.inspect_archive(path)
            self.assertEqual(url, URL)
            self.assertEqual(selected[1:], (".png", "standalone"))

    def test_embedded_epub_cover_is_recovered_without_network(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "example.zip"
            novel_zip(path)
            url, selected = recovery.inspect_archive(path)
            self.assertEqual(url, URL)
            self.assertEqual(selected[1:], (".png", "embedded_epub"))

    def test_only_matching_snapshot_books_are_packaged(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "novels"
            source.mkdir()
            novel_zip(source / "a.zip", cover=png_image())
            novel_zip(source / "unrelated.zip",
                      url="https://novelfull.com/not-in-our-list.html",
                      cover=png_image())
            output = root / "covers"
            with patch.object(recovery, "snapshot", return_value={
                URL: {"title": "Novel Test", "url": URL}}):
                result = recovery.recover(source, root / "unused.json", output)
            self.assertEqual(len(result["covers"]), 1)
            manifest = json.loads((output / "covers_manifest.json").read_text("utf-8"))
            self.assertEqual(manifest["covers"][0]["source_url"], URL)
            self.assertEqual(manifest["covers"][0]["website"], "NovelFull")
            self.assertEqual(result["summary"]["unresolved"], 1)
            self.assertTrue((output / manifest["covers"][0]["cover_file"]).exists())

    def test_duplicate_url_never_publishes_second_cover(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "novels"
            source.mkdir()
            novel_zip(source / "a.zip", cover=png_image())
            novel_zip(source / "b.zip", cover=png_image())
            with patch.object(recovery, "snapshot", return_value={
                URL: {"title": "Novel Test", "url": URL}}):
                result = recovery.recover(source, root / "unused.json", root / "covers")
            self.assertEqual(len(result["covers"]), 1)
            self.assertEqual(result["summary"]["unresolved"], 1)


if __name__ == "__main__":
    unittest.main()
