"""SQLite connection helper. Applies schema on first open."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..storage import corpus_root
from .schema import SCHEMA_SQL, SCHEMA_VERSION

DB_PATH = corpus_root() / ".vizier.db"


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Open (or create) the vizier corpus DB. Applies schema idempotently."""
    db_path = path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    cur.execute("SELECT value FROM meta WHERE key='schema_version'")
    row = cur.fetchone()
    if row and int(row[0]) == SCHEMA_VERSION:
        return
    cur.executescript(SCHEMA_SQL)
    cur.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)",
        (str(SCHEMA_VERSION),),
    )
    conn.commit()
