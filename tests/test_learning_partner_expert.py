import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "workbuddy/experts/learning-partner"

class PartnerPackageTests(unittest.TestCase):
    def test_manifest_and_referenced_assets_are_portable(self):
        manifest = json.loads((ROOT / ".codebuddy-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIsInstance(manifest["homepage"], str)
        self.assertTrue(40 <= len(manifest["displayDescription"]["zh"]) <= 50)
        for agent in manifest["agents"]:
            self.assertTrue((ROOT / agent).is_file(), agent)
        for skill in manifest["skills"]:
            self.assertTrue((ROOT / skill / "SKILL.md").is_file(), skill)
        self.assertTrue((ROOT / "skills/learning-log/references/record-contract.md").is_file())
        self.assertTrue((ROOT / "skills/reading-companion/references/catalog.v3.json").is_file())

    def test_catalog_has_no_legacy_personal_status(self):
        catalog = json.loads((ROOT / "skills/reading-companion/references/catalog.v3.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["records"]), 147)
        for record in catalog["records"]:
            self.assertTrue({"owner", "status", "transition_level", "interest_hook"}.isdisjoint(record))
            self.assertEqual(record["release_status"], "discover_only")
            self.assertFalse(record["edition_verified"])

    def test_no_unreviewed_reading_card_is_shipped(self):
        refs = ROOT / "skills/reading-companion/references"
        self.assertFalse((refs / "reading-cards/tier1-now.md").exists())
        self.assertFalse((refs / "bookshelf.json").exists())

    def test_prompt_guards_against_unapproved_persistence_and_followup(self):
        agent = (ROOT / "agents/learning-partner.md").read_text(encoding="utf-8")
        log = (ROOT / "skills/learning-log/SKILL.md").read_text(encoding="utf-8")
        reading = (ROOT / "skills/reading-companion/SKILL.md").read_text(encoding="utf-8")
        chat = (ROOT / "skills/partner-chat/SKILL.md").read_text(encoding="utf-8")
        # 记忆策略（2026-10-27 家长决策）：要点默认记、孩子可拒记、诚实说明记的是要点
        self.assertIn("这段别记", agent)
        self.assertIn("不是每一句对话", agent)
        self.assertNotIn("普通聊天默认不保存", agent)
        self.assertIn("不是本人", agent)
        self.assertNotIn("profiles/learning-log-{child_id}.jsonl", log)
        self.assertNotIn("场景计数（一次对话一条）", chat)
        self.assertIn("should_ask=true", reading)
        self.assertIn("once_pending", reading)
        self.assertNotIn("一天 3 页", reading)

if __name__ == "__main__":
    unittest.main()
