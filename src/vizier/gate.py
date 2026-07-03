"""vizier.gate — adaptive "does this need data visuals?" gate.

Commissioned 2026-05-06 to support the upstream → weaver pipeline. The
orchestrator asks vizier whether a piece warrants chart authoring before
committing to the cost of producing charts.

Input: a upstream reporting-bundle (with `draft/annotations.json` from the
compositor agent that proposed candidate charts).
Output: a structured decision — yes/no, kept candidates, dropped
candidates with reasons. Each kept candidate is a vizier/chart-spec/v1
ready to be authored.

The gate uses vizier's existing taste-discovery infrastructure where
available (the `informed` critique path); for now it leans on a focused
LLM call against vizier's house principles plus the compositor's
candidate proposals. Promotion to retrieval-grounded judgment is a
follow-up.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from somm import SommLLM


WORKLOAD = "vizier_gate"

# Vizier's taste posture in a single block. Pulled from vizier/PRINCIPLES.md
# tone — kept tight so the gate stays a fast call.
HOUSE_TASTE = """\
Vizier's posture on charts in a research-review piece:

- A chart earns its place when it changes a reader's decision or carries a
  comparison the prose can't. Every axis exists to be looked at; every line
  exists to be compared.
- Decorative or "look how much data we have" charts fail. So do charts that
  restate one number the prose already gave precisely.
- Cost-over-time, before/after metrics, distributional evidence, and
  timeline-of-events are usually keepers. Static "ecosystem" diagrams,
  funnel diagrams without numbers, and word clouds usually fail.
- Two strong charts beat five middling ones. A piece can also have zero;
  not every research review needs a figure.
- Prefer the chart type that matches the comparison: line for change,
  bar for level, dot for distribution, sankey for flow, timeline for events.
- If the dossier doesn't actually contain the numbers the chart would
  show, the chart can't be authored — drop it.
"""


@dataclass
class ChartVerdict:
    candidate: dict
    keep: bool
    confidence: float  # 0..1
    reason: str
    chart_spec: dict | None = None  # filled when keep=True


@dataclass
class Decision:
    bundle: str
    artifact_name: str
    needs_charts: bool
    n_candidates: int
    n_kept: int
    verdicts: list[ChartVerdict] = field(default_factory=list)
    summary: str = ""
    provider: str = ""
    model: str = ""
    cost_usd: float = 0.0
    call_id: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _read_bundle_summary(bundle_dir: Path) -> tuple[str, str, list[dict]]:
    """Return (artifact_name, current_md_excerpt, chart_candidates)."""
    meta_path = bundle_dir / "metadata" / "artifact.json"
    artifact_name = ""
    if meta_path.exists():
        try:
            artifact_name = json.loads(meta_path.read_text()).get("name", "")
        except json.JSONDecodeError:
            pass

    current_md = ""
    cur_path = bundle_dir / "draft" / "current.md"
    if cur_path.exists():
        # Trim to the first ~12K chars so the gate stays fast.
        current_md = cur_path.read_text()[:12000]

    chart_candidates: list[dict] = []
    ann_path = bundle_dir / "draft" / "annotations.json"
    if ann_path.exists():
        try:
            ann = json.loads(ann_path.read_text())
            chart_candidates = ann.get("chart_candidates", [])
        except json.JSONDecodeError:
            pass
    return artifact_name, current_md, chart_candidates


def needs_charts(
    bundle_dir: Path,
    *,
    llm: SommLLM | None = None,
    model: str = "deepseek-v4-pro",
    provider: str = "deepseek",
) -> Decision:
    artifact_name, draft_excerpt, candidates = _read_bundle_summary(bundle_dir)
    n_cand = len(candidates)

    if n_cand == 0:
        return Decision(
            bundle=str(bundle_dir),
            artifact_name=artifact_name,
            needs_charts=False,
            n_candidates=0,
            n_kept=0,
            summary="Compositor proposed zero chart candidates. No charts to gate.",
        )

    llm = llm or SommLLM(project="vizier")

    cand_blob = "\n".join(
        f"{i + 1}. " + json.dumps(c, ensure_ascii=False) for i, c in enumerate(candidates)
    )

    system = (
        "You are vizier, the dataviz taste gate for a research-review longform "
        "piece. Decide which proposed chart candidates are worth authoring "
        "and which to drop. Be strict — the prose alone is often enough. "
        "Output strict JSON. No commentary."
    )

    user = (
        f"## Vizier's posture\n{HOUSE_TASTE}\n\n"
        f"## Article excerpt (first ~12KB of locked draft)\n{draft_excerpt}\n\n"
        f"## Compositor's chart candidates\n{cand_blob}\n\n"
        f"---\n\n"
        f"Output JSON of this exact shape:\n"
        '{\n'
        '  "needs_charts": true|false,\n'
        '  "summary": "one sentence why this piece does or does not need charts",\n'
        '  "verdicts": [\n'
        '    {"candidate_index": 1, "keep": true|false, "confidence": 0.0..1.0, '
        '"reason": "why", "chart_spec": {...}}\n'
        '  ]\n'
        '}\n'
        "If keep=true, fill chart_spec with: kind, title, x_axis, y_axis, "
        "data (a tiny inline series or pointer to where the numbers live), "
        "section, supports_decision."
    )

    result = llm.generate(
        prompt=user,
        system=system,
        workload=WORKLOAD,
        max_tokens=8000,
        temperature=0.1,
        provider=provider,
        model=model,
    )

    raw = result.text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Couldn't parse — treat as failure, return a single uncommitted decision.
        return Decision(
            bundle=str(bundle_dir),
            artifact_name=artifact_name,
            needs_charts=False,
            n_candidates=n_cand,
            n_kept=0,
            summary=f"vizier gate parse error; raw response stored. ({len(raw)} chars)",
            provider=result.provider,
            model=result.model,
            cost_usd=result.cost_usd,
            call_id=result.call_id,
        )

    verdicts: list[ChartVerdict] = []
    for v in parsed.get("verdicts", []):
        idx = v.get("candidate_index", 0) - 1
        cand = candidates[idx] if 0 <= idx < n_cand else {}
        verdicts.append(
            ChartVerdict(
                candidate=cand,
                keep=bool(v.get("keep", False)),
                confidence=float(v.get("confidence", 0.0)),
                reason=v.get("reason", ""),
                chart_spec=v.get("chart_spec"),
            )
        )

    n_kept = sum(1 for v in verdicts if v.keep)
    return Decision(
        bundle=str(bundle_dir),
        artifact_name=artifact_name,
        needs_charts=bool(parsed.get("needs_charts", n_kept > 0)),
        n_candidates=n_cand,
        n_kept=n_kept,
        verdicts=verdicts,
        summary=parsed.get("summary", ""),
        provider=result.provider,
        model=result.model,
        cost_usd=result.cost_usd,
        call_id=result.call_id,
    )


def write_decision(decision: Decision, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(decision.to_dict(), indent=2, ensure_ascii=False))
