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
    "tools/fanficfare_progress_runner.py",
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

    def test_internal_fanficfare_runner_is_in_tools(self):
        runner = ROOT / "tools" / "fanficfare_progress_runner.py"
        self.assertTrue(runner.is_file())
        self.assertFalse((ROOT / "fanficfare_progress_runner.py").exists())
        source = (ROOT / "novel_downloader.py").read_text(encoding="utf-8")
        self.assertIn('"tools" / "fanficfare_progress_runner.py"', source)

    def test_guides_and_research_are_in_docs(self):
        core = ("download-guide.md", "metadata-guide.md",
                "pdf-to-novel.md", "website-support.md")
        for name in core:
            self.assertTrue((ROOT / "docs" / name).is_file(), name)
        research = ROOT / "docs" / "research"
        # Historical investigations are consolidated rather than retained
        # as many outdated standalone guides.
        expected = ("source-feasibility-2026-11-15.md",
                    "source-test-evidence-archive.md",
                    "webnovel-browser-probe.md",
                    "webnovel-bulk-import.md",
                    "webnovel-two-chapter-sample.md")
        for name in expected:
            with self.subTest(name=name):
                self.assertTrue((research / name).is_file(), name)
        self.assertLessEqual(len(list(research.glob("*.md"))), 6,
                             "Keep source research consolidated and navigable")
        self.assertFalse(list((ROOT / "tools").glob("*.md")),
                         "Research notes must live in docs/research, not tools/")

    def test_renamed_repo_guards_export_and_local_downloader(self):
        from tools.export_completed_github_novels import REPO
        self.assertEqual(REPO, "RichardDaffern/Novel-Retriever")
        workflow = (ROOT / ".github/workflows/export-completed-novels-20261116.yml").read_text(encoding="utf-8")
        self.assertIn("github.repository == 'RichardDaffern/Novel-Retriever'", workflow)
        self.assertIn("tests.test_export_end_to_end", workflow)
        downloader = (ROOT / "tools/download_all_artifacts.ps1").read_text(encoding="utf-8")
        self.assertIn("RichardDaffern/Novel-Retriever", downloader)
        from tools import download_registry, publish_registry
        self.assertNotIn("RichardDaffern/Novel_Library",
                         (ROOT / "tools/download_registry.py").read_text(encoding="utf-8"))
        self.assertNotIn("RichardDaffern/Novel_Library",
                         (ROOT / "tools/publish_registry.py").read_text(encoding="utf-8"))
        self.assertNotIn("RichardDaffern/Novel_Library",
                         (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_ci_does_not_run_on_generated_registry_only_changes(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        triggers = workflow.split("\non:\n", 1)[1].split("\nconcurrency:", 1)[0]
        for event in ("push", "pull_request"):
            pattern = rf"(?m)^  {event}:\n    paths-ignore:\n      - 'DOWNLOADED_NOVELS.md'\n      - 'downloaded_novels.json'"
            self.assertRegex(triggers, pattern)
        # The default CI checks still cover ordinary source or workflow pushes.
        self.assertIn("jobs:", workflow)
        self.assertIn("windows-smoke:", workflow)
        self.assertIn("zip-archive-smoke:", workflow)

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
