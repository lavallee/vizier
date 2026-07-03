---
id: matrix-plot
source: chart-forms
type: chart_pattern
title: Matrix plot (adjacency matrix)
tags: [network, matrix, correlation]
details:
  purpose_families: [Correlation, Flow]
  capsule: >
    An adjacency matrix — rows and columns are the same set of nodes,
    cells colored or sized by their relationship. The right form when
    a network diagram would tangle. Reads like a heatmap with extra
    semantics.
  when_to_use:
    - Graph with many nodes (50+) where force-directed layouts hairball
    - Reader should compare specific pair relationships precisely
    - Both direction and magnitude of relationships matter
    - The matrix is mostly dense — networks are sparse, matrices are full
  when_not_to_use:
    - Graph is sparse and small — a network or chord diagram is more expressive
    - Readers unfamiliar with matrix reading (general audience)
    - Row/column order is arbitrary — matrix needs ordering to reveal structure
  reading_checklist:
    - Rows and columns in the same set? (Check — otherwise it's just a heatmap.)
    - Ordering — is there a clustering pattern visible, or is it alphabetical chaos?
    - Diagonal — blanked (self-loops excluded), or encoded (e.g., self-connection weight)?
    - Off-diagonal blocks — do dense patches form, suggesting community structure?
  common_mistakes:
    - Alphabetical row/column order — obscures structural clusters
    - No reordering algorithm (spectral, community detection, Cuthill-McKee)
    - Color palette that hides the zero-relationship cells
    - Missing diagonal annotation — self-loops need a convention
    - Using when a chord or arc diagram would read more intuitively
  alternatives:
    - id: network-diagram
      when: Sparse graph; clusters visible in force layout
    - id: heatmap
      when: Rows and columns are different variables, not the same set
    - id: chord-diagram
      when: Small set of nodes; all-pairs visualization around a ring
    - id: arc-diagram
      when: Nodes have a natural linear order
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A matrix plot displays the N×N adjacency matrix of a graph as a grid,
with cells colored (or sized) by the relationship between row and
column nodes. It's the form that scales where force-directed layouts
collapse into a hairball: 500 nodes work fine as a matrix, impossible
as a network.

**Works when**: graph is dense or large, and the reader should see
both individual pair relationships and global structure (blocks,
clusters, diagonal density). Social-network matrices, communication
patterns, trade flows between many countries — all read better as
matrices when the count climbs.

**Fails when**: the reader isn't matrix-literate. The form has a
steep learning curve; general-audience pieces benefit from a chord
or network diagram even at slight cost to scalability.

**Ordering is everything**: a randomly-ordered matrix shows nothing.
Reorder rows and columns so that structure emerges — communities
cluster along the diagonal, bridges appear in off-diagonal blocks.
Common algorithms: spectral ordering, hierarchical clustering,
Cuthill-McKee for bandwidth minimization, community detection
(Louvain) followed by within-community sort.
