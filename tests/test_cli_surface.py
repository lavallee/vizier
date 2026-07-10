from __future__ import annotations

from vizier.cli import main


def test_cli_keeps_legacy_malo_successor_surface():
    expected_top_level = {
        "analyze",
        "caption",
        "critique",
        "db",
        "eval",
        "ingest",
        "ink",
        "mcp",
        "patterns",
        "recommend-form",
        "snapshot",
        "stats",
        "suggest-palette",
        "suggest-ramp",
        "validate",
    }

    assert expected_top_level <= set(main.commands)
    assert {"build", "embed", "search", "similar", "stats"} <= set(
        main.commands["db"].commands
    )
    assert {"export", "list"} <= set(main.commands["patterns"].commands)
    assert {"full", "informed", "judge", "naive", "results"} <= set(
        main.commands["eval"].commands
    )


def test_cli_exceeds_malo_with_pre_render_journalism_guide():
    assert "guide" in main.commands
