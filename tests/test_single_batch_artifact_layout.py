"""Regression tests for download-artifact's flat single-match extraction layout."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.chunked_download import assemble, chapter_plan
from hashlib import sha256

URL = "https://example.org/very-long-story.html"


def make_piece(root: Path, url: str, key: str, first: int, last: int) -> Path:
    folder = root / f"chapter-batch-{key}-{first:05d}-{last:05d}"
    book = folder / "book"
    book.mkdir(parents=True)
    rows = []
    for position in range(first, last + 1):
        filename = f"chapter_{position:04d}.txt"
        text = (f"Chapter {position}\n\n"
                f"Chapter {position} paragraph with synthetic content for validation.\n")
        (book / filename).write_text(text, encoding="utf-8")
        rows.append({"position": position, "chapter_number": position,
                     "title": f"Chapter {position}", "file": filename,
                     "word_count": len(text.split()),
                     "sha256": sha256(text.encode()).hexdigest()})
    (book / "chapters.json").write_text(json.dumps(rows), encoding="utf-8")
    (book / "metadata.json").write_text(json.dumps({
        "source_url": url, "chapter_count": len(rows),
        "title": "A Synthetic Very Long Story",
        "author": "Synthetic Test Author", "language": "en",
    }), encoding="utf-8")
    (book / "source.epub").write_bytes(b"synthetic batch archive fixture")
    (folder / "part.json").write_text(json.dumps({
        "version": 1, "url": url, "key": key, "start": first, "end": last,
    }), encoding="utf-8")
    return folder



class SingleBatchLayoutTests(unittest.TestCase):
    def test_flat_single_artifact_assembles_with_complete_chapters(self):
        plan = chapter_plan(URL, 3, "1-3", chunk_size=200)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chunks = root / "completed_batches"
            named = make_piece(chunks, URL, plan["key"], 1, 3)
            # The real failed Golden Time job downloaded this exact layout:
            # completed_batches/part.json and completed_batches/book/...
            for item in list(named.iterdir()):
                shutil.move(str(item), str(chunks / item.name))
            named.rmdir()
            result = assemble(plan, chunks, root / "out")
            metadata = json.loads((result / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["chapter_count"], 3)
            self.assertEqual(metadata["assembled_from_batches"], 1)
            self.assertTrue((result / "source.epub").is_file())
            for position in range(1, 4):
                self.assertTrue((result / f"chapter_{position:05d}.txt").is_file())

    def test_named_single_artifact_continues_to_work(self):
        plan = chapter_plan(URL, 2, "1-2", chunk_size=200)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_piece(root / "parts", URL, plan["key"], 1, 2)
            output = assemble(plan, root / "parts", root / "out")
            self.assertTrue((output / "source.epub").is_file())

    def test_flat_artifact_is_never_accepted_for_multi_batch(self):
        plan = chapter_plan(URL, 3, "1-3", chunk_size=2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chunks = root / "parts"
            make_piece(chunks, URL, plan["key"], 1, 2)
            make_piece(chunks, URL, plan["key"], 3, 3)
            (chunks / "part.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe for multi-batch"):
                assemble(plan, chunks, root / "out")
            self.assertFalse((root / "out").exists())

    def test_ambiguous_flat_and_named_artifacts_are_rejected(self):
        plan = chapter_plan(URL, 1, "1-1", chunk_size=200)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chunks = root / "parts"
            make_piece(chunks, URL, plan["key"], 1, 1)
            (chunks / "part.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                assemble(plan, chunks, root / "out")

    def test_flat_artifact_with_wrong_manifest_identity_is_rejected(self):
        plan = chapter_plan(URL, 1, "1-1", chunk_size=200)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chunks = root / "parts"
            named = make_piece(chunks, URL, plan["key"], 1, 1)
            for item in list(named.iterdir()):
                shutil.move(str(item), str(chunks / item.name))
            named.rmdir()
            manifest = chunks / "part.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["key"] = "wrong-book-identity"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Incorrect chapter batch identity"):
                assemble(plan, chunks, root / "out")
            self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
