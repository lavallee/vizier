---
id: data-editor-lens
source: rubrics
type: rubric
title: Data editor's critical lens
tags: [editorial, journalism, parity, framing, transparency]
---

# Data editor's critical lens

A structured pre-publication audit for any data-driven story or
profile. Runs as a named pass that emits a structured artifact
before the refine step, but the content of the lens is what a senior
data editor would catch in a 15-minute read of the bundle.

This is the editorial counterpart to the chart-form critique vizier
already produces. Chart-form critique looks at *one image at a
time*. The data-editor lens looks at the *whole story-data-chart
bundle* as a piece of journalism.

## Run when

- Before publishing a data-driven explainer, profile, or news piece
- After the data + draft + charts have been assembled
- Before any reader-facing copy edit pass — the audit findings
  should shape the copy edit, not be retrofitted to it

## What to check

The eight axes a senior data editor reads for. Each item has the
question, the failure mode it's catching, and the form a fix takes.

### 1. Data-vintage parity

**Q.** Are all the data series being compared from the same time
window? Or is the story's load-bearing comparison juxtaposing
this-year data with year-old data?

**Failure mode.** Comparing fresh data (e.g. just-released test
scores) with older context data (e.g. attendance reporting that
lags by a publication cycle) and treating them as a single
"recovery story." The vintage mismatch is invisible to readers
unless explicitly disclosed.

**Fix forms.**
- Wait for parity (push publication until the slower series
  catches up).
- Reframe so the cross-vintage comparison isn't load-bearing
  (move the lagging series to a context sidebar with explicit
  date disclosure).
- Make the mismatch the story (when the gap itself is the news).

### 2. News currency in the framing

**Q.** Does the story foreground the actual news (the new data
release) or does it bury the news behind an analysis frame?

**Failure mode.** Analytical pieces written around evergreen
themes that don't make space for the time-sensitive material that
prompted the piece. Loses the news hook; the reader can't tell
why this is being published now.

**Fix forms.**
- Lead with what's new; analytical context follows.
- If the analytical frame is the right structure, name the news
  in the deck or kicker so the time-sensitivity reads.

### 3. Subgroup symmetry

**Q.** Are the rules applied to subgroup analysis the same across
all subgroups? Or are some included and some excluded by
inconsistent thresholds?

**Failure mode.** Excluding small subgroups (e.g. n<30) for
"reliability" while the dominant subgroups also have small cells
that aren't disclosed. Or excluding subgroups whose movement
contradicts the headline. Selectivity disguised as methodology.

**Fix forms.**
- Apply the n-threshold consistently across all subgroups.
- If a subgroup is excluded, name it and disclose why; show it on
  a smaller-sample appendix chart.
- Disclose the n for every subgroup on the main chart, not just
  the ones excluded.

### 4. Hidden denominators

**Q.** Are the rates being compared computed against the same
denominator? When two percentages are placed next to each other,
do they refer to populations of comparable size?

**Failure mode.** Treating a rate that excludes some students
(e.g. 8th grade math, which excludes Algebra I-takers) the same
as a rate that includes everyone in that grade. The rate
arithmetically can't move the same way the broader rate does.

**Fix forms.**
- Re-compute on a unioned denominator before publishing.
- Show both the narrow and broad rates with the difference
  explained.

### 5. Asymmetric framing of subgroups

**Q.** Does the prose use the same structure, vocabulary, and
visual treatment for each subgroup, or does the framing default
to deficit language for some groups and progress language for
others?

**Failure mode.** Per Quinn (2020), achievement-gap framing
measurably increases reader bias against the lower-scoring group.
Defaulting to "Black students lag" framing while saying "Asian
students excel" is the same pattern with the polarity flipped.

**Fix forms.**
- Lead each subgroup's trajectory with its own change, not its
  relative position to other subgroups.
- Use parallel verbs and structures across subgroups in the prose.
- The gap is a derived series; foreground the absolute trajectories.

### 6. Causal language for descriptive findings

**Q.** Does any sentence in the draft imply causation that the
data doesn't establish? (Hint: any "because," "due to," "driven
by," "caused by" verb against descriptive cross-section data.)

**Failure mode.** Descriptive findings (X went up, Y stayed flat)
get prose-styled into causal claims (X went up *because* Y stayed
flat). Reader takes the implied causation as established.

**Fix forms.**
- Restate causal sentences as descriptive ones.
- If the causal claim is load-bearing, name the additional
  reporting that would establish it (and note that it isn't done
  yet).

### 7. Cherry-picked time windows

**Q.** Why these specific years? Would a different defensible
window tell a different story?

**Failure mode.** Comparing 2019 to 2025 because that's the
biggest change available, when 2018 to 2024 is also defensible
and shows a smaller (or different-shaped) movement.

**Fix forms.**
- Default to the obvious comparison window (most-recent year vs.
  pre-pandemic baseline; 5-year span; etc.) and disclose if
  another window was considered.
- Show the longer series so the chosen comparison endpoints are
  visible in context.

### 8. Reproducibility of every number

**Q.** Can the load-bearing numbers in the prose be reproduced
from a single named query against the published data?

**Failure mode.** Numbers in the prose drift from the chart, or
from a quick check; no one can verify the prose claim against the
underlying data.

**Fix forms.**
- Cross-check every number quoted in prose against the chart
  source data before publishing.
- Note: this catches the "wrong district code propagated through
  the prose" class of bug (see SOMA notebook for a case study).

## Output

Apply the lens by producing an audit document:

- **Verdict per axis** (pass / soft-flag / hard-flag).
- **Per-axis evidence** when flagged: the exact prose, chart, or
  query that fails the check.
- **Per-flag fix proposal** (one of the fix forms above).
- **Run timestamp + which version of the bundle was audited.**

The audit is the input to the editorial revision pass. It is not
the revision itself — it's the structured brief that the revision
executes.

## Provenance

This rubric was developed during the SOMA-schools project audit
when reader feedback identified a data-vintage parity issue (test
scores from 2024-25 vs. attendance from 2023-24) and a subgroup-
symmetry issue (excluded Asian + multi-race using the same
small-N rule despite multi-race actually being chartable). The
specific axes above are the ones that would have caught the
SOMA bugs *before* publication, not after.
