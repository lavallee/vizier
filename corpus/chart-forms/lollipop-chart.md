---
id: lollipop-chart
source: chart-forms
type: chart_pattern
title: Lollipop chart
tags: [magnitude, ranking, sparse, categorical]
details:
  purpose_families: [Magnitude, Ranking]
  capsule: >
    A dot at each category's value, connected to the baseline by a
    thin stem. The "diet bar chart" — length still encodes magnitude,
    but visual weight drops enough that many categories don't bludgeon
    the reader. Splits the difference between bar chart and dot plot.
  when_to_use:
    - 15–40 categories — too many for clean bars, too few for a strip plot
    - Values are zero-based and length encodes magnitude
    - You want dot-plot legibility with bar-chart precision
    - Paired comparisons (two lollipops side by side) or delta-to-baseline framing
  when_not_to_use:
    - Few categories (≤10) where bar chart gives more confident length reads
    - Values don't start at zero — dot plot is more honest; the stem implies a baseline
    - Distribution shape is the story — use a strip plot or histogram
    - Dots would be visually identical without the stems — you're not gaining anything
  reading_checklist:
    - Is zero the baseline? The stem implies it — a non-zero baseline is the classic lollipop lie.
    - Sorted by value or by category semantics? Alphabetical lollipops waste the form.
    - Dot size constant? Varying sizes smuggles in a second encoding, usually without a legend.
    - Paired or single-series? Paired lollipops (two dots, one stem between) encode delta; single lollipops encode magnitude.
    - Stems thin enough that dots, not sticks, dominate visually?
  common_mistakes:
    - Non-zero baseline with a stem — readers unconsciously use the stem length to estimate magnitude
    - Making the stems as thick as a bar chart — now it's just a bar chart with a weird cap
    - Adding color to both dot and stem without a reason — visual noise
    - Random category order — sort by value unless there's a semantic order
    - Using it for distribution data (per-point scatter) when a strip plot is the right form
  alternatives:
    - id: bar-chart
      when: 10 or fewer categories and length precision matters
    - id: dot-plot
      when: Values don't start at zero (temperatures, z-scores, rates around a mean)
    - id: slope-chart
      when: Two values per category connected — slope reads better than paired dots
    - id: strip-plot
      when: Many observations per category — points become a distribution
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A lollipop chart is, structurally, a bar chart with the bar replaced
by a thin line and a dot on top. The encoding is identical — length
from zero encodes magnitude — but the visual weight is much lower,
which lets the form scale to categories where a bar chart would feel
like a wall.

**Works when**: you have enough categories that a bar chart feels
heavy (roughly 15-40), values are zero-based, and the story is
magnitude + ordering. Also good for paired comparisons: two dots
connected by a single stem encodes "here's where X was, here's where
X became" in a way that two bars can't quite match.

**Fails when**: few categories. With 6 bars, the bar chart's
length-on-a-shared-axis is the strongest perceptual encoding
available — replacing that with a thin stem and a dot loses real
precision for no reason. At that count, just use a bar chart.

**The baseline trap**: a lollipop's stem visually asserts that zero
is the baseline. If the y-axis doesn't start at zero, the stems become
a lie — the length-to-data relationship breaks, but the visual
implies it hasn't. Non-zero baseline is dot-plot territory, not
lollipop territory.

**The diet-bar failure mode**: if the stems are as thick as bars,
the chart is just an awkward bar chart — the form's whole point was
to *reduce* visual weight. Stems should be hair-thin (1–1.5px),
dots should be the visible element. The affordance is "dot position,
anchored by a trace to zero" — not "a bar with a bump".

**Paired lollipops** (dumbbell / barbell variant): two dots per
category connected by a single line segment. Excellent for
"before/after", "two groups", "current vs target" stories. The
connecting line encodes a range or a delta, so readers read the gap
itself as data. If you care about the gap, the dumbbell usually beats
two side-by-side bars.
