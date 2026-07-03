---
id: diverging-bar
source: chart-forms
type: chart_pattern
title: Diverging bar chart
tags: [deviation, bar, reference-point]
details:
  purpose_families: [Deviation, Magnitude]
  capsule: >
    Bars that extend left or right from a central axis, encoding
    positive or negative deviation from a reference. The default form
    for "who's above and below?" stories — temperature anomalies,
    budget surpluses/deficits, Likert-scale responses.
  when_to_use:
    - Data has a natural reference point (zero, mean, target)
    - Direction (above vs. below) is part of the story
    - Reader wants to see magnitude on both sides symmetrically
    - Likert-scale survey results (agree / disagree with neutral middle)
  when_not_to_use:
    - No natural reference point — use a regular bar chart
    - Only one direction has data — unused white space wastes half the chart
    - Many categories where precise-value-reading matters — the center axis doubles scanning cost
    - Small deviations that the form exaggerates
  reading_checklist:
    - Where's the reference axis? ("Zero," "average," "target," "previous period" — it should be labeled.)
    - Color — diverging (two hues away from center) or just one hue? Diverging signals the reference.
    - Are both sides equally visually weighted, or is one side muted (biasing interpretation)?
    - Items sorted — by magnitude of deviation? Alphabetically? By category?
  common_mistakes:
    - Hidden / implicit reference — always show the center axis explicitly
    - Mixing positive and negative on the same-colored bars — convention is to use divergent palette
    - Unequal color weight (bright positive, muted negative, or vice-versa) — biases interpretation
    - Using for Likert data but stacking "Strongly agree" outside "Somewhat agree" — order matters
    - No axis label on the reference — what does "zero" mean here?
  alternatives:
    - id: bar-chart
      when: No natural reference; all bars start from a common baseline
    - id: stacked-bar
      when: Likert-scale responses — use a diverging-stacked-bar variant
    - id: dot-plot
      when: Showing deviations without heavy visual weight of bars
    - id: heatmap
      when: Many categories × many time points; spatial pattern matters
  canonical_examples:
    - eagereyes/when-bars-point-down
    - nightingale/tear-up-your-baseline
    - eagereyes/baselines
  antipattern_examples:
    - eagereyes/the-possible-stratagem-behind-the-biden-bar
  related_principles: []
---
A diverging bar chart uses a central axis (typically zero, a mean,
or a reference rate) and extends bars left (below reference) or
right (above). The form makes deviation direction and magnitude
readable at a glance.

**Works when**: the reference point is semantically meaningful.
Temperature anomalies from baseline, surplus/deficit from
break-even, Likert responses around a neutral midpoint, election
swing from previous cycle — the reference is what gives the chart
its argument.

**Fails when**: there's no natural reference or when the bars all
point the same way. If your data is all positive deviations, a
regular bar chart serves better — the diverging layout wastes half
the chart and invites readers to look for a negative half that
doesn't exist.

**Diverging-stacked variant** for Likert data: stacks "Strongly
disagree" and "Disagree" on the left, "Agree" and "Strongly agree"
on the right, with "Neutral" straddling the axis. Color by intensity
(dark = strong, light = mild). Great for comparing survey items
side by side.

**Color choice**: convention uses a divergent palette — two hues
away from a neutral center (red/blue, orange/teal). Use the same
saturation on both sides; uneven visual weight biases interpretation
about which side is the "story."

**Axis placement**: some variants put the reference axis on the side
rather than the middle, with positive-deviation bars above it and
negative below. Readable for small datasets; less compact than the
symmetric layout for many categories.
