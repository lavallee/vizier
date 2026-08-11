"""Storage helpers — corpus root and index location.

The two layouts these cover are the two vizier actually ships in: a source
checkout (repo `corpus/`, index beside it) and an installed wheel (packaged
`vizier/corpus/`, index in the user cache because site-packages may be
read-only). A regression here is invisible in the repo and total in the wild.
"""

from __future__ import annotations

from pathlib import Path

from vizier import storage


def test_corpus_root_prefers_the_repo_corpus_in_a_checkout(monkeypatch):
    monkeypatch.delenv("VIZIER_CORPUS_ROOT", raising=False)
    assert storage.corpus_root() == Path(storage.__file__).resolve().parents[2] / "corpus"


def test_corpus_root_can_be_overridden(monkeypatch, tmp_path):
    custom = tmp_path / "private-corpus"
    monkeypatch.setenv("VIZIER_CORPUS_ROOT", str(custom))
    assert storage.corpus_root() == custom.resolve()


def test_corpus_root_falls_back_to_the_packaged_corpus(monkeypatch, tmp_path):
    """An installed wheel has no repo corpus; the packaged one takes over."""
    monkeypatch.delenv("VIZIER_CORPUS_ROOT", raising=False)
    monkeypatch.setattr(storage, "REPO_CORPUS_ROOT", tmp_path / "nope" / "corpus")
    assert storage.corpus_root() == storage.PACKAGED_CORPUS_ROOT
    assert storage.is_packaged_corpus()


def test_an_empty_corpus_dir_is_not_mistaken_for_a_checkout(monkeypatch, tmp_path):
    """The 0.1.0 → 0.2.0 upgrade trap.

    0.1.0 created an empty `corpus/` beside site-packages as a side effect of
    opening its index. It survives the upgrade, and an existence check alone
    reads it as a source checkout — leaving the user with a corpus of nothing
    and the packaged one untouched.
    """
    monkeypatch.delenv("VIZIER_CORPUS_ROOT", raising=False)
    leftover = tmp_path / "corpus"
    leftover.mkdir()
    (leftover / ".vizier.db").write_bytes(b"")
    monkeypatch.setattr(storage, "REPO_CORPUS_ROOT", leftover)

    assert storage.corpus_root() == storage.PACKAGED_CORPUS_ROOT
    assert storage.is_packaged_corpus()

    # …but the same path with real items in it is a checkout.
    (leftover / "chart-forms").mkdir()
    (leftover / "chart-forms" / "bar-chart.md").write_text("---\n---\n")
    assert storage.corpus_root() == leftover


def test_packaged_corpus_ships_the_authored_sources():
    """The wheel's force-include allowlist, asserted from the source side."""
    authored = {"chart-forms", "ft-vocab", "rubrics", "principles"}
    present = {p.name for p in storage.REPO_CORPUS_ROOT.iterdir() if p.is_dir()}
    assert authored <= present
    assert len(list((storage.REPO_CORPUS_ROOT / "chart-forms").glob("*.md"))) == 43


def test_db_path_sits_beside_a_checkout_corpus(monkeypatch, tmp_path):
    monkeypatch.delenv("VIZIER_DB_PATH", raising=False)
    monkeypatch.setenv("VIZIER_CORPUS_ROOT", str(tmp_path))
    assert storage.db_path() == tmp_path.resolve() / storage.DB_FILENAME


def test_db_path_moves_to_the_cache_for_a_packaged_corpus(monkeypatch, tmp_path):
    monkeypatch.delenv("VIZIER_DB_PATH", raising=False)
    monkeypatch.delenv("VIZIER_CORPUS_ROOT", raising=False)
    monkeypatch.setattr(storage, "REPO_CORPUS_ROOT", tmp_path / "nope" / "corpus")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    assert storage.db_path() == tmp_path / "cache" / "vizier" / "corpus.db"


def test_db_path_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.setenv("VIZIER_DB_PATH", str(tmp_path / "elsewhere.db"))
    assert storage.db_path() == (tmp_path / "elsewhere.db").resolve()


def test_a_stale_cached_index_is_rebuilt_after_an_upgrade(monkeypatch, tmp_path):
    """The index is a cache that outlives the package that filled it.

    `~/.cache/vizier/corpus.db` survives every upgrade, so when a release
    changes the shipped corpus — 0.3.0 renamed the `weaver` source to
    `principles` — the old rows keep answering queries. Only an empty index
    used to trigger a rebuild, which meant an upgraded install served phantom
    items forever.
    """
    import importlib
    import sqlite3

    from vizier import __version__
    from vizier.db import build as B
    from vizier.db import query as Q

    # `vizier.db.connect` is both a module and a re-exported function; reach
    # for the module explicitly or monkeypatch resolves the function.
    connect_mod = importlib.import_module("vizier.db.connect")

    db = tmp_path / "cache.db"
    monkeypatch.setenv("VIZIER_DB_PATH", str(db))
    monkeypatch.setenv("VIZIER_AUTO_PRIVATE", "0")
    monkeypatch.setattr(Q, "DB_PATH", db)
    monkeypatch.setattr(connect_mod, "DB_PATH", db)

    monkeypatch.setattr(Q, "_auto_build_attempted", False)
    Q.ensure_index()

    conn = sqlite3.connect(db)
    assert B.build_version(conn) == __version__
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        (B.BUILD_VERSION_KEY, "0.0.1-old"),
    )
    conn.execute(
        "INSERT INTO items (key, source, item_id, type, title, body, body_hash, fetched_at)"
        " VALUES ('gone/ghost', 'gone', 'ghost', 'principle', 'Ghost', 'x', 'x', '2026-01-01T00:00:00Z')"
    )
    conn.commit()
    assert conn.execute("SELECT count(*) FROM items WHERE source='gone'").fetchone()[0] == 1
    conn.close()

    monkeypatch.setattr(Q, "_auto_build_attempted", False)
    Q.ensure_index()

    conn = sqlite3.connect(db)
    try:
        assert conn.execute("SELECT count(*) FROM items WHERE source='gone'").fetchone()[0] == 0
        assert B.build_version(conn) == __version__
    finally:
        conn.close()
