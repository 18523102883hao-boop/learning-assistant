"""Strict runtime validation. Provenance does not imply mastery or physical identity."""

import json
import re

from .errors import CompanionError

SOURCE_KINDS = {"parent_reported", "child_reported", "observed_in_session",
                "adult_verified", "externally_verified", "model_hypothesis"}
INTENTS = {"homework", "reading", "creation", "chat", "unknown"}
HOMEWORK = {"unknown", "in_progress", "paused", "reported_complete"}
ATTEMPTS = {"identified_condition", "drew_model", "wrote_step", "explained_reason", "revised_work", "read_passage", "created_draft", "self_report"}
ASSISTANCE = {"hint", "representation", "concept_explanation", "worked_example", "original_step_demo", "direct_correction"}
PERFORMANCE = {"not_observed", "partial", "correct", "incorrect", "ambiguous"}
INDEPENDENCE = {"not_assessed", "assisted", "child_reported_unaided", "visible_new_attempt_without_session_hint"}
VERIFICATION = {"child_reported", "model_checked", "adult_checked", "not_checked"}
BOOK_STATES = {"unknown", "want_to_try", "reading", "paused", "rereading", "child_reported_finished"}
RECORD_KINDS = {"session", "learning_event", "memory", "book", "followup"}


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


def choices(values, allowed, name, maximum=8):
    if not isinstance(values, list) or len(values) > maximum or len(set(str(v) for v in values)) != len(values):
        fail(f"{name} 须为无重复的短列表")
    for value in values:
        choice(value, allowed, name)


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
    if not isinstance(data, dict):
        fail("记录须为 JSON 对象")
    choice(data.get("source_kind"), SOURCE_KINDS, "source_kind")
    if kind == "session":
        keys(data, {"task_id", "interaction_intent", "homework_status", "pause_point", "source_kind"})
        identifier(data["task_id"], "task_id")
        choice(data["interaction_intent"], INTENTS, "interaction_intent")
        choice(data["homework_status"], HOMEWORK, "homework_status")
        text(data["pause_point"], "pause_point", empty=True)
        if data["interaction_intent"] != "homework" and data["homework_status"] == "in_progress":
            fail("离开作业意图须保留暂停状态，不可把切换当作完成")
    elif kind == "learning_event":
        keys(data, {"task_id", "concept_tags", "attempt_kind", "attempt_summary", "assistance", "performance", "independence_evidence", "source_kind", "verification"}, {"supersedes"})
        identifier(data["task_id"], "task_id")
        if not isinstance(data["concept_tags"], list) or not 1 <= len(data["concept_tags"]) <= 4:
            fail("concept_tags 须为 1–4 个概念标签")
        for tag in data["concept_tags"]:
            identifier(tag, "concept_tag")
        text(data["attempt_summary"], "attempt_summary", 240)
        choice(data["attempt_kind"], ATTEMPTS, "attempt_kind")
        choices(data["assistance"], ASSISTANCE, "assistance")
        choice(data["performance"], PERFORMANCE, "performance")
        choice(data["independence_evidence"], INDEPENDENCE, "independence_evidence")
        choices(data["verification"], VERIFICATION, "verification")
        if data["source_kind"] == "child_reported" and (data["performance"] != "not_observed" or data["attempt_kind"] != "self_report"):
            fail("孩子自报不等于已观察到正确作答")
        if data["source_kind"] not in {"observed_in_session", "child_reported"}:
            fail("学情事件只接受当次观察或明确自报；家长推测不转为学情")
        if data["attempt_kind"] == "self_report" and data["source_kind"] != "child_reported":
            fail("自报须保留自报来源")
        if data["independence_evidence"] == "child_reported_unaided" and data["source_kind"] != "child_reported":
            fail("独立自报须保留自报来源")
        if data["independence_evidence"] == "visible_new_attempt_without_session_hint" and (data["assistance"] or data["source_kind"] != "observed_in_session"):
            fail("已有帮助不能标为本会话无提示独立尝试")
        if "supersedes" in data:
            identifier(data["supersedes"], "supersedes")
    elif kind == "memory":
        keys(data, {"category", "content", "source_kind", "child_opt_in"})
        choice(data["category"], {"preference", "project_note"}, "category")
        text(data["content"], "content", 240)
        if data["child_opt_in"] is not True or data["source_kind"] != "child_reported":
            fail("可选聊天记忆须孩子明确愿意保留，不从闲聊或家长推测自动提取")
    elif kind == "book":
        keys(data, {"book_ref", "reading_state", "source_kind"}, {"position"})
        identifier(data["book_ref"], "book_ref")
        choice(data["reading_state"], BOOK_STATES, "reading_state")
        if data["source_kind"] != "child_reported":
            fail("个人阅读状态由孩子报告，不能从家中持有或旧 unread 推断")
        if "position" in data:
            text(data["position"], "position", 80, empty=True)
    elif kind == "followup":
        keys(data, {"book_ref", "state", "child_opt_in", "source_kind"})
        identifier(data["book_ref"], "book_ref")
        choice(data["state"], {"off", "once_pending", "used", "stopped"}, "state")
        if type(data["child_opt_in"]) is not bool or data["source_kind"] != "child_reported":
            fail("跟进状态须保留孩子本次意愿")
        if data["state"] == "once_pending" and data["child_opt_in"] is not True:
            fail("未获得单本明确同意，不安排跟进")
    else:
        fail("不支持的记录类型")
    choice(data["source_kind"], SOURCE_KINDS, "source_kind")
    return data
