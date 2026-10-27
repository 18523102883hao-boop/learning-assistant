"""Launch only the adult-installed, fixed Yiyi stdio binding. Never initializes data."""

import json
import os
import sys
from pathlib import Path

CHILD_ID = "student-b"
BINDING = Path.home() / ".workbuddy/learning-companion/bindings/learning-partner-yiyi.json"


class BindingError(ValueError):
    pass


def require(condition):
    if not condition:
        raise BindingError("学习记录尚未接通或绑定不符，请由家长检查本机安装；当前仍可聊天。")


def build_command(binding):
    require(isinstance(binding, dict) and set(binding) == {"schema_version", "child_id", "runtime_root", "python", "data_root", "materials"})
    require(type(binding["schema_version"]) is int and binding["schema_version"] == 1 and binding["child_id"] == CHILD_ID)
    for key in ("runtime_root", "python", "data_root", "materials"):
        require(isinstance(binding[key], str) and bool(binding[key]) and "\x00" not in binding[key])
        require(Path(binding[key]).is_absolute())
    runtime = Path(binding["runtime_root"]).resolve()
    python = Path(binding["python"])
    data = Path(binding["data_root"])
    materials = Path(binding["materials"])
    require(not data.is_symlink() and data.is_dir() and not (data / "state.sqlite3").is_symlink() and (data / "state.sqlite3").is_file())
    require(data.resolve() != runtime and runtime not in data.resolve().parents and data.resolve() not in runtime.parents)
    require((runtime / "companion/mcp_server.py").is_file())
    # A venv executable is normally a symlink to the base Python. Check its directory.
    require(python.is_file() and runtime in python.parent.resolve().parents)
    require(materials.is_file() and not materials.is_symlink() and runtime in materials.resolve().parents)
    return [str(python), "-I", "-m", "companion.mcp_server", "--root", str(data), "--child", CHILD_ID, "--materials", str(materials)]


def main():
    try:
        require(len(sys.argv) == 1 and not BINDING.is_symlink() and BINDING.is_file() and BINDING.stat().st_size <= 8192)
        if os.name == "posix":
            require(BINDING.stat().st_mode & 0o077 == 0)
        binding = json.loads(BINDING.read_text(encoding="utf-8"))
        command = build_command(binding)
        os.execv(command[0], command)
    except (BindingError, OSError, ValueError, TypeError):
        print("学习记录尚未接通或绑定不符，请由家长检查本机安装；未声明保存成功。", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
