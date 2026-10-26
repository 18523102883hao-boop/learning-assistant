import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from companion.errors import CompanionError
from companion.store import Store
from test_lifecycle import event
from test_store import session


class RetentionRequestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store.initialize(self.root / "a", "test-a", {"nickname": "小松", "grade": 5})

    def test_expired_evidence_is_erased_and_does_not_return_from_backup(self):
        self.assertTrue(hasattr(self.store, "prune"), "缺少已批准的90天保留清理")
        with patch("companion.store.now_utc", return_value="2026-01-01T00:00:00+00:00"):
            self.store.put("session", "current", session(), "start", 0, True)
            self.store.put("learning_event", "event-1", event(), "observe", 0, True)
            self.store.put("memory", "memory-1", {"category": "preference", "content": "过期测试偏好", "source_kind": "child_reported", "child_opt_in": True}, "remember", 0, True)
        backup = self.store.backup()
        self.store.prune("expiry-run", reference_time=datetime(2026, 10, 27, tzinfo=timezone.utc))
        self.assertIsNone(self.store.read("memory", "memory-1"))
        self.assertIsNone(self.store.read("learning_event", "event-1"))
        self.store.restore(backup, self.store.deletion_registry(), "restore-expired", registry_is_current=True)
        self.assertIsNone(self.store.read("learning_event", "event-1"))

    def test_book_request_is_not_a_purchase_or_reading_completion_or_followup(self):
        data = {"title": "一本关于纸飞机的书", "edition_details": "版本待核", "status": "would_like", "source_kind": "child_reported", "child_opt_in": True, "share_with_parent": False}
        self.store.put("book_request", "wish-1", data, "wish", 0, True)
        context = self.store.context(True)
        self.assertEqual(context["requests"][0]["data"]["status"], "would_like")
        self.assertEqual(context["books"], [])
        self.assertEqual(context["followups"], [])
        with self.assertRaises(CompanionError):
            self.store.put("book_request", "wish-2", data | {"status": "ordered"}, "pretend-order", 0, True)


if __name__ == "__main__":
    unittest.main()
