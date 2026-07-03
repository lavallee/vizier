---
details:
  origin: weaver/PRINCIPLES.md
  stage: Sketch
fetched_at: '2026-04-18T19:23:27.592472Z'
id: principle-match-the-chart-form-to-the-licit-comparisons
source: weaver
tags:
- sketch
title: Match the chart form to the licit comparisons
type: principle
---

A chart is a **physical invitation to certain readings**. Aligned
vertical bars on a shared x-axis invite left-to-right comparison.
Lines with a shared time axis invite trend reading. Stacked areas invite
totals-first reading. If the data cannot support one of those readings,
the chart form has to make it visually harder — not rely on a caption
to forbid it.

**Concrete example.** In `new-bern-profile/elections`, we have turnout
per election × age band, with the denominator fixed to *today's* active
voters. That denominator systematically biases older elections down —
an 18–29-year-old who voted in 2016 but moved away before 2024 isn't
in today's file, so they don't appear in the 2016 turnout numerator or
the denominator. The number for 2016 is mechanically lower than the
number for 2024.

The first pass used grouped vertical bars over time with color = age
band. That form aligns each color across the time axis — an explicit
invitation to read "18–29 turnout dropped from 2016 to 2024." Even with
a caption saying *don't do that*, the visual grouping is stronger than
the words. The second pass switched to **small multiples, one panel
per election**. Each panel internally ranks the four age bands by
horizontal bar length. Within-panel comparison is trivial (the 65+ bar
is obviously longer than 18–29 in every panel). Cross-panel comparison
requires moving the eye between boxes — a deliberate act the reader has
to choose, not the default reading.

The general rule: ask which axes of comparison the data supports, then
pick a form that aligns on those axes and fragments on the others.

- **Within-group, cross-category valid; cross-group invalid** → small
  multiples, one panel per group. Do not use grouped bars with a shared
  time axis.
- **Across time valid for totals but not for composition** → stacked
  area with the shared axis; don't let readers track a single band's
  absolute value by hand.
- **Rank within a list valid, cardinal comparison invalid** → use
  ordinal encoding (position on a dot plot), not length of bar.
- **Cohort composition changes between periods** → mark the
  compositional break visibly in the chart, don't just flag it in a
  footnote.
- **Comparison not supported at all** → decline to draw the chart.
  Pick a different slice that *is* supported, or say so in copy.
  An absent chart is a valid form choice; drawing a compromised one
  gives readers a wrong reading the caption can't erase.
  `maplewood-profile` stays county-level on elections because
  township-age-stratified turnout would require a voter file we
  don't have — the absence is the discipline.

If the chart does the wrong thing by default, rewrite the chart. A
good caption supplements a form-appropriate chart; it cannot salvage
one that's visually lying.
