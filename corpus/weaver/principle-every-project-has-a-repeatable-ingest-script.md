---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.591437Z'
id: principle-every-project-has-a-repeatable-ingest-script
source: weaver
tags:
- ingest
title: Every project has a repeatable ingest script
type: principle
---

The data file the viz reads should never be hand-built. It should come
from a runnable script — `ingest.js`, `ingest.py`, or a short
`Makefile` — that goes from named sources to the final JSON.

Receipts (negative): too many projects currently have `data.json` with
no script alongside. Six months later the recipe is gone. Rerunning
with newer ACS vintages, or validating a reader's question against the
source, becomes a research project instead of a one-liner.

Pattern:

- One file per project: `ingest.{js,py}` at the project root.
- Inputs named at the top (URL, file path, API endpoint + cut date).
- Outputs to `data.json` (or `data/*.json`) consumed by the viz.
- A sibling `PROVENANCE.md` or header comment saying how it was built
  and when.

Even genuinely bespoke data (a hand-curated CSV, a one-off spreadsheet)
should go through this wrapper. The script can be a three-line "read
CSV, record provenance, emit JSON" — the point is the convention, not
the complexity. Test: someone else (or future-you) can reproduce
`data.json` from the script alone.
