# vizier

**Building journalistic data visualizations — generating *and* critiquing.** vizier helps
make the graphics that carry a data story: it recommends the right chart *form* and
encoding, and — with a corpus of critical writing — judges what a finished chart got
wrong. It answers the parts of a chart that are actually *decidable*, and refuses the
ones that aren't honest.

Generation and critique live side by side on purpose — they share the same DNA. The
thresholds that let vizier *suggest* a form or palette are the thresholds it *critiques*
against, so what it proposes is what it would pass. Kept distinct, the two halves can even
be pointed at each other: a generator proposes, the critic pushes back.

- **Computable** (deterministic, no LLM, no keys) — chart-form recommendation and
  structural checks, plus colorblind-safe palette generation + validation, ordinal ramps,
  and legible ink. What vizier *suggests* is what vizier would *pass*. The color math is a
  faithful port of the `dataviz` method's validator (same thresholds, same Machado-2009
  colorblind transforms).
- **Corpus-backed critique** (optional, LLM) — retrieval-augmented judgment of an
  existing chart against a library of critique writing, with prior-art citation.

It's built to be **called by an agent or a generator** (like a charting tool) over MCP, so
the tool asks vizier for the right decision instead of re-deriving it. It's the decision +
critique companion to [`weaver`](https://github.com/lavallee/weaver), which renders the
graphics.

## Install

```bash
pip install vizier                 # the computable toolkit + pattern query + MCP server
pip install "vizier[search]"       # + semantic retrieval (find_similar); pulls onnxruntime
pip install "vizier[critique]"     # + LLM critique/eval (needs an LLM gateway; see below)
pip install "vizier[ingest]"       # + rebuild the corpus from source
```

The core has no proprietary and no heavyweight dependencies — `validate`, `suggest`,
`recommend`, `analyze`, and `ink` work from `pip install vizier` alone.

## Quickstart — the computable toolkit (no keys)

```bash
# generation — give me one that's right
vizier recommend-form "composition of a total over time" --n-series 5
vizier suggest-palette 6                 # a CVD-safe categorical palette, validated
vizier suggest-ramp 5 --hue navy         # a one-hue ordinal ramp, validated
vizier ink "#0072b2"                     # the legible text color for a fill

# critique — is this right?
vizier validate "#e69f00,#0072b2,#009e73,#56b4e9" --pairs all
vizier analyze chart.svg                 # palette + structural checks from SVG/HTML
```

Every suggestion is validated before it's returned (colorblind ΔE via Machado-2009,
WCAG contrast, OKLCH lightness/chroma). A request that can't be satisfied — a 9th
categorical hue, too many ordinal steps for a warm hue — errors clearly rather than
returning something that fails. See [docs/computed-color-checks.md](docs/computed-color-checks.md).

## MCP server

`vizier mcp` serves everything above (plus the corpus query) as an MCP stdio server, so
Claude Code / Cursor / any MCP client can call it. Register it:

```bash
claude mcp add vizier -- vizier mcp
```

Tools: `validate_palette`, `suggest_palette`, `suggest_ramp`, `ink_on`,
`analyze_artifact`, `check_contrast`, `recommend_form`, plus corpus query
(`search`, `find_similar`, `list_patterns`, `get_pattern`, `list_rubrics`, …).
Setup + troubleshooting: [docs/mcp-setup.md](docs/mcp-setup.md).

## Chart pattern library + reader

vizier ships 43 chart-form patterns (FT Visual Vocabulary families) — each with
when-to-use / when-not / alternatives / common-mistakes / reading-checklist. Browse
them or route to one:

```bash
vizier patterns list
vizier recommend-form --family Flow
```

`docs/reader/` is a self-contained static guide (open `docs/reader/index.html`, or the
published site — see below) that renders the whole library with live d3 demos, generated
from the pattern data (`vizier patterns export -o docs/reader/data.json`). It vendors its
own d3 and design tokens — no build step, no external dependencies.

## Website

The landing page and the chart-forms guide are served from GitHub Pages out of `docs/`
(`docs/index.html` + `docs/reader/`, with `.nojekyll` so the static files serve as-is).
Regenerate the guide's data whenever patterns change:

```bash
vizier patterns export -o docs/reader/data.json
```

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

What the corpus draws on and why is described in [INFLUENCES.md](INFLUENCES.md); the
per-source ingest notes are in [docs/process-notes-sources.md](docs/process-notes-sources.md).
Fetching is pluggable (`src/vizier/ingest/_common.py`): the bundled default is httpx;
point `$VIZIER_FETCHER` at a richer fetcher, or set your own `FETCHER`.

## Critique + evaluation (optional)

`vizier critique <image>` and the `vizier eval` harness use an LLM. vizier routes calls
through [`somm`](https://github.com/lavallee/somm) (an LLM gateway); provide a key in
`.env` (copy `.env.example`). The color-CVD case under `evals/` demonstrates the
measured lift from the computable findings — see `docs/computed-color-checks.md`.

## The vizier ↔ weaver split

vizier is the **critique + decision** companion to [`weaver`](https://github.com/lavallee/weaver),
which **renders** graphics. weaver draws the pixels; vizier decides which form and which
colors, and judges the result. The same thresholds serve both directions — see
[`PRINCIPLES.md`](PRINCIPLES.md).

## Development

```bash
uv sync
uv run pytest -q            # 17 tests (also runnable per-file: python tests/test_color.py)
uv run ruff check src/ tests/
```

Both run in CI on every PR and push (`.github/workflows/ci.yml`, Python 3.12–3.13).

MIT licensed. Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Release
process and versioning: [RELEASING.md](RELEASING.md); notable changes:
[CHANGELOG.md](CHANGELOG.md).
