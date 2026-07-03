---
id: chord-diagram
source: chart-forms
type: chart_pattern
title: Chord diagram
tags: [flow, network, circular, relationship]
details:
  purpose_families: [Flow, Correlation]
  capsule: >
    A circular diagram showing relationships (flows, connections)
    between groups arranged around a ring. The sankey's cousin for
    the many-to-many case where the "columns" are the same set —
    like trade between N countries, or emails among N teams.
  when_to_use:
    - Many-to-many flows within a single set of nodes (migration between N regions, calls between departments)
    - Both directions of each flow matter (A→B and B→A distinguish)
    - 8-20 nodes (fewer looks sparse; more tangles badly)
    - Visual impact / feature-story framing
  when_not_to_use:
    - One-way flow between two distinct stages — use sankey
    - Few nodes (<6) — a matrix or sankey reads better
    - Many nodes (>25) — chord diagrams tangle beyond recognition
    - Precise value reading matters — chord widths are approximate
  reading_checklist:
    - What do the outer arcs encode? (Typically: each node's total outflow or degree.)
    - What do the inner ribbons encode? (Typically: the relationship magnitude between two nodes.)
    - Is there a direction cue (asymmetric arcs, color-by-source)? Otherwise the chords could be undirected.
    - Node order around the ring — clustered by similarity, or arbitrary?
  common_mistakes:
    - No direction encoding — readers can't tell source from target
    - Random node ordering around the ring — sort by magnitude or by cluster
    - Inside-arc flows rendered uniformly when they have different weights
    - Missing hover or interaction affordance — static chord diagrams are hard to decode
    - Using for data that isn't actually many-to-many — sankey is clearer for directed flow
  alternatives:
    - id: sankey
      when: Distinct left-set and right-set (staged flow)
    - id: network-diagram
      when: Arbitrary graph structure; force layout handles it
    - id: matrix-plot
      when: Precise value reading matters and small enough to fit
    - id: arc-diagram
      when: Nodes arranged linearly; arcs above encode relationships
  canonical_examples:
    - nightingale/endless-river-an-overview-of-dataviz-for-categorical-data
    - observable/tomlarkworthy-spectral-layout
    - eagereyes/graphs-hairball
  antipattern_examples:
    - junkcharts/some-chart-types-are-not-scalable
  related_principles: []
---
A chord diagram arranges nodes around a circle, with arcs (chords)
connecting them. Arc width encodes flow or relationship magnitude.
Common uses: migration between countries, email traffic between
teams, co-occurrence of tags in articles, revenue flowing among
divisions.

**Works when**: you have a single set of nodes with many-to-many
flows or relationships among them. The ring layout avoids the
"hairball" problem of unconstrained network diagrams while still
showing all pairwise connections.

**Fails when**: the flow is genuinely two-stage (source set and
target set are different populations) — a sankey is clearer. Also
fails when node count climbs past ~20, because the chord density
becomes visual noise.

**Variants**:
- **Directional chord** (e.g., bilateral migration): each pair of
  nodes has two sub-arcs, one for each direction, stacked.
- **Undirected chord**: one arc per pair; loses direction but
  simplifies the visual.
- **Ribbon chord**: arcs are thick ribbons that fan in/out at their
  endpoints — more sankey-like, emphasizes magnitude.

**Cosmetic choices that matter**: (a) node order around the ring —
by cluster (so related nodes are adjacent) or by magnitude. Random
order makes chords cross unnecessarily. (b) color ribbons by source
node; the reader traces outflows from each node. (c) don't label
every ribbon; label nodes clearly and let tooltips do the rest on
interactive charts.
