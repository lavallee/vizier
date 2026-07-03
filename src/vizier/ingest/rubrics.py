"""Hand-authored rubrics.

Each rubric is a single Item with type=rubric and axes defined in the
frontmatter. Bodies hold prose from the source describing how to apply
each axis; structured axes live in the frontmatter so vizier can parse
them when evaluating.

Current rubrics:
- `cairo-five-pillars` — Alberto Cairo, *The Truthful Art* (2016), ch. 2.
  "The five qualities of great visualizations."
"""

from __future__ import annotations

from pathlib import Path

from ..schema import Item
from ..storage import corpus_root

SOURCE = "rubrics"


CAIRO_FIVE = Item(
    id="cairo-five-pillars",
    source=SOURCE,
    type="rubric",
    title="Cairo's Five Qualities of Great Visualization",
    url="https://www.thefunctionalart.com/",
    tags=["rubric", "cairo", "canonical"],
    details={
        "author": "Alberto Cairo",
        "origin": "The Truthful Art (2016), chapter 2",
    },
    axes=[
        {
            "name": "Truthful",
            "description": (
                "Based on thorough and honest research. The graphic doesn't "
                "deceive through omission, framing, chart-form, aggregation, "
                "or scale. The designer has interrogated the data for its "
                "limits before showing it, and the resulting visual doesn't "
                "invite readings the data can't bear."
            ),
        },
        {
            "name": "Functional",
            "description": (
                "Its visual encoding is appropriate for the data and for the "
                "reader's task. Position, length, and hue are used according "
                "to what they're perceptually good for. The form matches the "
                "licit comparisons; when it forces a comparison that the data "
                "doesn't support, it fails this test no matter how pretty."
            ),
        },
        {
            "name": "Beautiful",
            "description": (
                "Aesthetic craft in service of communication. Beautiful is "
                "not decoration — it's what makes a reader want to spend the "
                "time a functional but ugly chart would lose them from. "
                "Measured by: would the target audience linger?"
            ),
        },
        {
            "name": "Insightful",
            "description": (
                "Reveals something the reader wouldn't have seen otherwise — "
                "a pattern, an anomaly, a scale mismatch, a hidden structure. "
                "A chart that only restates what the reader already knows "
                "fails this, no matter how well-crafted."
            ),
        },
        {
            "name": "Enlightening",
            "description": (
                "Changes the reader's understanding of something that "
                "matters — morally, civically, or personally. Cairo's "
                "strongest test: has the graphic earned its place in the "
                "reader's attention by illuminating an important subject, "
                "or is it a trivial puzzle well-solved?"
            ),
        },
    ],
    body=(
        "Cairo proposes five qualities that a strong information graphic "
        "should satisfy, in roughly this order of priority: **Truthful → "
        "Functional → Beautiful → Insightful → Enlightening**.\n\n"
        "The qualities are independent tests, not a weighted sum. A chart "
        "that fails *Truthful* cannot be rescued by beauty; one that fails "
        "*Enlightening* is a toy, no matter how elegantly it shows what "
        "everyone already knew.\n\n"
        "Applied in critique, ask of a graphic: (1) Does it say anything "
        "the data doesn't support? (2) Is the encoding perceptually fit "
        "for the comparisons it invites? (3) Is it worth the reader's "
        "time to look at? (4) Does the reader leave knowing something "
        "they didn't? (5) Does what they learn matter?"
    ),
)


DATAVIZ_METHOD = Item(
    id="dataviz-method",
    source=SOURCE,
    type="rubric",
    title="The data-viz method — form heuristic, computable color checks, mark specs",
    tags=["rubric", "dataviz", "color", "accessibility", "canonical", "computable"],
    details={
        "origin": "Distilled from the `dataviz` skill (form heuristic, color formula + "
                  "runnable validator, marks & anatomy, interaction, anti-patterns).",
        "note": "vizier owns the COMPUTABLE half of this method in code (src/vizier/analyze): "
                "`vizier validate`, the MCP tools validate_palette/check_contrast/analyze_artifact, "
                "and the 'Computed color findings' block injected into critiques. So the color "
                "verdict is available with or without the skill present. When the `dataviz` skill "
                "IS available, its references/{choosing-a-form,color-formula,marks-and-anatomy,"
                "anti-patterns,interaction,palette}.md are the canonical long-form — cite them; "
                "this rubric is the portable subset.",
    },
    axes=[
        {"name": "Form fit",
         "description": "Is it even a chart? A single number is a stat tile / hero figure, not a "
                        "one-bar bar chart; >~7 classes that all carry meaning is a table. If a chart "
                        "IS right, the data's job picks the type: magnitude→bar/column (heatmap for a "
                        "grid); trend→line; tell series apart→grouped/stacked bar or multi-line; "
                        "one series is the point→emphasis (highlight one, gray the rest); above/below "
                        "a baseline→diverging bar; part-to-whole→stacked bar; before→after per item→"
                        "dumbbell. Emphasis is the most underused, most honest answer to 'make it clearer.'"},
        {"name": "Color job",
         "description": "Every color does exactly one job: categorical (identity — 8 hues, fixed order, "
                        "never cycled past 8), ordinal (one hue, monotone lightness), sequential "
                        "(magnitude, one hue light→dark), diverging (polarity, two hues + neutral gray "
                        "midpoint), or status (reserved good→critical, always icon+label). Never a "
                        "value-ramp on nominal categories; never a rainbow for magnitude."},
        {"name": "Colorblind-safe (COMPUTABLE)",
         "description": "Do not eyeball this — compute it. Adjacent (stacks/bars/lines) or all-pairs "
                        "(scatter/bubble/maps/small-multiples) Machado-2009 ΔE must clear 12 (target); "
                        "8–12 is a floor legal ONLY with secondary encoding (direct labels, gaps, "
                        "texture). OKLCH chroma ≥ 0.10 (below it a hue reads as gray) and lightness in "
                        "the mode's band. vizier computes all of this — a critique should cite the number, "
                        "not guess ('#2563a8↔#6b4ea8 ΔE 1.5 under deuteranopia'), because color-only "
                        "encoding in a grayscale-hostile context is a first-class structural risk."},
        {"name": "Contrast & legibility (COMPUTABLE)",
         "description": "Marks ≥ 3:1 vs the surface (sub-3:1 is legal only with a relief channel — "
                        "visible labels or a table view). Text wears text tokens, NEVER the series "
                        "color (a light categorical hue is illegible as text); identity comes from a "
                        "colored swatch beside ink text. WCAG text contrast 4.5:1 normal / 3:1 large. "
                        "vizier computes contrast (check_contrast)."},
        {"name": "Marks & chrome",
         "description": "Thin marks; bars ≤24px with a 4px rounded data-end at the baseline; lines 2px; "
                        "a 2px surface-color GAP between touching fills (every stacked segment, adjacent "
                        "bars) and a 2px surface ring on overlapping dots — never a drawn border. "
                        "Gridlines/axes are solid hairlines one step off the surface, never dashed. "
                        "NEVER a dual-axis chart (two y-scales invent a correlation) — use two charts, "
                        "small multiples, or index to a common base."},
        {"name": "Labels, interaction & a11y",
         "description": "A legend is always present for ≥2 series (none for one — the title names it); "
                        "direct-label selectively (the endpoint/extreme, never a number on every point). "
                        "An HTML chart is interactive by default: crosshair+tooltip on line/area, "
                        "per-mark tooltip on bar/dot/cell, hit target ≥24px (nearest-point/Voronoi for "
                        "dense scatter). Tooltips ENHANCE, never gate — every value is also in direct "
                        "labels or a table-view twin. One filter row above everything it scopes."},
    ],
    body=(
        "A procedure, run in order — **color comes last**; most bad charts pick colors first:\n\n"
        "1. **Pick the form** by the data's job (or decide it's not a chart — a stat tile, hero "
        "number, or table).\n"
        "2. **Assign color by the job it does** (categorical / ordinal / sequential / diverging / "
        "status), not by taste.\n"
        "3. **VALIDATE the palette by computation, not by eye** — colorblind ΔE, contrast, OKLCH "
        "band/chroma. (`vizier validate \"#..\" --pairs all|adjacent`, or the analyze_artifact / "
        "validate_palette MCP tools.)\n"
        "4. **Apply mark specs & the two spacers** (surface gap between fills, surface ring on dots).\n"
        "5. **Add the hover layer** — tooltips that enhance, never gate.\n"
        "6. **Accessibility pass** — legend for ≥2 series, a table-view twin, a selected (not "
        "auto-flipped) dark mode, texture as the CVD/print backup.\n\n"
        "**The non-negotiables** (true in every design system): never a dual-axis chart; assign "
        "categorical hues in a fixed order, never cycled (a 9th series folds into 'Other', small "
        "multiples, or composite encoding); sequential = one hue light→dark, diverging = two hues + a "
        "gray midpoint (never a rainbow, never a hue at the diverging midpoint); status colors are "
        "reserved and ship with icon+label; text wears text tokens, never the series color; a legend "
        "is always present for ≥2 series.\n\n"
        "**Anti-pattern catalog — if a chart matches an entry, it's wrong:**\n"
        "- Dual-axis (two y-scales) — invents a correlation; the #1 mistake.\n"
        "- Recolor-on-filter — color must follow the entity, not its current rank/row.\n"
        "- Cycling/generating hues past 8 — indistinguishable under CVD.\n"
        "- Eyeballing colorblind-safety — compute ΔE instead.\n"
        "- A value-ramp on nominal categories — double-encodes length as hue, burns the identity channel.\n"
        "- Rainbow / non-neighbor sequential ramp for magnitude.\n"
        "- A hue at the diverging midpoint, or two cool hues as the two poles.\n"
        "- Status color used for a non-status series (or vice-versa).\n"
        "- Eight categorical hues when the story is one number → emphasis, or a stat tile.\n"
        "- A one-bar bar chart or a 2-slice pie → a stat tile; a donut for comparing close values → a bar.\n"
        "- Thick saturated blocks, heavy/ dashed gridlines, no breathing room.\n"
        "- A border drawn around marks to separate them → use the 2px surface gap/ring instead.\n"
        "- A number on every data point; a label clipped by a too-small bar.\n"
        "- A truncated bar-chart baseline (bars must grow from zero).\n"
        "- `tabular-nums` on a large standalone/hero number (use proportional; tabular only in columns).\n"
        "- A tooltip as the ONLY way to read a value; pinpoint hover targets; per-chart filters; "
        "no table-view / color-only encoding on a continuous scale.\n\n"
        "The measurable checks (colorblind separation, contrast, lightness/chroma) are computed by "
        "vizier's `analyze` module, so a critique that touches color should carry the number, not a hunch."
    ),
)


# Hand-authored generated rubrics (do NOT delete other files in the dir — e.g.
# data-editor-lens.md is maintained separately). Writes are idempotent overwrites.
GENERATED = (CAIRO_FIVE, DATAVIZ_METHOD)


def run(*, root: Path | None = None) -> dict[str, int]:
    out_root = root or corpus_root()
    for item in GENERATED:
        item.write(out_root)
    return {"rubrics": len(GENERATED)}


if __name__ == "__main__":
    print(run())
