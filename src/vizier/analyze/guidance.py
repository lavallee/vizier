"""Deterministic implementation guidance for journalistic charts.

This is the generation-time counterpart to critique: given a chart job, surface
the form recommendation, the editorial checks a builder must satisfy, and prior
art from the configured corpus DBs. It deliberately avoids an LLM dependency so
the MCP/CLI can be used inside renderers and coding agents.
"""

from __future__ import annotations

from typing import Any

from ..db import query as Q
from . import forms as F


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    t = " " + text.lower() + " "
    return any(term in t for term in terms)


def _base_checks() -> list[dict[str, str]]:
    return [
        {
            "id": "reader-decision",
            "name": "Reader decision",
            "check": (
                "Write the sentence: after reading this, the audience should be "
                "able to decide, compare, or understand X. If X is only 'see the "
                "data,' the module needs a sharper job."
            ),
        },
        {
            "id": "headline-claim",
            "name": "Headline claim",
            "check": (
                "State the one factual claim the chart must carry before picking "
                "labels, annotations, or prose. Build the chart backward from that "
                "claim."
            ),
        },
        {
            "id": "fair-comparison",
            "name": "Fair comparison",
            "check": (
                "Name the benchmark that makes the value interpretable: statewide, "
                "county, district overall, same-level peers, prior period, target, "
                "or a documented 'no fair comparison available'."
            ),
        },
        {
            "id": "unit-denominator",
            "name": "Unit and denominator",
            "check": (
                "Put the unit in the axis/caption and name the denominator near "
                "the chart: percent of what, dollars per whom, count of which rows, "
                "or share of which total."
            ),
        },
        {
            "id": "counter-reading",
            "name": "Counter-reading",
            "check": (
                "List the most likely wrong reading and block it in the caption or "
                "annotation rather than burying it in distant methodology text."
            ),
        },
        {
            "id": "reader-affordance",
            "name": "Reader affordance",
            "check": (
                "Provide direct labels, a legend, endpoint labels, and tooltip/table "
                "fallbacks appropriate to the chart. Do not make color carry the "
                "only meaning."
            ),
        },
    ]


def _domain_checks(text: str) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    budget = _contains(
        text,
        (
            "budget", "revenue", "funding", "fund balance", "appropriation",
            "per pupil", "pupil cost", "operating", "tax levy", "dollars",
        ),
    )
    school = _contains(text, ("school", "district", "student", "pupil", "county", "statewide"))
    if budget:
        checks.extend([
            {
                "id": "money-basis",
                "name": "Money basis",
                "check": (
                    "Say whether dollars are nominal or inflation-adjusted. If no "
                    "adjustment exists, use nominal budget-year dollars and avoid "
                    "real-dollar change claims."
                ),
            },
            {
                "id": "fund-scope",
                "name": "Fund scope",
                "check": (
                    "Name whether the chart is operating fund, General Fund, all "
                    "funds, grants, debt service, or transfers. Do not let a revenue "
                    "mix imply it covers more funds than it does."
                ),
            },
            {
                "id": "published-metric",
                "name": "Published metric",
                "check": (
                    "For comparative cost per pupil, use the publisher's metric. "
                    "Do not recompute it from total budget divided by enrollment."
                ),
            },
        ])
    if budget and _contains(text, ("revenue", "mix", "source", "funding")):
        checks.append({
            "id": "part-to-whole-total",
            "name": "Part-to-whole total",
            "check": (
                "State the total behind the parts: share of proposed operating "
                "budget, not all-funds revenue, unless all funds are actually the "
                "denominator."
            ),
        })
    if school:
        checks.append({
            "id": "local-benchmark",
            "name": "Local benchmark",
            "check": (
                "Prefer a local benchmark a resident can reason about: county, "
                "same district, same level, or statewide if no local peer set is "
                "valid."
            ),
        })
    return checks


def _prior_art(job: str, context: str | None, *, k: int, semantic: bool) -> tuple[list[dict[str, Any]], str | None]:
    if k <= 0:
        return [], None
    text = " ".join(part for part in (job, context or "") if part)
    retrieval_query = " ".join(
        part for part in (
            job,
            context or "",
            "reader decision headline claim fair comparison denominator caveat annotation",
        )
        if part
    )
    queries = [
        retrieval_query,
        '"reader decision" OR "headline claim" OR "fair comparison" OR denominator OR caveat OR purpose',
    ]
    if _contains(text, ("budget", "revenue", "funding", "per pupil", "operating")):
        queries.append('"per pupil" OR budget OR revenue OR funding OR operating')
    if _contains(text, ("school", "district", "student", "pupil")):
        queries.append('school OR district OR student OR pupil')
    hits = []
    for q in queries:
        hits.extend(Q.search(q, k=k, exclude_sources=("chart-forms",)))
    semantic_error = None
    if semantic:
        try:
            hits.extend(Q.find_similar(retrieval_query, k=k, min_sim=0.25))
        except ModuleNotFoundError as e:
            semantic_error = str(e)
    deduped: dict[str, Q.Hit] = {}
    for hit in hits:
        if hit.source == "chart-forms":
            continue
        prev = deduped.get(hit.key)
        if prev is None or hit.score > prev.score:
            deduped[hit.key] = hit
    ordered = sorted(deduped.values(), key=lambda h: (-_prior_score(h), h.source, h.item_id))[:k]
    return [h.to_dict(body_chars=360) for h in ordered], semantic_error


def _prior_score(hit: Q.Hit) -> float:
    score = hit.score
    if hit.source == "weaver":
        score += 4.0
    elif hit.source in {"rubrics", "ft-vocab"}:
        score += 2.0
    if hit.type == "principle":
        score += 2.0
    text = f"{hit.title} {hit.body}".lower()
    for term in ("headline", "decision", "denominator", "comparison", "purpose", "caveat"):
        if term in text:
            score += 0.7
    return score


def implementation_guide(
    job: str,
    *,
    context: str | None = None,
    family: str | None = None,
    n_series: int | None = None,
    k_forms: int = 4,
    k_prior: int = 5,
    semantic: bool = False,
) -> dict[str, Any]:
    """Return a deterministic implementation guide for a chart job."""
    rec = F.recommend_form(job, family=family, n_series=n_series, k=k_forms)
    text = " ".join(part for part in (job, context or "") if part)
    prior, semantic_error = _prior_art(job, context, k=k_prior, semantic=semantic)
    guide = {
        "job": job,
        "context": context,
        "forms": rec["forms"],
        "form_notes": rec["notes"],
        "checks": _base_checks() + _domain_checks(text),
        "prior_art": prior,
    }
    if semantic_error:
        guide["semantic_error"] = semantic_error
    return guide


def format_guide(guide: dict[str, Any]) -> str:
    """Render `implementation_guide` for the CLI."""
    lines: list[str] = ["# Vizier implementation guide", "", f"Job: {guide['job']}"]
    if guide.get("context"):
        lines.append(f"Context: {guide['context']}")
    if guide.get("form_notes"):
        lines.append("")
        lines.append("Form notes:")
        for note in guide["form_notes"]:
            lines.append(f"- {note}")
    lines.append("")
    lines.append("Recommended forms:")
    forms = guide.get("forms") or []
    if forms:
        for i, form in enumerate(forms, 1):
            fams = ", ".join(form.get("purpose_families") or [])
            lines.append(f"{i}. {form.get('title')} ({form.get('id')}) [{fams}]")
            if form.get("capsule"):
                lines.append(f"   {form['capsule'].strip()}")
    else:
        lines.append("- No matching form. Tighten the job or pass --family.")

    lines.append("")
    lines.append("Implementation checks:")
    for check in guide.get("checks") or []:
        lines.append(f"- {check['name']}: {check['check']}")

    prior = guide.get("prior_art") or []
    if prior:
        lines.append("")
        lines.append("Prior-art signals:")
        for hit in prior:
            lines.append(f"- {hit['source']}/{hit['item_id']}: {hit['title']} ({hit['why']})")
    if guide.get("semantic_error"):
        lines.append("")
        lines.append(f"Semantic retrieval skipped: {guide['semantic_error']}")
    return "\n".join(lines)
