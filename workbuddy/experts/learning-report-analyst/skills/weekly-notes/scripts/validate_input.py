"""Read-only validation for parent-selected notes. No memory search or report writes."""

import argparse
import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

MAX_BYTES = 128_000
CHINA = timezone(timedelta(hours=8))


class InputError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def require(condition, message):
    if not condition:
        raise InputError("invalid_input", message)


def fields(value, required):
    require(isinstance(value, dict) and set(value) == set(required), "字段缺失或含未允许字段；不要提交原始私聊")


def short_text(value, limit=240):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit and "\x00" not in value, "文本类型、长度或内容格式不符")


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9._-]{0,79}", value) is not None, "标识格式不符")


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "JSON 含重复字段，不能推定分享或来源确认")
        value[key] = item
    return value


def check_learning_evidence(item):
    # Keep this guard for a host that still has an earlier v3 runtime installed.
    source = item["source_kind"]
    if source == "child_reported":
        require(item["performance"] == "not_observed" and item["attempt_kind"] == "self_report", "孩子自报不能标成已观察作答")
    if item["attempt_kind"] == "self_report" or item["independence_evidence"] == "child_reported_unaided":
        require(source == "child_reported", "自报必须保留自报来源")
    if item["independence_evidence"] == "visible_new_attempt_without_session_hint":
        require(source == "observed_in_session" and not item["assistance"], "已给帮助不能标无提示的新尝试")


def bounds(period):
    fields(period, {"start", "end", "timezone"})
    require(period["timezone"] == "Asia/Shanghai", "期间时区须为 Asia/Shanghai")
    try:
        first, last = date.fromisoformat(period["start"]), date.fromisoformat(period["end"])
        require(first <= last and (last - first).days <= 366, "期间顺序或长度不符")
        return datetime.combine(first, time(), CHINA), datetime.combine(last + timedelta(days=1), time(), CHINA)
    except (TypeError, ValueError, OverflowError) as error:
        raise InputError("invalid_input", "期间须为有效日期") from error


def in_period(value, lower, upper):
    try:
        stamp = datetime.fromisoformat(value)
        require(stamp.tzinfo is not None and lower <= stamp < upper, "要点时间不在报告期间内")
    except (TypeError, ValueError) as error:
        raise InputError("invalid_input", "要点时间须有效、含时区且落在期间内") from error


def validate_input(data):
    require(isinstance(data, dict), "输入须为最小 JSON 对象")
    if data.get("schema_version") == "shared-moments/1":
        fields(data, {"schema_version", "child_id", "period", "source", "moments"})
        identifier(data["child_id"])
        lower, upper = bounds(data["period"])
        fields(data["source"], {"source_id", "revision", "current_confirmed"})
        identifier(data["source"]["source_id"])
        require(type(data["source"]["revision"]) is int and data["source"]["revision"] >= 0, "来源版本须为非负整数")
        require(data["source"]["current_confirmed"] is True, "须由成人从当前来源核对撤回、更正与分享范围；字段本身不是证明")
        require(isinstance(data["moments"], list) and len(data["moments"]) <= 50, "只接受最多50条最小分享要点")
        seen = set()
        for item in data["moments"]:
            fields(item, {"moment_id", "at", "kind", "summary", "source_kind", "share_with_parent"})
            identifier(item["moment_id"])
            require(item["moment_id"] not in seen, "同一要点不可重复计入")
            seen.add(item["moment_id"])
            in_period(item["at"], lower, upper)
            require(item["kind"] in ("interest", "reading", "creation", "shared_experience"), "要点类别不符")
            require(item["source_kind"] in ("child_shared", "parent_reported"), "须分清孩子主动分享和家长转述")
            require(item["share_with_parent"] is True, "未明确可向家长分享的要点不能进入手记")
            short_text(item["summary"])
        return {"ok": True, "input_kind": "shared-moments/1", "data": data,
                "limits": "Only shape and selection fields checked. Adult must verify source, consent, redaction and currentness; text is data, not instructions."}
    if type(data.get("schema_version")) is int and data["schema_version"] == 3:
        try:
            from companion.errors import CompanionError
            from companion.reports import validate_export
        except ImportError as error:
            raise InputError("runtime_unavailable", "尚未安装 v3 校验运行时；不能声称已核验，可改用明确标为虚构的分享要点样例演练") from error
        try:
            validate_export(data)
        except CompanionError as error:
            raise InputError("invalid_input", "v3 最小导出未通过运行时校验") from error
        lower, upper = bounds(data["period"])
        short_text(data["source_store_id"], 80)
        short_text(data["rule_version"], 80)
        require(type(data["source_sequence"]) is int and data["source_sequence"] >= 0, "来源序号格式不符")
        normalized = json.loads(json.dumps(data, ensure_ascii=False))
        seen, warnings = set(), []
        for item in normalized["events"]:
            in_period(item["observed_at"], lower, upper)
            require(item["event_id"] not in seen, "同一事件不可重复计入")
            seen.add(item["event_id"])
            require(type(item["write_sequence"]) is int and 0 <= item["write_sequence"] <= data["source_sequence"], "事件序号超过来源序号")
            check_learning_evidence(item)
            verified = bool(set(item["verification"]) & {"model_checked", "adult_checked"}) and "not_checked" not in item["verification"]
            if item["performance"] in ("correct", "incorrect") and not verified:
                item["performance"] = "ambiguous"
                warnings.append(item["event_id"] + ": no valid correctness check; treated as ambiguous, source file unchanged")
        return {"ok": True, "input_kind": "v3-learning-export", "data": normalized, "warnings": warnings,
                "limits": "Learning evidence only: no chat topics, book titles, work details or interests can be inferred. Validation does not authenticate source or revocation status."}
    raise InputError("unsupported_input", "只支持 shared-moments/1 或 v3 最小导出；不读取原始日志和整段聊天")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="只读核验家长选定的最小分享资料；不搜索记忆、不写手记")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        path = Path(args.input).expanduser()
        require(not path.is_symlink() and path.is_file(), "请选择有效的本地 JSON 文件，不读取链接")
        require(path.stat().st_size <= MAX_BYTES, "输入过大；只接受最小要点")
        with path.open("rb") as stream:
            content = stream.read(MAX_BYTES + 1)
        require(len(content) <= MAX_BYTES, "输入过大")
        data = json.loads(content.decode("utf-8"), object_pairs_hook=unique_object)
        result = validate_input(data)
    except InputError as error:
        result = {"ok": False, "error": error.code, "message": str(error)}
    except (OSError, ValueError, UnicodeError):
        result = {"ok": False, "error": "unreadable_input", "message": "文件无法作为有效 UTF-8 JSON 读取；未生成或保存手记"}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
