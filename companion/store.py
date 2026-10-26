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
from datetime import datetime, timezone
from pathlib import Path

from . import RULE_VERSION, SCHEMA_VERSION
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
                PRAGMA user_version=3;
                PRAGMA journal_mode=DELETE;
                PRAGMA secure_delete=ON;
                CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE records (
                    kind TEXT NOT NULL, id TEXT NOT NULL, data TEXT NOT NULL,
                    revision INTEGER NOT NULL, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, PRIMARY KEY (kind, id));
                CREATE TABLE operations (
                    id TEXT PRIMARY KEY, digest TEXT NOT NULL, receipt TEXT NOT NULL);
                CREATE TABLE tombstones (
                    kind TEXT NOT NULL, id TEXT NOT NULL, mode TEXT NOT NULL,
                    deleted_at TEXT NOT NULL, PRIMARY KEY (kind, id));
            """)
            connection.execute("BEGIN IMMEDIATE")
            metadata = {"schema_version": SCHEMA_VERSION, "rule_version": RULE_VERSION,
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
            if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
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

    def _receipt(self, connection, operation_id, digest, record_id, revision):
        sequence = self._meta(connection, "sequence") + 1
        connection.execute("UPDATE meta SET value=? WHERE key='sequence'", (canonical(sequence),))
        receipt = {"ok": True, "id": record_id, "revision": revision, "sequence": sequence,
                   "operation_id": operation_id, "replayed": False}
        connection.execute("INSERT INTO operations VALUES (?,?,?)", (operation_id, digest, canonical(receipt)))
        return receipt

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
            stamp = now_utc()
            connection.execute("INSERT INTO records VALUES (?,?,?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET data=excluded.data, revision=excluded.revision, updated_at=excluded.updated_at",
                               (kind, record_id, canonical(data), revision + 1, old["created_at"] if old else stamp, stamp))
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
            row = connection.execute("SELECT * FROM records WHERE kind='session' AND id='current'").fetchone()
            return {"attribution": "bound_account", "child_id": self.child_id,
                    "profile": self._meta(connection, "profile"),
                    "session": self._envelope(row) if row else None, "events": [],
                    "sequence": self._meta(connection, "sequence")}
