"""Stdio only. Fixed deployment binding; no filesystem paths, shell or parent tools."""

import argparse
import importlib.metadata
import json
import sys
from typing import Literal

from .cli import outside_repository
from .errors import CompanionError
from .store import Store
from .materials import MaterialLibrary


def create_server(store, materials=None):
    from mcp.server.fastmcp import FastMCP
    from pydantic import StrictBool, StrictInt

    if importlib.metadata.version("mcp") != "1.26.0":
        raise CompanionError("sdk_version_mismatch", "MCP SDK 与验证版本不符，请按项目固定依赖安装后复验")
    server = FastMCP("family-learning-companion", log_level="WARNING")
    library = MaterialLibrary(materials)

    def guarded(action):
        try:
            return action()
        except CompanionError as error:
            return error.as_dict()
        except OSError:
            return {"ok": False, "error": "io_error", "message": "本地资料操作失败；未声明保存/删除完成"}

    def child_data(data):
        if len(json.dumps(data, ensure_ascii=False)) > 16000:
            raise CompanionError("invalid_input", "只接收小型事实候选")
        if "verification" in data and not isinstance(data["verification"], list):
            raise CompanionError("invalid_input", "verification 须为校验方式列表")
        if data.get("source_kind") not in ("observed_in_session", "child_reported") or "adult_checked" in data.get("verification", []):
            raise CompanionError("provenance_not_allowed", "儿童工具不可自行声明成人/外部已核验")
        return data

    @server.tool()
    def reading_materials(query: str, limit: StrictInt = 2) -> dict:
        """只检索已准入的书目候选，最多3条；不代表具体剧情/版本已核验。作业期间不主动调用。当前页可直接陪读。"""
        return guarded(lambda: library.search(query, limit))

    @server.tool()
    def companion_context(speaker_confirmed: StrictBool = False) -> dict:
        """读取当前绑定孩子最小续接信息。非本人或归因不明保持 false，不索要另一人档案。"""
        return guarded(lambda: store.context(speaker_confirmed))

    @server.tool()
    def save_learning_record(kind: Literal["session", "learning_event", "memory", "book", "followup"], record_id: str, data: dict,
                             operation_id: str, expected_revision: StrictInt, speaker_confirmed: StrictBool = False) -> dict:
        """仅保存必要短事实。新建版本0；更新先读版本；重试原操作ID。事件更正使用专门工具。只有ok=true才说自管已保存。"""
        return guarded(lambda: store.put(kind, record_id, child_data(data), operation_id, expected_revision, speaker_confirmed))

    @server.tool()
    def forget_learning_record(kind: Literal["memory", "learning_event", "book", "followup"], record_id: str,
                               operation_id: str, expected_revision: StrictInt, speaker_confirmed: StrictBool = False) -> dict:
        """实际清除所选自管记录，保留无正文撤回ID。不等于删除WorkBuddy历史/自动记忆/人工副本。"""
        return guarded(lambda: store.remove(kind, record_id, operation_id, expected_revision, speaker_confirmed))

    @server.tool()
    def correct_learning_event(old_id: str, new_id: str, data: dict, operation_id: str,
                               expected_revision: StrictInt, speaker_confirmed: StrictBool = False) -> dict:
        """AI讲错/识别纠正后，原子撤回旧学情依据，建立新ID；旧报告须成人重新生成替代。"""
        return guarded(lambda: store.correct_event(old_id, new_id, child_data(data), operation_id, expected_revision, speaker_confirmed))

    @server.tool()
    def consume_reading_followup(book_ref: str, operation_id: str, speaker_confirmed: StrictBool = False) -> dict:
        """仅在相关语境消费孩子此前明确选择的单本一次跟进。should_ask=true才问；默认off，重试/已使用不再问。"""
        return guarded(lambda: store.consume_followup(book_ref, operation_id, speaker_confirmed))

    @server.tool()
    def forget_learning_task(task_id: str, operation_id: str, expected_sequence: StrictInt, speaker_confirmed: StrictBool = False) -> dict:
        """孩子要忘记某任务：清除该任务的续接点与关联学情；当前有效序号须相符。仅涵盖自管数据。"""
        return guarded(lambda: store.forget_task(task_id, operation_id, expected_sequence, speaker_confirmed))

    @server.tool()
    def family_time_notice(boundary_type: Literal["outside_window", "homework_switch"], operation_id: str, speaker_confirmed: StrictBool = False) -> dict:
        """读取本机北京时间并领取一次软提醒。should_remind=true才提醒；不锁机、不假称孩子自定、不代替真实成人约定。"""
        return guarded(lambda: store.family_notice(boundary_type, operation_id, speaker_confirmed))

    return server


def main():
    parser = argparse.ArgumentParser(description="固定孩子身份的本地 stdio MCP；无HTTP监听")
    parser.add_argument("--root", required=True)
    parser.add_argument("--child", required=True)
    parser.add_argument("--materials", help="成人绑定的只读 catalog.v3.json；不是模型参数")
    args = parser.parse_args()
    try:
        store = Store(outside_repository(args.root), args.child)
        server = create_server(store, args.materials)
    except (CompanionError, ImportError) as error:
        message = str(error) if isinstance(error, CompanionError) else "缺少固定MCP依赖；请安装 .[mcp]"
        print(message, file=sys.stderr)
        return 2
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
