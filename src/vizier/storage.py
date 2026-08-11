"""Corpus read/write helpers.

Flat, file-backed, one markdown file per item. Good enough up to
low-thousands of items; swap for sqlite if we outgrow it.

**Where the corpus lives.** Two layouts, resolved in this order:

1. `$VIZIER_CORPUS_ROOT` — an explicit override, always wins.
2. `<repo>/corpus/` — a source checkout. The full corpus lives here,
   including any third-party sources rebuilt by `vizier ingest`.
3. `vizier/corpus/` inside the installed package — what ships in the
   wheel: vizier's own authored content only (the 43 chart-form
   patterns, the rubrics, the FT-vocabulary parse, the house
   principles). This is what a `pip install datavizier` reads.

**Where the index lives.** The SQLite index is a rebuildable artifact,
never source of truth. In a checkout it sits next to the corpus at
`corpus/.vizier.db` (as it always has). When the corpus is the packaged
one, site-packages may be read-only and is the wrong place for user
state, so the index goes to a per-user cache directory instead.
`$VIZIER_DB_PATH` overrides either.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from .schema import Item

#: The corpus in a source checkout — the full one, third-party included.
REPO_CORPUS_ROOT = Path(__file__).resolve().parents[2] / "corpus"
#: The corpus that ships in the wheel — vizier's own authored content only.
PACKAGED_CORPUS_ROOT = Path(__file__).resolve().parent / "corpus"

# Back-compat alias: this used to be the only root vizier knew about.
DEFAULT_CORPUS_ROOT = REPO_CORPUS_ROOT

CORPUS_ROOT_ENV = "VIZIER_CORPUS_ROOT"
DB_PATH_ENV = "VIZIER_DB_PATH"
DB_FILENAME = ".vizier.db"


def has_corpus_content(path: Path) -> bool:
    """True if `path` holds corpus items, not just an empty directory.

    Existence alone is not enough. vizier 0.1.0 created an empty `corpus/`
    next to site-packages as a side effect of opening its index, and that
    directory survives an upgrade — so an installed 0.2.0 mistook it for a
    source checkout and read a corpus of nothing while the real packaged one
    sat unused. Ask what's inside instead.
    """
    return path.is_dir() and any(path.glob("*/*.md"))


def corpus_root() -> Path:
    override = os.getenv(CORPUS_ROOT_ENV)
    if override:
        # An explicit path is the caller's business — honored even if empty,
        # since `vizier ingest` has to be able to fill a fresh one.
        return Path(override).expanduser().resolve()
    if has_corpus_content(REPO_CORPUS_ROOT):
        return REPO_CORPUS_ROOT
    return PACKAGED_CORPUS_ROOT


def is_packaged_corpus(root: Path | None = None) -> bool:
    """True when we're reading the corpus that shipped inside the wheel."""
    return (root or corpus_root()) == PACKAGED_CORPUS_ROOT


def cache_dir() -> Path:
    """Per-user cache directory for rebuildable vizier artifacts."""
    base = os.getenv("XDG_CACHE_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".cache"
    return root / "vizier"


def db_path() -> Path:
    """Absolute path to the corpus index for the active corpus root."""
    override = os.getenv(DB_PATH_ENV)
    if override:
        return Path(override).expanduser().resolve()
    root = corpus_root()
    if is_packaged_corpus(root):
        # site-packages is read-only on plenty of installs, and is never
        # the right home for user state anyway.
        return cache_dir() / "corpus.db"
    return root / DB_FILENAME


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
