#!/usr/bin/env python3
"""Build the 147-entry book knowledge base from TSV source cards."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import sys


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
BOOKSHELF = ROOT / "library" / "bookshelf.json"
DATA_DIR = BASE / "data"
GROUPS = {
    "child-picture-bridge": "儿童·图文书与桥梁书",
    "child-text": "儿童·纯文字与进阶",
    "history-society": "历史·社会·政治",
    "science-tech": "科学·技术·数学",
    "business-investment": "商业·投资·管理",
    "education-psychology": "教育·心理·学习",
    "literature-culture": "文学·散文·传记·文化",
}
FIELDS = [
    "book_id",
    "entry_type",
    "audience",
    "age_hint",
    "use_modes",
    "topics",
    "gist",
    "child_bridge",
    "use_when",
    "talk_angles",
    "guardrail",
    "source_grade",
    "source_note",
    "related_ids",
]
GROUP_INTRO = {
    "child-picture-bridge": "图文书、桥梁书、漫画、杂志和短篇集。优先按孩子当前话题找入口，一次只递一本。",
    "child-text": "纯文字或接近纯文字的儿童与少年读物。只用于孩子主动想读、共读或聊书时，不按年级硬推。",
    "history-society": "历史、社会、政治、经济与文明观察。多数是伙伴背景或孩子远期读物，不是当前任务。",
    "science-tech": "科学、数学、技术、AI 与自然。适合回应孩子的具体好奇，不把成人科普当成短期阅读指标。",
    "business-investment": "商业、投资、管理与决策。以伙伴背景和家长自读为主；只有孩子主动问现实问题时才取小概念。",
    "education-psychology": "教育、学习科学、心理与思维方法。优先作为伙伴和家长的理解框架，不拿来给孩子贴标签。",
    "literature-culture": "小说、散文、传记、传统经典与语言文化。按作品的可聊主题取用，不把成人文学当等级目标。",
}
ENTRY_TYPES = {"single", "series", "collection", "magazine", "workbook", "unknown"}
AUDIENCES = {"child", "teen", "adult", "parent", "family"}
USE_MODES = {"child_read", "co_read", "discuss", "background", "parent_only", "lookup"}


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_books() -> tuple[list[dict], dict[str, dict]]:
    payload = json.loads(BOOKSHELF.read_text(encoding="utf-8"))
    books = payload.get("books", [])
    meta = {book["book_id"]: book for book in books}
    if len(books) != 147 or len(meta) != 147:
        fail(f"bookshelf.json 应有 147 个唯一 book_id，实际 {len(books)} 条、{len(meta)} 个 ID")
    return books, meta


def read_rows() -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for path in sorted(DATA_DIR.glob("*.tsv")):
        group = path.stem
        if group not in GROUPS:
            fail(f"未知分组文件名：{path.name}")
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != FIELDS:
                fail(f"{path.name} 表头不符：{reader.fieldnames}")
            for line_no, row in enumerate(reader, 2):
                row = {field: (row.get(field) or "").strip() for field in FIELDS}
                book_id = row["book_id"].strip()
                where = f"{path.name}:{line_no} {book_id}"
                if not book_id:
                    fail(f"{path.name}:{line_no} 缺少 book_id")
                if not re.fullmatch(r"bk-[0-9]{4}", book_id):
                    fail(f"{where} book_id 格式应为 bk-0000")
                if book_id in seen:
                    fail(f"{where} 重复")
                seen.add(book_id)
                required = (
                    "entry_type",
                    "audience",
                    "age_hint",
                    "use_modes",
                    "topics",
                    "gist",
                    "use_when",
                    "talk_angles",
                    "guardrail",
                    "source_grade",
                    "source_note",
                )
                for field in required:
                    if not row[field].strip():
                        fail(f"{where} 字段 {field} 为空")
                if row["source_grade"] not in {"B", "C"}:
                    fail(f"{where} source_grade 只能是 B 或 C（本库没有逐页 A 级材料）")
                if row["entry_type"] not in ENTRY_TYPES:
                    fail(f"{where} entry_type 非法：{row['entry_type']}")
                if row["audience"] not in AUDIENCES:
                    fail(f"{where} audience 非法：{row['audience']}")
                row["group"] = group
                for field in ("use_modes", "topics", "use_when", "talk_angles", "related_ids"):
                    values = split_list(row[field])
                    if len(values) != len(set(values)):
                        fail(f"{where} 字段 {field} 有重复值")
                    row[field + "_list"] = values
                invalid_modes = sorted(set(row["use_modes_list"]) - USE_MODES)
                if invalid_modes:
                    fail(f"{where} use_modes 含非法值：{invalid_modes}")
                for related_id in row["related_ids_list"]:
                    if not re.fullmatch(r"bk-[0-9]{4}", related_id):
                        fail(f"{where} related_ids 格式非法：{related_id}")
                    if related_id == book_id:
                        fail(f"{where} related_ids 不能指向自己")
                rows.append(row)
    return rows


def merge_and_validate(books: list[dict], meta: dict[str, dict], rows: list[dict]) -> list[dict]:
    by_id = {row["book_id"]: row for row in rows}
    missing = sorted(set(meta) - set(by_id))
    unknown = sorted(set(by_id) - set(meta))
    if missing or unknown:
        fail(f"覆盖不完整。缺少 {missing}；多出 {unknown}")
    known_ids = set(by_id)
    for row in rows:
        dangling = sorted(set(row["related_ids_list"]) - known_ids)
        if dangling:
            fail(f"{row['book_id']} related_ids 指向不存在的条目：{dangling}")

    records: list[dict] = []
    book_order = {book["book_id"]: index for index, book in enumerate(books)}
    for row in sorted(rows, key=lambda item: book_order[item["book_id"]]):
        book = meta[row["book_id"]]
        record = {
            "book_id": row["book_id"],
            "group": row["group"],
            "group_label": GROUPS[row["group"]],
            "entry_type": row["entry_type"],
            "audience": row["audience"],
            "age_hint": row["age_hint"],
            "use_modes": row["use_modes_list"],
            "topics": row["topics_list"],
            "title": book["title"],
            "author": book.get("author", ""),
            "catalog_category": book.get("category", ""),
            "catalog_source": book.get("source", ""),
            "catalog_note": book.get("notes", ""),
            "gist": row["gist"],
            "child_bridge": row["child_bridge"] or None,
            "use_when": row["use_when_list"],
            "talk_angles": row["talk_angles_list"],
            "guardrail": row["guardrail"],
            "source_grade": row["source_grade"],
            "source_note": row["source_note"],
            "related_ids": row["related_ids_list"],
        }
        records.append(record)
    return records


def write_outputs(records: list[dict]) -> None:
    catalog = {
        "schema_version": "1.0",
        "catalog": "家庭书架 147 条书目知识卡",
        "source_catalog": "library/bookshelf.json",
        "generated_by": "library/book-knowledge/build.py",
        "source_grade_legend": {
            "A": "已读原文（本库不适用）",
            "B": "基于公认公开书目知识与既有稳定资料；可讲大意，不编页码或原句",
            "C": "仅目录/书名/家长备注；只介绍主题，细节须先看实体书或可靠资料",
        },
        "records": records,
    }
    (BASE / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (BASE / "catalog.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )

    index_lines = [
        "# 147 本书目知识索引",
        "",
        "> 机器可读全文：[catalog.json](catalog.json)／[catalog.jsonl](catalog.jsonl)。本索引只用于选书，详细内容在对应分组的浏览文件里。",
        "> `status`、`owner`、`transition_level` 等书架初始化字段不是孩子事实；`age_hint` 只是粗略使用建议，不是能力测评。",
        "",
        "## 使用顺序",
        "",
        "1. 先按 `book_id`、书名、主题或场景缩小到一两条记录。",
        "2. 读对应分组文件或 `catalog.json` 中的完整卡片。",
        "3. 只在非作业场景、孩子当前话题接得上时取 **一条** `child_bridge`；C 级内容不主动讲具体情节。",
        "4. 孩子不接就放下，不追问、不布置阅读任务。",
        "",
    ]
    for group, label in GROUPS.items():
        group_records = [record for record in records if record["group"] == group]
        index_lines.extend(
            [
                f"## {label}（{len(group_records)} 条）",
                "",
                f"浏览文件：[browse/{group}.md](browse/{group}.md)",
                "",
                "| 编号 | 书名 | 类型 | 使用 | 主题 | 一句话 |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for record in group_records:
            one_line = record["gist"].split("。")[0].strip()
            modes = "、".join(record["use_modes"])
            topics = "、".join(record["topics"][:4])
            index_lines.append(
                f"| {record['book_id']} | {record['title']} | {record['entry_type']} | {modes} | {topics} | {one_line}。 |"
            )
        index_lines.append("")
    (BASE / "index.md").write_text("\n".join(index_lines).rstrip() + "\n", encoding="utf-8")

    for group, label in GROUPS.items():
        group_records = [record for record in records if record["group"] == group]
        lines = [f"# {label}", "", f"> {GROUP_INTRO[group]}", ""]
        for record in group_records:
            modes = "、".join(record["use_modes"])
            topics = "、".join(record["topics"])
            related = "、".join(record["related_ids"]) if record["related_ids"] else "无"
            lines.extend(
                [
                    f"## {record['book_id']} · {record['title']}",
                    "",
                    f"- 作者：{record['author']}",
                    f"- 目录分类：{record['catalog_category']}｜类型：{record['entry_type']}｜适合：{record['audience']}／{record['age_hint']}｜用法：{modes}",
                    f"- 主题：{topics}",
                    f"- 讲什么：{record['gist']}",
                    f"- 孩子入口：{record['child_bridge'] or '暂无直接入口；只作伙伴背景或家长自读。'}",
                    f"- 何时用：{'；'.join(record['use_when'])}",
                    f"- 可聊方向：{'；'.join(record['talk_angles'])}",
                    f"- 边界：{record['guardrail']}",
                    f"- 来源：{record['source_grade']} 级——{record['source_note']}",
                ]
            )
            if record["catalog_note"]:
                lines.append(f"- 目录备注（非内容事实）：{record['catalog_note']}")
            lines.extend([f"- 关联：{related}", "", "---", ""])
        (BASE / "browse" / f"{group}.md").write_text(
            "\n".join(lines).rstrip() + "\n", encoding="utf-8"
        )


def main() -> int:
    books, meta = read_books()
    rows = read_rows()
    records = merge_and_validate(books, meta, rows)
    write_outputs(records)
    totals = {}
    grades = {}
    for record in records:
        totals[record["group"]] = totals.get(record["group"], 0) + 1
        grades[record["source_grade"]] = grades.get(record["source_grade"], 0) + 1
    print(f"records={len(records)}")
    for group, count in totals.items():
        print(f"  {group}: {count}")
    print(f"source_grades={grades}")
    print("validation=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
