---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.591864Z'
id: principle-preserve-uncertainty-at-ingest-don-t-reconstruct-downstream
source: weaver
tags:
- ingest
title: Preserve uncertainty at ingest, don't reconstruct downstream
type: principle
---

If the source publishes MOEs, standard errors, or confidence intervals,
carry them through `ingest` into `data.json`. Don't drop them and try
to reconstruct later — once dropped, they're gone for the reader *and*
the next analyst.

Receipts: the Maplewood age pyramid got MOE whiskers only after
retrofitting ingest to preserve cell-level MOEs from ACS. Had the
first pass written `count` without `moe`, the *survey data needs
visible error bars* principle in Build would have been un-actionable
without redoing ingest.

Default: the data file is a superset of what the viz renders.
Stripping happens at render time, not ingest time.
