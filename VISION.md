# Vision — vizier

**North star:** Look first; then show. When someone opens a table, vizier
shows them what is in it — honestly, with the comparisons it made counted.
When they have something to say, it shows them how — the best form first,
drawn from their rows, with the trade-offs stated and the honest warnings
attached — and judges the result with the same knowledge it used to make it.

**North-star metric:** shown-and-used figures — tables run through `vizier
show` whose output (a drawn figure, a Datawrapper chart, a sentence or a table)
was used, with its honesty notes resolved or consciously overridden, and the
downstream correction/review burden measured.

## Strategy bets

- **Exploration is a first-class purpose.** Most looking happens before there
  is a claim. `vizier explore` draws many small, quick views of a table (a
  field sheet, missingness, relationships, breakdowns, trends, outliers) with
  exploration's own honesty attached: how many comparisons were examined, n
  beside every statistic, rankings withheld when n is too small, associations
  that rest on a handful of rows marked, no causal language. Every view hands
  off to `show`.
- **Show, don't gatekeep.** A request to see data is a good request. vizier
  answers it with ranked options it has actually drawn, and says plainly when a
  sentence, a stat tile or a table would serve better — then provides that
  too. It never answers with a bare "no".
- **Generation and critique share one DNA.** The thresholds vizier draws with
  are the thresholds it validates against, so every figure it makes survives
  its own critic. `show` runs vizier's analyzers on the SVG it just drew.
- **Compute the decidable parts.** Profiling, form ranking, color, contrast,
  ink, structure and the honesty checks stay deterministic, keyless, offline
  and explainable — safe to call from agents and generators.
- **Strong defaults, honest notes.** Taste lives in the defaults (sorted bars,
  zero baselines, direct labels, validated color) and in notes that say what a
  reader could misread and what fixes it. Where a fix is mechanical, vizier
  applies it and says so.
- **Retrieve judgment with its prior art.** Optional corpus-backed critique
  cites the practices and criticism it relies on instead of returning an
  ungrounded aesthetic opinion.

## Goals

- Answer "what is in this table?" before anyone has a claim: a contact sheet
  of honest small views, each a step away from a finished figure.
- Draw the core journalistic forms from real rows as self-contained SVG and
  HTML that open from `file://` with no network: bar (grouped, stacked), line,
  scatter, dot, strip, histogram, slope, small multiples, heatmap, stacked
  area, choropleth when outlines are supplied, and the stat tile.
- Hand off to the tools people already publish with: Datawrapper through its
  API, and a neutral spec for workbenches and other renderers.

## Non-goals

- Being a general charting library. vizier draws the forms its pattern library
  can vouch for, with its defaults; bespoke graphics and house styling belong
  to the renderer or the page.
- Automating editorial judgment, story framing, or ethical trade-offs. vizier
  states the trade-offs; people make the call.
- Shipping copyrighted critique corpora in the public package.
- Refusing. When a request can't be met exactly (more hues than can be told
  apart, more steps than a ramp holds), vizier returns the best valid answer
  and says what to change.

## Engine map

- The table profiler and form ranker turn a CSV/JSON (plus an optional
  Frictionless datapackage) into ranked, explained options.
- Pattern and rubric data define form selection, trade-offs and reading
  contracts; the ranker quotes them.
- Python renderers produce the static SVG; the page wraps it with the ranking,
  notes and data, with no scripts.
- Deterministic color, contrast, ink, SVG/HTML and structural analyzers handle
  computable quality, on vizier's own output and on anyone else's.
- The public corpus interface, optional search/critique extras, and Somm model
  routing provide evidence-backed critique.
- CLI and MCP surfaces let people, agents and generators call the same layer.
