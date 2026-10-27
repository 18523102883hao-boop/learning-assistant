import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_store import session

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "companion" / "__main__.py").exists(), "尚未实现命令行闭环")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "student"
        result = self.run_cli("init", "--nickname", "小松", "--grade", "5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def run_cli(self, command, *args, payload=None, env=None):
        return subprocess.run([sys.executable, "-m", "companion", command, "--root", str(self.root), "--child", "test-a", *args], input=json.dumps(payload, ensure_ascii=False) if payload is not None else "", capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT, timeout=20)

    def test_utf8_json_round_trip_with_inherited_ascii_stdio(self):
        environment = os.environ | {"PYTHONIOENCODING": "ascii"}
        save = self.run_cli("put", "--kind", "session", "--id", "current", "--op", "utf8-save", "--expect", "0", "--speaker-confirmed", payload=session(), env=environment)
        self.assertEqual(save.returncode, 0, save.stdout + save.stderr)
        resumed = self.run_cli("context", "--speaker-confirmed", env=environment)
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)["session"]["data"]["pause_point"], session()["pause_point"])

    def test_separate_processes_save_resume_and_safe_error(self):
        save = self.run_cli("put", "--kind", "session", "--id", "current", "--op", "save-1", "--expect", "0", "--speaker-confirmed", payload=session())
        self.assertEqual(save.returncode, 0, save.stdout + save.stderr)
        resumed = json.loads(self.run_cli("context", "--speaker-confirmed").stdout)
        self.assertEqual(resumed["session"]["data"]["pause_point"], session()["pause_point"])
        bad = self.run_cli("put", "--kind", "session", "--id", "current", "--op", "bad-1", "--expect", "0", "--speaker-confirmed", payload=session())
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(json.loads(bad.stdout)["error"], "revision_conflict")
        self.assertNotIn("Traceback", bad.stderr)

    def test_backup_files_require_private_output_and_restore_requires_registry(self):
        out = Path(self.temp.name) / "parent" / "backup.json"
        backup = self.run_cli("backup", "--output", str(out))
        self.assertEqual(backup.returncode, 0, backup.stdout + backup.stderr)
        self.assertTrue(out.is_file())
        invalid = self.run_cli("backup", "--output", str(self.root / "parent-report.json"))
        self.assertNotEqual(invalid.returncode, 0)
        self.assertFalse((self.root / "parent-report.json").exists())

    def test_repository_cannot_be_runtime_data_root(self):
        original = self.root
        self.root = ROOT / ".runtime" / "forbidden-test"
        result = self.run_cli("init", "--nickname", "测试", "--grade", "3")
        self.root = original
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((ROOT / ".runtime" / "forbidden-test").exists())

    def test_parent_report_is_markdown_with_checkable_metadata(self):
        output = Path(self.temp.name) / "parent" / "week.md"
        result = self.run_cli("report", "--start", "2026-10-26", "--end", "2026-11-01", "--output", str(output))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(output.read_text(encoding="utf-8").startswith("# "), "周报应直接是 Markdown 文档，不是转义在 JSON 中")
        status = self.run_cli("report-status", "--metadata", str(output))
        self.assertEqual(status.returncode, 0, status.stdout)
        self.assertTrue(json.loads(status.stdout)["current"])


if __name__ == "__main__":
    unittest.main()
