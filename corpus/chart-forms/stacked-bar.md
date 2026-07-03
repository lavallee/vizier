---
id: stacked-bar
source: chart-forms
type: chart_pattern
title: Stacked bar chart
tags: [bar, part-to-whole, categorical, magnitude]
details:
  purpose_families: [Part-to-whole, Magnitude]
  capsule: >
    Shows how a single total splits into parts, across categories. The
    honest rendering for cohort funnels, budget breakdowns, survey
    compositions — anywhere you'd be tempted by a pie chart but want
    to support comparison across multiple wholes.
  when_to_use:
    - Composition of a single total (100% = one thing, split)
    - Composition across several totals you want to compare
    - Two to six component segments (beyond that, readers can't follow)
    - Absolute magnitude matters as much as the split
  when_not_to_use:
    - Many component segments (>6 — bar becomes an unreadable mosaic)
    - Reader needs to compare a middle segment across bars (hard because it doesn't share a baseline)
    - The composition changes continuously over time — use stacked area
    - The total itself isn't meaningful — just show the magnitudes separately
  alternatives:
    - id: waffle-chart
      when: Narrative / emotional framing; the "out of 100" should be countable
    - id: stacked-area
      when: Composition varies continuously over time
    - id: small-multiples
      when: More than 6 segments, or when each segment needs its own axis
    - id: pie-chart
      when: Single-total composition AND you don't need cross-comparison (rare)
    - id: sankey
      when: There IS a conserved flow between two staged wholes
    - id: treemap
      when: Hierarchical composition with many leaves
    - id: mosaic
      when: Two categorical axes with joint-frequency structure
  canonical_examples:
    - junkcharts/small-multiples-with-simple-axes
    - cairo-blog/stacked-bar-graphs-and-small-multiples-html
    - eagereyes/two-short-papers-on-part-to-whole-charts-at-eurovis
    - cairo-blog/nprs-college-majors-visualization-html
  antipattern_examples:
    - eagereyes/stacked-bars-are-the-worst
  reading_checklist:
    - Does every bar represent a meaningful total, or just an arbitrary sum?
    - Are segments in a consistent order across bars?
    - Which segment is the subject of the story? Is it on the outside (readable) or middle (hard)?
    - For a middle segment, are the differences across bars actually readable from this form?
  common_mistakes:
    - Alphabetical segment order — almost always wrong; order by magnitude or semantic sequence
    - More than 6 segments — the middle bands become an unreadable mosaic
    - Expecting readers to compare a middle segment across bars; it doesn't share a baseline
    - Labels inside narrow segments that get clipped; put them outside when the segment is too small
    - Using 100%-stacked (composition only) when the reader also needs the total magnitude; use the absolute variant
  related_principles:
    - weaver/principle-put-percentages-next-to-labels
---
The stacked bar is the workhorse of part-to-whole visualization: a
rectangle representing a total, split horizontally or vertically into
proportionally-sized segments. Variants include the 100% stacked bar
(all bars same length, shows composition only), the magnitude stacked
bar (bar length encodes the total, segments its parts), and the
diverging stacked bar (useful for Likert-scale data).

**Works when**: you have one to a few totals to compare, each splits
cleanly into 2–6 named segments, and the reader wants both "how big
is this whole?" and "how is it made up?" at the same time.

**Fails when**: segment count climbs above 6 and readers can no longer
track individual colors. Also when the reader needs to compare a
middle segment across bars — unlike the first and last segments,
interior segments don't share a baseline, and the eye can't measure
them. The fix is to either order bars so the segment of interest ends
up on the outside, or split into small multiples.

**The funnel case**: if you have a cohort that shrinks over stages
(100 visitors → 60 sign-ups → 25 activate → 8 subscribe), a four-step
horizontal bar chart is the honest rendering. The temptation to reach
for a sankey comes from wanting to "show the flow" — but a stacked
bar doesn't invent a destination for the missing 92%. The cohort
simply shrinks.

**Cosmetic**: (a) sort segments consistently (by magnitude or by
semantic order — never leave it to alphabetical). (b) label values
inside the segments when they're wide enough; outside otherwise. (c)
use one accent color against neutrals when a single segment is the
subject of the story.
