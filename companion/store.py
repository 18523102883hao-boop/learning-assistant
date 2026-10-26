"""One store per OS user/child. Tools are a narrow interface, not an OS sandbox.

candidate -> validation -> BEGIN IMMEDIATE -> retry/conflict checks -> commit
An operation receipt contains IDs only; it cannot resurrect forgotten payloads.
"""

import hashlib
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import RULE_VERSION, SCHEMA_VERSION, STORAGE_VERSION
from .archive import seal, unseal
from .contracts import identifier, validate, validate_profile
from .errors import CompanionError


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    @classmethod
    def initialize(cls, root, child_id, profile):
        identifier(child_id, "child_id")
        profile = validate_profile(profile)
        root = Path(root).expanduser()
        if root.is_symlink() or root.exists():
            raise CompanionError("already_exists", "初始化要求新的独立目录，不覆盖已有资料")
        root.mkdir(mode=0o700, parents=True)
        database = root / "state.sqlite3"
        try:
            connection = sqlite3.connect(database, isolation_level=None)
            connection.executescript("""
                PRAGMA user_version=4;
                PRAGMA journal_mode=DELETE;
                PRAGMA secure_delete=ON;
                CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE records (
                    kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    revision INTEGER NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, sequence INTEGER NOT NULL, PRIMARY KEY (kind, id));
                CREATE TABLE operations (
                    id TEXT PRIMARY KEY, digest TEXT NOT NULL, receipt TEXT NOT NULL);
                CREATE TABLE tombstones (
                    kind TEXT NOT NULL, id TEXT NOT NULL, mode TEXT NOT NULL,
                    deleted_at TEXT NOT NULL, PRIMARY KEY (kind, id));
                CREATE TABLE closed_tasks (id TEXT PRIMARY KEY);
            """)
            connection.execute("BEGIN IMMEDIATE")
            metadata = {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION,
                        "storage_version": STORAGE_VERSION,
                        "child_id": child_id, "profile": profile, "sequence": 0,
                        "store_id": str(uuid.uuid4()), "created_at": now_utc()}
            connection.executemany("INSERT INTO meta VALUES (?,?)", [(k, canonical(v)) for k, v in metadata.items()])
            connection.commit()
            connection.close()
            if os.name == "posix":
                database.chmod(0o600)
        except sqlite3.Error as error:
            raise CompanionError("storage_error", "初始化失败；未声明资料保存成功") from error
        return cls(root, child_id)

    @classmethod
    def migrate(cls, root, expected_child):
        """Explicit adult migration of early v3 physical storage; never silently upgrades."""
        identifier(expected_child)
        original = Path(root).expanduser()
        database = original / "state.sqlite3"
        if original.is_symlink() or database.is_symlink() or not database.is_file() or database.stat().st_nlink != 1:
            raise CompanionError("unsafe_path", "迁移只针对有效独立资料文件")
        connection = sqlite3.connect(database.resolve().as_uri() + "?mode=rw", uri=True, isolation_level=None, timeout=5)
        try:
            connection.execute("BEGIN IMMEDIATE")
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if cls._meta(connection, "child_id") != expected_child:
                raise CompanionError("identity_mismatch", "绑定身份不符，不迁移另一孩子的资料")
            if version == STORAGE_VERSION:
                return {"ok": True, "migrated": False, "storage_version": STORAGE_VERSION}
            if version != 3:
                raise CompanionError("schema_mismatch", "不支持的旧存储格式；需单独明确迁移")
            for kind, data in connection.execute("SELECT kind,data FROM records"):
                validate("session" if kind == "task" else kind, json.loads(data))
            connection.execute("CREATE TABLE IF NOT EXISTS closed_tasks (id TEXT PRIMARY KEY)")
            columns = {row[1] for row in connection.execute("PRAGMA table_info(records)")}
            if "sequence" not in columns:
                # Old same-second ordering was not saved; zero explicitly means unknown.
                connection.execute("ALTER TABLE records ADD COLUMN sequence INTEGER NOT NULL DEFAULT 0")
            connection.execute("INSERT INTO meta VALUES ('storage_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (canonical(STORAGE_VERSION),))
            connection.execute("PRAGMA user_version=4")
            connection.commit()
            return {"ok": True, "migrated": True, "storage_version": STORAGE_VERSION, "legacy_event_order": "same_second_unknown"}
        except (sqlite3.Error, ValueError) as error:
            raise CompanionError("migration_failed", "迁移失败，原事务已回滚；请成人核查有效副本") from error
        finally:
            if connection.in_transaction:
                connection.rollback()
            connection.close()

    def __init__(self, root, expected_child):
        identifier(expected_child, "child_id")
        original = Path(root).expanduser()
        if original.is_symlink():
            raise CompanionError("unsafe_path", "资料根目录不能是软链接")
        self.root = original.resolve()
        self.database = self.root / "state.sqlite3"
        self.child_id = expected_child
        with self._connection() as connection:
            self.store_id = self._meta(connection, "store_id")

    @staticmethod
    def _meta(connection, key):
        row = connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        if row is None:
            raise CompanionError("storage_error", "资料元数据不完整；请成人恢复有效副本")
        return json.loads(row[0])

    @contextmanager
    def _connection(self, write=False):
        if self.database.is_symlink() or not self.database.is_file() or self.database.stat().st_nlink != 1:
            raise CompanionError("unsafe_path", "数据库不存在或链接状态不安全")
        connection = None
        try:
            connection = sqlite3.connect(self.database.as_uri() + "?mode=rw", uri=True, timeout=5, isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA trusted_schema=OFF")
            connection.execute("PRAGMA secure_delete=ON")
            connection.execute("PRAGMA synchronous=FULL")
            if connection.execute("PRAGMA user_version").fetchone()[0] != STORAGE_VERSION:
                raise CompanionError("schema_mismatch", "资料版本不兼容；请成人运行明确迁移")
            if self._meta(connection, "child_id") != self.child_id:
                raise CompanionError("identity_mismatch", "账号绑定不符，不打开另一孩子的资料")
            if write:
                connection.execute("BEGIN IMMEDIATE")
            yield connection
            if write:
                connection.commit()
        except sqlite3.Error as error:
            if connection and connection.in_transaction:
                connection.rollback()
            code = "storage_busy" if "locked" in str(error).lower() else "storage_error"
            raise CompanionError(code, "资料暂时无法保存或读取；可继续当前帮助，稍后沿用原操作 ID 重试") from error
        finally:
            if connection:
                if connection.in_transaction:
                    connection.rollback()
                connection.close()

    def _envelope(self, row):
        return {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION,
                "child_id": self.child_id, "kind": row["kind"], "id": row["id"],
                "revision": row["revision"], "data": json.loads(row["data"]),
                "sequence": row["sequence"],
                "created_at": row["created_at"], "updated_at": row["updated_at"]}

    @staticmethod
    def _replay(connection, operation_id, request):
        digest = hashlib.sha256(canonical(request).encode()).hexdigest()
        old = connection.execute("SELECT digest, receipt FROM operations WHERE id=?", (operation_id,)).fetchone()
        if old:
            if old["digest"] != digest:
                raise CompanionError("operation_conflict", "操作 ID 已用于不同内容；请核对，不覆盖原记录")
            return digest, json.loads(old["receipt"]) | {"replayed": True}
        return digest, None

    def _receipt(self, connection, operation_id, digest, record_id, revision, extra=None):
        sequence = self._meta(connection, "sequence") + 1
        connection.execute("UPDATE meta SET value=? WHERE key='sequence'", (canonical(sequence),))
        receipt = {"ok": True, "id": record_id, "revision": revision, "sequence": sequence,
                   "operation_id": operation_id, "replayed": False}
        receipt.update(extra or {})
        connection.execute("INSERT INTO operations VALUES (?,?,?)", (operation_id, digest, canonical(receipt)))
        return receipt

    def _check_event(self, connection, data):
        states = connection.execute("SELECT data FROM records WHERE kind IN ('session','task')").fetchall()
        if not any(json.loads(row["data"])["task_id"] == data["task_id"] for row in states):
            raise CompanionError("unknown_task", "没有对应任务状态，不把未知题目归为学情")
        if data["independence_evidence"] == "visible_new_attempt_without_session_hint":
            rows = connection.execute("SELECT data FROM records WHERE kind='learning_event'").fetchall()
            if any((item := json.loads(row["data"]))["task_id"] == data["task_id"] and item["assistance"] for row in rows):
                raise CompanionError("evidence_conflict", "同一任务已获帮助，不能改称本会话无提示独立尝试")

    def _save_row(self, connection, kind, record_id, data, revision, created_at, updated_at, sequence=None):
        if sequence is None:
            sequence = self._meta(connection, "sequence") + 1
        connection.execute("INSERT INTO records VALUES (?,?,?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data, revision=excluded.revision, updated_at=excluded.updated_at, sequence=excluded.sequence",
                           (kind, record_id, canonical(data), revision, created_at, updated_at, sequence))

    def put(self, kind, record_id, data, operation_id, expected_revision, speaker_confirmed=False):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "当前说话者不确定，只提供通用帮助，暂停个人记录")
        identifier(record_id)
        identifier(operation_id, "operation_id")
        if type(expected_revision) is not int or expected_revision < 0:
            raise CompanionError("invalid_input", "expected_revision 须为非负整数")
        data = validate(kind, data)
        if kind == "session" and record_id != "current":
            raise CompanionError("invalid_input", "当前会话状态只使用 current ID")
        if kind in {"book", "followup"} and record_id != data["book_ref"]:
            raise CompanionError("invalid_input", "个人书状态 ID 必须与 book_ref 一致")
        request = {"action": "put", "kind": kind, "id": record_id, "data": data, "revision": expected_revision}
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, request)
            if replay:
                return replay
            if connection.execute("SELECT 1 FROM tombstones WHERE kind=? AND id=?", (kind, record_id)).fetchone():
                raise CompanionError("withdrawn", "此 ID 已删除或撤回，不可再次写回；新事实需新 ID")
            old = connection.execute("SELECT * FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
            revision = old["revision"] if old else 0
            if expected_revision != revision:
                raise CompanionError("revision_conflict", "资料已有更新；先读取有效状态，再决定是否保存")
            if kind == "learning_event":
                if old or "supersedes" in data:
                    raise CompanionError("immutable_event", "学习事件不原位改写；请用原子更正动作撤回旧依据")
                self._check_event(connection, data)
            stamp = now_utc()
            if kind == "session":
                task_id = data["task_id"]
                if connection.execute("SELECT 1 FROM tombstones WHERE kind='task' AND id=?", (task_id,)).fetchone():
                    raise CompanionError("withdrawn", "此任务已忘记，请为新任务使用新 ID")
                if connection.execute("SELECT 1 FROM closed_tasks WHERE id=?", (task_id,)).fetchone() and data["homework_status"] != "reported_complete":
                    raise CompanionError("task_closed", "此任务已报完成；新的尝试使用新任务 ID，不复活旧暂停点")
                if old:
                    previous = json.loads(old["data"])
                    if previous["task_id"] != task_id:
                        if previous["homework_status"] == "in_progress":
                            previous["homework_status"] = "paused"
                        self._save_task(connection, previous, old["created_at"], stamp)
                if data["homework_status"] == "reported_complete":
                    data = data | {"pause_point": ""}
                    connection.execute("INSERT OR IGNORE INTO closed_tasks VALUES (?)", (task_id,))
                self._save_task(connection, data, stamp, stamp)
            self._save_row(connection, kind, record_id, data, revision + 1, old["created_at"] if old else stamp, stamp)
            return self._receipt(connection, operation_id, digest, record_id, revision + 1)

    def read(self, kind, record_id):
        identifier(record_id)
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
            return self._envelope(row) if row else None

    def context(self, speaker_confirmed=False):
        if speaker_confirmed is not True:
            return {"attribution": "unconfirmed", "message": "只提供通用帮助，不读取个人上下文"}
        with self._connection() as connection:
            connection.execute("BEGIN")
            row = connection.execute("SELECT * FROM records WHERE kind='session' AND id='current'").fetchone()
            all_rows = connection.execute("SELECT * FROM records ORDER BY updated_at,id").fetchall()
            cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            events = [self._envelope(r) for r in all_rows if r["kind"] == "learning_event" and r["updated_at"] >= cutoff]
            if row:
                task_id = json.loads(row["data"])["task_id"]
                events = [r for r in events if r["data"]["task_id"] == task_id]
            return {"attribution": "bound_account", "child_id": self.child_id,
                    "profile": self._meta(connection, "profile"),
                    "session": self._envelope(row) if row else None, "events": events[-20:],
                    "pending_tasks": [self._envelope(r) for r in all_rows if r["kind"] == "task" and json.loads(r["data"])["homework_status"] in {"paused", "in_progress"} and (not row or json.loads(r["data"])["task_id"] != json.loads(row["data"])["task_id"])][-10:],
                    "books": [self._envelope(r) for r in all_rows if r["kind"] == "book"],
                    "followups": [self._envelope(r) for r in all_rows if r["kind"] == "followup"],
                    "memories": [self._envelope(r) for r in all_rows if r["kind"] == "memory" and r["updated_at"] >= cutoff],
                    "sequence": self._meta(connection, "sequence")}

    def _save_task(self, connection, data, created_at, updated_at):
        old = connection.execute("SELECT * FROM records WHERE kind='task' AND id=?", (data["task_id"],)).fetchone()
        self._save_row(connection, "task", data["task_id"], data, old["revision"] + 1 if old else 1, old["created_at"] if old else created_at, updated_at)

    def _forget_task_rows(self, connection, task_id):
        rows = connection.execute("SELECT * FROM records WHERE kind IN ('session','task','learning_event')").fetchall()
        for row in rows:
            if json.loads(row["data"])["task_id"] == task_id:
                if row["kind"] == "session":
                    connection.execute("DELETE FROM records WHERE kind='session' AND id='current'")
                else:
                    self._erase(connection, row["kind"], row["id"], "forget")
        self._erase(connection, "task", task_id, "forget")

    def _erase(self, connection, kind, record_id, mode):
        connection.execute("DELETE FROM records WHERE kind=? AND id=?", (kind, record_id))
        connection.execute("INSERT INTO tombstones VALUES (?,?,?,?) ON CONFLICT(kind,id) DO NOTHING", (kind, record_id, mode, now_utc()))

    def remove(self, kind, record_id, operation_id, expected_revision, speaker_confirmed=False, *, mode="forget"):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "当前说话者不确定，暂停个人资料修改")
        if kind not in {"session", "task", "learning_event", "memory", "book", "followup"} or mode not in {"forget", "retract"}:
            raise CompanionError("invalid_input", "不允许的删除范围或方式")
        identifier(record_id)
        identifier(operation_id, "operation_id")
        if type(expected_revision) is not int or expected_revision < 0:
            raise CompanionError("invalid_input", "删除需提供已读到的有效版本")
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": mode, "kind": kind, "id": record_id, "revision": expected_revision})
            if replay:
                return replay
            row = connection.execute("SELECT revision FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
            revision = row[0] if row else 0
            if revision != expected_revision:
                raise CompanionError("revision_conflict", "删除前资料已有变更；先核对当前版本")
            if kind in {"session", "task"}:
                stored = connection.execute("SELECT data FROM records WHERE kind=? AND id=?", (kind, record_id)).fetchone()
                if stored:
                    self._forget_task_rows(connection, json.loads(stored[0])["task_id"])
            else:
                self._erase(connection, kind, record_id, mode)
            if kind == "book":
                self._erase(connection, "followup", record_id, mode)
            return self._receipt(connection, operation_id, digest, record_id, 0)

    def correct_event(self, old_id, new_id, data, operation_id, expected_revision, speaker_confirmed=False):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "当前说话者不确定，暂停个人归因")
        for value in (old_id, new_id, operation_id):
            identifier(value)
        if old_id == new_id or type(expected_revision) is not int or expected_revision < 1:
            raise CompanionError("invalid_input", "更正使用新 ID 和原事件有效版本")
        data = validate("learning_event", data)
        data = data | {"supersedes": old_id}
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": "correct", "old": old_id, "new": new_id, "data": data, "revision": expected_revision})
            if replay:
                return replay
            old = connection.execute("SELECT * FROM records WHERE kind='learning_event' AND id=?", (old_id,)).fetchone()
            if not old or old["revision"] != expected_revision:
                raise CompanionError("revision_conflict", "原事件已变更或不存在；未覆盖")
            if connection.execute("SELECT 1 FROM records WHERE kind='learning_event' AND id=?", (new_id,)).fetchone() or connection.execute("SELECT 1 FROM tombstones WHERE kind='learning_event' AND id=?", (new_id,)).fetchone():
                raise CompanionError("record_conflict", "更正的新 ID 已被使用")
            if json.loads(old["data"])["task_id"] != data["task_id"]:
                raise CompanionError("invalid_input", "更正不能换成另一任务")
            self._check_event(connection, data)
            self._erase(connection, "learning_event", old_id, "retract")
            stamp = now_utc()
            self._save_row(connection, "learning_event", new_id, data, 1, stamp, stamp)
            return self._receipt(connection, operation_id, digest, new_id, 1, {"retracted_id": old_id})

    def consume_followup(self, book_ref, operation_id, speaker_confirmed=False):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "不确定本人意愿时不跟进")
        identifier(book_ref)
        identifier(operation_id)
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": "consume_followup", "book_ref": book_ref})
            if replay:
                return replay | {"should_ask": False}
            row = connection.execute("SELECT * FROM records WHERE kind='followup' AND id=?", (book_ref,)).fetchone()
            should_ask = bool(row and json.loads(row["data"])["state"] == "once_pending")
            if should_ask:
                data = json.loads(row["data"]) | {"state": "used"}
                self._save_row(connection, "followup", book_ref, data, row["revision"] + 1, row["created_at"], now_utc())
            return self._receipt(connection, operation_id, digest, book_ref, row["revision"] + int(should_ask) if row else 0, {"should_ask": should_ask})

    def forget_task(self, task_id, operation_id, expected_sequence, speaker_confirmed=False):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "归因不明时不改变个人资料")
        identifier(task_id)
        identifier(operation_id)
        if type(expected_sequence) is not int or expected_sequence < 0:
            raise CompanionError("invalid_input", "需要当前上下文的来源序号")
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": "forget_task", "task_id": task_id, "sequence": expected_sequence})
            if replay:
                return replay
            if self._meta(connection, "sequence") != expected_sequence:
                raise CompanionError("revision_conflict", "任务资料已变化，先重新核对再忘记")
            self._forget_task_rows(connection, task_id)
            return self._receipt(connection, operation_id, digest, task_id, 0)

    def family_notice(self, boundary_type, operation_id, speaker_confirmed=False):
        if speaker_confirmed is not True:
            raise CompanionError("attribution_unconfirmed", "不确定本人时不写入个人提醒状态")
        identifier(operation_id)
        if boundary_type not in ("outside_window", "homework_switch"):
            raise CompanionError("invalid_input", "不支持的家庭约定提醒")
        try:
            local = datetime.fromisoformat(now_utc()).astimezone(timezone(timedelta(hours=8)))
        except (ValueError, TypeError) as error:
            raise CompanionError("clock_unavailable", "没有可靠当前时间，不按时段提醒") from error
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": "family_notice", "boundary_type": boundary_type})
            if replay:
                return replay | {"should_remind": False}
            key = f"notice:{local.date()}:{boundary_type}"
            if boundary_type == "outside_window":
                minute = local.hour * 60 + local.minute
                eligible = not 450 <= minute < 1260
                message = "按家里的约定，现在到休息时间了。这题可以先停在这里，明天接着来；需要时也可以和家长商量。"
            else:
                row = connection.execute("SELECT data FROM records WHERE kind='session' AND id='current'").fetchone()
                eligible = bool(row and json.loads(row[0])["homework_status"] in {"in_progress", "paused"})
                message = "家里的约定是先作业后自由安排。要先停住这题再聊吗？暂停点可以留着。"
            used = connection.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone()
            remind = eligible and not used
            if remind:
                connection.execute("INSERT INTO meta VALUES (?,?)", (key, "true"))
            return self._receipt(connection, operation_id, digest, "family-notice", 0,
                                 {"should_remind": bool(remind), "message": message if remind else "", "local_date": str(local.date())})

    def _package_metadata(self, connection, package_type):
        return {"package_type": package_type, "schema_version": SCHEMA_VERSION,
                "rule_version": RULE_VERSION, "child_id": self.child_id,
                "store_id": self.store_id, "sequence": self._meta(connection, "sequence"),
                "created_at": now_utc(), "tombstones": [dict(r) for r in connection.execute("SELECT * FROM tombstones ORDER BY kind,id")],
                "closed_tasks": [r[0] for r in connection.execute("SELECT id FROM closed_tasks ORDER BY id")]}

    def backup(self):
        with self._connection() as connection:
            connection.execute("BEGIN")
            payload = self._package_metadata(connection, "backup")
            payload["profile"] = self._meta(connection, "profile")
            payload["records"] = [self._envelope(r) for r in connection.execute("SELECT * FROM records ORDER BY kind,id")]
            return seal(payload)

    def deletion_registry(self):
        with self._connection() as connection:
            connection.execute("BEGIN")
            return seal(self._package_metadata(connection, "deletion_registry"))

    def restore(self, package, current_registry, operation_id, *, registry_is_current=False):
        identifier(operation_id)
        if registry_is_current is not True or current_registry is None:
            raise CompanionError("registry_required", "恢复须由成人提供来源端最新删除清单；不能只用旧备份")
        payload = unseal(package, "backup", self.child_id)
        registry = unseal(current_registry, "deletion_registry", self.child_id)
        backup_deleted = {(r["kind"], r["id"]) for r in payload["tombstones"]}
        registry_deleted = {(r["kind"], r["id"]) for r in registry["tombstones"]}
        if payload["store_id"] != registry["store_id"] or registry["sequence"] < payload["sequence"] or not backup_deleted <= registry_deleted or not set(payload["closed_tasks"]) <= set(registry["closed_tasks"]):
            raise CompanionError("stale_registry", "删除清单来源不符或早于备份，不恢复")
        with self._connection(write=True) as connection:
            digest, replay = self._replay(connection, operation_id, {"action": "restore", "backup": package["sha256"], "registry": current_registry["sha256"]})
            if replay:
                return replay
            key = "restored_sequence:" + payload["store_id"]
            old_sequence = connection.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
            if old_sequence and json.loads(old_sequence[0]) > registry["sequence"]:
                raise CompanionError("stale_registry", "已见过更新删除清单，拒绝回退")
            # Tombstones first, then merge. Existing live state always wins over a backup.
            for row in registry["tombstones"]:
                if row["kind"] == "task":
                    self._forget_task_rows(connection, row["id"])
                else:
                    self._erase(connection, row["kind"], row["id"], row["mode"])
            deleted = {(r["kind"], r["id"]) for r in connection.execute("SELECT kind,id FROM tombstones")}
            connection.executemany("INSERT OR IGNORE INTO closed_tasks VALUES (?)", [(task_id,) for task_id in registry["closed_tasks"]])
            closed = {r[0] for r in connection.execute("SELECT id FROM closed_tasks")}
            for row in payload["records"]:
                if (row["kind"], row["id"]) in deleted or (row["kind"] in {"session", "task", "learning_event"} and ("task", row["data"]["task_id"]) in deleted):
                    continue
                if row["kind"] in {"session", "task"} and row["data"]["task_id"] in closed:
                    row = row | {"data": row["data"] | {"homework_status": "reported_complete", "pause_point": ""}}
                if not connection.execute("SELECT 1 FROM records WHERE kind=? AND id=?", (row["kind"], row["id"])).fetchone():
                    self._save_row(connection, row["kind"], row["id"], row["data"], row["revision"], row["created_at"], row["updated_at"], row.get("sequence", 0))
            for row in connection.execute("SELECT * FROM records WHERE kind IN ('session','task')").fetchall():
                data = json.loads(row["data"])
                if data["task_id"] in closed and (data["homework_status"] != "reported_complete" or data["pause_point"]):
                    self._save_row(connection, row["kind"], row["id"], data | {"homework_status": "reported_complete", "pause_point": ""}, row["revision"] + 1, row["created_at"], now_utc())
            connection.execute("INSERT INTO meta VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, canonical(registry["sequence"])))
            floor = max(self._meta(connection, "sequence"), registry["sequence"], max((row.get("sequence", 0) for row in payload["records"]), default=0))
            connection.execute("UPDATE meta SET value=? WHERE key='sequence'", (canonical(floor),))
            return self._receipt(connection, operation_id, digest, "restore", 1)
