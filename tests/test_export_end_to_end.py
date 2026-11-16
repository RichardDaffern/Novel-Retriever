"""Offline end-to-end consolidated export regression with fake GitHub artefacts."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import export_completed_github_novels as exporter
from tests.test_cover_dedup_integration import fixture, make_zip
from tools.novel_covers import CoverError


class ConsolidatedExportIntegrationTests(unittest.TestCase):
    def test_partial_artifact_failure_still_exports_valid_book_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = root / "book"
            fixture(book)
            raw = make_zip(root / "artifact.zip", book)
            key = exporter.source_key("https://novelfull.com/example.html")
            artifact = {"name": f"novel-100-{key}", "id": 123456,
                        "created_at": "2026-11-16T12:00:00Z",
                        "size_in_bytes": raw.stat().st_size}
            inaccessible = {"name": f"novel-100-{key}", "id": 123457,
                            "created_at": "2026-11-15T12:00:00Z",
                            "size_in_bytes": raw.stat().st_size}
            def download(item, destination):
                if item["id"] == inaccessible["id"]:
                    raise OSError("expired or inaccessible")
                shutil.copyfile(raw, destination)
            destination = root / "export"
            with (patch.dict(os.environ, {"GH_TOKEN": "fake-token"}),
                  patch.object(sys, "argv", ["export", "--output", str(destination),
                                             "--registry", str(root / "registry.json")]),
                  patch.object(exporter, "index_registry", return_value=(
                      {key: {"title": "Example Novel",
                             "source_url": "https://novelfull.com/example.html"}}, [100])),
                  patch.object(exporter, "GitHub") as github,
                  patch("tools.cover_pipeline.covers.download_site_cover",
                        side_effect=CoverError("no source image"))):
                github.return_value.run_artifacts.return_value = [artifact, inaccessible]
                github.return_value.download.side_effect = download
                exporter.main()
            report = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(report["exported_novels"], 1)
            self.assertEqual(len(report["novels"]), 1)
            self.assertEqual(len(list((destination / "novels").glob("*.zip"))), 1)
            self.assertGreaterEqual(len(report["warnings"]), 1)
            row = report["novels"][0]
            self.assertEqual(row["chapter_count"], 1)
            self.assertIn("novel-100", row["original_github_artifact"])
            self.assertEqual(len(row["zip_sha256"]), 64)
            self.assertEqual(row["cover_status"], "missing")
            self.assertTrue((destination / "SHA256SUMS.txt").is_file())


if __name__ == "__main__":
    unittest.main()
