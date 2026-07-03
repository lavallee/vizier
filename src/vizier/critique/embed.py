"""Dense embeddings for corpus retrieval.

Uses fastembed (ONNX-based local inference) so vizier has no API
dependency for retrieval. Default model is `BAAI/bge-small-en-v1.5`
(384 dims, ~130MB model file, CPU-friendly).

Embeddings are cached per-source under `corpus/.embeddings/<source>.jsonl`
keyed on `sha1(item_id + body)`. Rebuild is incremental: only items
whose hash is missing get re-embedded.

For retrieval:
- `build_source_index(source)` — ensure embeddings for every item in
  the source; return an in-memory index.
- `top_k(case_vec, index, k)` — cosine-similarity retrieval.
- `embed_query(text)` — embed one case text.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

from ..schema import Item
from ..storage import corpus_root, iter_items

MODEL_NAME = "BAAI/bge-small-en-v1.5"
DIMS = 384
CACHE_DIR = corpus_root() / ".embeddings"


@dataclass
class EmbeddedItem:
    item: Item
    vec: np.ndarray  # shape (DIMS,), L2-normalized


@lru_cache(maxsize=1)
def _model():
    # Lazy import — fastembed pulls onnxruntime and tokenizers on first use.
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=MODEL_NAME)


def _hash(item: Item) -> str:
    h = hashlib.sha1()
    h.update(item.id.encode("utf-8"))
    h.update(b"\0")
    h.update((item.body or "").encode("utf-8"))
    return h.hexdigest()[:16]


def _cache_path(source: str) -> Path:
    return CACHE_DIR / f"{source}.jsonl"


def _load_cache(source: str) -> dict[str, list[float]]:
    p = _cache_path(source)
    if not p.exists():
        return {}
    cache: dict[str, list[float]] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cache[row["hash"]] = row["embedding"]
    return cache


def _append_cache(source: str, entries: list[dict]) -> None:
    p = _cache_path(source)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")


def _embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    out = list(_model().embed(texts))
    return [v.tolist() if hasattr(v, "tolist") else list(v) for v in out]


def _item_text_for_embedding(item: Item) -> str:
    body = (item.body or "")[:3000]
    return f"{item.title}\n\n{body}"


def _normalize(v: list[float] | np.ndarray) -> np.ndarray:
    a = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(a)
    return a / n if n > 0 else a


def build_source_index(source: str, *, batch_size: int = 128) -> list[EmbeddedItem]:
    """Ensure the cache has embeddings for every item in `source`; return the index."""
    cache = _load_cache(source)
    items = list(iter_items(source=source))
    to_embed: list[tuple[Item, str, str]] = []
    for it in items:
        h = _hash(it)
        if h not in cache:
            to_embed.append((it, h, _item_text_for_embedding(it)))

    if to_embed:
        fresh: list[dict] = []
        for start in range(0, len(to_embed), batch_size):
            batch = to_embed[start:start + batch_size]
            vecs = _embed_texts([t[2] for t in batch])
            for (it, h, _), v in zip(batch, vecs, strict=True):
                cache[h] = v
                fresh.append({"hash": h, "id": it.id, "embedding": v})
        _append_cache(source, fresh)

    return [EmbeddedItem(item=it, vec=_normalize(cache[_hash(it)])) for it in items]


def build_indexes(sources: Iterable[str]) -> dict[str, list[EmbeddedItem]]:
    return {src: build_source_index(src) for src in sources}


def embed_query(text: str) -> np.ndarray:
    vec = _embed_texts([text])[0]
    return _normalize(vec)


def iter_scores(case_vec: np.ndarray, index: list[EmbeddedItem]) -> Iterator[tuple[EmbeddedItem, float]]:
    matrix = np.stack([e.vec for e in index])
    sims = matrix @ case_vec
    for e, s in zip(index, sims, strict=True):
        yield e, float(s)


def top_k(case_vec: np.ndarray, index: list[EmbeddedItem], *, k: int, min_sim: float = 0.0) -> list[tuple[EmbeddedItem, float]]:
    if not index:
        return []
    matrix = np.stack([e.vec for e in index])
    sims = matrix @ case_vec
    if k < len(sims):
        idx = np.argpartition(-sims, k)[:k]
        idx = idx[np.argsort(-sims[idx])]
    else:
        idx = np.argsort(-sims)
    return [(index[i], float(sims[i])) for i in idx if float(sims[i]) >= min_sim]


def cache_status() -> dict:
    if not CACHE_DIR.exists():
        return {}
    return {
        p.stem: sum(1 for _ in p.read_text(encoding="utf-8").splitlines() if _.strip())
        for p in CACHE_DIR.glob("*.jsonl")
    }
