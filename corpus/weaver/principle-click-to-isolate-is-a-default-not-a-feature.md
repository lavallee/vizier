---
details:
  origin: weaver/PRINCIPLES.md
  stage: Build
fetched_at: '2026-04-18T19:23:27.593240Z'
id: principle-click-to-isolate-is-a-default-not-a-feature
source: weaver
tags:
- build
title: Click-to-isolate is a default, not a feature
type: principle
---

Any sankey with more than two or three bands per column should let the
reader click a node to isolate the flow through it — highlighting all
its ancestors and descendants, dimming everything else. Click again (or
click empty canvas) to reset.

Sankeys look simple until you actually try to trace a specific voter
segment through the whole diagram: the color overlap, the width
disparities, and the typical width-based visual priority make it
genuinely hard to follow one thread. Click-to-isolate fixes that with
one gesture.

Implementation notes from `info-market-voting`:

- **BFS both directions.** From the clicked node, walk backward along
  `target → source` for ancestors, and forward along `source → target`
  for descendants. Keep the union of links visited.
- **Dim, don't hide.** Non-isolated links drop to ~4% opacity,
  non-isolated nodes to ~20% opacity. The shape of the whole remains
  visible; the clicked flow pops.
- **Same-node click resets.** The reader shouldn't have to hunt for a
  reset button.
- **Background click also resets.** Click on empty SVG canvas clears.
- **Surface the affordance in the tooltip.** On hover, show "click to
  isolate this flow" (or "click again to reset" when active). Hidden
  features are unused features.

This should be baked into whatever shared sankey helper weaver ends up
with. Don't rediscover it per project.
