"""SQL schema for the vizier corpus DB."""

from __future__ import annotations

SCHEMA_VERSION = 1

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
    key             TEXT    PRIMARY KEY,           -- "<source>/<item_id>"
    source          TEXT    NOT NULL,
    item_id         TEXT    NOT NULL,
    type            TEXT    NOT NULL,
    title           TEXT    NOT NULL,
    url             TEXT,
    body            TEXT    NOT NULL,
    body_hash       TEXT    NOT NULL,
    tier            TEXT,
    year            INTEGER,
    category        TEXT,
    organization    TEXT,
    country         TEXT,
    artifact_url    TEXT,
    methodology_url TEXT,
    publication_date TEXT,
    tags_json       TEXT    NOT NULL DEFAULT '[]',
    creators_json   TEXT    NOT NULL DEFAULT '[]',
    axes_json       TEXT    NOT NULL DEFAULT '[]',
    details_json    TEXT    NOT NULL DEFAULT '{}',
    fetched_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_items_source ON items(source);
CREATE INDEX IF NOT EXISTS idx_items_type   ON items(type);
CREATE INDEX IF NOT EXISTS idx_items_tier   ON items(tier);
CREATE INDEX IF NOT EXISTS idx_items_year   ON items(year);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    key UNINDEXED,
    title,
    body,
    tokenize = 'porter unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS embeddings (
    key        TEXT NOT NULL,
    model      TEXT NOT NULL,
    body_hash  TEXT NOT NULL,
    dims       INTEGER NOT NULL,
    vec        BLOB    NOT NULL,
    PRIMARY KEY (key, model),
    FOREIGN KEY (key) REFERENCES items(key) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model);
"""
