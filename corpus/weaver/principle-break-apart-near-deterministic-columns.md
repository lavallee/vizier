---
details:
  origin: weaver/PRINCIPLES.md
  stage: Sketch
fetched_at: '2026-04-18T19:23:27.592800Z'
id: principle-break-apart-near-deterministic-columns
source: weaver
tags:
- sketch
title: Break apart near-deterministic columns
type: principle
---

If two stages of a flow are highly correlated, putting them next to each
other in a sankey compresses everything into a narrow waist and wastes pixels.

In `info-market-voting`, `mode` (did they research?) essentially determined
`outcome` (what kind of vote they cast). The combined `segment → mode →
pathway → outcome` diagram was noisy and hard to read. The fix was three
separate diagrams:

- **Main**: `segment → outcome` (the headline story)
- **Zoom A**: filtered to researchers, `segment → source → outcome`
- **Zoom B**: filtered to shortcut users, `segment → heuristic → outcome`

Each zoom answers a specific question. The main view shows the whole
population. This pattern generalizes — if one stage of your flow is
mostly determined by another, break it out instead of showing both.
