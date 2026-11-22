"""`vizier explore` — what is in this table? Look first; then show.

`show` answers "how do I show this finding?". `explore` comes before there is
a finding: many small, quick, honest views instead of one polished figure, in
a fixed order —

1. a field sheet: one compact distribution per field, with counts, missing and
   suppressed values, range, median, and oddities called out;
2. missingness: which fields, and which groups, are missing together;
3. relationships: pairs of measures ranked by Spearman's rank correlation,
   each as a small scatter, with a leverage check (recomputed without the rows
   that drive it); the strongest few also conditioned on the most plausible
   confounder among the other measures (partial rank correlation), side by
   side, so a relationship that vanishes when conditioned is visible;
4. breakdowns: each measure by each low-cardinality dimension, as strips with
   medians, ranked by how much the groups differ relative to the spread within
   them (Kruskal–Wallis epsilon²);
5. trends, when there is a time field;
6. outliers: the rows furthest from the pattern, as a table.

Exploration has its own honesty, attached as notes, never as refusal: how many
comparisons were examined (a pattern found by looking at many is a lead to
test, not a finding), n beside every statistic, ranking withheld when n is too
small, associations driven by a handful of rows marked, no causal language,
shared scales across small multiples of one measure.

Deterministic; no model, no network. Same table reading and renderers as `show`.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from statistics import median
from typing import Any

from .. import __version__
from . import render as R
from . import svg as S
from .profile import ColumnProfile, Profile, parse_number, parse_time, profile_table
from .rank import Option
from .table import Table, load_table, table_from_records

SCHEMA = "vizier/explore/v1"

MIN_PAIR_N = 10      # below this, a correlation is drawn on request but not ranked
MIN_GROUP_N = 5      # below this, a group is shown but not ranked
MAX_DIM_CARD = 30    # dimensions with more groups than this aren't broken down
CARD_W = 360         # contact-sheet view width (px)
WIDE_W = 1100         # side-by-side views
BIG_W = 680          # a single view redrawn alone

#: section caps before --max-views scaling
CAPS = {"distribution": 12, "missingness": 2, "relationship": 8, "conditioned": 3,
        "breakdown": 6, "trend": 4, "outliers": 1}
ORDER = list(CAPS)


# ------------------------------------------------------------------ statistics

def rankdata(xs: list[float]) -> list[float]:
    """Average ranks (1-based), ties share their mean rank."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def spearman(a: list[float], b: list[float]) -> float | None:
    return pearson(rankdata(a), rankdata(b))


def partial(rxy: float, rxz: float, ryz: float) -> float | None:
    d = (1 - rxz ** 2) * (1 - ryz ** 2)
    if d <= 1e-12:
        return None
    return (rxy - rxz * ryz) / math.sqrt(d)


def quantile(sorted_xs: list[float], q: float) -> float:
    if not sorted_xs:
        return float("nan")
    pos = (len(sorted_xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    return sorted_xs[lo] + (sorted_xs[hi] - sorted_xs[lo]) * (pos - lo)


def epsilon_squared(groups: list[list[float]]) -> float | None:
    """Kruskal–Wallis H / (n - 1): between-group difference relative to the spread."""
    allv = [v for g in groups for v in g]
    n = len(allv)
    if n < 3 or len(groups) < 2:
        return None
    ranks = rankdata(allv)
    pos = 0
    h = 0.0
    for g in groups:
        rs = ranks[pos:pos + len(g)]
        pos += len(g)
        h += len(g) * (sum(rs) / len(g) - (n + 1) / 2) ** 2
    h *= 12 / (n * (n + 1))
    return h / (n - 1)


def leverage_drop(a: list[float], b: list[float]) -> tuple[list[int], float | None]:
    """Recompute Spearman without the rows that pull hardest on it.

    Leverage on a rank correlation is the size of a row's centred-rank product;
    drop the top k — a handful: at least 5, about 2% of rows, at most 10."""
    n = len(a)
    k = min(10, max(5, round(n * 0.02)))
    if n - k < MIN_PAIR_N:
        return [], None
    ra, rb = rankdata(a), rankdata(b)
    c = (n + 1) / 2
    lev = sorted(range(n), key=lambda i: -abs((ra[i] - c) * (rb[i] - c)))
    drop = set(lev[:k])
    keep = [i for i in range(n) if i not in drop]
    return sorted(drop), spearman([a[i] for i in keep], [b[i] for i in keep])


def theil_sen(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    step = max(1, n // 120)  # cap the pair count for big tables
    idx = list(range(0, n, step))
    slopes = [(ys[j] - ys[i]) / (xs[j] - xs[i]) for a, i in enumerate(idx) for j in idx[a + 1:] if xs[j] != xs[i]]
    b = median(slopes) if slopes else 0.0
    return median([y - b * x for x, y in zip(xs, ys)]), b


def mad(xs: list[float]) -> float:
    m = median(xs)
    return median([abs(x - m) for x in xs]) or (max(xs) - min(xs)) / 10 or 1.0


# ------------------------------------------------------------------ helpers

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")[:40] or "x"


def subset(table: Table, keep: list[int], name: str | None = None) -> Table:
    return Table(
        columns=list(table.columns),
        rows=[table.rows[i] for i in keep],
        source=table.source,
        name=name or table.name,
        meta=table.meta,
        states={k: [v[i] for i in keep] for k, v in table.states.items()},
        package=table.package,
        missing_values=table.missing_values,
    )


def apply_where(table: Table, where: list[str]) -> Table:
    """Keep rows matching every `COL=VALUE` / `COL!=VALUE` clause."""
    keep = list(range(len(table)))
    for clause in where or []:
        neg = "!=" in clause
        if "=" not in clause:
            raise ValueError(f"--where wants COL=VALUE, got {clause!r}")
        col, val = clause.split("!=" if neg else "=", 1)
        col, val = col.strip(), val.strip()
        if col not in table.columns:
            raise ValueError(f"--where: no column named {col!r}")
        vnum = parse_number(val)

        def match(cell, _val=val, _vnum=vnum):
            if cell is None:
                return _val == ""
            if cell == _val:
                return True
            return _vnum is not None and parse_number(cell) == _vnum

        keep = [i for i in keep if match(table.rows[i].get(col)) != neg]
    return subset(table, keep)


ROLE_OUT = {"measure": "measure", "dimension": "dimension", "time": "time", "geography": "geography",
            "label": "label", "identifier": "id", "geometry": "geography"}


def _state_key(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def oddities(c: ColumnProfile, table: Table) -> list[str]:
    """Things worth a second look in one field — said plainly, with counts."""
    out: list[str] = []
    n = c.n
    present = c.n_present
    if n and c.n_missing / n > 0.2:
        out.append(f"{c.n_missing} of {n} values missing ({c.n_missing / n:.0%}).")
    if present and c.n_distinct == 1:
        out.append("Every present value is the same.")
        return out
    raw = [v for v in table.column(c.name) if v is not None]
    if c.role == "measure" and present:
        xs = sorted(x for x in (parse_number(v) for v in raw) if x is not None)
        if not xs:
            return out
        q1, q3, med = quantile(xs, .25), quantile(xs, .75), quantile(xs, .5)
        iqr = q3 - q1
        counts: dict[float, int] = {}
        for x in xs:
            counts[x] = counts.get(x, 0) + 1
        top, topn = max(counts.items(), key=lambda kv: kv[1])
        if topn / len(xs) >= 0.8 and len(counts) > 1:
            out.append(f"One value dominates: {S.fmt(top, c.unit)} is {topn} of {len(xs)} ({topn / len(xs):.0%}).")
        elif topn >= 5 and topn / len(xs) >= 0.05 and len(counts) > 10:
            # A spike stands well above its neighbouring values, not just above the typical count.
            keys = sorted(counts)
            k = keys.index(top)
            neigh = [counts[x] for x in keys[max(0, k - 2):k] + keys[k + 1:k + 3]]
            near = sum(neigh) / len(neigh) if neigh else 1
            round_ = top == 0 or (float(top).is_integer() and abs(top) >= 10 and top % 10 == 0) or (
                float(top).is_integer() and any(not float(x).is_integer() for x in xs[:200]))
            if topn >= 3 * max(1.0, near) and round_:
                out.append(f"Spike at a round number: {S.fmt(top, c.unit)} appears {topn} times "
                           f"({topn / len(xs):.0%}) — check for a default, a cap, or a fill-in value.")
        sentinels = [x for x in (-1, -9, -99, -999, -9999, 999, 9999, 99999) if counts.get(float(x), 0) >= 1 and (x < 0 or x > 10 * max(1.0, abs(q3)))]
        if sentinels:
            out.append(f"Possible missing-value codes: {', '.join(S.fmt(float(s)) for s in sentinels)} "
                       f"— declare them in datapackage missingValues if they mean 'no data'.")
        if iqr > 0:
            far = sum(1 for x in xs if x > q3 + 3 * iqr or x < q1 - 3 * iqr)
            if far and far / len(xs) <= 0.1:
                side = "high" if xs[-1] - q3 > q1 - xs[0] else "low"
                out.append(f"Long {side} tail: {far} value(s) more than 3 IQR beyond the quartiles"
                           f" (max {S.fmt(xs[-1], c.unit)}, median {S.fmt(med, c.unit)}).")
        unit = (c.unit or "").lower()
        nl = c.name.lower()
        if unit == "%" and (xs[0] < 0 or xs[-1] > 100):
            bad = sum(1 for x in xs if x < 0 or x > 100)
            out.append(f"Impossible for a percentage: {bad} value(s) below 0 or above 100.")
        elif xs[0] < 0 and (unit in ("%", "usd") or re.search(r"(count|number|population|pop|people|persons|residents|students|rate|income|age|total|households)", nl)):
            bad = sum(1 for x in xs if x < 0)
            out.append(f"{bad} negative value(s), which this kind of measure can't take.")
    if c.geo == "lat":
        xs = [x for x in (parse_number(v) for v in raw) if x is not None]
        if any(abs(x) > 90 for x in xs):
            out.append("Latitude outside ±90.")
    if c.geo == "lon":
        xs = [x for x in (parse_number(v) for v in raw) if x is not None]
        if any(abs(x) > 180 for x in xs):
            out.append("Longitude outside ±180.")
    if c.role == "time" and c.max is not None:
        if c.max > date.today().year + 1:
            out.append(f"Dates in the future (latest {S.fmt_time(c.max, c.granularity)}).")
        if c.min is not None and c.min < 1800:
            out.append(f"Dates before 1800 (earliest {S.fmt_time(c.min, c.granularity)}) — a placeholder?")
    if c.role in ("dimension", "label", "geography") and c.top and present:
        v, k = c.top[0]
        if k / present >= 0.8 and c.n_distinct > 1:
            out.append(f"One value dominates: '{v}' is {k} of {present} ({k / present:.0%}).")
        variants: dict[str, set[str]] = {}
        for val in set(raw):
            variants.setdefault(re.sub(r"\s+", " ", val.strip().lower()), set()).add(val)
        dup = [sorted(vs) for vs in variants.values() if len(vs) > 1]
        if dup:
            out.append("Spelling variants that may be the same value: " + "; ".join(" / ".join(d[:3]) for d in dup[:3]) + ".")
    return out


def field_record(c: ColumnProfile, table: Table) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "name": c.name,
        "role": ROLE_OUT.get(c.role, c.role),
        "type": c.kind,
        "n": c.n,
        "missing": c.n_missing,
        "distinct": c.n_distinct,
        "oddities": oddities(c, table) if c.role != "geometry" else [],
    }
    if c.label and c.label != c.name:
        rec["label"] = c.label
    if c.unit:
        rec["unit"] = c.unit
    if c.description:
        rec["description"] = c.description
    if c.states:
        rec["states"] = {_state_key(k): v for k, v in c.states.items()}
    if c.role == "measure" and c.n_present:
        xs = sorted(x for x in (parse_number(v) for v in table.column(c.name)) if x is not None)
        rec["summary"] = {"min": xs[0], "max": xs[-1], "median": quantile(xs, .5), "q1": quantile(xs, .25),
                          "q3": quantile(xs, .75), "mean": sum(xs) / len(xs)}
    if c.role == "time" and c.min is not None:
        rec["summary"] = {"min": c.min, "max": c.max}
        rec["granularity"] = c.granularity
    if c.role in ("dimension", "label", "geography", "identifier") and c.top:
        rec["top"] = [{"value": v, "n": k} for v, k in c.top]
    return rec


# ------------------------------------------------------------------ views

@dataclass
class View:
    id: str
    kind: str
    title: str
    what: str
    fields: list[str]
    form: str
    n: int
    stat: dict | None = None
    caution: str | None = None
    show_args: dict = field(default_factory=dict)
    score: float = 0.0
    rank: int | None = None
    withheld: bool = False
    draw: Any = None           # callable(width) -> svg
    html: str | None = None    # for table-form views
    csv: str | None = None
    file: str | None = None
    wide: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = {"id": self.id, "kind": self.kind, "title": self.title, "what": self.what, "fields": self.fields,
             "form": self.form, "file": self.file, "n": self.n, "show_args": self.show_args}
        if self.stat is not None:
            d["stat"] = self.stat
        if self.caution:
            d["caution"] = self.caution
        if self.rank is not None:
            d["rank"] = self.rank
        if self.withheld:
            d["withheld"] = True
        return d


def _draw(table: Table, profile: Profile, form: str, roles: dict, words: S.Words, width: int, *,
          variant: str | None = None, view_id: str | None = None, applied_notes: bool = True, **ctx_kw) -> str:
    o = Option(form=form, title=form, score=0, reason="", roles=roles, variant=variant)
    ctx = R.Ctx(table=table, profile=profile, option=o, words=words, width=width, **ctx_kw)
    body, h = R.RENDERERS[form](ctx)
    if not words.notes and applied_notes:
        words.notes = [a["detail"] for a in ctx.applied]
    return S.frame(body, h, words, width=width, form=form, compact=width < BIG_W, view_id=view_id)


def _fmt_r(r: float | None) -> str:
    return "–" if r is None else f"{r:+.2f}"


class Explorer:
    def __init__(self, table: Table, *, focus: str | None = None, max_views: int = 24, prefix: str = ""):
        self.table = table
        self.profile = profile_table(table)
        self.focus = focus
        self.max_views = max_views
        self.prefix = prefix
        self.notes: list[str] = []
        self.pairs_examined = 0
        self.breakdowns_examined = 0
        p = self.profile
        if focus and p.get(focus) is None:
            raise ValueError(f"--focus: no column named {focus!r}")
        self.measures = [c for c in p.measures if c.n_present >= 3 and c.n_distinct > 1]
        self.dims = [c for c in p.columns if (c.role == "dimension" or (c.role == "geography" and c.kind == "category"))
                     and 2 <= c.n_distinct <= MAX_DIM_CARD]
        self.time = next((c for c in p.times if c.n_distinct >= 3), None)
        self.label = next((c for c in p.columns if c.role == "label"), None) or \
            next((c for c in p.columns if c.role in ("identifier",) or (c.role == "geography" and c.kind == "identifier")), None)
        self._num = {c.name: [parse_number(v) for v in table.column(c.name)] for c in self.measures}

    def vid(self, s: str) -> str:
        return self.prefix + s

    def nums(self, col: str) -> list[float | None]:
        return self._num[col]

    def pair(self, a: str, b: str, rows: set[int] | None = None) -> tuple[list[int], list[float], list[float]]:
        A, B = self.nums(a), self.nums(b)
        idx = [i for i in range(len(A)) if A[i] is not None and B[i] is not None and (rows is None or i in rows)]
        return idx, [A[i] for i in idx], [B[i] for i in idx]

    def lab(self, col: str) -> str:
        c = self.profile.get(col)
        return c.label if c else col

    def unit(self, col: str) -> str | None:
        c = self.profile.get(col)
        return c.unit if c else None

    # ---------------------------------------------------------- 1. field sheet
    def distributions(self) -> list[View]:
        p, t = self.profile, self.table
        cols = [c for c in p.columns if c.role != "geometry"]
        if self.focus:
            cols.sort(key=lambda c: c.name != self.focus)
        out = []
        for c in cols:
            vid = self.vid(f"dist-{slug(c.name)}")
            rec_odd = oddities(c, t)
            stats = [f"n={c.n_present:,} of {c.n:,}"]
            if c.n_missing:
                stats.append(f"{c.n_missing} missing" + (f" ({c.n_suppressed} suppressed / not collected)" if c.n_suppressed else ""))
            if c.role == "measure" and c.n_present:
                stats.append(f"{S.fmt(c.min, c.unit)}–{S.fmt(c.max, c.unit)}, median {S.fmt(c.median, c.unit)}")
            elif c.role == "time" and c.min is not None:
                stats.append(f"{S.fmt_time(c.min, c.granularity)}–{S.fmt_time(c.max, c.granularity)} ({c.granularity})")
            else:
                stats.append(f"{c.n_distinct:,} distinct")
            sub = " · ".join(stats)
            words = S.Words(title=c.label, subtitle=sub, notes=list(rec_odd))
            if c.role == "measure" and c.n_present:
                form, what = "histogram", f"How {c.label} is distributed across {c.n_present:,} rows."

                def draw(w, _c=c, _words=words, _vid=vid):
                    return _draw(t, p, "histogram", {"x": _c.name}, _copy(_words), w, view_id=_vid,
                                 height=170 if w < BIG_W else None, applied_notes=False)
                show_args = {"x": c.name}
            elif c.role == "time" and c.n_present:
                form, what = "bar-chart", f"How many rows fall in each {self._period(c)} of {c.label}."
                draw = self._timeline_drawer(c, words, vid)
                show_args = {"x": c.name}
            elif c.n_present and c.n_distinct >= 0.9 * c.n_present and c.n_present > 12:
                # Nearly every value is distinct: a bar of counts would be all ones. Describe it instead.
                from html import escape as _e
                kind = "an identifier" if c.role in ("identifier",) or (c.role == "geography" and c.kind == "identifier") else "a label"
                ex = ", ".join(_e(str(x)) for x in c.examples[:4])
                form, what = "none", f"{c.label} names rows ({kind}): {c.n_distinct:,} distinct values in {c.n_present:,} rows."
                draw = None
                show_args = {}
                dup = [v for v, k in (c.top or []) if k > 1][:3]
                html_ = (f"<strong>{_e(c.label)}</strong><p class=meta>{_e(sub)}</p><p class=what>e.g. {ex}"
                         + (f"</p><p class=caution>Repeated: {_e(', '.join(dup))}" if dup else "") + "</p>")
                out.append(View(id=vid, kind="distribution", title=c.label, what=what, fields=[c.name], form=form,
                                n=c.n_present, caution=("; ".join(rec_odd) or None), show_args=show_args, html=html_))
                continue
            elif c.n_present:
                form, what = "bar-chart", (f"The most common values of {c.label}." if c.n_distinct > 8
                                           else f"How many rows take each value of {c.label}.")
                draw = self._topvalues_drawer(c, words, vid)
                show_args = {"x": c.name}
            else:
                form, what = "none", f"{c.label} has no present values."
                draw = None
                show_args = {}
            out.append(View(id=vid, kind="distribution", title=c.label, what=what, fields=[c.name], form=form,
                            n=c.n_present, caution=("; ".join(rec_odd) or None), show_args=show_args, draw=draw))
        return out

    def _period(self, c: ColumnProfile) -> str:
        if c.granularity in ("day", "datetime", "month") and c.max is not None and c.min is not None and c.max - c.min < 3:
            return "month"
        return "year"

    def _timeline_drawer(self, c: ColumnProfile, words: S.Words, vid: str):
        period = self._period(c)
        counts: dict[float, int] = {}
        for v in self.table.column(c.name):
            tv = parse_time(v, year_ok=True) if v is not None else None
            if tv is None:
                continue
            k = math.floor(tv[0]) if period == "year" else math.floor(tv[0] * 12 + 1e-6) / 12
            counts[k] = counts.get(k, 0) + 1
        recs = [{"period": (str(int(k)) if period == "year" else f"{int(k)}-{int(round((k % 1) * 12)) + 1:02d}"), "rows": n}
                for k, n in sorted(counts.items())]
        dt = table_from_records(recs, name=c.name)
        dp = profile_table(dt)
        dp.get("period").role = "time"

        def draw(w):
            return _draw(dt, dp, "bar-chart", {"x": "period", "y": "rows"}, _copy(words), w, variant="time",
                         view_id=vid, height=170 if w < BIG_W else None)
        return draw

    def _topvalues_drawer(self, c: ColumnProfile, words: S.Words, vid: str):
        counts: dict[str, int] = {}
        for v in self.table.column(c.name):
            if v is not None:
                counts[v] = counts.get(v, 0) + 1
        items = sorted(counts.items(), key=lambda kv: -kv[1])
        top = items[:8]
        rest = items[8:]
        recs = [{"value": k, "rows": n} for k, n in top]
        if rest:
            recs.append({"value": f"{len(rest)} other values", "rows": sum(n for _, n in rest)})
        dt = table_from_records(recs, name=c.name)
        dp = profile_table(dt)
        dp.get("value").role = "dimension"

        def draw(w):
            return _draw(dt, dp, "bar-chart", {"x": "value", "y": "rows"}, _copy(words, x_label="Rows"), w, view_id=vid,
                         keep_order=True)
        return draw

    # ---------------------------------------------------------- 2. missingness
    def missingness(self) -> list[View]:
        p, t = self.profile, self.table
        cols = [c for c in p.columns if c.role not in ("geometry",) and c.n_missing]
        if not cols:
            self.notes.append("No missing values in any field.")
            return []
        out = []
        n = len(t)
        miss = {c.name: [t.rows[i].get(c.name) is None for i in range(n)] for c in cols}
        # fields missing together
        if len(cols) >= 2:
            recs = []
            for a in cols:
                for b in cols:
                    both = sum(1 for i in range(n) if miss[a.name][i] and miss[b.name][i])
                    recs.append({"field": a.label, "with": b.label, "rows": both})
            dt = table_from_records(recs)
            dp = profile_table(dt)
            for nm in ("field", "with"):
                dp.get(nm).role = "dimension"
            vid = self.vid("missing-together")
            words = S.Words(title="Fields missing together",
                            subtitle=f"Rows where both fields are missing (diagonal: each field alone). n={n:,} rows.")
            pairs = sorted(((a.label, b.label, sum(1 for i in range(n) if miss[a.name][i] and miss[b.name][i]))
                            for k, a in enumerate(cols) for b in cols[k + 1:]), key=lambda x: -x[2])
            top = pairs[0] if pairs else None
            out.append(View(
                id=vid, kind="missingness", title="Fields missing together",
                what="Each cell counts the rows where both fields are missing; a dense off-diagonal cell means those gaps tend to come together.",
                fields=[c.name for c in cols], form="heatmap", n=n,
                stat={"name": "rows missing both (largest pair)", "value": top[2], "n": n} if top else None,
                show_args={},
                draw=lambda w, _dt=dt, _dp=dp, _words=words, _vid=vid: _draw(
                    _dt, _dp, "heatmap", {"x": "with", "y": "field", "value": "rows"}, _copy(_words), max(w, 420), view_id=_vid)))
        # by group
        dim = next((d for d in self.dims if d.n_distinct <= 30), None)
        if dim:
            G = t.column(dim.name)
            groups = [g for g, _ in sorted({g: 0 for g in G if g is not None}.items())]
            recs = []
            for c in cols:
                for g in groups:
                    idx = [i for i in range(n) if G[i] == g]
                    m = sum(1 for i in idx if miss[c.name][i])
                    recs.append({"field": c.label, "group": g, "missing_pct": round(100 * m / len(idx), 1) if idx else None})
            dt = table_from_records(recs)
            dp = profile_table(dt)
            dp.get("field").role = "dimension"
            dp.get("group").role = "dimension"
            dp.get("missing_pct").unit = "%"
            dp.get("missing_pct").label = "Missing"
            vid = self.vid(f"missing-by-{slug(dim.name)}")
            words = S.Words(title=f"Missing values by {dim.label.lower()}",
                            subtitle=f"Share of rows missing each field, per {dim.label.lower()} ({len(groups)} groups).")
            out.append(View(
                id=vid, kind="missingness", title=words.title,
                what=f"Whether gaps cluster in some {dim.label.lower()} groups rather than spreading evenly.",
                fields=[c.name for c in cols] + [dim.name], form="heatmap", n=n, show_args={}, wide=True,
                draw=lambda w, _dt=dt, _dp=dp, _words=words, _vid=vid: _draw(
                    _dt, _dp, "heatmap", {"x": "group", "y": "field", "value": "missing_pct"}, _copy(_words),
                    max(w, WIDE_W), view_id=_vid)))
        return out

    # ---------------------------------------------------------- 3. relationships
    def relationships(self) -> tuple[list[View], list[View]]:
        ms = self.measures
        pairs = [(a, b) for k, a in enumerate(ms) for b in ms[k + 1:]]
        if self.focus and self.profile.get(self.focus) in ms:
            pairs = [(a, b) for a, b in pairs if self.focus in (a.name, b.name)]
            pairs = [((b, a) if b.name == self.focus else (a, b)) for a, b in pairs]  # focus on x
        self.pairs_examined = len(pairs)
        rho: dict[tuple[str, str], tuple[float | None, int]] = {}
        for a, b in [(a, b) for k, a in enumerate(ms) for b in ms[k + 1:]]:
            idx, A, B = self.pair(a.name, b.name)
            r = spearman(A, B) if len(idx) >= 3 else None
            rho[(a.name, b.name)] = rho[(b.name, a.name)] = (r, len(idx))
        views = []
        for a, b in pairs:
            r, n = rho[(a.name, b.name)]
            idx, A, B = self.pair(a.name, b.name)
            vid = self.vid(f"rel-{slug(a.name)}--{slug(b.name)}")
            stat: dict[str, Any] = {"name": "spearman_rho", "value": None if r is None else round(r, 3), "n": n}
            caution = None
            highlight: set[int] = set()
            withheld = n < MIN_PAIR_N or r is None
            if not withheld:
                dropped, r2 = leverage_drop(A, B)
                if r2 is not None:
                    stat["without_top_rows"] = {"dropped": len(dropped), "value": round(r2, 3)}
                    if abs(r) >= 0.2 and (abs(r2) < 0.5 * abs(r) or (r2 * r < 0)):
                        caution = (f"Driven by a handful of rows: ρ {_fmt_r(r)} with all {n}, {_fmt_r(r2)} without the "
                                   f"{len(dropped)} highest-leverage rows (ringed).")
                        highlight = {idx[i] for i in dropped}
            else:
                caution = f"n={n} is too small to rank a correlation; drawn for reference, not ranked."
            sub = (f"Spearman ρ {_fmt_r(r)}, n={n:,}" + (f"; without {stat['without_top_rows']['dropped']} top-leverage rows "
                   f"ρ {_fmt_r(stat['without_top_rows']['value'])}" if "without_top_rows" in stat else ""))
            words = S.Words(title=f"{b.label} vs {a.label.lower()}", subtitle=sub, notes=[caution] if caution else [])
            lab = self.label.name if self.label else None
            v = View(id=vid, kind="relationship", title=words.title,
                     what=f"Each dot is one row; ρ measures how consistently {b.label.lower()} rises (or falls) as {a.label.lower()} rises.",
                     fields=[a.name, b.name], form="scatterplot", n=n, stat=stat, caution=caution,
                     show_args={"x": a.name, "y": b.name}, score=abs(r) if r is not None else 0, withheld=withheld,
                     draw=lambda w, _a=a.name, _b=b.name, _words=words, _vid=vid, _hl=highlight, _lab=lab: _draw(
                         self.table, self.profile, "scatterplot", {"x": _a, "y": _b, "label": _lab}, _copy(_words), w,
                         view_id=_vid, highlight=_hl, height=300 if w < BIG_W else None))
            views.append(v)
        ranked = sorted([v for v in views if not v.withheld], key=lambda v: -v.score)
        for i, v in enumerate(ranked, 1):
            v.rank = i
        withheld = [v for v in views if v.withheld]
        if withheld:
            self.notes.append(f"{len(withheld)} pair(s) have fewer than {MIN_PAIR_N} rows with both values; "
                              "their correlations are listed without a rank and drawn only on request (--view).")
        # conditioned views for the strongest few
        cond = []
        for v in ranked[:CAPS["conditioned"]]:
            a, b = v.fields
            others = [m for m in ms if m.name not in (a, b)]
            best = None
            for z in others:
                rxz, _ = rho[(a, z.name)]
                ryz, _ = rho[(b, z.name)]
                if rxz is None or ryz is None:
                    continue
                score = abs(rxz * ryz)
                if best is None or score > best[0]:
                    best = (score, z, rxz, ryz)
            if best is None:
                continue
            _, z, rxz, ryz = best
            # partial correlation on the rows that have all three
            idx = [i for i in range(len(self.table)) if all(self.nums(c)[i] is not None for c in (a, b, z.name))]
            if len(idx) < MIN_PAIR_N:
                continue
            A = [self.nums(a)[i] for i in idx]
            B = [self.nums(b)[i] for i in idx]
            Z = [self.nums(z.name)[i] for i in idx]
            rab, raz, rbz = spearman(A, B), spearman(A, Z), spearman(B, Z)
            if None in (rab, raz, rbz):
                continue
            pr = partial(rab, raz, rbz)
            zs = sorted(Z)
            cut1, cut2 = quantile(zs, 1 / 3), quantile(zs, 2 / 3)
            thirds = [set(), set(), set()]
            for i, zv in zip(idx, Z):
                thirds[0 if zv <= cut1 else (1 if zv <= cut2 else 2)].add(i)
            panel_r = []
            for th in thirds:
                _, ta, tb = self.pair(a, b, th)
                panel_r.append((spearman(ta, tb) if len(ta) >= MIN_PAIR_N else None, len(ta)))
            vanished = pr is not None and abs(rab) >= 0.2 and abs(pr) < 0.5 * abs(rab)
            caution = (f"Mostly explained by {z.label.lower()}: ρ {_fmt_r(rab)} overall, partial ρ {_fmt_r(pr)} holding it fixed."
                       if vanished else None)
            vid = self.vid(f"cond-{slug(a)}--{slug(b)}--{slug(z.name)}")
            title = f"{self.lab(b)} vs {self.lab(a).lower()}, holding {z.label.lower()} fixed"
            sub = (f"Overall ρ {_fmt_r(rab)} (n={len(idx):,}); partial ρ given {z.label.lower()} {_fmt_r(pr)}. "
                   f"Panels split rows into thirds of {z.label.lower()}; scales are shared.")
            words = S.Words(title=title, subtitle=sub, notes=[caution] if caution else [])
            cond.append(View(
                id=vid, kind="conditioned", title=title,
                what=f"If the pattern in the first panel fades inside each third of {z.label.lower()}, {z.label.lower()} may be doing the work.",
                fields=[a, b, z.name], form="small-multiples", n=len(idx),
                stat={"name": "partial_spearman_rho", "value": None if pr is None else round(pr, 3), "n": len(idx),
                      "overall": round(rab, 3), "given": z.name,
                      "panels": [{"third": k + 1, "rho": None if pr_ is None else round(pr_, 3), "n": n_}
                                 for k, (pr_, n_) in enumerate(panel_r)]},
                caution=caution, show_args={"x": a, "y": b}, score=abs(rab), wide=True,
                draw=lambda w, _a=a, _b=b, _z=z, _th=thirds, _pr=panel_r, _words=words, _vid=vid, _rab=rab, _n=len(idx):
                    self._draw_conditioned(_a, _b, _z, _th, _pr, _rab, _n, _words, max(w, WIDE_W), _vid)))
        return ranked + withheld, cond

    def _draw_conditioned(self, a, b, z, thirds, panel_r, rab, n, words, width, vid) -> str:
        o = Option(form="scatterplot", title="", score=0, reason="", roles={"x": a, "y": b})
        ctx = R.Ctx(table=self.table, profile=self.profile, option=o, words=words, width=width)
        A = [x for x in self.nums(a) if x is not None]
        B = [x for x in self.nums(b) if x is not None]
        xd = S.nice_domain(min(A), max(A), 4)
        yd = S.nice_domain(min(B), max(B), 4)
        pw = (width - 24) / 4
        ph = 250
        allrows = set().union(*thirds)
        zs = sorted(v for v in self.nums(z.name) if v is not None)
        labels = [("All rows", f"ρ {_fmt_r(rab)}, n={n}")]
        edges = [zs[0], quantile(zs, 1 / 3), quantile(zs, 2 / 3), zs[-1]]
        names = ["Low", "Middle", "High"]
        for k, (r, nn) in enumerate(panel_r):
            labels.append((f"{names[k]} third: {S.fmt(edges[k], z.unit, compact=True)}–{S.fmt(edges[k + 1], z.unit, compact=True)}",
                           f"ρ {_fmt_r(r)}, n={nn}" if r is not None else f"n={nn}, too few to rank"))
        parts = []
        for k, rows in enumerate([allrows] + thirds):
            body, _ = R.render_scatter(ctx, panel=(0, 0, pw, ph), shared=yd, shared_x=xd, rows=rows)
            l1, l2 = labels[k]
            parts.append(f'<g transform="translate({12 + k * pw:.1f},52)">'
                         f'{S.text(44, -18, S.truncate(l1, 11, pw - 50), size=11, fill=S.INK, weight="600")}'
                         f'{S.text(44, -4, l2, size=11, fill=S.INK2)}{body}</g>')
        parts.insert(0, S.text(12, 12, f"y: {self.lab(b)}{S.unit_suffix(self.unit(b))} · panels: all rows, then thirds of "
                               f"{z.label.lower()} · shared scales", size=12, fill=S.INK2))
        return S.frame("\n".join(parts), ph + 56, words, width=width, form="small-multiples", compact=True, view_id=vid)

    # ---------------------------------------------------------- 4. breakdowns
    def breakdowns(self) -> list[View]:
        out = []
        fc = self.profile.get(self.focus) if self.focus else None
        combos = [(m, d) for m in self.measures for d in self.dims]
        if fc is not None and fc.role == "measure":
            combos = [(m, d) for m, d in combos if m.name == fc.name]
        elif fc is not None:
            combos = [(m, d) for m, d in combos if d.name == fc.name]
        self.breakdowns_examined = len(combos)
        for m, d in combos:
            V = self.nums(m.name)
            G = self.table.column(d.name)
            groups: dict[str, list[float]] = {}
            for v, g in zip(V, G):
                if v is not None and g is not None:
                    groups.setdefault(g, []).append(v)
            big = [vs for vs in groups.values() if len(vs) >= MIN_GROUP_N]
            small = [g for g, vs in groups.items() if len(vs) < MIN_GROUP_N]
            n = sum(len(vs) for vs in groups.values())
            eps = epsilon_squared(big) if len(big) >= 2 else None
            vid = self.vid(f"brk-{slug(m.name)}--{slug(d.name)}")
            caution = None
            if small:
                caution = (f"{len(small)} group(s) have fewer than {MIN_GROUP_N} rows; they are drawn, labelled with n, "
                           "and left out of the ranking.")
            withheld = eps is None
            if withheld and not caution:
                caution = f"Fewer than two groups with {MIN_GROUP_N}+ rows; not ranked."
            sub = (f"ε² {eps:.2f} (groups differ by {'a lot' if eps >= 0.26 else 'a moderate amount' if eps >= 0.08 else 'little'} "
                   f"relative to the spread within them), n={n:,} in {len(groups)} groups" if eps is not None
                   else f"n={n:,} in {len(groups)} groups")
            words = S.Words(title=f"{m.label} by {d.label.lower()}", subtitle=sub + ". Line = group median.",
                            notes=[caution] if caution else [])
            lab = self.label.name if self.label else None
            out.append(View(
                id=vid, kind="breakdown", title=words.title,
                what=f"Every row as a dot, one line per {d.label.lower()}, ordered by median — the spread is shown, not just an average.",
                fields=[m.name, d.name], form="strip-plot", n=n,
                stat={"name": "epsilon_squared", "value": None if eps is None else round(eps, 3), "n": n,
                      "groups": len(groups), "groups_ranked": len(big)},
                caution=caution, show_args={"x": d.name, "y": m.name}, score=eps or 0, withheld=withheld,
                draw=lambda w, _m=m.name, _d=d.name, _words=words, _vid=vid, _lab=lab: _draw(
                    self.table, self.profile, "strip-plot", {"x": _m, "y": _d, "label": _lab}, _copy(_words), w,
                    view_id=_vid, min_group=MIN_GROUP_N, label_n=True)))
        ranked = sorted([v for v in out if not v.withheld], key=lambda v: -v.score)
        for i, v in enumerate(ranked, 1):
            v.rank = i
        return ranked + [v for v in out if v.withheld]

    # ---------------------------------------------------------- 5. trends
    def trends(self) -> list[View]:
        if self.time is None:
            return []
        T = self.time
        tv = [parse_time(v, year_ok=True) if v is not None else None for v in self.table.column(T.name)]
        tvals = [t[0] if t else None for t in tv]
        series = next((d for d in self.dims if d.n_distinct <= 6), None)
        ms = self.measures
        if self.focus and self.profile.get(self.focus) in ms:
            ms = [self.profile.get(self.focus)]
        out = []
        for m in ms:
            V = self.nums(m.name)
            S_ = self.table.column(series.name) if series else [None] * len(V)
            cells: dict[tuple, list[float]] = {}
            for t, v, s in zip(tvals, V, S_):
                if t is None:
                    continue
                cells.setdefault((t, s), [])
                if v is not None:
                    cells[(t, s)].append(v)
            multi = any(len(vs) > 1 for vs in cells.values())
            recs = [{"t": S.fmt_time(t, T.granularity) if T.granularity in ("year", "month", "quarter") else str(t),
                     "_t": t, "series": s, "value": (median(vs) if vs else None)} for (t, s), vs in sorted(cells.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))]
            dt = table_from_records([{"t": r["_t"], "series": r["series"], "value": r["value"]} for r in recs])
            dp = profile_table(dt)
            dp.get("t").role = "time"
            dp.get("t").granularity = T.granularity
            dp.get("t").label = T.label
            dp.get("value").label = ("Median " + m.label.lower()) if multi else m.label
            dp.get("value").unit = m.unit
            vid = self.vid(f"trend-{slug(m.name)}")
            nrows = sum(len(vs) for vs in cells.values())
            sub = (f"n={nrows:,} rows" + (f"; median of several rows per {T.granularity or 'period'}" if multi else "")
                   + (f"; one line per {series.label.lower()}" if series else ""))
            words = S.Words(title=f"{m.label} over {T.label.lower()}", subtitle=sub)
            roles = {"x": "t", "y": "value", "series": "series" if series else None}
            out.append(View(
                id=vid, kind="trend", title=words.title, what=f"How {m.label.lower()} moves over {T.label.lower()}; gaps are missing periods.",
                fields=[T.name, m.name] + ([series.name] if series else []), form="line-chart", n=nrows,
                show_args={"x": T.name, "y": m.name, **({"series": series.name} if series else {})},
                draw=lambda w, _dt=dt, _dp=dp, _words=words, _vid=vid, _roles=roles: _draw(
                    _dt, _dp, "line-chart", {k: v for k, v in _roles.items() if v}, _copy(_words), w, view_id=_vid,
                    height=220 if w < BIG_W else None)))
        return out

    # ---------------------------------------------------------- 6. outliers
    def outliers(self, rels: list[View], brks: list[View]) -> list[View]:
        found: dict[int, tuple[float, str]] = {}
        for v in [r for r in rels if not r.withheld][:3]:
            a, b = v.fields
            idx, A, B = self.pair(a, b)
            if len(idx) < MIN_PAIR_N:
                continue
            ic, sl = theil_sen(A, B)
            res = [y - (ic + sl * x) for x, y in zip(A, B)]
            s = mad(res)
            for i, rr in zip(idx, res):
                z = abs(rr) / (1.4826 * s)
                if z > 3.5 and z > found.get(i, (0, ""))[0]:
                    found[i] = (z, f"{self.lab(b)} {S.fmt(self.nums(b)[i], self.unit(b))} is far from the "
                                   f"{self.lab(b).lower()}–{self.lab(a).lower()} pattern ({z:.1f} robust SDs)")
        for v in [r for r in brks if not r.withheld][:3]:
            m, d = v.fields
            V, G = self.nums(m), self.table.column(d)
            groups: dict[str, list[int]] = {}
            for i, (x, g) in enumerate(zip(V, G)):
                if x is not None and g is not None:
                    groups.setdefault(g, []).append(i)
            for g, idx in groups.items():
                if len(idx) < MIN_GROUP_N:
                    continue
                xs = [V[i] for i in idx]
                md, s = median(xs), mad(xs)
                for i in idx:
                    z = abs(V[i] - md) / (1.4826 * s)
                    if z > 3.5 and z > found.get(i, (0, ""))[0]:
                        found[i] = (z, f"{self.lab(m)} {S.fmt(V[i], self.unit(m))} vs a {g} median of "
                                       f"{S.fmt(md, self.unit(m))} ({z:.1f} robust SDs)")
        if not found:
            return []
        top = sorted(found.items(), key=lambda kv: -kv[1][0])[:15]
        labcol = self.label.name if self.label else None
        rows = []
        for i, (z, why) in top:
            name = (self.table.rows[i].get(labcol) if labcol else None) or f"row {i + 1}"
            rows.append({"row": i + 1, "label": name, "score": round(z, 1), "why": why})
        from html import escape
        html = ("<strong>Rows furthest from the pattern</strong><div class=tbl><table><thead><tr><th>Row</th><th>" + escape(self.lab(labcol) if labcol else "Label")
                + "</th><th class=num>Robust SDs</th><th>Why it stands out</th></tr></thead><tbody>"
                + "".join(f"<tr><td>{r['row']}</td><td>{escape(str(r['label']))}</td><td class=num>{r['score']}</td>"
                          f"<td style='white-space:normal'>{escape(r['why'])}</td></tr>" for r in rows)
                + "</tbody></table></div>")
        import csv
        import io
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["row", "label", "score", "why"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        return [View(id=self.vid("outliers"), kind="outliers", title="Rows furthest from the pattern",
                     what="Rows far from the strongest relationships (robust line) or from their group's median — check them before trusting a pattern.",
                     fields=[f for v in (rels[:3] + brks[:3]) for f in v.fields] + ([labcol] if labcol else []),
                     form="table", n=len(rows), html=html, csv=buf.getvalue(), wide=True,
                     caution="Unusual is not wrong: an outlier can be an error, a real extreme, or the story.",
                     show_args={})]

    # ---------------------------------------------------------- assemble
    def run(self) -> list[View]:
        dists = self.distributions()
        miss = self.missingness()
        rels, cond = self.relationships()
        brks = self.breakdowns()
        trends = self.trends()
        outs = self.outliers(rels, brks)
        pools = {"distribution": dists, "missingness": miss, "relationship": [v for v in rels if not v.withheld],
                 "conditioned": cond, "breakdown": [v for v in brks if not v.withheld] + [v for v in brks if v.withheld],
                 "trend": trends, "outliers": outs}
        caps = dict(CAPS)
        total = sum(min(caps[k], len(pools[k])) for k in ORDER)
        if total > self.max_views:
            scale = self.max_views / total
            caps = {k: (max(1, math.floor(min(caps[k], len(pools[k])) * scale)) if pools[k] else 0) for k in ORDER}
            while sum(min(caps[k], len(pools[k])) for k in ORDER) > self.max_views:
                k = max(ORDER, key=lambda k: min(caps[k], len(pools[k])))
                caps[k] -= 1
        drawn: list[View] = []
        for k in ORDER:
            drawn += pools[k][: caps[k]]
        self.drawn_ids = {v.id for v in drawn}
        self.all_views = dists + miss + rels + cond + brks + trends + outs
        nrel = len([v for v in rels if v.id in self.drawn_ids])
        if self.pairs_examined:
            self.notes.insert(0, f"{self.pairs_examined} pair(s) of measures looked at; the strongest {nrel} are drawn. "
                                 "A pattern found by looking at many is a lead to test, not a finding.")
        nb = len([v for v in brks if v.id in self.drawn_ids])
        if self.breakdowns_examined:
            self.notes.insert(1 if self.pairs_examined else 0,
                              f"{self.breakdowns_examined} measure-by-group breakdown(s) looked at; the {nb} with the "
                              "largest group differences are drawn.")
        if rels or cond:
            self.notes.append("Correlation is not cause: these views show which measures move together in this table, "
                              "not why. Shared causes, geography and how the data were made can all produce them.")
        if any(v.caution and v.caution.startswith("Driven by") for v in rels):
            self.notes.append("Some associations rest on a handful of rows; each such view says so and gives ρ without them.")
        self.notes.append("Small multiples of the same measure share their axis scales.")
        self.notes.append(f"n is given beside every statistic; groups under {MIN_GROUP_N} rows and pairs under "
                          f"{MIN_PAIR_N} rows are shown but not ranked.")
        return drawn


def _copy(w: S.Words, **kw) -> S.Words:
    d = dict(title=w.title, subtitle=w.subtitle, x_label=w.x_label, y_label=w.y_label, source=w.source,
             notes=list(w.notes), annotations=dict(w.annotations))
    d.update(kw)
    return S.Words(**d)


# ------------------------------------------------------------------ page

CSS_EXTRA = """
.sheet{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;margin:10px 0 24px}
.card{background:#fff;border:1px solid var(--rule);border-radius:6px;padding:8px 10px 10px;min-width:0}
.card.wide{grid-column:1/-1}.card svg{width:100%;height:auto;display:block}
.card .what{font-size:13px;color:var(--ink2);margin:6px 0 2px}.card .meta{font-size:12px;color:var(--muted)}
.card .caution{font-size:12px;color:#8a4b00;margin-top:4px}.card .id{font-family:ui-monospace,monospace;font-size:11px;color:var(--muted)}
main{max-width:1180px}.notes li{margin:2px 0}
"""


def _page(result: dict, views: list[View], svgs: dict[str, str], sections: list[tuple[str, list[View]]] | None = None) -> str:
    from html import escape

    from .compose import CSS
    title = result["source"]["name"]
    sub = result["subset"]
    bits = [f"{result['source']['rows']:,} rows"]
    if sub.get("where"):
        bits.append("where " + " and ".join(sub["where"]))
    if sub.get("focus"):
        bits.append(f"focus: {sub['focus']}")
    if sub.get("by"):
        bits.append(f"by {sub['by']}")
    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>{escape(title)} — vizier explore</title><style>{CSS}{CSS_EXTRA}</style></head><body><main>",
           f"<h1>What's in {escape(title)}</h1><p class=lede>{' · '.join(escape(b) for b in bits)}. "
           "Look first; then show — every view lists the <code>vizier show</code> arguments that turn it into a figure.</p>",
           "<h2>Before you read the views</h2><ul class=notes>" + "".join(f"<li>{escape(n)}</li>" for n in result["notes"]) + "</ul>"]
    heads = {"distribution": "1 · Field sheet", "missingness": "2 · Missing values", "relationship": "3 · Relationships",
             "conditioned": "3b · Relationships, conditioned", "breakdown": "4 · Breakdowns", "trend": "5 · Trends",
             "outliers": "6 · Outliers"}
    groups = sections or [("", views)]
    for gname, gviews in groups:
        if gname:
            out.append(f"<h2>{escape(gname)}</h2>")
        for kind in ORDER:
            vs = [v for v in gviews if v.kind == kind]
            if not vs:
                continue
            out.append(f"<h3>{heads[kind]}</h3><div class=sheet>")
            for v in vs:
                out.append(f"<div class='card{' wide' if v.wide else ''}' id='{escape(v.id)}'>")
                if v.id in svgs:
                    out.append(svgs[v.id])
                elif v.html:
                    out.append(v.html)
                out.append(f"<p class=what>{escape(v.what)}</p>")
                meta = [f"<span class=id>{escape(v.id)}</span>", f"n={v.n:,}"]
                if v.rank:
                    meta.append(f"rank {v.rank}")
                if v.show_args:
                    meta.append("<code>vizier show … " + " ".join(f"--{k} {escape(str(val))}" for k, val in v.show_args.items()) + "</code>")
                out.append(f"<p class=meta>{' · '.join(meta)}</p>")
                if v.caution and v.kind != "distribution":
                    out.append(f"<p class=caution>{escape(v.caution)}</p>")
                out.append("</div>")
            out.append("</div>")
    others = [v for v in result.get("_undrawn", [])]
    if others:
        out.append("<h3>Looked at, not drawn</h3><table><thead><tr><th>id</th><th>What</th><th>Statistic</th></tr></thead><tbody>")
        for v in others:
            st = v.get("stat") or {}
            sv = f"{st.get('name')} {st.get('value')} (n={st.get('n')})" if st else ""
            out.append(f"<tr><td class=id>{escape(v['id'])}</td><td style='white-space:normal'>{escape(v['title'])}"
                       f"{' — not ranked' if v.get('withheld') else ''}</td><td>{escape(sv)}</td></tr>")
        out.append("</tbody></table><p class=muted>Redraw any of these with <code>vizier explore TABLE --view ID</code>.</p>")
    out.append(f"<p class=muted>Made by vizier {escape(result['vizier_version'])} · static SVG, no scripts, works offline.</p>")
    out.append("</main></body></html>")
    return "\n".join(out)


# ------------------------------------------------------------------ entry point

def explore(
    source: str | Path | Table,
    *,
    out_dir: str | Path | None = None,
    max_views: int = 24,
    focus: str | None = None,
    by: str | None = None,
    where: list[str] | None = None,
    view: str | None = None,
    datapackage: str | Path | None = None,
) -> dict[str, Any]:
    """Explore a table. Returns the `vizier/explore/v1` dict; writes files if `out_dir`."""
    table = source if isinstance(source, Table) else load_table(source, datapackage=datapackage)
    where = list(where or [])
    table = apply_where(table, where)
    if by and by not in table.columns:
        raise ValueError(f"--by: no column named {by!r}")

    base = Explorer(table, focus=focus, max_views=max_views)
    sections: list[tuple[str, list[View]]] = []
    if by:
        G = table.column(by)
        sizes: dict[str, int] = {}
        for g in G:
            if g is not None:
                sizes[g] = sizes.get(g, 0) + 1
        keep = sorted(sizes, key=lambda g: -sizes[g])[:6]
        per = max(6, max_views // max(1, len(keep)))
        explorers = []
        drawn: list[View] = []
        for g in keep:
            sub = subset(table, [i for i, x in enumerate(G) if x == g], name=f"{by} = {g}")
            ex = Explorer(sub, focus=focus, max_views=per, prefix=f"by-{slug(g)}-")
            d = ex.run()
            sections.append((f"{base.profile.get(by).label} = {g} ({sizes[g]:,} rows)", d))
            drawn += d
            explorers.append(ex)
        notes = [f"--by {by}: the sheet is re-run for each of the {len(keep)} largest groups"
                 + (f" (of {len(sizes)})" if len(sizes) > len(keep) else "") + "."]
        notes += explorers[0].notes if explorers else []
        all_views = [v for ex in explorers for v in ex.all_views]
        pairs = sum(ex.pairs_examined for ex in explorers)
        brk = sum(ex.breakdowns_examined for ex in explorers)
        if pairs:
            notes[1:2] = [f"{pairs} pair(s) of measures looked at across the groups; the strongest in each are drawn. "
                          "A pattern found by looking at many is a lead to test, not a finding."]
    else:
        drawn = base.run()
        notes = base.notes
        all_views = base.all_views
        pairs, brk = base.pairs_examined, base.breakdowns_examined

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "vizier_version": __version__,
        "source": {"path": table.source, "name": table.name, "rows": len(table), "datapackage": bool(table.package)},
        "subset": {**({"focus": focus} if focus else {}), **({"by": by} if by else {}), "where": where},
        "fields": [field_record(c, table) for c in base.profile.columns],
        "views": [],
        "comparisons_examined": {"pairs": pairs, "breakdowns": brk},
        "notes": notes,
    }

    out = Path(out_dir) if out_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    if view:
        v = next((x for x in all_views if x.id == view), None)
        if v is None:
            raise ValueError(f"no view {view!r}; ids: " + ", ".join(x.id for x in all_views[:40]))
        rec = v.to_dict()
        if v.draw:
            svg = v.draw(BIG_W if not v.wide else max(BIG_W, WIDE_W))
            if out:
                (out / f"{v.id}.svg").write_text(svg, encoding="utf-8")
                rec["file"] = f"{v.id}.svg"
            rec["svg"] = svg if not out else None
        elif v.csv and out:
            (out / f"{v.id}.csv").write_text(v.csv, encoding="utf-8")
            rec["file"] = f"{v.id}.csv"
        result["views"] = [rec]
        return result

    svgs: dict[str, str] = {}
    for v in drawn:
        if v.draw:
            svg = v.draw(CARD_W)
            svgs[v.id] = svg
            if out:
                (out / f"{v.id}.svg").write_text(svg, encoding="utf-8")
                v.file = f"{v.id}.svg"
        elif v.csv and out:
            (out / f"{v.id}.csv").write_text(v.csv, encoding="utf-8")
            v.file = f"{v.id}.csv"
    result["views"] = [v.to_dict() for v in drawn]
    undrawn = [v.to_dict() for v in all_views if v.id not in {d.id for d in drawn}]
    if undrawn:
        result["undrawn"] = undrawn
    if out:
        html = _page({**result, "_undrawn": undrawn}, drawn, svgs, sections or None)
        (out / "index.html").write_text(html, encoding="utf-8")
        (out / "explore.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        result["out_dir"] = str(out)
    return result
