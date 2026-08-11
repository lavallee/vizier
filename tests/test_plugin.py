"""The Claude Code plugin's manifest, skills, and bundled MCP server.

The plugin is a second, independent surface on the same package: it declares
its own version, it ships skills that name CLI commands, and it launches the
MCP server through a wrapper script. Each of those can drift out of sync with
the code silently — an install still "succeeds", it just does the wrong thing.
`tests/install/run.sh` proves the plugin installs; this proves it stays true.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from vizier import __version__

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MCP_CONFIG = ROOT / ".mcp.json"
LAUNCHER = ROOT / "bin" / "vizier-mcp"
SKILLS = ROOT / "skills"


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def test_plugin_version_tracks_the_package(manifest):
    assert manifest["version"] == __version__, (
        "bump .claude-plugin/plugin.json alongside src/vizier/__init__.py "
        "and pyproject.toml — see RELEASING.md"
    )


def test_plugin_declares_the_mcp_server():
    servers = json.loads(MCP_CONFIG.read_text())["mcpServers"]
    assert "vizier" in servers
    # The launcher must be addressed through the plugin root: the plugin is
    # installed into a cache directory whose path nobody can predict.
    assert servers["vizier"]["command"] == "${CLAUDE_PLUGIN_ROOT}/bin/vizier-mcp"


def test_launcher_is_executable():
    """Git preserves the mode bit; a plugin install does not re-chmod."""
    assert os.access(LAUNCHER, os.X_OK), "chmod +x bin/vizier-mcp"


def test_launcher_falls_back_before_giving_up():
    body = LAUNCHER.read_text()
    assert "command -v vizier" in body
    assert "uvx --from datavizier" in body
    assert "uv tool install datavizier" in body, "the failure path must name the fix"


def test_both_skills_are_present_and_shaped():
    """Parse the frontmatter as real YAML, not with a regex.

    A stray `: ` in an unquoted description parses as a mapping and the whole
    block is dropped — the skill then loads with no name and no description, so
    it silently never fires. A regex is happy to match right past that.
    """
    import yaml

    found = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))
    assert found == ["chart-critique", "chart-design"]

    for skill in found:
        text = (SKILLS / skill / "SKILL.md").read_text()
        block = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        assert block, f"{skill} is missing YAML frontmatter"
        try:
            meta = yaml.safe_load(block.group(1))
        except yaml.YAMLError as exc:
            raise AssertionError(f"{skill}: frontmatter is not valid YAML — {exc}") from exc
        assert isinstance(meta, dict), f"{skill}: frontmatter did not parse to a mapping"
        assert meta.get("name") == skill, f"{skill}: name must match its directory"
        description = meta.get("description")
        assert isinstance(description, str), f"{skill}: description is missing or not a string"
        # The description is the only thing the model sees when deciding whether
        # to invoke — a vague one means the skill never fires.
        assert len(description) > 80, f"{skill}: description is too thin to trigger on"


@pytest.mark.parametrize(
    "command",
    [
        "vizier recommend-form",
        "vizier patterns show",
        "vizier guide",
        "vizier analyze",
        "vizier doctor",
        "vizier suggest-palette",
        "vizier validate",
        "vizier critique",
    ],
)
def test_skills_only_reference_real_commands(command):
    """Every CLI invocation the skills teach has to actually exist."""
    from click.testing import CliRunner

    from vizier.cli import main

    corpus = " ".join((SKILLS / s / "SKILL.md").read_text() for s in ("chart-design", "chart-critique"))
    if command not in corpus:
        pytest.skip(f"{command} is not referenced by the skills")

    parts = command.split()[1:]  # drop the `vizier` prefix
    result = CliRunner().invoke(main, [*parts, "--help"])
    assert result.exit_code == 0, f"{command} is not a real command: {result.output}"


def test_skills_keep_color_in_proportion():
    """The point of vizier is form and honesty; color is the last five percent.

    This is a guard against the drift that made the docs read like a color
    library — if a skill ever spends more lines on hues than on choosing a
    form, the emphasis has slipped.
    """
    design = (SKILLS / "chart-design" / "SKILL.md").read_text().lower()
    color_terms = sum(design.count(t) for t in ("palette", "colorblind", "hue", "contrast"))
    form_terms = sum(design.count(t) for t in ("form", "reader", "checklist", "pattern"))
    assert form_terms > color_terms * 2, (
        f"chart-design leans too far into color ({color_terms} color mentions "
        f"vs {form_terms} form/reader mentions)"
    )
