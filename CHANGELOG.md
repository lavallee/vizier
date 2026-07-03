# Changelog

All notable changes to vizier are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and vizier adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). See
[RELEASING.md](RELEASING.md) for the release process.

## [0.1.0] — unreleased

First public release. Replace "unreleased" with the date when the `v0.1.0` tag
is cut.

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
