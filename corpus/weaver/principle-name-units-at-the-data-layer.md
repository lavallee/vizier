---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.592111Z'
id: principle-name-units-at-the-data-layer
source: weaver
tags:
- ingest
title: Name units at the data layer
type: principle
---

Agents vs. adults, raw counts vs. per-capita, nominal vs.
inflation-adjusted — resolve these at ingest, not at render. The data
file has one canonical unit per field, and the field name carries it
(`pop_count`, `pop_share`, `adults_per_agent`).

Receipts: the voting-agent scale factor (agents ↔ adults) in
`info-market-voting` works because the ratio is *in the data* and the
viz uses it everywhere. When it was implicit — "multiply by 6.4 in
tooltips, remember" — the number inevitably diverged between places.

Pairs with *be explicit about units* in Narrate. This is the upstream
discipline that makes that principle cheap to honor.
