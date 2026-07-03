# Influences

What vizier's taste is built to emulate — and the philosophy behind turning it
into something a machine can act on.

## The philosophy

Good data visualization has a large, contentious literature. Juries disagree;
critics disagree with juries; the academic evidence disagrees with both about how
much any of it matters. A working editor holds all of that in tension and, under
deadline, still makes a call: *this form, not that one; this palette, not that one;
this chart earns its place, that one doesn't.*

vizier's project is to **distill that broad, argued-over body of opinion down to a
determination** — ideally one small and firm enough to sit in a state machine. Not
because taste is simple, but because most of the decisions that actually block a
chart are more decidable than the discourse around them suggests. Whether a palette
survives the common colorblindness transforms, whether label ink is being confused
for a series hue, whether the chosen form matches the comparison the data supports —
these have answers. vizier's job is to find the answers that *are* computable and
return them deterministically, and to fall back on corpus-grounded critique only for
the parts that genuinely require judgment.

This is why generation and critique are colocated. They are the same knowledge read
in two directions: the thresholds that let vizier *propose* a form or palette are the
thresholds it *critiques* against, so what it suggests is what it would pass. Held
apart, the two halves can even be pointed at each other — a generator proposes, the
critic pushes back — which is the most honest test of either.

## The families of influence

vizier doesn't reproduce any single authority. It triangulates across kinds of
signal that fail in different directions, so no one bias dominates.

**Award juries.** Competition results are an ordinal signal of expert consensus:
a tiered winners list tells you a piece cleared a high bar against a given year's
panel. Jury commentary, where it's published, explains *why*. Useful, but situated —
awards reward the canon of their moment and their venue, so they're one input, not
ground truth.

**Structural critique.** Venues that dissect finished charts — the before/after,
"here's what's wrong and here's the fix" tradition exemplified by *Junk Charts* —
teach the *language* of evaluation and calibrate the axes from the negative
direction. This register is the closest match to the voice vizier itself should
produce.

**Practitioner walkthroughs.** The maker explaining what they were trying to show,
what alternatives they weighed, what they compromised on, and what they'd change in
hindsight. Award citations tell you what passed; walkthroughs teach the transferable
*reasoning* — the highest-leverage material for turning examples into judgment.

**Canonical theory and explicit rubrics.** The durable arguments and named
frameworks a graphics desk expects a senior hire to have internalized — Tufte and
Bertin for the classical grammar, Cairo's Truthful/Functional/Beautiful/Insightful/
Enlightening pillars for a modern synthesis, Munzner for task-type structure, and the
*FT Visual Vocabulary* as the closest thing to a public rubric for chart-form choice.
Theory is where a rubric gets its vocabulary; the empirical literature is where
claims about *why* one encoding beats another get tested.

**A negative corpus.** Systematically bad examples calibrate the same axes from the
opposite side. Popularity is not correctness here, so these are sampled as
counter-examples, never treated as authority.

## From influence to determination

The families above are how vizier learns the shape of expert taste; they are not what
it ships. Only vizier's **own authored distillations** are redistributed — the
chart-form pattern library, the rubrics, the FT-vocabulary parse. Third-party writing
is copyrighted and is never committed; a contributor rebuilds their own working corpus
locally (see the corpus notes under `docs/`). What travels with the tool is the
*determination* — the computable checks and the critique scaffolding those influences
were distilled into.
