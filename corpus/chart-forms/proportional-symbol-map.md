---
id: proportional-symbol-map
source: chart-forms
type: chart_pattern
title: Proportional-symbol map
tags: [spatial, map, count, magnitude]
details:
  purpose_families: [Spatial, Magnitude]
  capsule: >
    A map with circles (or other shapes) sized by a count or
    magnitude, placed at each location. Preserves geography (unlike
    a cartogram) while encoding count (which choropleths can't
    honestly do). The honest map for raw-count stories.
  when_to_use:
    - Count or magnitude data with meaningful locations
    - Geography should stay recognizable
    - Absolute values matter, not just distributions
    - Areas have wildly different sizes and you want to decouple area from count
  when_not_to_use:
    - Rate / ratio data — use a choropleth
    - Very dense point distribution — symbols overlap hopelessly
    - Tiny differences in magnitude — circles aren't legible at small sizes
    - Readers need precise values from the visual alone
  reading_checklist:
    - Are symbols area-scaled or radius-scaled? (If radius, values look ~4× too big for 2× the actual.)
    - Is there a nested-circle legend? Without it, readers can't decode mid-range sizes.
    - Overlap — are smaller symbols hidden behind larger ones? Transparency or z-ordering helps.
    - Is this a raw count (proportional-symbol's job) or a rate (should be a choropleth)?
  common_mistakes:
    - Radius-scaled circles instead of area-scaled — overstates differences
    - No legend key showing what symbol sizes mean
    - Symbols overlapping without transparency — hides what's underneath
    - Using when a choropleth of rate would answer the reader's question
    - Symbols too small across the range — biggest is visible, smallest is invisible
  alternatives:
    - id: choropleth
      when: Data is a rate / ratio, not a count
    - id: cartogram
      when: Geography can be distorted to encode magnitude directly
    - id: dot-map
      when: Individual observations — one symbol per event, not aggregated
    - id: hex-bin-map
      when: Equal-weight regional comparison, not magnitude
  canonical_examples:
    - cairo-blog/elegant-maps-reveal-grim-reality-html
    - cairo-blog/classes-in-choropleth-maps-html
    - cairo-blog/multiple-shapes-multiple-projections-html
  antipattern_examples: []
  related_principles: []
---
A proportional-symbol map places a symbol (usually a circle) at each
feature's location, with the symbol's area scaled to the value.
Earthquake maps (circle size = magnitude), city-population maps,
and COVID case-count maps are classic uses.

**Works when**: you have count or magnitude data that would be
misleading as a choropleth (because area would confound) and you
want to keep the geography recognizable. An earthquake map with
circle-size-magnitude preserves both "where" and "how big" better
than a choropleth would.

**Fails when**: densities are high and symbols overlap, or when
tiny values produce unreadable-small symbols. Transparency helps
with overlap up to a point; beyond that, switch to a hex-bin heatmap
on the same geography.

**Area scaling, not radius**: a value of 4× needs area × 4, so
radius × 2. Scaling radius directly misrepresents the data; a 2×
radius looks 4× bigger. Disclose the scaling in the legend.

**Legend design**: show nested circles at reference values
(e.g., 100 / 1,000 / 10,000) so readers can calibrate the size
encoding. "Biggest circle = X" without intermediate references
leaves the middle of the range unreadable.

**Pairing with choropleth**: a proportional-symbol map + a choropleth
of rate in the same piece can do both jobs — "here's where the
raw count is big" and "here's where the rate is high." They usually
disagree in instructive ways (dense cities dominate count; rural
areas dominate rate).
