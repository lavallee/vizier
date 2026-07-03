---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ship
fetched_at: '2026-04-18T19:23:27.595543Z'
id: principle-pre-ship-checklist
source: weaver
tags:
- ship
title: Pre-ship checklist
type: principle
---

Before declaring a project shippable:

- [ ] Summary findings visible without any click (tabs/dropdowns only for deep dives)
- [ ] Headline takeaway in plain language at the top
- [ ] Reading guide above each novel diagram type
- [ ] Units explicitly named; scale factor shown if synthetic
- [ ] Percentages on leftmost/rightmost sankey stages
- [ ] Category order in sankey columns is narrative, not algorithmic
- [ ] No near-deterministic column pairs in a single diagram
- [ ] Sankeys support click-to-isolate with a visible affordance
- [ ] No combinatorial explosions (max ~10 categories per column)
- [ ] Glossary under every non-trivial viz
- [ ] Citations inline in copy, full list in expandable
- [ ] Methodology accessible but collapsed by default
- [ ] On-bar text uses luminance-based contrast (not eyeballed); all labels ≥ 4.5:1 contrast against their background
- [ ] Text on colored fills uses inline `style` not class/attr (CSS silently overrides `attr('fill')`)
- [ ] Viz legible in grayscale; information encoded with more than color alone
- [ ] AP style (or your project's house style) applied consistently
- [ ] Any diagnostic paired with intervention guidance
- [ ] Calibrated against external priors where they exist
- [ ] Tested in a browser at the viewport it'll be read in
- [ ] Ingest is a runnable script with provenance; `data.json` reproduces from it

---
