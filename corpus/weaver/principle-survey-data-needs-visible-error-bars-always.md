---
details:
  origin: weaver/PRINCIPLES.md
  stage: Build
fetched_at: '2026-04-18T19:23:27.593379Z'
id: principle-survey-data-needs-visible-error-bars-always
source: weaver
tags:
- build
title: Survey data needs visible error bars, always
type: principle
---

Whenever a chart shows a survey-sourced estimate (ACS, CPS, BRFSS,
Pew, GSS, CES), render the published margin-of-error as a whisker on
the chart itself. Do not show only the point estimate and let readers
assume precision the data doesn't have.

Concrete example. The Maplewood age pyramid first showed 4,086 boys
and 3,192 girls aged 0-17 from the ACS 5-year. Read as point
estimates, that's a 28% male excess — implausible enough to prompt
a reader question. The cell-level MOEs tell a different story:
the 15-17 female cell is 308 ±103 at 90% CI, ±33% relative. Once
you combine the band-level MOEs (via sqrt-sum-of-squares per Census
guidance) and render them as whiskers, the apparent skew is visibly
inside sampling variance.

This applies specifically to ACS at small geographies (MCDs, places
under ~50k). For larger geographies (counties, states) the MOEs are
tight enough that the whisker is nearly invisible — which is itself
informative ("ACS here is precise") and worth showing.

Practical patterns:

- **Single-cell estimates**: thin horizontal line through the bar
  tip with small vertical caps at ±MOE. Rendered in a high-contrast
  color (black on dark theme, dark-gray on light) so it stays
  legible over the colored bar.
- **Stacked or grouped estimates**: combine cell MOEs as
  sqrt(sum(MOE_i²)) per the Census ACS handbook. Don't sum MOEs
  linearly (that over-states uncertainty) or take a max (under-states).
- **Ratios and rates**: delta-method propagation if you want
  precision; a rough "±5pp" annotation is usually enough for journalism.
- **Captions**: say what the CI is (90% for ACS, 95% for most polls)
  and how to read it. Readers don't remember what ±X means across
  datasets.

The chart is not the final word. The point estimate is a *best guess*
drawn from a sample, and readers should see the uncertainty the
source publishes — not infer it from a trailing sentence. The upstream
half of this principle lives in Ingest (*preserve uncertainty at ingest,
don't reconstruct downstream*); if MOEs aren't on the data, this
principle can't be honored at all.
