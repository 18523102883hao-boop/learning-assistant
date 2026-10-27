import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "workbuddy/experts/learning-report-analyst"

class ReportPackageTests(unittest.TestCase):
    def test_manifest_and_report_reference_are_portable(self):
        manifest = json.loads((ROOT / ".codebuddy-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIsInstance(manifest["homepage"], str)
        for agent in manifest["agents"]:
            self.assertTrue((ROOT / agent).is_file(), agent)
        for skill in manifest["skills"]:
            self.assertTrue((ROOT / skill / "SKILL.md").is_file(), skill)
        self.assertTrue((ROOT / "skills/weekly-report/references/weekly-report-template.md").is_file())

    def test_report_uses_actual_minimal_export_and_excludes_raw_logs(self):
        agent = (ROOT / "agents/learning-report-analyst.md").read_text(encoding="utf-8")
        skill = (ROOT / "skills/weekly-report/SKILL.md").read_text(encoding="utf-8")
        combined = agent + skill
        for field in ("schema_version", "source_store_id", "source_sequence", "source_kind", "verification", "supersedes"):
            self.assertIn(field, combined)
        self.assertNotIn("一个孩子的学习事件文件（jsonl）", combined)
        self.assertNotIn("场景分布行", combined)
        self.assertIn("原始私聊", combined)
        self.assertIn("成功回执", combined)

if __name__ == "__main__":
    unittest.main()
