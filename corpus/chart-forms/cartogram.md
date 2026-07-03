---
id: cartogram
source: chart-forms
type: chart_pattern
title: Cartogram
tags: [spatial, map, distortion, population]
details:
  purpose_families: [Spatial, Magnitude]
  capsule: >
    A map where regions are resized (and often reshaped) according to
    a metric — usually population. Fixes the choropleth's area-
    dominance bug for count-based stories at the cost of geographic
    recognizability.
  when_to_use:
    - A count or magnitude whose story the choropleth would distort
    - Readers can still recognize regions under moderate distortion
    - The metric driving resizing is genuinely the story (population-weighted election maps, GDP maps)
    - You're willing to lose geographic fidelity for magnitude fidelity
  when_not_to_use:
    - Readers need to find specific places — distortion hurts navigation
    - The metric doesn't meaningfully drive the size (why are we distorting?)
    - The distortion is so severe regions become unrecognizable
  alternatives:
    - id: choropleth
      when: Showing a rate or ratio where area distortion isn't a problem
    - id: proportional-symbol-map
      when: Want to keep the real map but add a count overlay
    - id: hex-bin-map
      when: All regions should be visually equal-weight
  canonical_examples:
    - observable/joewdavies-grid-cartogram-of-europe
    - cairo-blog/elegant-maps-reveal-grim-reality-html
    - cairo-blog/multiple-shapes-multiple-projections-html
  antipattern_examples: []
  reading_checklist:
    - What metric is driving the distortion? (Should be stated, not guessed.)
    - Can you still identify the regions, or has the distortion crossed into illegibility?
    - Is the cartogram a companion to a normal map, or a replacement? Companions are safer.
    - Which variant is it — contiguous, Dorling, equal-area hex? Each has different tradeoffs.
  common_mistakes:
    - Too much distortion — readers can't identify regions any more
    - Using a cartogram when the choropleth would have worked — distortion tax isn't paying for anything
    - Not pairing with a regular map — readers lose geographic anchor
    - Dorling circles used when adjacency matters — circles float free of their neighbors
    - No legend explaining what drove the resizing — readers assume area
  related_principles: []
---
A cartogram remaps geography according to a variable — most commonly
population. A US election cartogram makes California bigger and
Wyoming smaller, so that the visual weight of each region matches its
political weight rather than its empty acreage.

**Works when**: the choropleth would mislead. If the metric you care
about is really per-person (votes, disease cases, income) but raw
land area would swamp it, a cartogram is the corrective. The
distortion itself is a sign that conveys the mismatch between
geographic intuition and demographic reality.

**Fails when**: readers can't recognize the distorted regions, or
when the metric driving the resize isn't actually the story. A
cartogram "just to look interesting" fails because the distortion
costs navigation ability.

**Variants**:
- **Equalized (hex/square) cartograms**: every region gets the same
  size. Useful when you want to treat every state or country as
  equal-weight visually. Loses everything except topology.
- **Non-contiguous** (NPR "states as circles"): geography is abandoned,
  regions float; preserves shape of regions but not adjacency.
- **Contiguous, Dorling, Gastner-Newman**: progressively more
  computationally-constrained methods that preserve adjacency or
  shape or both while distorting sizes.

Choice among variants is a tradeoff. Equalized is clearest for
small-count data; contiguous is best when geographic pattern matters;
Dorling (each region a proportional circle) is most readable for
strong magnitude differences.

**Pairing**: a cartogram often lives alongside a regular choropleth
in the same piece. Reader gets both views — "what the landscape
looks like" and "what the population actually weighs."
