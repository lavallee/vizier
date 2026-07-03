---
id: sunburst
source: chart-forms
type: chart_pattern
title: Sunburst
tags: [hierarchy, radial, part-to-whole]
details:
  purpose_families: [Part-to-whole]
  capsule: >
    A radial treemap — concentric rings, each a level of a hierarchy,
    segments sized by value. Better than treemap when depth matters
    more than size; worse when precise area comparison is needed.
  when_to_use:
    - Hierarchical data where depth itself is part of the story
    - Reader should see a tree's full structure in one view
    - Interactive drill-down is available (click to zoom a branch)
    - 3-5 levels of hierarchy — beyond that, inner rings become slivers
  when_not_to_use:
    - Flat or shallow hierarchy — sunburst wastes space
    - Precise magnitude comparison — angles and areas are hard to judge
    - Non-interactive export (print, static image) — deep rings become unreadable
    - Many leaves per branch — becomes a dartboard of tiny segments
  reading_checklist:
    - How deep does the hierarchy go? Each ring = one level of nesting.
    - What does angle encode? (Typically: value, summed through children.)
    - Can you drill down (click to zoom into a branch), or is this static?
    - For small slivers — is the piece inviting you to hover for labels, or are they just lost?
  common_mistakes:
    - Fewer than 2 levels — just draw a pie (or better, a bar)
    - No labels on inner rings — readers can't identify categories
    - No hover / zoom in static export — limits the form's strength
    - Color-encoding a second variable on top of area — readers can't decode both
    - Using when a treemap would suffice (treemap reads magnitude better)
  alternatives:
    - id: treemap
      when: Magnitude comparison matters; radial layout hides differences
    - id: icicle-plot
      when: Left-to-right hierarchy reading; more compact for wide trees
    - id: stacked-bar
      when: Two-level hierarchy; simple share comparison
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A sunburst is a radial version of a treemap: concentric rings, one
per level of a hierarchy, each ring's segments sized by value. The
center is the root; inner rings are higher in the tree; the outer
edge is leaves.

**Works when**: hierarchy depth is part of the story. Directory
structures, product category trees, ontology exploration — cases
where "how deep does this branch go?" is a meaningful question.
Interactive sunbursts shine: click a segment to zoom into its
subtree, and the form becomes a navigable hierarchy browser.

**Fails when**: the hierarchy is shallow (a pie chart of one level
is clearer) or when readers need precise magnitude comparison across
branches. Angle + radius is a harder encoding than the rectangular
area of a treemap, and much harder than bar length.

**Static-vs-interactive tradeoff**: sunbursts are much better
interactive. In print or static export, inner rings usually become
unreadable and the outer ring loses context. If the output is static,
prefer a treemap or icicle plot.
