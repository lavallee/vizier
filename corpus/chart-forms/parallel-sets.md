---
id: parallel-sets
source: chart-forms
type: chart_pattern
title: Parallel sets / alluvial diagram
tags: [categorical, ribbon, co-occurrence, joint-frequency]
details:
  purpose_families: [Part-to-whole, Distribution]
  capsule: >
    Shows how categorical attributes co-occur — joint frequencies between
    two or more axes. Ribbons encode 'how many share these values'; the
    column order is editorial, not causal. Parallel sets is the answer
    when readers might reach for a sankey on branching data.
  when_to_use:
    - Several categorical attributes crossed (demographics × behavior × outcome)
    - The interesting thing is which combinations are common
    - Totals aren't conserved between columns (same population counted each column)
    - Axes have manageable cardinality (~2-5 values each)
  when_not_to_use:
    - There's a real conserved flow between columns — use sankey
    - Only two categorical variables — a stacked bar or mosaic is clearer
    - High-cardinality categoricals (8+ values per axis) — the ribbon soup is unreadable
    - The ordering between axes is meaningful / causal — readers will read causation the form doesn't claim
  alternatives:
    - id: sankey
      when: There IS a conserved flow between columns (not just co-occurrence)
    - id: stacked-bar
      when: Only one or two categorical axes to show
    - id: heatmap
      when: Exactly two categoricals; cell-based encoding works better
    - id: mosaic
      when: Exactly two categoricals; area encoding works better
  canonical_examples:
    - eagereyes/parallel-sets-released
    - eagereyes/a-spike-of-interest-in-parallel-sets
    - eagereyes/parallel-sets-implemented-by-third-party
    - nightingale/endless-river-an-overview-of-dataviz-for-categorical-data
    - eagereyes/two-short-papers-on-part-to-whole-charts-at-eurovis
  antipattern_examples:
    # Cases where sankey was reached for on data that was really joint-categorical
    - cairo-blog/the-guardian-puts-flow-charts-on-map-html
  reading_checklist:
    - Are the ribbons co-occurrence (same population counted at each axis), not flow? That's what "parallel sets" claims.
    - What order are the axes in, and could the ribbons be rearranged without changing what's true?
    - Which axis drives the color? That's the population you're tracing across combinations.
    - For the thickest ribbon between two values — how many observations is that share?
    - Any axis with >5 values? Consider whether density is hiding structure.
  common_mistakes:
    - Coloring by the rightmost axis instead of the leftmost — readers can't trace a population across the diagram
    - Axes in alphabetical order instead of an order that exposes the pattern
    - Too-high-cardinality axis (8+ values) — ribbon soup obscures the story
    - Rendering as a three-stage sankey with d3-sankey — visually plausible but smuggles in a left-to-right causal claim the data doesn't support
    - No reading guide above the diagram explaining that ribbons are co-occurrence, not flow
  related_principles:
    - weaver/principle-order-stage-categories-meaningfully
    - weaver/principle-reading-guide-directly-above-each-novel-diagram
---
Parallel sets (also called alluvial diagrams in some contexts) show the
**joint frequency structure** of several categorical attributes. Each
axis is one attribute; each colored band on an axis is a value; a ribbon
between two axes is the count of observations that share both values.

The form was introduced formally by Robert Kosara and Caroline Ziemkiewicz
in 2006–2010, predating the modern d3-sankey boom and solving a different
problem. Kosara's Parallel Sets posts on eagereyes are the canonical
reference.

**The key distinction from sankey**: a sankey tells a left-to-right flow
story; parallel sets tells a "which combinations exist" story. In a
sankey, the order of the columns is baked into the data. In parallel
sets, reordering the axes doesn't change what's true — only what's
emphasized. That means the visual direction (left before right) is
editorial, not claim. A designer picks the axis order to expose the
pattern they want to highlight.

**Works when**: you're crossing two to four categorical attributes
(demographic × behavior × outcome, say) and the story is which
combinations are common. High-trust right-leaning newspaper readers
are a different population from low-trust left-leaning social-media
consumers; parallel sets shows both populations, sized by share, and
the density of the ribbons between them shows which cross-combinations
matter.

**Fails when**: (a) the columns really do have a flow between them — a
sankey is the right form. (b) either axis has more than ~6 values —
the ribbon-crossing density becomes visual noise. (c) the reader has
strong prior about causation between axes — they'll read the ribbons
as implying direction.

**Cosmetic**: color by the leftmost axis's value (by convention — it
lets readers trace a population across all axes). Keep axes axis-labels
prominent so readers don't lose track of what each column means.
