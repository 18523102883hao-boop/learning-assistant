import tempfile
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import closing

from companion.errors import CompanionError
from companion.store import Store
from test_lifecycle import event
from test_store import session


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store.initialize(self.root / "a", "test-a", {"nickname": "小松", "grade": 5})
        self.store.put("session", "current", session(), "start", 0, True)

    def test_event_cannot_be_overwritten_or_superseded_outside_correction(self):
        self.store.put("learning_event", "event-1", event(), "observe", 0, True)
        with self.assertRaises(CompanionError):
            self.store.put("learning_event", "event-1", event(assistance=[], independence_evidence="not_assessed"), "erase-help", 1, True)
        with self.assertRaises(CompanionError):
            self.store.put("learning_event", "event-2", event(supersedes="event-1"), "fake-correction", 0, True)

    def test_completed_task_does_not_reappear_on_live_or_fresh_restore(self):
        self.store.put("session", "current", session(task_id="task-2"), "switch-b", 1, True)
        backup = self.store.backup()
        self.store.put("session", "current", session(homework_status="reported_complete"), "complete-a", 2, True)
        self.store.put("session", "current", session(task_id="task-2"), "resume-b", 3, True)
        registry = self.store.deletion_registry()
        self.store.restore(backup, registry, "restore-live", registry_is_current=True)
        self.assertEqual(self.store.context(True)["pending_tasks"], [])
        fresh = Store.initialize(self.root / "fresh", "test-a", {"nickname": "小松", "grade": 5})
        fresh.restore(backup, registry, "restore-fresh", registry_is_current=True)
        self.assertEqual(fresh.context(True)["pending_tasks"], [])

    def test_forget_current_task_does_not_block_new_task_or_resurrect_old(self):
        self.store.put("learning_event", "event-1", event(), "observe", 0, True)
        backup = self.store.backup()
        self.store.remove("session", "current", "forget-task", 1, True)
        self.assertIsNone(self.store.read("learning_event", "event-1"))
        self.store.put("session", "current", session(task_id="task-2"), "new-start", 0, True)
        self.store.restore(backup, self.store.deletion_registry(), "restore-old", registry_is_current=True)
        self.assertEqual(self.store.context(True)["session"]["data"]["task_id"], "task-2")
        self.assertEqual(self.store.context(True)["pending_tasks"], [])
        self.assertIsNone(self.store.read("learning_event", "event-1"))

    def test_invalid_source_and_correction_types_raise_structured_errors(self):
        for source in ([], {}, True, None):
            with self.subTest(source=source), self.assertRaises(CompanionError):
                self.store.put("learning_event", "event-1", event(source_kind=source), "bad-source", 0, True)
        for data in (None, [], "text"):
            with self.subTest(data=data), self.assertRaises(CompanionError):
                self.store.correct_event("event-1", "event-2", data, "bad-correction", 1, True)

    def test_family_notice_is_clock_based_and_once_per_local_date(self):
        self.assertTrue(hasattr(self.store, "family_notice"), "缺少可核验的软提醒去重")
        with patch("companion.store.now_utc", return_value="2026-10-27T14:00:00+00:00"):
            first = self.store.family_notice("outside_window", "notice-1", True)
            self.assertTrue(first["should_remind"])
            self.assertFalse(self.store.family_notice("outside_window", "notice-1", True)["should_remind"])
            self.assertFalse(self.store.family_notice("outside_window", "notice-2", True)["should_remind"])
        with patch("companion.store.now_utc", return_value="2026-10-28T01:00:00+00:00"):
            self.assertFalse(self.store.family_notice("outside_window", "notice-3", True)["should_remind"])
        with patch("companion.store.now_utc", return_value="2026-10-28T14:00:00+00:00"):
            self.assertTrue(self.store.family_notice("outside_window", "notice-4", True)["should_remind"])

    def test_whole_task_forget_checks_current_sequence(self):
        self.assertTrue(hasattr(self.store, "forget_task"), "缺少任务范围清除")
        self.store.put("learning_event", "event-1", event(), "observe", 0, True)
        with self.assertRaises(CompanionError):
            self.store.forget_task("task-1", "stale-forget", 1, True)
        self.store.forget_task("task-1", "forget", 2, True)
        self.assertIsNone(self.store.context(True)["session"])
        self.assertIsNone(self.store.read("learning_event", "event-1"))

    def test_legacy_storage_is_rejected_until_explicit_non_destructive_migration(self):
        database = self.root / "a" / "state.sqlite3"
        with closing(sqlite3.connect(database)) as connection, connection:
            connection.execute("PRAGMA user_version=3")
            connection.execute("DROP TABLE closed_tasks")
            if "sequence" in {row[1] for row in connection.execute("PRAGMA table_info(records)")}:
                connection.execute("ALTER TABLE records DROP COLUMN sequence")
        with self.assertRaises(CompanionError) as caught:
            Store(self.root / "a", "test-a")
        self.assertEqual(caught.exception.code, "schema_mismatch")
        self.assertTrue(hasattr(Store, "migrate"), "缺少旧物理格式迁移")
        Store.migrate(self.root / "a", "test-a")
        reopened = Store(self.root / "a", "test-a")
        self.assertEqual(reopened.context(True)["session"]["data"]["pause_point"], session()["pause_point"])
        self.assertEqual(reopened.backup()["payload"]["schema_version"], 3)

    def test_legacy_completed_state_is_included_in_current_recovery_registry(self):
        self.store.put("session", "current", session(homework_status="reported_complete"), "done", 1, True)
        with closing(sqlite3.connect(self.root / "a" / "state.sqlite3")) as connection, connection:
            connection.execute("PRAGMA user_version=3")
            connection.execute("DROP TABLE closed_tasks")
            connection.execute("ALTER TABLE records DROP COLUMN sequence")
        Store.migrate(self.root / "a", "test-a")
        reopened = Store(self.root / "a", "test-a")
        self.assertIn("task-1", reopened.deletion_registry()["payload"]["closed_tasks"])


if __name__ == "__main__":
    unittest.main()
