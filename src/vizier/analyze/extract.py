"""Pull exact color swatches out of a chart artifact.

vizier's critique input is normally a raster image -> vision caption, which can't
recover exact hexes. But when the artifact is **SVG or HTML source** (or the user
just hands over a palette), the colors are right there in the markup — and exact
colors are what the deterministic checks in `color` need.

This is deliberately honest rather than clever: it scrapes every `fill` / `stroke`
/ `stop-color` / inline-style color it can find, normalizes them, and splits them
into a *chromatic* set (the likely data palette) and an *achromatic* set (near
white/black/gray — usually axis, grid, text, surface chrome) using the same OKLCH
chroma floor the validator uses. A gray used as a real data series will land in
the achromatic bucket — so the split is a starting point the caller can override,
not an oracle.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .color import CHROMA_FLOOR, oklch

_HEX6 = re.compile(r"#[0-9a-fA-F]{6}\b")
_HEX3 = re.compile(r"#[0-9a-fA-F]{3}\b")
_RGB = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
# color-bearing attributes/properties, so we skip URLs, ids, and #anchors
_COLOR_CTX = re.compile(
    r"(?:fill|stroke|stop-color|color|background(?:-color)?)\s*[:=]\s*['\"]?\s*"
    r"(#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\))",
    re.IGNORECASE,
)
_SKIP = {"#ffffff", "#fff", "#000000", "#000"}


@dataclass
class Extracted:
    palette: list[str]              # chromatic swatches — the likely categorical data colors
    achromatic: list[str]           # near white/black/gray — likely chrome (axis/grid/text/surface)
    counts: dict[str, int] = field(default_factory=dict)   # first-seen frequency of every color
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "palette": self.palette,
            "achromatic": self.achromatic,
            "counts": self.counts,
            "note": self.note,
        }


def _norm(token: str) -> str | None:
    token = token.strip().lower()
    m = _RGB.match(token)
    if m:
        r, g, b = (min(255, int(x)) for x in m.groups())
        return f"#{r:02x}{g:02x}{b:02x}"
    if _HEX6.fullmatch(token):
        return token
    if _HEX3.fullmatch(token):
        return "#" + "".join(c * 2 for c in token[1:])
    return None


def extract_colors(text: str) -> dict[str, int]:
    """Every color found in color-bearing contexts, in first-seen order,
    mapped to how many times it appears. Skips pure black/white and `none`."""
    counts: dict[str, int] = {}
    for raw in _COLOR_CTX.findall(text):
        h = _norm(raw)
        if h is None or h in _SKIP:
            continue
        counts[h] = counts.get(h, 0) + 1
    return counts


def extract(text: str, *, surface: str | None = None) -> Extracted:
    """Split the artifact's colors into a chromatic data-palette candidate and
    the achromatic chrome. `surface`, if given, is dropped from both."""
    counts = extract_colors(text)
    surf = (surface or "").strip().lower() or None
    palette: list[str] = []
    achromatic: list[str] = []
    for h in counts:
        if surf and h == surf:
            continue
        if oklch(h)[1] >= CHROMA_FLOOR:
            palette.append(h)
        else:
            achromatic.append(h)
    note = (
        f"{len(palette)} chromatic + {len(achromatic)} achromatic (near white/black/gray) "
        "colors found in fill/stroke/stop-color/style. The chromatic set is the "
        "likely categorical data palette; a gray used as a real series would land "
        "in 'achromatic' — confirm before trusting the split."
    )
    return Extracted(palette=palette, achromatic=achromatic, counts=counts, note=note)


def looks_like_markup(text: str) -> bool:
    """Cheap sniff: is this SVG/HTML/CSS source (vs. a plain hex list)?"""
    t = text.lstrip()[:200].lower()
    return t.startswith(("<svg", "<!doctype", "<html", "<?xml")) or "<svg" in text[:2000]
