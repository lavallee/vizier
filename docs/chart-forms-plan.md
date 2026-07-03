# Chart forms guide — schema + taxonomy plan

*Build plan for a comprehensive patterns/antipatterns collection, readable
by humans via a weaver project and queryable by agents via MCP. Internal
reference; not a public doc.*

## Goals

1. **One entry per chart form**, each with when-to-use + when-not + named
   alternatives. A practitioner can walk a decision path and land on
   the right form.
2. **Transclusion** — "instead reach for X" inlines X's capsule summary
   so readers (and agents) don't have to chase links.
3. **Agent-callable** — MCP tools return fully-resolved patterns so a
   downstream LLM can ground a recommendation in structured evidence,
   not prose retrieval.
4. **Sourced** — every pattern cites the corpus items that justify it.

## Where it lives

- Source of truth: `corpus/chart-forms/<id>.md` (one markdown file per
  pattern, same conventions as every other corpus source).
- Indexed by the existing SQLite DB; no schema changes — all pattern-
  specific fields go under `Item.details`.
- Surfaced by:
  - `vizier.db.query.get_pattern(id)` — pattern with optional transclusion
  - MCP tools `get_pattern` / `list_patterns`
  - A weaver `chart-forms-guide` project that renders the full graph

## Item shape

```yaml
---
id: sankey
source: chart-forms
type: chart_pattern       # new type literal
title: Sankey diagram
tags: [flow, ribbon, conservation]
details:
  # Taxonomy (FT Visual Vocabulary aligned, primary + possibly-secondary)
  purpose_families: [Flow, Part-to-whole]
  # Short capsule rendered when this pattern is transcluded elsewhere
  capsule: >
    A diagram of conservation under flow: the total on the left equals
    the total on the right. Reach for it when the data has a real
    conserved quantity moving between discrete states.
  when_to_use:
    - "Real conserved quantity (energy, money, population, carbon)"
    - "Reader should see how that quantity partitions between states"
    - "Columns are mutually-exclusive categories, not time steps"
  when_not_to_use:
    - "Funnel / cohort shrinkage — 'lost' users aren't a conserved bucket"
    - "Branching co-occurrence (attribute × attribute); use parallel sets"
    - "Rank reshuffle; use a bump chart"
  common_mistakes:
    # Cosmetic / configuration traps — not about picking the wrong form,
    # but about doing the right form badly. Separates "should I use this?"
    # from "am I using this well?"
    - "Letting d3-sankey's default nodeSort tangle the ribbons; use nodeSort(null) with explicit stageOrder"
    - "Ornamental click-to-isolate without dim-don't-hide on the rest of the flow"
    - "Near-deterministic columns compressed into one sankey; split them"
  alternatives:
    - id: parallel-sets
      when: "Branching co-occurrence without flow conservation"
    - id: bump-chart
      when: "Story is ordering over time, not magnitude"
    - id: stacked-area
      when: "Part-to-whole over continuous time, no discrete states"
    - id: flow-map
      when: "Geography is the flow substrate (rivers, migration)"
  canonical_examples:
    - observable/d3-sankey-component
    - visualising-data/energy-technologies-visualisation-for-the-iea
    - cairo-blog/bloomberg-visualizes-shrinking-html
  antipattern_examples:
    # corpus items whose critique illustrates "this shouldn't be a sankey"
    - junkcharts/clear-and-confused-states
  related_principles:
    - weaver/principle-order-stage-categories-meaningfully
    - weaver/principle-reading-guide-directly-above-each-novel-diagram
---
A sankey is a diagram of conservation under flow...

(Full prose body. Expanded from the sankey-when-and-how essay. The
prose is for humans; agents prefer the structured fields.)
```

### Why stash in `details`

Keeping pattern-specific fields in `Item.details` means no schema
migration, no change to SQLite populate/query, and no need to
distinguish pattern DB rows from any other item. The MCP tools can
project the details dict into typed fields at query time. If the
pattern type outgrows this representation we can promote fields to
the main schema later — nothing will break in the meantime.

### `capsule` vs `body`

- `capsule`: ~40-word summary for transclusion (shown inline when
  another pattern references this one). Content rule: must stand
  alone — no back-references.
- `body`: the full essay. Used when the reader lands on this pattern
  directly. Can reference capsules from alternatives.

## Taxonomy: FT Visual Vocabulary families

Using FT Visual Vocabulary verbatim because (a) it's already in the
corpus at `ft-vocab/*`, (b) practitioners recognize it, and (c) it
maps cleanly to purpose-first questions.

| Family | Purpose-question a reader is asking |
|---|---|
| **Deviation** | "How do these values diverge from a reference?" |
| **Correlation** | "Do these two variables move together?" |
| **Ranking** | "What's the order?" |
| **Distribution** | "What does the spread look like?" |
| **Change over time** | "How has it changed?" |
| **Magnitude** | "Which is bigger?" |
| **Part-to-whole** | "How does this split up?" |
| **Spatial** | "Where?" |
| **Flow** | "What moves, from where to where?" |

Patterns can claim **multiple** families (sankey = Flow + Part-to-whole;
flow-map = Flow + Spatial; bump chart = Ranking + Change-over-time).
The decision diagram routes on the *primary* family but the `list_patterns`
tool returns anything matching the filter.

## Seed list (staging order)

Picked to cover the most-reached-for and the most-common-mistake-bait
patterns first, skewing toward forms we already have evidence about
in the corpus:

| # | ID | Primary family | Why seed first |
|---|---|---|---|
| 1 | **sankey** | Flow | already written; proves schema |
| 2 | **parallel-sets** | Part-to-whole | canonical "not-sankey" alternative |
| 3 | **stacked-bar** | Part-to-whole | honest alternative to a funnel-sankey |
| 4 | **bump-chart** | Ranking | rank-over-time pair with sankey |
| 5 | **flow-map** | Spatial, Flow | the sankey-on-a-map case |
| 6 | **stacked-area** | Part-to-whole, Change | next common sankey-alternative |
| 7 | **line-chart** | Change | the default; everyone needs it |
| 8 | **small-multiples** | Distribution, Change | meta-form; almost always the answer |
| 9 | **scatterplot** | Correlation | the default correlation form |
| 10 | **choropleth** | Spatial | most-abused spatial form |
| 11 | **cartogram** | Spatial | the "area misrepresents" fix |
| 12 | **pie-chart** | Part-to-whole | antipattern-heavy; necessary |

Later additions (when schema is proven): bar, dot plot, slope chart,
heatmap, histogram, boxplot, violin, streamgraph, treemap, waffle,
marimekko, connected scatter, chord, network, dendrogram.

## Transclusion mechanics

### In the weaver reader

The renderer walks each pattern's `alternatives[]` and, per entry,
fetches the referenced pattern's `capsule` and inlines it below the
"when NOT to use" list with a heading like "Instead: **Parallel sets** —
*{capsule}*. (open →)". The "open →" link jumps to that pattern's
anchor on the same page.

### In the MCP server

`get_pattern(id, transclude=True)` returns:

```json
{
  "id": "sankey",
  "title": "Sankey diagram",
  "capsule": "...",
  "body": "...",
  "when_to_use": [...],
  "when_not_to_use": [...],
  "purpose_families": ["Flow", "Part-to-whole"],
  "alternatives": [
    {
      "id": "parallel-sets",
      "when": "Branching co-occurrence without flow conservation",
      "title": "Parallel sets / alluvial",
      "capsule": "Shows joint frequencies between categorical axes...",
      "purpose_families": ["Part-to-whole"]
    },
    ...
  ],
  "canonical_examples": [
    { "key": "observable/d3-sankey-component", "title": "...", "url": "..." },
    ...
  ]
}
```

With `transclude=False` the alternatives and examples come back as
bare ID references, for callers that want minimal payloads.

`list_patterns(purpose_family=?)` returns an array of `{id, title,
purpose_families, capsule}` — the shortlist an agent uses to narrow
down.

## Decision diagram generalization

The sankey-when-and-how decision tree becomes a family-first router:

```
What's the question the reader is asking?
  ├─ "How does it split?"          → Part-to-whole family
  │    ├─ over time?               → Stacked area / streamgraph
  │    └─ at a single moment?      → Stacked bar / pie (with caveats)
  │    └─ between categorical axes? → Parallel sets
  ├─ "What moves, where?"          → Flow family
  │    ├─ geography is substrate?  → Flow-map
  │    └─ conserved quantity?      → Sankey
  ├─ "What's the order?"           → Ranking family
  │    ├─ over time?               → Bump chart
  │    └─ at one moment?           → Ordered bar / dot plot
  ├─ "How has it changed?"         → Change-over-time family
  │    └─ one or few series?       → Line chart
  │    └─ many series?             → Small multiples
  ├─ ... (remaining 5 families)
```

This is a tree; the weaver renderer draws it as a radial or a
left-to-right tree. Each terminal form links to its pattern page.

## Build order

1. **Now**: schema lockdown + seed 4 patterns (sankey, parallel-sets,
   stacked-bar, bump-chart). Confirm schema stands up before going wide.
2. **Next**: MCP tools `get_pattern` / `list_patterns` with transclusion.
3. **Then**: fill out the remaining 8 seed patterns.
4. **Finally**: weaver reader with the generalized decision diagram.

Each stage ships independently — corpus items are useful the moment
they're written; MCP works as soon as the items are present; the reader
is the last mile.
