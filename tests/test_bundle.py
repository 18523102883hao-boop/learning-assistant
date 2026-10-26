import hashlib
import json
import tempfile
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path

try:
    from companion.bundle import build_release
except ImportError:
    build_release = None

ROOT = Path(__file__).resolve().parents[1]


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(build_release, "尚未实现分角色可核验交付包")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_child_and_parent_skills_are_separate_and_private_sources_absent(self):
        output = Path(self.temp.name) / "release"
        build_release(ROOT, output, "test-a")
        with zipfile.ZipFile(output / "child-test-a.zip") as archive:
            names = archive.namelist()
            self.assertEqual(len([n for n in names if n.endswith("/SKILL.md")]), 5)
            self.assertFalse(any("parent-review" in n or n.startswith(("profiles/", "library/", "notes/", ".git/")) for n in names))
            binding = json.loads(archive.read("BINDING.template.json"))
            self.assertEqual(binding["delivery_level"], "ADULT_VALIDATION_ONLY")
            self.assertEqual(binding["child_id"], "test-a")
            catalog = json.loads(archive.read("materials/catalog.v3.json"))
            self.assertEqual(len(catalog["records"]), 147)
            self.assertNotIn("interest_hook", str(catalog))
        with zipfile.ZipFile(output / "parent-tools.zip") as archive:
            self.assertIn("skills/parent-review/SKILL.md", archive.namelist())
            self.assertFalse(any("homework-help" in n for n in archive.namelist()))

    def test_reproducible_archives_and_hash_manifest(self):
        first, second = Path(self.temp.name) / "first", Path(self.temp.name) / "second"
        build_release(ROOT, first, "test-a")
        build_release(ROOT, second, "test-a")
        manifest = json.loads((first / "release.json").read_text())
        for name, checksum in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((first / name).read_bytes()).hexdigest(), checksum)
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

    def test_extracted_runtime_can_run_cli_checks_without_original_checkout(self):
        output = Path(self.temp.name) / "release"
        build_release(ROOT, output, "test-a")
        extracted = Path(self.temp.name) / "extracted"
        with zipfile.ZipFile(output / "runtime-source.zip") as archive:
            self.assertIn("tests/test_cli.py", archive.namelist())
            archive.extractall(extracted)
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_cli.py", "-q"], cwd=extracted, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
