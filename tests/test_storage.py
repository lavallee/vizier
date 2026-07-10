"""Storage helpers."""

from __future__ import annotations

from pathlib import Path

from vizier import storage


def test_corpus_root_defaults_to_repo_corpus(monkeypatch):
    monkeypatch.delenv("VIZIER_CORPUS_ROOT", raising=False)
    assert storage.corpus_root() == Path(storage.__file__).resolve().parents[2] / "corpus"


def test_corpus_root_can_be_overridden(monkeypatch, tmp_path):
    custom = tmp_path / "private-corpus"
    monkeypatch.setenv("VIZIER_CORPUS_ROOT", str(custom))
    assert storage.corpus_root() == custom.resolve()
