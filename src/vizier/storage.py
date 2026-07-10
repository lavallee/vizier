"""Corpus read/write helpers.

Flat, file-backed, one markdown file per item. Good enough up to
low-thousands of items; swap for sqlite if we outgrow it.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from .schema import Item

DEFAULT_CORPUS_ROOT = Path(__file__).resolve().parents[2] / "corpus"
CORPUS_ROOT_ENV = "VIZIER_CORPUS_ROOT"


def corpus_root() -> Path:
    override = os.getenv(CORPUS_ROOT_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_CORPUS_ROOT


def iter_items(source: str | None = None, root: Path | None = None) -> Iterator[Item]:
    r = root or corpus_root()
    pattern = f"{source}/*.md" if source else "*/*.md"
    for path in sorted(r.glob(pattern)):
        yield Item.from_file(path)


def count_by_source(root: Path | None = None) -> dict[str, int]:
    r = root or corpus_root()
    counts: dict[str, int] = {}
    for sub in sorted(p for p in r.iterdir() if p.is_dir()):
        counts[sub.name] = sum(1 for _ in sub.glob("*.md"))
    return counts
