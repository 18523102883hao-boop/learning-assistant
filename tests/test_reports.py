import json
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from companion.store import Store
from companion.errors import CompanionError
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

    def test_export_metadata_types_and_sequence_are_validated(self):
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        for field, value in (("source_store_id", []), ("source_store_id", ""), ("rule_version", None), ("rule_version", ""), ("source_sequence", -1)):
            with self.subTest(field=field, value=value):
                invalid = deepcopy(exported)
                invalid[field] = value
                with self.assertRaises(CompanionError):
                    render_report(invalid)

    def test_export_event_must_belong_to_period_and_source_sequence(self):
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        for timestamp in ("2026-10-25T15:59:59+00:00", "2026-11-01T16:00:00+00:00"):
            with self.subTest(timestamp=timestamp):
                invalid = deepcopy(exported)
                invalid["events"][0]["observed_at"] = timestamp
                with self.assertRaises(CompanionError):
                    render_report(invalid)
        invalid = deepcopy(exported)
        invalid["events"][0]["write_sequence"] = invalid["source_sequence"] + 1
        with self.assertRaises(CompanionError):
            render_report(invalid)

    def test_duplicate_export_event_is_rejected(self):
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        exported["events"].append(deepcopy(exported["events"][0]))
        with self.assertRaises(CompanionError):
            render_report(exported)

    def test_export_rejects_contradictory_source_help_and_independence(self):
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        contradictions = [
            {"source_kind": "child_reported", "attempt_kind": "self_report", "performance": "correct"},
            {"independence_evidence": "visible_new_attempt_without_session_hint", "assistance": ["hint"]},
            {"source_kind": "observed_in_session", "attempt_kind": "self_report"},
        ]
        for update in contradictions:
            invalid = deepcopy(exported)
            invalid["events"][0].update(update)
            with self.subTest(update=update), self.assertRaises(CompanionError):
                render_report(invalid)

    def test_legacy_unchecked_performance_never_becomes_verified_fact(self):
        for index, (performance, verification) in enumerate((p, v) for p in ("correct", "incorrect") for v in ([], ["not_checked"], ["child_reported"], ["model_checked", "not_checked"])):
            with self.subTest(performance=performance, verification=verification):
                store = Store.initialize(Path(self.temp.name) / f"legacy-{index}", "test-a", {"nickname": "小松", "grade": 5})
                store.put("session", "current", session(), "start", 0, True)
                store.put("learning_event", "event-weak", event(performance=performance, verification=verification), "attempt", 0, True)
                report = render_report(parent_export(store.backup(), "2026-10-26", "2026-11-01"))
                self.assertNotIn("经所列方式核对为正确", report["markdown"])
                self.assertNotIn("本次尝试仍有错误", report["markdown"])
                self.assertIn("不能判断正误", report["markdown"])

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
        legacy_metadata = first["metadata"] | {}
        legacy_metadata.pop("report_format_version", None)
        self.assertFalse(report_is_current(self.store.backup(), legacy_metadata))
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

    def test_latest_outcome_uses_real_record_order_even_with_reversed_ids_same_second(self):
        with patch("companion.store.now_utc", return_value="2026-10-27T08:05:00+00:00"):
            self.store.put("learning_event", "event-z", event(performance="partial"), "earlier", 0, True)
            self.store.put("learning_event", "event-a", event(performance="correct"), "later", 0, True)
        exported = parent_export(self.store.backup(), "2026-10-26", "2026-11-01")
        self.assertEqual(exported["events"][-1]["event_id"], "event-a")
        self.assertIn("本次尝试经所列方式核对为正确", render_report(exported)["markdown"])


if __name__ == "__main__":
    unittest.main()
