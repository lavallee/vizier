# Evaluation protocol

How we measure whether vizier's judgment improves as the corpus and
rubric scaffolding grow.

## What we measure

Four axes, all 1–5 integer scores emitted by an LLM judge comparing
two critiques of the same artifact against a ground-truth assessment:

- **alignment** — does the critique identify the same structural
  issues the ground truth flags? Partial credit for catching some.
  Penalize critiques that hallucinate problems or miss named ones.
- **specificity** — does the critique refer to *this* artifact's
  specific choices (chart form, encoding, labels, audience), or
  could it apply verbatim to any data visualization?
- **actionability** — would a designer reading this know what to
  change, and why? "Make it clearer" = low; "replace this sankey
  with a dot plot because X" = high.
- **structural risk identification** — does it name risks the chart
  form, encoding, or interaction model creates for a cold reader,
  independent of whether the ground truth names them?

Aggregate output per run:

- Per-case winner (A, B, or tie).
- Mean axis scores per side.
- Axis deltas (B − A).
- Totals: wins by underlying run + ties + parse failures.

## Case files

One markdown file per case in `evals/cases/<id>.md`. Frontmatter:

```yaml
---
id: <slug>                          # unique, stable
source_kind: weaver | wild
artifact_title: "…"
artifact_url: https://…
ground_truth_source: weaver-notes | sigma-jury | junkcharts-critique | kantar-jury
tags: [chart-type, topic, audience, …]
---
```

Body: prose describing the artifact. Keep descriptions *truthful*
and *specific* but *pre-retrospective* — don't leak weaver's learned
lessons into the description for weaver cases. The description is
what the critic sees; the ground truth is what we compare against.

### Ground-truth resolution (automatic)

- `weaver-notes` → `weaver/projects/<slug>/notes.md` (looser match on
  directory name suffix, e.g., `new-bern` ↔ `new-bern-profile`).
- `sigma-jury` / `kantar-jury` / `junkcharts-critique` → corpus item
  matched by URL or slugified title. That item is also *excluded*
  from retrieval during the informed run so the critic can't quote
  its own oracle.

## Running an eval

### Full cycle (recommended)

```
uv run vizier eval full
```

Runs naive → informed (multi style) → judge (n=3 median) → prints
results. All stamped with the current `corpus_hash` from
`corpus/manifest.json`.

### Individual steps

```
uv run vizier eval naive               # baseline: plain LLM, no corpus
uv run vizier eval informed            # corpus-retrieved + rubrics
uv run vizier eval informed --style ft # publication-style overlay
uv run vizier eval judge <A> <B>       # single-pass judge
uv run vizier eval judge <A> <B> -n 3  # median-of-3 (lower variance)
uv run vizier eval results             # reprint latest judge summary
```

### Optional knobs

- `--resilient` on `informed` / `full`: cross-provider fallback
  (OpenRouter → MiniMax) with retries. Off by default so eval runs
  reproduce exactly. Records `fallback_trace` in each per-case
  output.
- `--style <name>` on `informed` / `full`: overlay FT / NYT /
  Pudding / Junk Charts publication-style lens on the base rubric.
- `--model <id>` / `--provider <name>` on `informed` / `full`:
  run the informed critique on a non-default backend for
  head-to-head model comparisons (e.g.
  `--model gemini-2.5-pro --provider gemini`). The run directory
  is suffixed with a model tag (`…-informed-gemini-2-5-pro`) so
  parallel runs don't collide.

### Model head-to-heads

To compare two models on identical case descriptions:

```
uv run vizier eval informed                                  # Opus 4.7 (default)
uv run vizier eval informed --model gemini-2.5-pro --provider gemini
uv run vizier eval judge <opus-run> <gemini-run> -n 3
```

The judge (Opus 4.7 by default) scores both against the same
ground truth. With `n=3`, the variance floor is low enough to
detect per-axis differences ≥ ~0.3.

### Swapping the judge model

**Default judge is Gemini 2.5 Pro via the Gemini API free tier**
($0/run). To cross-check with a paid model:

```
uv run vizier eval judge <A> <B> -n 3 --model anthropic/claude-opus-4.7 --provider openrouter
```

In our one measured head-to-head (Opus-informed vs Gemini-informed,
13 cases, both judges), Gemini judge and Opus judge agreed on the
winner — which rules out "judge prefers its own output" as a worry
for this specific comparison. Running both graders is the standard
rigor check for a new head-to-head or a new case set.

### Vision captions (optional per case)

When a case has an image at `evals/cases/images/<case-id>.png`
(PNG or JPG), `vizier eval informed` runs the captioner first and
splices the caption into the user prompt. Cache is keyed on
`sha256(image) + model + prompt_version` — same image cost-free on
re-runs.

- Default captioner: `qwen2.5vl:7b` via local ollama. ~20s–17min per
  image on M1 Pro depending on resolution (cap width around 1024 for
  ~5 min per image at reasonable accuracy).
- Cache: `evals/captions/<sha>.<model>.<version>.md`. Each run's
  per-case output records `vision_caption` metadata (sha, model,
  duration, cached-or-fresh) so runs are provenance-complete.
- Skip vision: `vizier eval informed --no-vision`.

**Caption-per-page discipline.** If an artifact spans multiple
pages/views (a hero + detail chart + methodology page), caption each
page separately and name them in the case's `artifact_image_path`
list. Don't caption page A and describe the project as if the caption
covers pages B and C too — the critic will conflate the screenshot
with the case description and surface observations about content that
wasn't in either.

### Cost expectations

- Default path (Gemini judge + Gemini informed + Gemini naive):
  **$0 per full eval** on the Gemini API free tier.
- All-Opus-4.7 via OpenRouter (naive + informed + judge n=3, 13 cases):
  **~$15–20 per full eval cycle**. Opt in explicitly.
- Mixed (Gemini informed, Opus judge): ~$1–2 per cycle.

Every run's index.json records `model` + `provider` so cost
attribution is recoverable after the fact.

## Interpreting a run

### Wins

Per-case majority. With `n=3` the judge runs 3 independent passes and
takes the majority vote per case; pure 1–1–1 ties surface as `tie`.

### Axis deltas

`B − A` means "informed − naive" for the standard comparison.
Positive = informed beat naive on that axis. Magnitudes ≤ ~0.3 may
be judge noise; ≥ 0.5 are more likely real.

### Fallback trace

If `--resilient` was set and any case used a non-primary provider,
the per-case frontmatter has:

```yaml
fallback_trace:
  - { provider: openrouter, model: anthropic/claude-opus-4.7, outcome: rate_limited, … }
  - { provider: minimax,    model: MiniMax-M2.7,              outcome: ok, … }
fallback_attempts: 2
```

Runs with fallbacks aren't apples-to-apples with primary-only runs —
MiniMax M2.7 critique ≠ Opus 4.7 critique. Treat as a completeness
signal, not a quality signal.

## Variance

Same critique re-judged returns different scores; observed range
≈ ±0.3 per axis per pass. Median-of-3 cuts that by ~1.7×.

Practical implication: to detect a *corpus improvement* worth
≥ 0.3 on one axis, use `n=3` at minimum. To detect ≥ 0.15 you'd
need `n=9` or a different judge methodology (e.g., pairwise
ranking with Elo updates).

## Longitudinal tracking

Each judge run writes `evals/judge/<timestamp>-judge/index.json`
with the `corpus_hash` the runs were scored against. To see
whether a corpus change moved the needle:

1. Note current `corpus_hash` before the change.
2. Run `vizier eval full` — capture pre-change judge output.
3. Make the corpus change (`vizier ingest <source>` for a new source,
   edits to existing sources, new rubric, new principle, etc.).
4. `vizier snapshot` — regenerate manifest; note new `corpus_hash`.
5. Run `vizier eval full` again — capture post-change judge output.
6. Compare the per-axis deltas and per-case winners.

The `corpus_hash` is the anchor for "which corpus state was this
evaluated against," so a git-like history of corpus ↔ eval outcomes
is recoverable from the run directory alone.

## Adding a case

1. Pick an artifact with a resolvable ground truth (weaver
   retrospective, Sigma jury commentary, Kantar special-award quote,
   Junk Charts post that critiques a specific chart, etc.).
2. Write a description that's specific about form, encoding, audience,
   and context — but *doesn't* leak the ground truth's conclusions.
3. Add tags the retrieval layer can match (chart family, topic,
   audience).
4. Set `ground_truth_source` to one of the recognized values.
5. Re-run `vizier eval full` — the new case appears in the winner
   totals and axis means.

## Known variance sources

- **Judge stochasticity** — same (A, B, ground-truth) tuple produces
  different scores run-to-run. Mitigated by `n=3`.
- **Case description thinness** — if a description omits the encoding
  the ground truth flags, neither critique can catch it. Review the
  retrieval summary and the critique body after adding a case.
- **Ground-truth noise** — weaver retrospectives are authored once,
  not consensus-reviewed. Jury commentary is a single committee's
  read. The judge's "alignment with ground truth" inherits whatever
  flavor that ground truth has. Treat alignment as one axis among
  four, not the sole quality signal.
