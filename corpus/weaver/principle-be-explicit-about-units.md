---
details:
  origin: weaver/PRINCIPLES.md
  stage: Narrate
fetched_at: '2026-04-18T19:23:27.594350Z'
id: principle-be-explicit-about-units
source: weaver
tags:
- narrate
title: Be explicit about units
type: principle
---

If your viz shows synthetic data, say so — and scale back to real units
wherever possible.

In this project, each synthetic "agent" stands for 5–20 real voting-age
adults depending on community size. Every number is shown both ways in
tooltips and stats:

> 152 agents ≈ 972 adults

A scale note above the main sankey makes the mapping explicit:
*"3,000 synthetic agents represent roughly 19,300 voting-age adults
in Cupertino. Each agent stands in for about 6.4 real adults — so a
band of 50 agents represents around 321 people."*

Never mix terms. "Voter" means a real person who votes. "Agent" means
our synthetic representation. Readers shouldn't have to guess which
is which. The upstream discipline (*name units at the data layer*,
in Ingest) is what makes this consistent across the viz.
