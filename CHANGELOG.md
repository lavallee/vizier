# Changelog

All notable changes to vizier are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and vizier adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). See
[RELEASING.md](RELEASING.md) for the release process.

## [0.4.0] — 2026-11-22

### Changed — the stance
- **vizier now shows people how to visualize their data, instead of deciding
  whether they should.** A request to see data is treated as a good request:
  vizier ranks the ways to show it, draws the best ones, states the
  trade-offs, and — when a sentence, a stat tile or a table would serve the
  reader better — says so *and provides it*, beside any chart it can draw. It
  no longer answers with a refusal. Rendering is now a goal; being a general
  charting library is the non-goal. `VISION.md`, `PRINCIPLES.md`, the README,
  the `chart-design` skill, the plugin manifests and the roster are rewritten
  to match; the taste (strong defaults, honest warnings) stays.
- Derisive wording softened where it was tone rather than substance: the
  skill's "'See the data' is not a job — it's a request for a table", the
  gate's "Be strict — the prose alone is often enough", "Is it even a chart?"
  in the dataviz-method rubric, "one lonely bar" in the bar-chart pattern,
  and "Essays without a question are decoration" in the Pudding critique lens.

### Added
- **`vizier show <table.csv|.json>`** — the new front door, also an MCP tool
  (`show`) and a library call (`vizier.show.show`). Deterministic, no model,
  no network:
  - profiles the table (types, date granularity, cardinality, geography hints
    — FIPS, ZIP/ZCTA, ISO codes, state names, lat/lon — identifiers, ranges,
    missingness), reading a Frictionless `datapackage.json` beside it for
    titles, units, descriptions and `missingValues`, and `<field>__state`
    columns that mark values suppressed or not collected;
  - ranks forms from the pattern corpus plus sentence / stat tile / table,
    each with what it shows well, what it hides and its common mistakes;
  - draws the top options from the real rows as self-contained SVG and an
    offline HTML page (no scripts, no network): bar (grouped, stacked, top-N,
    median), line (gaps for missing), stacked area, scatter, dot, strip,
    histogram, slope, small multiples, heatmap, choropleth (GeoJSON or an SVG
    path column; otherwise it says what's needed) and stat tile. Suppressed
    and missing values are drawn as gaps or marked — never as zero;
  - puts the words on the figure: a claim from `--for` becomes the title (a
    question becomes the subtitle), axis labels carry units, a source line,
    `--annotate KEY=TEXT` slots, and `--caveats FILE` notes;
  - attaches honesty notes — axis not at zero, dual axis (never drawn), too
    many series, small sample, rate without a denominator, suppressed and
    missing values, correlation-not-cause, area weight on maps — each with
    what could be misread and the fix, applied where mechanical;
  - runs vizier's own `analyze` color and structure checks on every SVG it
    draws and reports the result;
  - `--format datawrapper` builds the chart through Datawrapper's v3 API when
    `DATAWRAPPER_API_TOKEN` is set (unpublished draft by default, `--publish`
    to publish), and prints the exact requests otherwise. Tested against a
    fake server only;
  - `--format spec` prints a neutral `vizier/show-spec/v1` JSON (chosen form,
    field roles, colors, words, notes, alternatives) for other tools.
- `python -m vizier.gate <bundle>` now actually runs (it was documented but
  `gate.py` had no entry point), and exits 1 when a decision fails.

### Changed — behaviour
- **Palette and ramp requests that can't be met no longer error.**
  `suggest_palette(n)` past the validated ceiling returns the largest palette
  that passes, with `met: false`, `requested`, and `advice` (fold the tail
  into "Other", small multiples, direct labels); a theme with no variant for
  the mode falls back to the default theme and says so. `suggest_ramp` returns
  the longest ramp the hue holds, with `met: false` and `advice`. Returned
  colors are still always valid. Malformed requests (n < 1, an unknown theme
  or hue name) still raise. The CLI prints the advice on stderr and exits 0;
  the MCP `suggest_palette` accepts `n` up to 64.
- **Gate output shape (`vizier/gate-decision/v2`).** `Decision` gains
  `status` (`ok` / `no_candidates` / `error`), `error`, `raw_response` and an
  `ok` flag; each `ChartVerdict` gains `improve` (kept: how to make it
  better), `instead` (dropped: `{form, why, how}` — what to show in its
  place) and `instead_source` (`model` or `default`). A model reply that
  can't be parsed is now `status: "error"` with `needs_charts: null` — it
  used to be reported as `needs_charts: false`, indistinguishable from a real
  "no charts". Existing field names are unchanged. The prompt now asks for an
  alternative for every dropped candidate and an improvement for every kept
  one. `somm` is imported only when the gate makes a call.
- `recommend_form` notes now offer the stat tile or table alongside the chart
  forms rather than as "not a chart"; "distributed" now routes to the
  Distribution family.

## [0.3.1] — 2026-08-11

### Fixed
- **An upgraded install kept serving the corpus of the version before it.** The
  index is a cache, and for a packaged install it lives in
  `~/.cache/vizier/corpus.db` — which outlives the package that filled it. The
  auto-build only ran when that index was *empty*, so upgrading to 0.3.0 left
  the renamed `weaver/*` rows in place, answering `list_principles` and
  `search` alongside the new `principles/*` ones. `vizier doctor` on a
  freshly-upgraded install showed the source that no longer exists.

  The index now records which vizier built it, and a read refreshes it whenever
  that differs from the running version. The rebuild already pruned rows whose
  files are gone; nothing was ever reaching it.

## [0.3.0] — 2026-08-11

### Changed
- **The `weaver` corpus source is now `principles`.** vizier's 41 house
  principles kept the name of the tool they were first written for; that tool
  is deprecated and its repo is private, so the public package, the site, and
  every `list_principles` / `lookup` response were naming something nobody
  outside could see — and the two public links to it 404'd.

  **Breaking for anyone addressing items by key:** `weaver/principle-x` is now
  `principles/principle-x`, `source="weaver"` filters become
  `source="principles"`, and the ingest module is `vizier.ingest.principles`.
  The principle bodies themselves are unchanged.

- **The companion project on the site and in the README is now
  [artoo](https://github.com/lavallee/artoo)**, which is public and current:
  artoo builds and ships the artifact — a self-contained HTML mini-site
  carrying the research behind the presentation — and vizier decides and judges
  the chart on it. This repo's own chart-forms guide is an artoo artifact.
  Where the old text described a renderer specifically, it now describes *any*
  renderer, which is what vizier actually supports.

- Eval ground-truth notes moved behind `$VIZIER_EVAL_NOTES_ROOT`
  (`ground_truth_source: house-notes`) instead of a hardcoded sibling repo, and
  `vizier ingest principles` reads `$VIZIER_PRINCIPLES_ROOT`. Neither ships;
  the already-ingested items are committed under `corpus/principles/`.

### Added
- `vizier patterns export` now warns when example links fail to resolve. The
  guide's example titles and URLs are transcluded from the *third-party* corpus,
  which isn't redistributed — so exporting from a machine that hasn't run
  `vizier ingest` silently stripped 112 of 117 links and still reported success.

## [0.2.1] — 2026-08-11

### Fixed
- **Upgrading from 0.1.0 left vizier reading an empty corpus.** 0.1.0 created
  an empty `corpus/` directory next to site-packages as a side effect of
  opening its index; that directory survives an upgrade, and 0.2.0's
  source-checkout detection accepted any directory that merely *existed*. An
  upgraded install therefore served nothing while the packaged corpus sat
  unused a directory away. Detection now asks whether the directory actually
  holds corpus items. An explicit `VIZIER_CORPUS_ROOT` is still honored even
  when empty, so `vizier ingest` can fill a fresh one.

  Fresh installs of 0.2.0 were unaffected; anyone who had run 0.1.0 was not.
  The install test now simulates the leftover directory.

## [0.2.0] — 2026-08-11

Ships vizier as a Claude Code plugin, and fixes the three defects that made a
plain `pip install datavizier` much less useful than the source checkout.

### Added
- **Claude Code plugin** (`.claude-plugin/`, `skills/`, `.mcp.json`). Two skills
  — `chart-design`, which fires before any chart code gets written and decides
  the form from the reader's question, and `chart-critique`, which judges a
  chart that already exists — plus vizier's MCP server, bundled and launched by
  `bin/vizier-mcp` (uses an installed `vizier`, falls back to `uvx`, and
  explains itself if neither is available). Install with
  `/plugin install vizier@lyra-forge`.
- **`vizier doctor`** — reports the corpus index, which optional extras are
  installed, which provider keys are visible, and what to run to fix each gap.
  `--json` for scripts; exits non-zero only when something is actually broken.
- **`vizier patterns show <id>`** — one chart form in full (when to use, when
  not, alternatives, common mistakes, reading checklist) at the CLI, matching
  what the `get_pattern` MCP tool already returned.
- **Install tests** (`tests/install/run.sh`) — provisions a sandboxed wheel
  install and asserts what a source checkout can't: the corpus travels in the
  wheel, the index self-builds, the MCP server completes a handshake, the plugin
  installs from a marketplace, and the optional paths explain themselves. Runs
  in CI as its own job.

### Fixed
- **The authored corpus now ships in the wheel.** It never had, so every
  `recommend-form`, `guide`, and `patterns` call on a `pip install` silently
  returned nothing — the corpus root resolved to a path outside site-packages.
  The 43 patterns, rubrics, FT-vocabulary parse, and house principles are
  packaged under `vizier/corpus/`; third-party sources remain unredistributed.
- **The index builds itself on first use**, into a per-user cache directory when
  the corpus is the packaged one (site-packages is often read-only, and is never
  the right home for user state). `VIZIER_DB_PATH` overrides it.
- **`vizier mcp` works on current MCP SDKs.** SDK 2.0 renamed
  `mcp.server.fastmcp.FastMCP` to `mcp.server.mcpserver.MCPServer`; the server
  now imports either, so it no longer dies on any install that didn't have the
  locked SDK version.
- **The critique path explains itself instead of tracebacking.** A missing
  `[critique]` extra, a missing provider key, a missing vision key, and bad
  image input are now messages naming the command that fixes them (exit 2).
- **`.env` is read from the working directory upward**, not from a repo-relative
  path that doesn't exist in an installed package.

### Changed
- Site and README lead with the plugin, and are rebalanced around the decision
  that actually matters — which form answers the reader's question, and whether
  the comparison is fair. Color is presented as what it is: the last five
  percent, handled in one command.
- Fixed a button-label contrast bug on the site: a bare `a:visited` rule
  outranked `.btn` on specificity, repainting button text in the accent color it
  sat on (1.00:1) once the link had been visited.

## [0.1.0] — 2026-07-11

First public release. Published to PyPI as **`datavizier`** (the bare `vizier`
name was already taken); the import package and CLI are both `vizier`.

### Added
- **Computable toolkit** (deterministic, no LLM, no keys): `validate`,
  `suggest-palette`, `suggest-ramp`, `ink`, `analyze`, and `recommend-form`.
  Every suggestion is validated before it's returned; unsatisfiable requests
  error rather than returning something that fails. Color math is a faithful
  port of the `dataviz` method's validator (Machado-2009 CVD transforms, OKLCH
  lightness/chroma, WCAG contrast).
- **Chart-pattern library**: 43 chart-form patterns across the nine FT Visual
  Vocabulary families, each with when-to-use / when-not / alternatives /
  common-mistakes / reading-checklist, queryable via BM25.
- **Corpus-backed critique** (optional `[critique]` extra): retrieval-augmented
  judgment of a chart against a corpus of critical writing, routed through
  `somm`.
- **MCP server** (`vizier mcp`): 16 tools exposing the toolkit and corpus query.
- **Chart-forms guide** (`docs/reader/`): a self-contained static reader
  rendering the whole pattern library with live d3 demos — no build step, its
  own vendored d3 and design tokens.
- **GitHub Pages site** (`docs/`): landing page leading with the journalistic
  generate-and-critique story, plus the guide.
- `INFLUENCES.md` describing the families of source vizier emulates and the
  philosophy of distilling broad expert taste into a determination.
- Minimal CI (`.github/workflows/ci.yml`): `ruff` + `pytest` on Python
  3.12–3.13; `RELEASING.md` release checklist.

### Changed
- Framing now leads with **building journalistic data visualizations —
  generating and critiquing**; colorblind-safe color is one supporting
  capability, not the front door.
- The corpus fetcher is pluggable via a generic plug point (`$VIZIER_FETCHER`
  or a `FETCHER` callable) with an httpx default — no proprietary fetcher named
  in the source or required for open-source use.
- `[critique]` pins `somm>=0.7` / `somm-core>=0.7` (both on PyPI).

### Removed
- `SOURCES.md` (heavy with internal sourcing detail); replaced by the lighter,
  public `INFLUENCES.md`.
