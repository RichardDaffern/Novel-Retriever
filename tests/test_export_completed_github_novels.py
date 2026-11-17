"""Offline tests for the completed-novel HF export; no network required."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_STORED

from tools.export_completed_github_novels import (
    GitHub, check_archive, package_novel, safe_member, safe_title, source_key,
)


def sample_archive(path: Path):
    epub = io.BytesIO()
    with ZipFile(epub, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=ZIP_STORED)
        z.writestr("META-INF/container.xml", "<container/>")
        z.writestr("OEBPS/book.opf", "<package/>")
    folder = "a-test-book/"
    with ZipFile(path, "w") as z:
        z.writestr(folder + "source.epub", epub.getvalue())
        z.writestr(folder + "metadata.json", json.dumps({
            "title": "Test Book", "source_url": "https://novelfull.com/test-book.html",
            "chapter_count": 2,
        }))
        z.writestr(folder + "chapters.json", json.dumps([
            {"chapter_number": 1}, {"chapter_number": 2}
        ]))
        z.writestr(folder + "chapter_00001.txt", "The first test chapter " * 30)
        z.writestr(folder + "chapter_00002.txt", "The second test chapter " * 30)


class ExportTests(unittest.TestCase):
    def test_source_key_is_deterministic(self):
        url = "https://novelfull.com/test-book.html"
        self.assertEqual(source_key(url), source_key(url))
        self.assertEqual(len(source_key(url)), 20)

    def test_safe_names_and_paths(self):
        self.assertEqual(safe_title("One: A/Book?"), "One_ A_Book")
        for name in ("/private.txt", "../private.txt", "book/../../hidden",
                     "book/./metadata.json", "book//metadata.json",
                     "C:/metadata.json", "book/name:stream",
                     "book/name. ", "book/\\\\metadata.json"):
            self.assertFalse(safe_member(name))

    def test_novel_export_accepts_nested_complete_artifact(self):
        with TemporaryDirectory() as d:
            folder = Path(d)
            raw = folder / "github.zip"
            ready = folder / "ready.zip"
            sample_archive(raw)
            meta, count = check_archive(raw)
            self.assertEqual(meta["title"], "Test Book")
            self.assertEqual(count, 2)
            package_novel(raw, ready)
            self.assertTrue(ready.exists())
            with ZipFile(ready) as output:
                self.assertEqual(output.testzip(), None)
                names = output.namelist()
                self.assertEqual(len(names), len(set(names)), "Duplicate ZIP entries")
                self.assertEqual(sum(name.endswith("/source.epub") for name in names), 1)
                self.assertEqual(sum(name.endswith("/metadata.json") for name in names), 1)

    def test_reject_case_aliased_members(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "aliased.zip"
            sample_archive(source)
            with ZipFile(source, "a") as archive:
                archive.writestr("A-TEST-BOOK/METADATA.JSON", "{}")
            with self.assertRaisesRegex(ValueError, "duplicate or case-aliased"):
                check_archive(source)

    def test_failed_artifact_download_preserves_existing_cache(self):
        class BrokenStream:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def raise_for_status(self):
                pass

            def iter_content(self, chunk_size):
                yield b"partial response"
                raise OSError("connection interrupted")

        class Redirect:
            status_code = 302
            headers = {"Location": "https://cdn.example.org/archive.zip"}

        with TemporaryDirectory() as directory:
            root = Path(directory)
            cached = root / "cached.zip"
            cached.write_bytes(b"existing verified cache")
            github = GitHub("test-token")
            with patch.object(github.api, "get", return_value=Redirect()), \\
                    patch("tools.export_completed_github_novels.requests.get",
                          return_value=BrokenStream()):
                with self.assertRaisesRegex(OSError, "connection interrupted"):
                    github.download({"id": 123}, cached)
            self.assertEqual(cached.read_bytes(), b"existing verified cache")
            self.assertEqual(sorted(p.name for p in root.iterdir()), ["cached.zip"])

    def test_reject_incomplete_novel(self):
        with TemporaryDirectory() as d:
            source = Path(d) / "bad.zip"
            with ZipFile(source, "w") as z:
                z.writestr("metadata.json", "{}")
            with self.assertRaisesRegex(ValueError, "source.epub"):
                check_archive(source)


if __name__ == "__main__":
    unittest.main()
