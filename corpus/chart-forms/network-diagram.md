---
id: network-diagram
source: chart-forms
type: chart_pattern
title: Network diagram (force-directed graph)
tags: [network, graph, relationships, nodes-edges]
details:
  purpose_families: [Flow, Correlation]
  capsule: >
    Nodes and edges laid out by a physical simulation (springs repel
    nodes, edges pull connected nodes together). The right form for
    arbitrary graph structure where both neighborhood and clusters
    matter. The wrong form if you reach for it by default.
  when_to_use:
    - Data is genuinely a graph (arbitrary connections between entities)
    - Structure (clusters, hubs, bridges) is the story
    - 20-200 nodes (fewer is sparse; more becomes hairball)
    - Reader can interact (zoom, hover, filter)
  when_not_to_use:
    - The data has natural ordering (time, rank, magnitude) — use a more constrained form
    - Node count > ~200 — becomes unreadable hairball
    - Static export where interaction isn't available — usually illegible
    - Actually a flow between two stages — use sankey
  reading_checklist:
    - What do the nodes represent, and what do the edges?
    - Are there clusters visible? Community detection or manual color-grouping should help them pop.
    - Are there hubs — high-degree nodes connected to many others? Those are the structural anchors.
    - Does the layout look reproducible, or is it a one-off force-sim snapshot?
  common_mistakes:
    - No clustering or community detection to anchor the layout
    - Random initial conditions — non-reproducible layouts
    - Unlabeled nodes — readers can't identify anything
    - Every edge drawn identically when edge weight is meaningful
    - Using for what is really a tree — use a dendrogram or tree layout
  alternatives:
    - id: chord-diagram
      when: All-pairs relationships within a small set (circular layout reads better)
    - id: sankey
      when: Two-stage directed flow
    - id: matrix-plot
      when: Dense graph — adjacency matrix scales to large N
    - id: arc-diagram
      when: Nodes arranged linearly with connections as arcs
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A network (or force-directed graph) renders nodes and edges with
positions computed by a physics simulation: repulsive forces push
nodes apart, edge tensions pull connected nodes together, and an
equilibrium layout emerges. The form is famous for exposing community
structure — nodes that connect heavily to each other cluster
visually.

**Works when**: the data is genuinely a graph with no natural
ordering (social networks, citation networks, ingredient graphs) and
the reader is looking for structural properties — hubs, clusters,
bridges. Interactive versions work much better than static.

**Fails when**: the data has natural ordering that a more constrained
form would honor. Time-series, ranked lists, and hierarchical data
all have better-suited forms. Also fails at >200 nodes without
aggressive filtering — the "hairball" is the classic critique.

**Layout reproducibility**: force simulations are stochastic; two
runs produce different layouts. For publication, seed the random
generator and disclose the seed, or use a deterministic layout
algorithm (spectral, circular with cluster grouping) for consistency.

**Cluster detection helps more than layout tuning**: running
community detection (Louvain, Leiden) and coloring nodes by cluster
makes the structure readable where a pure force-layout would stay
cluttered.
