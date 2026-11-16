"""Regression checks for historical bulk recovery and ReadNovelFull preflight."""
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RecoveryCompatibilityTests(unittest.TestCase):
    def test_historical_bulk_recovery_module_is_compatible(self):
        from tools.bulk_recovery import main as original_entry
        from tools.bulk_download_recovery import main as current_entry
        self.assertIs(original_entry, current_entry)

    def test_historical_cli_invocation_is_supported(self):
        result = subprocess.run(
            [sys.executable, "-m", "tools.bulk_recovery", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--plan", result.stdout)
        self.assertIn("--artifacts", result.stdout)

    def test_readnovelfull_dependencies_installed_before_import(self):
        source = (ROOT / ".github/workflows/readnovelfull-download.yml").read_text(
            encoding="utf-8"
        )
        preflight = source.split("  prepare:", 1)[1].split("\n  chapter-batches:", 1)[0]
        install = preflight.index("name: Install ReadNovelFull dependencies")
        validate = preflight.index("name: Validate and normalise ReadNovelFull book URL")
        self.assertLess(install, validate)


if __name__ == "__main__":
    unittest.main()
