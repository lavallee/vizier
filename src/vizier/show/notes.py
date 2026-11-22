"""Honesty checks, as notes attached to the output.

None of these veto a figure. Each says what a reader could misread and what
fixes it; where the fix is mechanical, `show` has already applied it
(`applied: true`) and the note says what was done.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .profile import Profile
from .rank import Fields, Option

_RATE_NAME = re.compile(r"(rate|per[_\s]|percent|pct|share|prevalence|proportion|ratio|_per_|incidence)", re.I)
_COUNT_NAME = re.compile(r"(^n$|^n_|count|total|population|pop\b|pop_|households|denominator|enrol|respondents|sample|cases|size)", re.I)

_MESSAGES = {
    "axis-not-zero": (
        "A line's slope looks steeper than the change is, relative to the whole value.",
        "The axis start is labelled. If the size of the change against the total matters, redraw from zero (--zero).",
    ),
    "too-many-series": (
        "Past about eight hues, readers match the wrong line or dot to the wrong name.",
        "The tail is gray as 'Other'. To compare every series, use small multiples or a table.",
    ),
    "too-many-categories": (
        "A list cut to the top values hides the rest, including any near the cut.",
        "Say how many are not shown, and offer the table for the full list.",
    ),
    "too-many-panels": (
        "Panels left out are invisible, so the grid looks complete when it isn't.",
        "Say how many panels are not shown; the table has every series.",
    ),
    "missing-not-plotted": (
        "Rows left off the chart make it look complete; filling them with zero would invent values.",
        "They are left out, not zeroed, and counted here. Say why they are missing if you know.",
    ),
    "ramp-steps": (
        "More color classes than the eye can order makes neighbouring classes look the same.",
        "Values are binned into the classes the ramp can hold; label key values or add a table.",
    ),
    "unmatched-areas": (
        "Areas with no outline drop off the map silently.",
        "Check the join key; the unmatched rows are counted here.",
    ),
}


def load_caveats(path: str | Path) -> list[dict[str, str]]:
    """Read a caveats file: a JSON list of {effect, misuse, instead}."""
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        data = data.get("caveats", [])
    out = []
    for c in data:
        if isinstance(c, str):
            out.append({"effect": c, "misuse": "", "instead": ""})
        elif isinstance(c, dict):
            out.append({k: str(c.get(k, "") or "") for k in ("effect", "misuse", "instead")})
    return out


def caveat_line(c: dict[str, str]) -> str:
    s = c.get("effect", "").rstrip(".")
    s = s + "." if s else ""
    if c.get("misuse"):
        s += f" It does not support {c['misuse'].rstrip('.')[0].lower() + c['misuse'].rstrip('.')[1:]}."
    if c.get("instead"):
        s += f" {c['instead'].rstrip('.')[0].upper() + c['instead'].rstrip('.')[1:]}."
    return s.strip()


def _used_columns(option: Option) -> list[str]:
    cols: list[str] = []
    for k, v in option.roles.items():
        if k in ("columns",):
            continue
        for x in (v if isinstance(v, list) else [v]):
            if isinstance(x, str) and not x.startswith("__"):
                cols.append(x)
    return cols


def honesty_notes(profile: Profile, fields: Fields, option: Option, *, applied: list[dict],
                  dual_axis: tuple[str, str] | None = None) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    used = [profile.get(c) for c in _used_columns(option)]
    used = [c for c in used if c is not None]

    for a in applied:
        misread, fix = _MESSAGES.get(a["check"], ("", ""))
        notes.append({"check": a["check"], "severity": "warn", "misread": misread, "fix": fix,
                      "applied": True, "detail": a["detail"]})

    if dual_axis:
        a, b = dual_axis
        notes.append({
            "check": "dual-axis", "severity": "warn",
            "misread": "Two y-axes in different units invite reading a relationship into where two arbitrary scales happen to cross.",
            "fix": "Each measure gets its own figure on its own axis; compare them side by side, or index both to a common start.",
            "applied": True,
            "detail": f"{a} and {b} are in different units; they are drawn as separate figures, not on two axes.",
        })

    if option.form in ("bar-chart", "dot-plot") and option.is_chart:
        ycol = option.roles.get("y")
        yc = profile.get(ycol) if isinstance(ycol, str) else None
        if yc and option.form == "bar-chart" and yc.min is not None and yc.max and yc.min > 0 and yc.min / yc.max > 0.8:
            notes.append({
                "check": "truncated-axis", "severity": "info",
                "misread": "The differences are small next to the values, which tempts a cut-off axis — that would make them look large.",
                "fix": "Bars start at zero so lengths stay honest. If the difference is the story, chart the difference itself.",
                "applied": True, "detail": "Bars are drawn from zero.",
            })

    if option.form in ("scatterplot", "histogram", "strip-plot") or (option.form == "small-multiples" and option.variant == "scatter"):
        n = min((c.n_present for c in used if c.role == "measure"), default=profile.n_rows)
        if n < 15:
            notes.append({
                "check": "small-sample", "severity": "warn",
                "misread": f"With {n} points, an apparent pattern can easily be chance.",
                "fix": "The count is in the subtitle; avoid a trend line and say how many there are.",
                "applied": True, "detail": f"n = {n} is stated on the figure.",
            })

    count_cols = [c for c in profile.columns if c.role == "measure" and _COUNT_NAME.search(c.name)]
    for c in used:
        if c.role != "measure":
            continue
        is_rate = (c.unit == "%") or bool(_RATE_NAME.search(c.name)) or bool(_RATE_NAME.search(c.label or ""))
        if is_rate and not count_cols:
            notes.append({
                "check": "rate-without-denominator", "severity": "warn",
                "misread": f"{c.label} is a rate; with no denominator a reader can't tell whether a high value covers fifty people or fifty thousand, or how stable small areas are.",
                "fix": "Add the denominator (population, cases, respondents) as a column, or say in a note what the rate is out of.",
                "applied": False, "detail": "",
            })
            break

    supp = [c for c in used if c.n_suppressed]
    for c in supp:
        kinds = ", ".join(f"{k} ({v})" for k, v in c.states.items())
        notes.append({
            "check": "suppressed-values", "severity": "warn",
            "misread": "A suppressed or uncollected value read as zero — or the figure read as complete.",
            "fix": "They are drawn as hatched gaps or labelled in place, and counted here.",
            "applied": True, "detail": f"{c.label}: {kinds}.",
        })

    missing = [c for c in used if c.n_missing > c.n_suppressed and c.role in ("measure", "time")]
    if missing and not any(n["check"] == "missing-not-plotted" for n in notes):
        c = missing[0]
        notes.append({
            "check": "missing-values", "severity": "info",
            "misread": "Missing values filled in as zero would invent data; left out silently, they make the figure look complete.",
            "fix": "Missing values are gaps, not zeros.",
            "applied": True, "detail": f"{c.label}: {c.n_missing - c.n_suppressed} missing.",
        })

    if option.form == "scatterplot":
        notes.append({
            "check": "correlation-not-cause", "severity": "info",
            "misread": "Two measures that move together across rows don't show that one causes the other; a shared cause can drive both.",
            "fix": "Say so in the note. If a likely confounder is in the table, color or facet by it, or plot it next.",
            "applied": False, "detail": "",
        })

    if option.form == "choropleth":
        notes.append({
            "check": "area-weight", "severity": "info",
            "misread": "Big, empty areas dominate a map; small, dense ones vanish, so the eye weighs land, not people.",
            "fix": "Pair the map with a ranked chart or table, or use a cartogram / dot plot when population is the point.",
            "applied": False, "detail": "",
        })
    return notes


def figure_notes(notes: list[dict[str, Any]], caveats: list[dict[str, str]]) -> list[str]:
    """The short lines printed on the figure: caveats, then what was applied."""
    out = [caveat_line(c) for c in caveats if c.get("effect")]
    for n in notes:
        if n.get("applied") and n.get("detail") and n["check"] not in ("truncated-axis", "small-sample"):
            out.append(n["detail"])
    return out
