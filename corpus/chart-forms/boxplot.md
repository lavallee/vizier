---
id: boxplot
source: chart-forms
type: chart_pattern
title: Boxplot
tags: [distribution, summary, quartiles, comparison]
details:
  purpose_families: [Distribution]
  capsule: >
    A five-number summary per group: min, Q1, median, Q3, max, with
    outliers as dots. Tukey's invention for quick distribution
    comparison across many groups. Loses shape detail (bimodality
    hides inside the box); wins on compactness.
  when_to_use:
    - Comparing distributions across many groups (5-50+)
    - Quartile structure is the summary that matters (medians and IQRs)
    - The groups' distributions are roughly unimodal
    - Compactness and scannability matter more than shape fidelity
  when_not_to_use:
    - Distributions are multi-modal — boxplot hides the modes
    - Sample size per group is very small (<~10) — boxplot becomes misleading
    - Readers aren't trained on the form — it has a learning curve
    - Shape matters more than summary — use violin or ridgeline
  reading_checklist:
    - What do the box edges mean here? (Q1/Q3 is standard, but check — sometimes it's SD.)
    - What's the whisker rule? (1.5×IQR is common; others exist. Disclosed?)
    - Median vs. mean — is the line inside the box the median? If the mean is also shown, is it clearly distinguished?
    - Any group's box collapsed to a thin strip? That's tiny IQR — worth flagging.
  common_mistakes:
    - No outlier definition disclosed (1.5×IQR? 3×IQR?) — reader can't calibrate
    - Mean line added alongside median without clear marker — readers confuse them
    - Tiny width on the boxes — whiskers blur into box edges
    - No baseline grid — readers can't read Q1/Q3 precisely
    - Boxplots of count data that should be bars — count doesn't have a distribution shape
  alternatives:
    - id: violin
      when: Shape matters (multi-modality, tails)
    - id: ridgeline
      when: Many groups and shape matters — density curves stacked
    - id: histogram
      when: One or few groups — histogram preserves more detail
    - id: strip-plot
      when: Small samples where raw points are honest
  canonical_examples:
    - junkcharts/what-is-this-stacked-range-chart
  antipattern_examples:
    - nightingale/ive-stopped-using-box-plots-should-you
    - nightingale/i-stopped-using-box-plots-the-aftermath
  related_principles: []
---
The boxplot (Tukey's "box-and-whisker plot") is the compact
five-number summary: the box spans the interquartile range (Q1 to
Q3), a line inside marks the median, whiskers extend to a conventional
range (typically 1.5×IQR), and dots mark outliers beyond that. Many
boxplots fit side by side, so it's the go-to form for comparing
20 groups' distributions.

**Works when**: the summary statistics are what you care about and
the distributions are approximately unimodal. A boxplot of
test-scores across 30 classrooms is readable in a way 30 histograms
isn't.

**Fails when**: the distribution is multimodal — the box collapses
the modes into a middle blob, and readers can't see them. It also
fails with very small samples: with 5 points a boxplot invents
quartile structure that isn't really there.

**Variants**:
- **Violin plot**: wraps the boxplot in a density curve, showing
  distribution shape. Best when you want both summary AND shape.
- **Notched boxplot**: adds a confidence notch around the median;
  non-overlapping notches are a rough significance cue.
- **Jittered points overlay**: keeps the box but shows the raw
  observations as jittered dots — best of both worlds when sample
  size permits.

**Learning curve**: readers unfamiliar with the form see the box
edges as "most of the data" and miss that the whiskers extend past
them. A reading guide is almost always helpful for a general-audience
piece.
