"""Corpus → SQLite populator.

Idempotent: walks every `corpus/<source>/*.md`, upserts items, rebuilds
the FTS index for changed rows, and (re-)embeds any item whose body
hash changed. Uses fastembed via `vizier.critique.embed` so the retrieval
stack shares one embedding model.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

import numpy as np

from ..schema import Item
from ..storage import corpus_root, iter_items
from .connect import connect


EMBED_MODEL = "bge-small-en-v1.5"   # stable label; bound to fastembed model
EMBED_DIMS = 384


def _body_hash(item: Item) -> str:
    h = hashlib.sha1()
    h.update(item.id.encode("utf-8"))
    h.update(b"\0")
    h.update((item.body or "").encode("utf-8"))
    return h.hexdigest()[:16]


def _item_to_row(item: Item) -> dict:
    return {
        "key": f"{item.source}/{item.id}",
        "source": item.source,
        "item_id": item.id,
        "type": item.type,
        "title": item.title,
        "url": item.url,
        "body": item.body or "",
        "body_hash": _body_hash(item),
        "tier": item.tier,
        "year": item.year,
        "category": item.category,
        "organization": item.organization,
        "country": item.country,
        "artifact_url": item.artifact_url,
        "methodology_url": item.methodology_url,
        "publication_date": (item.details or {}).get("publication_date"),
        "tags_json": json.dumps(item.tags or []),
        "creators_json": json.dumps(item.creators or []),
        "axes_json": json.dumps(item.axes or []),
        "details_json": json.dumps(item.details or {}),
        "fetched_at": item.fetched_at.isoformat() if item.fetched_at else "",
    }


_UPSERT_ITEM_SQL = """
INSERT INTO items (
    key, source, item_id, type, title, url, body, body_hash,
    tier, year, category, organization, country,
    artifact_url, methodology_url, publication_date,
    tags_json, creators_json, axes_json, details_json, fetched_at
) VALUES (
    :key, :source, :item_id, :type, :title, :url, :body, :body_hash,
    :tier, :year, :category, :organization, :country,
    :artifact_url, :methodology_url, :publication_date,
    :tags_json, :creators_json, :axes_json, :details_json, :fetched_at
)
ON CONFLICT(key) DO UPDATE SET
    source=excluded.source,
    item_id=excluded.item_id,
    type=excluded.type,
    title=excluded.title,
    url=excluded.url,
    body=excluded.body,
    body_hash=excluded.body_hash,
    tier=excluded.tier,
    year=excluded.year,
    category=excluded.category,
    organization=excluded.organization,
    country=excluded.country,
    artifact_url=excluded.artifact_url,
    methodology_url=excluded.methodology_url,
    publication_date=excluded.publication_date,
    tags_json=excluded.tags_json,
    creators_json=excluded.creators_json,
    axes_json=excluded.axes_json,
    details_json=excluded.details_json,
    fetched_at=excluded.fetched_at
"""


def _upsert_items(conn: sqlite3.Connection) -> tuple[int, int, int]:
    """Walk corpus/, upsert items, mirror to FTS. Returns (written, new, changed)."""
    cur = conn.cursor()

    # Snapshot current keys + hashes so we can detect new/changed/removed
    cur.execute("SELECT key, body_hash FROM items")
    existing: dict[str, str] = {row["key"]: row["body_hash"] for row in cur.fetchall()}
    seen_keys: set[str] = set()
    new_count = 0
    changed_count = 0
    written = 0

    for item in iter_items():
        row = _item_to_row(item)
        prev = existing.get(row["key"])
        if prev is None:
            new_count += 1
        elif prev != row["body_hash"]:
            changed_count += 1
        cur.execute(_UPSERT_ITEM_SQL, row)
        seen_keys.add(row["key"])
        written += 1

    # Handle deletions: items present in DB but no longer on disk
    stale = set(existing) - seen_keys
    for key in stale:
        cur.execute("DELETE FROM items WHERE key = ?", (key,))

    # Rebuild FTS snapshot. Simpler than trigger-based maintenance and
    # cheap at our scale (~6.5K rows fit in well under a second).
    cur.execute("DELETE FROM items_fts")
    cur.execute(
        "INSERT INTO items_fts (rowid, key, title, body) "
        "SELECT rowid, key, title, body FROM items"
    )
    conn.commit()
    return written, new_count, changed_count


def _items_needing_embedding(conn: sqlite3.Connection, model: str) -> list[tuple[str, str, str]]:
    """Return (key, body_hash, text_for_embedding) for items with no current embedding."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT i.key, i.body_hash, i.title, i.body
          FROM items i
          LEFT JOIN embeddings e
                 ON e.key = i.key
                AND e.model = ?
         WHERE e.key IS NULL
            OR e.body_hash != i.body_hash
        """,
        (model,),
    )
    out: list[tuple[str, str, str]] = []
    for row in cur.fetchall():
        text = f"{row['title']}\n\n{(row['body'] or '')[:3000]}"
        out.append((row["key"], row["body_hash"], text))
    return out


def _embed_and_store(
    conn: sqlite3.Connection,
    pending: list[tuple[str, str, str]],
    *,
    model: str,
    dims: int,
    batch_size: int = 128,
    progress_every: int = 256,
) -> int:
    """Embed pending texts via fastembed and write to `embeddings`."""
    if not pending:
        return 0
    from ..critique import embed as E  # reuse the fastembed handle

    cur = conn.cursor()
    n_written = 0
    t0 = time.monotonic()
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        texts = [text for _, _, text in batch]
        vecs = E._embed_texts(texts)
        rows = []
        for (key, body_hash, _), v in zip(batch, vecs, strict=True):
            arr = np.asarray(v, dtype=np.float32)
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            rows.append((key, model, body_hash, dims, arr.tobytes()))
        cur.executemany(
            "INSERT OR REPLACE INTO embeddings (key, model, body_hash, dims, vec) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        n_written += len(rows)
        if n_written % progress_every == 0 or n_written == len(pending):
            rate = n_written / max(time.monotonic() - t0, 1e-3)
            print(f"  embedded {n_written}/{len(pending)} ({rate:.1f} items/s)", flush=True)
    return n_written


def populate(*, embed: bool = False) -> dict:
    """Walk corpus/, upsert items, and (optionally) embed new/changed bodies.

    Default is no embedding — BM25 search is immediately usable, and the
    slow per-item vector computation can run separately via
    `populate_embeddings_only()` so a fresh clone isn't blocked for minutes.
    """
    from .connect import DB_PATH
    conn = connect()
    try:
        written, new, changed = _upsert_items(conn)
        info: dict = {
            "db_path": str(DB_PATH),
            "items_written": written,
            "items_new": new,
            "items_changed": changed,
        }
        if embed:
            pending = _items_needing_embedding(conn, EMBED_MODEL)
            info["embeddings_pending"] = len(pending)
            info["embeddings_written"] = _embed_and_store(
                conn, pending, model=EMBED_MODEL, dims=EMBED_DIMS,
            )
        return info
    finally:
        conn.close()


def populate_embeddings_only() -> dict:
    """Fill in any missing embeddings for items already in the DB.

    Assumes `populate()` has run; idempotent across repeated invocations.
    Re-embeds items whose body hash changed since last embed.
    """
    from .connect import DB_PATH
    conn = connect()
    try:
        pending = _items_needing_embedding(conn, EMBED_MODEL)
        return {
            "db_path": str(DB_PATH),
            "embeddings_pending": len(pending),
            "embeddings_written": _embed_and_store(
                conn, pending, model=EMBED_MODEL, dims=EMBED_DIMS,
            ),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(populate(), indent=2))
