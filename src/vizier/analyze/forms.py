"""Form-dimension generation — the counterpart to critiquing a chart against its
pattern. Given a data-job, route to the right chart form(s) over the 43-pattern
library, guarded by the form heuristic's "is it even a chart?" checks.

Where `suggest_palette` answers "which colors," `recommend_form` answers "which
form" — the other half of a generation-time decision a renderer (weaver) would
otherwise make on its own.
"""

from __future__ import annotations

from ..db import query as Q

FAMILIES = [
    "Deviation", "Correlation", "Ranking", "Distribution", "Change over time",
    "Magnitude", "Part-to-whole", "Spatial", "Flow",
]


# Keyword → FT family, so a job phrased in words the pattern bodies don't literally
# contain still routes (BM25 alone misses "before and after per item"). Broad on
# purpose — a job can hit several families, and we merge with the BM25 hits.
_FAMILY_HINTS: dict[str, tuple[str, ...]] = {
    "Part-to-whole": ("part-to-whole", "part to whole", "composition", "share of", "proportion",
                      "breakdown", "makeup", "percent of", "% of", "made up of", "out of 100"),
    "Change over time": ("over time", "trend", "time series", "change over", "across years",
                         "timeline", "growth", "before and after", "before/after", "year over year"),
    "Ranking": ("rank", "ranking", "top ", "largest", "biggest", "order by", "sorted", "leaderboard"),
    "Distribution": ("distribution", "spread", "histogram", "frequency", "density", "variation", "outliers"),
    "Correlation": ("correlation", "relationship", " vs ", "versus", "against", "scatter", "x and y"),
    "Magnitude": ("magnitude", "compare amounts", "how many", "how much", "size of", "counts by"),
    "Deviation": ("deviation", "above below", "above/below", "surplus", "deficit", "vs baseline",
                  "vs target", "diverge", "net change"),
    "Flow": ("flow", "sankey", "from-to", "pathway", "transition", "funnel", "conserved"),
    "Spatial": ("map", "geographic", "by state", "by county", "by region", "spatial", "location", "where"),
}


def _infer_families(job: str) -> list[str]:
    jl = " " + job.lower() + " "
    return [fam for fam, hints in _FAMILY_HINTS.items() if any(h in jl for h in hints)]


def _match_family(f: str) -> str:
    fl = f.strip().lower()
    for fam in FAMILIES:
        if fam.lower() == fl or fl in fam.lower() or fam.lower() in fl:
            return fam
    return f  # pass through; list_patterns will simply return nothing for a bad family


def recommend_form(
    job: str | None = None,
    *,
    family: str | None = None,
    n_series: int | None = None,
    k: int = 4,
) -> dict:
    """Recommend chart form(s) for a data-job.

    Pass a free-text `job` ("part-to-whole over time, 5 series"), and/or an FT
    `family`, and optionally `n_series`. Returns ranked patterns (capsule,
    when-to / when-not, alternatives, common mistakes) plus form-heuristic
    `notes` — including when the answer is *not a chart* (a stat tile or a table).
    """
    if not job and not family:
        raise ValueError("give a `job` (free-text data-question) or a `family`")

    notes: list[str] = []
    # "Is it even a chart?" guards, straight from the form heuristic.
    if isinstance(n_series, int):
        if n_series <= 1:
            notes.append(
                "A single current value is a stat tile / hero figure, not a chart "
                "(a single ratio against a limit is a meter) — don't reach for a "
                "one-bar bar chart or a 2-slice pie."
            )
        elif n_series > 7:
            notes.append(
                f"{n_series} classes all carrying meaning is usually a table (or "
                "table + chart), not more colors — past ~7 the categorical channel "
                "blurs. If a chart is still right, fold the tail into 'Other' or "
                "facet into small multiples."
            )

    target: list[str] = [_match_family(family)] if family else []
    if job:
        target += [f for f in _infer_families(job) if f not in target]

    # BM25 relevance rank over the pattern text (used as a tiebreak / for job words
    # the families miss).
    bm25_rank: dict[str, int] = {}
    if job:
        for i, h in enumerate(Q.search(job, k=k * 4, source="chart-forms")):
            bm25_rank.setdefault(h.item_id, i)

    # Score family candidates by fit: a *primary* target-family match is worth more
    # than a secondary one, so the canonical form (scatterplot for Correlation,
    # stacked-area for Part-to-whole) rises above patterns that only claim the family
    # in passing (arc/chord claim Correlation secondarily).
    score: dict[str, int] = {}
    for fam in target:
        for p in Q.list_patterns(purpose_family=fam):
            pf = p.get("purpose_families") or []
            s = sum((2 if i == 0 else 1) for i, f in enumerate(pf) if f in target)
            score[p["id"]] = max(score.get(p["id"], 0), s)
    for pid in bm25_rank:            # job matched a pattern no family caught → keep it
        score.setdefault(pid, 0)

    ids = sorted(score, key=lambda pid: (-score[pid], bm25_rank.get(pid, 999), pid))[:k]

    forms: list[dict] = []
    for pid in ids[:k]:
        p = Q.get_pattern(pid, transclude=True)
        if not p:
            continue
        forms.append({
            "id": p["id"],
            "title": p.get("title"),
            "purpose_families": p.get("purpose_families"),
            "capsule": p.get("capsule"),
            "when_to_use": p.get("when_to_use"),
            "when_not_to_use": p.get("when_not_to_use"),
            "alternatives": p.get("alternatives"),
            "common_mistakes": p.get("common_mistakes"),
        })

    return {"job": job, "family": family, "n_series": n_series, "notes": notes, "forms": forms}


def format_recommendation(rec: dict) -> str:
    """Render `recommend_form`'s result for the CLI."""
    lines: list[str] = []
    for n in rec.get("notes") or []:
        lines.append(f"! {n}")
    if rec.get("notes"):
        lines.append("")
    if not rec.get("forms"):
        lines.append("(no matching chart pattern — try a different job description or family)")
        return "\n".join(lines)
    for i, f in enumerate(rec["forms"], 1):
        fams = ", ".join(f.get("purpose_families") or [])
        lines.append(f"{i}. {f['title']}  ({f['id']}) [{fams}]")
        if f.get("capsule"):
            lines.append(f"   {f['capsule'].strip()}")
        alts = f.get("alternatives") or []
        if alts:
            alt_str = "; ".join(f"{a.get('id')} — {a.get('when')}" for a in alts if isinstance(a, dict))
            if alt_str:
                lines.append(f"   alternatives: {alt_str}")
        lines.append("")
    return "\n".join(lines).rstrip()
