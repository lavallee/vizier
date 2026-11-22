# vizier

**Look first; then show.** `vizier explore` answers "what is in this table?" before
anyone has a claim — a contact sheet of small, honest views. `vizier show` answers "how
do I show this finding?".

**Show people how to visualize their data — and judge the result.** Hand vizier a table
and, if you have one, the claim or question the figure should serve. It profiles the
columns, ranks the ways to show them, and draws the best few from your actual rows as
self-contained SVG and HTML: the form that fits first, with what each option shows well,
what it hides, and the mistakes people most often make with it. When a sentence, a stat
tile or a table would serve the reader better, vizier says so *and writes it* — beside the
charts, never instead of a chart it could draw.

The taste is in the defaults and the notes: sorted bars on a zero baseline, direct labels,
validated colorblind-safe color, gaps (never zeros) for suppressed values, and honesty
notes for the things a reader could misread — each with its fix, applied where the fix is
mechanical. The same knowledge runs the other way as critique: vizier checks the SVG it
just drew, and anyone else's chart, against its pattern library and color math.

It's built to be **called by a person, an agent or a generator**, works with no model and
no network, and hands off to Datawrapper or to any renderer through a neutral spec.

## Install

The primary path is the agent plugin, where vizier fires *before* a chart gets
built. In Claude Code:

```
/plugin marketplace add lyra-forge/marketplace
/plugin install vizier@lyra-forge
```

In Codex:

```bash
codex plugin marketplace add lyra-forge/marketplace
codex plugin add vizier@lyra-forge
```

Two skills — `chart-design` (show data / design a chart) and `chart-critique` (judge one) — plus
vizier's MCP server, so the same answers are available as tools. The skills drive the
`vizier` CLI, which installs separately. Start a new harness session after installing:

```bash
uv tool install datavizier        # or: pip install datavizier
vizier doctor                     # what's live, what's missing, and how to fix it
```

The PyPI distribution is `datavizier` (the bare name was taken); the import package and
command are both `vizier` — `import vizier`, `vizier …`. Python 3.12+.

```bash
pip install datavizier                 # the toolkit, pattern library, and MCP server
pip install "datavizier[search]"       # + semantic retrieval (find_similar)
pip install "datavizier[critique]"     # + LLM critique/eval (needs an LLM gateway; see below)
pip install "datavizier[ingest]"       # + rebuild the corpus from source
```

The core has no proprietary and no heavyweight dependencies, and needs no key and no
network: `vizier show`, form recommendation, the journalism checks, the pattern library,
structural analysis, and color all work from `pip install datavizier` alone. The 43 chart-form
patterns ship inside the package; the index builds itself on first use.

## Quickstart

```bash
# explore — what is in this table? (before there is a claim)
vizier explore data.csv                                       # contact sheet: index.html + SVGs + explore.json
vizier explore data.csv --focus rent --where "city=Newark"    # one field at the centre, a subgroup
vizier explore data.csv --view rel-income--rent --out big/    # redraw one view, larger

# show — the front door
vizier show data.csv --for "Rents rose fastest downtown"     # ranked, drawn, annotated
vizier show data.csv --x year --y rent --series district      # say which columns play which role
vizier show data.csv --caveats caveats.json --geometry areas.geojson --geo-key fips
vizier show data.csv --format spec                            # neutral JSON for other tools
vizier show data.csv --format datawrapper                     # dry run without a token

# decide by hand — the same knowledge, one question at a time
vizier recommend-form "how a budget splits, across five districts" --n-series 5
vizier patterns show stacked-bar         # when to use, when NOT, mistakes, checklist
vizier guide "per-pupil spending vs the state average" --context "<headline>"

# critique — is this one right?
vizier analyze chart.svg                 # structural + color checks from the artifact
vizier critique chart.png                # corpus-backed review (optional extra + key)

# color, once
vizier suggest-palette 6                 # a CVD-safe categorical palette, validated
vizier suggest-ramp 5 --hue navy         # a one-hue ordinal ramp, validated
vizier validate "#e69f00,#0072b2,#009e73" --pairs all
vizier ink "#0072b2"                     # the legible text color for a fill
```

### `vizier explore`

`vizier explore TABLE` writes `index.html` — one static page readable as a contact sheet —
plus one SVG per view and `explore.json` (`vizier/explore/v1`). In order:

1. **Field sheet** — one compact distribution per field (histogram, top values, timeline),
   with n, missing and suppressed counts, range, median, and oddities called out: a spike at
   a round number, a long tail, a dominant value, impossible values, likely missing-value codes.
2. **Missingness** — which fields are missing together, and in which groups.
3. **Relationships** — pairs of measures ranked by Spearman's ρ, each a small scatter with a
   leverage check (ρ recomputed without the rows that drive it, which are ringed); the
   strongest few also conditioned on the likeliest confounder (partial rank correlation),
   with panels for each third of it side by side on shared scales.
4. **Breakdowns** — each measure by each low-cardinality dimension as strips with medians,
   ranked by how much groups differ relative to the spread within them (ε²).
5. **Trends** when there is a time field. 6. **Outliers** — rows furthest from the pattern.

The notes say how many comparisons were examined and that a pattern found by looking at
many is a lead to test, not a finding; n sits beside every statistic; groups under 5 rows
and pairs under 10 are shown but not ranked. `--focus COL` centres one field; `--by COL`
re-runs the sheet per group; `--where "COL=VALUE"` subsets. Every view carries the
`show_args` that hand it to `vizier show`.

### `vizier show`

`vizier show TABLE` writes a folder (default `./vizier-show-<name>/`) with `index.html` —
the best option first, the others after it, the full ranking, the honesty notes, the
column profile and the data — plus one `.svg` per drawn chart and a `spec.json`. The page
has no scripts and fetches nothing; it opens from `file://`.

- **Profiling** reads CSV or JSON (nested records flatten), and a Frictionless
  `datapackage.json` beside the table for titles, units, descriptions and
  `missingValues`. Columns are typed (number, date with granularity, category, identifier,
  geography — FIPS, ZIP/ZCTA, ISO codes, state names, lat/lon) and given roles. A
  `<field>__state` column marks values as suppressed or not collected: they are drawn as
  hatched gaps or labelled in place, and counted in the notes — never drawn as zero.
- **Ranking** covers bar (grouped, stacked, top-N), line, slope, scatter, dot, strip,
  histogram, small multiples, heatmap, stacked area, choropleth (when outlines are
  supplied, as GeoJSON or an SVG path column — otherwise it says what's needed), and the
  sentence, stat tile and table. `--for` routes by the words in your claim; a claim
  becomes the title, a question becomes the subtitle.
- **Words on the figure**: title, subtitle, axis labels with units, source line (from the
  datapackage or `--source`), `--annotate KEY=TEXT` slots, and `--caveats FILE` (a JSON
  list of `{effect, misuse, instead}`) in the notes.
- **Honesty notes**: axis not at zero, dual axis (never drawn — each measure gets its own
  figure), too many series (tail folded to gray "Other"), small sample, a rate without a
  denominator, suppressed and missing values, correlation-not-cause on scatters,
  area-weight on maps. Each says what could be misread and the fix.
- **Checks**: every drawn SVG goes back through `vizier analyze`'s color and structure
  checks, and the result is printed with it.
- **Datawrapper**: `--format datawrapper` builds the chosen form through Datawrapper's API
  when `DATAWRAPPER_API_TOKEN` is set (create, upload, unpublished draft by default;
  `--publish` to publish) and prints the edit URL. Without a token it prints the exact
  requests it would send. Forms map to Datawrapper types as follows; strip plots, maps,
  stat tiles, sentences and multiple scatters have no automatic equivalent and say so.

  | vizier form | Datawrapper type |
  |---|---|
  | bar chart (sorted / top-N / median) | `d3-bars` |
  | grouped bars | `d3-bars-grouped` |
  | columns over time, histogram (pre-binned) | `column-chart` |
  | stacked bar | `d3-bars-stacked` |
  | line chart | `d3-lines` |
  | stacked area | `d3-area` |
  | scatterplot | `d3-scatter-plot` |
  | dot plot | `d3-dot-plot` |
  | slope chart | `d3-arrow-plot` |
  | small multiples of lines / bars | `multiple-lines` / `multiple-columns` |
  | heatmap, table | `tables` |

`recommend-form` returns the form that fits *with* its `when_not_to_use` list and the
alternatives that name your situation. `guide` returns the honesty checks for the job: the
benchmark that makes a number interpretable, percent *of what* and dollars *per whom*, the
most likely wrong reading and where you're blocking it.

Color is the last five percent, and it's handled: every palette is validated before it's
returned (colorblind ΔE via Machado-2009, WCAG contrast, OKLCH lightness/chroma). A request
that can't be met exactly — a ninth categorical hue, more steps than a ramp holds — returns
the best valid answer with `met: false` and what to change (fold the tail into "Other",
small multiples, direct labels). See [docs/computed-color-checks.md](docs/computed-color-checks.md).

## MCP server

`vizier mcp` serves everything above (plus the corpus query) as an MCP stdio server, so
Codex, Claude Code, Cursor, and other MCP clients can call it. Either marketplace
plugin registers it for you;
elsewhere:

```bash
claude mcp add vizier -- vizier mcp
```

Tools: `explore`, `show`, `recommend_form`, `implementation_guide`, `list_patterns`, `get_pattern`,
`analyze_artifact`, `validate_palette`, `suggest_palette`, `suggest_ramp`, `ink_on`,
`check_contrast`, plus corpus query (`search`, `find_similar`, `list_rubrics`, …).
Setup + troubleshooting: [docs/mcp-setup.md](docs/mcp-setup.md).

## Chart pattern library + reader

vizier ships 43 chart-form patterns (FT Visual Vocabulary families) — each with
when-to-use / when-not / alternatives / common-mistakes / reading-checklist. Browse them
or route to one:

```bash
vizier patterns list --family Flow
vizier patterns show sankey
```

`docs/reader/` is a self-contained static guide (open `docs/reader/index.html`, or the
published site) that renders the whole library with live d3 demos, generated from the
pattern data (`vizier patterns export -o docs/reader/data.json`). It vendors its own d3
and design tokens — no build step, no external dependencies.

## Corpus (rebuild your own)

vizier's critique is sharpened by a corpus of data-viz writing (award commentary,
critique blogs, practitioner walkthroughs). **Only vizier's own authored content ships**
— the 43 patterns, the rubrics, the FT-vocabulary parse, and the house principles.
The third-party sources are **not redistributed** (they're copyrighted); rebuild them
locally:

```bash
vizier ingest all        # fetch + parse into corpus/<source>/
vizier db build --embed  # index for search + retrieval
```

Set `VIZIER_CORPUS_ROOT=/absolute/path/to/corpus-root` before running `vizier ingest` or
`vizier db build` to write/read a corpus outside the installed package tree. This is how
the private corpus artifact is rebuilt without copying private source material into the
public package. `VIZIER_DB_PATH` overrides where the index itself lives (default: beside
the corpus in a checkout, or a per-user cache directory for a packaged install).

What the corpus draws on and why is described in [INFLUENCES.md](INFLUENCES.md); the
per-source ingest notes are in [docs/process-notes-sources.md](docs/process-notes-sources.md).
Fetching is pluggable (`src/vizier/ingest/_common.py`): the bundled default is httpx;
point `$VIZIER_FETCHER` at a richer fetcher, or set your own `FETCHER`.

If you keep a private or local corpus DB with the same schema, keep it out of the
distributed package and point vizier at it at runtime — this is the plug point for
proprietary prior art, so nothing private ever ships in the public package:

```bash
VIZIER_PRIVATE_DB=/absolute/path/to/private/.vizier.db vizier db search "reader decision"
VIZIER_EXTENSION_DBS=/absolute/path/to/private/.vizier.db vizier db search "reader decision"
VIZIER_EXTENSION_DBS="/path/one.db:/path/two.db" vizier mcp
```

Extension DBs are opened read-only and merged into the read-side corpus APIs:
`search`, `find_similar`, `lookup`, `list_sources`, `list_principles`,
`list_rubrics`, `list_patterns`, `get_pattern`, and `stats`.
`VIZIER_EXTRA_DB_PATHS` is accepted as an alias for the same path-list. As a
convenience, vizier also auto-discovers an extension DB in a sibling
`vizier-private/corpus/vizier-private.db`; set `VIZIER_AUTO_PRIVATE=0` to disable
that and run against the public corpus only.

## Critique + evaluation (optional)

`vizier critique <image>` and the `vizier eval` harness use an LLM. vizier routes calls
through [`somm`](https://github.com/lavallee/somm) (an LLM gateway); provide a key in
`.env` (copy `.env.example`) — vizier reads `.env` from the working directory upward.
`vizier doctor` names exactly what's missing. The color-CVD case under `evals/`
demonstrates the measured lift from the computable findings — see
`docs/computed-color-checks.md`.

## vizier & artoo

vizier shows the data and judges the chart. [`artoo`](https://github.com/lavallee/artoo)
builds and ships the page it lives on — a self-contained HTML mini-site that carries
the research behind the presentation, with provenance, a private-file firewall, and
deployment (`uv tool install artoo-artifacts`).

They meet at the artifact: artoo owns packaging and publication; vizier owns the figure
— drawing it with `show`, or judging one drawn elsewhere. This repo's own chart-forms
guide is an artoo artifact — see [`docs/reader/artifact.toml`](docs/reader/artifact.toml).

More generally, vizier is built to be *asked*: any renderer or generator can take
`vizier show --format spec` (the form, field roles, colors, words and notes) and draw it
its own way, or call the primitives for form and color, and the same thresholds serve
both directions. See [`PRINCIPLES.md`](PRINCIPLES.md).

### Why the figures are drawn in Python, not d3

The static SVG is the deliverable that gets embedded and critiqued, so it has to exist
without a browser. vizier's renderers generate it directly in Python — deterministic,
offline, testable, and no 280 KB script inside every figure; hover detail rides on native
SVG `<title>` elements. The layouts follow the hand-written d3 demos in the chart-forms
guide (`docs/reader/live-examples.js`), which still vendor a pinned d3 for that guide.

## Development

```bash
uv sync
uv run pytest -q            # also runnable per-file: python tests/test_color.py
uv run ruff check src/ tests/
tests/install/run.sh        # what a *user's* install does — see tests/install/README.md
```

All three run in CI on every PR and push (`.github/workflows/ci.yml`, Python 3.12–3.13).
The install test is the one that catches what a source checkout hides: whether the
corpus travelled in the wheel, whether the MCP server starts, whether the plugin
installs, and whether the optional paths explain themselves when they can't run.

MIT licensed. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Release
process and versioning: [RELEASING.md](RELEASING.md); notable changes:
[CHANGELOG.md](CHANGELOG.md).
