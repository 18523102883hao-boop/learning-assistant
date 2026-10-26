"""Adult-only, deterministic reports from structured evidence, never raw conversations."""

import hashlib
from datetime import date, datetime, time, timedelta, timezone

from . import RULE_VERSION, SCHEMA_VERSION
from .archive import encoded, unseal
from .contracts import ASSISTANCE, ATTEMPTS, INDEPENDENCE, PERFORMANCE, VERIFICATION, choice, choices, identifier, keys
from .errors import CompanionError

CHINA = timezone(timedelta(hours=8))
# Only reviewed labels can enter a parent report. Unknown IDs are not echoed.
CONCEPT_LABELS = {"fractions-equivalence": "等值分数", "fractions-addition": "分数加法",
                  "decimal-place-value": "小数位值", "word-problem-relations": "应用题数量关系",
                  "multiplication-meaning": "乘法含义", "reading-evidence": "阅读中的文本依据",
                  "paragraph-structure": "段落组织", "english-word-meaning": "英语词义"}
ATTEMPT_LABELS = {"identified_condition": "找出了题目条件", "drew_model": "画图或做了表示", "wrote_step": "写出了一步",
                  "explained_reason": "解释了自己的理由", "revised_work": "修改了原尝试", "read_passage": "查阅了文本",
                  "created_draft": "做出了草稿", "self_report": "只有孩子自报，未见过程"}
HELP_LABELS = {"hint": "方向提示", "representation": "图示或具体表示", "concept_explanation": "概念说明",
               "worked_example": "例题示范", "original_step_demo": "原题关键步骤示范", "direct_correction": "直接纠错"}
PERFORMANCE_LABELS = {"not_observed": "未观察到作答", "partial": "看到部分推进", "correct": "本次尝试经所列方式核对为正确",
                      "incorrect": "本次尝试仍有错误", "ambiguous": "依据不清，暂停结论"}
INDEPENDENCE_LABELS = {"not_assessed": "未评估是否能独立继续", "assisted": "获得帮助后推进，不能据此说独立掌握",
                       "child_reported_unaided": "孩子自报可以独立继续，尚未观察",
                       "visible_new_attempt_without_session_hint": "看到本会话未给提示的新尝试，不外推长期掌握"}
CHECK_LABELS = {"child_reported": "孩子自报", "model_checked": "模型核对", "adult_checked": "成人核对", "not_checked": "未核对"}
LIMITATION = "仅反映所保存的有限互动；未使用、未记录或未见尝试均不能说明不会、不认真或缺少进步。模型核对可能出错。"


def period_bounds(start, end):
    try:
        first, last = date.fromisoformat(start), date.fromisoformat(end)
        if first > last or (last - first).days > 366:
            raise ValueError("range")
        return datetime.combine(first, time(), CHINA), datetime.combine(last + timedelta(days=1), time(), CHINA)
    except (ValueError, TypeError, OverflowError) as error:
        raise CompanionError("invalid_period", "日期须为 YYYY-MM-DD，起止顺序正确且不超过 366 天") from error


def parent_export(backup, start, end):
    try:
        child_id = backup["payload"]["child_id"]
        identifier(child_id)
    except (KeyError, TypeError) as error:
        raise CompanionError("invalid_package", "缺少有效资料包身份") from error
    payload = unseal(backup, "backup", child_id)
    lower, upper = period_bounds(start, end)
    events = []
    for row in payload["records"]:
        if row["kind"] != "learning_event" or not lower <= datetime.fromisoformat(row["created_at"]) < upper:
            continue
        data = row["data"]
        # Deliberately exclude attempt_summary, memories, pause points and reading notes.
        events.append({"event_id": row["id"], "task_id": data["task_id"],
                       "concept_labels": list(dict.fromkeys(CONCEPT_LABELS[tag] for tag in data["concept_tags"] if tag in CONCEPT_LABELS)) or ["未核实知识点"],
                       **{k: data[k] for k in ("attempt_kind", "assistance", "performance", "independence_evidence", "source_kind", "verification")}})
    return {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION,
            "child_id": child_id, "source_store_id": payload["store_id"], "source_sequence": payload["sequence"],
            "period": {"start": start, "end": end, "timezone": "Asia/Shanghai"}, "events": events}


def validate_export(export):
    keys(export, {"schema_version", "rule_version", "child_id", "source_store_id", "source_sequence", "period", "events"})
    identifier(export["child_id"])
    keys(export["period"], {"start", "end", "timezone"})
    period_bounds(export["period"]["start"], export["period"]["end"])
    if export["schema_version"] != SCHEMA_VERSION or export["period"]["timezone"] != "Asia/Shanghai" or type(export["source_sequence"]) is not int:
        raise CompanionError("invalid_input", "摘要版本、时区或来源序号不符")
    if not isinstance(export["events"], list):
        raise CompanionError("invalid_input", "摘要事件必须是列表")
    for data in export["events"]:
        keys(data, {"event_id", "task_id", "concept_labels", "attempt_kind", "assistance", "performance", "independence_evidence", "source_kind", "verification"})
        identifier(data["event_id"])
        identifier(data["task_id"])
        choices(data["concept_labels"], set(CONCEPT_LABELS.values()) | {"未核实知识点"}, "concept_labels", 4)
        choice(data["attempt_kind"], ATTEMPTS, "attempt_kind")
        choices(data["assistance"], ASSISTANCE, "assistance")
        choice(data["performance"], PERFORMANCE, "performance")
        choice(data["independence_evidence"], INDEPENDENCE, "independence_evidence")
        choice(data["source_kind"], {"child_reported", "observed_in_session"}, "source_kind")
        choices(data["verification"], VERIFICATION, "verification")


def render_report(export, supersedes=None):
    validate_export(export)
    if supersedes is not None:
        identifier(supersedes, "supersedes")
    report_id = "report-" + hashlib.sha256(encoded({"export": export, "supersedes": supersedes})).hexdigest()[:20]
    metadata = {"report_id": report_id, "supersedes": supersedes,
                **{k: export[k] for k in ("schema_version", "rule_version", "child_id", "source_store_id", "source_sequence", "period")}}
    lines = [f"# 学习互动摘要 · {export['child_id']}", "", f"期间：{export['period']['start']} 至 {export['period']['end']}（北京时间）", "", LIMITATION, ""]
    if supersedes:
        lines.extend([f"本版替代 `{supersedes}`。请替换已保存的旧副本；工具无法远程删除人工复制件。", ""])
    tasks = {}
    for event in export["events"]:
        tasks.setdefault(event["task_id"], []).append(event)
    if not tasks:
        lines.extend(["本期证据不足，不推断掌握情况或使用动机。", "", "家长可以做：按孩子需要提供一本书、一张纸或安静时间，不额外安排测验。"])
    for task_id, events in tasks.items():
        labels = list(dict.fromkeys(label for event in events for label in event["concept_labels"]))
        last = events[-1]
        helps = list(dict.fromkeys(h for event in events for h in event["assistance"]))
        attempts = list(dict.fromkeys(ATTEMPT_LABELS[event["attempt_kind"]] for event in events))
        checks = "、".join(CHECK_LABELS[v] for v in last["verification"]) or "未核对"
        lines.extend([f"## 任务 `{task_id}`", "",
                      "- 卡在哪里：" + "、".join(labels) + "。仅为本次求助涉及的概念。",
                      "- 试了什么：" + "；".join(attempts) + "。",
                      "- 哪种帮助后怎样：" + ("、".join(HELP_LABELS[h] for h in helps) or "未记到具体帮助") + "；" + PERFORMANCE_LABELS[last["performance"]] + f"（{checks}）。这不是帮助效果的因果证明。",
                      "- 能否独立继续：" + INDEPENDENCE_LABELS[last["independence_evidence"]] + "。", "",
                      "依据 ID：" + "、".join(f"`{e['event_id']}`" for e in events) + "。同一任务多轮不计为多次独立失败。", ""])
    if tasks:
        lines.append("家长可以做：等孩子愿意时，让她选是否展示一个自己的办法；无需追加练习或比较姐妹。")
    lines.extend(["", f"报告 ID：`{report_id}`；来源序号：{export['source_sequence']}。资料更正/撤回后须重新生成并替代旧版。", ""])
    return {"metadata": metadata, "markdown": "\n".join(lines)}


def report_is_current(backup, metadata):
    payload = backup["payload"]
    return all(metadata.get(key) == payload.get(value) for key, value in (("child_id", "child_id"), ("source_store_id", "store_id"), ("source_sequence", "sequence")))
