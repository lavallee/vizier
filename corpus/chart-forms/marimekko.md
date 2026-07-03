---
id: marimekko
source: chart-forms
type: chart_pattern
title: Marimekko chart
tags: [part-to-whole, two-dimensional, business, market-share]
details:
  purpose_families: [Part-to-whole, Magnitude]
  capsule: >
    A 2D stacked bar where column widths encode one magnitude (e.g.
    market size by segment) and each column's stacked heights encode
    another (share by brand, within segment). Popular in business
    decks; the mosaic plot is its statistical twin.
  when_to_use:
    - Both dimensions carry meaningful magnitude that readers should see
    - Segment × brand, market × competitor, channel × product
    - 3-6 columns and 3-6 rows per column — stays legible
    - The "big cell in a big column" story is the headline
  when_not_to_use:
    - Only one dimension matters — use a stacked bar chart
    - Cells need precise comparison across non-adjacent columns (variable widths defeat alignment)
    - Dozens of segments — cells get too small to read values
    - Statistical independence claim — use a mosaic plot, which makes the expected-vs-observed difference explicit
    - Readers need to see within-segment ranking — a sorted bar-chart-per-segment reads faster
  reading_checklist:
    - Do column widths sum to 100% (of total market), or are they absolute (in dollars)? Label it.
    - Within-column stacks: are segments ordered consistently across columns, or per-column by size?
    - Is the top-level total visible somewhere? Readers should be able to verify "widths × average heights ≈ total".
    - Are large cells (big share × big segment) annotated with labels, or left to area-estimation?
    - For within-column comparison: readers see stack proportion, but ordering within stack matters.
  common_mistakes:
    - Unsorted columns (random order defeats the "big market first" read)
    - Within-column segment order inconsistent across columns — impossible to trace one brand
    - Missing column-width units — readers can't tell if widths are revenue, units, or percent
    - Treating it as a generic stacked bar with pretty widths — the widths must carry meaning
    - Using bright, saturated colors for every segment — makes the big-cell headline vanish in chroma
    - Color encoding the same as the row dimension (redundant, no extra info)
  alternatives:
    - id: mosaic
      when: The question is statistical independence — expected cell area vs observed tells the story
    - id: stacked-bar
      when: Only one dimension carries magnitude — the width dimension is nominal
    - id: treemap
      when: Hierarchy is 3+ levels deep and the share-across-siblings reads fine without a 2D grid
    - id: bar-chart
      when: One-dimensional magnitude comparison — marimekko is overkill
  canonical_examples:
    - chart-forms/mosaic
    - chart-forms/stacked-bar
  antipattern_examples: []
  related_principles: []
---
A marimekko chart (sometimes mekko chart, or variable-width stacked
bar) packs two magnitudes into a single grid. Column widths encode
"how big is this segment?"; within each column, stacked heights encode
"share within segment". The resulting cells are area-proportional to
"segment size × share within segment" — which on the right framing is
a real quantity (revenue, units sold, customers reached).

**Works when**: business strategy presentations where the question is
"where do we have share in the big markets?". A marimekko with columns
sized by market and stacks colored by competitor lets a reader see at
a glance "our brand dominates the small Pacific market but is a
minor player in the massive US market" — without two separate charts.

**Fails when**: readers need to compare a specific brand's share
between two non-adjacent columns. Because columns have different
widths, the visual heights of "20% share in a wide market" and "20%
share in a narrow market" are very different cell sizes; the 20%-vs-20%
equivalence is lost. A small-multiples bar chart with matched y-axes
beats marimekko for that question.

**The stacked-order trap**: if brand A is on the bottom of one
column and the top of another, no reader can trace brand A
consistently. Pick a stack order (alphabetical, or by global share)
and keep it across every column. This is the single most common
marimekko mistake in business decks — analysts let each column
self-sort, which makes the chart faster to read per-column and
impossible to read across-columns.

**Mosaic vs marimekko**: structurally the same chart, used for
different jobs. Mosaic plots (statistics) use it to reveal departures
from conditional independence — cells shaded by Pearson residuals,
with the "expected sizes under independence" as the reference. Marimekko
(business) uses it to show joint magnitude — cells shaded by brand,
with the "big cells" as the finding.

**Color discipline**: the headline is cell *area*, not cell color.
Desaturated stacks let the big cells own the eye; brightly-colored
every-segment stacks turn the chart into a rainbow where area and
chroma fight each other. Save bright color for the 1-2 cells the
narrative is about.
