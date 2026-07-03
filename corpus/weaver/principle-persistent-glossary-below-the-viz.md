---
details:
  origin: weaver/PRINCIPLES.md
  stage: Narrate
fetched_at: '2026-04-18T19:23:27.593944Z'
id: principle-persistent-glossary-below-the-viz
source: weaver
tags:
- narrate
title: Persistent glossary below the viz
type: principle
---

Tooltips disappear when the cursor moves. A glossary always-visible
below the chart lets readers look up a term without losing their place.

In this project, every term (segment, outcome, mode, pathway, heuristic)
has a swatch, label, and one-line description in a two-column glossary
block. About 12 terms total — all visible simultaneously.

**Two shapes, pick by context.** In single-chart or single-subject
projects (`info-market-voting`), an under-viz glossary block is
ideal — readers see the chart and its terms together. In multi-view
profiles with shared provenance (`new-bern-profile`,
`maplewood-profile`), a dedicated `data-sources.html` page combines
glossary + provenance + dataset-tier labels across views; each view
links to it. Both honor the principle (terms never disappear when
the cursor moves); the second pattern trades eyeline proximity for
reusability across pages. Don't mix them within a project.
