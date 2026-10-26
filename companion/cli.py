"""Adult administration and reproducible local tests. Not exposed as a child tool."""

import argparse
import importlib.metadata
import json
import os
import platform
import re
import sqlite3
import sys
import tempfile
from pathlib import Path

from . import __version__
from .errors import CompanionError
from .reports import parent_export, render_report, report_is_current
from .store import Store
from .stdio import configure_utf8_stdio


def outside_repository(path):
    path = Path(path).expanduser()
    if path.is_symlink():
        raise CompanionError("unsafe_path", "入口不能是软链接")
    path = path.resolve()
    code_root = Path(__file__).resolve().parents[1]
    if path.is_relative_to(code_root) or any((parent / ".git").exists() for parent in (path, *path.parents)):
        raise CompanionError("repository_data_forbidden", "运行资料、报告和备份必须放在 Git 仓库外")
    return path


def load_json(path):
    candidate = Path(path).expanduser()
    if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 8_000_000:
        raise CompanionError("invalid_package", "只读取有效的小型本地 JSON 包，不读取链接")
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise CompanionError("invalid_package", "JSON 包无法解析") from error


def private_output(path, text, child_root):
    original = Path(path).expanduser()
    if original.is_symlink():
        raise CompanionError("unsafe_path", "导出文件不能是软链接")
    output = outside_repository(original)
    if output.is_relative_to(child_root.resolve()):
        raise CompanionError("private_output_required", "成人导出放在孩子资料根目录以外的家长私有目录")
    if output.exists():
        raise CompanionError("output_exists", "输出文件已存在；使用新版本文件名，不静默覆盖")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".companion-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        # Hard-link creates a new file atomically without replacing a racing writer.
        os.link(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {"ok": True, "message": "已写入指定成人目录；请保管私有副本"}


def parser():
    root = argparse.ArgumentParser(description="学习伙伴 v3：成人部署/维护 CLI，非任意模型命令工具")
    commands = root.add_subparsers(dest="command", required=True)
    for command in ("init", "migrate", "prune", "wishlist", "context", "put", "remove", "backup", "deletion-registry", "restore", "parent-export", "report", "report-status", "doctor"):
        child = commands.add_parser(command)
        child.add_argument("--root", required=True)
        child.add_argument("--child", required=True)
        if command == "init":
            child.add_argument("--nickname", required=True)
            child.add_argument("--grade", type=int, required=True)
        if command in {"context", "put", "remove"}:
            child.add_argument("--speaker-confirmed", action="store_true")
        if command in {"put", "remove"}:
            child.add_argument("--kind", required=True)
            child.add_argument("--id", required=True)
            child.add_argument("--op", required=True)
            child.add_argument("--expect", type=int, required=True)
        if command in {"backup", "deletion-registry", "parent-export", "report"}:
            child.add_argument("--output", required=True)
        if command in {"parent-export", "report"}:
            child.add_argument("--start", required=True)
            child.add_argument("--end", required=True)
        if command == "report":
            child.add_argument("--supersedes")
        if command == "report-status":
            child.add_argument("--metadata", required=True)
        if command == "restore":
            child.add_argument("--package", required=True)
            child.add_argument("--registry", required=True)
            child.add_argument("--op", required=True)
            child.add_argument("--confirm-current-registry", action="store_true")
        if command == "prune":
            child.add_argument("--op", required=True)
    return root


def execute(args):
    original_root = Path(args.root).expanduser()
    if original_root.is_symlink():
        raise CompanionError("unsafe_path", "运行资料根目录不能是软链接")
    data_root = outside_repository(original_root)
    if args.command == "init":
        Store.initialize(data_root, args.child, {"nickname": args.nickname, "grade": args.grade})
        return {"ok": True, "child_id": args.child, "version": __version__}
    if args.command == "migrate":
        return Store.migrate(data_root, args.child)
    store = Store(data_root, args.child)
    if args.command == "prune":
        return store.prune(args.op)
    if args.command == "wishlist":
        return store.wishlist()
    if args.command == "context":
        return store.context(args.speaker_confirmed)
    if args.command == "put":
        raw = sys.stdin.read(64_001)
        if len(raw) > 64_000:
            raise CompanionError("invalid_input", "输入过大；仅保存短事实")
        try:
            data = json.loads(raw)
        except ValueError as error:
            raise CompanionError("invalid_input", "stdin 须为有效 JSON") from error
        return store.put(args.kind, args.id, data, args.op, args.expect, args.speaker_confirmed)
    if args.command == "remove":
        return store.remove(args.kind, args.id, args.op, args.expect, args.speaker_confirmed)
    if args.command in {"backup", "deletion-registry", "parent-export"}:
        payload = store.deletion_registry() if args.command == "deletion-registry" else store.backup()
        if args.command == "parent-export":
            payload = parent_export(payload, args.start, args.end)
        return private_output(args.output, json.dumps(payload, ensure_ascii=False, indent=2) + "\n", data_root)
    if args.command == "restore":
        return store.restore(load_json(args.package), load_json(args.registry), args.op, registry_is_current=args.confirm_current_registry)
    if args.command == "report":
        report = render_report(parent_export(store.backup(), args.start, args.end), args.supersedes)
        content = report["markdown"] + "\n<!-- companion-metadata: " + json.dumps(report["metadata"], ensure_ascii=False) + " -->\n"
        result = private_output(args.output, content, data_root)
        return result | {"report_id": report["metadata"]["report_id"], "format": "Markdown"}
    if args.command == "report-status":
        candidate = Path(args.metadata)
        if candidate.is_symlink() or not candidate.is_file() or candidate.stat().st_size > 8_000_000:
            raise CompanionError("invalid_package", "无效报告文件")
        content = candidate.read_text(encoding="utf-8")
        marker = re.search(r"<!-- companion-metadata: (\{[^\n]*\}) -->", content)
        if marker:
            try:
                report = json.loads(marker[1])
            except ValueError as error:
                raise CompanionError("invalid_package", "报告元数据不完整") from error
        else:
            report = load_json(candidate)
        if not isinstance(report, dict):
            raise CompanionError("invalid_package", "报告元数据须为对象")
        metadata = report.get("metadata", report)
        return {"ok": True, "current": report_is_current(store.backup(), metadata), "message": "发生更正/撤回或新增资料后，旧版需重生并替代"}
    if args.command == "doctor":
        try:
            mcp = importlib.metadata.version("mcp")
        except importlib.metadata.PackageNotFoundError:
            mcp = "not_installed"
        return {"ok": True, "version": __version__, "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
                "mcp": mcp, "child_id": store.child_id, "os_permissions_verified": False, "workbuddy_verified": False}
    raise CompanionError("invalid_input", "不支持的命令")


def main():
    configure_utf8_stdio()
    args = parser().parse_args()
    try:
        result = execute(args)
    except CompanionError as error:
        print(json.dumps(error.as_dict(), ensure_ascii=False))
        return 2
    except OSError:
        print(json.dumps({"ok": False, "error": "io_error", "message": "本地文件操作失败，未宣称完成；请成人核查路径/权限/磁盘"}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
