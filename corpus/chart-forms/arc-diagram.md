---
id: arc-diagram
source: chart-forms
type: chart_pattern
title: Arc diagram
tags: [network, linear, arcs, relationships]
details:
  purpose_families: [Flow, Correlation]
  capsule: >
    Nodes on a line, relationships as arcs above. The rare form that
    works better for network data than force-directed layouts when
    the nodes have a meaningful sequence (book chapters, protein
    residues, timeline events).
  when_to_use:
    - Nodes have a natural linear order (sequence, time, rank)
    - Relationships form a sparse graph (dense = hairball above the line)
    - Reader should see "what connects to what" without losing the order
    - Both local (adjacent-node) and distant (across-line) relationships matter
  when_not_to_use:
    - No natural node order — force-directed layout is more honest
    - Many edges — arcs pile up and cross
    - Many nodes (>50) — axis gets too long to scan
    - Bi-directional relationships where direction matters — arcs can't easily encode direction
  reading_checklist:
    - Node order along the axis — does it carry meaning (sequence, time, rank)?
    - Arc thickness and height — do they encode distinct things, or are they redundant?
    - Short arcs between adjacent nodes vs. tall arcs between distant ones — is that distribution the story?
    - Arcs above the axis only, or above and below? (Dual often encodes two relationship types.)
  common_mistakes:
    - Alphabetical node order when a semantic sequence exists
    - Uniform arc thickness when edge weight varies
    - No visual hierarchy between close and far connections
    - Too many arcs — looks like a wedding invitation list
    - Using when a network diagram would actually read better
  alternatives:
    - id: chord-diagram
      when: Nodes have no order; circular layout suits all-pairs relationships
    - id: network-diagram
      when: Arbitrary graph without linear structure
    - id: sankey
      when: Directed flow between two stages (not within one sequence)
    - id: matrix-plot
      when: Dense graph — arcs pile into mud above the axis
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
An arc diagram lays nodes out along a line and draws each relationship
as an arc above (or below). The form earns its keep when nodes have
a meaningful linear order: characters in a book plotted in order of
first appearance with co-occurrence arcs; amino acids along a protein
sequence with folding-contact arcs; historical events along a
timeline with causal arcs.

**Works when**: node order carries meaning. A force-directed layout
throws away that order; an arc diagram preserves it, and the visual
tension between "close neighbors" (short arcs) and "long-distance
connections" (tall arcs) tells the structural story.

**Fails when**: the graph is dense (arcs pile into visual mud) or
when nodes have no natural sequence (then the form is just a
circular chord diagram unrolled).

**Weighted edges**: map weight to arc thickness. Don't also map it
to color; the encoding becomes redundant.

**Scrolling variant**: for long sequences (full genomes, long
novels), arc diagrams can scroll horizontally. Works in web contexts
where panning is available; fails in print.
