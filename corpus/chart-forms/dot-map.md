---
id: dot-map
source: chart-forms
type: chart_pattern
title: Dot map
tags: [spatial, map, point, individual]
details:
  purpose_families: [Spatial, Distribution]
  capsule: >
    A dot per observation placed at its real location. The oldest
    form of spatial data viz (John Snow's 1854 cholera map) and still
    the most honest way to show "where did these things happen?"
    without regional aggregation.
  when_to_use:
    - Individual observations with meaningful locations (incidents, events, trees)
    - Reader should see clusters and gaps, not regional summaries
    - Sample size large enough for pattern but not so large that points saturate
    - Geographic detail matters — not just which region
  when_not_to_use:
    - Rates or ratios — choropleth reads them better
    - Very dense point cloud — switch to hex-bin or 2D density
    - Privacy concerns about individual locations (public health, violence)
    - Points so sparse the map looks empty
  reading_checklist:
    - One dot = one observation, or one dot = N observations? (Check the key.)
    - Are dots overplotted — is density eating the pattern? (Transparency or hex-bins help.)
    - Any suspicious clusters that might be data-collection artifacts rather than real patterns?
    - Basemap context — can you anchor what you're seeing to a familiar place?
  common_mistakes:
    - Uniform dot size for wildly different magnitudes — use proportional symbols instead
    - No basemap context — readers can't anchor the points
    - One dot per record when records are aggregated (becomes proportional-symbol)
    - Privacy-leaking precision — round to neighborhood level for sensitive data
    - Oversaturated areas that hide density — transparency or hex-binning helps
  alternatives:
    - id: choropleth
      when: Rate / ratio per region, not individual locations
    - id: hex-bin-map
      when: Many points overlapping — aggregate to equal-area cells
    - id: proportional-symbol-map
      when: One symbol per place encoding a magnitude
    - id: heatmap
      when: 2D density; abandon the map frame entirely
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A dot map places one dot per observation at its actual location.
John Snow's 1854 map of cholera deaths around the Broad Street pump
is the canonical example; any individual-incident map (crime, 311
reports, earthquake epicenters, tree inventories) follows the same
pattern.

**Works when**: you have individual observations with real locations
and the reader should see clusters and gaps. Unlike a choropleth
(which aggregates by region) or a heatmap (which aggregates by cell),
the dot map preserves each event's position.

**Fails when**: density is so high that dots saturate the map. The
fix is transparency (alpha < 1), hex-binning, or switching to a 2D
density / kernel heatmap — which is a different form with different
tradeoffs.

**Aggregation tradeoff**: the dot map's honesty about individual
points comes at a cost when there's too many. At some density,
aggregation (hex-bin, choropleth) becomes more readable. Pick
based on what the reader should do: look for clusters → dot map
at low density; compare regional rates → choropleth; see overall
concentration → hex-bin.
