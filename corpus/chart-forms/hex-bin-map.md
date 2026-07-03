---
id: hex-bin-map
source: chart-forms
type: chart_pattern
title: Hex-bin map (equal-area)
tags: [spatial, map, hexagon, aggregation]
details:
  purpose_families: [Spatial, Magnitude]
  capsule: >
    A map where regions are replaced with uniformly-sized hexagons,
    each colored by value. Fixes the choropleth's area-dominance bug
    by treating every region as equal visual weight. Popular for
    US-state-level political maps (FiveThirtyEight, NPR).
  when_to_use:
    - Comparing regions where geographic area is a confounder (US states)
    - Reader should read regions as equal-weight
    - Approximate adjacency matters but exact shape doesn't
    - A single-metric value per region to encode as color
  when_not_to_use:
    - Precise geographic pattern matters — hexagons distort shape
    - Readers will be confused by non-geographic region shapes — general audiences often are
    - Many regions — hex grid becomes busy quickly
    - Sub-region detail matters (county-level within states, say)
  reading_checklist:
    - Can you identify your state / region? Hex layouts need approximate adjacency to stay readable.
    - What does cell color encode? (The whole reason you swapped out a choropleth.)
    - Does every region get one hex (equal visual weight), or is the grid weighted by some other variable?
    - Is there a companion geographic map, or is this the only view? Unfamiliar audiences may need both.
  common_mistakes:
    - Hex layout that doesn't preserve approximate adjacency — readers lose geographic anchor
    - No state-name labels — unfamiliar audiences can't decode
    - Diverging palette applied to non-diverging data (or vice-versa)
    - Missing the real map as a companion — reader loses orientation
    - Using when a normal choropleth would have been fine (rate data, low area-variance)
  alternatives:
    - id: choropleth
      when: The metric is a rate, not a count; geographic area isn't confounding
    - id: cartogram
      when: You want to distort but preserve some area information
    - id: proportional-symbol-map
      when: You want to keep the real map with magnitude circles overlaid
    - id: dot-map
      when: Individual observations have meaningful locations
  canonical_examples:
    - visualising-data/experimental-isarithmic-maps-visualise-electoral-data
    - junkcharts/brexit-bremain-the-world-did-not-end-so-dataviz-people-can-throw-shade-and-color
  antipattern_examples: []
  related_principles: []
---
A hex-bin map (or equal-area cartogram with hexagonal cells)
replaces each region on a map with a uniformly-sized hexagon,
placed to roughly preserve geographic adjacency. Every region gets
the same visual weight regardless of its actual area.

**Works when**: the story is about regions-as-equal-voters-or-units
and the choropleth's area-dominance would mislead. FiveThirtyEight's
state-level political maps are the canonical case: Wyoming gets one
hex, California gets one hex, and readers compare political leanings
without Wyoming's size distorting the view.

**Fails when**: geographic detail matters or when readers can't
navigate non-geographic layouts. For a county-level hex map, most
readers won't know which hex is their county; labels don't all fit
at hex size.

**Variants**:
- **Square-tile map**: same idea with squares; simpler layout, less
  organic feel.
- **Hex honeycomb at national scale**: every US state represented by
  one hex; approximate US geographic layout preserved.
- **Hex binning for point data**: hexagon grid overlaid on a real
  map, each hex colored by count of points that fall in it. Different
  use case — a 2D histogram on a geographic substrate.

**Pairing with real map**: hex maps often work best as a companion
view to a geographic map, not a replacement. Readers get orientation
from the real map and equal-weight comparison from the hex view.
