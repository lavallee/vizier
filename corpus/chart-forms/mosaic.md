---
id: mosaic
source: chart-forms
type: chart_pattern
title: Mosaic plot
tags: [categorical, area, two-variable, contingency]
details:
  purpose_families: [Part-to-whole, Distribution]
  capsule: >
    A 2D contingency table where each cell's area is proportional to
    its count. Beats a stacked bar when you want both margins' shapes
    visible; beats a heatmap when magnitudes matter more than color.
  when_to_use:
    - Two categorical variables with meaningful joint frequencies
    - Both marginal distributions and the interaction matter
    - Few categories per axis (2-5 each) — the grid becomes illegible fast
    - Shows conditional independence visually (cells proportional if independent)
  when_not_to_use:
    - One variable dominates and the other is noise — a bar chart suffices
    - Many cells (>5×5) — tiles become tiny and unreadable
    - Continuous variables — use a scatter or heatmap
    - Readers need precise values — the area encoding is for patterns, not numbers
  reading_checklist:
    - Row heights and column widths encode the marginal distributions — are those shapes what you'd expect?
    - Is there residual shading (color by deviation from independence)? Without it the form loses half its power.
    - If the data were independent, cells would form a uniform grid. How far from that does it look?
    - Are the rows/columns sorted in a sensible order, or alphabetically?
  common_mistakes:
    - No residual shading (color by departure from expected independence) — loses half the form's power
    - Uneven text sizing across tiles with different areas
    - Too many categories — mosaic collapses into unreadable strips
    - Using when you really wanted a stacked bar
    - Alphabetical category order instead of by magnitude
  alternatives:
    - id: heatmap
      when: Many categories per axis; color encoding scales better
    - id: stacked-bar
      when: Only one categorical axis (not truly 2D)
    - id: parallel-sets
      when: Three or more categorical axes
    - id: treemap
      when: Hierarchical composition, not a flat 2D table
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A mosaic plot shows a 2D contingency table as a grid of rectangles,
with each rectangle's area proportional to its cell count. Originally
from statistical exploratory data analysis (Hartigan & Kleiner,
1981), it's still the best form for "how do these two categorical
variables interact?"

**Works when**: both the marginal distributions (row and column totals)
and the joint structure matter. The row heights and column widths
encode the marginals; the individual cells encode the joint. When
variables are independent, cells appear as a uniform grid; when they
interact, cells distort visibly.

**Fails when**: category counts per axis climb past ~5. The form
needs legible tiles, and 6×6 grids produce squares too small to
read in typical viewports.

**Residual shading**: the canonical extension is to color each cell
by its deviation from the independent expectation (blue for
overrepresented, red for underrepresented). Combined with the area
encoding, the form shows both frequencies and departures in one view.
This is the difference between a mosaic plot and a "fancy stacked
bar" — residual shading is what gives it statistical meaning.
