# Changelog

All notable changes to vizier are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and vizier adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). See
[RELEASING.md](RELEASING.md) for the release process.

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
