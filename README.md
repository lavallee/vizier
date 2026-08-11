# vizier

**Chart judgment for people and agents.** Most bad charts aren't ugly — they're a
defensible-looking answer to a question nobody asked, or an honest-looking answer the
data can't support. Both failures happen before the first line of plotting code. vizier
moves that decision onto something documented: it picks the chart *form* from the
reader's question, runs the checks a graphics desk runs before publishing, and — with a
corpus of critical writing — judges what a finished chart got wrong.

It answers the parts of a chart that are actually *decidable*, and refuses the ones that
aren't honest. It's built to be **called by an agent or a generator**, so the tool asks
vizier for the decision instead of re-deriving it from a half-remembered rule.

## Install

The primary path is the Claude Code plugin, where vizier fires *before* a chart gets
built:

```
/plugin marketplace add lyra-forge/marketplace
/plugin install vizier@lyra-forge
```

Two skills — `chart-design` (decide a chart) and `chart-critique` (judge one) — plus
vizier's MCP server, so the same answers are available as tools. The skills drive the
`vizier` CLI, which installs separately:

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
network: form recommendation, the journalism checks, the pattern library, structural
analysis, and color all work from `pip install datavizier` alone. The 43 chart-form
patterns ship inside the package; the index builds itself on first use.

## Quickstart

```bash
# decide — give me one that's right
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

`recommend-form` returns the form that fits *with* its `when_not_to_use` list and the
alternatives that name your situation — the alternatives are where the judgment is.
`guide` returns the honesty checks for the job: the benchmark that makes a number
interpretable, percent *of what* and dollars *per whom*, the most likely wrong reading
and where you're blocking it.

Color is the last five percent, and it's handled: every palette is validated before it's
returned (colorblind ΔE via Machado-2009, WCAG contrast, OKLCH lightness/chroma), and a
request that can't be satisfied honestly errors rather than returning something that
fails. See [docs/computed-color-checks.md](docs/computed-color-checks.md).

## MCP server

`vizier mcp` serves everything above (plus the corpus query) as an MCP stdio server, so
Claude Code / Cursor / any MCP client can call it. The plugin registers it for you;
elsewhere:

```bash
claude mcp add vizier -- vizier mcp
```

Tools: `recommend_form`, `implementation_guide`, `list_patterns`, `get_pattern`,
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
— the 43 patterns, the rubrics, the FT-vocabulary parse, and the weaver principles.
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

## The vizier ↔ weaver split

vizier is the **critique + decision** companion to [`weaver`](https://github.com/lavallee/weaver),
which **renders** graphics. weaver draws the pixels; vizier decides which form and which
colors, and judges the result. The same thresholds serve both directions — see
[`PRINCIPLES.md`](PRINCIPLES.md).

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
