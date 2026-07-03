---
id: histogram
source: chart-forms
type: chart_pattern
title: Histogram
tags: [distribution, one-variable, bins]
details:
  purpose_families: [Distribution]
  capsule: >
    Bars representing binned counts of a single continuous variable.
    The default tool for "what does this distribution look like?" —
    shape, spread, skew, modality. Bin-width choice shapes what you
    see; tune it.
  when_to_use:
    - Single continuous variable whose distribution shape matters
    - Sample size big enough to reveal shape (>~50 observations)
    - Readers should see modality, skew, or outliers at a glance
    - Comparison between 2-3 distributions (overlaid with transparency, or faceted)
  when_not_to_use:
    - Sample is tiny (<30) — use a strip plot or beeswarm
    - Comparing many distributions — use small multiples of histograms or ridgeline
    - Distribution is fundamental and precise quantiles matter — complement with a boxplot
    - You're mostly interested in the relationship to another variable — use scatterplot
  reading_checklist:
    - Bin width — too narrow shows noise, too wide hides structure. Would a different bin count tell a different story?
    - Shape — unimodal, bimodal, skewed? (Summary stats like mean/median can hide multi-modality.)
    - Outliers — dots at the extreme tails. Include or truncated?
    - Is the y-axis counts or density? Density normalizes across samples; counts are literal.
  common_mistakes:
    - Arbitrary bin width hiding structure — try a few; extreme bin widths change the story
    - Integer counts in a histogram of integer data — bins of width 1 with clear baselines
    - Log y-axis without labeling — wrecks the reader's intuition about count scale
    - Stacked histograms to compare groups — overlaid with transparency or faceted reads better
    - Starting the x-axis at an arbitrary nonzero value — the distribution's position matters
  alternatives:
    - id: boxplot
      when: Comparing medians and quartiles across groups; precise summary is the task
    - id: violin
      when: Want both distribution shape AND summary stats across groups
    - id: strip-plot
      when: Small sample; raw points are more honest than bins
    - id: ridgeline
      when: Comparing many groups — density curves stacked
  canonical_examples:
    - junkcharts/whats-a-histogram
    - junkcharts/equal-area-histograms
    - visualising-data/using-containers-house-skewed-data-values
  antipattern_examples: []
  related_principles: []
---
A histogram bins a continuous variable into equal-width intervals and
shows the count (or density) in each bin as a bar. It's the default
and usually the best first look at a distribution: shape, spread,
central tendency, skew, modality, and outliers all appear at a glance.

**Works when**: you have enough observations (>50 at minimum;
~200+ is safe) and the shape of the distribution is what matters.
The choice of bin width is the chart's most important dial — too
narrow and you see noise, too wide and you lose structure. Always
try 2–3 bin widths before committing.

**Fails when**: you're comparing many distributions (stacked
histograms are unreadable; faceted panels or ridgeline are better)
or you have so few observations that bins are arbitrary.

**Density variant**: replaces counts with a normalized density so
distributions with different sample sizes overlay cleanly. Loses
the literal "how many" information; gains the ability to compare
shapes.

**Cumulative variant (ECDF)**: plots the running fraction of
observations below each value. More sample-efficient than a histogram
for small samples; preserves every observation; harder to read for
multimodal structure.
