"""Informed critique — retrieves corpus + applies named rubrics.

Difference from `naive`:

- System prompt names the rubrics and tells the critic to work axis-
  by-axis (Cairo 5-pillars).
- User message includes: the artifact description, the full weaver
  principles + rubrics (always), and tag-matched items from sigma,
  kantar, junkcharts, pudding.
- Output stamps `rubric_set`, `retrieval_summary`, and `corpus_hash`
  so naive and informed runs can be diff'd per case.

Uses `somm` as the LLM substrate (same as naive), workload
`critique_informed`. Routing and telemetry identical to naive.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import somm
from dotenv import load_dotenv

from .. import manifest as manifest_mod
from .. import vision as V
from ..llm import generate_resilient
from . import retrieve as R
from . import styles as S

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

CASES_DIR = Path(__file__).resolve().parents[3] / "evals" / "cases"
RUNS_DIR = Path(__file__).resolve().parents[3] / "evals" / "runs"

# Default to Gemini 2.5 Pro via the Gemini API — free tier covers vizier's
# eval volume. Paid models (Opus 4.7 via OpenRouter, etc.) are opt-in
# via `--model` / `--provider` at the CLI or via run() kwargs.
MODEL = "gemini-2.5-pro"
DEFAULT_PROVIDER: str | None = "gemini"
WORKLOAD = "critique_informed"
PROJECT = "vizier"
BASE_RUBRIC_SET = ("weaver", "cairo-5-pillars", "ft-visual-vocabulary")
DEFAULT_STYLE = "multi"

SYSTEM = """\
You are an information-design critic trained in the tradition of \
practitioners who work at the top of the field — the Financial Times \
visual-journalism team, the New York Times graphics desk, Alberto \
Cairo's Truthful Art framework, and the Junk Charts school of \
structural critique.

You will be given:

1. A textual description of the artifact being critiqued.
2. **Rubrics** — Cairo's 5-pillar framework (Truthful → Functional → \
Beautiful → Insightful → Enlightening) and the FT Visual Vocabulary \
(9 chart families × sub-types for selecting the right form for the \
comparison being made).
3. **Internal principles** — a lived rubric distilled from real \
projects, covering chart-form fit, coherent narrative structure, \
uncertainty handling, interaction defaults, glossaries, and audience \
calibration. Treat these as high-signal heuristics, not rules.
4. **Retrieved prior art** — comparable award-winning and critique \
work from Sigma Awards, Kantar IIB, Junk Charts, and Pudding. Cite \
them by short title when a specific piece informs your judgment.

Work Cairo's pillars as axes, in order:

- **Truthful**: does the chart say anything the data can't support? \
Name the counter-narratives it *fails* to rule out, not the generic \
ones.
- **Functional**: does the chart form match the licit comparisons? \
Is the encoding perceptually fit for the audience's task? Use the FT \
Visual Vocabulary to name the family and, if applicable, propose a \
better sub-type.
- **Beautiful**: is the aesthetic serving comprehension or competing \
with it? Would the target audience linger?
- **Insightful**: does the reader leave knowing something they \
couldn't see in the raw data? If not, what would bring the insight \
closer to the surface?
- **Enlightening**: does the subject matter justify the reader's \
attention?

Additional structural risks to always check:

- Hidden denominators / cut-date mismatches that bias trend readings.
- Near-deterministic columns that compress a sankey's story into \
noise.
- Survey data without visible uncertainty.
- Interaction defaults (tabs, dropdowns) that gate summary-level \
comparisons behind clicks.
- Color-only encoding that fails grayscale or colorblind audiences.
- Jargon labels that assume the reader's prior knowledge exceeds the \
stated audience.

Be specific. Cite the retrieved prior art where relevant (e.g., \
"Reuters 2022 Shahed year showed the same reader's task with a \
different form …"). Do not recite Cairo's pillar names without \
applying them. Call out where the description is thin, and say what \
you would need to see in the artifact to resolve that question.\
"""


def _case_paths() -> list[Path]:
    return sorted(CASES_DIR.glob("*.md"))


def _load_case(path: Path) -> dict:
    post = frontmatter.load(str(path))
    data = dict(post.metadata)
    data["body"] = post.content
    data["_path"] = path
    return data


def _computed_findings_for_case(case: dict) -> str | None:
    """If a case carries an explicit `palette` or an `artifact_svg_path`, run the
    deterministic color checks and return a critique-ready findings block. This is
    the one place a vizier critique carries measured ground truth rather than an
    LLM/vision guess. Optional `chart_mode` / `chart_surface` frontmatter tune it."""
    from ..analyze.findings import computed_color_findings
    markup = None
    svgp = case.get("artifact_svg_path")
    if svgp:
        p = Path(svgp)
        if not p.is_absolute():
            p = case["_path"].parent / svgp
        if p.exists():
            markup = p.read_text(encoding="utf-8", errors="ignore")
    return computed_color_findings(
        palette=case.get("palette"),
        markup=markup,
        mode=case.get("chart_mode", "light"),
        surface=case.get("chart_surface"),
    )


def _build_user_prompt(case: dict, context: str, caption: V.Caption | None = None,
                       computed: str | None = None) -> str:
    parts = [f"# Artifact: {case['artifact_title']}\n\n{case['body']}"]
    if caption is not None:
        parts.append(
            "---\n\n"
            "# What the vision captioner saw\n\n"
            f"_Produced by `{caption.model}` on a screenshot of the artifact. "
            "Treat as an imperfect witness, not ground truth — caption "
            "inaccuracies should be visible in the critique's observations._\n\n"
            f"{caption.text}"
        )
    if computed:
        parts.append(
            "---\n\n"
            "# Computed color findings (deterministic ground truth)\n\n"
            "_Measured from the artifact's exact colors, not inferred from the image — "
            "correct by construction. Treat as evidence, not opinion; fold any failures "
            "into your structural-risk assessment and cite the numbers._\n\n"
            f"{computed}"
        )
    parts.extend([
        "---\n\n# Rubrics and prior art\n\n" + context,
        "---\n\n"
        "# Your critique\n\n"
        "Work Cairo's five pillars in order, then call out any "
        "structural risks you'd flag in a newsroom review. Cite "
        "retrieved prior art by short title when it sharpens a "
        "point. End with 3–5 concrete suggestions a designer could "
        "act on.",
    ])
    return "\n\n".join(parts)


def _critique_one(
    llm: somm.SommLLM,
    case: dict,
    style: S.Style,
    *,
    resilient: bool = False,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
    use_vision: bool = True,
    vision_backend: str = V.DEFAULT_BACKEND,
) -> tuple[str, dict]:
    retrieval = R.retrieve(case)
    context = R.format_for_prompt(retrieval)
    ctx_tokens = R.token_estimate(context)

    cap: V.Caption | None = V.caption_for_case(case, backend=vision_backend) if use_vision else None
    computed = _computed_findings_for_case(case)
    user_prompt = _build_user_prompt(case, context, caption=cap, computed=computed)
    system_prompt = SYSTEM + style.addendum
    t0 = datetime.now(timezone.utc)
    fallback_trace: list[dict] | None = None
    if resilient:
        rr = generate_resilient(
            llm,
            prompt=user_prompt,
            system=system_prompt,
            workload=WORKLOAD,
            max_tokens=16000,
            temperature=0.3,
        )
        result = rr.result
        fallback_trace = rr.fallback_trace
    else:
        result = llm.generate(
            prompt=user_prompt,
            system=system_prompt,
            workload=WORKLOAD,
            max_tokens=16000,
            temperature=0.3,
            model=model,
            provider=provider,
        )
    t1 = datetime.now(timezone.utc)
    meta = {
        "call_id": result.call_id,
        "provider": result.provider,
        "model": result.model,
        "duration_seconds": (t1 - t0).total_seconds(),
        "tokens_in": result.tokens_in,
        "tokens_out": result.tokens_out,
        "cost_usd": result.cost_usd,
        "outcome": getattr(result.outcome, "value", str(result.outcome)),
        "context_tokens_estimate": ctx_tokens,
        "retrieval_summary": retrieval["retrieval_summary"],
        "computed_color_findings": bool(computed),
    }
    if fallback_trace is not None:
        meta["fallback_trace"] = fallback_trace
        meta["fallback_attempts"] = len(fallback_trace)
    if cap is not None:
        meta["vision_caption"] = {
            "backend": cap.backend,
            "model": cap.model,
            "sha": cap.sha,
            "prompt_version": cap.prompt_version,
            "duration_s": round(cap.duration_s, 2),
            "image_bytes": cap.image_bytes,
            "source_path": cap.source_path,
            "cached": cap.cached,
            "caption_chars": len(cap.text),
        }
    return result.text.strip(), meta


def _write_output(
    run_dir: Path,
    case: dict,
    critique: str,
    meta: dict,
    corpus_hash: str,
    rubric_set: list[str],
    style_name: str,
) -> Path:
    post = frontmatter.Post(
        critique,
        case_id=case["id"],
        case_kind=case["source_kind"],
        artifact_title=case["artifact_title"],
        artifact_url=case.get("artifact_url"),
        ground_truth_source=case.get("ground_truth_source"),
        critique_kind="informed",
        style=style_name,
        corpus_hash=corpus_hash,
        rubric_set=rubric_set,
        run_at=datetime.now(timezone.utc).isoformat(),
        somm_call_id=meta["call_id"],
        provider=meta["provider"],
        model=meta["model"],
        duration_seconds=round(meta["duration_seconds"], 2),
        tokens_in=meta["tokens_in"],
        tokens_out=meta["tokens_out"],
        cost_usd=meta["cost_usd"],
        outcome=meta["outcome"],
        context_tokens_estimate=meta["context_tokens_estimate"],
        retrieval_summary=meta["retrieval_summary"],
    )
    out_path = run_dir / f"{case['id']}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
    return out_path


def run(
    *,
    style: str = DEFAULT_STYLE,
    resilient: bool = False,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
    use_vision: bool = True,
    vision_backend: str = V.DEFAULT_BACKEND,
) -> dict:
    cases = [_load_case(p) for p in _case_paths()]
    if not cases:
        raise RuntimeError(f"no cases found in {CASES_DIR}")

    style_obj = S.resolve(style)
    rubric_set = list(BASE_RUBRIC_SET) + list(style_obj.rubric_tags)

    corpus_state = manifest_mod.build()
    corpus_hash = corpus_state["corpus_hash"]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = "informed" if style == DEFAULT_STYLE else f"informed-{style}"
    # Suffix with a short model tag so side-by-side runs (opus vs gemini)
    # don't collide in the directory listing.
    model_tag = _short_model_tag(model)
    if model_tag:
        suffix = f"{suffix}-{model_tag}"
    run_dir = RUNS_DIR / f"{ts}-{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)

    llm = somm.llm(project=PROJECT)
    try:
        results: list[dict] = []
        for case in cases:
            print(f"  → {case['id']}", flush=True)
            critique, meta = _critique_one(
                llm, case, style_obj,
                resilient=resilient, model=model, provider=provider,
                use_vision=use_vision, vision_backend=vision_backend,
            )
            _write_output(run_dir, case, critique, meta, corpus_hash, rubric_set, style)
            results.append({
                "case_id": case["id"],
                "call_id": meta["call_id"],
                "provider": meta["provider"],
                "model": meta["model"],
                "duration_seconds": round(meta["duration_seconds"], 2),
                "tokens_in": meta["tokens_in"],
                "tokens_out": meta["tokens_out"],
                "cost_usd": meta["cost_usd"],
                "outcome": meta["outcome"],
                "context_tokens_estimate": meta["context_tokens_estimate"],
            })
    finally:
        llm.close()

    index = {
        "critique_kind": "informed",
        "style": style,
        "model": model,
        "provider": provider,
        "workload": WORKLOAD,
        "project": PROJECT,
        "corpus_hash": corpus_hash,
        "rubric_set": rubric_set,
        "run_at": ts,
        "total_cases": len(results),
        "cases": results,
    }
    (run_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return {"run_dir": str(run_dir), "cases": len(results)}


def _short_model_tag(model: str) -> str:
    """Short directory-safe tag for a model string, used to suffix run dirs.

    Turns "anthropic/claude-opus-4.7" → "opus-4-7"
    and   "gemini-2.5-pro" → "gemini-2-5-pro"
    so parallel runs on different models don't collide.
    """
    if not model or model == MODEL:
        return ""
    tail = model.rsplit("/", 1)[-1]
    return tail.replace(".", "-").replace(":", "-").replace(" ", "-").lower()


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
