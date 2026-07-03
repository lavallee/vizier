---
id: pie-chart
source: chart-forms
type: chart_pattern
title: Pie chart
tags: [part-to-whole, angle, antipattern]
details:
  purpose_families: [Part-to-whole]
  capsule: >
    A circle sliced by angle to show composition. Widely taught, widely
    reached-for, and in most cases the wrong choice. Stacked bars and
    proportional bars almost always beat a pie for the same data.
  when_to_use:
    - Exactly 2–3 slices with dramatically different sizes
    - The "whole" is meaningful and the slices are mutually exclusive
    - A single-moment composition (no cross-category comparison needed)
    - Readers only need "the one that's dominant" — not precise values
  when_not_to_use:
    - More than 3–4 slices — human angle judgment degrades fast
    - Comparing compositions across multiple categories — pies don't scan
    - Slices similar in size — readers can't distinguish
    - Values matter precisely — angle is a worse encoding than length
    - Trying to read a tiny slice — angle approaches zero and becomes unreadable
  alternatives:
    - id: stacked-bar
      when: Almost always. The stacked bar does everything a pie does, better.
    - id: bar-chart
      when: You want readers to compare slices precisely (just show them as bars)
    - id: treemap
      when: Hierarchical composition or many small slices
    - id: waffle-chart
      when: The "whole" is a count you want readers to be able to count
  canonical_examples:
    - eagereyes/in-defense-of-pie-charts
    - eagereyes/a-pair-of-pie-chart-papers
    - eagereyes/pie-charts
  antipattern_examples:
    - junkcharts/ten-pie-charts-are-you-worried-yet
    - cairo-blog/fun-note-on-pie-charts-html
    - eagereyes/stacked-bars-are-the-worst
  reading_checklist:
    - How many slices? If >4, ask why this isn't a bar chart.
    - Which two slices are the closest in size? Can you tell which is bigger without reading the numbers? (Often no — the form fails here.)
    - Is there a dominant slice that's the story? If yes, pie can work; if no, use bars.
    - Is this one of several pies? Cross-pie comparison is a red flag.
  common_mistakes:
    - 5+ slices — angle judgment collapses
    - Side-by-side pies for category comparison — readers can't compare angles across charts
    - Tiny slices with unreadable labels — below ~3% just lump into "other"
    - 3D pies — cosmetic distortion on top of already-weak encoding
    - Donut used for decoration; the center hole has no analytic role
  related_principles: []
---
The pie chart deserves its own entry because it's so widely reached
for despite being a weak form. Humans are bad at judging angles
compared to lengths or positions. A pie of five slices makes it
harder to tell which is biggest than a horizontal bar chart of the
same data.

**The narrow case where pies earn their keep**: two or three slices
with one dramatically dominant. "75% of revenue from subscriptions"
works fine as a pie because the reader doesn't need to compare
precise slice sizes — the story is the dominant slice, not the
differences among the smaller ones.

**Why they fail at most things**:
- Five-slice pies force angle comparison between similarly-sized
  slices; readers consistently guess wrong.
- Pies compared side-by-side (multiple pies for categories) require
  cross-pie angle comparison that humans can't do. Stacked bars lined
  up next to each other are readable in a way pies aren't.
- Tiny slices (<5%) become unreadable; labels overlap.
- Donuts inherit all of a pie's problems and add one more: the
  center hole can be put to decorative use (which is the point) but
  invites decorative misuse.

**What to show instead**: horizontal bars, sorted by magnitude. A
stacked bar if you want to emphasize the "whole." A proportional-
stacked bar (100%-normalized) if composition-only. All three beat a
pie for every property a reader might want.

The honest pedagogy: this form persists mostly because spreadsheet
defaults created a generation of pie-chart instincts. Replacing it
takes active choice, not more education about why.
