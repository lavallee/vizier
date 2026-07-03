---
id: radar-chart
source: chart-forms
type: chart_pattern
title: Radar chart
tags: [magnitude, profile, multivariate, often-wrong]
details:
  purpose_families: [Magnitude, Correlation]
  capsule: >
    A polygon-on-polar-axes form for comparing a handful of categorical
    attributes across one or a few entities. Mostly wrong, occasionally
    right. Reach for it only when shape-as-archetype is the story and
    every axis shares a commensurable scale.
  when_to_use:
    - 4–6 axes, all with commensurable units (e.g. standardized scores)
    - The story is "which archetype is this?" — specialist vs all-rounder
    - Comparing ≤3 entities, where crossings are deliberate
    - Each axis has a meaningful, non-arbitrary order around the circle
  when_not_to_use:
    - Axes have unrelated units (GPA + height + salary — no comparable scale)
    - More than ~6 axes — polygon shapes converge; everyone looks similar
    - Precise magnitude matters — position-on-a-shared-axis encodes better
    - More than 3 overlapping series — spaghetti, even with transparency
    - Axes would be in arbitrary order — the polygon "shape" reads as signal where there's none
    - The form is chosen for aesthetics ("it looks like a star") rather than a reader's task
  reading_checklist:
    - Are the axes on the same scale, or axis-normalized? Axis-normalized hides magnitude differences.
    - Is the axis order semantic (clockwise = related-attribute clusters) or arbitrary?
    - How many axes? Over 6, most shapes look like jagged circles.
    - Are series outlined or filled? Filled encodes area, which is double the data (2×values → 4×area).
    - Could the same story be told with grouped bars or a slope chart?
  common_mistakes:
    - Filling the polygon — area is a nonlinear function of values and overstates differences
    - Arbitrary axis order (alphabetical, data-column order) — polygon shape becomes meaningless but reads as signal
    - Different max per axis (auto-scaling) — readers can't compare magnitudes across axes at all
    - Too many overlapping series — transparency helps but doesn't rescue ≥4 entities
    - Using radar because "it's eye-catching" when bars would be clearer — form chasing aesthetic
    - Labels placed inside the chart, colliding with polygon edges or axis lines
  alternatives:
    - id: small-multiples
      when: Multiple entities to compare — one bar-chart panel per entity beats overlapping polygons
    - id: parallel-sets
      when: Attributes are categorical and you care about co-occurrence rather than magnitude
    - id: slope-chart
      when: Comparing two scenarios (before/after) across several attributes
    - id: dot-plot
      when: Single entity, many attributes, zero-based optional — readable and precise
    - id: heatmap
      when: Many entities × many attributes — color encoding scales where shape doesn't
  canonical_examples:
    - nightingale/the-stellar-chart-an-elegant-alternative-to-radar-charts
  antipattern_examples:
    - junkcharts/an-overused-chart-why-it-fails-and-how-to-fix-it
  related_principles: []
---
The radar chart — also called spider chart, web chart, or star plot —
plots a handful of attribute values on spokes around a center point,
then connects them into a polygon. The shape of that polygon is what
readers perceive.

That shape is why the form is popular. It's also why the form is
usually wrong.

**The trap**: the visual affordance of "shape" implies that shape
carries meaning. Readers see a pentagon-that-leans-right and interpret
"this entity is strong in the right-side attributes, weak in the
left-side ones." But the shape is entirely determined by the order the
analyst chose to place axes around the circle. Swap two non-adjacent
axes and the "shape" changes completely. The lean is an artifact, not
a finding — unless the axis order is itself semantic (which it almost
never is in practice).

**The compounded trap**: filled radars encode the data twice. The
polygon's perimeter encodes the values directly (position on each
spoke), but the filled area is a *nonlinear function* of those values.
Double one value while halving another and the area might barely
change even though the story is completely different.

**When it earns its keep**: sports-analytics archetypes where all
axes are already standardized to 0–100 percentile ranks and the
question really is "which archetype is this?" (all-rounder vs
specialist). The axis order can be chosen to cluster related
attributes, so the polygon's lean is semantic. Kept to 5–6 axes and
≤3 entities, it can communicate archetype at a glance in a way that
stacked bars can't.

**When a bar chart wins**: almost every other case. A sorted bar
chart for a single entity's attributes gives precise values, doesn't
imply spurious shape, and scales to any number of attributes. For
multiple entities, small multiples of bars — one panel per entity,
shared x-axis — let readers compare archetypes without the polygon's
illusions.

**The Stellar Chart**: a radar variant that drops the connecting
polygon entirely, leaving just the dots on each axis. Eliminates the
fill-area encoding issue and the shape-from-axis-order artifact, at
the cost of the "gestalt archetype" read the polygon provides. A
reasonable middle-ground for when you want the radial layout without
its lies.
