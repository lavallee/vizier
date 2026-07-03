---
id: treemap
source: chart-forms
type: chart_pattern
title: Treemap
tags: [part-to-whole, hierarchy, rectangle-packing]
details:
  purpose_families: [Part-to-whole, Magnitude]
  capsule: >
    Nested rectangles sized by value. Shows hierarchy and share
    simultaneously. Good for "many categories, wide magnitude range";
    bad for precision because rectangles compress magnitude comparisons
    worse than bars do.
  when_to_use:
    - Hierarchical data with a single continuous metric (budget categories, file sizes, stock-market sectors)
    - Many categories (>15) where bars would overflow
    - Wide magnitude range — small slices still get some visual space
    - Reader wants "what's biggest in this hierarchy?" answered quickly
  when_not_to_use:
    - Flat (non-hierarchical) data — use sorted bars
    - Precise comparison between non-adjacent rectangles — area is hard to judge
    - Small number of categories — bars are always clearer
    - Negative values — treemaps can't encode them
  reading_checklist:
    - What's the hierarchy here — are the large outer tiles parent categories, leaves, or both?
    - What does the tile area encode? (Should be stated explicitly.)
    - Is color a second dimension, or redundant decoration?
    - Small tiles — are they the story, or the garnish? Treemaps de-emphasize them.
  common_mistakes:
    - No labels on small rectangles — unidentifiable tiles
    - Alphabetical tile order instead of sorted by size (for non-hierarchical variants)
    - Using rainbow color to encode a second variable while using area for the first — too much going on
    - Hiding hierarchy levels with uniform coloring — use nesting borders or hierarchy-aware color
    - Reading the tiles as interactive when they're not (and vice versa)
  alternatives:
    - id: sunburst
      when: Hierarchy depth matters more than magnitude
    - id: bar-chart
      when: Flat data with few categories
    - id: icicle-plot
      when: Left-to-right hierarchy reading is natural
    - id: stacked-bar
      when: Two-level hierarchy only
  canonical_examples:
    - observable/d3-treemap
    - eagereyes/treemaps
    - junkcharts/visualizing-hierarchies
    - observable/enjalot-treemap-of-sequences
    - visualising-data/treemap-data-art
  antipattern_examples: []
  related_principles: []
---
A treemap packs rectangles of area proportional to a value into a
fixed frame, with nesting expressing hierarchy. Shneiderman invented
the form in the early 90s for visualizing disk usage; it now appears
in budget breakdowns, stock-market sector maps, genre hierarchies,
and anywhere else with many-leaf hierarchical data.

**Works when**: your data is hierarchical and has a wide magnitude
range. A treemap of US federal budget by agency → program reveals
structure a flat bar chart would miss — Defense's massive share
dominates, but small programs stay visible.

**Fails when**: flat (non-hierarchical) data is being presented in
hierarchy form without real hierarchy. A "treemap of top 20
companies" is just a bar chart with extra steps — and a worse
encoding.

Also fails for precise comparison: readers can judge bar lengths
reliably but not rectangle areas. Two tiles of similar size look
equal even when one is 10-20% bigger.

**Layout algorithm matters**: squarified treemaps keep rectangles
close to square (best for readability); slice-and-dice treemaps
produce thin slivers (bad); strip treemaps strike a balance. Most
libraries default to squarified; check yours.

**Color**: use color for a second dimension (category membership,
growth rate, positive/negative change), not for size (already on
area). Avoid too many categorical hues — 5-7 top-level groups max.
