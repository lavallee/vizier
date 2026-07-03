---
id: color-cvd-stacked-area
source_kind: synthetic
artifact_title: "NJ school race/ethnicity — 7-category stacked area (original palette)"
ground_truth_source: inline
palette: "#b4530a,#6b4ea8,#2f7d6b,#2563a8,#b5497f,#8a8a8f,#9a8478"
chart_surface: "#fafaf7"
tags: [stacked-area, categorical-color, accessibility, colorblind]
ground_truth: >
  The decisive critique is a COLOR / ACCESSIBILITY failure a reader can't
  eyeball but which is provable by computation: (1) the categorical palette is
  not colorblind-safe — Asian (#2563a8, blue) and Black (#6b4ea8, violet)
  collapse to ΔE ~1.5 under deuteranopia, far below the ≥12 target, so red-green
  colorblind readers (~8% of men) cannot tell those two series apart where color
  is the only channel; (2) three hues sit below the OKLCH chroma floor — Hispanic
  teal #2f7d6b, Native #8a8a8f (near-pure gray), and Two-or-more #9a8478 (taupe) —
  so they read as grays rather than identities, and Native vs Two-or-more are two
  near-identical grays. The fix is a re-derived CVD-safe palette (e.g. an
  Okabe-Ito–derived set) validated to ΔE ≥ 12, plus a redundant channel (direct
  band labels) so identity never rests on color alone. A strong critique names the
  specific failing pairs and the ΔE, not a vague "consider colorblind users."
---

## Description

A 7-category stacked-area chart showing the racial/ethnic composition of a New
Jersey school district over ~25 years — White, Black, Hispanic, Asian, Pacific
Islander, Native American, and Two-or-more races — as each group's share of
enrollment, on a warm off-white surface (#fafaf7). The bands are colored with the
palette listed in the frontmatter; a legend maps color → group; share-% labels sit
at the right edge. The composition shifts substantially over the period (White and
Black decline, Hispanic and Asian grow).

The chart's craft is otherwise solid — clean stacked area, direct end labels, a
legend, sensible baseline — so the decisive question is whether its **color
encoding** actually lets every reader tell the seven groups apart.
