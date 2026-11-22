# Roadmap — vizier

## Outcome 1 — Stabilize the public 0.1 contract

- Keep the PyPI distribution, import package, CLI, MCP tools, docs, reader, and
  optional extras mutually consistent through clean-install tests.
- Preserve Malo notice-period parity where promised while making Vizier the
  sole forward implementation.
- Add compatibility fixtures for patterns, rubrics, extension databases, and
  generated reader data.

*Graduation:* a clean public install supplies every documented computable tool
and the promised read-side parity surface. *Kill:* legacy commands without a
current consumer receive a dated removal path rather than permanent shims.

## Outcome 2 — Prove the decision-and-critique loop on real graphics

- Integrate Vizier into at least two production graphics workflows
  from form selection through artifact analysis and specialist critique.
- Record rule findings, overrides, human critique, and final artifact outcomes
  as evaluation cases.
- Turn repeated reviewer findings into deterministic checks only when the
  boundary is genuinely computable.

*Graduation:* Vizier prevents or materially improves a real chart issue and
the same rule passes its own generated recommendation. *Kill:* checks that
produce unmanageable false positives remain critique guidance, not gates.

## Outcome 3 — Measure critique quality and retrieval value

- Expand evaluation beyond color into form, reading order, uncertainty,
  annotation, mobile legibility, and accessibility with typed expected
  findings.
- Compare public-only, private-extension, and no-retrieval critique while
  tracking citation quality and unsupported claims.
- Make failure to retrieve relevant prior art visible rather than masking it
  with model confidence.

*Graduation:* retrieval shows measured lift on held-out critique cases and its
citations are usable by a reviewer. *Kill:* corpus-backed critique stays
optional if it cannot outperform the computable layer plus a clear rubric.

## Outcome 4 — Grow a bounded ecosystem

- Publish stable integration guidance for generators, MCP clients, private
  extension databases, and new pattern/rubric contributions.
- Keep public/private corpus boundaries, licensing, and reproducibility guarded
  in CI.
- Decide the Malo archive/error policy after the notice period from actual
  usage evidence.

*Graduation:* an external consumer integrates without private artifacts or a
source checkout. *Kill:* no extension point becomes permanent without a second
real consumer.

## Outcome 5 — Prove `show` on real tables

- Run `vizier show` on real notebook and newsroom tables (with datapackages,
  suppressed values and geography) and record where the ranking, the words or
  the notes needed a human override.
- Verify the Datawrapper path against the live API with a real token (the
  suite only covers a fake server), including the type ids and the metadata
  keys for scatter axes and table heatmaps.
- Decide whether an interactive variant (vendored, pinned d3) earns its place
  beside the static SVG.

*Graduation:* the top-ranked option is used as drawn, or with only word
changes, on most real tables tried. *Kill:* forms that keep needing hand
repair drop out of the renderable set and stay ranked-only.

## Keeping this file honest

Released capabilities move to `CHANGELOG.md`; compatibility promises carry an
owner and review date rather than lingering as vague future work.
