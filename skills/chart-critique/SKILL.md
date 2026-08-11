---
name: chart-critique
description: Judge a chart that already exists. Invoke FIRST — before any other charting or visualization skill — when asked to review, critique, audit, assess, or improve a chart, graph, plot, figure, or dashboard, whether it's a source file, a screenshot, or a published graphic, and when asked whether a chart is misleading or whether it's the right chart. Checks the artifact structurally with no keys, answers the form's documented reading checklist against it, and adds corpus-backed judgment with prior-art citation when an LLM key is available.
---

# chart-critique

Critique in a useful order: does the form fit the reader's job, is the
comparison fair, what will a reader get wrong — and only then, cosmetics.
Reversing that order produces the familiar useless review that fixes the
gridlines on a chart that shouldn't exist.

**Preflight:** `vizier --version`; install with `uv tool install datavizier`
if missing. Steps 1–4 need no keys and no network.

## 1. Read the artifact before you opine

If you have the source file (SVG or HTML):

```bash
vizier analyze chart.svg --pairs all
```

That extracts the palette the chart *actually* renders — separating data
color from axis/grid/text chrome — and runs the deterministic checks. It's
evidence, not opinion, and it costs nothing.

If you only have an image, look at it and describe what's encoded on each
channel: what's on x, what's on y, what color is doing, what size is doing.
Write that down before judging anything. Half of chart critique is noticing
that a channel is carrying nothing, or carrying two things at once.

## 2. Name the form and pull its file

```bash
vizier patterns list                 # find the id
vizier patterns show <id>            # when-to-use, when-NOT, mistakes, checklist
```

The form's **`when_not_to_use`** list is the sharpest instrument here. If the
chart's situation appears on it, you have found the real problem and
everything downstream is secondary. Say which alternative the pattern names
for this case, and why.

## 3. Answer the reading checklist against the artifact

Every documented form ships a reading checklist — the questions a reader must
be able to answer from the graphic. Work through it out loud, answering from
the chart alone.

The verdict on each is one of three, and "can't tell" is a finding, not a
gap in your effort:

- **answered** — the chart carries it.
- **can't tell from the artifact** — a reader can't either. This is the
  finding.
- **answered wrongly** — the chart implies something the data doesn't
  support. This is the serious one; lead with it.

## 4. Check the fairness of the comparison

Independent of form, these are what turn a competent chart into a misleading
one:

- Denominator and unit stated near the chart, not in distant methodology.
- Baseline: is a truncated axis inflating a difference on a length encoding?
- Benchmark: is the comparison to a peer, a prior period, or nothing at all?
- Time basis: nominal vs inflation-adjusted, seasonal effects, uneven bins.
- Aggregation: does the total conceal a reversal in the parts?
- The counter-reading: the most likely wrong conclusion. Is it blocked, or
  is it the first thing a skimmer takes away?

Then the form's **Common mistakes** list, which is where the cosmetic and
configuration defects belong — sort order, segment count, label clipping,
color carrying meaning alone. These go *last* in the writeup even when
they're the easiest to fix.

## 5. Corpus-backed critique (optional, needs a key)

For a rendered chart image, vizier can retrieve the relevant pattern
checklist plus prior art from a corpus of award commentary, structural
critique, and practitioner walkthroughs, and synthesize a review with
citation:

```bash
vizier critique chart.png --context "<the headline that ran with it>"
vizier critique chart.png --palette "#e69f00,#0072b2,#009e73"   # folds in the color checks
```

This needs `pip install 'datavizier[critique]'` and one provider key in a
`.env` file. `vizier doctor` says exactly what's missing and how to supply
it. If it isn't configured, don't stall — steps 1–4 are the substance, and
say plainly that the corpus pass was skipped.

## Writing the review

Order findings by what would change the chart most, not by how easy they are
to fix:

1. **Form fit** — right form for the reader's job, or which one instead.
2. **Honesty** — fair comparison, denominator, baseline, counter-reading.
3. **Readability** — what a reader can't answer from the graphic.
4. **Cosmetics** — sort order, labels, chrome, color.

Be specific and be fair: name what the chart does well, cite the documented
rule behind each criticism rather than asserting taste, and give each finding
a concrete fix. "Use a grouped bar so the middle segment shares a baseline"
is a review. "Feels cluttered" is not.
