---
id: box-and-jitter-strip
source: chart-forms
type: chart_pattern
title: Box-and-jitter-strip
tags: [distribution, categorical, hybrid, small-n-safe]
details:
  purpose_families: [Distribution]
  capsule: >
    A boxplot overlaid (or adjacent) with every point jittered out so
    sample size and density show. Gets the summary-stat read of a
    boxplot and the honest-every-point read of a strip plot, at the
    cost of a denser chart. The honest small-N compromise.
  when_to_use:
    - Samples per group are modest (10–100) — a boxplot alone would hide N
    - Groups might have outliers, bimodality, or uneven density worth seeing
    - Readers want summary stats (median, IQR) AND the raw observations
    - Paper/plot audiences familiar with both forms; the overlay reads immediately
  when_not_to_use:
    - Samples per group > ~200 — overplotted jitter becomes a smudge; use violin + boxplot
    - Samples per group < 10 — just show the raw dots; the box is over-claimed summary
    - Audiences unfamiliar with boxplots — explain one thing at a time
    - Space is tight — the overlay needs vertical or horizontal room
  reading_checklist:
    - Is N visible? Count roughly per group — sparse groups lose their boxplot credibility.
    - Are outliers from the boxplot the same points the strip plot shows as far-out dots? (They should be.)
    - Is the jitter width bounded so dots don't wander outside their group's column?
    - Is the box semitransparent or offset? Dots sitting behind an opaque box are worse than useless.
    - Is every sample shown, or just a jitter-downsample? Downsampling should be disclosed.
  common_mistakes:
    - Opaque box over the dots (you can't see the individual data any more)
    - Jitter too wide — points cross group boundaries and the category split blurs
    - Jitter not seeded — chart moves between refreshes, undermining trust
    - Dots too large for the N — an N=100 group fills its column with overlapping blobs; use smaller r or reduce opacity
    - Using this hybrid when a violin+box would carry the same story with less overplot
  alternatives:
    - id: boxplot
      when: Summary stats are enough; individual points would just be noise
    - id: strip-plot
      when: N is small-to-medium and the dots should dominate; boxplot overlay would be over-claim
    - id: violin
      when: N is large enough to estimate density faithfully; shape beats individual dots
    - id: ridgeline
      when: Many groups (>6) and density shape is comparable across them
  canonical_examples:
    - chart-forms/boxplot
    - chart-forms/strip-plot
  antipattern_examples: []
  related_principles: []
---
A box-and-jitter-strip puts two forms on top of each other: a boxplot
for the summary (median, IQR, whiskers) and a strip plot (jittered
dots) for every actual observation. The overlay is dense but honest:
readers see both the story the summary tells and the evidence behind
it.

**Why combine them**: a boxplot collapses N samples into five
numbers. At N=40 that's fine; at N=12 it's over-claim. A strip plot
shows every dot but loses the summary read (you can't glance and
know the median). The hybrid recovers both at once.

**Why not always combine them**: at large N (hundreds per group),
the strip plot becomes a smudge and the boxplot gets hidden
underneath it. At very small N (5 or fewer), the boxplot's quartile
lines are drawn from too few points to be meaningful — better to
just show the dots and annotate the median.

**Cosmetic defaults that matter more than usual**: the box must be
semitransparent (say 30-40% opacity) so the dots behind it read. The
jitter must be bounded — typically to ~60% of the band width — so
dots stay clearly inside their group's column. The jitter seed should
be fixed so the chart is stable across refreshes; a wobbling chart
undermines the form's whole claim of "here are the real points".

**When N varies across groups**: the hybrid is especially useful
because a boxplot of 8 points looks visually identical to a boxplot
of 80, and readers can't see the difference. With the strip-dots
behind, the N-disparity is immediate: one column has a sparse
scatter, the other is packed.
