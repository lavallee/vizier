---
id: line-chart
source: chart-forms
type: chart_pattern
title: Line chart
tags: [change-over-time, time-series, default]
details:
  purpose_families: [Change over time, Correlation]
  capsule: >
    The default form for change over continuous time. Each line is one
    series; position encodes value, x-axis encodes time. Boring, which
    is its main virtue — readers don't have to learn a new form.
  when_to_use:
    - Continuous or quasi-continuous time (daily, monthly, quarterly)
    - One to ~6 series (more becomes spaghetti)
    - Values are meaningful in magnitude, not just rank
    - Trend is the story, not point-in-time comparison
  when_not_to_use:
    - Categorical x-axis — use a bar chart
    - Many series (>6) — use small multiples
    - Rank-over-time is the actual story — use a bump chart
    - Y-axis values span many orders of magnitude with uniform weight — consider log scale explicitly
  alternatives:
    - id: small-multiples
      when: More than 6 series, or comparable panels per category
    - id: slope-chart
      when: Only two time points matter — before / after
    - id: bump-chart
      when: Story is rank reshuffle, not magnitude
    - id: stacked-area
      when: Composition of a total changing over time
    - id: connected-scatter
      when: Two continuous variables over time; the trajectory is the story
  canonical_examples:
    - cairo-blog/lines-arent-just-for-time-series-html
    - cairo-blog/line-charts-arent-just-for-time-series-html
    - cairo-blog/defying-conventions-in-visualization-html
    - eagereyes/baselines
    - nightingale/tear-up-your-baseline
  antipattern_examples:
    - eagereyes/all-line-charts-are-wrong-but-some-are-useful
  reading_checklist:
    - Where does the y-axis start — zero, or the data's min? That shapes how dramatic "change" looks.
    - Is the x-axis continuous (sensible for a line) or categorical (wrong)?
    - Series labeled at the line's end, or buried in a legend?
    - Annotated inflection points — or does the reader have to guess what caused the bend?
  common_mistakes:
    - Y-axis choice not considered — start-at-zero and start-at-min tell different stories; pick on purpose
    - Corner legend with many colored squares — label lines at the right edge instead
    - No annotation at inflection points — the reader sees the shape but not why
    - Log scale applied silently — always label the axis explicitly
    - Too many series on one chart (>6) — switch to small multiples
    - Dual-axis (a second y-scale for another measure) — the two scales' alignment is arbitrary, so the chart invents a correlation that isn't in the data; use two charts, small multiples, or index both series to a common base (=100 at t0) on one axis
  related_principles: []
---
The line chart is the default for change over time and is almost never
the wrong first move. Readers have internalized it; no reading guide
needed. Its virtue is boringness.

**Works when**: your x-axis is continuous (dates, seconds, degrees)
and you have enough data points that connecting them traces a
meaningful trajectory. One to six series are readable simultaneously;
beyond that, lines start overlapping unpredictably.

**Fails when**: you have twenty series you want to compare — the chart
becomes spaghetti. The fix is small multiples (one line per panel)
or a highlight-one-series variant where most lines are muted grey and
only the subject of the story gets color.

Also fails when the x-axis is categorical — bars are better for
comparing discrete categories because position on the x-axis doesn't
imply an ordering.

**Cosmetic choices that matter disproportionately**: (a) y-axis start
point. A line chart that starts at zero emphasizes absolute magnitude;
one that starts at a rolling min-value emphasizes the movement.
Neither is always right; the right choice depends on whether the
reader's question is "how big?" or "is it moving?" (b) annotations at
inflection points do more pedagogical work than any legend can. (c)
label series at the right edge of the chart where the line ends
(right-aligned to the last data point), not in a corner-legend.
