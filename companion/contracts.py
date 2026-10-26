"""Strict runtime validation. Provenance does not imply mastery or physical identity."""

import json
import re

from .errors import CompanionError

SOURCE_KINDS = {"parent_reported", "child_reported", "observed_in_session",
                "adult_verified", "externally_verified", "model_hypothesis"}
INTENTS = {"homework", "reading", "creation", "chat", "unknown"}
HOMEWORK = {"unknown", "in_progress", "paused", "reported_complete"}


def fail(message):
    raise CompanionError("invalid_input", message)


def identifier(value, name="id"):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{0,79}", value):
        fail(f"{name} 须为 1–80 位小写字母、数字、点、下划线或短横线，且以字母开头")
    return value


def text(value, name, maximum=400, *, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()) or "\x00" in value:
        fail(f"{name} 须为不超过 {maximum} 字的有效文本")


def choice(value, allowed, name):
    if not isinstance(value, str) or value not in allowed:
        fail(f"{name} 不在允许值中")


def keys(data, required, optional=()):
    if not isinstance(data, dict) or not set(required) <= set(data) or set(data) - set(required) - set(optional):
        fail("缺少必要字段或包含未允许字段；不要保存完整对话、照片或任意身份字段")


def validate_profile(data):
    keys(data, {"nickname", "grade"}, {"source_kind"})
    text(data["nickname"], "nickname", 20)
    if type(data["grade"]) is not int or not 1 <= data["grade"] <= 6:
        fail("grade 须为小学 1–6 年级")
    if "source_kind" in data:
        choice(data["source_kind"], SOURCE_KINDS, "source_kind")
    return {"source_kind": "parent_reported"} | data


def validate(kind, data):
    # Round-trip copies values and rejects non-JSON inputs before any transaction.
    try:
        data = json.loads(json.dumps(data, ensure_ascii=False, allow_nan=False))
    except (TypeError, ValueError):
        fail("内容必须是合法 JSON")
    if kind == "session":
        keys(data, {"task_id", "interaction_intent", "homework_status", "pause_point", "source_kind"})
        identifier(data["task_id"], "task_id")
        choice(data["interaction_intent"], INTENTS, "interaction_intent")
        choice(data["homework_status"], HOMEWORK, "homework_status")
        text(data["pause_point"], "pause_point", empty=True)
        if data["interaction_intent"] != "homework" and data["homework_status"] == "in_progress":
            fail("离开作业意图须保留暂停状态，不可把切换当作完成")
    else:
        fail("不支持的记录类型")
    choice(data["source_kind"], SOURCE_KINDS, "source_kind")
    return data
