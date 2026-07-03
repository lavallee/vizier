---
id: sankey
source: chart-forms
type: chart_pattern
title: Sankey diagram
tags: [flow, ribbon, conservation, categorical]
details:
  purpose_families: [Flow, Part-to-whole]
  capsule: >
    A diagram of conservation under flow: the total on the left equals
    the total on the right. Reach for it when the data has a real
    conserved quantity moving between discrete, mutually-exclusive states.
  when_to_use:
    - Real conserved quantity (energy, money, population, carbon, water)
    - Reader should see how that quantity partitions between states
    - Columns are mutually-exclusive categories, not time steps
    - Ribbon thickness carries meaningful magnitude
  when_not_to_use:
    - Funnel / cohort shrinkage — 'lost' users aren't a conserved bucket
    - Branching co-occurrence (attribute × attribute) — use parallel sets
    - Rank reshuffle — ribbon thickness fights small-integer rank deltas
    - Geography is the substrate — use a flow-map
    - Ornamental use with no defensible unit of ribbon-width
  alternatives:
    - id: parallel-sets
      when: Branching co-occurrence without flow conservation
    - id: bump-chart
      when: Story is ordering over time, not magnitude
    - id: stacked-area
      when: Part-to-whole over continuous time, no discrete states
    - id: flow-map
      when: Geography is the flow substrate (rivers, migration, trade)
    - id: stacked-bar
      when: Single-step funnel or shrinking cohort
    - id: chord-diagram
      when: Many-to-many within one set of nodes (not staged flow)
    - id: network-diagram
      when: Arbitrary graph structure without stages
    - id: arc-diagram
      when: Nodes have a linear order and connections are sparse
  canonical_examples:
    - observable/d3-sankey-component
    - visualising-data/energy-technologies-visualisation-for-the-iea
    - cairo-blog/bloomberg-visualizes-shrinking-html
    - cairo-blog/the-guardian-puts-flow-charts-on-map-html
  antipattern_examples:
    - junkcharts/clear-and-confused-states
    - visualising-data/google-analytics-introduces-visitor-flow-visualisation
  reading_checklist:
    - Does the left-total equal the right-total? If not, the chart lies by construction.
    - What is the unit of ribbon-width? (Pause if you can't name it.)
    - Are the columns mutually-exclusive states, not time steps?
    - Is the within-stage order semantic, or alphabetical (= meaningless)?
    - For each dominant ribbon, can you trace both its source and destination without guessing?
  common_mistakes:
    - Letting d3-sankey's default nodeSort tangle the ribbons — use `nodeSort(null)` with an explicit `stageOrder` per column
    - Skipping click-to-isolate or implementing it as hide-don't-dim; readers need to trace a node's full flow without losing context
    - Near-deterministic columns squashed into one diagram — when mode nearly determines outcome, split into two sankeys
    - Ribbons ordered left-to-right without a semantic order for the categories on each axis (alphabetical is almost never right)
    - Default black path-fill leaks through on bezier ribbons — always set fill=none on the link paths
    - Using a sankey when the left-total doesn't actually equal the right-total — the chart lies by construction
  related_principles:
    - weaver/principle-order-stage-categories-meaningfully
    - weaver/principle-reading-guide-directly-above-each-novel-diagram
    - weaver/principle-break-apart-near-deterministic-columns
  related_projects:
    - title: "Sankey: when and how (and when not to)"
      href: ../sankey-when-and-how/
      blurb: >
        Sibling essay on when the sankey earns its keep, how to keep ribbons
        legible, and the funnel/rank/flow-map anti-cases in depth.
---
A sankey is a diagram of **conservation under flow**. The total on the
left equals the total on the right, and each ribbon traces where a unit
of the conserved quantity went. That constraint is the sankey's
superpower: when the data really has a conserved quantity moving between
states, the ribbons show you the partition at a glance.

The constraint is also the trap. The visual language *asserts*
conservation. If the underlying data doesn't carry it, the ribbons imply
a partition that doesn't exist.

**Works when**: the quantity is really conserved (energy TWh through a
grid; dollars through a budget; species through an extinction funnel;
voters through mutually-exclusive outcomes). Each column is a discrete
categorical state, not a time point. Transitions between columns are
meaningful.

**Fails when**: the "flow" is a user funnel where the missing cohort
just stopped being counted — a sankey invents a "Dropped off" bucket
to satisfy the left-total-equals-right-total constraint, and readers
read that bucket as a destination. Or when there's no direction in the
data at all (parallel sets territory). Or when the magnitudes are
small-integer ranks that the thickness encoding can't discriminate.

**Cosmetic traps** even when the form fits: (a) not ordering categories
meaningfully — d3-sankey's default sort tangles ribbons; always use
`nodeSort(null)` with an explicit `stageOrder`. (b) near-deterministic
columns — when the mode nearly determines the outcome, a single joint
sankey compresses to a single dominant ribbon and hides the structure;
split into two. (c) click-to-isolate affordance missing — readers need
to trace one node's full flow, so clicking should dim-don't-hide the
rest of the diagram.
