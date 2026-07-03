"""Corpus manifest — a reproducible snapshot of corpus state.

Written after each `vizier ingest all` to `corpus/manifest.json`.
Records per-source: item count, total body bytes, and a hash that
covers all items' (id, title, tier, body). Two snapshots with the
same hash describe the same corpus.

Why we want it: the user plans to build a critique emitter and
track how its judgment quality evolves as the corpus and rubric
scaffolding grow. The manifest is the minimum scaffolding for
"which corpus state was this evaluation run against?"
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .schema import Item
from .storage import corpus_root, iter_items


def _item_hash_input(item: Item) -> str:
    return f"{item.id}\n{item.title}\n{item.tier or ''}\n{item.body}"


def build(root: Path | None = None) -> dict:
    r = root or corpus_root()
    sources: dict[str, dict] = {}
    total_items = 0
    total_bytes = 0
    hasher = hashlib.sha256()

    # Iterate deterministically (sorted paths)
    source_dirs = sorted(p for p in r.iterdir() if p.is_dir())
    for sdir in source_dirs:
        source = sdir.name
        tier_counts: Counter[str] = Counter()
        type_counts: Counter[str] = Counter()
        year_span: list[int] = []
        src_bytes = 0
        count = 0
        src_hash = hashlib.sha256()
        for item in sorted(iter_items(source=source, root=r), key=lambda i: i.id):
            count += 1
            h_input = _item_hash_input(item).encode("utf-8")
            src_hash.update(h_input)
            hasher.update(h_input)
            src_bytes += len(item.body.encode("utf-8"))
            if item.tier:
                tier_counts[item.tier] += 1
            type_counts[item.type] += 1
            if item.year is not None:
                year_span.append(item.year)
        sources[source] = {
            "items": count,
            "body_bytes": src_bytes,
            "tiers": dict(tier_counts),
            "types": dict(type_counts),
            "year_min": min(year_span) if year_span else None,
            "year_max": max(year_span) if year_span else None,
            "hash": src_hash.hexdigest()[:16],
        }
        total_items += count
        total_bytes += src_bytes

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_items": total_items,
        "total_body_bytes": total_bytes,
        "corpus_hash": hasher.hexdigest()[:16],
        "sources": sources,
    }


def write(root: Path | None = None) -> Path:
    r = root or corpus_root()
    manifest = build(r)
    out = r / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return out


if __name__ == "__main__":
    path = write()
    print(f"wrote {path}")
