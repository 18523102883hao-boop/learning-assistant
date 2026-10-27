"""Catalogue discovery only: never upgrades old metadata into verified plot or child facts."""

import json
from pathlib import Path

from . import SCHEMA_VERSION
from .contracts import identifier, text
from .errors import CompanionError

LIMITS = "仅旧书架目录识别；版本、册次和家中位置待核。不能据此讲具体剧情、原句或推断谁读过。可讨论孩子给的当前页。"


def normalize_catalog(source):
    if not isinstance(source, dict) or not isinstance(source.get("books"), list):
        raise CompanionError("invalid_input", "旧书架目录格式不符")
    records, seen = [], set()
    for item in source["books"]:
        book_ref = identifier(item["book_id"])
        if book_ref in seen:
            raise CompanionError("invalid_input", "目录书目 ID 重复")
        seen.add(book_ref)
        text(item["title"], "title", 200)
        author = item.get("author", "待核")
        text(author, "author", 200)
        records.append({"book_ref": book_ref, "title": item["title"], "author": author,
                        "source_ref": "library/bookshelf.json#" + book_ref,
                        "source_scope": "catalogue_identification", "accuracy_status": "needs_edition_check",
                        "release_status": "discover_only", "edition_verified": False,
                        "holding_status": "parent_catalogued_unverified", "limits": LIMITS})
    return {"schema_version": SCHEMA_VERSION, "catalog_version": "v3.2026-10-27", "records": records}


class MaterialLibrary:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else None

    def search(self, query, limit=2):
        text(query, "query", 80)
        if type(limit) is not int or not 1 <= limit <= 3:
            raise CompanionError("invalid_input", "一次仅取 1–3 条目录候选")
        if self.path is None or not self.path.exists():
            return {"available": False, "matches": [], "message": "当前没有可读目录；仍可基于孩子提供的当前页一起读"}
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > 2_000_000:
            raise CompanionError("invalid_material", "资料入口不符合固定只读目录要求")
        try:
            catalog = json.loads(self.path.read_text(encoding="utf-8"))
            if catalog["schema_version"] != SCHEMA_VERSION:
                raise ValueError("version")
            matches = []
            for item in catalog["records"]:
                if item.get("release_status") != "discover_only" or item.get("source_scope") != "catalogue_identification":
                    continue
                if query.casefold().strip() not in (item["title"] + " " + item["author"]).casefold():
                    continue
                identifier(item["book_ref"])
                text(item["title"], "title", 200)
                text(item["author"], "author", 200)
                matches.append({k: item[k] for k in ("book_ref", "title", "author", "source_ref", "source_scope", "accuracy_status", "release_status") } | {"limits": LIMITS})
                if len(matches) == limit:
                    break
            return {"available": True, "matches": matches, "message": "目录候选；不代表适读、理解或内容已核验"}
        except (ValueError, KeyError, TypeError, UnicodeError) as error:
            raise CompanionError("invalid_material", "资料目录损坏或格式不兼容，先停用目录，仍可围绕当前页帮助") from error
