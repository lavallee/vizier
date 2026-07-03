"""LLM judge — compare two critique runs per case against ground truth.

For each case with matching outputs in both runs, the judge sees:

- The artifact description.
- Ground truth (lookup rules below).
- Critique A and Critique B (anonymized to A/B, order randomized per
  case so the model can't learn a positional bias).

Judge emits structured scores (1–5) on: alignment with ground truth,
specificity, actionability, structural-risk identification; plus a
short rationale and a winner (A / B / tie).

Ground truth resolution:
- `weaver-notes` → reads the sibling project's `notes.md` from the
  weaver repo (unseen by the critiquing model by design).
- `sigma-jury` → reads the jury commentary from the matching corpus
  item (by slugified artifact title + year).
- `junkcharts-critique` → reads the matching Junk Charts corpus
  item's body.
- `kantar-jury` → reads the jury quote from the matching Kantar
  corpus item.

Output lands in `evals/judge/<timestamp>/<case-id>.md` per case and
an aggregate `index.json` with per-case winners and overall score
deltas.
"""

from __future__ import annotations

import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import somm
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .. import manifest as manifest_mod
from ..ingest._common import slugify
from ..storage import iter_items

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

CASES_DIR = Path(__file__).resolve().parents[3] / "evals" / "cases"
RUNS_DIR = Path(__file__).resolve().parents[3] / "evals" / "runs"
JUDGE_DIR = Path(__file__).resolve().parents[3] / "evals" / "judge"
WEAVER_PROJECTS = Path(__file__).resolve().parents[4] / "weaver" / "projects"

# Default judge on free tier (Gemini 2.5 Pro). Gemini emits JSON
# cleanly and in the one Opus-vs-Gemini-critique measurement the
# Gemini judge agreed with Opus judge on the winner — unbiased enough
# as a default. Override with --model / --provider for rigor checks.
MODEL = "gemini-2.5-pro"
DEFAULT_PROVIDER: str | None = "gemini"
WORKLOAD = "critique_judge"
PROJECT = "vizier"

SYSTEM = """\
You are comparing two critiques (A and B) of the same data \
visualization artifact against a ground-truth assessment. Your job \
is to judge each critique's *quality*, not its aesthetics.

You will score each critique on four axes (1–5 scale):

1. **Alignment with ground truth** — does it identify the same \
structural issues the ground truth flags? Partial credit for \
catching some. Penalize critiques that hallucinate issues the \
ground truth says are actually handled, or that miss issues the \
ground truth names explicitly.

2. **Specificity** — does the critique refer to *this* artifact's \
specific choices (chart form, encoding, labels, audience), or could \
it be applied verbatim to any data visualization? Generic advice \
scores low.

3. **Actionability** — would a designer reading this know what to \
change, and why? A critique that ends with "make it clearer" scores \
low; one that names a specific alternative form or encoding scores \
high.

4. **Structural risk identification** — does the critique name \
risks that the chart form, encoding, or interaction model creates \
for a cold reader? This is distinct from alignment: some risks are \
in the ground truth, some aren't but should be.

Then pick a winner: `"A"`, `"B"`, or `"tie"`. Tie only when the \
critiques are genuinely equivalent in quality. Explain in one \
paragraph what differentiated them.

Respond with JSON matching the schema provided. No prose outside \
the JSON.\
"""


class AxisScores(BaseModel):
    alignment: int = Field(..., ge=1, le=5)
    specificity: int = Field(..., ge=1, le=5)
    actionability: int = Field(..., ge=1, le=5)
    structural_risk: int = Field(..., ge=1, le=5)


class Judgment(BaseModel):
    a: AxisScores
    b: AxisScores
    winner: str = Field(..., pattern="^(A|B|tie)$")
    rationale: str


def _load_case(case_id: str) -> dict:
    path = CASES_DIR / f"{case_id}.md"
    post = frontmatter.load(str(path))
    data = dict(post.metadata)
    data["body"] = post.content
    return data


def _load_run_outputs(run_dir: Path) -> dict[str, dict]:
    """Return {case_id: {text, metadata}} for every .md output."""
    out: dict[str, dict] = {}
    for p in sorted(run_dir.glob("*.md")):
        post = frontmatter.load(str(p))
        out[str(post.metadata.get("case_id") or p.stem)] = {
            "text": post.content,
            "metadata": dict(post.metadata),
            "path": str(p),
        }
    return out


def _ground_truth_weaver(case: dict) -> str | None:
    # Case id looks like "weaver-<slug>". Try exact, then prefix match
    # (e.g., case "weaver-new-bern" → dir "new-bern-profile").
    project = re.sub(r"^weaver-", "", case["id"])
    path = WEAVER_PROJECTS / project / "notes.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    for p in WEAVER_PROJECTS.iterdir():
        if not p.is_dir():
            continue
        if (p.name == project or p.name.startswith(project + "-") or project.startswith(p.name + "-")) \
                and (p / "notes.md").exists():
            return (p / "notes.md").read_text(encoding="utf-8")
    return None


def _ground_truth_corpus(case: dict, source: str) -> str | None:
    """Find a corpus item whose title/url matches the case's artifact."""
    target_title = case.get("artifact_title", "")
    target_url = case.get("artifact_url", "") or ""
    target_slug = slugify(target_title)

    best = None
    for item in iter_items(source=source):
        item_slug = slugify(item.title or "")
        if item.artifact_url and item.artifact_url.rstrip("/") == target_url.rstrip("/"):
            return item.body
        if item_slug in target_slug or target_slug in item_slug:
            best = item
    if best is not None:
        return best.body
    return None


def _resolve_ground_truth(case: dict) -> str:
    src = case.get("ground_truth_source", "")
    if src == "weaver-notes":
        return _ground_truth_weaver(case) or "(weaver notes not found for this case)"
    if src == "sigma-jury":
        return _ground_truth_corpus(case, "sigma") or "(no matching Sigma corpus item)"
    if src == "junkcharts-critique":
        return _ground_truth_corpus(case, "junkcharts") or "(no matching Junk Charts post)"
    if src == "kantar-jury":
        return _ground_truth_corpus(case, "kantar") or "(no matching Kantar item)"
    if src in ("inline", "manual"):
        # Self-contained cases (e.g. computable-capability tests) carry their own
        # ground truth in a `ground_truth` frontmatter field.
        gt = case.get("ground_truth")
        if isinstance(gt, (list, tuple)):
            gt = "\n".join(str(x) for x in gt)
        return gt or "(no inline ground_truth provided)"
    return "(no ground-truth source configured)"


def _build_user_prompt(case: dict, ground_truth: str, text_a: str, text_b: str) -> str:
    schema = Judgment.model_json_schema()
    return (
        f"# Artifact: {case['artifact_title']}\n\n"
        f"{case['body']}\n\n"
        "---\n\n"
        f"# Ground truth ({case.get('ground_truth_source','unknown')})\n\n"
        f"{ground_truth}\n\n"
        "---\n\n"
        "# Critique A\n\n"
        f"{text_a}\n\n"
        "---\n\n"
        "# Critique B\n\n"
        f"{text_b}\n\n"
        "---\n\n"
        "Respond with JSON matching this schema exactly:\n\n"
        f"```json\n{json.dumps(schema, indent=2)}\n```"
    )


def _parse_judgment(text: str) -> Judgment | None:
    # Extract JSON from fenced block or raw body
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    raw = m.group(1) if m else None
    if raw is None:
        m = re.search(r"(\{.*\})", text, re.DOTALL)
        raw = m.group(1) if m else None
    if raw is None:
        return None
    # Common model tics that break strict JSON: stray `;` before the
    # closing brace, trailing commas.
    cleaned = re.sub(r";\s*\}", "}", raw)
    cleaned = re.sub(r",\s*\}", "}", cleaned)
    cleaned = re.sub(r",\s*\]", "]", cleaned)
    for candidate in (cleaned, raw):
        try:
            data = json.loads(candidate)
            return Judgment(**data)
        except Exception:
            continue
    return None


def _judge_one(
    llm: somm.SommLLM,
    case: dict,
    text_a: str,
    text_b: str,
    *,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
) -> tuple[Judgment | None, str, dict]:
    gt = _resolve_ground_truth(case)
    prompt = _build_user_prompt(case, gt, text_a, text_b)
    result = llm.generate(
        prompt=prompt,
        system=SYSTEM,
        workload=WORKLOAD,
        max_tokens=2500,
        temperature=0.1,
        model=model,
        provider=provider,
    )
    judgment = _parse_judgment(result.text)
    meta = {
        "call_id": result.call_id,
        "provider": result.provider,
        "model": result.model,
        "tokens_in": result.tokens_in,
        "tokens_out": result.tokens_out,
        "cost_usd": result.cost_usd,
        "outcome": getattr(result.outcome, "value", str(result.outcome)),
        "ground_truth_chars": len(gt),
    }
    return judgment, result.text, meta


def _median_int(xs: list[int]) -> int:
    """Integer median. On even-length input, rounds down to avoid fractional axis scores."""
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else int((xs[n // 2 - 1] + xs[n // 2]) // 2)


def _aggregate_judgments(js: list[Judgment]) -> Judgment:
    """Combine N judgments into one: median per-axis scores + majority winner.

    Tie-breaking on winner: if no strict majority, emit `tie`.
    """
    assert js, "aggregating empty judgment list"
    a_axes = AxisScores(
        alignment=_median_int([j.a.alignment for j in js]),
        specificity=_median_int([j.a.specificity for j in js]),
        actionability=_median_int([j.a.actionability for j in js]),
        structural_risk=_median_int([j.a.structural_risk for j in js]),
    )
    b_axes = AxisScores(
        alignment=_median_int([j.b.alignment for j in js]),
        specificity=_median_int([j.b.specificity for j in js]),
        actionability=_median_int([j.b.actionability for j in js]),
        structural_risk=_median_int([j.b.structural_risk for j in js]),
    )
    votes = {"A": 0, "B": 0, "tie": 0}
    for j in js:
        votes[j.winner] += 1
    # Strict majority required; otherwise tie
    top = max(votes, key=lambda k: votes[k])
    winner = top if votes[top] > len(js) // 2 else "tie"
    rationale = (
        f"aggregated from {len(js)} judgments; "
        f"winner votes={votes}. first rationale: {js[0].rationale[:500]}"
    )
    return Judgment(a=a_axes, b=b_axes, winner=winner, rationale=rationale)


def _judge_one_median(
    llm: somm.SommLLM,
    case: dict,
    text_a: str,
    text_b: str,
    *,
    n: int,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
) -> tuple[Judgment | None, list[str], dict]:
    """Run the judge N times; return aggregated judgment + raw texts + meta.

    Each individual call shows up in somm's telemetry with the usual
    workload tag. Per-run judgments are preserved in the trace so the
    aggregation can be re-derived if the median rule changes later.
    """
    judgments: list[Judgment] = []
    raws: list[str] = []
    metas: list[dict] = []
    for _ in range(n):
        j, raw, m = _judge_one(llm, case, text_a, text_b, model=model, provider=provider)
        raws.append(raw)
        metas.append(m)
        if j is not None:
            judgments.append(j)
    if not judgments:
        return None, raws, {
            "n_runs": n,
            "n_parsed": 0,
            "per_run_meta": metas,
        }
    aggregated = _aggregate_judgments(judgments) if len(judgments) > 1 else judgments[0]
    agg_meta = {
        "n_runs": n,
        "n_parsed": len(judgments),
        "winner_votes": {
            "A": sum(1 for j in judgments if j.winner == "A"),
            "B": sum(1 for j in judgments if j.winner == "B"),
            "tie": sum(1 for j in judgments if j.winner == "tie"),
        },
        "per_run_judgments": [j.model_dump() for j in judgments],
        "per_run_call_ids": [m["call_id"] for m in metas],
        "total_tokens_in": sum(m["tokens_in"] for m in metas),
        "total_tokens_out": sum(m["tokens_out"] for m in metas),
        "ground_truth_chars": metas[0].get("ground_truth_chars", 0),
        "provider": metas[0].get("provider"),
        "model": metas[0].get("model"),
    }
    return aggregated, raws, agg_meta


def run(
    run_a: str,
    run_b: str,
    *,
    n: int = 1,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
) -> dict:
    """Judge two critique runs against each other.

    run_a, run_b: run directory names under evals/runs/ (e.g.,
    "20260418T203531Z-naive" and "20260418T205521Z-informed"), or
    absolute paths.
    n: number of judge passes per case. Aggregated by median
       (per-axis scores) and majority vote (winner). N=3 cuts
       stochastic noise by ~1.7× at 3× cost; N=1 is the legacy path.
    """
    dir_a = Path(run_a) if Path(run_a).is_absolute() else RUNS_DIR / run_a
    dir_b = Path(run_b) if Path(run_b).is_absolute() else RUNS_DIR / run_b
    if not dir_a.is_dir() or not dir_b.is_dir():
        raise RuntimeError(f"run dir not found: {dir_a} / {dir_b}")

    a_outputs = _load_run_outputs(dir_a)
    b_outputs = _load_run_outputs(dir_b)
    shared = sorted(set(a_outputs) & set(b_outputs))
    if not shared:
        raise RuntimeError("no case overlap between the two runs")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = JUDGE_DIR / f"{ts}-judge"
    out_dir.mkdir(parents=True, exist_ok=True)

    llm = somm.llm(project=PROJECT)
    corpus_hash = manifest_mod.build()["corpus_hash"]

    rng = random.Random(hash(ts))
    per_case: list[dict] = []
    totals = {"A": 0, "B": 0, "tie": 0, "parse_fail": 0}
    # Track scores by the underlying run (naive/informed), not the shuffled A/B
    # label the judge sees — otherwise means reflect shuffle noise, not runs.
    axes = ("alignment", "specificity", "actionability", "structural_risk")
    axis_sums_by_run = {dir_a.name: {ax: 0 for ax in axes}, dir_b.name: {ax: 0 for ax in axes}}
    scored_count = 0

    try:
        for case_id in shared:
            case = _load_case(case_id)
            text_a_raw = a_outputs[case_id]["text"]
            text_b_raw = b_outputs[case_id]["text"]

            # Randomize which physical run is labeled A vs B per case
            flip = rng.random() < 0.5
            label_a_source = dir_b.name if flip else dir_a.name
            label_b_source = dir_a.name if flip else dir_b.name
            text_for_a = text_b_raw if flip else text_a_raw
            text_for_b = text_a_raw if flip else text_b_raw

            print(f"  → {case_id}  (A={label_a_source}, B={label_b_source})  n={n}", flush=True)
            if n > 1:
                judgment, raws, meta = _judge_one_median(
                    llm, case, text_for_a, text_for_b, n=n,
                    model=model, provider=provider,
                )
                raw = "\n\n---\n\n".join(raws)
            else:
                judgment, raw, meta = _judge_one(
                    llm, case, text_for_a, text_for_b,
                    model=model, provider=provider,
                )

            if judgment is None:
                totals["parse_fail"] += 1
                status = "parse_fail"
                winner_source = None
            else:
                # Map A/B winner back to the underlying run source
                if judgment.winner == "A":
                    winner_source = label_a_source
                    totals[_side(label_a_source, dir_a.name, dir_b.name)] += 1
                elif judgment.winner == "B":
                    winner_source = label_b_source
                    totals[_side(label_b_source, dir_a.name, dir_b.name)] += 1
                else:
                    winner_source = "tie"
                    totals["tie"] += 1
                status = "ok"
                scored_count += 1
                # The judgment's `a` / `b` scores describe the shuffled labels.
                # Map them back through label_a_source / label_b_source so we
                # aggregate per underlying run.
                for side_letter, ax_scores, run_name in (
                    ("A", judgment.a, label_a_source),
                    ("B", judgment.b, label_b_source),
                ):
                    for axis in axes:
                        axis_sums_by_run[run_name][axis] += getattr(ax_scores, axis)

            # Write per-case judgment file
            post = frontmatter.Post(
                raw,
                case_id=case_id,
                status=status,
                run_a=dir_a.name,
                run_b=dir_b.name,
                label_a_source=label_a_source,
                label_b_source=label_b_source,
                winner_source=winner_source,
                corpus_hash=corpus_hash,
                **({"judgment": judgment.model_dump()} if judgment else {}),
                **meta,
            )
            (out_dir / f"{case_id}.md").write_text(
                frontmatter.dumps(post) + "\n", encoding="utf-8"
            )
            per_case.append({
                "case_id": case_id,
                "status": status,
                "winner_source": winner_source,
                "judgment": judgment.model_dump() if judgment else None,
                **meta,
            })
    finally:
        llm.close()

    index = {
        "judge_at": ts,
        "judge_n": n,
        "judge_model": model,
        "judge_provider": provider,
        "run_a": dir_a.name,
        "run_b": dir_b.name,
        "corpus_hash": corpus_hash,
        "totals_by_winner": {
            dir_a.name: totals["A"],
            dir_b.name: totals["B"],
            "tie": totals["tie"],
            "parse_fail": totals["parse_fail"],
        },
        "mean_axis_scores": {
            run_name: {axis: (sums[axis] / max(1, scored_count)) for axis in axes}
            for run_name, sums in axis_sums_by_run.items()
        },
        "axis_delta_b_minus_a": {
            axis: (
                (axis_sums_by_run[dir_b.name][axis] - axis_sums_by_run[dir_a.name][axis])
                / max(1, scored_count)
            )
            for axis in axes
        },
        "cases": per_case,
    }
    (out_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return {"judge_dir": str(out_dir), "totals": totals}


def _side(winner_dir_name: str, a_dir_name: str, b_dir_name: str) -> str:
    """Return which run 'won' using the run's name as an identity label.

    The judge's `winner` field is A/B on the *judge-side* labels (shuffled).
    We map back through `label_a_source` / `label_b_source` to identify
    the actual underlying run, then attribute the win to whichever run
    that is.
    """
    if winner_dir_name == a_dir_name:
        return "A"
    if winner_dir_name == b_dir_name:
        return "B"
    return "tie"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("usage: python -m vizier.critique.judge <run-a> <run-b> [n=1]")
        sys.exit(2)
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print(json.dumps(run(sys.argv[1], sys.argv[2], n=n), indent=2))
