"""SQLite-backed corpus index for vizier.

Three-table design:
  - `items` holds one row per corpus markdown file (all frontmatter + body)
  - `items_fts` is an FTS5 virtual table mirroring title + body
  - `embeddings` stores one float32 blob per `(item_key, model)` pair

Item key is `<source>/<item_id>` so the DB is snapshot-addressable.

The markdown files on disk remain source of truth; this DB is a
rebuildable index. `vizier.db.build.populate()` is idempotent — it reads
`body_hash` per item and only re-embeds when a body changes.

Public entrypoints:

    from vizier import db
    db.connect()                     # -> sqlite3.Connection (ensures schema)
    db.build.populate()              # walk corpus/ and upsert
    db.query.search("bar chart", k=10)
    db.query.find_similar(text, k=8, source="junkcharts")
    db.query.lookup("weaver", "principle-show-the-evidence")
"""

from __future__ import annotations

from . import build, query, schema
from .connect import DB_PATH, connect

__all__ = ["DB_PATH", "connect", "build", "query", "schema"]
