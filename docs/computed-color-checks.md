# Computed color checks — vizier's first deterministic signal

Everything else in vizier is LLM-mediated: a chart image becomes a vision caption,
then a text-LLM critiques the caption + retrieved corpus prose. Nothing was ever
*computed* from the artifact. This upgrade adds the one part of data-viz that is
genuinely computable — color — so a critique can carry **ground truth** instead of
an eyeballed guess.

It is a faithful port of the `dataviz` skill's `validate_palette.js` (same
thresholds, same Machado-2009 colorblind transforms), so vizier and that skill never
disagree on a verdict. vizier owns the *computable* half in code; when the skill is
present, its `references/*` are the canonical long-form prose.

## Why this, and why it should move the numbers

vizier's own `PRINCIPLES.md` names **structural-risk identification** as the
highest-leverage axis, and lists *"color-only encoding in grayscale-hostile
contexts"* as a structural risk it currently judges only by eye. A measured ΔE is
the sharpest possible version of exactly that finding — maximally *specific*
(`#2563a8↔#6b4ea8 ΔE 1.5 under deuteranopia`) and *actionable* (`re-derive to
ΔE ≥ 12`), which are two of the four judge axes. The signal is correct by
construction, so the LLM can't fake or soften it.

## What was added

| Piece | Where | What it does |
|---|---|---|
| Color math | `src/vizier/analyze/color.py` | OKLCH lightness/chroma, Machado-2009 CVD ΔE, WCAG contrast, ordinal-ramp checks. `validate_categorical` / `validate_ordinal` / `contrast`. |
| Extraction | `src/vizier/analyze/extract.py` | Pull exact hexes from **SVG/HTML source** and split chromatic data colors from achromatic chrome via the chroma floor. (A raster image can't give exact colors — this is the one path that can.) |
| Findings bridge | `src/vizier/analyze/findings.py` | Render a report as critique-ready evidence, translating each hard fail into vizier's structural-risk language. |
| CLI | `vizier validate "#..,#.." [--pairs all\|adjacent] [--ordinal]` · `vizier analyze chart.svg` | Standalone, deterministic, no LLM. Exit 1 on hard FAIL. |
| MCP tools | `validate_palette`, `check_contrast`, `analyze_artifact` (`mcp_server.py`) | Any project can call vizier for a computed check — dogfoodable from Claude Code. |
| Critique wiring | `informed.py` (case `palette:` / `artifact_svg_path:` frontmatter) · `adhoc.py` (`--palette`) | Injects a "Computed color findings" block as ground truth + surfaces it in output. `meta.computed_color_findings` records provenance. |
| Method rubric | `ingest/rubrics.py` → `corpus/rubrics/dataviz-method.md` | The dataviz method (form heuristic + six checks + anti-pattern catalog) as an always-included rubric; folds a few anti-patterns into `line-chart` / `bar-chart` `common_mistakes`. |

## Generation side — the full-service half

The checks run in reverse: the thresholds that *judge* a palette also *generate*
one that passes. `src/vizier/analyze/generate.py` adds the generation primitives,
so a renderer (weaver, or any agent) asks vizier for correct colors instead of
rolling its own:

| Primitive | CLI | MCP | Returns |
|---|---|---|---|
| Categorical palette | `vizier suggest-palette 6 [--theme muted]` | `suggest_palette` | `n` CVD-safe hues, validated before return (n>8 refused) |
| Ordinal ramp | `vizier suggest-ramp 5 --hue navy` | `suggest_ramp` | a one-hue ramp that passes, or a clear error if infeasible |
| Legible ink | `vizier ink "#0072b2"` | `ink_on` | the dark/light text color that clears WCAG on a fill |

Guarantee: **what vizier suggests is what vizier would pass** — every returned asset
is validated by the same `color` checks first (`tests/test_generate.py`, 6/6). A
request that can't be satisfied (a 9th categorical hue, too many ordinal steps for
a warm hue) raises rather than returning something that fails.

This is the surface **weaver calls at generation time**, over MCP, rather than
duplicating the color math — see `PRINCIPLES.md` → "Generation and critique are one
expertise." The corpus-backed judgment stays critique-side and LLM-mediated; only
the computed part crosses into generation.

## With vs without the `dataviz` skill

- **Engine is vizier's own Python** — no node, no skill dependency. The computed
  verdict is available in every environment.
- **Prose defers when the skill is present.** The `dataviz-method` rubric says so
  explicitly: cite `references/{choosing-a-form,color-formula,anti-patterns,…}.md`
  as canonical long-form when available; the rubric is the portable subset.
- Thresholds are identical, so a palette that passes `vizier validate` passes the
  skill's validator and vice-versa.

## Measuring the lift

A self-contained capability case ships at `evals/cases/color-cvd-stacked-area.md`:
a 7-category stacked area with a palette that fails CVD (the njschooldata
pre-fix palette), carrying inline `ground_truth` (a new `ground_truth_source:
inline` mode in `judge.py`). Its `palette:` frontmatter makes the informed run
inject computed findings; naive gets none.

```bash
uv run vizier eval full          # naive vs informed(+computed) across all cases, judged n=3
uv run vizier eval results       # reprint the latest judge summary
```

Expected shape: on this case the informed critique should name the exact failing
pair + ΔE and the sub-chroma-floor grays, where naive gives generic "consider
colorblind users" advice — a large structural-risk / specificity delta. The other
13 cases have no `palette:` frontmatter, so their behavior is unchanged (the
computed block only fires when exact colors are available).

**Cleaner isolation — measured.** `evals/experiments/computed_color_ab.py` runs the
informed critique on this case WITH vs WITHOUT the computed block, corpus held
constant, judged n=3 against the inline ground truth (`eval full` conflates the
computed lift with the corpus lift; this doesn't):

| axis | without computed | with computed | Δ |
|---|---|---|---|
| alignment | 2 | 5 | **+3** |
| specificity | 4 | 5 | +1 |
| actionability | 5 | 5 | 0 |
| structural_risk | 4 | 5 | +1 |

Winner: with-computed. The with-computed critique names ΔE, deuteranopia, the
`#2563a8`↔`#6b4ea8` pair, and the chroma floor; without it, the critique manages
only a generic "ΔE." The headline is **alignment 2→5** — without the measured block
the critique (even with the corpus) didn't identify the actual CVD failure. Single
case, single judge (gemini), n=3, fixed A/B order — a demonstration, but the effect
(+3) is far outside judge noise (±0.3/axis). Re-run: `uv run python
evals/experiments/computed_color_ab.py`.

> Note: running the eval needs `somm`'s providers configured (`somm status
> --project vizier`). The deterministic layer (`vizier validate`, `analyze`, the MCP
> tools, `tests/test_color.py`) needs no network and no somm.

## Tests

`tests/test_color.py` asserts parity with the JS validator on the njschooldata
palettes (contrast values, the ΔE 1.5 deutan collapse, the chroma-floor trio, the
ordinal light-end). Run: `uv run python tests/test_color.py`.

## Known limits / follow-ups

- **Raster input can't give exact colors.** Computed findings fire for SVG/HTML
  source, an explicit `--palette`, or case frontmatter — not from a PNG. Sampling a
  palette from a raster (Pillow quantize / k-means) is the natural next step, and
  pairs with the deferred SVG-rasterization work in the chart-forms roadmap.
- **A gray used as a real data series** lands in the "achromatic/chrome" bucket
  during extraction — the split is a starting point, not an oracle (noted in the
  output).
- **Anti-patterns folded into patterns** is a seed (`line-chart`, `bar-chart`); the
  full catalog lives in the `dataviz-method` rubric. Distributing the rest across
  the 43 patterns' `common_mistakes` is incremental corpus work.
