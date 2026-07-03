---
id: dot-plot
source: chart-forms
type: chart_pattern
title: Dot plot
tags: [magnitude, ranking, categorical, sparse]
details:
  purpose_families: [Magnitude, Ranking, Distribution]
  capsule: >
    A dot per category at its value — the tidy alternative to bar
    charts when you have many categories, when values don't start at
    zero, or when the "thick bar" visual is heavier than the data
    warrants. Cleveland's recommendation for exactly these cases.
  when_to_use:
    - Many categories (>~15) where bars would be visually heavy
    - Values don't naturally start at zero (temperatures, rates, z-scores)
    - The story is order and approximate magnitude, not precise comparison
    - You need to show a range or comparison (paired dots, dumbbell variant)
  when_not_to_use:
    - Few categories (<10) with zero-based magnitudes — bar chart reads better
    - Precise magnitude comparison is the story — bars encode length more accurately
    - You have continuous time — use a line chart
    - Dots would be dense enough to overplot — use a strip plot or beeswarm
  reading_checklist:
    - Is the value axis zero-based? Dot plots often aren't (and that's fine) — just notice.
    - Sorted by value, or by some semantic order? Alphabetical is almost always a waste.
    - Faint grid lines per row — readers need context to anchor each dot.
    - If dumbbells, what does the connecting line mean? (Range? Delta? Two time points?)
  common_mistakes:
    - Tiny unconnected dots that readers can't parse as categories
    - No guide lines / grid — dots float without context on the value axis
    - Confusing dot plots with scatterplots when only one axis is quantitative
    - Alphabetical category order — sort by value
    - Mixing multiple series without a clear legend or paired visual connection
  alternatives:
    - id: bar-chart
      when: 10 or fewer categories and values start at zero
    - id: strip-plot
      when: Many dots per category — dots become a distribution
    - id: slope-chart
      when: Paired values per category (e.g., before/after) with line connecting them
  canonical_examples:
    - nightingale/beyond-the-bar-alternative-methods-for-visualizing-two-points-of-change
    - junkcharts/dot-plots-with-varying-dot-sizes
    - eagereyes/eagereyestv-episode-2-unit-charts-dot-plots-and-isotype-and-what-makes-them-spec
  antipattern_examples: []
  related_principles: []
---
The dot plot is the form William Cleveland argued should replace most
bar charts. Each category gets a dot positioned at its value. Visual
weight is much lower than a bar chart, so the form scales to many
categories gracefully.

**Works when**: you have many categories, when the values don't
start at zero (temperatures, effect sizes, percentages around a
mean), or when the visual heaviness of a bar chart would overpower
the data. A dot plot of 30 countries' GDP per capita reads clearly
where 30 bars would feel like a wall.

**Fails when**: readers need precise magnitude comparisons between
two specific categories. Length-on-a-shared-axis (bar chart) is more
accurate than position-on-a-shared-axis for that specific task.
Bars win.

**Dumbbell variant**: two dots per category connected by a line,
encoding two values (paired before/after, two groups, a range).
Excellent for "show the gap" stories. Annotate the connecting line
with the delta when meaningful.

**Cleveland ordering**: always sort by magnitude in dot plots;
alphabetical ordering wastes the main visual affordance. If the
categories have a meaningful sequence (budget fiscal years), use
that order instead.
