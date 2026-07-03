---
details:
  origin: weaver/projects/new-bern-profile/notes.md
fetched_at: '2026-04-18T19:23:27.596903Z'
id: project-new-bern-profile
source: weaver
tags:
- weaver-project
title: 'new-bern-profile: New Bern — retrospective notes'
type: process_note
---

# New Bern — retrospective notes

*Written retrospectively, 2026-04-18, after the PRINCIPLES.md
workflow-stage reorganization. These answers are reconstructed from
the shipped project; they are what the Frame/Explore notes would have
said if we'd had the new stages when starting.*

---

## Frame

### Decision the reader should be able to make
A newsroom editor pulling an outlet into a news desert should know
what to lead with — which beats carry weight in New Bern specifically,
and which common-sense beats (e.g., young-voter mobilization) the data
doesn't support covering.

### Headline claim
New Bern is a retiree-skewed, high-turnout, Craven-County coastal town
whose elections are decided by voters 55+; any newsroom here needs to
lead with aging and downstream health coverage, not youth civic
engagement. Elections data shows *who's registered and who's voted*, not
who voted for whom or how young cohorts behave — plan coverage around
that limit.

### Counter-narrative ruled out
Three, all surfaced as editorial hooks on the elections page:

1. "Young-voter turnout has collapsed over the last four elections" —
   ruled out by the small-multiples form, which shows the denominator
   is *today's active voter file*, biasing earlier elections down.
2. "Party registration predicts voting behavior" — ruled out by
   explicitly noting the voter file tells you who's registered, not
   how they voted.
3. "Turnout is broadly high" — ruled out by showing turnout is
   high *at the top of the age ladder*, concentrated, not diffused.

### Audience and prior knowledge
Newsroom editors. Assumed to know what ACS is, read election returns,
and recognize the difference between registration and behavior. Not
assumed to know the Medill news-desert classification or the specifics
of the Craven County voter file.

---

## Explore

### What the data can and can't say

**Can say:**
- Age distribution and its MOEs (ACS 5-year, Craven County)
- Party registration counts by age band (NC voter file)
- Turnout per election, by age band, using today's voter file as denominator
- Presidential race outcomes at the county level
- Library, broadband, CHR health indicators (county-level)

**Can't say (but readers might assume):**
- Vote share by age (voter file has registration, not ballot content)
- How 18–29 turnout has *actually* trended — denominator mismatch
- Township-level turnout or demographics (dataset is county-level)
- BRFSS health at New Bern scale (only metro-level available)

**Could say with more ingest:**
- Precinct-level registration and turnout (NC state board publishes)
- Medill news-desert score if we pulled the current dataset

### Unresolved tensions
None major that we recall. Scope was narrow (one place, one audience).

---

## Gap report

### Honors ✓

- **Match chart form to licit comparisons** — small-multiples on
  elections.js prevents the denominator false-reading. This is the
  canonical example cited in PRINCIPLES.md.
- **Name the counter-narrative** — six editorial hooks on the
  elections page explicitly name gotchas readers would otherwise hit.
- **Lede-first** — hero + 5–7 takeaways before charts.
- **AP style** — "Craven County," "New Bern, N.C." used consistently.
- **Contrast discipline** — inline `style='fill'` used on on-bar text.
- **Action-oriented framing** — "what to lead with" is explicit, not
  buried.

### Violates ✗

- **Every project has a repeatable ingest script** — `data.js` is
  auto-generated from `simba scripts/export_new_bern_profile.py` but
  the script lives outside the project; no local `ingest.*` or
  `PROVENANCE.md` re-points at it.
- **Denominators travel with the data** — the "active-voter file as
  denominator" fact lives in code comments and chart notes, not in
  the data structure itself. A future analyst rebuilding the chart
  from `data.js` alone would not see the constraint.
- **Name units at the data layer** — voter-file counts are `male`,
  `female`, `count`, `votes` — not `male_count`, `dem_share`, etc.
  ACS and voter-file counts are indistinguishable in field names.
- **Reading guide directly above each novel diagram** — heatmap and
  small-multiples have context *below* (as editorial hooks) but no
  1–2 sentence "how to read this" *above*.
- **Name names, cite research inline** — sources are bylined and
  footnoted, but specific claims don't carry author-year cites.

### Reveals as missing from PRINCIPLES.md

- **Document the external pipeline, even if ingest lives elsewhere.**
  Both New Bern and Maplewood pull from a shared `simba` data
  warehouse. A local `PROVENANCE.md` that names the external script,
  the input URLs, and the cut date — without necessarily re-hosting
  the ingest — would close the reproducibility gap. Candidate new
  Ingest principle.
- **Editorial-hook form as counter-narrative surfacer.** Our
  existing *name the counter-narrative* principle is a Frame-stage
  discipline; New Bern shows it also deserves a Narrate-stage
  expression ("every chart that rules out an obvious misreading
  should carry a short card or hook saying so"). Candidate new
  Narrate principle.
