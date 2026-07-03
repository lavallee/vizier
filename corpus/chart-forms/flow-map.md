---
id: flow-map
source: chart-forms
type: chart_pattern
title: Flow map
tags: [spatial, flow, geography, migration]
details:
  purpose_families: [Spatial, Flow]
  capsule: >
    A map with directed lines showing volumes moving between places.
    The right form when geography IS the substrate the flow happens
    on — migration, rivers, trade, power transmission, airline routes.
  when_to_use:
    - The flow's origins and destinations are geographic points
    - Geography itself is meaningful to the story (routes, basins, borders)
    - Volume magnitudes vary enough to encode as line thickness
    - Fewer than ~30 flows (beyond that, tangling eats the map)
  when_not_to_use:
    - The geography is incidental — a sankey without the map is cleaner
    - All flow happens within one small region (zoom in; it's not spatial)
    - Flows are many-to-many with small individual volumes (becomes hairball)
    - You need precise origin/destination totals — add a side table or switch to sankey
  alternatives:
    - id: sankey
      when: Origins and destinations are categorical, not geographic
    - id: choropleth
      when: The story is net change by region, not directed flow
    - id: arc-diagram
      when: Flows are between nodes in a network where geography doesn't help
  canonical_examples:
    - cairo-blog/the-guardian-puts-flow-charts-on-map-html
    - cairo-blog/bloomberg-visualizes-shrinking-html
    - cairo-blog/echoes-of-minard-axios-maps-flow-of-html
    - cairo-blog/migration-flows-within-europe-html
    - kantar/2019-flowmap-blue
    - kantar/2017-on-their-way-the-journey-of-foreign-fighters
  antipattern_examples: []
  reading_checklist:
    - What is the line thickness encoding? (Should be proportional to flow volume with a legend.)
    - Does the geography matter to the flow, or is the map ornamental?
    - Direction — is there a clear cue (arrows, curvature, gradient)?
    - Are there origins/destinations that the map hides because they'd overlap? Missing structure lies too.
  common_mistakes:
    - Arrowhead markers fixed-size while stroke scales — huge markers overwhelm thin flows
    - Straight lines (they read as pipes, not as directional motion)
    - Too many flows (>30) — hairball obscures the pattern
    - No width legend — readers can't decode ribbon thickness into volumes
    - Map projection wrong for the geography (Mercator for Arctic shipping distorts the story)
  related_principles: []
---
A flow map is a map with directed lines — typically curved — whose
thickness encodes a volume moving between two geographic points. The
canonical example is Charles Minard's 1869 map of Napoleon's Russian
campaign; modern versions include migration corridors, river-discharge
maps, and airline-route networks.

The form works when **geography is doing analytical work**. Migration
flows between US metros look different on a map than they do in a
sankey, because the map reveals regional clusters (Sun Belt inflow,
coastal outflow). Rivers on a map show the physical reality of the
drainage basin. Trade routes trace the straits and chokepoints that
shaped them.

The form fails when geography is ornament — when the map frame adds
nothing the sankey didn't have. A "flow map" of funding between
foundations and recipients, projected onto a map just because both
have addresses, smuggles in spatial intuition the data doesn't support.

**Line-width encoding** should be proportional to volume, with a clear
reference legend. Curvature helps (curved lines read as directional
where straight ones can read as pipes), and asymmetric curves (bulging
one way) signal direction without an explicit arrowhead. Arrowheads
work too but must be sized with the stroke so big flows don't get
dwarfed by their own markers.

**Hybrid with sankey**: some pieces (Bloomberg's "arterial sankey"
for the Mississippi) overlay ribbon-style flows on a map; works when
the route itself — the river — is the substrate.
