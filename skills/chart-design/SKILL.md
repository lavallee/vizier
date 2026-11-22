---
name: chart-design
description: ALWAYS use this before creating, designing, choosing, or recommending ANY chart, graph, plot, figure, or dashboard — in any library or medium (d3, Vega, matplotlib, plotly, Recharts, Observable, Datawrapper, hand-written SVG), and whenever someone asks to see their data, what chart to use, or how to show a table. Use it even when another visualization or design skill is available — this one runs FIRST. It shows how to visualize the data — `vizier show` ranks the ways to show a table against 43 documented chart forms, draws the best ones from the real rows with titles, units, source and honesty notes, and offers a sentence or table when that serves better — then hands off. Skipping it means deciding the chart from habit.
---

# chart-design

Someone asked to see their data. Show them how: the best form first, drawn
from their rows, with the trade-offs stated and the honest warnings attached.
When a sentence or a table would serve the reader better, say so and provide
it — beside the chart, not instead of one you could draw. Never answer a
request to see data with a refusal.

The taste is real and it stays: forms come from a documented library, not
from habit; bars start at zero; color is the last five percent. It shows up
as strong defaults and as notes with fixes, not as gatekeeping.

**If a styling or design-system skill is also available**, run this one first
and that one after: this decides *what* to show — the form, the encoding, the
checks it has to survive — and that decides how it looks.

**Preflight:** if `vizier --version` fails, install it — `uv tool install
datavizier` (or `pip install datavizier`). No keys, no network, nothing
proprietary: everything in this skill runs on the core install. `vizier
doctor` reports what's live. If vizier's MCP tools are available
(`…__show`, `…__recommend_form`, `…__get_pattern`, `…__implementation_guide`
— the prefix depends on how the server was registered), they return the same
answers as the CLI commands below; use either.

## 1. If there's a table, start with `vizier show`

```bash
vizier show data.csv --for "<the claim or question the figure serves>"
```

It profiles the columns (types, units, geography, missing and suppressed
values — a `datapackage.json` beside the file is read for titles, units and
missing-value codes), ranks the ways to show them, and writes a folder with
an offline `index.html` and one `.svg` per drawn option. Read the ranking,
not just the winner:

- **Each option says what it shows well, what it hides, and the mistakes most
  often made with it** — quoted from the pattern library.
- **A sentence, stat tile or table can rank first.** Two numbers usually read
  best as a sentence; vizier writes it. A chart is still drawn beside it so
  the person can choose.
- **The honesty notes travel with the figure.** Each says what a reader could
  misread and the fix; `applied` means vizier already did it (bars from zero,
  a tail folded into "Other", gaps instead of zeros, separate figures instead
  of a second y-axis).

Steer it when the defaults guess wrong: `--x`, `--y`, `--series`, `--label`;
`--caveats caveats.json` puts dataset caveats in the figure notes;
`--geometry areas.geojson --geo-key fips` draws a map; `--annotate
"Newark=Highest in the state"` fills an annotation slot. `--format spec`
prints a neutral JSON (form, roles, colors, words, notes) to hand to another
renderer; `--format datawrapper` builds the chart in Datawrapper (a dry run
until `DATAWRAPPER_API_TOKEN` is set).

## 2. Say what the reader gets

Whether or not `show` drew it, write one sentence:

> After reading this, the reader can **\_\_\_**.

Decide / compare / notice / rank / locate / look up their own row — all good
jobs. "See the data" is a fine starting point too: it usually means *look up
my row* (a table, which `show` provides) or *get the overall shape* (a
distribution or trend). If the job is unclear, ask what the figure is for,
and meanwhile show the top options so the person has something to react to.

Then name the **headline claim**: the one factual statement the figure has to
carry. Pass it as `--for`; it becomes the title. Build backward from it — the
claim decides the annotation and the sort order.

## 3. Check the form against the library

```bash
vizier recommend-form "<the comparison, in the reader's words>" --n-series <N>
vizier patterns show <id>        # add --json to parse it
```

`--n-series` adds the notes on when a stat tile or a table should sit beside
the chart and when a form collapses past six categories.

- **`when_not_to_use` on the top form** matters more than `when_to_use`. If
  your case is on that list, take the alternative that names your situation.
- **The alternatives are where the judgment is.** Each says *when* to switch.
  Two forms that disagree on the same data are teaching you what the data is.

Browse by purpose when the job is fuzzy: `vizier patterns list --family Flow`
— families are Change over time, Correlation, Deviation, Distribution, Flow,
Magnitude, Part-to-whole, Ranking, Spatial.

## 4. Run the journalism checks

```bash
vizier guide "<the job>" --context "<headline or caption>" --n-series <N>
```

Answer each check *in the figure or its caption*:

- **Fair comparison** — the benchmark that makes the value interpretable:
  prior period, peer group, target, statewide, or an explicit "no fair
  comparison available."
- **Unit and denominator** — percent *of what*, dollars *per whom*, count of
  *which* rows, near the chart.
- **Counter-reading** — the most likely wrong reading, blocked with an
  annotation or a caption line.
- **Reader affordance** — direct labels, endpoint labels, a table fallback.
  Never let color carry the only meaning.

If a check can't be satisfied, say so in the caption. An acknowledged gap is
honest; a silent one is the defect.

## 5. Encode by strength, then annotate

- Position beats length beats angle beats area beats color. Put the most
  important comparison on the strongest channel available.
- Sort by value unless the order itself means something (time, size buckets,
  a funnel).
- Direct labels over a legend whenever they fit.
- Zero baseline for bars and areas (length encodes the value); lines may start
  elsewhere if the axis says so.
- The annotation is part of the figure: the headline claim should be readable
  off the graphic without the surrounding prose.

Avoid dual y-axes (two arbitrary scales invent a relationship — show two
panels), 3D, truncated bar baselines, pies for comparison or past about five
slices, and rainbow ramps for ordered data. The form's **Common mistakes**
(`vizier patterns show <id>`) list the traps people actually hit.

## 6. Color: one command, then move on

```bash
vizier suggest-palette 6              # categorical, colorblind-safe, validated
vizier suggest-ramp 5 --hue navy      # ordered data: one hue, light → dark
vizier validate "#e69f00,#0072b2,#009e73" --pairs all   # check one you were handed
vizier ink "#0072b2"                  # legible label color on that fill
```

Everything returned has already cleared colorblind separation, contrast, and
lightness/chroma checks. If a request can't be met exactly (a ninth
categorical hue, too many ordinal steps), vizier returns the best valid answer
and what to change — usually grouping categories into "Other", small
multiples, or direct labels. `show` applies that fallback itself.

Use ordered color for ordered data and categorical color for categorical
data, and never encode anything in color alone.

## 7. Check the artifact you actually built

`show` already runs this on what it draws. For a figure made elsewhere:

```bash
vizier analyze chart.svg     # or .html — pulls the real palette out and checks it
```

Then walk the form's **Reading checklist** (`vizier patterns show <id>`)
against the figure, answering each question from the graphic alone. Anything
you can't answer, a reader can't either.

To go further — a full critique of a rendered chart against the corpus of
critical writing — use the `chart-critique` skill.
