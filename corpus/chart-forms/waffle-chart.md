---
id: waffle-chart
source: chart-forms
type: chart_pattern
title: Waffle chart
tags: [part-to-whole, magnitude, count]
details:
  purpose_families: [Part-to-whole, Magnitude]
  capsule: >
    A grid of small squares colored by category. Makes abstract
    percentages concrete — "60 out of 100" is visible as 60 colored
    squares. The right form for pieces where readers should *feel*
    the numbers, not just read them.
  when_to_use:
    - Part-to-whole with a small natural denominator (out of 100, out of 10)
    - Emotional / narrative impact matters (social data, human scale)
    - Category count is modest (2-5 segments)
    - Reader should be able to count if they wanted
  when_not_to_use:
    - Many categories — colors exceed perceptual limits
    - Comparing many wholes — waffles don't line up for cross-comparison
    - Abstract metrics where the unit doesn't map to countable things
    - Data where precise comparisons matter — bars are more accurate
  reading_checklist:
    - What does each square represent? ("1 person," "1%," "1 case"?)
    - Is the denominator meaningful — is "out of 100" or "out of 10" the right unit?
    - Could you actually count the colored squares? (That's the form's core affordance.)
    - Multiple waffles side-by-side? They compare only at the same scale.
  common_mistakes:
    - Non-round denominators forced into 100 squares — fractional cells mislead
    - Too many colors — readers can't distinguish them in a dense grid
    - Random-looking cell order — cells should fill left-to-right, bottom-up
    - Missing labels on the colors — readers can't decode without a legend
    - Using when a stacked bar would work just as well — novelty tax
  alternatives:
    - id: stacked-bar
      when: Analytical / compact — no narrative reason for individual squares
    - id: pie-chart
      when: Single dominant slice — pie works in the very narrow case
    - id: dot-plot
      when: Many categories; waffle cells would crowd
    - id: bar-chart
      when: Analytical comparison between multiple wholes
  canonical_examples:
    - eagereyes/engaging-readers-with-square-pie-waffle-charts
    - observable/observablehq-plot-survey-waffle
    - eagereyes/charts-and-metaphors
  antipattern_examples: []
  related_principles: []
---
A waffle chart is a 10×10 (or 5×5, or similar) grid of small squares
colored by category. Its power is making abstract numbers concrete:
"25% of households" becomes 25 colored squares in a grid of 100,
and readers can verify that by counting.

**Works when**: the piece has narrative weight and readers should
*feel* the number rather than just read it. "1 in 8 Americans is
food-insecure" reads differently as "12.5%" than as a grid of 100
squares with 12 colored in. The Pudding and FiveThirtyEight use waffle
charts for exactly this emotional-literal effect.

**Fails when**: precise comparison matters. Bars encode magnitude
better; waffles are for communication first and analysis second.

**Variants**:
- **Icon array**: replace squares with human figures (for population
  statistics) or domain-specific icons (houses, cars, ballots). More
  emotional impact, less visual density.
- **Square waffle**: 10×10 grid, 1 square = 1%. Most readable.
- **Rectangle waffle**: m × n grid where m×n = denominator. Useful
  when the denominator isn't 100.
- **Bar-to-waffle hybrid**: a rectangular count grid sized by the
  total.

**Cell ordering**: left-to-right, bottom-to-top (like reading) for
cumulative fill. Don't scatter colored cells randomly — readers
interpret the sub-pattern as part of the data.
