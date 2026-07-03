---
id: connected-scatter
source: chart-forms
type: chart_pattern
title: Connected scatter
tags: [correlation, change-over-time, path]
details:
  purpose_families: [Correlation, Change over time]
  capsule: >
    A scatterplot where observations are ordered in time and joined
    by a line. The path itself is part of the story — "how we got
    from here to there" across two dimensions. Great for before-COVID /
    after-COVID stories, country trajectories.
  when_to_use:
    - Two continuous variables with an ordered sequence of observations (years, months)
    - The PATH matters, not just start and end — "how it got there"
    - ~6-40 observations (enough to see a trajectory; not so many that it tangles)
    - Telling a journey / trajectory story, not a correlation summary
  when_not_to_use:
    - The observations aren't really ordered — use a plain scatter
    - Too few points (<5) — a table is clearer
    - Too many points (>40) — line becomes tangled
    - The correlation itself is the story — just show the scatter
  reading_checklist:
    - Which end is the start, which is the end? (Gradient, arrowhead, or endpoint labels needed.)
    - What are the axes? (Two variables whose relationship is the story.)
    - Are the key inflection points annotated? A connected scatter without annotations is half a chart.
    - If the path loops or zigzags — what happened? (That's the story.)
  common_mistakes:
    - No direction indicator — readers don't know which end is start / end
    - Unlabeled intermediate points — reader sees the path but not the milestones
    - Line too thick / too thin — harder to read than balanced
    - Using for data without real ordering — misleads about temporal structure
    - Skipping annotations at key inflection points (crises, transitions)
  alternatives:
    - id: scatterplot
      when: Just showing correlation; order doesn't matter
    - id: line-chart
      when: One variable over time; the other isn't the subject
    - id: small-multiples
      when: Many trajectories — grid of connected scatters per entity
  canonical_examples:
    - eagereyes/the-connected-scatterplot-for-presenting-paired-time-series
    - cairo-blog/in-praise-of-connected-scatter-plots-html
    - cairo-blog/more-connected-scatter-plot-fun-html
    - cairo-blog/bloomberg-visual-datas-connected-html
  antipattern_examples:
    - nightingale/connected-scatterplots-make-me-feel-dumb
  related_principles: []
---
A connected scatter plots two variables against each other and joins
the points in observation order (usually time). The form combines
correlation and trajectory: readers see both "how these two quantities
relate" and "how we moved through that space."

**Works when**: the story is a journey. Unemployment × inflation year-by-year for one country tells a different story than a bar chart of either or a correlation summary of both. The line reveals that in the 70s both climbed together, then diverged in the 80s — a fact neither variable alone reveals.

**Fails when**: the observations aren't actually ordered. Connecting dots
in a plain scatterplot implies a path that isn't in the data.

**Direction encoding**: mandatory. Options include (a) arrowhead at
one end of the line; (b) gradient color along the path (light at
start → dark at end); (c) labels at start and end ("2015" / "2024");
(d) dot size growing along the path. Choose at least one; readers
can't guess.

**Annotations**: connected-scatter trajectories often have meaningful
inflection points — a crisis, a policy change, a pandemic. Annotate
those directly on the chart; the reader needs context to interpret
the twists.

**When it shines**: NYT and FT have used this form heavily for
"pre-COVID / COVID / post-COVID" trajectories on pairs like retail
spending × restaurant bookings, or GDP × unemployment. The path is
literally the story.
