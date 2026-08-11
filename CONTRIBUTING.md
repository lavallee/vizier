# Contributing to vizier

Thanks for your interest. A few things keep the project coherent.

## Setup

```bash
uv sync
uv run pytest -q
uv run ruff check src/ tests/
tests/install/run.sh                   # what a user's install does — see tests/install/README.md
```

Run the install test before anything that touches packaging, the corpus layout,
the MCP server, or the plugin. It's the only thing that exercises a wheel
install, and the failures it catches are invisible from a source checkout.

Opening this repo in Claude Code warns that `CLAUDE_PLUGIN_ROOT` is unset for
the `vizier` MCP server. That's expected: the repo root doubles as the plugin
root, so its `.mcp.json` is written for the plugin's environment. Ignore the
warning, or register the server yourself with
`claude mcp add vizier -- uv --directory . run vizier mcp`.

## The two halves — keep them distinct

- **Computable** (`src/vizier/analyze/`): deterministic, no LLM. Anything here must be
  correct by construction and covered by a test in `tests/`. **What vizier suggests
  must pass its own validation** — a returned palette/ramp/ink is always valid, or
  the call errors clearly.
- **Corpus-backed critique** (`src/vizier/critique/`): LLM-mediated judgment. Keep LLM
  opinion out of the computable layer — the color/contrast/form verdicts are ground
  truth, not opinion.

## Never commit third-party corpus

Only vizier's **own authored** corpus ships:
`corpus/{chart-forms,rubrics,ft-vocab,principles}`. The scraped sources (kantar,
junkcharts, cairo-blog, nightingale, …) are gitignored and rebuilt with
`vizier ingest` — they're copyrighted and must not be committed.

## Adding a chart pattern

Add `corpus/chart-forms/<id>.md` (`type: chart_pattern`) following the existing
schema (`purpose_families`, `capsule`, `when_to_use` / `when_not_to_use`,
`alternatives`, `common_mistakes`, `reading_checklist`). Then:

```bash
vizier db build --no-embed
vizier recommend-form "<the job it serves>"   # check it routes
```

## Color / thresholds

Any palette, ramp, or threshold change must pass the validator (`vizier validate` and
the color tests). Thresholds match the `dataviz` method (Machado-2009 CVD ΔE ≥ 12
target, OKLCH chroma floor, WCAG contrast) — don't drift them without a reason and a
test.

## Fetching is pluggable

The corpus fetcher (`src/vizier/ingest/_common.py`) uses httpx by default, and an
optional richer fetcher if you point `$VIZIER_FETCHER` at one. To use your own, set
`FETCHER` or add an adapter — don't hard-code a proprietary client into the ingest path.
