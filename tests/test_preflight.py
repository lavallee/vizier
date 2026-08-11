"""Preflight checks for the key-bearing paths.

The contract these lock in: a missing extra or a missing key produces a
message naming the command that fixes it, and never a traceback. The
computable core stays reachable either way.
"""

from __future__ import annotations

import pytest

from vizier import preflight


def _no_keys(monkeypatch):
    monkeypatch.setattr(preflight, "_env_loaded", True)  # don't read a real .env
    for name, _ in preflight.PROVIDER_KEYS:
        monkeypatch.delenv(name, raising=False)


def test_missing_critique_extra_names_the_install_command(monkeypatch):
    monkeypatch.setattr(preflight, "has_module", lambda name: name != "somm")
    with pytest.raises(preflight.CritiqueUnavailable) as exc:
        preflight.require_critique()
    assert "datavizier[critique]" in str(exc.value)


def test_missing_provider_key_names_the_keys_it_accepts(monkeypatch):
    monkeypatch.setattr(preflight, "has_module", lambda name: True)
    _no_keys(monkeypatch)
    with pytest.raises(preflight.CritiqueUnavailable) as exc:
        preflight.require_critique()
    message = str(exc.value)
    assert "GEMINI_API_KEY" in message
    assert ".env" in message


def test_vision_backend_key_is_checked_separately(monkeypatch):
    """A text key alone isn't enough — something has to read the image."""
    monkeypatch.setattr(preflight, "has_module", lambda name: True)
    _no_keys(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    with pytest.raises(preflight.CritiqueUnavailable) as exc:
        preflight.require_critique(vision_backend="minimax_mcp")
    assert "MINIMAX_API_KEY" in str(exc.value)


def test_local_vision_backend_needs_no_key(monkeypatch):
    monkeypatch.setattr(preflight, "has_module", lambda name: True)
    _no_keys(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "x")
    preflight.require_critique(vision_backend="ollama")


def test_doctor_reports_a_healthy_core_install():
    r = preflight.doctor()
    assert r.items > 0, "the repo corpus index should be populated"
    assert r.problems == []
    assert r.ok


def test_doctor_flags_an_empty_index(monkeypatch, tmp_path):
    """The failure mode that made a fresh pip install useless."""
    from vizier.db import query as Q

    monkeypatch.setattr(Q, "stats", lambda **_: {"items": 0, "embeddings": 0})
    r = preflight.doctor()
    assert not r.ok
    assert any("vizier db build" in p for p in r.problems)
