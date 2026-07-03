---
id: streamgraph
source: chart-forms
type: chart_pattern
title: Streamgraph
tags: [part-to-whole, change-over-time, feature]
details:
  purpose_families: [Part-to-whole, Change over time]
  capsule: >
    A stacked area chart with a centered (or offset) baseline. More
    editorial feel than analytic tool. Works for feature stories where
    overall flow shape is the story — not for reading precise values.
  when_to_use:
    - Feature/editorial piece where visual impact matters
    - Many categories (>6) that would crowd a stacked area
    - Total envelope shape is the story — not individual values
    - Readers shouldn't need to extract exact numbers
  when_not_to_use:
    - Readers need to read specific values — streamgraphs hide the zero baseline
    - Analytical comparison across categories — layers float unpredictably
    - Few categories (<4) — stacked area is clearer
    - Stable total where a 100%-stacked area would tell the story
  reading_checklist:
    - Is this piece editorial or analytical? Streamgraph is wrong for the latter.
    - Baseline — centered, offset, or zero? Centered makes precise values unreadable.
    - Are bands labeled inline, or buried in a color legend?
    - Envelope shape — does it grow, shrink, or flutter? That's usually the story.
  common_mistakes:
    - Using streamgraph when a stacked area would work — novelty tax
    - No labels on the bands — floating ribbons are unidentifiable
    - Hover-only labeling for print export — labels missing entirely
    - Poorly-chosen category order that creates visual chaos
    - Ordering by alphabetical instead of by similarity or magnitude
  alternatives:
    - id: stacked-area
      when: Analytical use; zero-baseline matters
    - id: small-multiples
      when: Reader needs per-category trajectory, not aggregate shape
    - id: line-chart
      when: Individual series trajectories are the story
    - id: ridgeline
      when: Distribution per category over time is the real question
  canonical_examples:
    - visualising-data/making-sense-of-streamgraphs
    - cairo-blog/googles-music-timeline-some-thoughts-html
    - nightingale/endless-river-an-overview-of-dataviz-for-categorical-data
  antipattern_examples:
    - junkcharts/leave-good-alone
  related_principles: []
---
A streamgraph is a stacked area chart with the baseline adjusted —
centered (symmetric around an axis) or offset — rather than anchored
at zero. The NYT Movie Box Office piece and Lee Byron's music-listening
charts popularized the form in the late 2000s.

**Works when**: the piece is feature-editorial and the overall shape
is the story. "How did music genre shares evolve over a decade" reads
beautifully as a streamgraph; individual numbers are beside the point.

**Fails when**: readers need to extract specific values. The centered
baseline means you can't read absolute quantities from the y-axis;
each band's bottom edge depends on what's below it. For analytical
reading, stacked area (zero-baseline) is more honest.

**Variants**:
- **ThemeRiver** (original academic form): centered baseline, fixed
  ordering.
- **Wiggle / silhouette**: adjusts layer order dynamically to
  minimize visual noise.
- **Expand / percentage streamgraph**: 100% normalized so the total
  is constant; emphasizes share shifts over time.

**Cosmetic essentials**: label bands directly (in-line) rather than
in a color legend. Order categories so the largest stays nearest the
axis — it anchors the shape for readers. Use a muted palette; bright
colors on many overlapping bands creates visual noise.
