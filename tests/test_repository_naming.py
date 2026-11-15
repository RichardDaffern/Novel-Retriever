"""Verify repository paths and local documentation links across platforms."""
from __future__ import annotations

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)")
PUBLIC_ENTRYPOINTS = (
    "novel_downloader.py",
    "Download-All-Novels.cmd",
    "PDF-to-Novel/Convert-PDFs.cmd",
    "DOWNLOADED_NOVELS.md",
    "downloaded_novels.json",
    ".github/workflows/ci.yml",
    ".github/workflows/download-novel.yml",
    ".github/workflows/freewebnovel-download.yml",
    ".github/workflows/readnovelfull-download.yml",
    ".github/workflows/wuxiaclick-download.yml",
    ".github/workflows/scribblehub-download.yml",
    ".github/workflows/library-bulk-download.yml",
    ".github/workflows/download-covers.yml",
    ".github/workflows/pdf-conversion-ci.yml",
)


class RepositoryNamingTests(unittest.TestCase):
    def test_public_download_and_workflow_entrypoints_preserved(self):
        for path in PUBLIC_ENTRYPOINTS:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)

    def test_markdown_local_links_resolve(self):
        for document in ROOT.rglob("*.md"):
            if any(folder in (".git", "Downloaded_Novels") for folder in document.parts):
                continue
            text = document.read_text(encoding="utf-8")
            for match in LINK.finditer(text):
                raw = match.group(1).strip("<>")
                if raw.startswith("#"):
                    continue
                parsed = urlsplit(raw)
                if parsed.scheme or parsed.netloc:
                    continue
                target_path = unquote(parsed.path)
                if not target_path:
                    continue
                target = document.parent / target_path
                with self.subTest(document=str(document.relative_to(ROOT)),
                                  link=raw):
                    self.assertTrue(target.exists(),
                                    f"Broken local link: {document.relative_to(ROOT)} -> {raw}")

    def test_guides_and_research_are_in_docs(self):
        core = ("download-guide.md", "metadata-guide.md",
                "pdf-to-novel.md", "website-support.md")
        for name in core:
            self.assertTrue((ROOT / "docs" / name).is_file(), name)
        research = ROOT / "docs" / "research"
        self.assertGreaterEqual(len(list(research.glob("*.md"))), 10)
        self.assertFalse(list((ROOT / "tools").glob("*.md")),
                         "Research notes must live in docs/research, not tools/")

    def test_no_obsolete_internal_module_references(self):
        old_names = (
            "fff_progress_runner",
            "tools.library_bulk", "tools.bulk_download",
            "tools.bulk_recovery", "tools.bulk_stress",
            "tools.freewebnovel_probe",
            "tools.verified_crosspost_download",
            "tools.verified_crosspost_artifact",
            "novel_sources.json", "verified_crossposts.json",
        )
        for folder in (ROOT / "tools", ROOT / "tests"):
            for source in folder.rglob("*.py"):
                if source.resolve() == Path(__file__).resolve():
                    continue
                body = source.read_text(encoding="utf-8")
                for name in old_names:
                    with self.subTest(file=str(source.relative_to(ROOT)), name=name):
                        # Match full unqualified import, not a substring of
                        # a valid renamed identifier.
                        stale = re.search(
                            r"(?<![A-Za-z0-9_])" + re.escape(name)
                            + r"(?![A-Za-z0-9_])", body)
                        self.assertIsNone(stale, f"Stale reference {name} in {source}")


if __name__ == "__main__":
    unittest.main()
