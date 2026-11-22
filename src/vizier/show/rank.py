"""Rank the ways to show a table.

Input: a `Profile` and, optionally, the claim or question the figure serves.
Output: an ordered list of `Option`s — chart forms from the 43-pattern corpus,
and three non-chart forms (a sentence, a stat tile, a table) that are ranked
on the same footing. A sentence that carries two numbers well is offered as
the better choice *and written out*; it is never a refusal, and a drawable
chart is always offered beside it.

Each option says what it shows well, what it hides, and the mistakes most
often made with it. For chart forms those come from the pattern's own text
(`capsule`, `when_not_to_use`, `common_mistakes`), so the ranking and the
pattern library can't drift apart.

Deterministic: the family hints are the same ones `recommend_form` uses, and
the pattern files are read straight from the corpus — no index, no model.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from typing import Any

from ..analyze.forms import _infer_families
from .profile import ColumnProfile, Profile

#: Forms `show` can draw from rows today.
RENDERABLE = {
    "bar-chart", "stacked-bar", "line-chart", "scatterplot", "dot-plot", "strip-plot",
    "histogram", "slope-chart", "small-multiples", "heatmap", "choropleth", "stacked-area",
    "stat-tile", "sentence", "table",
}

#: Non-chart forms, described here because the pattern corpus is about charts.
NON_CHART = {
    "sentence": {
        "title": "A sentence",
        "shows": "A few numbers, exactly, in the order the argument needs them, with the comparison spelled out.",
        "hides": "Shape: a reader can't see a trend, a spread or an outlier in a sentence.",
        "mistakes": [
            "Rounding away the difference the sentence is about.",
            "Leaving out the unit or the comparison that makes the number mean something.",
        ],
    },
    "stat-tile": {
        "title": "A stat tile",
        "shows": "One number, big, with its unit and the comparison that makes it mean something.",
        "hides": "Everything around the number: its history, its spread, how it ranks.",
        "mistakes": [
            "A number with no benchmark (prior period, target, peer) — it can't be judged.",
            "Drawing it as a one-bar bar chart, which adds ink and no comparison.",
        ],
    },
    "table": {
        "title": "A table",
        "shows": "Exact values for lookup: a reader who wants their own row finds it.",
        "hides": "Pattern: comparisons across many rows are slow, and nothing pops out.",
        "mistakes": [
            "Sorting alphabetically when the story is the ranking.",
            "Too many decimal places, and numbers left-aligned so digits don't line up.",
        ],
    },
}


@lru_cache(maxsize=64)
def pattern(pid: str) -> dict[str, Any]:
    """A chart-form pattern's details, read from the corpus file."""
    import frontmatter

    from .. import storage

    for root in (storage.corpus_root(), storage.PACKAGED_CORPUS_ROOT, storage.REPO_CORPUS_ROOT):
        p = root / "chart-forms" / f"{pid}.md"
        if p.exists():
            post = frontmatter.load(str(p))
            d = dict(post.metadata.get("details") or {})
            d["title"] = post.metadata.get("title", pid)
            d["id"] = pid
            return d
    return {"id": pid, "title": pid.replace("-", " ").capitalize()}


def _first_sentence(text: str | None) -> str:
    if not text:
        return ""
    t = " ".join(text.split())
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    return m.group(1) if m else t


@dataclass
class Option:
    form: str
    title: str
    score: float
    reason: str
    roles: dict[str, Any] = field(default_factory=dict)
    shows: str = ""
    hides: str = ""
    mistakes: list[str] = field(default_factory=list)
    drawable: bool = True
    needs: str | None = None
    variant: str | None = None
    rank: int = 0

    @property
    def is_chart(self) -> bool:
        return self.form not in NON_CHART

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["is_chart"] = self.is_chart
        return {k: v for k, v in d.items() if v not in (None, "")}


# ---------------------------------------------------------------- field choice

_WORD = re.compile(r"[a-z0-9]+")
_STOP = {"the", "a", "an", "of", "and", "or", "in", "on", "by", "to", "for", "with", "is", "are",
         "how", "what", "does", "do", "where", "which", "than", "vs", "versus", "per", "as", "at",
         "more", "less", "higher", "lower", "most", "least", "it", "its", "that", "this", "be"}


def _tokens(text: str | None) -> set[str]:
    out = set()
    for w in _WORD.findall((text or "").lower()):
        if w in _STOP or len(w) < 3:
            continue
        out.add(w)
        if w.endswith("s") and len(w) > 4:
            out.add(w[:-1])
    return out


def claim_score(col: ColumnProfile, claim: str | None) -> int:
    if not claim:
        return 0
    ct = _tokens(claim)
    words = _tokens(" ".join(filter(None, [col.name.replace("_", " "), col.label, col.description or ""])))
    return len(ct & words)


def mention_position(col: ColumnProfile, claim: str | None) -> int:
    """Where in the claim this column is first named (large if never)."""
    if not claim:
        return 10_000
    words = _tokens(" ".join(filter(None, [col.name.replace("_", " "), col.label, col.description or ""])))
    best = 10_000
    for i, w in enumerate(_WORD.findall(claim.lower())):
        if w in words or (w.endswith("s") and w[:-1] in words):
            best = min(best, i)
    return best


@dataclass
class Fields:
    time: ColumnProfile | None
    measures: list[ColumnProfile]
    dims: list[ColumnProfile]
    label: ColumnProfile | None
    geometry: ColumnProfile | None
    geo: list[ColumnProfile]
    xy: tuple[str, str] | None = None   # explicit scatter axes
    mentioned: list[str] = field(default_factory=list)  # measures the claim names, in order

    def scatter_xy(self, usable: list[ColumnProfile]) -> tuple[str, str]:
        """Scatter axes: explicit flags win; else the first-named measure is x and
        the last-named is y ("diesel, income and asthma" → asthma against diesel)."""
        if self.xy:
            return self.xy
        names = [u.name for u in usable]
        named = [m for m in self.mentioned if m in names]
        if len(named) >= 2:
            return named[0], named[-1]
        return usable[0].name, usable[1].name

    def names(self) -> dict[str, Any]:
        return {
            "time": self.time.name if self.time else None,
            "measures": [m.name for m in self.measures],
            "dimensions": [d.name for d in self.dims],
            "label": self.label.name if self.label else None,
            "geometry": self.geometry.name if self.geometry else None,
        }


def choose_fields(profile: Profile, claim: str | None = None, overrides: dict[str, Any] | None = None) -> Fields:
    """Pick the time axis, measures, dimensions and label column — claim words first."""
    ov = {k: v for k, v in (overrides or {}).items() if v}

    def _get(name):
        c = profile.get(name)
        if c is None:
            raise ValueError(f"no column named {name!r}; columns are: {', '.join(x.name for x in profile.columns)}")
        return c

    # Claim-named measures first, in the order the claim names them; then the rest.
    measures = sorted(profile.measures, key=lambda c: (claim_score(c, claim) == 0,
                                                      mention_position(c, claim), profile.columns.index(c)))
    # Measures with no usable values can't be drawn; keep them last so notes can name them.
    measures.sort(key=lambda c: c.n_present == 0)
    times = sorted(profile.times, key=lambda c: (-claim_score(c, claim), -(c.n_distinct)))
    # Low-cardinality geography names (county, state) work as dimensions too.
    dim_pool = profile.dimensions + [g for g in profile.geographies
                                     if g.kind == "category" and g.n_distinct < max(2, profile.n_rows)]
    dims = sorted(dim_pool, key=lambda c: (-claim_score(c, claim), c.n_distinct))
    labels = profile.by_role("label") + [g for g in profile.geographies if g.kind == "identifier"] + profile.by_role("identifier")
    label = None
    for c in labels:
        if c.kind in ("text", "category") or c.role == "label":
            label = c
            break
    label = label or (labels[0] if labels else None)

    time = times[0] if times else None
    if "x" in ov:
        x = _get(ov["x"])
        if x.role == "time":
            time = x
        elif x.role == "measure":
            measures = [x] + [m for m in measures if m is not x]
        else:
            dims = [x] + [d for d in dims if d is not x]
            time = None if ov.get("x") and x.role != "time" and time and "series" not in ov else time
    if "y" in ov:
        ys = [_get(n.strip()) for n in str(ov["y"]).split(",") if n.strip()]
        rest = [m for m in measures if m not in ys]
        if "x" in ov and _get(ov["x"]).role == "measure":
            measures = [_get(ov["x"])] + [y for y in ys if y.name != ov["x"]] + [m for m in rest if m.name != ov["x"]]
        else:
            measures = ys + rest
    if "series" in ov:
        s = _get(ov["series"])
        dims = [s] + [d for d in dims if d is not s]
        if "x" in ov and _get(ov["x"]).role not in ("time", "measure"):
            dims = [_get(ov["x"]), s] + [d for d in dims if d.name not in (ov["x"], s.name)]
    if "label" in ov:
        label = _get(ov["label"])
    if time is not None and time.n_distinct <= 1:
        time = None
    dims = [d for d in dims if d.n_distinct >= 1]
    xy = None
    if "x" in ov and "y" in ov:
        xy = (ov["x"], str(ov["y"]).split(",")[0].strip())
    elif "y" in ov:
        xy = None if len(measures) < 2 else (measures[1].name, measures[0].name)
    mentioned = [m.name for m in measures if claim_score(m, claim) > 0]
    return Fields(time=time, measures=measures, dims=dims, label=label,
                  geometry=profile.geometry, geo=profile.geographies, xy=xy, mentioned=mentioned)


# ---------------------------------------------------------------- ranking

def _same_unit(ms: list[ColumnProfile]) -> bool:
    units = {(m.unit or "").lower() for m in ms}
    return len(units) == 1


def _opt(form: str, score: float, reason: str, roles: dict[str, Any], **kw) -> Option:
    if form in NON_CHART:
        nc = NON_CHART[form]
        return Option(form=form, title=nc["title"], score=score, reason=reason, roles=roles,
                      shows=nc["shows"], hides=nc["hides"], mistakes=list(nc["mistakes"]), **kw)
    p = pattern(form)
    hides = (p.get("when_not_to_use") or [""])[0]
    return Option(
        form=form,
        title=p.get("title", form),
        score=score,
        reason=reason,
        roles=roles,
        shows=_first_sentence(p.get("capsule")),
        hides=f"Not the right form when: {hides[0].lower() + hides[1:]}" if hides else "",
        mistakes=list((p.get("common_mistakes") or [])[:2]),
        **kw,
    )


def rank_forms(profile: Profile, claim: str | None = None, *,
               overrides: dict[str, Any] | None = None, geometry_available: bool | None = None) -> tuple[list[Option], Fields]:
    """Rank the ways to show this table. Returns (options best-first, chosen fields)."""
    f = choose_fields(profile, claim, overrides)
    fams = set(_infer_families(claim)) if claim else set()
    n = profile.n_rows
    usable = [m for m in f.measures if m.n_present > 0]
    M = len(usable)
    T = f.time
    D = f.dims
    opts: list[Option] = []
    relationship = len([m for m in f.mentioned if any(u.name == m for u in usable)]) >= 2
    has_geom = geometry_available if geometry_available is not None else f.geometry is not None
    lab = f.label.name if f.label else None

    def add(form, score, reason, roles, **kw):
        opts.append(_opt(form, score, reason, roles, **kw))

    if M == 0:
        add("table", 100, "No numeric column to draw, so the honest figure is the table itself.",
            {"columns": [c.name for c in profile.columns if c.role != "geometry"]})
        if D:
            d = D[0]
            add("bar-chart", 60, f"Counting rows by {d.label} gives a number per category to draw.",
                {"x": d.name, "y": "__count__", "label": d.name}, variant="count")
        return _finish(opts, fams, relationship), f

    m0 = usable[0]
    total_values = sum(m.n_present for m in usable)

    # ---- tiny tables: a sentence or a tile is often the clearest form, and we say so
    if n == 1:
        if M == 1:
            add("stat-tile", 100, "One number: a stat tile shows it at the size it deserves.", {"value": m0.name})
            add("sentence", 92, "One number reads naturally in a sentence — here it is, ready to use.", {"values": [m0.name]})
        elif M == 2:
            add("sentence", 100, "Two numbers: a sentence carries this, here it is.", {"values": [m.name for m in usable]})
            add("stat-tile", 80, "Two tiles side by side, if the page has room for big numbers.", {"values": [m.name for m in usable]})
        if M >= 2 and _same_unit(usable):
            add("bar-chart", 85 if M > 2 else 78,
                f"{M} measures in the same unit can sit on one axis as bars.",
                {"x": "__measure__", "y": "__value__", "measures": [m.name for m in usable]}, variant="measures")
        if M > 2:
            add("table", 82, f"{M} different numbers about one thing: a small table keeps each exact.",
                {"columns": [m.name for m in usable]})
        else:
            add("table", 40, "A one-row table, if the numbers need to sit with others on the page.",
                {"columns": [m.name for m in usable]})
        return _finish(opts, fams, relationship), f

    # ---- time series
    if T is not None:
        nt = T.n_distinct
        series = D[0] if D else None
        s = series.n_distinct if series else (M if M > 1 and _same_unit(usable) else 1)
        ys = [m.name for m in usable] if (not series and M > 1 and _same_unit(usable)) else [m0.name]
        roles = {"x": T.name, "y": ys[0] if len(ys) == 1 else ys, "series": series.name if series else None}
        if nt == 2:
            if s >= 2:
                add("slope-chart", 100, f"Two points in time for {s} series: a slope per series shows who rose and who fell.", roles)
                add("bar-chart", 80, "Grouped bars put the two periods side by side for each series.",
                    {"x": series.name if series else "__measure__", "y": m0.name, "series": T.name}, variant="grouped")
                add("table", 60, "A before/after table with the change column is easy to scan.", {"columns": None})
            else:
                add("sentence", 100, "One series at two dates: a sentence says from what to what, here it is.",
                    {"values": [m0.name], "time": T.name})
                add("bar-chart", 82, "Two bars on a zero baseline show the size of the change honestly.",
                    {"x": T.name, "y": m0.name}, variant="time")
                add("slope-chart", 70, "A single slope line works if it will sit beside others.", roles)
                add("table", 40, "A two-row table.", {"columns": None})
            return _finish(opts, fams, relationship), f
        if s > 6:
            add("small-multiples", 100,
                f"{s} series is too many lines for one panel — one small panel each, on a shared scale.",
                {**roles, "facet": series.name if series else None}, variant="line")
            add("line-chart", 85,
                f"One panel works if a few of the {s} series are the story: highlight them and grey the rest.",
                roles, variant="highlight")
            if s * nt <= 2000:
                add("heatmap", 80, f"A heatmap of {series.label if series else 'series'} by {T.label} fits every value in one grid.",
                    {"x": T.name, "y": series.name if series else None, "value": m0.name})
        else:
            add("line-chart", 100,
                f"Change over {nt} {T.granularity or 'time'} points" + (f" for {s} series" if s > 1 else "") + ": a line is the default and it reads at a glance.",
                roles)
            if s > 1 and series is not None:
                add("small-multiples", 78, "One panel per series avoids crossing lines and lets each be read alone.",
                    {**roles, "facet": series.name}, variant="line")
            if nt <= 12 and s <= 3:
                add("bar-chart", 72, f"With {nt} periods, columns on a zero baseline show each period's level.",
                    {"x": T.name, "y": m0.name, "series": series.name if series else None}, variant="time")
            if s >= 3 and nt >= 6:
                add("heatmap", 62, "A heatmap shows every value at once, at the cost of precise reading.",
                    {"x": T.name, "y": series.name if series else None, "value": m0.name})
        if s > 1 and "Part-to-whole" in fams:
            add("stacked-area", 88, "The claim is about composition over time: stacked area shows the total and its parts.", roles)
        if nt <= 4 and s == 1:
            add("sentence", 75, f"Only {nt} points: a sentence can carry the change exactly.", {"values": [m0.name], "time": T.name})
        else:
            add("sentence", 30, "A one-line summary of the change, for alt text or the lede.", {"values": [m0.name], "time": T.name})
        add("table", 55 if nt <= 8 else 35, "The values for lookup.", {"columns": None})
        return _finish(opts, fams, relationship), f

    # ---- categories (no time)
    if D:
        d = D[0]
        c = d.n_distinct
        d2 = D[1] if len(D) > 1 else None
        if d2 is not None and n > c:
            c2 = d2.n_distinct
            roles = {"x": d.name, "series": d2.name, "y": m0.name}
            hm = {"x": d2.name, "y": d.name, "value": m0.name}
            if "Part-to-whole" in fams:
                add("stacked-bar", 100, f"Each {d.label} splits into {c2} parts of a whole.", roles)
            if c * c2 <= 600:
                add("heatmap", 96, f"{d.label} by {d2.label}: a heatmap shows all {c * c2} combinations in one grid.", hm)
            if c2 <= 6 and c <= 15:
                add("bar-chart", 90, f"Grouped bars compare {c2} {d2.label} values within each {d.label}.", roles, variant="grouped")
            if c2 <= 12:
                add("small-multiples", 80, f"One bar panel per {d2.label}, on a shared scale.",
                    {"x": d.name, "y": m0.name, "facet": d2.name}, variant="bar")
            add("stacked-bar", 70, "Stacked bars, if the parts add up to a meaningful total.", roles)
            add("table", 66, "A cross-tab keeps every value exact.", {"columns": None})
            return _finish(opts, fams, relationship), f
        if c == 2 and M == 1 and n == 2:
            add("sentence", 100, "Two numbers: a sentence carries this, here it is.", {"values": [m0.name], "by": d.name})
            add("bar-chart", 88, "Two bars on a zero baseline, if the page needs a picture of the gap.",
                {"x": d.name, "y": m0.name})
            add("stat-tile", 60, "Two tiles side by side.", {"values": [m0.name], "by": d.name})
            add("table", 40, "A two-row table.", {"columns": None})
            return _finish(opts, fams, relationship), f
        if M >= 2 and c >= 8 and n == c:
            add("scatterplot", 90 + (12 if "Correlation" in fams else 0),
                f"Two measures across {c} {d.label} values: a scatter shows whether they move together.",
                {"x": f.scatter_xy(usable)[0], "y": f.scatter_xy(usable)[1], "label": d.name})
        if c <= 25 and n == c:
            add("bar-chart", 100, f"{c} {d.label} values, one number each: sorted bars are the most accurate read.",
                {"x": d.name, "y": m0.name})
            if M >= 2 and _same_unit(usable[:2]):
                add("dot-plot", 92, f"Two measures per {d.label} on one axis: dots show the gap between them.",
                    {"x": d.name, "y": [m.name for m in usable[:2]]}, variant="paired")
            else:
                add("dot-plot", 78, "Dots on a shared axis are tidier than many bars when values are close.",
                    {"x": d.name, "y": m0.name})
            add("table", 58 if c > 10 else 45, "A ranked table for lookup.", {"columns": None})
        elif n == c:
            add("bar-chart", 90, f"{c} categories won't fit as bars; the top 15 with the rest folded into 'Other' will.",
                {"x": d.name, "y": m0.name}, variant="top")
            add("strip-plot", 88, f"All {c} values as dots on one axis show the spread and the outliers.",
                {"x": m0.name, "label": d.name})
            if c >= 30:
                add("histogram", 80, f"The distribution of {m0.label} across {c} {d.label} values.", {"x": m0.name})
            add("table", 75, f"{c} rows is a lookup job: a sorted table lets a reader find their own.", {"columns": None})
        else:
            # several rows per category: a distribution per group
            add("strip-plot", 95, f"{n} rows across {c} groups: a dot per row, one line per {d.label}, shows each group's spread.",
                {"x": m0.name, "y": d.name, "label": lab})
            add("bar-chart", 82, f"Bars of the median {m0.label} per {d.label} — say it's a median.",
                {"x": d.name, "y": m0.name}, variant="median")
            if M >= 2:
                add("scatterplot", 85 + (15 if "Correlation" in fams else 0),
                    f"Two measures over {n} rows: a scatter shows whether they move together"
                    + (f", colored by {d.label}." if c <= 8 else "."),
                    {"x": f.scatter_xy(usable)[0], "y": f.scatter_xy(usable)[1], "label": lab, "series": d.name if c <= 8 else None})
            add("histogram", 70, f"The distribution of {m0.label} overall.", {"x": m0.name})
            add("table", 50, f"A summary table per {d.label}.", {"columns": None})
        if has_geom:
            add("choropleth", 70 + (30 if "Spatial" in fams else 0),
                "Outlines are supplied, so the values can be mapped.",
                {"value": m0.name, "geometry": f.geometry.name if f.geometry else "__geojson__", "label": lab or d.name})
        elif any(g.geo for g in f.geo):
            _map_needs(add, f, fams)
        add("sentence", 25, "A one-line summary for alt text or the lede.", {"values": [m0.name]})
        return _finish(opts, fams, relationship), f

    # ---- no categories: measures over rows (labelled or not)
    one_named = len(f.mentioned) == 1
    if M >= 2:
        sx, sy = f.scatter_xy(usable)
        add("scatterplot", 80 if one_named else 100, f"{M} measures over {n} rows: a scatter of {profile.get(sy).label} against {profile.get(sx).label} shows whether they move together.",
            {"x": sx, "y": sy, "label": lab})
        if M >= 3:
            add("small-multiples", 72, f"One scatter panel per measure against {m0.label}.",
                {"y": m0.name, "x": [m.name for m in usable[1:4]], "label": lab}, variant="scatter")
    if n >= 20:
        add("histogram", 92 if (M == 1 or one_named) else 75, f"The distribution of {m0.label} across {n} rows.", {"x": m0.name})
    add("strip-plot", 85 if M == 1 else 68, f"Every row as a dot on one {m0.label} axis.", {"x": m0.name, "label": lab})
    if n <= 25 and lab:
        add("bar-chart", 88, f"{n} labelled rows, one number each: sorted bars.", {"x": lab, "y": m0.name})
    if has_geom:
        add("choropleth", 80 + (25 if "Spatial" in fams else 0),
            "Outlines are supplied, so the values can be mapped.",
            {"value": m0.name, "geometry": f.geometry.name if f.geometry else "__geojson__", "label": lab})
    elif any(g.geo for g in f.geo):
        _map_needs(add, f, fams)
    add("table", 60 if n <= 30 else 45, "Every row, sortable, for lookup.", {"columns": None})
    add("sentence", 40 if total_values > 4 else 95,
        "A one-line summary (range and median) for alt text or the lede." if total_values > 4
        else "A handful of numbers: a sentence carries them, here it is.", {"values": [m0.name]})
    return _finish(opts, fams, relationship), f


def _map_needs(add, f: Fields, fams: set[str]) -> None:
    g = next(g for g in f.geo if g.geo)
    add("choropleth", 50 + (20 if "Spatial" in fams else 0),
        f"{g.label} looks like {g.geo} geography, so a map is possible.",
        {"value": f.measures[0].name if f.measures else None, "key": g.name},
        drawable=False,
        needs=(f"Outlines to draw: pass --geometry FILE.geojson (with a property matching {g.name}), "
               "or include an SVG path column. Without them the ranking falls back to the forms above."))


_FAMILY_BOOST = {
    "Correlation": {"scatterplot": 14},
    "Change over time": {"line-chart": 8, "slope-chart": 6, "small-multiples": 3},
    "Ranking": {"bar-chart": 8, "dot-plot": 5},
    "Distribution": {"histogram": 14, "strip-plot": 12},
    "Part-to-whole": {"stacked-bar": 12, "stacked-area": 10},
    "Spatial": {"choropleth": 6},
    "Magnitude": {"bar-chart": 4},
    "Deviation": {"bar-chart": 3, "dot-plot": 3},
}


def _finish(opts: list[Option], fams: set[str], relationship: bool = False) -> list[Option]:
    for o in opts:
        if relationship and o.form == "scatterplot":
            o.score += 15
            o.reason += " The claim names two or more measures, so how they relate is the point."
        for fam in fams:
            o.score += _FAMILY_BOOST.get(fam, {}).get(o.form, 0)
    # One entry per (form, variant), best score kept.
    best: dict[tuple[str, str | None], Option] = {}
    for o in opts:
        k = (o.form, o.variant)
        if k not in best or o.score > best[k].score:
            best[k] = o
    ordered = sorted(best.values(), key=lambda o: (not o.drawable, -o.score))
    # Undrawable options go after every drawable one, but are still listed.
    for i, o in enumerate(ordered, 1):
        o.rank = i
    return ordered
