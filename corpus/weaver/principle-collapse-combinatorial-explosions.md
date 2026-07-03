---
details:
  origin: weaver/PRINCIPLES.md
  stage: Sketch
fetched_at: '2026-04-18T19:23:27.592949Z'
id: principle-collapse-combinatorial-explosions
source: weaver
tags:
- sketch
title: Collapse combinatorial explosions
type: principle
---

When a category can be a combination of primitives (e.g., "this voter
touched both local news AND a voter guide AND social media"), showing
every combination creates dozens of tiny nodes that nobody reads.

In our first pass, the pathway column had entries like `P1+P4`,
`P2+P7+P9`, `multi_source`, etc. — 30+ nodes when we only have 9
primitive channels. The fix was to define a meaningful ordering and
bucket each agent by their **primary** pathway (highest-quality source
touched). We went from 30 nodes to 10, and the story got clearer.

The reusable technique: define an ordered list of categories, then
classify each entity by its first match in that order. Reader gets a
one-dimensional summary of a multi-dimensional touch pattern.
