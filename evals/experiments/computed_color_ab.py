"""Focused A/B: does the computed-color-findings layer sharpen the critique?

Runs the informed critique on the color-CVD case WITH vs WITHOUT the injected
"Computed color findings" block — corpus retrieval is identical for both, so the
only difference is whether vizier hands the model the measured ground truth — then
judges the two (median of n) against the case's inline ground truth. This isolates
the computed layer's contribution, which `eval full` (naive vs informed) conflates
with the corpus lift.

    uv run python evals/experiments/computed_color_ab.py [n]
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")  # exactly what `vizier eval` does — puts GEMINI_API_KEY in the env

import somm  # noqa: E402
from vizier.critique import informed as I, judge as J, styles as S  # noqa: E402

CASE = ROOT / "evals" / "cases" / "color-cvd-stacked-area.md"
MODEL, PROVIDER = "gemini-2.5-pro", "gemini"   # free-tier; the working provider here
AXES = ["alignment", "specificity", "actionability", "structural_risk"]
PROBES = ("ΔE", "deuteran", "1.5", "#2563a8", "#6b4ea8", "chroma")


def _names(text: str) -> list[str]:
    t = text.lower()
    return [p for p in PROBES if p.lower() in t]


def main(n: int = 3) -> None:
    case = I._load_case(CASE)
    case_no = {**case, "palette": None, "artifact_svg_path": None}  # suppress computed block
    llm = somm.SommLLM(project="vizier")
    style = S.resolve("multi")
    kw = dict(use_vision=False, model=MODEL, provider=PROVIDER)

    print("→ informed WITHOUT computed findings…")
    text_a, _ = I._critique_one(llm, case_no, style, **kw)
    print("→ informed WITH computed findings…")
    text_b, meta = I._critique_one(llm, case, style, **kw)
    print(f"  computed fired: {meta.get('computed_color_findings')}")

    print(f"→ judging n={n}  (A = without, B = with)…")
    j, _raws, jm = J._judge_one_median(llm, case, text_a, text_b, n=n, model=MODEL, provider=PROVIDER)
    if j is None:
        print("judge produced no parseable verdict:", jm)
        return

    print("\n  axis                A(without)  B(with)   Δ(B−A)")
    for ax in AXES:
        a, b = getattr(j.a, ax), getattr(j.b, ax)
        print(f"  {ax:<18} {a:>7}     {b:>5}    {b - a:+d}")
    print(f"\n  winner: {j.winner}   (A = without-computed, B = with-computed)")
    print(f"  with-computed critique names:    {_names(text_b) or '(none)'}")
    print(f"  without-computed critique names: {_names(text_a) or '(none)'}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
