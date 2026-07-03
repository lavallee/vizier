---
axes:
- description: 'Is it even a chart? A single number is a stat tile / hero figure,
    not a one-bar bar chart; >~7 classes that all carry meaning is a table. If a chart
    IS right, the data''s job picks the type: magnitude→bar/column (heatmap for a
    grid); trend→line; tell series apart→grouped/stacked bar or multi-line; one series
    is the point→emphasis (highlight one, gray the rest); above/below a baseline→diverging
    bar; part-to-whole→stacked bar; before→after per item→dumbbell. Emphasis is the
    most underused, most honest answer to ''make it clearer.'''
  name: Form fit
- description: 'Every color does exactly one job: categorical (identity — 8 hues,
    fixed order, never cycled past 8), ordinal (one hue, monotone lightness), sequential
    (magnitude, one hue light→dark), diverging (polarity, two hues + neutral gray
    midpoint), or status (reserved good→critical, always icon+label). Never a value-ramp
    on nominal categories; never a rainbow for magnitude.'
  name: Color job
- description: Do not eyeball this — compute it. Adjacent (stacks/bars/lines) or all-pairs
    (scatter/bubble/maps/small-multiples) Machado-2009 ΔE must clear 12 (target);
    8–12 is a floor legal ONLY with secondary encoding (direct labels, gaps, texture).
    OKLCH chroma ≥ 0.10 (below it a hue reads as gray) and lightness in the mode's
    band. vizier computes all of this — a critique should cite the number, not guess
    ('#2563a8↔#6b4ea8 ΔE 1.5 under deuteranopia'), because color-only encoding in
    a grayscale-hostile context is a first-class structural risk.
  name: Colorblind-safe (COMPUTABLE)
- description: Marks ≥ 3:1 vs the surface (sub-3:1 is legal only with a relief channel
    — visible labels or a table view). Text wears text tokens, NEVER the series color
    (a light categorical hue is illegible as text); identity comes from a colored
    swatch beside ink text. WCAG text contrast 4.5:1 normal / 3:1 large. vizier computes
    contrast (check_contrast).
  name: Contrast & legibility (COMPUTABLE)
- description: Thin marks; bars ≤24px with a 4px rounded data-end at the baseline;
    lines 2px; a 2px surface-color GAP between touching fills (every stacked segment,
    adjacent bars) and a 2px surface ring on overlapping dots — never a drawn border.
    Gridlines/axes are solid hairlines one step off the surface, never dashed. NEVER
    a dual-axis chart (two y-scales invent a correlation) — use two charts, small
    multiples, or index to a common base.
  name: Marks & chrome
- description: 'A legend is always present for ≥2 series (none for one — the title
    names it); direct-label selectively (the endpoint/extreme, never a number on every
    point). An HTML chart is interactive by default: crosshair+tooltip on line/area,
    per-mark tooltip on bar/dot/cell, hit target ≥24px (nearest-point/Voronoi for
    dense scatter). Tooltips ENHANCE, never gate — every value is also in direct labels
    or a table-view twin. One filter row above everything it scopes.'
  name: Labels, interaction & a11y
details:
  note: 'vizier owns the COMPUTABLE half of this method in code (src/vizier/analyze):
    `vizier validate`, the MCP tools validate_palette/check_contrast/analyze_artifact,
    and the ''Computed color findings'' block injected into critiques. So the color
    verdict is available with or without the skill present. When the `dataviz` skill
    IS available, its references/{choosing-a-form,color-formula,marks-and-anatomy,anti-patterns,interaction,palette}.md
    are the canonical long-form — cite them; this rubric is the portable subset.'
  origin: Distilled from the `dataviz` skill (form heuristic, color formula + runnable
    validator, marks & anatomy, interaction, anti-patterns).
fetched_at: '2026-07-02T20:30:16.204931Z'
id: dataviz-method
source: rubrics
tags:
- rubric
- dataviz
- color
- accessibility
- canonical
- computable
title: The data-viz method — form heuristic, computable color checks, mark specs
type: rubric
---

A procedure, run in order — **color comes last**; most bad charts pick colors first:

1. **Pick the form** by the data's job (or decide it's not a chart — a stat tile, hero number, or table).
2. **Assign color by the job it does** (categorical / ordinal / sequential / diverging / status), not by taste.
3. **VALIDATE the palette by computation, not by eye** — colorblind ΔE, contrast, OKLCH band/chroma. (`vizier validate "#.." --pairs all|adjacent`, or the analyze_artifact / validate_palette MCP tools.)
4. **Apply mark specs & the two spacers** (surface gap between fills, surface ring on dots).
5. **Add the hover layer** — tooltips that enhance, never gate.
6. **Accessibility pass** — legend for ≥2 series, a table-view twin, a selected (not auto-flipped) dark mode, texture as the CVD/print backup.

**The non-negotiables** (true in every design system): never a dual-axis chart; assign categorical hues in a fixed order, never cycled (a 9th series folds into 'Other', small multiples, or composite encoding); sequential = one hue light→dark, diverging = two hues + a gray midpoint (never a rainbow, never a hue at the diverging midpoint); status colors are reserved and ship with icon+label; text wears text tokens, never the series color; a legend is always present for ≥2 series.

**Anti-pattern catalog — if a chart matches an entry, it's wrong:**
- Dual-axis (two y-scales) — invents a correlation; the #1 mistake.
- Recolor-on-filter — color must follow the entity, not its current rank/row.
- Cycling/generating hues past 8 — indistinguishable under CVD.
- Eyeballing colorblind-safety — compute ΔE instead.
- A value-ramp on nominal categories — double-encodes length as hue, burns the identity channel.
- Rainbow / non-neighbor sequential ramp for magnitude.
- A hue at the diverging midpoint, or two cool hues as the two poles.
- Status color used for a non-status series (or vice-versa).
- Eight categorical hues when the story is one number → emphasis, or a stat tile.
- A one-bar bar chart or a 2-slice pie → a stat tile; a donut for comparing close values → a bar.
- Thick saturated blocks, heavy/ dashed gridlines, no breathing room.
- A border drawn around marks to separate them → use the 2px surface gap/ring instead.
- A number on every data point; a label clipped by a too-small bar.
- A truncated bar-chart baseline (bars must grow from zero).
- `tabular-nums` on a large standalone/hero number (use proportional; tabular only in columns).
- A tooltip as the ONLY way to read a value; pinpoint hover targets; per-chart filters; no table-view / color-only encoding on a continuous scale.

The measurable checks (colorblind separation, contrast, lightness/chroma) are computed by vizier's `analyze` module, so a critique that touches color should carry the number, not a hunch.
