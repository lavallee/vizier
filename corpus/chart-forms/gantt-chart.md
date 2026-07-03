---
id: gantt-chart
source: chart-forms
type: chart_pattern
title: Gantt chart
tags: [time, project, schedule, dependencies]
details:
  purpose_families: [Change over time, Part-to-whole]
  capsule: >
    Horizontal bars on a time axis, one row per task, spanning each
    task's start and end. The canonical form for project schedules.
    Adds dependency arrows and a critical-path highlight when the
    story is "what happens if task X slips?".
  when_to_use:
    - Project / production / broadcast schedule with 5–50 tasks
    - Readers need to see task duration AND task ordering
    - Dependencies matter — which tasks block which, critical path
    - Milestones (diamonds) mark decision/delivery points
  when_not_to_use:
    - Single-stream timeline (no concurrent tasks) — a timeline strip is simpler
    - Hundreds of tasks — zoom-to-detail affordances become essential; use a dashboard
    - The story is aggregate throughput, not individual tasks — use a burndown or cumulative-flow
    - Dates are unknown or rough — Gantt's precision implies the data is precise
  reading_checklist:
    - What does bar length encode: planned duration, actual duration, or both (planned-outline + actual-fill)?
    - Is there a critical path highlighted? If not, what's the consequence of task X slipping?
    - Are dependencies drawn, or is the reader inferring them from row order?
    - Milestone markers visually distinct from bars (diamonds, not tiny squares)?
    - Today's date / "as of" marker on the time axis?
  common_mistakes:
    - Dependency-arrow spaghetti — 30 tasks × 3 deps each = 90 arrows; becomes unreadable, use tooltips
    - Tasks sorted alphabetically instead of by start-date or dependency order
    - No critical-path signal — reader can't prioritize what to watch
    - Bars all one color even though some are "completed" / "in progress" / "at risk" / "blocked"
    - Time axis too coarse (months when story is weeks) or too fine (days when story is quarters)
    - Missing a "today" vertical line — readers can't orient themselves in the schedule
  alternatives:
    - id: line-chart
      when: Continuous progress over time (burndown, cumulative hours) — Gantt is overkill
    - id: matrix-plot
      when: Dependency structure is the real story, not durations — tasks × tasks matrix
    - id: slope-chart
      when: Before/after reschedule comparison on a handful of tasks
    - id: waterfall-chart
      when: Cumulative changes over discrete periods
  canonical_examples: []
  antipattern_examples: []
  related_principles: []
---
A Gantt chart is a bar chart on a time axis, with each row representing
a task and each bar spanning that task's start and end. Henry Gantt
formalized it for industrial scheduling; a hundred years later it's
still the default chart for any "what happens when" conversation.

**Works when**: tasks are discrete, dated, and concurrent, and the
reader needs to see both durations and ordering at a glance. A kitchen
renovation with 20 trades and a critical path through the plumbing is
a perfect Gantt use case. So is broadcast programming (shows × time
slots × channels) and agile sprint planning (stories × days × assignees,
though that's a weird Gantt variant).

**Fails when**: the project is either too small (three tasks in a
linear order — just a sentence would work) or too large (hundreds of
tasks where no reader can track which arrow points to which). At the
high end, Gantt charts need interaction: filter, zoom-to-timeframe,
expand-collapse groupings.

**The critical path**: the longest chain of dependent tasks, whose
total duration sets the project's earliest finish. Without it
highlighted, readers can't tell which slips matter (a slip on the
critical path moves the finish date; a slip on any other task is
absorbed by slack). Color the critical-path bars distinctly — many
teams use amber or red — so one glance tells readers where to worry.

**Dependency arrows**: useful for 5-15 tasks, pathological past 20.
Alternative: show dependencies on hover, or clearly number tasks and
use a separate matrix-plot for the precedence structure. Never draw
100 arrows in hope that readers will mentally filter them — they
won't.

**Milestones vs tasks**: milestones are zero-duration — deliverables,
decision points, external deadlines. Render them as diamonds or
vertical lines, not as tiny 1-pixel bars; readers shouldn't have to
pattern-match between shapes to notice "oh, that's the launch date".

**Status coloring**: planned-outline with a fill-bar underneath
showing completion (e.g., 60% shaded) is the richest encoding in a
small footprint. Red for "behind schedule", amber for "at risk",
green for "ahead" works if you separate status from the critical-path
highlight.
