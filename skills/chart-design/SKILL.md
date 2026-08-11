---
name: chart-design
description: ALWAYS use this before creating, designing, choosing, or recommending ANY chart, graph, plot, figure, or dashboard — in any library or medium (d3, Vega, matplotlib, plotly, Recharts, Observable, hand-written SVG), and whenever someone asks what chart to use or how to show some data. Use it even when another visualization or design skill is available — this one runs FIRST and decides *what* to build, then hands off. It picks the form from the reader's question against 43 documented chart forms and their when-not-to-use lists, runs the honesty checks a newsroom applies before publishing (fair comparison, denominator, counter-reading, benchmark), and names the anti-patterns for the form you land on. Skipping it means deciding the chart from habit.
---

# chart-design

Most bad charts are not ugly. They are a defensible-looking answer to a
question nobody asked, or an honest-looking answer to a question the data
can't support. Both failures happen before the first line of code, which is
why this runs first.

The order below is the whole skill. Form is decided against a documented
library, not from memory. Color is the last five percent and takes one
command.

**If a styling or design-system skill is also available**, run this one first
and that one after: this decides *what* to build — the form, the encoding, the
checks it has to survive — and that decides how it looks. Don't let a palette
be the first decision made about a chart.

**Preflight:** if `vizier --version` fails, install it — `uv tool install
datavizier` (or `pip install datavizier`). No keys, no network, nothing
proprietary: everything in this skill runs on the core install. `vizier
doctor` reports what's live. If vizier's MCP tools are available
(`…__recommend_form`, `…__get_pattern`, `…__implementation_guide` — the prefix
depends on how the server was registered), they return the same answers as the
CLI commands below; use either.

## 1. Say what the reader gets

Write one sentence before anything else:

> After reading this, the reader can **\_\_\_**.

Decide / compare / notice / rank / locate are jobs. "See the data" is not a
job — it's a request for a table. If you can't finish the sentence, ask the
user what the chart is for; do not start guessing at forms.

Then name the **headline claim**: the one factual statement the chart has to
carry. Build backward from it. A chart with no claim gets no annotation, no
sort order, and no reason to prefer one form over another.

## 2. Get the form from the library, not from habit

```bash
vizier recommend-form "<the comparison, in the reader's words>" --n-series <N>
```

`--n-series` is load-bearing — it triggers the guards that catch "this
shouldn't be a chart at all" and "this form collapses past six categories."

Read what comes back properly:

- **`when_not_to_use` on the top form** matters more than `when_to_use`. If
  your case is on that list, the recommendation is wrong for you — take the
  alternative that names your situation.
- **The alternatives are where the judgment is.** Each says *when* to switch.
  Two forms that disagree on the same data are teaching you what the data
  actually is.
- Pull one form in full when you need the detail:
  `vizier patterns show <id>` (add `--json` to parse it).

Browse by purpose when the job is fuzzy: `vizier patterns list --family Flow`
— families are Change over time, Correlation, Deviation, Distribution, Flow,
Magnitude, Part-to-whole, Ranking, Spatial.

**When not to make a chart at all.** Two numbers are a sentence. Precise
lookup is a table. A single number with no comparison is a stat line, not a
chart — and if you're building a stat tile anyway, it still needs the
comparison that makes the number mean something.

## 3. Run the honesty checks

```bash
vizier guide "<the job>" --context "<headline or caption>" --n-series <N>
```

This returns the checks a graphics desk applies before publishing. Answer
each one *in the chart or its caption* — not in your head:

- **Fair comparison** — name the benchmark that makes the value
  interpretable: prior period, peer group, target, statewide, or an explicit
  "no fair comparison available."
- **Unit and denominator** — percent *of what*, dollars *per whom*, count of
  *which* rows. Put it in the axis or the caption, near the chart.
- **Counter-reading** — the most likely *wrong* reading. Block it with an
  annotation or a caption line. Don't bury it in methodology.
- **Reader affordance** — direct labels, endpoint labels, a table fallback.
  Never let color carry the only meaning.

If a check can't be satisfied, say so in the caption. An acknowledged gap is
honest; a silent one is the defect.

## 4. Encode by strength, then annotate

- Position beats length beats angle beats area beats color. Push the most
  important comparison onto the strongest channel available.
- Sort by value, not alphabetically, unless the category order is itself
  meaningful (time, size buckets, a funnel).
- Direct labels over a legend whenever they fit — a legend is a lookup task
  you're handing the reader.
- Zero baseline is mandatory for bars and area (length encodes the value);
  not required for lines, where the story is change.
- The annotation is part of the chart, not decoration. The headline claim
  should be readable off the graphic without the surrounding prose.

Then check the form's documented traps before you build:
`vizier patterns show <id>` → **Common mistakes**. They are specific and
they are the ones people actually hit (alphabetical stacking order, middle
segments nobody can compare, clipped in-segment labels).

**Never**: dual y-axes (the correlation is an artifact of two arbitrary
scales), 3D anything, truncated bar baselines, pie charts used for
comparison or with more than about five slices, rainbow ramps for ordered
data.

## 5. Color: one command, then move on

Color is the last five percent of a good chart and the first ninety percent
of most chart advice. Resist that. Get a validated palette and go:

```bash
vizier suggest-palette 6              # categorical, colorblind-safe, validated
vizier suggest-ramp 5 --hue navy      # ordered data: one hue, light → dark
vizier validate "#e69f00,#0072b2,#009e73" --pairs all   # check one you were handed
vizier ink "#0072b2"                  # legible label color on that fill
```

Everything returned has already cleared colorblind separation, contrast, and
lightness/chroma checks — there is nothing further to eyeball. If a request
can't be satisfied honestly (a ninth categorical hue, too many ordinal
steps), vizier errors instead of returning something that fails; take the
error as the answer and change the encoding, usually by grouping categories
or switching to small multiples.

Two rules that matter more than the hues: **use ordered color for ordered
data and categorical color for categorical data**, and **never encode
anything in color alone** — pair it with position, a label, or a shape.

## 6. Check the artifact you actually built

```bash
vizier analyze chart.svg     # or .html — pulls the real palette out and checks it
```

This reads the rendered file, so it catches what the library did rather than
what you intended. Then walk the form's **Reading checklist**
(`vizier patterns show <id>`) against your own chart, answering each question
from the graphic alone. Anything you can't answer, a reader can't either.

To go further — a full critique of a rendered chart against the corpus of
critical writing — use the `chart-critique` skill.
