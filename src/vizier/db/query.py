"""Read-side queries against the vizier corpus DB.

Three primary entry points:

    search(q, *, k=10, **filters)          -- BM25 full-text (FTS5)
    find_similar(text, *, k=8, **filters)  -- embedding cosine similarity
    lookup(source, item_id)                -- direct key lookup

Filters accepted by search/find_similar: `source`, `type`, `tier`,
`year_from`, `year_to`, `tags` (intersection, OR semantics), `exclude_sources`.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from .build import EMBED_DIMS, EMBED_MODEL
from .connect import connect


@dataclass
class Hit:
    key: str
    source: str
    item_id: str
    type: str
    title: str
    url: str | None
    body: str
    tier: str | None
    year: int | None
    organization: str | None
    tags: list[str]
    creators: list[str]
    details: dict
    score: float
    why: str

    def to_dict(self, *, body_chars: int | None = None) -> dict:
        out: dict[str, Any] = {
            "key": self.key,
            "source": self.source,
            "item_id": self.item_id,
            "type": self.type,
            "title": self.title,
            "url": self.url,
            "tier": self.tier,
            "year": self.year,
            "organization": self.organization,
            "tags": self.tags,
            "creators": self.creators,
            "score": round(self.score, 4),
            "why": self.why,
        }
        if body_chars is None:
            out["body"] = self.body
        else:
            body = self.body or ""
            out["body"] = body[:body_chars] + ("…" if len(body) > body_chars else "")
        return out


def _row_to_hit(row: sqlite3.Row, score: float, why: str) -> Hit:
    return Hit(
        key=row["key"],
        source=row["source"],
        item_id=row["item_id"],
        type=row["type"],
        title=row["title"],
        url=row["url"],
        body=row["body"],
        tier=row["tier"],
        year=row["year"],
        organization=row["organization"],
        tags=json.loads(row["tags_json"] or "[]"),
        creators=json.loads(row["creators_json"] or "[]"),
        details=json.loads(row["details_json"] or "{}"),
        score=score,
        why=why,
    )


def _apply_filters(
    base_sql: str,
    *,
    source: str | None = None,
    sources: Sequence[str] | None = None,
    exclude_sources: Sequence[str] | None = None,
    type: str | None = None,
    tier: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    tags: Sequence[str] | None = None,
) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if source:
        clauses.append("i.source = ?")
        params.append(source)
    if sources:
        clauses.append(f"i.source IN ({','.join('?' for _ in sources)})")
        params.extend(sources)
    if exclude_sources:
        clauses.append(f"i.source NOT IN ({','.join('?' for _ in exclude_sources)})")
        params.extend(exclude_sources)
    if type:
        clauses.append("i.type = ?")
        params.append(type)
    if tier:
        clauses.append("i.tier = ?")
        params.append(tier)
    if year_from is not None:
        clauses.append("i.year >= ?")
        params.append(year_from)
    if year_to is not None:
        clauses.append("i.year <= ?")
        params.append(year_to)
    if tags:
        # OR across tags — any tag match qualifies. Tag JSON stored as
        # `["foo","bar"]`; use json_each for intersection.
        tag_list = list(tags)
        clauses.append(
            "EXISTS (SELECT 1 FROM json_each(i.tags_json) t "
            f"WHERE t.value IN ({','.join('?' for _ in tag_list)}))"
        )
        params.extend(tag_list)
    if clauses:
        sep = " AND " if " WHERE " in base_sql.upper() else " WHERE "
        base_sql = base_sql + sep + " AND ".join(clauses)
    return base_sql, params


_FTS_OPERATORS = {"OR", "AND", "NOT", "NEAR"}


def _normalize_fts_query(q: str) -> str:
    """Make casual queries safe for FTS5 MATCH without breaking advanced syntax.

    FTS5's default tokenizer splits `forecast-cone` in indexed text into
    two tokens `forecast` `cone`. A bare query `forecast-cone`, though,
    is parsed as `forecast -cone` (cone as NOT) which trips users and
    returns empty. Worse, `'` can nudge the parser into column-qualifier
    mode.  This helper normalizes the *query* to match how documents
    were *indexed*:

      - preserves double-quoted phrases (`"exact phrase"` passes through
        verbatim)
      - preserves FTS5 operator keywords (`OR`, `AND`, `NOT`, `NEAR`,
        `NEAR(...)`)
      - for any other token: replace `-` and `'` with spaces (splitting
        into multiple AND-combined tokens, matching tokenizer behavior)
      - tokens still containing `:` or `.` get wrapped in quotes so
        they can't be parsed as column qualifiers or operators
      - drops empty tokens

    Power users who want strict phrase match can always pass
    `"forecast-cone"` explicitly — that's preserved.
    """
    if not q:
        return q
    out: list[str] = []
    i, n = 0, len(q)
    while i < n:
        c = q[i]
        if c.isspace():
            i += 1
            continue
        # Already-quoted phrase — pass through verbatim, including quotes
        if c == '"':
            j = i + 1
            while j < n and q[j] != '"':
                j += 1
            end = j + 1 if j < n else j
            out.append(q[i:end])
            i = end
            continue
        # Read a bare token
        j = i
        while j < n and not q[j].isspace() and q[j] != '"':
            j += 1
        tok = q[i:j]
        i = j
        if not tok:
            continue
        upper = tok.upper()
        if upper in _FTS_OPERATORS or (
            upper.startswith("NEAR(") and tok.endswith(")")
        ):
            out.append(tok)
            continue
        # Split on hyphens/apostrophes to match how the FTS tokenizer
        # indexed the corresponding text.
        for part in tok.replace("-", " ").replace("'", " ").split():
            if not part:
                continue
            # Still-dangerous punctuation (`:` column qualifier, `.` operator
            # prefix) → quote the part so FTS5 treats it as literal phrase.
            if any(ch in part for ch in ":.") :
                out.append(f'"{part.replace(chr(34), chr(34) * 2)}"')
            else:
                out.append(part)
    return " ".join(out)


def search(
    q: str,
    *,
    k: int = 10,
    conn: sqlite3.Connection | None = None,
    **filters: Any,
) -> list[Hit]:
    """BM25-ranked FTS5 search over title + body.

    Casual queries work without thinking about FTS5 syntax — hyphens,
    apostrophes, dots, and colons in tokens are auto-quoted. Advanced
    users can still use operators: `"exact phrase"`, `A OR B`,
    `NEAR(foo bar, 5)`. Title matches are boosted 2× via `bm25`.
    """
    q_normalized = _normalize_fts_query(q)
    own = conn is None
    conn = conn or connect()
    try:
        sql = (
            "SELECT i.*, bm25(items_fts, 0.0, 2.0, 1.0) AS rank_score "
            "FROM items_fts "
            "JOIN items i ON i.rowid = items_fts.rowid "
            "WHERE items_fts MATCH ?"
        )
        params: list[Any] = [q_normalized]
        sql, extra_params = _apply_filters(sql, **filters)
        params.extend(extra_params)
        sql += " ORDER BY rank_score LIMIT ?"
        params.append(k)
        rows = conn.execute(sql, params).fetchall()
        return [
            # FTS5 BM25 returns negative values where lower is better; flip sign
            # so "higher score = better" is consistent across search/find_similar.
            _row_to_hit(r, score=-float(r["rank_score"]), why="fts5")
            for r in rows
        ]
    finally:
        if own:
            conn.close()


def _embed_query(text: str) -> np.ndarray:
    from ..critique import embed as E  # shares the fastembed handle
    arr = np.asarray(E._embed_texts([text])[0], dtype=np.float32)
    n = np.linalg.norm(arr)
    return arr / n if n > 0 else arr


def _load_matrix(conn: sqlite3.Connection, model: str, **filters: Any) -> tuple[list[sqlite3.Row], np.ndarray]:
    """Fetch (rows, matrix) for the requested filter subset.

    `rows[i]` corresponds to `matrix[i]`. Matrix is L2-normalized at
    populate-time, so cosine similarity = dot product.
    """
    sql = (
        "SELECT i.*, e.vec, e.dims FROM items i "
        "JOIN embeddings e ON e.key = i.key "
        "WHERE e.model = ?"
    )
    params: list[Any] = [model]
    sql, extra_params = _apply_filters(sql, **filters)
    params.extend(extra_params)
    rows = conn.execute(sql, params).fetchall()
    if not rows:
        return [], np.empty((0, EMBED_DIMS), dtype=np.float32)
    dims = rows[0]["dims"]
    matrix = np.empty((len(rows), dims), dtype=np.float32)
    for i, r in enumerate(rows):
        matrix[i] = np.frombuffer(r["vec"], dtype=np.float32)
    return rows, matrix


def find_similar(
    text: str,
    *,
    k: int = 8,
    min_sim: float = 0.25,
    conn: sqlite3.Connection | None = None,
    model: str = EMBED_MODEL,
    **filters: Any,
) -> list[Hit]:
    """Embedding cosine-similarity retrieval.

    Uses the per-item fastembed vectors stored in `embeddings`. For ~10K
    items this is a single matmul and is fast enough to avoid introducing
    ANN infrastructure.
    """
    own = conn is None
    conn = conn or connect()
    try:
        rows, matrix = _load_matrix(conn, model, **filters)
        if matrix.shape[0] == 0:
            return []
        q_vec = _embed_query(text)
        sims = matrix @ q_vec
        if k < sims.shape[0]:
            idx = np.argpartition(-sims, k)[:k]
            idx = idx[np.argsort(-sims[idx])]
        else:
            idx = np.argsort(-sims)
        out: list[Hit] = []
        for i in idx:
            s = float(sims[i])
            if s < min_sim:
                continue
            out.append(_row_to_hit(rows[i], score=s, why=f"sim={s:.3f}"))
            if len(out) >= k:
                break
        return out
    finally:
        if own:
            conn.close()


def lookup(
    source: str,
    item_id: str,
    *,
    conn: sqlite3.Connection | None = None,
) -> Hit | None:
    own = conn is None
    conn = conn or connect()
    try:
        r = conn.execute(
            "SELECT * FROM items WHERE key = ?",
            (f"{source}/{item_id}",),
        ).fetchone()
        return _row_to_hit(r, score=1.0, why="lookup") if r else None
    finally:
        if own:
            conn.close()


def list_sources(*, conn: sqlite3.Connection | None = None) -> list[dict]:
    """Source-level counts + type breakdown."""
    own = conn is None
    conn = conn or connect()
    try:
        sources = conn.execute(
            "SELECT source, COUNT(*) AS n FROM items GROUP BY source ORDER BY n DESC"
        ).fetchall()
        out: list[dict] = []
        for s in sources:
            types = {
                r["type"]: r["n"]
                for r in conn.execute(
                    "SELECT type, COUNT(*) AS n FROM items WHERE source = ? GROUP BY type",
                    (s["source"],),
                ).fetchall()
            }
            out.append({"source": s["source"], "count": s["n"], "types": types})
        return out
    finally:
        if own:
            conn.close()


def list_principles(
    *,
    stage: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> list[Hit]:
    """Return weaver principles, optionally filtered by workflow stage."""
    own = conn is None
    conn = conn or connect()
    try:
        rows = conn.execute(
            "SELECT * FROM items WHERE source = 'weaver' AND type = 'principle' ORDER BY title"
        ).fetchall()
        hits = [_row_to_hit(r, score=1.0, why="principle") for r in rows]
        if stage:
            s = stage.lower()
            hits = [
                h for h in hits
                if (h.details.get("stage") or "").lower() == s
            ]
        return hits
    finally:
        if own:
            conn.close()


def list_rubrics(*, conn: sqlite3.Connection | None = None) -> list[Hit]:
    """Return canonical rubric items (Cairo pillars, FT vocab, other rubrics)."""
    own = conn is None
    conn = conn or connect()
    try:
        rows = conn.execute(
            "SELECT * FROM items WHERE type = 'rubric' OR source = 'rubrics' "
            "OR source = 'ft-vocab' ORDER BY source, title"
        ).fetchall()
        return [_row_to_hit(r, score=1.0, why="rubric") for r in rows]
    finally:
        if own:
            conn.close()


def get_pattern(
    pattern_id: str,
    *,
    transclude: bool = True,
    conn: sqlite3.Connection | None = None,
) -> dict | None:
    """Return a chart_pattern item with its references resolved.

    When `transclude=True`, alternatives and canonical_examples are
    replaced with full-object payloads (title, capsule, url, ...) so
    a caller sees one-hop neighbors without a second query. Set
    `transclude=False` for a bare-reference payload.
    """
    own = conn is None
    conn = conn or connect()
    try:
        hit = lookup("chart-forms", pattern_id, conn=conn)
        if hit is None or hit.type != "chart_pattern":
            return None
        out: dict[str, Any] = hit.to_dict(body_chars=None)
        # Expose the source-local id as `id` (not just `item_id`) — nicer
        # for callers, matches how patterns are referenced in alternatives.
        out["id"] = hit.item_id
        # Hit.to_dict doesn't include details — grab directly from the Hit
        details = hit.details or {}
        for k in (
            "purpose_families", "capsule", "when_to_use", "when_not_to_use",
            "common_mistakes", "reading_checklist",
        ):
            out[k] = details.get(k)
        out["alternatives"] = list(details.get("alternatives") or [])
        out["canonical_examples"] = list(details.get("canonical_examples") or [])
        out["antipattern_examples"] = list(details.get("antipattern_examples") or [])
        out["related_principles"] = list(details.get("related_principles") or [])
        out["related_projects"] = list(details.get("related_projects") or [])

        if not transclude:
            return out

        # Resolve alternatives
        resolved_alts: list[dict] = []
        for alt in out["alternatives"]:
            alt_id = alt.get("id") if isinstance(alt, dict) else alt
            alt_when = alt.get("when") if isinstance(alt, dict) else None
            alt_hit = lookup("chart-forms", alt_id, conn=conn)
            if alt_hit is None:
                resolved_alts.append({"id": alt_id, "when": alt_when, "_missing": True})
                continue
            alt_details = alt_hit.details or {}
            resolved_alts.append({
                "id": alt_id,
                "title": alt_hit.title,
                "when": alt_when,
                "capsule": (alt_details.get("capsule") or "").strip(),
                "purpose_families": alt_details.get("purpose_families") or [],
            })
        out["alternatives"] = resolved_alts

        # Resolve canonical_examples (key = "source/item_id")
        resolved_ex: list[dict] = []
        for key in out["canonical_examples"]:
            parts = str(key).split("/", 1)
            if len(parts) != 2:
                continue
            h = lookup(parts[0], parts[1], conn=conn)
            if h:
                resolved_ex.append({
                    "key": f"{h.source}/{h.item_id}",
                    "title": h.title,
                    "url": h.url,
                })
        out["canonical_examples"] = resolved_ex

        resolved_anti: list[dict] = []
        for key in out["antipattern_examples"]:
            parts = str(key).split("/", 1)
            if len(parts) != 2:
                continue
            h = lookup(parts[0], parts[1], conn=conn)
            if h:
                resolved_anti.append({
                    "key": f"{h.source}/{h.item_id}",
                    "title": h.title,
                    "url": h.url,
                })
        out["antipattern_examples"] = resolved_anti

        return out
    finally:
        if own:
            conn.close()


def list_patterns(
    *,
    purpose_family: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> list[dict]:
    """Return a compact list of chart_pattern items.

    Each entry is `{id, title, capsule, purpose_families}` — enough for
    an agent to narrow down. Pass `purpose_family` (e.g. 'Flow',
    'Part-to-whole') to filter.
    """
    own = conn is None
    conn = conn or connect()
    try:
        rows = conn.execute(
            "SELECT * FROM items WHERE source = 'chart-forms' "
            "AND type = 'chart_pattern' ORDER BY title"
        ).fetchall()
        out: list[dict] = []
        for r in rows:
            details = json.loads(r["details_json"] or "{}")
            families = details.get("purpose_families") or []
            if purpose_family and purpose_family not in families:
                continue
            out.append({
                "id": r["item_id"],
                "title": r["title"],
                "capsule": (details.get("capsule") or "").strip(),
                "purpose_families": families,
            })
        return out
    finally:
        if own:
            conn.close()


def stats(*, conn: sqlite3.Connection | None = None) -> dict:
    own = conn is None
    conn = conn or connect()
    try:
        n_items = conn.execute("SELECT COUNT(*) AS n FROM items").fetchone()["n"]
        n_emb = conn.execute(
            "SELECT COUNT(*) AS n FROM embeddings WHERE model = ?", (EMBED_MODEL,)
        ).fetchone()["n"]
        by_source = list_sources(conn=conn)
        return {
            "items": n_items,
            "embeddings": n_emb,
            "embedding_model": EMBED_MODEL,
            "sources": by_source,
        }
    finally:
        if own:
            conn.close()
