"""Checksummed portable packages; checksum is corruption detection, not authentication."""

import hashlib
import json
from datetime import datetime

from . import SCHEMA_VERSION
from .contracts import identifier, keys, validate, validate_profile
from .errors import CompanionError


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def seal(payload):
    return {"payload": payload, "sha256": hashlib.sha256(encoded(payload)).hexdigest()}


def unseal(package, package_type, child_id):
    try:
        keys(package, {"payload", "sha256"})
        payload = package["payload"]
        if len(encoded(package)) > 8_000_000 or seal(payload)["sha256"] != package["sha256"]:
            raise ValueError("checksum")
        common = {"package_type", "schema_version", "rule_version", "child_id", "store_id", "sequence", "created_at", "tombstones", "closed_tasks"}
        keys(payload, common | ({"records", "profile"} if package_type == "backup" else set()))
        if payload["package_type"] != package_type or payload["schema_version"] != SCHEMA_VERSION or payload["child_id"] != child_id:
            raise ValueError("scope")
        if type(payload["sequence"]) is not int or payload["sequence"] < 0:
            raise ValueError("sequence")
        for stamp in [payload["created_at"]]:
            if datetime.fromisoformat(stamp).tzinfo is None:
                raise ValueError("time")
        if not isinstance(payload["store_id"], str) or not isinstance(payload["tombstones"], list):
            raise ValueError("metadata")
        if not isinstance(payload["closed_tasks"], list):
            raise ValueError("closed tasks")
        for task_id in payload["closed_tasks"]:
            identifier(task_id)
        seen = set()
        for row in payload["tombstones"]:
            keys(row, {"kind", "id", "mode", "deleted_at"})
            identifier(row["id"])
            if row["kind"] not in {"session", "task", "learning_event", "memory", "book", "followup", "book_request"} or row["mode"] not in {"forget", "retract", "expired"}:
                raise ValueError("tombstone")
            key = (row["kind"], row["id"])
            if key in seen or datetime.fromisoformat(row["deleted_at"]).tzinfo is None:
                raise ValueError("duplicate")
            seen.add(key)
        if package_type == "backup":
            validate_profile(payload["profile"])
            if not isinstance(payload["records"], list):
                raise ValueError("records")
            seen = set()
            for row in payload["records"]:
                keys(row, {"schema_version", "rule_version", "child_id", "kind", "id", "revision", "data", "created_at", "updated_at"}, {"sequence"})
                if type(row.get("sequence", 0)) is not int or row.get("sequence", 0) < 0:
                    raise ValueError("event order")
                identifier(row["id"])
                validate("session" if row["kind"] == "task" else row["kind"], row["data"])
                if row["child_id"] != child_id or row["schema_version"] != SCHEMA_VERSION or type(row["revision"]) is not int or row["revision"] < 1:
                    raise ValueError("record scope")
                if row["kind"] == "session" and row["id"] != "current":
                    raise ValueError("session")
                if row["kind"] in {"book", "followup"} and row["id"] != row["data"]["book_ref"]:
                    raise ValueError("book")
                if datetime.fromisoformat(row["created_at"]).tzinfo is None or datetime.fromisoformat(row["updated_at"]).tzinfo is None:
                    raise ValueError("record time")
                key = (row["kind"], row["id"])
                if key in seen:
                    raise ValueError("duplicate")
                seen.add(key)
        return payload
    except (CompanionError, TypeError, ValueError, KeyError, OverflowError) as error:
        raise CompanionError("invalid_package", "迁移包损坏、版本不符或身份范围不一致；未导入") from error
