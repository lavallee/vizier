---
details:
  origin: weaver/PRINCIPLES.md
  stage: Sketch
fetched_at: '2026-04-18T19:23:27.592645Z'
id: principle-prefer-scrolling-over-clicking
source: weaver
tags:
- sketch
title: Prefer scrolling over clicking
type: principle
---

A click is a much taller ask than a scroll — especially on mobile, where
tabs and dropdowns are small targets and can hide the content the reader
came for. Scrolling is passive; clicking requires the reader to know
something is behind the tab and decide it's worth seeing.

Apply this ruthlessly:

- **Don't hide comparable views behind tabs.** If a reader would
  meaningfully benefit from seeing tier-A and tier-B side by side,
  show them both. In `info-market-voting`, Finding 4 originally had
  three race-tier tabs switching the ranking chart. We replaced it with
  a single chart that shows all three tiers per community at once —
  readers see the cliff in one glance instead of remembering three
  separate states.
- **Don't rely on tooltips to deliver the takeaway.** Tooltips are
  decoration, not structure. Any claim that can't survive without a
  hover doesn't belong in the headline story.
- **Dropdowns and filters are for deep dives, not headlines.** It's
  fine to gate exploratory interactions behind clicks — e.g., picking
  one community out of ten for a focused sankey. But the summary-level
  findings should never require interaction to perceive.
- **Test on a phone.** If a meaningful comparison is broken on a
  narrow viewport, the comparison is broken full stop.

Interaction is earned. Default to scroll.
