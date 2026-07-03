---
id: icicle-plot
source: chart-forms
type: chart_pattern
title: Icicle plot
tags: [hierarchy, part-to-whole, linear]
details:
  purpose_families: [Part-to-whole]
  capsule: >
    A hierarchical chart laid out as horizontal (or vertical) bars
    stacked top-to-bottom by level. The linear cousin of treemap and
    sunburst — easier to read when the hierarchy is wide and shallow.
  when_to_use:
    - Hierarchical data that's wide and shallow (many leaves per branch)
    - Reader should see the full tree without radial distortion
    - Natural left-to-right or top-to-bottom reading works with the data
    - Leaves should be individually labelable
  when_not_to_use:
    - Shallow two-level hierarchy — stacked bar or treemap is cleaner
    - Very deep trees — icicle layouts grow long quickly
    - Precise magnitude comparison between leaves — bars are still better
    - Reader needs to "drill down" into one branch — sunburst with zoom works better
  reading_checklist:
    - Reading direction — top-to-bottom (hierarchy depth) or left-to-right (time)?
    - Each level a row (or column); does the width at each level encode value?
    - Labels — are narrow leaves still readable, or just blanks?
    - Flame-graph variant: heights stack (call-depth), widths are time. Recognize which you're in.
  common_mistakes:
    - Labels truncated on narrow leaves — leaves need enough width to be readable
    - Uniform color across all levels — depth visual cue is wasted
    - Alphabetical leaf order within a branch — sort by magnitude or semantic sequence
    - Using for flat data — adds hierarchy visual overhead where there isn't any
  alternatives:
    - id: treemap
      when: Rectangular packing preserves more space for small leaves
    - id: sunburst
      when: Circular layout reads better with drill-down interaction
    - id: stacked-bar
      when: Only two levels; linear form suffices
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
An icicle plot lays out a hierarchy as stacked bars: each level is a
row (or column), each branch's bar is sized by its value, and leaves
sit at the outermost edge. Tufte-era form; still a good choice when
the tree is wide.

**Works when**: the hierarchy is wide and shallow — many sibling
leaves per branch, 2-4 levels deep. Budget categories with many line
items, software-directory structures, ontology trees all read well
as icicle plots.

**Fails when**: the hierarchy is deep (bars stack farther than a
screen allows) or shallow (stacked bar or treemap reads the same
structure with less visual overhead).

**Orientation**: vertical icicle (levels as columns, time flowing
left-to-right) or horizontal (levels as rows, hierarchy flowing
top-to-bottom). Horizontal is more common; vertical reads better
when the hierarchy has a "time" semantic (protocol message trees,
call stacks, nested transactions).

**Flame graph variant**: icicle plots rotated 180° are commonly
called flame graphs and used for CPU profiling. Root at the bottom,
hot-call-paths rising to the top — the "flame" shape. Same form,
different domain conventions.
