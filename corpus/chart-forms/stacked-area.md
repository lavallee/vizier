---
id: stacked-area
source: chart-forms
type: chart_pattern
title: Stacked area chart
tags: [area, part-to-whole, change-over-time]
details:
  purpose_families: [Part-to-whole, Change over time]
  capsule: >
    Shows how composition shifts continuously over time. Each colored
    band is a category; the total is the top envelope. Reach for it
    when you need both "how is this made up?" and "how has it changed?"
    in one view.
  when_to_use:
    - Composition of a total over continuous time
    - Two to six component series (more becomes unreadable)
    - The total envelope itself is part of the story
    - Category membership is stable (categories don't appear/disappear)
  when_not_to_use:
    - You need to compare middle layers precisely — they lose their baseline
    - Categories churn over the time range (gaps are confusing)
    - Discrete time points — use a stacked bar
    - 100% normalized + composition stable — use a proportional stacked bar instead
  alternatives:
    - id: stacked-bar
      when: Time points are discrete or few
    - id: line-chart
      when: Interested in individual series movements, not the composition
    - id: small-multiples
      when: More than 6 series, or readers need to compare individual trajectories
    - id: sankey
      when: Actually tracking conserved flow between discrete states
  canonical_examples:
    - cairo-blog/googles-music-timeline-some-thoughts-html
    - visualising-data/last-fm-listening-clocks
    - cairo-blog/the-problem-with-unlabeled-scales-html
  reading_checklist:
    - Is the baseline at zero (analytical) or centered/offset (editorial)?
    - Is the top envelope — the running total — meaningful or just incidental?
    - Which band is the story about? Middle bands lose their baseline; check whether the piece invites precise reading of them.
    - Does the total grow, shrink, or stay flat? The envelope shape is half the story.
  common_mistakes:
    - Putting the layer the story is about in the middle of the stack — it loses its baseline and becomes unreadable
    - Too many series (>6) — interior layers can't be visually distinguished
    - Streamgraph variant used for analytical reading — the centered baseline wrecks "how much is zero"
    - No surface gap between bands — a 2px gap in the surface color (never a drawn border) separates touching fills; without it, low-contrast neighbors blur into one band
    - Category order changes between adjacent time periods — creates visual jumps that aren't in the data
    - No total line or reference — readers can't tell if the whole envelope is growing or shrinking
  related_principles: []
---
A stacked area chart stacks multiple area charts on top of each other.
The x-axis is continuous (usually time), each y-band is a category, and
the top of the topmost band gives the total. It's the continuous-time
cousin of the stacked bar.

**Works when**: you want the reader to see both composition and total
at once, over a continuous range. Energy mix by year, market share by
quarter, sector contributions to GDP over decades — classic stacked-
area cases.

**Fails when**: the middle layers are the subject of the story. Unlike
the bottom layer (which sits on the baseline) and the top layer (which
traces the total), interior layers float — their shape depends on
what's underneath them. Readers can't visually distinguish "layer 3
grew" from "layer 2 shrank under layer 3". If a specific middle layer
matters, pull it out as a separate line chart.

Also fails when the categories churn — a category that appears in 2020
and disappears in 2023 creates a gap that looks like data loss.

**Streamgraph variant**: centered baseline (instead of zero-baseline)
makes the overall envelope symmetric and often more visually striking,
at the cost of losing "how much is zero" as a reference. Appropriate
for feature-story framing; not for analytical reading.
