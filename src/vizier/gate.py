"""vizier.gate — which candidate charts to author now, and what to show instead.

Sits in front of a chart-authoring pipeline: an upstream orchestrator hands
vizier a reporting bundle with the compositor's proposed chart candidates and
asks which to build. vizier answers for every candidate:

- **keep** — author it, plus how to make it better (`improve`);
- **set aside** — and what to show *instead* (`instead`: a form from the same
  ranking `vizier show` uses — another chart, a sentence, a stat tile or a
  table — with why and how). A dropped candidate never comes back bare.

Input: a reporting-bundle directory (with `draft/annotations.json` from the
compositor agent that proposed candidate charts).
Output: a `Decision`. `status` is `"ok"`, `"no_candidates"` or `"error"`; a
model reply that can't be parsed is an **error** (`needs_charts=None`, the raw
reply kept in `raw_response`), never a quiet "no charts".

`needs_charts` keeps its name and meaning for existing callers: true when at
least one candidate is kept. The model call goes through somm, as before.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # somm is the optional `critique` extra; import it only when a call is made
    from somm import SommLLM


WORKLOAD = "vizier_gate"

#: The forms a candidate can be redirected to — the vocabulary `vizier show` ranks.
SHOW_FORMS = (
    "sentence", "stat-tile", "table", "bar-chart", "stacked-bar", "line-chart", "slope-chart",
    "scatterplot", "dot-plot", "strip-plot", "histogram", "small-multiples", "heatmap",
    "choropleth", "stacked-area",
)

# Vizier's posture, kept tight so the gate stays a fast call.
HOUSE_TASTE = """\
Vizier's posture on figures in a research-review piece:

- Someone proposed each candidate because they wanted a reader to see
  something. Take that seriously: for every candidate, say the best way to
  show it — which may be this chart, a better chart, a sentence, a stat tile
  or a table.
- A chart is the right call when it carries a comparison, a trend, a spread
  or a relationship that prose would make the reader assemble in their head.
- Two numbers usually read best as a sentence; one number with a benchmark
  as a stat tile; precise lookup across many rows as a table. Those are good
  answers, not consolation prizes — and they still need to be written.
- Prefer the form that matches the comparison: line for change, bar for
  level, dot or strip for distribution, scatter for relationship, slope for
  two points in time, small multiples for many series.
- Diagrams with no numbers, and word clouds, rarely carry a claim; redirect
  them to the numbers or the sentence they were standing in for.
- If the dossier doesn't contain the numbers a chart needs, say which numbers
  are missing and what can be shown with what is there.
- Several figures can earn their place; so can none. Fewer, sharper figures
  usually serve the reader better than many.
"""


@dataclass
class ChartVerdict:
    candidate: dict
    keep: bool
    confidence: float  # 0..1
    reason: str
    chart_spec: dict | None = None  # filled when keep=True
    #: kept candidates: concrete ways to make the chart better
    improve: list[str] = field(default_factory=list)
    #: dropped candidates: {"form", "why", "how"} — what to show instead
    instead: dict | None = None
    #: "model" when the model supplied `instead`, "default" when vizier filled the gap
    instead_source: str | None = None


@dataclass
class Decision:
    bundle: str
    artifact_name: str
    needs_charts: bool | None  # None when status == "error": the gate could not decide
    n_candidates: int
    n_kept: int
    verdicts: list[ChartVerdict] = field(default_factory=list)
    summary: str = ""
    provider: str = ""
    model: str = ""
    cost_usd: float = 0.0
    call_id: str = ""
    status: str = "ok"  # ok | no_candidates | error
    error: str = ""
    raw_response: str = ""

    @property
    def ok(self) -> bool:
        return self.status != "error"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["ok"] = self.ok
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


def _default_instead(candidate: dict) -> dict:
    """What to show when the model set a candidate aside without saying."""
    return {
        "form": "table",
        "why": "The gate set this aside without naming an alternative; a small table of the "
               "candidate's numbers keeps them available to the reader.",
        "how": "List the values the candidate would have plotted, with units and the source; "
               "run `vizier show` on them to see the ranked options.",
    }


def _parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError(f"expected a JSON object, got {type(parsed).__name__}")
    return parsed


def needs_charts(
    bundle_dir: Path,
    *,
    llm: "SommLLM | None" = None,
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
            status="no_candidates",
            summary="The compositor proposed no chart candidates, so there is nothing to choose between.",
        )

    if llm is None:
        from somm import SommLLM

        llm = SommLLM(project="vizier")

    cand_blob = "\n".join(
        f"{i + 1}. " + json.dumps(c, ensure_ascii=False) for i, c in enumerate(candidates)
    )

    system = (
        "You are vizier, the data-visualisation editor for a research-review longform "
        "piece. For each proposed chart candidate, decide whether to author it as "
        "proposed; for every one you keep, say how to make it better, and for every one "
        "you set aside, say what to show instead (a better chart, a sentence, a stat "
        "tile or a table). Never set a candidate aside without an alternative. "
        "Output strict JSON. No commentary."
    )

    user = (
        f"## Vizier's posture\n{HOUSE_TASTE}\n\n"
        f"## Article excerpt (first ~12KB of locked draft)\n{draft_excerpt}\n\n"
        f"## Compositor's chart candidates\n{cand_blob}\n\n"
        f"---\n\n"
        f"Forms you may name: {', '.join(SHOW_FORMS)}.\n\n"
        f"Output JSON of this exact shape:\n"
        '{\n'
        '  "needs_charts": true|false,\n'
        '  "summary": "one sentence on how this piece should show its numbers",\n'
        '  "verdicts": [\n'
        '    {"candidate_index": 1, "keep": true|false, "confidence": 0.0..1.0, '
        '"reason": "why", "chart_spec": {...}, '
        '"improve": ["..."], '
        '"instead": {"form": "<one of the forms>", "why": "...", "how": "..."}}\n'
        '  ]\n'
        '}\n'
        "If keep=true: fill chart_spec with kind, title, x_axis, y_axis, data (a tiny "
        "inline series or a pointer to where the numbers live), section, "
        "supports_decision; and give 1-3 concrete `improve` items. "
        "If keep=false: `instead` is required — the form to show, why it serves the "
        "reader better, and how to make it (for a sentence, write the sentence)."
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

    raw = result.text or ""
    try:
        parsed = _parse_json(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        # A reply we can't read is a failed decision, not a decision against charts.
        return Decision(
            bundle=str(bundle_dir),
            artifact_name=artifact_name,
            needs_charts=None,
            n_candidates=n_cand,
            n_kept=0,
            status="error",
            error=f"could not parse the gate's reply as JSON: {exc}",
            raw_response=raw,
            summary=f"vizier gate failed: unparseable model reply ({len(raw)} chars); no decision was made.",
            provider=result.provider,
            model=result.model,
            cost_usd=result.cost_usd,
            call_id=result.call_id,
        )

    verdicts: list[ChartVerdict] = []
    for v in parsed.get("verdicts", []):
        if not isinstance(v, dict):
            continue
        idx = int(v.get("candidate_index", 0) or 0) - 1
        cand = candidates[idx] if 0 <= idx < n_cand else {}
        keep = bool(v.get("keep", False))
        improve = v.get("improve") or []
        if isinstance(improve, str):
            improve = [improve]
        instead = v.get("instead") if isinstance(v.get("instead"), dict) else None
        source = None
        if not keep:
            if instead and instead.get("form"):
                source = "model"
            else:
                instead, source = _default_instead(cand), "default"
        verdicts.append(
            ChartVerdict(
                candidate=cand,
                keep=keep,
                confidence=float(v.get("confidence", 0.0) or 0.0),
                reason=v.get("reason", ""),
                chart_spec=v.get("chart_spec"),
                improve=[str(x) for x in improve] if keep else [],
                instead=None if keep else instead,
                instead_source=source,
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


if __name__ == "__main__":  # `python -m vizier.gate <bundle_dir> ...`
    from vizier.__main__gate import main as _main

    raise SystemExit(_main())
