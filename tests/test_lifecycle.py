import copy
import json
import tempfile
import unittest
from pathlib import Path

from companion.errors import CompanionError
from companion.store import Store
from test_store import session


def event(**changes):
    return {"task_id": "task-1", "concept_tags": ["fractions-equivalence"],
            "attempt_kind": "drew_model", "attempt_summary": "用等长线段表示分数",
            "assistance": ["representation"], "performance": "partial",
            "independence_evidence": "assisted", "source_kind": "observed_in_session",
            "verification": ["model_checked"]} | changes


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store.initialize(self.root / "a", "test-a", {"nickname": "小松", "grade": 5})
        for method in ("backup", "deletion_registry", "restore", "remove", "correct_event", "consume_followup"):
            self.assertTrue(hasattr(self.store, method), f"尚未实现 {method}")
        self.store.put("session", "current", session(), "start", 0, True)

    def test_visible_evidence_is_distinct_from_child_self_report(self):
        self.store.put("learning_event", "event-1", event(), "observe", 0, True)
        self.store.put("learning_event", "event-2", event(attempt_kind="self_report", attempt_summary="孩子说我会了", assistance=[], performance="not_observed", independence_evidence="child_reported_unaided", source_kind="child_reported", verification=["child_reported"]), "self-report", 0, True)
        self.assertEqual(len(self.store.context(True)["events"]), 2)
        with self.assertRaises(CompanionError):
            self.store.put("learning_event", "event-3", event(independence_evidence="visible_new_attempt_without_session_hint"), "inflate", 0, True)

    def test_no_attempt_or_foreign_task_cannot_become_observed_evidence(self):
        for data in (event(attempt_kind="no_attempt"), event(task_id="nonexistent"), event(source_kind="child_reported", performance="correct")):
            with self.subTest(data=data), self.assertRaises(CompanionError):
                self.store.put("learning_event", "event-bad", data, "bad", 0, True)

    def test_same_task_prior_help_prevents_claiming_unhinted_independence(self):
        self.store.put("learning_event", "event-1", event(), "first-help", 0, True)
        with self.assertRaises(CompanionError):
            self.store.put("learning_event", "event-2", event(assistance=[], performance="correct", independence_evidence="visible_new_attempt_without_session_hint"), "false-unaided", 0, True)

    def test_household_shared_book_has_independent_reading_state(self):
        other = Store.initialize(self.root / "b", "test-b", {"nickname": "小禾", "grade": 3})
        data = {"book_ref": "shared-book", "reading_state": "reading", "source_kind": "child_reported", "position": "第三页"}
        self.store.put("book", "shared-book", data, "read-a", 0, True)
        self.assertEqual(other.context(True)["books"], [])
        other.put("book", "shared-book", data | {"reading_state": "want_to_try", "position": ""}, "read-b", 0, True)
        self.assertEqual(self.store.read("book", "shared-book")["data"]["reading_state"], "reading")

    def test_followup_is_off_by_default_and_consumed_once(self):
        self.assertFalse(self.store.consume_followup("shared-book", "no-reminder", True)["should_ask"])
        self.store.put("followup", "shared-book", {"book_ref": "shared-book", "state": "once_pending", "child_opt_in": True, "source_kind": "child_reported"}, "opt-in", 0, True)
        self.assertTrue(self.store.consume_followup("shared-book", "ask-once", True)["should_ask"])
        self.assertFalse(self.store.consume_followup("shared-book", "ask-once", True)["should_ask"])
        self.assertFalse(self.store.consume_followup("shared-book", "ask-again", True)["should_ask"])

    def test_optional_memory_requires_opt_in(self):
        data = {"category": "preference", "content": "喜欢纸飞机设计", "source_kind": "child_reported", "child_opt_in": False}
        with self.assertRaises(CompanionError):
            self.store.put("memory", "preference-1", data, "unasked", 0, True)
        self.store.put("memory", "preference-1", data | {"child_opt_in": True}, "asked", 0, True)
        self.assertEqual(len(self.store.context(True)["memories"]), 1)

    def test_forgetting_removes_content_from_database_and_exports(self):
        secret = "测试用可清除偏好内容六七八九"
        self.store.put("memory", "memory-1", {"category": "preference", "content": secret, "source_kind": "child_reported", "child_opt_in": True}, "remember", 0, True)
        self.store.remove("memory", "memory-1", "forget", 1, True)
        self.assertIsNone(self.store.read("memory", "memory-1"))
        self.assertNotIn(secret, json.dumps(self.store.backup(), ensure_ascii=False))
        self.assertNotIn(secret.encode(), (self.root / "a" / "state.sqlite3").read_bytes())
        with self.assertRaises(CompanionError):
            self.store.put("memory", "memory-1", {"category": "preference", "content": secret, "source_kind": "child_reported", "child_opt_in": True}, "resurrect", 0, True)

    def test_correction_retracts_old_evidence_atomically(self):
        self.store.put("learning_event", "event-1", event(), "original", 0, True)
        with self.assertRaises(CompanionError):
            self.store.correct_event("event-1", "event-2", event(performance="fictional"), "bad-correction", 1, True)
        self.assertIsNotNone(self.store.read("learning_event", "event-1"))
        self.store.correct_event("event-1", "event-2", event(performance="ambiguous", attempt_summary="原识别有误，不作能力推断"), "correction", 1, True)
        self.assertIsNone(self.store.read("learning_event", "event-1"))
        self.assertEqual([x["id"] for x in self.store.context(True)["events"]], ["event-2"])

    def test_restore_old_backup_requires_current_deletions_and_preserves_new_state(self):
        self.store.put("learning_event", "event-1", event(), "original", 0, True)
        old = self.store.backup()
        self.store.remove("learning_event", "event-1", "withdraw", 1, True, mode="retract")
        self.store.put("session", "current", session(pause_point="新的有效暂停点"), "new-state", 1, True)
        current_registry = self.store.deletion_registry()
        self.store.restore(old, current_registry, "restore-1", registry_is_current=True)
        self.assertIsNone(self.store.read("learning_event", "event-1"))
        self.assertEqual(self.store.read("session", "current")["data"]["pause_point"], "新的有效暂停点")
        fresh = Store.initialize(self.root / "fresh", "test-a", {"nickname": "小松", "grade": 5})
        with self.assertRaises(CompanionError):
            fresh.restore(old, None, "unsafe-restore")
        fresh.restore(old, current_registry, "safe-restore", registry_is_current=True)
        self.assertIsNone(fresh.read("learning_event", "event-1"))

    def test_backup_of_other_child_or_tampered_package_is_rejected(self):
        other = Store.initialize(self.root / "b", "test-b", {"nickname": "小禾", "grade": 3})
        with self.assertRaises(CompanionError):
            other.restore(self.store.backup(), self.store.deletion_registry(), "cross-child", registry_is_current=True)
        damaged = copy.deepcopy(self.store.backup())
        damaged["payload"]["child_id"] = "test-b"
        with self.assertRaises(CompanionError):
            self.store.restore(damaged, self.store.deletion_registry(), "damaged", registry_is_current=True)

    def test_switching_task_keeps_previous_unfinished_pause(self):
        self.store.put("session", "current", session(task_id="task-2", pause_point="另一道题", homework_status="in_progress"), "new-task", 1, True)
        pending = self.store.context(True)["pending_tasks"]
        self.assertEqual(pending[0]["data"]["task_id"], "task-1")
        self.assertEqual(pending[0]["data"]["homework_status"], "paused")


if __name__ == "__main__":
    unittest.main()
