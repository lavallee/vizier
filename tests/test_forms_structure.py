"""Form recommendation + structural lint. Runnable: uv run python tests/test_forms_structure.py

test_recommend_* touch the SQLite corpus index (they need `vizier db build`).
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import numpy as np

from vizier.analyze import forms as F, structure as St
from vizier.db import query as Q
from vizier.db.build import EMBED_DIMS, EMBED_MODEL
from vizier.db.connect import connect

_EXTENSION_ENV_NAMES = (
    "VIZIER_PRIVATE_DB",
    "VIZIER_PRIVATE_CORPUS_DB",
    "VIZIER_PRIVATE_ROOT",
    "VIZIER_EXTENSION_DBS",
    "VIZIER_EXTRA_DB_PATHS",
    "VIZIER_AUTO_PRIVATE",
)


def _raises(fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
        return False
    except ValueError:
        return True


def test_recommend_form_routes_to_expected():
    ids = [f["id"] for f in F.recommend_form("composition of a total over time", n_series=5)["forms"]]
    assert "stacked-area" in ids or "stacked-bar" in ids, ids


def test_recommend_form_routes_budget_part_to_whole_language():
    rec = F.recommend_form("one total split into four non-hierarchical categories", n_series=4, k=4)
    ids = [f["id"] for f in rec["forms"]]
    assert ids and ids[0] == "stacked-bar", ids
    assert "dendrogram" not in ids and "sunburst" not in ids, ids


def test_recommend_form_routes_single_series_annual_trend():
    rec = F.recommend_form("one annual numeric metric over seven school budget years", n_series=1, k=4)
    ids = [f["id"] for f in rec["forms"]]
    assert ids and ids[0] == "line-chart", ids
    assert not any("stat tile" in n for n in rec["notes"]), rec["notes"]


def test_recommend_form_budget_module_includes_trend_and_mix():
    rec = F.recommend_form(
        "district profile budget module combining per-pupil cost trend over years "
        "and operating revenue source mix",
        n_series=5,
        k=5,
    )
    ids = [f["id"] for f in rec["forms"]]
    assert "line-chart" in ids[:4], ids
    assert "stacked-bar" in ids[:4], ids


def test_recommend_form_guards():
    assert any("stat tile" in n for n in F.recommend_form("one KPI", n_series=1)["notes"])
    assert any("table" in n for n in F.recommend_form("many categories", n_series=9)["notes"])


def test_recommend_form_family_route():
    ids = [f["id"] for f in F.recommend_form(family="Flow", k=4)["forms"]]
    assert ids, "family route returned nothing"


def test_recommend_form_needs_input():
    assert _raises(F.recommend_form)


def test_lint_flags_text_in_series_color():
    svg = '<svg><rect fill="#0072b2"/><text fill="#0072b2">B -39</text></svg>'
    findings = St.lint_svg(svg)["findings"]
    assert findings and findings[0]["check"] == "text-wears-series-color"


def test_lint_passes_ink_text():
    svg = '<svg><rect fill="#0072b2"/><text fill="#111827">label</text></svg>'
    assert St.lint_svg(svg)["findings"] == []


def _test_embedding() -> np.ndarray:
    vec = np.ones(EMBED_DIMS, dtype=np.float32)
    return vec / np.linalg.norm(vec)


def _insert_extension_items(db_path: Path, *, with_embedding: bool = False) -> None:
    conn = connect(db_path)
    try:
        rows = [
            {
                "key": "private-test/budget-editor",
                "source": "private-test",
                "item_id": "budget-editor",
                "type": "principle",
                "title": "Budget journalism needle",
                "body": (
                    "A budget chart should name the reader decision and the fair "
                    "comparison."
                ),
                "body_hash": "hash-principle",
                "details": {"stage": "brief"},
            },
            {
                "key": "private-rubric/editorial-budget-criteria",
                "source": "private-rubric",
                "item_id": "editorial-budget-criteria",
                "type": "rubric",
                "title": "Editorial Budget Criteria",
                "body": (
                    "Budget charts need denominators, inflation notes, and peer "
                    "comparisons."
                ),
                "body_hash": "hash-rubric",
                "details": {},
            },
            {
                "key": "chart-forms/private-budget-mix",
                "source": "chart-forms",
                "item_id": "private-budget-mix",
                "type": "chart_pattern",
                "title": "Private Budget Mix",
                "body": "Show the composition of a school budget against a stated total.",
                "body_hash": "hash-pattern",
                "details": {
                    "purpose_families": ["Part-to-whole"],
                    "capsule": "A budget-specific part-to-whole form.",
                    "alternatives": [{"id": "stacked-bar", "when": "default public form"}],
                    "canonical_examples": ["private-test/budget-editor"],
                },
            },
        ]
        conn.executemany(
            """
            INSERT INTO items (
                key, source, item_id, type, title, body, body_hash,
                tags_json, creators_json, axes_json, details_json, fetched_at
            )
            VALUES (
                :key, :source, :item_id, :type, :title, :body, :body_hash,
                '[]', '[]', '[]', :details_json, '2026-07-05T00:00:00'
            )
            """,
            [{**row, "details_json": json.dumps(row["details"])} for row in rows],
        )
        fts_rows = conn.execute(
            "SELECT rowid, key, title, body FROM items ORDER BY key"
        ).fetchall()
        conn.executemany(
            "INSERT INTO items_fts (rowid, key, title, body) VALUES (?, ?, ?, ?)",
            [(r["rowid"], r["key"], r["title"], r["body"]) for r in fts_rows],
        )
        if with_embedding:
            vec = _test_embedding()
            conn.executemany(
                "INSERT INTO embeddings (key, model, body_hash, dims, vec) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (row["key"], EMBED_MODEL, row["body_hash"], EMBED_DIMS, vec.tobytes())
                    for row in rows
                ],
            )
        conn.commit()
    finally:
        conn.close()


def _save_extension_env() -> dict[str, str | None]:
    return {name: os.environ.get(name) for name in _EXTENSION_ENV_NAMES}


def _with_extension_env(db_path: Path | None):
    saved = _save_extension_env()
    os.environ.pop("VIZIER_PRIVATE_DB", None)
    os.environ.pop("VIZIER_PRIVATE_CORPUS_DB", None)
    os.environ.pop("VIZIER_PRIVATE_ROOT", None)
    if db_path is None:
        os.environ.pop("VIZIER_EXTENSION_DBS", None)
    else:
        os.environ["VIZIER_EXTENSION_DBS"] = str(db_path)
    os.environ.pop("VIZIER_EXTRA_DB_PATHS", None)
    os.environ["VIZIER_AUTO_PRIVATE"] = "0"
    return saved


def _restore_env(saved: dict[str, str | None]) -> None:
    for name, value in saved.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


def test_search_and_lookup_read_extension_db():
    saved: dict[str, str | None] | None = None
    try:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "extension.db"
            _insert_extension_items(db_path)
            saved = _with_extension_env(db_path)

            hits = Q.search("budget journalism needle", k=5)
            assert any(h.key == "private-test/budget-editor" for h in hits), [h.key for h in hits]

            comma_hits = Q.search("budget journalism needle, fair comparison; reader/decision", k=5)
            assert any(h.key == "private-test/budget-editor" for h in comma_hits), [h.key for h in comma_hits]

            hit = Q.lookup("private-test", "budget-editor")
            assert hit is not None
            assert hit.why == "lookup:extension-db"

            principles = Q.list_principles()
            assert any(h.key == "private-test/budget-editor" for h in principles)
            assert any(h.key == "private-test/budget-editor" for h in Q.list_principles(stage="brief"))

            rubrics = Q.list_rubrics()
            assert any(h.key == "private-rubric/editorial-budget-criteria" for h in rubrics)

            patterns = Q.list_patterns(purpose_family="Part-to-whole")
            assert any(p["id"] == "private-budget-mix" for p in patterns), patterns

            pattern = Q.get_pattern("private-budget-mix")
            assert pattern is not None
            assert pattern["why"] == "lookup:extension-db"
            assert pattern["alternatives"][0]["id"] == "stacked-bar"
            assert pattern["canonical_examples"][0]["key"] == "private-test/budget-editor"

            local_stats = Q.stats(include_extensions=False)
            all_stats = Q.stats()
            assert all_stats["items"] == local_stats["items"] + 3
            assert any(s["source"] == "private-test" for s in all_stats["sources"])
    finally:
        if saved is not None:
            _restore_env(saved)


def test_extension_db_paths_auto_discovers_sibling_vizier_private():
    saved = _save_extension_env()
    old_db_path = Q.DB_PATH
    old_cwd = Path.cwd()
    try:
        for name in _EXTENSION_ENV_NAMES:
            os.environ.pop(name, None)
        os.environ["VIZIER_AUTO_PRIVATE"] = "1"
        with tempfile.TemporaryDirectory() as td:
            projects = Path(td)
            repo_corpus = projects / "vizier" / "corpus"
            repo_corpus.mkdir(parents=True)
            private_corpus = projects / "vizier-private" / "corpus"
            private_corpus.mkdir(parents=True)
            private_db = private_corpus / "vizier-private.db"
            private_db.write_bytes(b"not-a-real-db")

            Q.DB_PATH = repo_corpus / ".vizier.db"
            os.chdir(repo_corpus.parent)
            assert Q.extension_db_paths() == [private_db.resolve()]
    finally:
        os.chdir(old_cwd)
        Q.DB_PATH = old_db_path
        _restore_env(saved)


def test_extension_db_paths_can_disable_auto_private():
    saved = _save_extension_env()
    old_db_path = Q.DB_PATH
    old_cwd = Path.cwd()
    try:
        for name in _EXTENSION_ENV_NAMES:
            os.environ.pop(name, None)
        os.environ["VIZIER_AUTO_PRIVATE"] = "0"
        with tempfile.TemporaryDirectory() as td:
            projects = Path(td)
            repo_corpus = projects / "vizier" / "corpus"
            repo_corpus.mkdir(parents=True)
            private_corpus = projects / "vizier-private" / "corpus"
            private_corpus.mkdir(parents=True)
            (private_corpus / "vizier-private.db").write_bytes(b"not-a-real-db")

            Q.DB_PATH = repo_corpus / ".vizier.db"
            os.chdir(repo_corpus.parent)
            assert Q.extension_db_paths() == []
    finally:
        os.chdir(old_cwd)
        Q.DB_PATH = old_db_path
        _restore_env(saved)


def test_find_similar_reads_extension_db():
    saved_env: dict[str, str | None] | None = None
    saved_embed_query = Q._embed_query
    try:
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "extension.db"
            _insert_extension_items(db_path, with_embedding=True)
            saved_env = _with_extension_env(db_path)
            Q._embed_query = lambda _text: _test_embedding()

            hits = Q.find_similar("budget revenue mix journalism", k=5, min_sim=0.25)
            keys = [h.key for h in hits]
            assert "private-test/budget-editor" in keys, keys
            assert any(h.why.endswith(":extension-db") for h in hits), [h.why for h in hits]
    finally:
        Q._embed_query = saved_embed_query
        if saved_env is not None:
            _restore_env(saved_env)


def test_stats_reports_unreadable_extension_db_without_breaking_search():
    saved: dict[str, str | None] | None = None
    try:
        with tempfile.TemporaryDirectory() as td:
            missing_path = Path(td) / "missing.db"
            saved = _with_extension_env(missing_path)

            stats = Q.stats()
            assert stats["extension_dbs"]
            assert stats["extension_dbs"][0]["path"] == str(missing_path.resolve())
            assert "error" in stats["extension_dbs"][0]

            hits = Q.search("line chart", k=1)
            assert hits
    finally:
        if saved is not None:
            _restore_env(saved)


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    import traceback
    passed = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(TESTS)} passed")
    raise SystemExit(0 if passed == len(TESTS) else 1)
