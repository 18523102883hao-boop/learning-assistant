"""Optional real deployment check. All writes use disposable synthetic child stores."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "workbuddy/experts/learning-partner"


@unittest.skipUnless(os.environ.get("YIYI_TEST_RUNTIME"), "需指定已安装运行时，验证真实 stdio 启动器")
class YiyiStdioDeploymentTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_launcher_persistence_followup_correction_forgetting_and_identity(self):
        from contextlib import asynccontextmanager
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from companion.store import Store

        runtime = Path(os.environ["YIYI_TEST_RUNTIME"]).resolve()
        python = runtime / ".venv/bin/python"
        launcher = PACKAGE / "scripts/start_learning_records.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            binding_path = home / ".workbuddy/learning-companion/bindings/learning-partner-yiyi.json"
            binding_path.parent.mkdir(parents=True)
            data = root / "student-b"
            Store.initialize(data, "student-b", {"nickname": "小禾", "grade": 3})
            other = root / "student-a"
            Store.initialize(other, "student-a", {"nickname": "小松", "grade": 5})
            binding = {"schema_version": 1, "child_id": "student-b", "runtime_root": str(runtime), "python": str(python), "data_root": str(data), "materials": str(runtime / "materials/catalog.v3.json")}

            def write_binding(value):
                binding_path.write_text(json.dumps(value))
                binding_path.chmod(0o600)

            write_binding(binding)
            parameters = StdioServerParameters(command=str(python), args=[str(launcher)], env={"HOME": str(home)})

            @asynccontextmanager
            async def connected():
                async with stdio_client(parameters) as (reader, writer):
                    async with ClientSession(reader, writer) as client:
                        await client.initialize()

                        async def call(name, args):
                            result = await client.call_tool(name, args)
                            self.assertFalse(result.isError, result.content)
                            return result.structuredContent or json.loads(result.content[0].text)

                        yield client, call

            state = {"task_id": "task-demo", "interaction_intent": "homework", "homework_status": "in_progress", "pause_point": "虚构题中正在画分组图", "source_kind": "observed_in_session"}
            event = {"task_id": "task-demo", "concept_tags": ["multiplication-groups"], "attempt_kind": "drew_model", "attempt_summary": "虚构的分组图尝试", "assistance": ["representation"], "performance": "partial", "independence_evidence": "assisted", "source_kind": "observed_in_session", "verification": ["model_checked"]}
            async with connected() as (client, call):
                tools = (await client.list_tools()).tools
                self.assertEqual({t.name for t in tools}, {"companion_context", "save_learning_record", "forget_learning_record", "correct_learning_event", "consume_reading_followup", "forget_learning_task", "family_time_notice", "reading_materials"})
                for tool in tools:
                    self.assertTrue({"child_id", "root", "path"}.isdisjoint(tool.inputSchema["properties"]))
                self.assertNotIn("profile", await call("companion_context", {}))
                self.assertEqual((await call("companion_context", {"speaker_confirmed": True}))["child_id"], "student-b")
                args = {"kind": "session", "record_id": "current", "data": state, "operation_id": "save-demo", "expected_revision": 0, "speaker_confirmed": True}
                self.assertTrue((await call("save_learning_record", args))["ok"])
                self.assertTrue((await call("save_learning_record", args))["replayed"])
                self.assertFalse((await call("save_learning_record", args | {"operation_id": "cross-demo", "data": state | {"child_id": "student-a"}}))["ok"])
                self.assertTrue((await call("save_learning_record", args | {"kind": "learning_event", "record_id": "event-demo", "data": event, "operation_id": "event-demo"}))["ok"])
                followup = {"book_ref": "fictional-book", "state": "once_pending", "child_opt_in": True, "source_kind": "child_reported"}
                self.assertTrue((await call("save_learning_record", args | {"kind": "followup", "record_id": "fictional-book", "data": followup, "operation_id": "opt-demo"}))["ok"])
                ask = {"book_ref": "fictional-book", "operation_id": "ask-demo", "speaker_confirmed": True}
                self.assertTrue((await call("consume_reading_followup", ask))["should_ask"])
                self.assertFalse((await call("consume_reading_followup", ask))["should_ask"])
            async with connected() as (_, call):
                context = await call("companion_context", {"speaker_confirmed": True})
                self.assertEqual(context["session"]["data"], state)
                self.assertEqual(len(context["events"]), 1)
                self.assertFalse((await call("consume_reading_followup", ask | {"operation_id": "ask-new-process"}))["should_ask"])
                self.assertTrue((await call("correct_learning_event", {"old_id": "event-demo", "new_id": "event-corrected", "data": event | {"performance": "ambiguous"}, "operation_id": "correct-demo", "expected_revision": 1, "speaker_confirmed": True}))["ok"])
                context = await call("companion_context", {"speaker_confirmed": True})
                self.assertEqual([e["id"] for e in context["events"]], ["event-corrected"])
                self.assertTrue((await call("forget_learning_task", {"task_id": "task-demo", "operation_id": "forget-demo", "expected_sequence": context["sequence"], "speaker_confirmed": True}))["ok"])
            async with connected() as (_, call):
                context = await call("companion_context", {"speaker_confirmed": True})
                self.assertIsNone(context["session"])
                self.assertEqual(context["events"], [])
            self.assertEqual(Store(other, "student-a").context(True)["sequence"], 0)
            write_binding(binding | {"data_root": str(other)})
            result = subprocess.run([str(python), str(launcher)], env=os.environ | {"HOME": str(home)}, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("不打开另一孩子的资料", result.stderr)


if __name__ == "__main__":
    unittest.main()
