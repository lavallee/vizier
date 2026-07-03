---
id: calendar-heatmap
source: chart-forms
type: chart_pattern
title: Calendar heatmap
tags: [time, cyclic, density, categorical-time]
details:
  purpose_families: [Change over time, Distribution]
  capsule: >
    A grid laid out by day-of-week × week-of-year (or similar calendar
    decomposition), with each cell colored by magnitude. Optimized for
    revealing weekly, monthly, and seasonal cycles at a glance —
    GitHub's contribution graph is the canonical instance.
  when_to_use:
    - Daily-or-finer cadence data over months or years
    - Cyclic patterns matter — weekdays vs weekends, seasons, pay cycles
    - Reader should see both "is today high?" AND "what's the rhythm?"
    - Activity counts, transaction volumes, sleep/exercise logs, commits
  when_not_to_use:
    - Continuous numeric x-axis makes more sense (use a line chart)
    - You care about precise values, not pattern — a table or line beats color
    - Sub-daily granularity is the story — use a day×hour heatmap
    - Fewer than ~6 weeks of data — the grid is too sparse to reveal rhythm
    - Scale spans orders of magnitude and linear color would mask variation (use log-color, or pre-log the values)
  reading_checklist:
    - Is the cell layout day-of-week × week (GitHub style), or month-grid (calendar style)? Affects what patterns pop.
    - What does "empty" mean — zero, or missing data? (The distinction matters for honesty.)
    - Linear color scale or quantile? Quantile hides magnitude but reveals rank; linear is the other way.
    - Is a day's baseline shift (DST, timezone changes, data-pipeline outage) being read as data?
    - Month/quarter boundaries marked? Without them, long-range seasonality blurs.
  common_mistakes:
    - Linear color on long-tail data — most cells saturate to one color, outliers dominate
    - Not annotating zero vs missing (both render as the empty/light color)
    - Grid cells too small — rhythm emerges but specific days become unclickable
    - Default viridis / rainbow scales — obscure cyclic structure; monotone-single-hue reads more faithfully
    - No week-start indication (Monday vs Sunday first is ambiguous across audiences)
    - Comparing cells across two different color scales (different-range yearly panels side-by-side mislead)
  alternatives:
    - id: heatmap
      when: x and y are both categorical (not calendar-derived) — ordinary 2D density
    - id: line-chart
      when: Continuous trend matters more than cyclic pattern
    - id: bar-chart
      when: Short time window (4-8 weeks); precision beats rhythm
    - id: ridgeline
      when: Comparing many distributions across days rather than magnitudes
  canonical_examples:
    - chart-forms/heatmap
  antipattern_examples: []
  related_principles: []
---
A calendar heatmap is a grid where each cell is one calendar unit
(usually a day) and color encodes that unit's value. The specific
layout — typically 7 rows (day of week) × N columns (weeks) — is what
makes it a *calendar* heatmap rather than a generic heatmap. The
layout does the work: weekly rhythms show up as horizontal bands;
seasonality shows up as column-block shading; single-day anomalies
pop out as stray bright cells against a calm field.

**Works when**: the underlying quantity has cyclic structure that
reveals itself at the day-of-week level. GitHub's green-contribution
graph works because developers really do commit more on weekdays and
less on weekends and holidays; the chart makes that structure legible
at a glance. Transaction volume, sleep duration, calls to a hotline,
bike-share trips — these all have weekly and seasonal cycles that a
line chart would smooth out.

**Fails when**: the cyclic dimension isn't actually there. Plotting a
slowly-trending quantity on a calendar heatmap turns the cells into
noise; a line chart shows the trend faithfully. Also fails when the
reader needs precise values — color is a coarse channel, and reading
"is this 42 or 47?" off a colored cell is guesswork.

**Empty vs zero**: the classic honesty trap. A day with zero
activity and a day with missing data render as the same "blank" cell.
Either annotate the distinction (different cell border, tooltip) or
drop the missing days entirely — don't let readers see a
false-uniform stretch that was really a data outage.

**Color-scale choices**: the default rainbow/viridis-on-dark design
obscures calendar structure because its hue cycles are orthogonal to
the data's real variation. Monotone single-hue scales (GitHub's
grays-to-greens, say) read as "more vs less" without competing
visual narratives. For long-tail data, log-transform the values
*before* mapping to color — linear-on-log-data squashes the bulk of
your cells into the low end.

**Month-grid variant**: instead of 7×N, show one traditional
month-calendar per month (a 5×7 mini-calendar, repeated). Reads
closer to a real wall calendar; slightly worse at revealing
pure-weekly rhythm (the weekdays move column-by-column across
months), slightly better at anchoring readers in specific dates.
