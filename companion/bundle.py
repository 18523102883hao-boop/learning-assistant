"""Reproducible allowlisted archives. No recursive repository or private-data copying."""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from . import RULE_VERSION, SCHEMA_VERSION, __version__
from .contracts import identifier
from .errors import CompanionError

CHILD_SKILLS = ("homework-help", "reading-companion", "explore-task", "partner-chat", "learning-log")
MODULES = ("__init__", "__main__", "errors", "contracts", "store", "archive", "reports", "cli", "mcp_server", "materials", "bundle")
CARDS = ("visible-page", "evidence-and-choice", "make-it-work")
TEST_MODULES = ("store", "lifecycle", "reports", "cli", "mcp", "regressions", "materials", "retention_requests", "bundle")


def read_source(source, relative):
    path = source / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(source) or path.stat().st_size > 2_000_000:
        raise CompanionError("missing_source", f"缺少有效的允许交付文件：{relative}")
    return path.read_bytes()


def archive(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100600 << 16
            output.writestr(info, content)


def build_release(source, output, child_id="test-a"):
    identifier(child_id)
    source = Path(source).resolve()
    original_output = Path(output).expanduser()
    if original_output.is_symlink():
        raise CompanionError("unsafe_path", "不向软链接交付目录写入")
    output = original_output.resolve()
    if output.exists():
        raise CompanionError("output_exists", "交付目录已存在；使用新版本目录，不覆盖")
    base = "workbuddy/final/"
    child = {"PROJECT_INSTRUCTIONS.md": read_source(source, base + "PROJECT_INSTRUCTIONS.md")}
    for skill in CHILD_SKILLS:
        child[f"skills/{skill}/SKILL.md"] = read_source(source, base + f"skills/{skill}/SKILL.md")
    guide = "skills/learning-log/references/record-contract.md"
    child[guide] = read_source(source, base + guide)
    for path in ("catalog.v3.json", "manifest.json", "README.md", *(f"cards/{card}.md" for card in CARDS)):
        child["materials/" + path] = read_source(source, "materials/" + path)
    child["BINDING.template.json"] = json.dumps({"schema_version": SCHEMA_VERSION, "child_id": child_id, "delivery_level": "ADULT_VALIDATION_ONLY", "runtime_mode": "W-A", "platform_verified": False}, ensure_ascii=False, indent=2).encode()
    child["MCP_CONFIG.template.json"] = json.dumps({"mcpServers": {"family-learning-companion": {"command": "/ABS/VENV/PYTHON", "args": ["-m", "companion.mcp_server", "--root", "/ABS/CHILD-DATA", "--child", child_id, "--materials", "/ABS/READONLY-MATERIALS/catalog.v3.json"]}}}, indent=2).encode()
    for filename in ("DEPLOYMENT.md", "CAPABILITIES.md"):
        child[filename] = read_source(source, base + filename)
    parent = {"PROJECT_INSTRUCTIONS.md": read_source(source, base + "PARENT_INSTRUCTIONS.md"), "skills/parent-review/SKILL.md": read_source(source, base + "skills/parent-review/SKILL.md"), "RUNTIME.md": read_source(source, base + "RUNTIME.md")}
    runtime = {f"companion/{name}.py": read_source(source, f"companion/{name}.py") for name in MODULES}
    runtime.update({name: read_source(source, name) for name in ("pyproject.toml", "requirements-mcp.lock.txt")})
    runtime["RUNTIME.md"] = read_source(source, base + "RUNTIME.md")
    for name in TEST_MODULES:
        relative = f"tests/test_{name}.py"
        runtime[relative] = read_source(source, relative)
    # Adult setup archive is self-contained. It is never a child's project root.
    config_paths = ["PROJECT_INSTRUCTIONS.md", "PARENT_INSTRUCTIONS.md", "CHANGELOG.md", "DEPLOYMENT.md", "CAPABILITIES.md", "RUNTIME.md", guide,
                    *(f"skills/{skill}/SKILL.md" for skill in (*CHILD_SKILLS, "parent-review"))]
    for relative in config_paths:
        runtime[base + relative] = read_source(source, base + relative)
    for path in ("catalog.v3.json", "manifest.json", "README.md", *(f"cards/{card}.md" for card in CARDS)):
        runtime["materials/" + path] = read_source(source, "materials/" + path)
    runtime["schemas/v3/record.schema.json"] = read_source(source, "schemas/v3/record.schema.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".companion-release-", dir=output.parent))
    try:
        entries = {f"child-{child_id}.zip": child, "parent-tools.zip": parent, "runtime-source.zip": runtime}
        for name, files in entries.items():
            archive(staging / name, files)
        manifest = {"version": __version__, "rule_version": RULE_VERSION, "delivery_level": "ADULT_VALIDATION_ONLY",
                    "sha256": {name: hashlib.sha256((staging / name).read_bytes()).hexdigest() for name in entries},
                    "limits": "Code/configuration packaging only; platform, OS, model and child acceptance separate."}
        (staging / "release.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output.exists():
            raise CompanionError("output_exists", "交付目录在制作时已出现，不覆盖")
        os.rename(staging, output)
        return manifest
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description="生成分角色成人验证包，不安装/部署")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--child", default="test-a")
    args = parser.parse_args()
    try:
        result = build_release(args.source, args.output, args.child)
    except (CompanionError, OSError) as error:
        result = error.as_dict() if isinstance(error, CompanionError) else {"ok": False, "error": "io_error", "message": "交付文件操作失败，未完成"}
        print(json.dumps(result, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
