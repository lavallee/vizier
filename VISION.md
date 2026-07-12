# Vision — vizier

**North star:** Every journalistic chart decision that can be made honestly by
rule or prior art is made consistently before publication, while choices that
require editorial judgment stay explicit and receive evidence-backed critique.

**North-star metric:** reviewed artifact adoption — published graphics whose
form, encoding, color, structure, and critique path used Vizier, with rule
findings resolved or consciously overridden and downstream correction/review
burden measured.

## Strategy bets

- **Generation and critique share one DNA.** The thresholds Vizier recommends
  are the thresholds it validates, so proposed forms and palettes can survive
  their own critic.
- **Compute the decidable parts.** Deterministic form, color, contrast, ink,
  and structure checks stay keyless, fast, explainable, and safe to call from
  agents and generators.
- **Retrieve judgment with its prior art.** Optional corpus-backed critique
  cites the practices and criticism it relies on instead of returning an
  ungrounded aesthetic opinion.

## Non-goals

- Rendering charts or replacing Weaver and project-specific graphics code.
- Automating editorial judgment, story framing, or ethical tradeoffs.
- Shipping copyrighted critique corpora in the public package.
- Returning a recommendation when constraints make an honest answer impossible.

## Engine map

- Pattern and rubric data define form-selection and reading contracts.
- Deterministic color, contrast, ink, SVG/HTML, and structural analyzers handle
  computable quality.
- The public corpus interface, optional search/critique extras, and Somm model
  routing provide evidence-backed judgment.
- MCP and CLI surfaces let agents and generators call the same decision layer.
- Weaver renders the artifact; Vizier and specialist review judge it before
  publication.
