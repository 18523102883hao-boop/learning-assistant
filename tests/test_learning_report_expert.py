import json
import importlib.util
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch
from copy import deepcopy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "workbuddy/experts/learning-report-analyst"

class ReportPackageTests(unittest.TestCase):
    def test_manifest_and_report_reference_are_portable(self):
        manifest = json.loads((ROOT / ".codebuddy-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIsInstance(manifest["homepage"], str)
        self.assertEqual(manifest["defaultInitPrompt"], manifest["quickPrompts"][0])
        self.assertTrue(40 <= len(manifest["displayDescription"]["zh"]) <= 50)
        for agent in manifest["agents"]:
            self.assertTrue((ROOT / agent).is_file(), agent)
        for skill in manifest["skills"]:
            self.assertTrue((ROOT / skill / "SKILL.md").is_file(), skill)
        self.assertTrue((ROOT / "skills/weekly-notes/references/weekly-notes-template.md").is_file())

    def load_validator(self):
        path = ROOT / "skills/weekly-notes/scripts/validate_input.py"
        self.assertTrue(path.is_file(), "原生 Skill 缺少真实输入校验脚本")
        spec = importlib.util.spec_from_file_location("journal_input_validator", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def shared_input(self):
        return {"schema_version": "shared-moments/1", "child_id": "test-a",
                "period": {"start": "2026-10-20", "end": "2026-10-26", "timezone": "Asia/Shanghai"},
                "source": {"source_id": "manual-demo", "revision": 1, "current_confirmed": True},
                "moments": [{"moment_id": "moment-1", "at": "2026-10-25T11:00:00+00:00", "kind": "creation",
                             "summary": "孩子愿意分享她给虚构漫画角色换了一个结局。", "source_kind": "child_shared", "share_with_parent": True}]}

    def test_shared_moments_accepts_only_explicit_shareable_current_input(self):
        module = self.load_validator()
        valid = self.shared_input()
        result = module.validate_input(valid)
        self.assertEqual(result["input_kind"], "shared-moments/1")
        self.assertEqual(result["data"]["moments"][0]["moment_id"], "moment-1")
        for update in ({"share_with_parent": False}, {"share_with_parent": "true"}, {"at": "2026-11-01T11:00:00+00:00"}, {"raw_chat": "不应进入手记的私聊"}):
            invalid = deepcopy(valid)
            invalid["moments"][0].update(update)
            with self.subTest(update=update), self.assertRaises(module.InputError):
                module.validate_input(invalid)
        invalid = deepcopy(valid)
        invalid["moments"].append(deepcopy(invalid["moments"][0]))
        with self.assertRaises(module.InputError):
            module.validate_input(invalid)
        invalid = deepcopy(valid)
        invalid["source"]["current_confirmed"] = False
        with self.assertRaises(module.InputError):
            module.validate_input(invalid)

    def test_input_validator_cli_handles_utf8_and_never_writes_a_report(self):
        self.load_validator()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "selected.json"
            path.write_text(json.dumps(self.shared_input(), ensure_ascii=False), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "skills/weekly-notes/scripts/validate_input.py"), "--input", str(path)], capture_output=True, text=True, encoding="utf-8", timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])
            self.assertEqual(sorted(p.name for p in Path(temporary).iterdir()), ["selected.json"])

    def test_duplicate_json_share_field_is_rejected_without_a_report(self):
        self.load_validator()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ambiguous.json"
            payload = json.dumps(self.shared_input(), ensure_ascii=False).replace('"share_with_parent": true', '"share_with_parent": false, "share_with_parent": true')
            path.write_text(payload, encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "skills/weekly-notes/scripts/validate_input.py"), "--input", str(path)], capture_output=True, text=True, encoding="utf-8", timeout=10)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["error"], "invalid_input")

    def test_v3_guards_remain_safe_with_an_older_installed_validator(self):
        module = self.load_validator()
        package = types.ModuleType("companion")
        package.__path__ = []
        errors = types.ModuleType("companion.errors")
        errors.CompanionError = ValueError
        reports = types.ModuleType("companion.reports")
        reports.validate_export = lambda value: None
        source = {"schema_version": 3, "rule_version": "v3.2026-10-27", "child_id": "test-a", "source_store_id": "store-test", "source_sequence": 3,
                  "period": self.shared_input()["period"], "events": [{"event_id": "event-1", "task_id": "task-1", "observed_at": "2026-10-25T11:00:00+00:00", "write_sequence": 3,
                  "concept_labels": ["应用题数量关系"], "attempt_kind": "identified_condition", "assistance": [], "performance": "correct", "independence_evidence": "not_assessed", "source_kind": "observed_in_session", "verification": ["not_checked"]}]}
        with patch.dict(sys.modules, {"companion": package, "companion.errors": errors, "companion.reports": reports}):
            normalized = module.validate_input(source)
            self.assertEqual(normalized["data"]["events"][0]["performance"], "ambiguous")
            self.assertEqual(source["events"][0]["performance"], "correct", "不得修改来源对象")
            invalid = deepcopy(source)
            invalid["events"][0].update(source_kind="child_reported", attempt_kind="self_report", independence_evidence="visible_new_attempt_without_session_hint", assistance=["hint"])
            with self.assertRaises(module.InputError):
                module.validate_input(invalid)

    def test_report_uses_actual_minimal_export_and_excludes_raw_logs(self):
        agent = (ROOT / "agents/learning-report-analyst.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/weekly-notes/SKILL.md").read_text(encoding="utf-8")
        combined = agent + skill
        for field in ("schema_version", "source_store_id", "source_sequence", "source_kind", "verification", "supersedes"):
            self.assertIn(field, combined)
        self.assertNotIn("一个孩子的学习事件文件（jsonl）", combined)
        self.assertNotIn("场景分布行", combined)
        self.assertIn("原始私聊", combined)
        self.assertIn("成功回执", combined)

if __name__ == "__main__":
    unittest.main()
