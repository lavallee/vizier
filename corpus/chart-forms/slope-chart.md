---
id: slope-chart
source: chart-forms
type: chart_pattern
title: Slope chart
tags: [change-over-time, before-after, ranking, comparison]
details:
  purpose_families: [Change over time, Ranking]
  capsule: >
    Two time points, connected by a line per item. Shows change,
    reshuffle, and rank-crossings in a single compact form. Reach for
    it whenever a bump chart would be too much or a line chart is
    oversized for just two moments.
  when_to_use:
    - Exactly two time points (or states) to compare
    - Many items (8-40) would clutter a bar chart pair
    - You want both magnitude change AND rank reshuffling visible
    - The crossings between items tell part of the story
  when_not_to_use:
    - Three or more time points — use a line chart or bump chart
    - Only one or two items — just show the numbers
    - Magnitudes are essentially identical (no visible slope) — use a bar chart delta
    - The items don't really match across the two time points (population changed)
  reading_checklist:
    - Two time points only? Three or more and this should have been a bump chart.
    - Are the movers highlighted, or does every line look equally important?
    - Crossings — who crossed whom, and when did the crossing happen?
    - Labels at both ends? Readers need to identify items without relying on color alone.
  common_mistakes:
    - Connecting lines drawn too thin to register change
    - No item labels — readers can't identify which lines they're tracking
    - Crowding items whose lines cross at the same point — consider highlighting the subjects
    - Missing reference line or annotation — readers don't know what matters
    - Using bright colors on every line — save accent for the items that moved
  alternatives:
    - id: bump-chart
      when: Three or more time points with rank reshuffle as the story
    - id: line-chart
      when: Many time points, magnitude matters more than reshuffle
    - id: bar-chart
      when: Just showing the delta between two states, not the endpoints
  canonical_examples:
    - observable/d3-cancer-survival-rates
    - visualising-data/simplified-slope-graphs
    - cairo-blog/from-scatter-plot-to-slope-chart-html
    - nightingale/beyond-the-bar-alternative-methods-for-visualizing-two-points-of-change
  antipattern_examples: []
  related_principles: []
---
A slope chart is a line chart simplified to two time points. Each
item becomes a line connecting its value at time A to its value at
time B. The form packs a lot of information into a small space:
magnitude at each endpoint, change (the slope), direction (up or
down), and relative ordering (which crosses which).

**Works when**: you have a "before and after" comparison with many
items. A bar chart pair would require readers to visually pair
same-labeled bars; the slope chart does that work for them. A line
chart would be visually sparse with only two x-values; slope chart
uses that space well.

**Fails when**: three or more time points are involved. At that
point you need a proper line chart or bump chart, because the slope
chart's visual simplification becomes a lie.

**Cosmetic**: (a) label each line at both endpoints; readers need
to identify items without relying on color alone. (b) muted colors
for most lines, accent for the subjects of the story (Tufte uses
this pattern heavily). (c) consider a reference line at the overall
mean or at zero-change. (d) ordering the endpoint labels by final
rank helps the reader scan.

**Compared to bump chart**: slope charts use magnitude on the y-axis;
bump charts use rank. If the absolute values matter, slope. If the
reshuffle matters and the magnitudes are comparable, bump.
