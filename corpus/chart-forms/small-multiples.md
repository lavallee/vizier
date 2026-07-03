---
id: small-multiples
source: chart-forms
type: chart_pattern
title: Small multiples
tags: [meta-form, comparison, trellis, facets]
details:
  purpose_families: [Change over time, Distribution, Magnitude]
  capsule: >
    A grid of small versions of the same chart, one per category. Almost
    always the answer when you have "too many series on one chart."
    Tufte's recommendation and the form most underused in data journalism.
  when_to_use:
    - 4–25 categories to compare on the same chart type
    - Each category's trajectory is readable individually at small size
    - Readers should compare shapes across panels, not exact values
    - You have more series than a single chart can hold
  when_not_to_use:
    - Only 2–3 categories — one chart with colored series is cleaner
    - Panels would each need their own y-axis scale — the form's power is shared axes
    - The comparison is really about one dimension across all categories — use a single summary chart
  alternatives:
    - id: line-chart
      when: Three or fewer series — put them all on one chart
    - id: heatmap
      when: Reader needs to scan across many categories for a single value
    - id: ridgeline
      when: Distribution per category, not time-series per category
  canonical_examples:
    - junkcharts/small-multiples-with-simple-axes
    - junkcharts/small-multiples
    - cairo-blog/stacked-bar-graphs-and-small-multiples-html
    - visualising-data/little-visualisation-design-part-18
  reading_checklist:
    - Shared axes? If each panel has its own scale, cross-panel comparison is invalid.
    - Panel order — magnitude, similarity, geographic, or alphabetical (= meaningless)?
    - Reference line across panels? Readers need a visual anchor.
    - The standout panel — what makes it different from its neighbors?
  common_mistakes:
    - Per-panel y-axis scales — the form's comparison power comes from shared axes
    - Alphabetical panel order — almost always wrong; sort by magnitude or similarity
    - Too-small panels — if readers squint to read the axes, the form fails
    - No summary reference line across panels — readers need a visual anchor
    - Scrolling grid — if the panels don't fit one viewport, cross-panel comparison breaks down
  related_principles: []
---
Small multiples are Tufte's rename for what statisticians called a
trellis plot: a grid of small charts, each showing the same form for
a different category, with shared axes across panels. The reader
compares by scanning the grid, not by overlaying twenty lines on one
chart.

**Works when**: you have 4 to 25 categories (countries, brands,
segments, regions, patients) and you want the reader to see both the
overall shape per category and the variation across categories.
Shared axes are critical — if each panel has its own scale, the form
loses its comparison power and becomes a dashboard.

**Fails when**: two or three categories are actually sufficient.
Multiples force a grid layout that eats a lot of space, and if your
data would fit on a single chart as colored lines, that's almost
always the better choice.

Also fails when the story is one specific thing about one category —
small multiples makes every panel equal weight, which buries the
story. A single chart with the subject category highlighted works
better.

**Layout details that matter**: (a) sort panels by some meaningful
order — magnitude, similarity, or alphabetically at worst. Random
order makes the grid feel arbitrary. (b) add a summary reference
line across all panels (the overall average, or an annotation of a
key threshold) so readers have a visual anchor. (c) keep each panel
small enough that the grid fits in one viewport — if it scrolls,
comparison breaks down.
