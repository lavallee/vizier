---
details:
  origin: weaver/PRINCIPLES.md
  stage: Sketch
fetched_at: '2026-04-18T19:23:27.593098Z'
id: principle-order-stage-categories-meaningfully
source: weaver
tags:
- sketch
title: Order stage categories meaningfully
type: principle
---

d3-sankey's default node order within a column is optimized for minimum
link crossings, not for narrative. If you want segments ranked from
most-engaged to least-engaged top-to-bottom, you have to do it yourself.

Pattern used in this project:

```js
// Define explicit order per stage
const SEGMENT_ORDER = ['civic_actives', 'habitual_voters', ...]
// Sort nodes within each stage; rebuild indices; pass to d3Sankey with .nodeSort(null)
```

Ordering bakes in a reading direction. In our case: top rows = voters
most likely to participate; bottom rows = least. That creates an
immediate visual story before readers parse any numbers.

---
