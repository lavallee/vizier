---
id: ridgeline
source: chart-forms
type: chart_pattern
title: Ridgeline plot
tags: [distribution, density, comparison, stacked]
details:
  purpose_families: [Distribution]
  capsule: >
    Stacked density curves, one per group, overlapping slightly. The
    form Wilkinson called "joyplot" — scales to 10-30 groups better
    than boxplot or violin by trading some vertical space for shape
    fidelity.
  when_to_use:
    - Many groups (10-40) whose distribution shapes should be compared
    - Shape matters (modality, skew), not just summary stats
    - Sample per group big enough for a smooth density (>~50)
    - Groups have a natural order (time, intensity, geography)
  when_not_to_use:
    - Few groups (<6) — violins or histograms read better
    - Precise quantile comparison — boxplot beats ridgeline
    - Order of groups is arbitrary — overlap creates meaningless visual rhythms
    - Small samples per group — density becomes noise
  reading_checklist:
    - Ordering — by magnitude, time, geography, or alphabetical (= missed opportunity)?
    - Bandwidth — do the curves look smooth but not over-smoothed? Extreme bumps may be artifacts.
    - Does any group show multiple peaks? That's a bimodality you'd lose in a boxplot.
    - How much do ridges overlap? More overlap = compact but busier reading.
  common_mistakes:
    - Bandwidth unchosen — default smoothing distorts multi-modal structure
    - Excessive overlap — curves bleed into each other, shape becomes illegible
    - Groups in alphabetical order when the pattern would emerge from time or magnitude order
    - No x-axis label — readers can't decode the scale
    - Using when the distributions are essentially identical — the form's power is contrast
  alternatives:
    - id: violin
      when: 6-12 groups; compact box+density per group
    - id: boxplot
      when: Many groups; summary stats suffice
    - id: small-multiples
      when: Groups should be compared panel-by-panel without overlap
    - id: histogram
      when: Few groups; histogram per group (overlaid or faceted) preserves shape better
    - id: strip-plot
      when: Sample per group is small; raw points are honest
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
Ridgeline plots stack kernel density curves for many groups, with each
curve offset slightly so the stack reads top-down. The form was
popularized as "joyplots" after the Joy Division album cover (itself
a ridgeline of pulsar emissions). Recognized in statistical
visualization as a solid alternative to boxplot/violin for many-group
distribution comparison.

**Works when**: you have ~10-40 groups with meaningful ordering. The
stacking means you use vertical space efficiently; the overlap means
you can see shape contrasts that would be lost in separate panels.

**Fails when**: groups are few (a single clean chart is better) or
when they're in arbitrary order (the overlap invents visual rhythms
that aren't in the data).

**Choosing bandwidth and overlap**: two parameters that set the
form's feel. Narrower bandwidth shows more detail at the cost of
noise; more overlap compresses vertically at the cost of clarity.
Try both and pick by what story emerges.
