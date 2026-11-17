"""Regression tests for archive and cover publication safety (offline)."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from zipfile import ZipFile

from PIL import Image

from tools.novel_covers import write_cover
from tools.novel_dedupe import _copy_if_needed, _safe_members, file_digest


def cover_bytes(fmt="JPEG"):
    output = BytesIO()
    Image.new("RGB", (100, 150), (60, 80, 120)).save(output, format=fmt)
    return output.getvalue()


class AuditHardeningTests(unittest.TestCase):
    def test_file_hash_is_streamed_not_read_all_at_once(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "large.zip"
            payload = b"archive-content" * 200000
            path.write_bytes(payload)
            with patch.object(Path, "read_bytes", side_effect=AssertionError("full read")):
                self.assertEqual(file_digest(path), sha256(payload).hexdigest())

    def test_copy_failure_does_not_publish_partial_zip(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source, destination = root / "source.zip", root / "output" / "novel.zip"
            source.write_bytes(b"valid archive bytes")
            with patch("tools.novel_dedupe.shutil.copy2", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    _copy_if_needed(source, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(list(destination.parent.iterdir()), [])
            self.assertTrue(_copy_if_needed(source, destination))
            self.assertFalse(_copy_if_needed(source, destination))
            self.assertEqual(destination.read_bytes(), source.read_bytes())

    def test_deduplication_rejects_unsafe_raw_zip_paths(self):
        for member in ("book/./chapter.txt", "book//chapter.txt",
                       "book/../chapter.txt", "C:/chapter.txt",
                       "book/name:stream", "book/name. ", "book/\\chapter.txt"):
            with self.subTest(member=member):
                buffer = BytesIO()
                with ZipFile(buffer, "w") as archive:
                    archive.writestr(member, b"chapter")
                buffer.seek(0)
                with ZipFile(buffer) as archive:
                    with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
                        _safe_members(archive)

    def test_failed_cover_replace_preserves_existing_cover(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            original = cover_bytes()
            (folder / "cover.jpg").write_bytes(original)
            with patch.object(Path, "replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    write_cover(folder, cover_bytes(), ".jpg")
            self.assertEqual((folder / "cover.jpg").read_bytes(), original)
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ["cover.jpg"])

    def test_new_cover_publishes_before_removing_old_format(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "cover.jpg").write_bytes(cover_bytes())
            name = write_cover(folder, cover_bytes("PNG"), ".png")
            self.assertEqual(name, "cover.png")
            self.assertFalse((folder / "cover.jpg").exists())
            self.assertEqual(sorted(p.name for p in folder.iterdir()), ["cover.png"])


if __name__ == "__main__":
    unittest.main()
