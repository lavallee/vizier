---
id: dendrogram
source: chart-forms
type: chart_pattern
title: Dendrogram
tags: [hierarchy, tree, clustering, phylogeny]
details:
  purpose_families: [Part-to-whole, Correlation]
  capsule: >
    A tree diagram where branch height (or length) encodes distance —
    phylogenetic relatedness, cluster-merge cost, edit distance. Unlike
    sunburst and icicle, the branches carry quantitative meaning, not
    just hierarchy.
  when_to_use:
    - Hierarchical clustering output — branch height = merge distance
    - Phylogenetic or taxonomic relationships with branch lengths
    - Showing which groups pair up, and at what similarity
    - Audiences familiar with tree diagrams (bioinformatics, stats)
  when_not_to_use:
    - Pure hierarchy with no distance semantics — use sunburst, icicle, or treemap
    - More than ~100 leaves — overlapping labels; consider tanglegrams or aggregation
    - Readers care about magnitude within leaves rather than structure — use bars
    - The hierarchy is wide and shallow — a tidy tree with 3 levels and 50 siblings becomes a comb
  reading_checklist:
    - What does branch height encode? Merge distance, evolutionary time, something else? Label it.
    - Are leaves ordered semantically, or by the clustering algorithm's implicit order?
    - Linkage method shown? (Single, complete, average, Ward's — they produce different trees.)
    - Is there a cut-height line indicating the "natural" cluster count? If not, how is the reader supposed to pick one?
    - Circular (radial) or rectangular? Circular saves horizontal space but loses direct-comparison of branch heights.
  common_mistakes:
    - Unlabeled branch-height scale — "how different" is the form's whole point, so its units must be shown
    - Using default alphabetical leaf order when the clustering implies a natural order (reorder by tree structure)
    - Coloring branches arbitrarily — color should mark cluster membership at some chosen cut-height, not decorate
    - Overly tall/skinny aspect — branches become illegible; ideally ~golden-ratio or wider
    - Mixing linkage methods across panels without calling it out; the same data produces very different trees
  alternatives:
    - id: sunburst
      when: Pure hierarchy with part-to-whole — no distance semantics on branches
    - id: icicle-plot
      when: Same as sunburst but rectangular layout — better for reading precise widths
    - id: network-diagram
      when: Non-tree connectivity (graph with cycles) — dendrogram can't encode this
    - id: heatmap
      when: Clustered-rows heatmap — a dendrogram alongside a heatmap (bioinformatics classic) carries both structure and values
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A dendrogram is a tree diagram where the *height* of internal nodes
carries quantitative meaning. In hierarchical clustering, that height
is the distance at which two sub-clusters merged; in phylogenetics,
it's evolutionary time or substitution rate; in information retrieval,
it might be edit distance. The encoding makes dendrograms look like
sunburst or icicle charts but function quite differently — the
branch lengths aren't an artifact of layout, they're data.

**The diagnostic use**: hierarchical clustering outputs a dendrogram
the analyst reads to pick a cluster count. Draw a horizontal cut-line
at some height; the branches it crosses become the cluster
assignments. A well-behaved dataset shows "natural gaps" — large
jumps in merge distance — that suggest where to cut. A gap-less
dendrogram is the algorithm telling you there's no clean cluster
count in this data.

**Leaf ordering matters**: the clustering algorithm fixes a *partial*
order on leaves (you can swap the two children of any internal node
without changing the tree's meaning). The analyst's job is to pick a
particular ordering that groups similar leaves adjacent — so the
visual reads as "related things near each other" rather than as an
arbitrary zigzag. Standard approach: rotate internal nodes so the
smaller subtree is always on a consistent side.

**The linkage-method footnote**: "which linkage?" is not a cosmetic
decision — single-linkage, complete-linkage, average, and Ward's all
produce materially different trees on the same distance matrix.
Single-linkage chains (single-link clusters hang off other clusters
as long strings of leaves); complete-linkage produces tight balls;
Ward's minimizes variance. Label the method somewhere readers can see
it.

**Heatmap-with-dendrogram**: a classic bioinformatics combination —
rows of a heatmap are reordered by the dendrogram on the left, and
columns by a dendrogram on top. The dendrograms show *why* the
heatmap's block structure looks the way it does. This is probably
the dendrogram's most valuable role in practice: as scaffolding for
another chart rather than the main event.

**Radial dendrogram** variant: branches radiate from a center point
rather than hanging down from a root at the top. Saves horizontal
space for large trees (the circular layout gives more room at the
leaves than a rectangular one of the same total size). Loses direct
branch-height comparison — your eye can't accurately compare the
radii of two arcs the way it compares two vertical distances.
