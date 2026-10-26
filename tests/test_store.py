import concurrent.futures
import tempfile
import unittest
from pathlib import Path

try:
    from companion.store import Store
    from companion.errors import CompanionError
except ImportError:
    Store = None
    CompanionError = Exception


def session(**changes):
    data = {"task_id": "task-1", "interaction_intent": "homework",
            "homework_status": "in_progress", "pause_point": "画了两条等长线段",
            "source_kind": "observed_in_session"}
    return data | changes


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Store, "尚未实现固定身份持久化工具")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "student-a"
        self.store = Store.initialize(self.root, "test-a", {"nickname": "小松", "grade": 5})

    def test_saved_state_survives_new_process_connection(self):
        receipt = self.store.put("session", "current", session(), "op-1", 0, True)
        reopened = Store(self.root, "test-a")
        self.assertEqual(reopened.read("session", "current")["data"]["pause_point"], "画了两条等长线段")
        self.assertEqual(receipt["revision"], 1)

    def test_binding_cannot_be_changed_by_payload_or_reopen(self):
        with self.assertRaises(CompanionError):
            Store(self.root, "test-b")
        with self.assertRaises(CompanionError):
            self.store.put("session", "current", session(child_id="test-b"), "op-2", 0, True)
        self.assertIsNone(self.store.read("session", "current"))

    def test_retry_has_one_write_and_conflicting_reuse_fails(self):
        first = self.store.put("session", "current", session(), "retry-1", 0, True)
        retry = self.store.put("session", "current", session(), "retry-1", 0, True)
        self.assertTrue(retry["replayed"])
        self.assertEqual(first["sequence"], retry["sequence"])
        with self.assertRaises(CompanionError):
            self.store.put("session", "current", session(pause_point="别的状态"), "retry-1", 0, True)

    def test_stale_update_does_not_overwrite_new_state(self):
        self.store.put("session", "current", session(), "write-1", 0, True)
        self.store.put("session", "current", session(pause_point="已画出四等份"), "write-2", 1, True)
        with self.assertRaises(CompanionError):
            self.store.put("session", "current", session(pause_point="旧内容"), "write-3", 1, True)
        self.assertEqual(self.store.read("session", "current")["revision"], 2)

    def test_concurrent_creates_have_one_winner(self):
        def write(index):
            try:
                return self.store.put("session", "current", session(), f"concurrent-{index}", 0, True)["ok"]
            except CompanionError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(write, range(2)))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(self.store.read("session", "current")["revision"], 1)

    def test_uncertain_speaker_cannot_write_or_read_personal_context(self):
        self.store.put("session", "current", session(), "visible", 0, True)
        with self.assertRaises(CompanionError):
            self.store.put("session", "current", session(), "uncertain", 1, False)
        context = self.store.context(False)
        self.assertEqual(context["attribution"], "unconfirmed")
        self.assertNotIn("profile", context)
        self.assertNotIn("画了", str(context))

    def test_unknown_fields_and_invalid_values_leave_no_state(self):
        for data in (session(raw_chat="不能保存的整段聊天"), session(homework_status="verified_complete"), session(pause_point="x" * 401)):
            with self.subTest(data=data):
                with self.assertRaises(CompanionError):
                    self.store.put("session", "current", data, "bad-input", 0, True)
        self.assertIsNone(self.store.read("session", "current"))

    def test_chat_switch_preserves_unfinished_homework_and_pause(self):
        self.store.put("session", "current", session(), "start", 0, True)
        with self.assertRaises(CompanionError):
            self.store.put("session", "current", session(interaction_intent="chat"), "bad-switch", 1, True)
        self.store.put("session", "current", session(interaction_intent="chat", homework_status="paused"), "switch", 1, True)
        state = self.store.context(True)
        self.assertEqual(state["session"]["data"]["homework_status"], "paused")
        self.assertEqual(state["events"], [])

    def test_symlinked_database_is_rejected(self):
        target = Path(self.temp.name) / "other.sqlite3"
        database = self.root / "state.sqlite3"
        database.rename(target)
        try:
            database.symlink_to(target)
        except OSError:
            self.skipTest("当前系统不允许创建测试软链接")
        with self.assertRaises(CompanionError):
            Store(self.root, "test-a")


if __name__ == "__main__":
    unittest.main()
