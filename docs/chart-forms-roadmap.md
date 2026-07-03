# Chart-forms guide — roadmap + progress

*Handoff doc. Captures the state of the vizier + weaver effort as of
2026-04-23 (end-of-day refresh) and what's still open. Written so a
future session can pick up cold.*

---

## The arc, in three phases

### Phase 1 · corpus build-out
**Goal:** so vizier's critique can cite prior art, ingest practitioner-walkthrough content from the open web. **State: done.**

- **6,657 non-pattern items** across 14 sources:
  `kantar`, `sigma`, `junkcharts`, `pudding`, `weaver` (internal
  principles), `rubrics`, `ft-vocab`, `source-opennews`, `eagereyes`,
  `visualising-data`, `cairo-blog`, `nightingale`, `snd`, `observable`.
- **Shared scaffolding:** `_sitemap_blog.py` (sitemap + optional
  richer-fetcher fallback for Cloudflare), `_fetch_html.py` (raw HTML +
  image caching at `corpus/<source>/_raw/` and `_images/`, gitignored).
- FT Chart Doctor + SND.Ink **deferred** — both gated (subscription,
  account). If creds arrive, route through the optional richer fetcher
  (`$VIZIER_FETCHER`) with a browser strategy and login.

### Phase 2 · queryable substrate
**Goal:** make the corpus callable from agents and fast to query. **State: done.**

- **SQLite at `corpus/.vizier.db`**: `items`, `items_fts` (FTS5 virtual),
  `embeddings` (bge-small-en-v1.5 blobs). Regenerable via
  `vizier db build`; body-hash check means re-embed only changed rows.
- **Query layer** (`vizier.db.query`): `search()` (BM25),
  `find_similar()` (cosine), `lookup()`, `list_sources()`,
  `list_rubrics()`, `list_principles(stage=?)`, `stats()`, plus
  pattern-specific `get_pattern(id, transclude=True)` and
  `list_patterns(purpose_family=?)`.
- **MCP server** (`vizier mcp`, stdio): 9 tools exposing the query
  layer. Wire-up example for Claude Desktop / Cursor below.

### Phase 3 · chart-forms guide
**Goal:** a wiki-shaped reference for chart forms, queryable by agents and readable by humans. **State: v1 shipped.**

- **36 `chart_pattern` corpus items** across all 9 FT Visual
  Vocabulary families. Each pattern carries structured fields
  (see schema below) and a prose body.
- **Weaver reader** (`reader/`)
  renders the 36 patterns as a hash-routed guide:
  - Root TOC: "Decide by question" ladder + full family grid
  - Per-family pages at `#/family/<slug>` (primary-first pattern order)
  - Deep links at `#/family/<slug>/<pattern-id>`
  - Each pattern section: family eyebrow, capsule, reading
    checklist, WU/WN columns, prose body, common mistakes,
    transcluded alternatives, canonical + antipattern examples
  - **36 live d3 demos** — one per pattern
  - **Interactive parameter sliders** on histogram (bin count),
    ridgeline (bandwidth), strip-plot (collide radius)
  - **Decoder rings** inline on boxplot, sunburst, chord-diagram,
    matrix-plot
  - **Annotated demos** on sankey, violin, bump-chart, scatterplot,
    parallel-sets
  - **Comparison cards** at `#/compare`: same data / different forms
    (distribution triad, spatial triad)
  - **Review harness** at `#/review`: every demo in sequence with an
    automated issue checker (text clipping + text-text overlap via
    viewport-relative rects)

---

## Current state at a glance

```
vizier: 36 chart_pattern items + 6,657 other corpus items = 6,693 total
weaver: chart-forms-guide project, 36/36 demo coverage, 0 flagged issues
```

| Axis | Count / state |
|---|---|
| Patterns | 43 |
| Families populated | 9/9 (FT Visual Vocabulary complete) |
| Live d3 demos | 43/43 |
| Interactive sliders | 3 (histogram, ridgeline, strip-plot) |
| Decoder rings | 8 (boxplot, sunburst, chord, matrix-plot, violin, parallel-sets, cartogram, radar) |
| Interactive patterns | **33/43 with toggle** (+small-multiples, radar-chart) — 100-assertion test suite via `npm run check:chart-forms:interactive`. 3 more (histogram, ridgeline, strip-plot) are always-interactive via sliders. Remaining 7 (bar, stacked-bar, diverging-bar, dot-plot, lollipop, pie, waffle) were skipped by P1 — values already labeled, no affordance earns its keep. |
| Static/interactive toggle | present on 33/43 demos; principles doc renders at `#/interactivity` (INTERACTIVITY.md → HTML) |
| Vite dev | pinned to port 5173, bound to all interfaces, `oslo` / `oslo.local` / `.local` allowed for LAN access |
| Teaching annotations | 5 (sankey, violin, bump, scatter, parallel-sets) |
| Glossary terms (cross-cutting) | 17 (IQR, KDE, bandwidth, Dorling, …) |
| Related-projects links | 1 (sankey → sankey-when-and-how) |
| Canonical examples resolved | 91 |
| Antipattern examples resolved | 20 |
| Dangling alternative refs | 0 |
| Automated review issues | 0 (regression-checked via `npm run check:chart-forms`) |
| Reading-checklist coverage | 36/36 |
| Common-mistakes coverage | 36/36 |

---

## Item schema (the chart_pattern shape)

```yaml
---
id: sankey                     # matches filename, source-local slug
source: chart-forms
type: chart_pattern
title: Sankey diagram
tags: [flow, ribbon, conservation, categorical]
details:
  purpose_families: [Flow, Part-to-whole]     # FT Vocab, primary-first
  capsule: >                                  # one-line transcluded summary
    A diagram of conservation under flow...
  when_to_use:        [...]                   # picking-the-form gate
  when_not_to_use:    [...]
  common_mistakes:    [...]                   # cosmetic/config traps
  reading_checklist:  [...]                   # questions a reader should ask
  alternatives:                               # refs to other patterns
    - id: parallel-sets
      when: "Branching co-occurrence..."
  canonical_examples:      [<source>/<id>, ...]
  antipattern_examples:    [<source>/<id>, ...]
  related_principles:      [weaver/principle-*]
---
Prose body (a few hundred words on the form, variants, cosmetic details).
```

`get_pattern(id, transclude=True)` returns this structure with
`alternatives[].capsule` and `canonical_examples[].title/url` resolved
to full objects.

---

## Open tradeoffs / design decisions worth revisiting

1. **Markdown source of truth vs SQLite index** — we picked markdown
   + regenerable DB. Snapshot via `vizier patterns export` to JSON for
   weaver consumption. Costs: the weaver reader is a snapshot of a
   moment. Fine at this scale (~36 patterns); revisit if live-updating
   the reader becomes interesting.

2. **Hash router vs real SPA** — weaver's chart-forms-guide uses a
   hash router to stay a single-vite-build project. Scales to maybe
   100 patterns before the all-at-once render becomes heavy. Beyond
   that, lazy-load demo modules.

3. **Comparison cards are hand-authored** —
   `renderDistributionTriad` and `renderSpatialTriad` each hand-pick
   data + forms. Can't auto-generate from pattern pairs. Low effort
   per card but doesn't scale if you want 20 comparisons.

4. **Demos embedded in one file** — `live-examples.js` is ~2700
   lines. Splitting per-demo into separate modules would be tidier
   but reduces the "one import" simplicity. Keep as-is until the
   file becomes painful.

5. **No per-family decision diagrams** — we shipped one decision
   diagram (sankey-when-and-how, a sibling weaver project). Could
   generalize that pattern to each family, but each one is hand-
   authored. See Tier-2 items below.

6. **Synthetic data per demo** — each demo has its own synthetic
   seed. "Canonical demo dataset per family" would let comparison
   cards reuse data without re-inventing; cross-cutting refactor
   that's not worth it yet.

7. **FT Visual Vocabulary as the taxonomy axis** — aligned to the
   ft-vocab corpus item already in our corpus. Alternatives (Kirk's
   9-slice wheel, Cairo's 5-pillar) would be valid; changing now
   would be disruptive.

---

## Roadmap (prioritized)

### Tier 1 · polish + correctness
- [x] **Cross-link to sankey-when-and-how** — shipped via a new `related_projects` field on the sankey pattern (threaded through `query.get_pattern` + rendered as "Go deeper" card in the reader).
- [x] **Decoder rings for parallel-sets, violin, cartogram** — all three shipped. Violin's decoder contrasts unimodal vs bimodal ("a boxplot would hide this"); parallel-sets makes the "axis order is editorial" rule visual; cartogram states "shape is NOT geography".
- [x] **Glossary** — 17-term glossary at `reader/glossary.js`. Route `#/glossary` + deep-link `#/glossary/<slug>`. First-occurrence-per-pattern inline linkify on body/checklist/mistakes (~27 links on the distribution family page). Flash-highlight on deep-link arrival.
- [x] **Review harness as regression check** — `npm run check:chart-forms` runs playwright headlessly against `#/review`, counts clean/flagged, and exits non-zero on any issue. Current: 36 demos, 36 clean, 0 flagged.

### Customer-feedback asks (integrated this session)
- [x] **Fast `vizier db build`** — default is now items + FTS5 only (~seconds). Separate `vizier db embed` backfills vectors; `--embed` flag on build runs both. Stderr hint fires when >50 items lack embeddings. Fixes the "MCP surface is non-functional for ~12 min on fresh clone" pain.
- [x] **MCP registration guide** — `docs/mcp-setup.md` covers `claude mcp add` for other projects, JSON config for Claude Desktop/Cursor, tool-reference table, troubleshooting (empty list_principles / find_similar, FTS5 punctuation, uv PATH). README now has a pointer.
- [x] **FTS5 escaping for hyphens/apostrophes** — `_normalize_fts_query` in `vizier/db/query.py`. Splits on `-` and `'` to match FTS5's own tokenizer (so `forecast-cone` works like `forecast cone`), quotes `:`/`.`, preserves advanced syntax (`"phrase"`, `OR`, `NEAR(...)`). 11/11 normalization cases pass; `forecast-cone` went from 0 hits to 3.
- [x] **`vizier critique <image>` command (v1)** — `src/vizier/critique/adhoc.py` + CLI. Flow: vision caption → LLM pattern classifier → retrieve pattern checklist/mistakes + BM25 snippets → somm LLM synthesizes structured review. Raster-only for now (PNG/JPG/WEBP); SVG + URL input are follow-ups.

### Tier 2 · depth
- [ ] **Worked examples pulled from corpus** — pattern pages currently cite external URLs (Observable, Kirk, Kosara). For 5-10 highest-signal examples, cache one image from `corpus/<source>/_images/<item>/` and display inline as "from the corpus" with the cite.
- [ ] **Per-family decision diagrams** — generalize the sankey-when-and-how tree. Each family page gets a small decision widget that walks from "what's the reader asking?" to the primary forms in that family. Visual complement to the "Decide by question" text ladder.
- [ ] **More patterns** — gap analysis: radar/spider (commonly asked, usually wrong), marimekko, calendar heatmap (as its own pattern distinct from heatmap), dendrogram, Gantt, box-and-jitter-strip (hybrid), lollipop-chart (explicit rather than dot-plot variant).
- [ ] **`decode_chart(pattern_id)` MCP tool** — returns just `reading_checklist` + `common_mistakes`. Handy when an agent gets shown a user's chart and needs to ask the right questions about it.
- [ ] **Pattern-quality score on canonical_examples** — some references are stronger than others. A 0-1 confidence field per canonical reference would let the reader surface the best ones first.

### Tier 3 · ambitious
- [ ] **Image-annotated worked examples** — embed a real chart from the corpus WITH annotations ("this ribbon is 6 of 1000; it reads as 'nothing' but the story calls it 'significant drop'"). Turns the reader from reference into case-study exemplar.
- [ ] **Corpus re-ingest cadence** — monthly `vizier ingest all` + `vizier db build`. Kosara + Kirk + Cairo + Nightingale are prolific; fresh items improve retrieval quality over time.
- [ ] **Second reader UX** — "flash card" view: one pattern at a time, swipe left/right, optimized for learning a form in isolation. Separate route, same data.
- [ ] **FT Chart Doctor via `browser_login`** — if the user provides FT credentials, ingest Alan Smith's column. Would add 150+ walkthrough items from a top source.
- [ ] **SND.Ink via category curation** — the current `snd` ingester pulls categories generically; a more targeted pass might capture the "Show Don't Tell" walkthrough archive that was the original ask.
- [ ] **Retrieval evals with chart-forms** — our evals/ pipeline measures informed-critique quality against ground truth. Running with chart-forms items as additional retrieval context should improve the "what form should they have used?" axis score.

---

## Running + config

**Vizier (Python + uv):**
```
cd /Users/lavallee/Projects/vizier

# corpus health
uv run vizier stats                    # items per source
uv run vizier db stats                 # DB row counts
uv run vizier patterns list            # 36 patterns

# rebuild
uv run vizier db build                 # walks corpus/, upserts, re-embeds changed rows
uv run vizier patterns export -o docs/reader/data.json

# serve
uv run vizier mcp                      # stdio MCP server

# evals (not central to this effort, but still operational)
uv run vizier eval full
```

**Preview the guide (static — no build):**
```
cd ~/Projects/vizier
python -m http.server 8000 -d docs   # then open http://localhost:8000/reader/
```
The guide vendors its own d3 and design tokens, so it serves as plain static
files (this is also what GitHub Pages serves out of `docs/`).

**MCP config (Claude Desktop / Cursor / claude.ai):**
```json
{
  "mcpServers": {
    "vizier": {
      "command": "uv",
      "args": ["--directory", "/Users/lavallee/Projects/vizier", "run", "vizier", "mcp"]
    }
  }
}
```

---

## Key paths

| Path | Purpose |
|---|---|
| `vizier/corpus/` | All corpus items (markdown + YAML frontmatter) |
| `vizier/corpus/chart-forms/` | The 36 chart_pattern items |
| `vizier/corpus/.vizier.db` | SQLite index — regenerable, gitignored |
| `vizier/src/vizier/schema.py` | Item / ItemType literal |
| `vizier/src/vizier/db/query.py` | search / find_similar / lookup / pattern-aware queries |
| `vizier/src/vizier/db/build.py` | Corpus → SQLite populator |
| `vizier/src/vizier/mcp_server.py` | FastMCP stdio server |
| `vizier/src/vizier/ingest/` | 14 per-source ingesters + shared helpers |
| `vizier/scripts/suggest_pattern_examples.py` | Replayable find_similar-based curation |
| `vizier/docs/chart-forms-plan.md` | Schema + taxonomy plan doc |
| `vizier/docs/process-notes-sources.md` | Source-tiering reference |
| `vizier/docs/index.html` | Landing page (GitHub Pages) |
| `vizier/docs/reader/` | The chart-forms guide (self-contained static) |
| `vizier/docs/reader/data.json` | Exported snapshot from vizier |
| `vizier/docs/reader/live-examples.js` | 36 demo renderers + comparison triads |
| `vizier/docs/reader/main.js` | Hash router + pattern-section renderer |
| `weaver/projects/sankey-when-and-how/` | Earlier sibling project — specific-form essay |

---

## Routes reference (chart-forms-guide)

| Hash | Renders |
|---|---|
| `#/` | Root TOC: "Decide by question" ladder + 9-family grid |
| `#/family/<slug>` | All patterns in a family, primary-family-first |
| `#/family/<slug>/<pattern-id>` | Same page, scrolled to that pattern |
| `#/compare` | Same-data-different-forms triads |
| `#/review` | Dev harness: every demo + automated issue list |

Family slugs: `flow`, `part-to-whole`, `ranking`, `change-over-time`,
`magnitude`, `distribution`, `correlation`, `spatial`, `deviation`.

---

## Recent commits (for git-log context)

**vizier:**
- `569983d` — chart-forms: +9 patterns (27→36), close dangling refs
- `3cfd1db` — enrich canonical + antipattern examples from corpus
- `3f59816` — 15 new patterns + common_mistakes field
- `81df712` — chart_pattern corpus + MCP graph tools (initial 12)
- `b974d1d` — reading_checklist field
- `f222188` — sankey YAML fix (fill:none was parsed as dict)

**weaver:**
- `15822cb` — #/review harness + 24 layout fixes
- `1a41c83` — interactive parameter sliders
- `1bdf4b4` — #/compare route
- `1e35cd3` — annotated demos + decoder rings
- `2f2a249` — render reading_checklist block
- `6ec03dd` — "Decide by question" ladder on root
- `bb7dd9f` — hash router + per-family pages
- `fac865e` — 100% demo coverage (36/36)

---

## Quick "what's next?" if picking this up fresh

Tier 1 + the customer-feedback asks are all in. The next natural
pickup set is Tier 2 + the `vizier critique` extensions:

1. **Pre-flight**: `uv run vizier db build` (fast now) + `uv run vizier patterns export -o docs/reader/data.json`, then preview with `python -m http.server 8000 -d docs`. Fast; no build step.
2. **Extend `vizier critique`**: SVG input (rasterize via `cairosvg` or headless chromium), URL input (fetch + page screenshot). Also useful: a `--pattern auto` mode that surfaces the classifier's top-3 candidates rather than forcing one choice.
3. **Worked examples pulled from corpus** (Tier 2) — for the 5-10 highest-signal canonical references, cache one image from `corpus/<source>/_images/<item>/` and display inline as "from the corpus".
4. **Per-family decision diagrams** (Tier 2) — generalize the sankey-when-and-how tree pattern.
5. **New patterns** (Tier 2) — radar/spider, marimekko, calendar heatmap, lollipop, box-and-jitter-strip hybrid.

The project is in a state where anything from Tier 2 or Tier 3 is a
clean addition — no core refactors needed.
