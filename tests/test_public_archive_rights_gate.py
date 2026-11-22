from __future__ import annotations

import unittest

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

    def test_accepts_separate_https_permission_page(self):
        evidence = validate_rights_evidence(
            "true",
            "https://author.example/permissions/archive",
            "https://novelfull.com/example-novel.html",
        )
        self.assertEqual(evidence, "https://author.example/permissions/archive")


if __name__ == "__main__":
    unittest.main()
