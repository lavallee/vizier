---
id: strip-plot
source: chart-forms
type: chart_pattern
title: Strip plot (1-D scatter)
tags: [distribution, raw-points, small-sample]
details:
  purpose_families: [Distribution]
  capsule: >
    Every observation as a dot on one axis. The most honest form for
    small samples — no binning choices, no summary, no invented
    structure. Beeswarm variant spreads overlapping dots horizontally
    so density is readable.
  when_to_use:
    - Small sample (<100) where every observation matters
    - Showing individual points is more honest than a summary
    - Adding raw points over a box/violin for detail
    - Comparing a few groups with clear individual points per group
  when_not_to_use:
    - Very large samples (>~1000) — overplotting hides the pattern, use a histogram
    - Reader needs summary stats — use boxplot or violin
    - Distribution shape is what matters — density or histogram
  reading_checklist:
    - Is every observation visible, or are they overplotted without jitter?
    - Is the jitter random (hides density) or beeswarm (shows density)?
    - Is there a reference line (mean, median) to anchor the group?
    - At this sample size, can you actually see individual points — or has density eaten them?
  common_mistakes:
    - No jitter when points overplot — multiple equal values collapse to one
    - Too much jitter — looks like a scatter without a second variable
    - No groupings or labels — readers see dots but not meaning
    - Used when n is large — becomes a dense strip, not an informative plot
    - Missing reference line (mean, median) when it would help anchor the display
  alternatives:
    - id: histogram
      when: Large sample where shape matters more than individuals
    - id: boxplot
      when: Summary across many groups
    - id: violin
      when: Want shape AND summary
    - id: dot-plot
      when: Categorical axis with one value per category
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A strip plot puts every observation on a single axis as a dot — no
binning, no density estimation, no summary. The "1-D scatterplot."
When paired with jitter (small random perpendicular offset) to
avoid overplotting or with a beeswarm layout (dots pushed sideways
so they don't overlap), the form shows individual observations and
their distribution at once.

**Works when**: the sample is small (<100) and every point has
weight. Clinical trial data, panel survey responses, small-group
comparisons. Also excellent as an overlay on top of a boxplot or
violin — summary plus raw observations.

**Fails when**: the sample is large. Even with jitter, 1000+ points
on one axis becomes a solid band; switch to histogram or density.

**Beeswarm variant**: dots are laid out horizontally so they don't
overlap. Preserves every point's exact y-value while revealing
density. Best at sample sizes of 50-500.

**Jitter strategy**: uniform jitter up to some fraction of the
between-group spacing is standard. Too little and points hide each
other; too much and the plot loses its 1-D discipline.
