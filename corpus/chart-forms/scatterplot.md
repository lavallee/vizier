---
id: scatterplot
source: chart-forms
type: chart_pattern
title: Scatterplot
tags: [correlation, two-variable, point]
details:
  purpose_families: [Correlation, Distribution]
  capsule: >
    Plots two continuous variables against each other, one point per
    observation. The canonical form for showing correlation. Extensions
    (bubble, color, connected) encode a third dimension.
  when_to_use:
    - Two continuous variables whose relationship is the story
    - Enough observations to reveal a pattern (~30+)
    - Readers should see both the trend AND the outliers
    - The relationship isn't well-summarized by a single number
  when_not_to_use:
    - One continuous variable — use a histogram or strip plot
    - Too many observations overplotting (>~5k) — use a hex-bin or 2D density
    - The variables are categorical — use a mosaic or heatmap
    - The relationship is primarily time — use a line chart or connected scatter
  alternatives:
    - id: heatmap
      when: Both variables are categorical or binned, or >5k observations
    - id: connected-scatter
      when: Observations are ordered in time and the path is meaningful
    - id: small-multiples
      when: A third grouping variable — split into panels
  canonical_examples:
    - observable/d3-splom
    - junkcharts/the-scatterplot-matrix-a-great-tool
    - eagereyes/the-explanatory-power-of-data-points
  antipattern_examples:
    - cairo-blog/trend-lines-in-scatter-plots-html
  reading_checklist:
    - Direction — does the cloud slope up, down, or neither? (That's the relationship.)
    - Tight or loose? Width of the cloud = strength of the relationship.
    - Any outliers? What are they? (Often the real story.)
    - If there's a trend line, is it asserted evidence or decoration? Squint to read the data without it.
  common_mistakes:
    - Radius-scaled bubbles instead of area-scaled — makes big values look 4× too big
    - Regression line as a default overlay — tells readers what you concluded, not what the data shows
    - Overplotting ignored (>5k points) — switch to hex-bin or 2D density
    - Missing margins / rug plots — readers can't see the marginal distributions
    - Inappropriate transparency — too little, overplotting hides density; too much, points disappear
    - Pinpoint hover targets — an 8px dot you must land on dead-center; dense scatter needs a nearest-point / Voronoi hit layer (~24px effective), and the value must be reachable without hover (a tooltip enhances, never gates — pair it with a table view)
  related_principles: []
---
The scatterplot is the default form for two-continuous-variable
correlation. Each point represents one observation; position encodes
the two variables. Readers look for (a) overall direction — does the
cloud slope up, down, or neither? (b) spread — how tight is the
relationship? (c) outliers — what doesn't fit?

**Works when**: you have enough points to see structure (below ~20,
any apparent pattern could be noise) and few enough to render without
overplotting (above ~5k, the mass becomes a blob). Between those
bounds, the scatterplot is almost always an appropriate first look at
two-variable data.

**Fails when**: the variables aren't really continuous (mosaic or
heatmap is more honest), or when overplotting obliterates the
pattern. Overplotting has a family of fixes — transparency, jitter,
hex-bin, 2D density, rug plots at the margins — but they each carry
tradeoffs. A heatmap of a 2D histogram is often the right answer for
>10k points.

**Trend-line overlays** are tempting and usually wrong at first. The
bare scatter tells readers something; adding a regression line tells
them what you already concluded. If you want to assert a relationship,
annotate it; don't bake it in as a default overlay.

**Bubble chart variant**: encode a third dimension in point size.
Works when the third dimension is categorical-ish with a natural
order (GDP, population, count of X) and when the range is small
enough that readers can distinguish big from small. Use area, not
radius, for size encoding — a radius-scaled bubble of double the
value looks four times as big, which misreads.

**Connected scatter variant**: join the points in order when the
observations have a natural ordering (usually time). The path is
part of the story — "we got here by this trajectory." Reuters and the
NYT use this form often for dual-outcome journeys (unemployment ×
inflation over time, say).
