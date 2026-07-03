---
id: violin
source: chart-forms
type: chart_pattern
title: Violin plot
tags: [distribution, density, comparison]
details:
  purpose_families: [Distribution]
  capsule: >
    A mirror-pair of density curves per group, often with a boxplot
    inside. Shows shape (modality, skew) across groups where boxplots
    would collapse detail. Best when distribution shape is part of
    the story.
  when_to_use:
    - Comparing distribution SHAPES across multiple groups
    - Distributions might be multi-modal, skewed, or long-tailed
    - Sample per group is big enough to estimate density (>~50)
    - Readers will look at the shape (not just summary statistics)
  when_not_to_use:
    - Summary stats (median/IQR) are enough — boxplot is more compact
    - Samples per group are small — density estimate is unreliable
    - Many groups (>~15) — violin shapes crowd each other
    - Readers aren't familiar with the form — it's unusual outside data-science audiences
  reading_checklist:
    - Shape — is any group bimodal (two bulges)? That's the violin's killer feature over boxplot.
    - Is there a box or median line inside? Summary + shape in one view is ideal.
    - Bandwidth tuning — does it look smoothed or noisy? A noisy violin is often over-fit.
    - Any group where the violin is very narrow or very wide? That's a consistency / variance contrast.
  common_mistakes:
    - No boxplot or summary inside the violin — loses the quantile info
    - Bandwidth too narrow or wide — shape distorts; always tune it
    - Asymmetric violin when the mirror is unnecessary — use a ridgeline instead
    - Coloring each violin uniquely when they're all the same variable — save color for a real encoding
    - Tiny violins where the density shape isn't legible
  alternatives:
    - id: boxplot
      when: Compact summary across many groups suffices
    - id: ridgeline
      when: More than ~12 groups — ridgeline scales better
    - id: histogram
      when: One or two groups; histogram is more familiar
    - id: strip-plot
      when: Sample is small; show the raw points (beeswarm layout is a variant)
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A violin plot is a kernel density estimate mirrored around a central
axis, usually with a boxplot inside. The form shows distribution
shape (modality, skew, long tails) where boxplots would collapse
detail, and scales to ~10-15 groups before getting crowded.

**Works when**: your distributions might be multi-modal or otherwise
shape-interesting and you have enough sample per group (~50+) that
density estimates are reliable. Wage distributions, patient response
times, student test scores often have multi-modal structure that a
boxplot hides.

**Fails when**: small sample sizes (density becomes noise masquerading
as shape), or many groups (shapes crowd together). The form is also
relatively unfamiliar to general-audience readers — adding a reading
guide is often necessary.

**Embedded boxplot**: the best violin plots put a miniature boxplot
(or at least the median + IQR lines) inside each violin. Readers get
both summary and shape in one.

**Kernel bandwidth**: the single most important setting. Too narrow
and the violin looks noisy; too wide and it becomes a symmetric blob.
Tune on the data and disclose the choice in the caption for technical
readers.

**Half-violin variant**: for some layouts (e.g., paired comparisons),
a half-violin with raw points on the other side gives more information
than either alone.
