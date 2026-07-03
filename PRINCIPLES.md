# Vizier principles

Working practices for evaluation and judgment — the critique companion
to `weaver`. Weaver is about **execution**; vizier is about
**evaluation**. Shared vision (information-design tradition,
chart-form rigor, audience-first framing), distinct roles.

The file is organized by workflow stage (Collect → Retrieve →
Evaluate → Deliver → Measure) with cross-cutting meta-principles
first, the same shape `weaver/PRINCIPLES.md` uses. Stages are messy
and iterative in practice — moving between them is expected.

---

## Cross-cutting

### Evaluation is not execution

Weaver makes, vizier judges. The disciplines overlap but diverge in
method:

- **Weaver's discipline** is generative: "I have a blank canvas;
  what's the right move?"
- **Vizier's discipline** is forensic: "I have an artifact; what did
  the maker catch, miss, or not yet see?"

Principles that work for both (match chart form to licit comparisons;
name the audience; declare the headline claim) live in both books.
Principles uniquely about judgment (constraint-difficulty accounting;
ground-truth exclusion in retrieval; prior-art citation) live here.

When a principle appears in both, the wording matches — the cross-
reference is explicit so the two books stay consistent as they grow.

### Generation and critique are one expertise

vizier's knowledge is bidirectional. The checks that *judge* a palette
also *generate* a passing one; the pattern library that critiques a
form also recommends it. So vizier is not only the critic — it is the
dataviz **expertise**, and the split with weaver is sharpening
accordingly:

- **weaver renders** — the SVG/DOM, layout, motion, the actual pixels.
- **vizier decides** — which form, which colors, does the palette clear
  colorblind + contrast, what did a finished artifact get wrong.

"Evaluation is not execution" still holds: vizier never draws. But the
*computable* decisions — colorblind-safe palettes, ordinal ramps,
legible ink, form-fit — now live in vizier as callable primitives
(`src/vizier/analyze`, exposed over the MCP tools `suggest_palette` /
`suggest_ramp` / `ink_on` / `validate_palette` / `analyze_artifact` /
`check_contrast`). weaver, and any generator, should *ask vizier* at
generation time rather than duplicate the color math or re-derive the
form taxonomy. What vizier suggests is what vizier would pass — the same
thresholds serve both directions.

Keep the two halves distinct in kind, though: the generation
primitives above are **computable and deterministic** (correct by
construction, no LLM). The corpus-backed judgment — prior-art
citation, constraint-difficulty, publication lens — stays critique-
side and LLM-mediated. Don't let "vizier generates now" blur into
"vizier's LLM opinions are ground truth." Only the computed part is.

### Pattern recognition, not general reasoning

The April 2026 measurement showed corpus-informed critique's biggest
lift over a naive LLM is on **structural-risk identification** —
specifically the subtle, domain-specific failure modes (denominator
mismatches, cohort composition breaks, within-panel-vs-cross-panel
asymmetries) that don't transfer from general training.

This tells us what the corpus actually adds: **a domain-specific
pattern library, not smarter reasoning.** A competent generalist can
apply Cairo's framework. The corpus provides specific prior patterns
to match against. That matches how senior practitioners work — they
haven't gotten smarter in general; they've accumulated a library of
failure-mode archetypes and success-under-constraint archetypes.

Implication: corpus investments should prioritize *more examples of
the same failure modes* (more Junk Charts posts, more Sigma jury
commentary, more weaver retrospectives) over more frameworks or
rubrics. The marginal principle-book adds little; the marginal 50
well-chosen case studies add a lot.

### Keep eval cheap enough to run often

Longitudinal tracking requires running eval repeatedly. If each cycle
costs $10+, cycles happen rarely, and the corpus-change-to-outcome
feedback loop dies. Default to free-tier models (Gemini 2.5 Pro via
the Gemini API); opt into paid models (Opus 4.7) only for specific
rigor checks or production-critic comparisons.

This isn't a compromise on quality — the free-tier critique still
dominates naive-critique by a comfortable margin. Opus sharpens it
another notch, but the marginal lift doesn't justify paying for every
methodology iteration.

---

## Collect

### Keep the corpus on

Corpus-building is ongoing discipline, not a one-time ingest. Every
annual Sigma cycle, every new Junk Charts post, every weaver
retrospective adds coverage. Rerun `vizier ingest all` periodically;
the `corpus_hash` is the anchor.

### Prefer specific pattern libraries over canonical theory

A new Junk Charts critique post teaches vizier a specific failure mode
it can match against future artifacts. A new canonical-theory chapter
teaches a framework vizier mostly already has. Given finite time, bias
toward the former.

The exception is rubrics that *structure how to apply* existing
pattern libraries (Cairo's five pillars, FT Visual Vocabulary
families, Junk Charts Trifecta Checkup). Those shape retrieval and
critique output and earn their place.

### Tag for constraint-difficulty

Award corpus items — Sigma especially — often carry implicit
difficulty signals in their jury commentary: "the team worked in
exile," "dataset was 100+ inconsistent spreadsheets from rights
groups," "only publishable from outside the country," "the reporter
was abroad when the story broke." These are the markers of
constraint-difficulty, and they're precisely where senior practitioner
pattern-matching lives — high-impact stories that were *hard* to
visualize and were done well despite that.

When ingesting, tag items that carry constraint markers so retrieval
can bias toward similar-constraint prior art when evaluating a hard
piece. A state-2 comparable (hard + good) is more valuable than 10
state-1 comparables (easy + good).

### Multiple critique sources, not a single authority

No single source captures the full shape of critique: Junk Charts is
strong on chart-form rigor but decontextualized; Sigma/Kantar juries
weigh journalism impact and methodology over chart craft; weaver
retrospectives capture execution under specific constraints but are
self-critiques (inherent investment in defending choices).

Maintain source diversity in the corpus. The triangulation —
"chart-form rigor says X, jury commentary says Y, practitioner
retrospective says Z" — is the shape of a complete evaluation. Any
single source read alone produces a partial lens.

---

## Retrieve

### Ground-truth exclusion is non-negotiable

When a case's ground-truth item is in the corpus, exclude it from
retrieval. Otherwise the critic quotes its oracle.

Currently implemented in `src/vizier/critique/retrieve.py`: matches on
URL and slugified title (≥12 chars to avoid spurious matches like
`2015-r`). Every run's `retrieval_summary.excluded_ground_truth_items`
logs what got dropped.

Why it matters: without exclusion, informed-critique scores look
good for the wrong reason — the model is summarizing the jury
commentary it was just handed. The delta vs naive becomes an artifact
of retrieval structure, not of real pattern-matching improvement.

### Case-based recall beats rubric-axis recall

When designing retrieval, favor concrete-piece similarity
(this-resembles-X) over principle-tag similarity
(this-involves-principle-P). The embeddings change empirically showed
this: hybrid (embeddings + tag bonus + tier bonus) retrieved
thematically-tighter picks than keyword-matching alone, and the
resulting critiques cited specific prior pieces more.

"This resembles the Reuters 2022 Shahed piece" does more calibration
work than "this is a Flow-family chart per the FT Vocabulary." The
rubric axes structure the output; the case similarities carry the
judgment.

### Always-include the rubric scaffold

Weaver principles, Cairo's five pillars, and the FT Visual Vocabulary
are always included in full (not top-K retrieved). They're small
enough to fit in context (~40 weaver principles + 67 FT chart types +
5 Cairo pillars ≈ 15K tokens) and load-bearing enough that partial
inclusion would degrade critique structure.

Per-source top-K (Sigma, Kantar, Junk Charts) is where retrieval
quality matters — that's the pattern library.

---

## Evaluate

### Name the critique lens

Before producing a critique, decide which lens applies. Four useful
ones (matching the weaver Frame-stage principle):

1. **Representation** — is what's shown the best encoding of the
   material?
2. **Completeness** — are there things missing that would improve it?
3. **Difficulty-adjusted craft** — given the constraints, how well
   did the work perform?
4. **Audience fit** — does the form work for the actual reader?

The same artifact can pass one lens and fail another. Don't collapse
them. A critique that names its lens can be right or wrong, but it's
legible; a critique that doesn't is vague by construction.

Style selection (`--style=ft|nyt|pudding|junkcharts|multi`) maps
loosely to lenses: `junkcharts` weights representation + audience
fit, `pudding` weights completeness + audience fit, `multi` blends
all four. Pick by case.

### Constraint-difficulty is a first-class input

Senior practitioners' implicit pattern library is largely
**state-2 examples**: hard story + good craft. That's where skill is
legible. A fair critique distinguishes:

- **State 1** — easy story + good craft: unremarkable; expected
- **State 2** — hard story + good craft: the craft signal; name the
  specific techniques used to cope with the constraint
- **State 3** — easy story + weak craft: straightforward failure
- **State 4** — hard story + weak craft: separate constraint-imposed
  ceiling from bad craft; the critique carries both dimensions

Sigma and Malofiej jury commentary disproportionately recognize
state 2 — the jury's implicit framing is often "look what this team
pulled off despite X." When the retrieved prior art is Sigma-heavy,
the critique should inherit that constraint-aware framing. When it's
Junk-Charts-heavy (chart-form rigor, decontextualized), the critique
is freer to score on pure chart-form axes.

Don't score craft without naming the constraint context first.
Otherwise the critique is unfair to hard problems and too kind to
easy ones.

### Structural risk is the highest-leverage axis

Of the four judge axes (alignment / specificity / actionability /
structural risk), **structural-risk identification** is where
informed critique beats naive by the largest margin (typically +1.0
or more). Focus critique attention there:

- Denominator mismatches / cut-date biases
- Cohort composition breaks
- Color-only encoding in grayscale-hostile contexts
- Ornamental interactivity gating the headline story
- Chart-form invitation to illegal comparisons
- Jargon labels assuming prior knowledge the audience doesn't have

This is where domain pattern-matching pays off. Don't under-invest
here by letting rubric-axis thoroughness crowd out structural
observations.

### Cite comparable prior work

Same principle as weaver's Critique-stage addition. A critique that
names a specific comparable piece is sharper than one citing only
principles. Practitioners talk this way. Vizier's retrieval surfaces
candidates; the critique prompt instructs the model to cite them by
short title where relevant.

Avoid citation theatre (referencing pieces that aren't actually
similar). The surfaced comparable should share structural features,
not just topic. "Both are about climate change" is not a useful
comparable; "both use a flowchart-as-navigation structure" is.

---

## Deliver

### Genre shapes voice

Critique voice should match artifact genre:

- **Design-critique targets** (racetracks, bad encodings, abuse of
  form) → Junk Charts voice: Trifecta Checkup, direct, concrete
  re-chart proposal
- **Civic-data explanatory work** → multi-lens voice: chart-form
  rigor + story-craft + audience calibration
- **Newsroom coverage profiles** → editor-facing voice, light rubric
  name-dropping
- **Portfolio / generative / high-craft pieces** → Cairo's five
  pillars explicitly, with acknowledgment that craft signal matters
  independently of utility

Don't default to one rubric framing for every artifact. Style is a
genre selector; retrieval tilts it; explicit `--style` overrides.

### Keep the rubric invisible when the argument carries

Cairo's pillars and FT Vocabulary families are evaluation scaffolds,
not audience-facing structure. A critique that opens "Let me apply
Cairo's five pillars..." reads as homework. A critique that *uses*
the pillars to structure an argument but leads with the finding
lands better.

The stronger vizier gets at pattern recognition, the less it needs to
explicitly name the rubric to make its case. Rubric-naming is a
scaffold; remove it when the argument no longer needs it.

### End with concrete, named moves

A critique that ends with "make it clearer" is useless; one that
ends with "replace the racetrack with a sorted horizontal bar chart,
or if the dashboard constraint is real, switch to a bullet chart
per Stephen Few 2005" is actionable.

Concreteness discipline:

- Name the alternative form (not "a better chart")
- Name the specific encoding change (not "fix the labels")
- Cite a piece that did it well, if one is retrievable
- Acknowledge when the constraint makes the alternative unavailable
  ("if brand requires circular, use radial-bar-from-common-radius")

---

## Measure

### `corpus_hash` is the anchor

Every eval run stamps the `corpus_hash` it was evaluated against.
That's the provenance for "did this corpus change help?" A judge
output without a `corpus_hash` is a dated photograph with no
timestamp.

### Compare runs at comparable corpus states

Don't compare naive@hash-X to informed@hash-Y — the informed run
might have benefitted from retrieval that wasn't in X. Always pair
naive and informed at the same corpus hash. `vizier eval full` enforces
this by running both in one command.

When comparing *two different corpus states*: run the full pipeline
(naive + informed + judge) under each hash, then diff the judge
outputs. The per-case winners and the per-axis deltas together
answer "did this corpus change improve judgment?"

### Judge variance is real; median it out

Same critique re-judged returns scores varying ±0.3 per axis.
Median-of-N (default N=3) cuts that by ~1.7×. To detect a corpus
improvement worth ≥0.3 per axis, N=3 is the minimum; to detect ≥0.15
you need N=9 or a different methodology (pairwise ranking, Elo).

Variance budget matters more when the expected lift is small —
adding a handful of Junk Charts posts is unlikely to move aggregate
scores by more than 0.1 per axis, so N=9 would be needed to see it.
Adding a whole new source (Malofiej book ingest) might move scores
by 0.3+, detectable at N=3.

### Cross-check the judge

One judge can have systematic bias (self-preference, methodology
blind spots). For new head-to-heads, run the judge under at least
two models and check they agree on the winner. Disagreement is a
signal to look closer, not noise to average.

We did this once (Opus vs Gemini informed-critique, judged by
Gemini): both judges agreed Opus-informed > Gemini-informed. That
rules out Gemini self-preference for that specific comparison.
Different judge pair, different comparison → re-check.

---

## Retrospect

Vizier's eval protocol is itself a thing being evaluated. When a
measurement round teaches us something about vizier (not about the
subject), update this file.

What was learned in the first measurement rounds (April 2026):

- Cairo's Truthful and Functional pillars carry the critique; the
  other three are more useful as generation prompts than evaluation
  axes (incorporated into *structural risk is highest-leverage*).
- Prior-art citation is measurably sharper than axiom reasoning
  (incorporated into *cite comparable prior work*).
- Awards-jury lens and chart-form lens are not the same dimension
  (incorporated into *name the critique lens*).
- Retrievers surface ground-truth items by default; exclusion is
  required (incorporated into *ground-truth exclusion*).
- Default-paid models silently burn budget during methodology
  iteration (incorporated into *keep eval cheap*).

Add to this list when the next measurement round surfaces a pattern
worth encoding.
