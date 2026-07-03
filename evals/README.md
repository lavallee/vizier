# evals/

Measure whether vizier's critique judgment improves as the corpus and
rubric scaffolding grow.

## Shape

- `cases/` — reference cases. Each is a markdown file with YAML
  frontmatter naming: the artifact being critiqued, a short target
  critique (what a human expert judged), which axes are load-bearing,
  and provenance. Start small (3–5 cases drawn from weaver
  retrospectives), grow when the signal is proven.
- `runs/<timestamp>.jsonl` — per-run output. Each line pairs a case ID
  with vizier's emitted critique, the `corpus_hash` it was evaluated
  against (from `corpus/manifest.json`), and the rubric set used.
  With these, we can diff: "run at corpus hash X vs. run at corpus
  hash Y on the same cases."

## What "learning" means here

Not gradient-descent learning. Vizier is a prompt/retrieval system with
a growing corpus. It "learns" in the sense that a richer corpus and
sharper rubrics should yield critiques that:

1. Agree with weaver's lived retrospectives (we have these already).
2. Agree with external judgments we trust (Sigma juries, Kantar
   special-award commentary where it exists).
3. Produce structured, axis-addressed critiques (not prose-mush).

The first test run comes when the critique emitter exists — not
before. This scaffold just makes sure we don't have to reinvent it
at that point.
