"""Naive critique — plain LLM, no corpus, no rubric.

Baseline for tracking whether vizier's informed critiques add value. The
prompt deliberately avoids weaver/FT/Cairo language — we want to see
what the base model produces without any of vizier's specific insights.

Uses `somm` as the LLM substrate:

- Every call lands in `.somm/calls.sqlite` with project `vizier` and
  workload `critique_naive` — queryable via `somm status`, `somm tail`,
  and the MCP tools.
- Model and provider are chosen via somm's router. We pass
  `model="claude-opus-4-7"` so the baseline uses the strongest
  Anthropic model; if that fails, somm falls back through its chain.

Per-case output lands in `evals/runs/<timestamp>-naive/<case-id>.md`.
Each output records the somm call_id, corpus_hash, and token usage,
so informed critique runs (future) can be diffed against the exact
corpus state and LLM call provenance.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import frontmatter
import somm
from dotenv import load_dotenv

from .. import manifest as manifest_mod

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

CASES_DIR = Path(__file__).resolve().parents[3] / "evals" / "cases"
RUNS_DIR = Path(__file__).resolve().parents[3] / "evals" / "runs"

# Default to Gemini 2.5 Pro via the Gemini API (free tier). Keeps
# every `vizier eval naive` run at zero cost. Paid models (Opus 4.7 via
# OpenRouter, etc.) must be opted into explicitly.
MODEL = "gemini-2.5-pro"
DEFAULT_PROVIDER: str | None = "gemini"
WORKLOAD = "critique_naive"
PROJECT = "vizier"

SYSTEM = """\
You are critiquing a data visualization. You will be given a textual \
description of the artifact — its subject, encoding, chart form, \
interactive behavior, audience, and surrounding context. Work only from \
the description; do not assume images are available.

Produce a specific, concrete critique. Call out:

- What the graphic appears to do well.
- What could be improved.
- Any structural risk (misreadings the chart form invites, comparisons \
the data cannot support, encodings at odds with the audience's task).
- Concrete suggestions a designer could act on.

Be honest about uncertainty: if the description is thin in a relevant \
area, say so. Avoid generic advice — critique this specific artifact.\
"""


def _case_paths() -> list[Path]:
    return sorted(CASES_DIR.glob("*.md"))


def _load_case(path: Path) -> dict:
    post = frontmatter.load(str(path))
    data = dict(post.metadata)
    data["body"] = post.content
    data["_path"] = path
    return data


def _build_user_prompt(case: dict) -> str:
    return f"# Artifact: {case['artifact_title']}\n\n{case['body']}"


def _critique_one(
    llm: somm.SommLLM,
    case: dict,
    *,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
) -> tuple[str, dict]:
    prompt = _build_user_prompt(case)
    t0 = datetime.now(timezone.utc)
    result = llm.generate(
        prompt=prompt,
        system=SYSTEM,
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
    }
    return result.text.strip(), meta


def _write_output(
    run_dir: Path,
    case: dict,
    critique: str,
    meta: dict,
    corpus_hash: str,
) -> Path:
    post = frontmatter.Post(
        critique,
        case_id=case["id"],
        case_kind=case["source_kind"],
        artifact_title=case["artifact_title"],
        artifact_url=case.get("artifact_url"),
        ground_truth_source=case.get("ground_truth_source"),
        critique_kind="naive",
        corpus_hash=corpus_hash,
        rubric_set=[],
        run_at=datetime.now(timezone.utc).isoformat(),
        somm_call_id=meta["call_id"],
        provider=meta["provider"],
        model=meta["model"],
        duration_seconds=round(meta["duration_seconds"], 2),
        tokens_in=meta["tokens_in"],
        tokens_out=meta["tokens_out"],
        cost_usd=meta["cost_usd"],
        outcome=meta["outcome"],
    )
    out_path = run_dir / f"{case['id']}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
    return out_path


def iter_runs() -> Iterator[Path]:
    """Yield run directories in chronological order."""
    if not RUNS_DIR.exists():
        return
    for p in sorted(RUNS_DIR.iterdir()):
        if p.is_dir():
            yield p


def run(*, model: str = MODEL, provider: str | None = DEFAULT_PROVIDER) -> dict:
    """Run naive critique across every case in evals/cases/.

    Returns the run directory path and per-case outcomes.
    """
    cases = [_load_case(p) for p in _case_paths()]
    if not cases:
        raise RuntimeError(f"no cases found in {CASES_DIR}")

    corpus_state = manifest_mod.build()
    corpus_hash = corpus_state["corpus_hash"]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_DIR / f"{ts}-naive"
    run_dir.mkdir(parents=True, exist_ok=True)

    llm = somm.llm(project=PROJECT)
    try:
        results: list[dict] = []
        for case in cases:
            print(f"  → {case['id']}", flush=True)
            critique, meta = _critique_one(llm, case, model=model, provider=provider)
            _write_output(run_dir, case, critique, meta, corpus_hash)
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
            })
    finally:
        llm.close()

    index = {
        "critique_kind": "naive",
        "model": MODEL,
        "workload": WORKLOAD,
        "project": PROJECT,
        "corpus_hash": corpus_hash,
        "rubric_set": [],
        "run_at": ts,
        "total_cases": len(results),
        "cases": results,
    }
    (run_dir / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return {"run_dir": str(run_dir), "cases": len(results)}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
