---
id: heatmap
source: chart-forms
type: chart_pattern
title: Heatmap
tags: [correlation, matrix, color, two-variable]
details:
  purpose_families: [Correlation, Distribution, Magnitude]
  capsule: >
    A 2D matrix where each cell is colored by value. The workhorse
    form for showing structure across two categorical axes, for
    time-of-day-by-day-of-week patterns, and for correlation matrices.
    Color is the weakest quantitative encoding — use it for pattern,
    not precise values.
  when_to_use:
    - Two categorical axes with a value for each combination
    - Readers need to scan for patterns (bands, hotspots), not read precise numbers
    - 2D histograms / binned scatter data — heatmap replaces overplotted scatter
    - Calendar heatmaps (day × hour, day × year) where temporal structure is the story
  when_not_to_use:
    - Readers need precise values — color is a poor quantitative encoding
    - One axis is continuous and the other ordered — line chart per row may be better
    - High-cardinality axes (>30 each) — cells become unreadable
    - The value distribution is skewed — most cells wash out at the low end
  reading_checklist:
    - Row and column ordering — does it reveal structure, or is it alphabetical?
    - Palette — sequential (one hue) for magnitudes, diverging (two hues) for data with a midpoint. Match?
    - Is there a clear legend with thresholds? Color is a poor quantitative encoding without one.
    - Cells that stand out — are they genuine outliers, or an artifact of the palette's nonlinearity?
  common_mistakes:
    - Rainbow color palette — perceptually nonlinear, creates bands that aren't in the data
    - Diverging palette for non-diverging data (or vice-versa) — picks the wrong narrative
    - No color legend — readers have no way to decode
    - Unordered axes — heatmaps need row/column ordering to reveal structure; sort by similarity or by magnitude
    - Zero-baseline mismatch — "blue for high" conflicts with domain conventions for some data
  alternatives:
    - id: scatterplot
      when: Both axes are continuous and you have fewer than ~5k points
    - id: hex-bin-map
      when: You're heatmapping geographic data
    - id: small-multiples
      when: A third grouping dimension matters
    - id: parallel-sets
      when: Both axes are categorical AND you care about joint frequencies as flows
    - id: mosaic
      when: 2D categorical table where margins and joint both matter
    - id: hex-bin-map
      when: Heatmapping geographic data with adjacency-preserving cells
    - id: matrix-plot
      when: Rows and columns are the same set (adjacency structure)
  canonical_examples:
    - nightingale/how-to-choose-colors-for-your-data-visualizations
    - nightingale/five-steps-to-a-diverging-and-contrasting-color-scheme-for-data-visualization
    - nightingale/perceptual-uniformity-with-hcl-wizard
  antipattern_examples: []
  related_principles: []
---
A heatmap encodes a third dimension as color in a 2D grid, with the
two axes usually categorical or discretized continuous. Classic uses:
correlation matrices, calendar-shaped time patterns, gene expression
grids, genre × year popularity tables.

**Works when**: pattern-recognition is the task. Readers scan for
bands, clusters, hotspots; precise values are decoration, not the
story. A calendar heatmap of website traffic makes "evening surge on
Tuesdays" pop in a way a time-series with 168 points does not.

**Fails when**: readers need to compare two specific cells' exact
values. Color is a terrible quantitative encoding — humans can
distinguish ~7 steps reliably, fewer in context. For precision, put
the numbers in the cells (but then consider whether you need color
at all).

**Palette selection**: sequential (light → dark, one hue) for
magnitudes that have a natural zero or baseline; diverging (two hues
away from a neutral center) for data with a meaningful midpoint
like zero or a reference rate; qualitative (multi-hue) never — it
doesn't encode order.

**Axis ordering matters** as much as palette choice. A heatmap with
alphabetical rows and columns often shows nothing; the same data with
rows sorted by similarity (hierarchical clustering) or magnitude
reveals structure. For many-genre by many-year heatmaps, reorder to
reveal.
