---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.591575Z'
id: principle-document-the-external-pipeline-even-when-ingest-lives-elsewhere
source: weaver
tags:
- ingest
title: Document the external pipeline, even when ingest lives elsewhere
type: principle
---

Some projects pull from a shared data warehouse or pipeline that lives
outside the project (our `simba` tooling, or a lab's export scripts).
The previous principle still applies — but its honoring happens via a
*pointer*, not the script itself. Every project gets a
`PROVENANCE.md` at its root that names the external generator, inputs,
cut date, and (for sims) random seed and calibration targets.

Receipts: `new-bern-profile`, `maplewood-profile`, and
`info-market-voting` all pull from external Python scripts; none had
a local `PROVENANCE.md`. Six months later, someone reading the
project sees `data.js` headers saying "Auto-generated, do not edit"
and can't find the recipe without grep-ing across repos. That's the
gap this principle closes.

Minimum contents of `PROVENANCE.md`:

- **Generator.** Path to the external script (incl. repo if separate).
- **Inputs.** Source URLs / APIs + cut dates.
- **Output.** The data file this project consumes.
- **Rebuild command.** What someone runs to re-derive the data.
- **Parameters, if simulation.** Random seed, parameter ceilings,
  calibration targets (e.g., *Cupertino informed rate capped at 15%
  per research prior ceiling*).

This is a wrapper around the first ingest principle, not a weaker
alternative. The test is the same: someone else (or future-you) can
reproduce the data from what's at the project root alone.
