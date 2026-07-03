---
details:
  origin: weaver/PRINCIPLES.md
  stage: Narrate
fetched_at: '2026-04-18T19:23:27.593801Z'
id: principle-reading-guide-directly-above-each-novel-diagram
source: weaver
tags:
- narrate
title: Reading guide directly above each novel diagram
type: principle
---

A one-or-two-sentence "how to read this" before the first instance of
any non-obvious diagram. Colorize the column names to match the viz:

> **How to read these diagrams.** The main view shows agents flowing
> from who they are (<span style="color:#6366f1">Segment</span>)
> to how their vote lands (<span style="color:#22c55e">Outcome</span>).
> Thicker bands = more agents.

Don't assume readers know what a sankey is. Don't assume they'll parse
axis labels without a framing sentence.

**Explain the *why* of structural splits.** When a principle forces
you to break one chart into several (per *break apart near-deterministic
columns* or *collapse combinatorial explosions*), the reading guide
should name the reasoning. In `info-market-voting`, the main sankey
plus two zooms exist because mode nearly determined outcome — the zooms
aren't just deep-dives, they're structural fixes. A guide that says
"we split this because the two columns were nearly deterministic, so
the combined view was noisy" teaches the reader the principle while
they read the chart.
