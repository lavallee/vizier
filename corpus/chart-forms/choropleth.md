---
id: choropleth
source: chart-forms
type: chart_pattern
title: Choropleth map
tags: [spatial, map, rate, ratio]
details:
  purpose_families: [Spatial, Magnitude]
  capsule: >
    A map where regions are colored by a value. Perfect for rates and
    ratios that are meaningful per area. Dangerous for counts and
    magnitudes, because area itself encodes nothing — big empty
    regions dominate the visual story.
  when_to_use:
    - Rate or ratio data that's meaningful per area (unemployment rate, vote share)
    - The spatial distribution itself is the story
    - Regions have comparable sizes, OR the metric is normalized by population
    - Readers care about geographic patterns, not precise values
  when_not_to_use:
    - Counts or raw magnitudes — use proportional symbols or a cartogram
    - Regions vary wildly in size AND population (area dominates, e.g. US states + counts)
    - There are too many tiny regions to see (urban counties on a state map)
    - The metric doesn't vary smoothly across space — use dot maps or classification
  alternatives:
    - id: cartogram
      when: Population or some other metric should drive the size, not geographic area
    - id: proportional-symbol-map
      when: Raw counts / magnitudes that shouldn't be area-encoded
    - id: hex-bin-map
      when: Many tiny regions that should read as equal-weight
    - id: dot-map
      when: Individual observations have meaningful locations
  canonical_examples:
    - visualising-data/experimental-isarithmic-maps-visualise-electoral-data
    - eagereyes/a-smart-take-on-election-maps
    - cairo-blog/when-choropleth-maps-deceive-html
    - visualising-data/bivariate-choropleth-maps
    - cairo-blog/classes-in-choropleth-maps-html
  antipattern_examples:
    - junkcharts/canonical-us-political-map
    - junkcharts/gaining-precision-by-deleting-data
  reading_checklist:
    - Is the metric a rate / ratio / percentage — or a raw count? If count, ask why the choropleth isn't a cartogram.
    - What are the class breaks? Equal-interval, quantile, or manual? Disclosed?
    - Is the color palette ordered (one hue, light→dark) or diverging (two hues)? Does that match the data?
    - Big empty regions — are they dominating the visual story when they shouldn't?
  common_mistakes:
    - Coloring by count instead of rate — big empty regions dominate the visual
    - Equal-interval binning on a skewed variable — most regions end up in the lowest bin
    - Undisclosed classification breaks — always show the legend thresholds
    - Discrete palette that implies ordering where the variable doesn't have one
    - Missing data treated as zero — distinguish "no data" from "zero" visually
  related_principles: []
---
A choropleth colors each region of a map according to a value. It's
the default form for "how does this metric vary geographically?"
Election maps, unemployment maps, disease-rate maps, income-gini
maps — almost every time you see a "where does X happen?" piece, it's
a choropleth.

**Works when**: the metric is a rate or ratio (per-capita, percentage,
average), and the geographic pattern is part of the story. "Counties
with higher rates of X cluster in the rural Northeast" is a claim the
choropleth supports.

**Fails catastrophically when**: the metric is a raw count. The
canonical US political map is a choropleth of vote share, but if you
colored the same states by **number** of voters, the tiny densely-
populated coasts would disappear and vast empty Wyoming would
dominate — a misrepresentation. Alberto Cairo, Andy Kirk, and
Kaiser Fung have all written extensively on this trap; the fix is
either to switch to a cartogram (equal-area or population-weighted)
or to use proportional-symbol circles for the count.

**The area-vs-population distortion** affects the US so much that
"election map" has become a standard example of choropleth deception.
Big empty states look politically dominant; dense populous counties
disappear. Isarithmic maps (like Andy Kirk's experimental electoral
piece) and hex-bin maps (538's) are specific fixes.

**Classification matters more than color palette**. An equal-interval
binning of a right-skewed variable will leave most regions in the
lowest bin, obscuring variation. Quintiles (or manual breaks keyed to
the data's actual structure) usually work better. Always show the
legend's binning thresholds explicitly.
