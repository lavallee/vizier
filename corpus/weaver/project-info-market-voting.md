---
details:
  origin: weaver/projects/info-market-voting/notes.md
fetched_at: '2026-04-18T19:23:27.595994Z'
id: project-info-market-voting
source: weaver
tags:
- weaver-project
title: 'info-market-voting: Info-market-voting — retrospective notes'
type: process_note
---

# Info-market-voting — retrospective notes

*Written retrospectively, 2026-04-18, after the PRINCIPLES.md
workflow-stage reorganization. These answers are reconstructed from
the shipped project; they are what the Frame/Explore notes would have
said if we'd had the new stages when starting.*

*This is the principle-heaviest project — most of PRINCIPLES.md's
receipts cite it. Expect high honor-rates and the thinnest gap report
of the three we've revisited.*

---

## Frame

### Decision the reader should be able to make
A civic funder, policy actor, or state LWV league should leave knowing
**which intervention lever to pull in which type of community** — and
why one-size-fits-all "just publish a voter guide" advice fails.

### Headline claim
Most Americans cast local votes on almost no information. The failure
modes are distinct by community type (supply-gap vs. language mismatch
vs. demand-gap vs. media-market structure), and research identifies
specific interventions that work for each. One map doesn't fit all
communities.

### Counter-narrative ruled out
Three named:

1. **"Voters are irrational."** Ruled out by framing the sim around
   rational-ignorance research (Downs, Popkin, Lupia–McCubbins): cue
   use is a defensible strategy when information is scarce.
2. **"Publish a voter guide and voters will use it."** Ruled out by
   the Ashtabula demand-gap card, which shows supply alone doesn't
   move behavior where civic trust is thin.
3. **"Language access is a nice-to-have."** Ruled out by the Pharr
   card showing Spanish-language supply is the binding constraint.

### Audience and prior knowledge
Civic funders, state LWV leaders, policymakers, community foundations,
digital-local publishers. Assumed to care about actionable
interventions and name-able orgs. Not assumed to know sankeys,
agent-based simulations, or cue-voting theory — all get glossaries
and reading guides.

---

## Explore

### What the data can and can't say

**Can say:**
- Agent-level information pathways through 10 real communities
  calibrated to published priors
- Segment × outcome flows (who ends up with an evidence-grounded vote,
  who skips, who votes on a cue)
- Race-tier differences (federal vs. mid-tier vs. down-ballot) within
  each community
- Supply-grid diagnostics per community (what civic-info channels
  exist)
- Which specific levers correlate with which outcomes in each
  community type

**Can't say (but readers might assume):**
- Individual voter behavior (agents are synthetic; 5–20 real adults
  per agent)
- Causal effects of interventions (the sim is diagnostic, not
  experimental)
- What happens when multiple failure modes coexist (cards treat them
  as independent archetypes)

**Could say with more ingest:**
- Additional communities beyond the calibrated 10
- Time-series if we re-simulated with historical supply conditions

### Unresolved tensions
None that we recall at ship. The scope was narrow (diagnosis + rx),
the audience was clear (funders + civic leaders), and the "what the
chart can't claim" was ruled out structurally.

---

## Gap report

### Honors ✓ (nearly everything)

- **Match chart form to licit comparisons** — main sankey (segment →
  outcome) kept separate from zoom sankeys (researchers, shortcut
  users) to avoid the near-deterministic-column compression.
- **Collapse combinatorial explosions** — pathway column bucketed to
  primary source (10 categories, not 30).
- **Order stage categories meaningfully** — SEGMENT_ORDER, MODE_ORDER,
  OUTCOME_ORDER, PATHWAY_ORDER explicit; sankey uses
  `.nodeSort(null)` to preserve.
- **Click-to-isolate** — BFS both directions, dim-don't-hide, same-node
  resets, background resets, tooltip affordance. Canonical
  implementation.
- **Contrast via `onBarText()`** — luminance-based, inline
  `.style('fill', ...)` everywhere.
- **Tiered rankings shown together** (Finding 4) — all three race
  tiers per community in one view, no tabs.
- **Scrolling over clicking** — deep dives use a community dropdown,
  but summary findings never require interaction.
- **Persistent glossary below the viz** — two-column block, all terms
  visible simultaneously.
- **Reading guides above novel diagrams** — with colored column
  swatches.
- **Lede-first** — 5-takeaway hero before any chart; methodology in
  collapsible `<details>` at the bottom.
- **Agents ≈ adults dual-display** — "152 agents ≈ 972 adults"
  everywhere; scale note names the per-community factor.
- **AP style via `apLabel()`** — consistent across the project.
- **Action-oriented conclusions** — every failure-mode card pairs
  diagnosis with "What has worked elsewhere" + "Who should act"
  naming specific orgs.
- **Calibrate against external priors** — Cupertino's 22% informed
  rate was caught against 5–15% research prior ceiling and tightened.

### Violates ✗

- **Every project has a repeatable ingest script** — same pattern
  across the portfolio: `data.js` generated by
  `scripts/voting_sim/build_weaver_data.py` living outside the project.
  No local `ingest.*` or `PROVENANCE.md`. Random seed, parameter
  ceilings, calibration targets aren't captured at the project root.
- **Name names, cite research inline** — research is cited (Downs,
  Popkin, Lupia–McCubbins, Trounstine) but the inline author-year
  convention isn't applied to every claim that leans on a source.

### Reveals as missing from PRINCIPLES.md

- **Explain the *why* of structural splits in the reading guide.**
  The main sankey + two zooms exist because "mode nearly determines
  outcome" — a fact the break-apart principle turned into three
  diagrams. The reading guide above each zoom could name that
  reasoning explicitly ("we split this because the two columns were
  nearly deterministic — the combined view was noisy"). Teaches the
  reader the principle along with the chart. Candidate *addition*
  to the existing *reading guide directly above each novel diagram*
  principle.
- **Sim-parameter provenance**. For simulation projects specifically,
  `PROVENANCE.md` needs to capture the random seed, parameter
  ceilings, and calibration targets — not just source URLs. Sub-case
  of the external-pipeline principle but worth calling out: sim
  reproducibility is richer than data reproducibility.
