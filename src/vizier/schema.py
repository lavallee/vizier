"""Corpus item schema.

A corpus item is anything that can inform visualization judgment —
an award winner, a process writeup, a critique post, a principle,
a rubric axis, or a raw artifact. One item per file, written as
markdown with YAML frontmatter.

Storage convention:
    corpus/<source>/<id>.md

where `<id>` is a source-local stable slug. The body of the file
holds free text (judges' commentary, process writeup, critique,
principle body); the frontmatter holds the structured fields below.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import frontmatter
from pydantic import BaseModel, Field, ConfigDict


ItemType = Literal[
    "award_entry",    # an entry/winner in a competition
    "process_note",   # a practitioner's "how we made this" writeup
    "critique",       # a critique of someone else's work
    "rubric",         # a structured framework (Cairo pillars, FT vocab)
    "principle",      # a named principle or meta-principle
    "artifact",       # a standalone viz with no attached critique
    "chart_pattern",  # a chart form with when-to-use, when-not, alternatives
]


class Item(BaseModel):
    """One corpus item. Frontmatter == all fields but `body`."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="source-local stable slug")
    source: str = Field(..., description="sigma, kantar, pudding, junkcharts, weaver, ft-vocab, cairo, ...")
    type: ItemType
    title: str
    url: str | None = Field(None, description="canonical source URL this item was extracted from")
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = Field(default_factory=list)

    # Award-specific
    year: int | None = None
    tier: str | None = Field(None, description="gold/silver/bronze/winner/shortlist/honorable-mention/etc.")
    category: str | None = None
    creators: list[str] = Field(default_factory=list)
    organization: str | None = None
    country: str | None = None
    artifact_url: str | None = Field(None, description="URL of the graphic/project being judged or described")
    methodology_url: str | None = None

    # Rubric-specific
    axes: list[dict[str, Any]] = Field(default_factory=list, description="for type=rubric: [{name, description, weight?}, ...]")

    # Free-form for anything source-specific we don't want to promote
    details: dict[str, Any] = Field(default_factory=dict)

    # Body is written into the markdown below the frontmatter, not the YAML
    body: str = ""

    def path(self, root: Path) -> Path:
        return root / self.source / f"{self.id}.md"

    def to_frontmatter(self) -> frontmatter.Post:
        data = self.model_dump(mode="json", exclude={"body"}, exclude_none=False)
        data = {k: v for k, v in data.items() if v not in (None, [], {}, "")}
        return frontmatter.Post(self.body or "", **data)

    @classmethod
    def from_file(cls, path: Path) -> "Item":
        post = frontmatter.load(str(path))
        data = dict(post.metadata)
        data["body"] = post.content
        return cls(**data)

    def write(self, root: Path) -> Path:
        p = self.path(root)
        p.parent.mkdir(parents=True, exist_ok=True)
        post = self.to_frontmatter()
        p.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
        return p
