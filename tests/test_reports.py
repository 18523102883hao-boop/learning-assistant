import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from companion.store import Store
from test_lifecycle import event
from test_store import session

try:
    from companion.reports import parent_export, render_report, report_is_current
except ImportError:
    parent_export = render_report = report_is_current = None


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(parent_export, "尚未实现受控字段家长摘要")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store.initialize(Path(self.temp.name) / "a", "test-a", {"nickname": "小松", "grade": 5})
        with patch("companion.store.now_utc", return_value="2026-10-27T08:00:00+00:00"):
            self.store.put("session", "current", session(), "start", 0, True)
            self.store.put("learning_event", "event-1", event(attempt_summary="这是不会导出的朋友真名和对话原句"), "attempt", 0, True)
            self.store.put("memory", "memory-1", {"category": "preference", "content": "这段普通聊天只留本人空间", "source_kind": "child_reported", "child_opt_in": True}, "remember", 0, True)

    def test_report_uses_only_vetted_labels_and_behavior_not_private_text(self):
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        report = render_report(exported)
        text = json.dumps(report, ensure_ascii=False)
        self.assertIn("等值分数", text)
        for forbidden in ("朋友真名", "普通聊天只留", "attempt_summary", "memory-1", "掌握率", "懒惰"):
            self.assertNotIn(forbidden, text)
        self.assertIn("获得帮助", report["markdown"])

    def test_correction_invalidates_old_report_and_new_report_supersedes(self):
        first = render_report(parent_export(self.store.backup(), "2026-10-26", "2026-11-01"))
        self.assertTrue(report_is_current(self.store.backup(), first["metadata"]))
        self.store.remove("learning_event", "event-1", "retract", 1, True, mode="retract")
        self.assertFalse(report_is_current(self.store.backup(), first["metadata"]))
        updated = render_report(parent_export(self.store.backup(), "2026-10-26", "2026-11-01"), supersedes=first["metadata"]["report_id"])
        self.assertEqual(updated["metadata"]["supersedes"], first["metadata"]["report_id"])
        self.assertNotIn("等值分数", updated["markdown"])
        self.assertIn("证据不足", updated["markdown"])

    def test_unknown_concept_tag_does_not_echo_unreviewed_text_to_parent(self):
        self.store.put("learning_event", "event-2", event(concept_tags=["unreviewed-person-name"]), "unknown-concept", 0, True)
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        self.assertNotIn("unreviewed-person-name", json.dumps(exported))

    def test_time_period_is_china_local_and_does_not_guess_outcomes(self):
        exported = parent_export(self.store.backup(), "2026-10-28", "2026-10-28")
        self.assertEqual(exported["events"], [])
        report = render_report(exported)
        self.assertIn("证据不足", report["markdown"])


if __name__ == "__main__":
    unittest.main()
