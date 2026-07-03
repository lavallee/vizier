---
id: bump-chart
source: chart-forms
type: chart_pattern
title: Bump chart
tags: [ranking, change-over-time, reshuffle]
details:
  purpose_families: [Ranking, Change over time]
  capsule: >
    Tracks how a set of items' ranks change across time steps. Ordering
    is the primary affordance — line crossings are the story. Reach for
    it whenever a reader will ask "who moved, and when?"
  when_to_use:
    - A fixed set of items with a rank at each time step
    - The story is how ranks reshuffle, not the magnitudes
    - 5–15 items (fewer looks sparse; more becomes spaghetti)
    - Discrete time steps (years, quarters, tournament rounds)
  when_not_to_use:
    - The magnitudes matter more than the ranks — use a line chart
    - Items enter/exit the ranked set frequently (bumps leave gaps)
    - Too many items (>15) — crossings become impossible to follow
    - The ranking itself is noisy — line crossings will mostly be jitter
  alternatives:
    - id: slope-chart
      when: Only two time points; bump simplifies to the slope
    - id: line-chart
      when: Absolute values matter; ranks are secondary
    - id: small-multiples
      when: Too many items (>15) — one panel per item reads better than crossings
    - id: sankey
      when: Quantities flow between ranked buckets (rare; specific case)
  canonical_examples:
    - junkcharts/hammock-plots
    - nightingale/step-charts
    - kantar/2015-job-market-tracker
  reading_checklist:
    - Y-axis is rank (#1 = top, typically), not magnitude. Confirm before reading.
    - Who are the crossings between? That's the reshuffle story.
    - Is there a subject-of-the-story item visually highlighted, or is every line equal weight?
    - Do items enter or exit the ranked set over time? Gaps in a line = departure.
  common_mistakes:
    - Labels on both ends when there are too many series — end-labels collide
    - Animating the crossings — the static form is supposed to show them all at once
    - Using rank on the y-axis without ticks for #1, #2, #3 — readers need the ordinal anchor
    - Too many series (>15) — becomes visual spaghetti; switch to small multiples
    - No accent color for the subject of the story — every series looks equally important
  related_principles: []
---
A bump chart is a line chart of ranks. Each item gets a line whose
y-position at each time step is its rank (#1 at the top, typically).
Lines cross when items swap positions. That's the whole point: the
crossings are the story.

The form's power is that it translates the magnitude difference between
ranks — which varies wildly (being #1 is a huge gap from #2; being #11
is indistinguishable from #12) — into a flat ordinal axis where every
position-swap looks the same size. A sankey of the same data would
make a small position shift (#5 to #6) visually comparable to a huge
one (#1 to #7), because ribbon thickness encodes magnitude, not rank.

**Works when**: you have a small set of items (5–15) with a meaningful
rank at each time step, and the reader wants to see who climbed, who
fell, and when they crossed each other.

**Fails when**: the magnitudes are the story (use a line chart); items
churn in and out of the set (broken bump segments are hard to read);
or there are too many items to untangle visually.

**Cosmetic**: (a) label each line on BOTH ends when there's room, or
just at one end if labels collide — beyond ~7 items, one end is safer.
(b) use a single accent color for the item you want to highlight, muted
colors for the rest. (c) don't animate unless you have a reason — the
whole point of the static chart is that crossings are legible
simultaneously. (d) consider "hammock plot" variants (from Kaiser Fung's
Junk Charts) when crossings are the primary affordance but magnitudes
still need some visual weight.
