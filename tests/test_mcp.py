import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from companion.store import Store
from test_store import session

ROOT = Path(__file__).resolve().parents[1]
if importlib.util.find_spec("mcp"):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client


@unittest.skipUnless(importlib.util.find_spec("mcp"), "需安装 .[mcp] 才能验证真实 stdio 协议")
class MCPTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_fixed_binding_tool_inventory_and_safe_failures(self):
        self.assertTrue((ROOT / "companion" / "mcp_server.py").exists(), "尚未实现有限 MCP 工具")

        with tempfile.TemporaryDirectory() as temp:
            data_root = Path(temp) / "student"
            Store.initialize(data_root, "test-a", {"nickname": "小松", "grade": 5})
            parameters = StdioServerParameters(command=sys.executable, args=["-m", "companion.mcp_server", "--root", str(data_root), "--child", "test-a"], cwd=str(ROOT))
            async with stdio_client(parameters) as (reader, writer):
                async with ClientSession(reader, writer) as client:
                    await client.initialize()
                    tools = (await client.list_tools()).tools
                    names = {tool.name for tool in tools}
                    self.assertEqual(names, {"companion_context", "save_learning_record", "forget_learning_record", "correct_learning_event", "consume_reading_followup", "forget_learning_task", "family_time_notice", "reading_materials"})
                    for tool in tools:
                        self.assertNotIn("root", tool.inputSchema["properties"])
                        self.assertNotIn("child_id", tool.inputSchema["properties"])

                    async def call(name, args):
                        result = await client.call_tool(name, args)
                        self.assertFalse(result.isError, result.content)
                        return result.structuredContent or json.loads(result.content[0].text)

                    anonymous = await call("companion_context", {})
                    self.assertEqual(anonymous["attribution"], "unconfirmed")
                    args = {"kind": "session", "record_id": "current", "data": session(), "operation_id": "mcp-save", "expected_revision": 0, "speaker_confirmed": True}
                    self.assertTrue((await call("save_learning_record", args))["ok"])
                    self.assertEqual((await call("companion_context", {"speaker_confirmed": True}))["child_id"], "test-a")
                    bad = await call("save_learning_record", args | {"operation_id": "mcp-escape", "data": session(child_id="test-b")})
                    self.assertFalse(bad["ok"])
                    provenance = await call("save_learning_record", args | {"operation_id": "mcp-provenance", "data": session(source_kind="adult_verified")})
                    self.assertFalse(provenance["ok"])
                    refused = await call("forget_learning_record", {"kind": "memory", "record_id": "missing", "operation_id": "uncertain-forget", "expected_revision": 0})
                    self.assertFalse(refused["ok"])
                    malformed = await call("save_learning_record", args | {"operation_id": "mcp-malformed", "data": session() | {"verification": None}})
                    self.assertFalse(malformed["ok"])
                    missing_library = await call("reading_materials", {"query": "纸飞机"})
                    self.assertFalse(missing_library["available"])


if __name__ == "__main__":
    unittest.main()
