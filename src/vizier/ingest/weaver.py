"""Weaver internal corpus ingest.

Two classes of item:
- Principles extracted from weaver/PRINCIPLES.md — one Item per named
  principle (each `###` heading under a workflow stage).
- Project notes from weaver/projects/*/notes.md — one Item per project
  that has a notes.md (treated as a process_note).

This is vizier's internal calibration set: if vizier's judgments disagree
with weaver's own lived lessons, something's wrong.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..schema import Item
from ..storage import corpus_root
from ._common import slugify

SOURCE = "weaver"

WEAVER_ROOT = Path(__file__).resolve().parents[4] / "weaver"
PRINCIPLES_PATH = WEAVER_ROOT / "PRINCIPLES.md"
PROJECTS_ROOT = WEAVER_ROOT / "projects"


# Workflow stages that bracket principle sections in PRINCIPLES.md
STAGES = (
    "Cross-cutting meta-principles",
    "Explore",
    "Frame",
    "Ingest",
    "Sketch",
    "Build",
    "Narrate",
    "Critique",
    "Ship",
    "Retrospect",
)


def _parse_principles(md: str) -> list[tuple[str, str, str]]:
    """Return list of (stage, principle_title, body_markdown)."""
    lines = md.splitlines()
    out: list[tuple[str, str, str]] = []
    current_stage: str | None = None
    current_title: str | None = None
    current_body: list[str] = []

    def flush():
        nonlocal current_title, current_body
        if current_stage and current_title:
            body = "\n".join(current_body).strip()
            if body:
                out.append((current_stage, current_title, body))
        current_title = None
        current_body = []

    for line in lines:
        m2 = re.match(r"^##\s+(.*?)\s*$", line)
        if m2:
            flush()
            heading = m2.group(1).strip()
            current_stage = heading if heading in STAGES else current_stage
            continue
        m3 = re.match(r"^###\s+(.*?)\s*$", line)
        if m3:
            flush()
            current_title = m3.group(1).strip()
            continue
        if current_title is not None:
            current_body.append(line)

    flush()
    return out


def _principle_to_item(stage: str, title: str, body: str) -> Item:
    return Item(
        id=slugify(f"principle-{title}"),
        source=SOURCE,
        type="principle",
        title=title,
        details={"stage": stage, "origin": "weaver/PRINCIPLES.md"},
        tags=[stage.lower().replace(" ", "-")],
        body=body,
    )


def _project_to_item(project_dir: Path) -> Item | None:
    notes = project_dir / "notes.md"
    if not notes.exists():
        return None
    body = notes.read_text(encoding="utf-8").strip()
    if not body:
        return None
    # Use first non-blank line as title, or the project directory name
    title = project_dir.name
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            title = line.lstrip("#").strip() or title
            break
        if line:
            title = line
            break
    return Item(
        id=slugify(f"project-{project_dir.name}"),
        source=SOURCE,
        type="process_note",
        title=f"{project_dir.name}: {title}" if title != project_dir.name else project_dir.name,
        details={"origin": f"weaver/projects/{project_dir.name}/notes.md"},
        tags=["weaver-project"],
        body=body,
    )


def run(*, root: Path | None = None) -> dict[str, int]:
    out_root = root or corpus_root()
    weaver_dir = out_root / SOURCE
    if weaver_dir.exists():
        for p in weaver_dir.glob("*.md"):
            p.unlink()

    counts = {"principles": 0, "projects": 0}

    if PRINCIPLES_PATH.exists():
        md = PRINCIPLES_PATH.read_text(encoding="utf-8")
        for stage, title, body in _parse_principles(md):
            _principle_to_item(stage, title, body).write(out_root)
            counts["principles"] += 1

    if PROJECTS_ROOT.exists():
        for project in sorted(PROJECTS_ROOT.iterdir()):
            if not project.is_dir():
                continue
            item = _project_to_item(project)
            if item:
                item.write(out_root)
                counts["projects"] += 1

    return counts


if __name__ == "__main__":
    print(run())
