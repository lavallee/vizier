---
details:
  origin: weaver/projects/maplewood-profile/notes.md
fetched_at: '2026-04-18T19:23:27.596485Z'
id: project-maplewood-profile
source: weaver
tags:
- weaver-project
title: 'maplewood-profile: Maplewood — retrospective notes'
type: process_note
---

# Maplewood — retrospective notes

*Written retrospectively, 2026-04-18, after the PRINCIPLES.md
workflow-stage reorganization. These answers are reconstructed from
the shipped project; they are what the Frame/Explore notes would have
said if we'd had the new stages when starting.*

---

## Frame

### Decision the reader should be able to make
A newsroom editor covering Maplewood (or considering doing so) should
understand Maplewood's demographic tier, partisan environment, and
civic infrastructure well enough to plan beats — and know which
common beat-ideas the available data can't support without extra
reporting.

### Headline claim
Maplewood is a family-heavy, upper-middle-income inner-ring suburb in
a heavily Democratic county that swung 4pp toward Trump in 2024 as a
one-time event, not a trend. The primary is where elections are
decided. Schools and local civic life are the coverage beats; the
biggest data blind spot is the NJ voter file.

### Counter-narrative ruled out
Two specific ones:

1. "Maplewood has a real sex imbalance in 0–17 (28% male excess)" —
   ruled out by rendering MOE whiskers. At ~±500 per band, the
   apparent skew is inside sampling variance.
2. "Essex is drifting Republican" — ruled out by showing the 2024
   4pp shift is discontinuous, not a steady drift, and doesn't match
   Hudson/Passaic's larger cracks.

### Audience and prior knowledge
Newsroom editors familiar with ACS and election returns. Implicit
prior: they know the New Bern coverage-profile exists and will read
Maplewood as a comparison case (inner-ring suburb vs. coastal-rural
town, Democratic stronghold vs. competitive). Not assumed to know
the NJ voter-file situation or the BMF availability.

---

## Explore

### What the data can and can't say

**Can say:**
- ACS age/income/tenure with MOEs (Maplewood township)
- Essex County election returns, 2008–2024 (MIT Election Lab)
- Peer-county comparisons (DEM share, trend direction)
- BRFSS health indicators at metro scale (Newark MSA) as upper-bound
  anchors for Maplewood
- NCES school enrollment, IMLS library usage
- County-level USDA typology (metro tier 1, Nonspecialized)

**Can't say (but readers might assume):**
- Age-stratified turnout (no NJ voter file ingested)
- Party registration by demographic (same reason)
- Maplewood-level BRFSS (only metro-level exists publicly)
- Non-profit density (no BMF ingested for NJ)
- Medill news-desert score (no Medill dataset ingested)

**Could say with more ingest:**
- Primary turnout (NJ state publishes results, not currently ingested)
- School-district-level performance (NJ DOE)

### Unresolved tensions
- **Standalone profile vs. comparative to New Bern.** The data-sources
  page explicitly invites comparison; main.js doesn't frame it as
  comparative. Traveled forward unresolved — reader infers.
- **"Family-heavy" framing vs. adult-coverage needs.** Takeaways
  lead with schools, but the actual adult population is large and
  mental-health data (at metro scale) hints at underserved adult
  coverage. Tension not surfaced.

---

## Gap report

### Honors ✓

- **Survey data needs visible error bars** — age pyramid is the
  canonical example: cell-level MOEs preserved through ingest,
  combined via sqrt-sum-of-squares, rendered as whiskers, named in
  the counter-narrative.
- **Match chart form to licit comparisons** — elections page stays
  at the county level rather than attempt township-level
  age-stratified turnout it can't support. Absence-as-choice.
- **Name the counter-narrative** — sex-skew and Essex-drift both
  named explicitly with the data's response.
- **Declare audience + prior knowledge** — "newsroom editor" is
  stated; New Bern is the implicit comparison.
- **Preserve uncertainty at ingest** — MOEs on ACS, lo/hi bounds
  on BRFSS, all carried to render.

### Violates ✗

- **Every project has a repeatable ingest script** — same as New Bern:
  `data.js` generated from external `simba` pipeline, no local script.
- **Denominators travel with the data** — ACS 2020–24 vintage is in
  the byline, not structured on the data. Elections data lacks
  denominator metadata entirely.
- **AP style** — inconsistency: title is "Maplewood, NJ" (should be
  "Maplewood, N.J."); body copy is mostly correct.
- **Reading guide directly above each novel diagram** — pyramid,
  pres-2024-multi, pres-trend, health charts all missing one-line
  reading guides. Chart notes come *after*.
- **Persistent glossary below the viz** — `data-sources.html` is a
  separate page, not below-the-chart. Readers lose context switching
  pages.
- **Name names, cite research inline** — sources bylined and
  footnoted; no inline author-year.

### Reveals as missing from PRINCIPLES.md

- Same **Document-the-external-pipeline** candidate surfaced by
  New Bern.
- **"Data-sources page" as a design pattern** — both profiles ship
  a dedicated data-sources page that combines provenance + caveats
  + dataset tiers. This is an emergent pattern worth naming. It
  sits between Ingest and Narrate: the Ingest discipline (document
  sources) gets an in-product Narrate surface (the page itself).
  Candidate new principle.
- **Absence-as-choice.** Maplewood's decision not to attempt
  township-level age-stratified turnout (which would require the NJ
  voter file we don't have) is an application of *match chart form
  to licit comparisons* — but the principle as written implies
  "pick a form"; Maplewood shows "decline to draw" is a valid
  sibling. Worth adding as a bullet under that principle.
- **Named unresolved tensions retroactively.** Writing this notes.md
  surfaced two tensions (standalone vs. comparative; family-heavy
  framing vs. adult-coverage needs) that traveled silently in the
  shipped project. Evidence that the Explore-stage tension-naming
  discipline would have caught them if we'd been doing it.
