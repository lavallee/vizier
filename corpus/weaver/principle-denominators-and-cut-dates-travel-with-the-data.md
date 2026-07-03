---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.591723Z'
id: principle-denominators-and-cut-dates-travel-with-the-data
source: weaver
tags:
- ingest
title: Denominators and cut dates travel with the data
type: principle
---

When numerator and denominator come from different sources or different
points in time, record both on the data file — not just in the chart
caption.

Receipts: `new-bern-profile/elections` turnout is per-election
numerators (historical vote records) divided by *today's* active-voter
denominator. That denominator choice is the most important fact about
the chart, and it was invisible in `data.json` — it showed up only
after we'd already drawn the wrong chart form (grouped bars over time,
inviting the trend-reading the denominator can't support).

Pattern: every aggregated metric in the data file carries a
`denominator` field (what population it's a share of, including the
*as-of* date) and an optional `notes` field for caveats the chart
needs to respect. The viz reads those, the reader never sees them, but
they survive into retrospect.
