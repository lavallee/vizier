"""FT Visual Vocabulary ingest.

Source: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary

The Visual Vocabulary is a ~9-family taxonomy that the FT Visual
Journalism Team uses to select chart forms by the comparison being
made. Each family names when to use it, then lists specific chart
types with one-line descriptions. We ingest this as:

- One rubric Item with the families as axes.
- Details carry the full family → chart-type hierarchy, each type with
  its description and any linked reading.

Modeled after the structure of the repo's README. If FT updates the
README, rerun this script.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from ..schema import Item
from ..storage import corpus_root

SOURCE = "ft-vocab"
README_URL = (
    "https://raw.githubusercontent.com/Financial-Times/chart-doctor/"
    "main/visual-vocabulary/README.md"
)

# The families in the order they appear in the README.
# The README uses inline typos ("bebroken", "arenas") — we preserve the
# literal descriptions but trim to content.
FAMILIES = (
    "Deviation",
    "Correlation",
    "Ranking",
    "Distribution",
    "Change over Time",
    "Part-to-whole",
    "Magnitude",
    "Spatial",
    "Flow",
)


_link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _strip_markdown_links(text: str) -> str:
    return _link_re.sub(r"\1", text)


def _parse_readme(md: str) -> dict:
    """Return {family: {"description": str, "types": [{"name": str, "description": str}, ...]}}"""
    # Operate line-by-line
    lines = md.splitlines()
    out: dict[str, dict] = {}
    current_family: str | None = None
    current_family_desc: list[str] = []
    current_type_name: str | None = None
    current_type_desc: list[str] = []

    def flush_type():
        nonlocal current_type_name, current_type_desc
        if current_family and current_type_name:
            desc = "\n".join(current_type_desc).strip()
            # Keep only the first paragraph for the type description
            first_para = desc.split("\n\n")[0].strip()
            out[current_family]["types"].append({
                "name": current_type_name,
                "description": _strip_markdown_links(first_para),
            })
        current_type_name = None
        current_type_desc = []

    for line in lines:
        m2 = re.match(r"^###\s+(.*?)\s*$", line)
        if m2:
            # Moving to a new family (or general/todo section)
            flush_type()
            heading = m2.group(1).strip()
            if heading in FAMILIES:
                current_family = heading
                current_family_desc = []
                out[current_family] = {"description": "", "types": []}
            else:
                # Flush previous family description if we haven't
                if current_family and current_family_desc:
                    out[current_family]["description"] = _strip_markdown_links(
                        "\n".join(current_family_desc).strip().split("\n\n")[0]
                    )
                    current_family_desc = []
                current_family = None
            continue
        m4 = re.match(r"^####\s+(.*?)\s*$", line)
        if m4:
            # New chart type — flush the family description on first sight
            if current_family and current_family_desc:
                out[current_family]["description"] = _strip_markdown_links(
                    "\n".join(current_family_desc).strip().split("\n\n")[0]
                )
                current_family_desc = []
            flush_type()
            current_type_name = m4.group(1).strip()
            continue
        if current_family:
            if current_type_name is None:
                current_family_desc.append(line)
            else:
                current_type_desc.append(line)

    flush_type()

    # Any family still without a description (description set only on #### transition)
    for fam in FAMILIES:
        if fam in out and not out[fam]["description"]:
            # This shouldn't normally happen, but be safe.
            out[fam]["description"] = ""

    return out


def _fetch_readme() -> str:
    r = httpx.get(README_URL, follow_redirects=True, timeout=30)
    r.raise_for_status()
    return r.text


def _build_item(md: str, families: dict) -> Item:
    axes = []
    for fam in FAMILIES:
        if fam not in families:
            continue
        data = families[fam]
        types = [t["name"] for t in data["types"]]
        axes.append({
            "name": fam,
            "description": data["description"],
            "chart_types": types,
        })

    body_parts = [
        "FT's Visual Vocabulary is a poster + web reference used by the FT "
        "Visual Journalism Team to pick chart forms by the comparison "
        "being made. Nine chart families, each with a family of sub-types. "
        "Selection starts by identifying the comparison (deviation? "
        "correlation? part-to-whole?) and narrows to a specific type from "
        "there.",
        "",
        "## Families",
    ]
    for fam in FAMILIES:
        if fam not in families:
            continue
        data = families[fam]
        body_parts.append(f"\n### {fam}\n\n{data['description']}\n")
        for t in data["types"]:
            body_parts.append(f"- **{t['name']}**: {t['description']}")

    body = "\n".join(body_parts)

    details = {
        "origin": "Financial-Times/chart-doctor/visual-vocabulary",
        "chart_families": {
            fam: families[fam] for fam in FAMILIES if fam in families
        },
    }

    return Item(
        id="ft-visual-vocabulary",
        source=SOURCE,
        type="rubric",
        title="FT Visual Vocabulary",
        url="https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary",
        tags=["rubric", "chart-selection", "ft", "canonical"],
        axes=axes,
        details=details,
        body=body,
    )


def run(*, root: Path | None = None) -> dict[str, int]:
    out_root = root or corpus_root()
    fam_dir = out_root / SOURCE
    if fam_dir.exists():
        for p in fam_dir.glob("*.md"):
            p.unlink()
    md = _fetch_readme()
    families = _parse_readme(md)
    item = _build_item(md, families)
    item.write(out_root)
    total_types = sum(len(families[f]["types"]) for f in FAMILIES if f in families)
    return {"rubric": 1, "families": len(families), "chart_types": total_types}


if __name__ == "__main__":
    print(run())
