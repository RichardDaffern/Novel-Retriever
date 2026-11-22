from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.rights_gate import validate_rights_evidence


class PublicArchiveRightsGateTests(unittest.TestCase):
    def test_rejects_missing_confirmation(self):
        with self.assertRaisesRegex(ValueError, "explicitly confirm rights"):
            validate_rights_evidence("false", "https://author.example/permission")

    def test_rejects_missing_evidence(self):
        with self.assertRaisesRegex(ValueError, "separate author/rights-holder"):
            validate_rights_evidence("true", "")

    def test_rejects_non_https_evidence(self):
        with self.assertRaisesRegex(ValueError, "clean HTTPS URL"):
            validate_rights_evidence("true", "http://author.example/permission")

    def test_rejects_the_book_listing_as_evidence(self):
        source = "https://novelfull.com/example-novel.html"
        with self.assertRaisesRegex(ValueError, "public book listing"):
            validate_rights_evidence("true", source, source)

    def test_rejects_listing_url_with_tracking_query_as_evidence(self):
        source = "https://novelfull.com/example-novel.html?utm_source=feed"
        with self.assertRaisesRegex(ValueError, "public book listing"):
            validate_rights_evidence(
                "true",
                "https://novelfull.com/example-novel.html",
                source,
            )

    def test_accepts_separate_https_permission_page(self):
        evidence = validate_rights_evidence(
            "true",
            "https://author.example/permissions/archive",
            "https://novelfull.com/example-novel.html",
        )
        self.assertEqual(evidence, "https://author.example/permissions/archive")

    def test_every_public_download_workflow_requires_the_gate(self):
        root = Path(__file__).resolve().parents[1]
        workflows = [
            "library-bulk-download.yml",
            "download-novel.yml",
            "freewebnovel-download.yml",
            "readnovelfull-download.yml",
            "wuxiaclick-download.yml",
            "scribblehub-download.yml",
        ]
        for name in workflows:
            content = (root / ".github" / "workflows" / name).read_text(encoding="utf-8")
            with self.subTest(workflow=name):
                self.assertIn("rights_evidence_url:", content)
                self.assertIn("python tools/rights_gate.py", content)
        bulk = (root / ".github" / "workflows" / "library-bulk-download.yml").read_text(encoding="utf-8")
        self.assertEqual(
            bulk.count("rights_evidence_url: ${{ inputs.rights_evidence_url }}"),
            5,
        )
        self.assertIn("--plan-file library_bulk_plan.json", bulk)

    def test_plan_file_urls_are_checked_after_name_resolution(self):
        plan = {
            "groups": {
                "NovelFull": [{"novel_url": "https://novelfull.com/example-novel.html"}]
            },
            "skipped": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(plan), encoding="utf-8")
            from tools.rights_gate import _urls_from_plan
            with self.assertRaisesRegex(ValueError, "public book listing"):
                validate_rights_evidence(
                    "true",
                    "https://novelfull.com/example-novel.html?from=menu",
                    _urls_from_plan(path),
                )


if __name__ == "__main__":
    unittest.main()
