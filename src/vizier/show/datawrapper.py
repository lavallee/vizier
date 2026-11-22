"""Build a chart in Datawrapper from a ranked option.

Uses Datawrapper's public REST API (v3, https://api.datawrapper.de/v3), as
documented in its developer reference (checked 2026-11):

- ``POST /charts`` — JSON ``{title, type, metadata}``; returns the chart ``id``.
- ``PUT /charts/{id}/data`` — the CSV, ``Content-Type: text/csv``.
- ``POST /charts/{id}/publish`` — only with ``publish=True``.

Authentication is ``Authorization: Bearer <token>``, read from
``DATAWRAPPER_API_TOKEN``. With no token nothing is sent: `build_requests`
returns the exact requests that would go out, and `show` prints them.

The client is a thin class over an ``httpx.Client`` so tests can hand it a fake
transport; nothing here is exercised against the live service by the suite.
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from typing import Any

import httpx

from .profile import Profile, parse_number, parse_time
from .rank import Option
from . import svg as S
from .table import Table

API = "https://api.datawrapper.de/v3"
EDIT_URL = "https://app.datawrapper.de/chart/{id}/visualize"

#: vizier form (and variant) -> Datawrapper visualization type id.
TYPE_MAP: dict[tuple[str, str | None], str] = {
    ("bar-chart", None): "d3-bars",
    ("bar-chart", "top"): "d3-bars",
    ("bar-chart", "median"): "d3-bars",
    ("bar-chart", "measures"): "d3-bars",
    ("bar-chart", "count"): "d3-bars",
    ("bar-chart", "grouped"): "d3-bars-grouped",
    ("bar-chart", "time"): "column-chart",
    ("stacked-bar", None): "d3-bars-stacked",
    ("line-chart", None): "d3-lines",
    ("line-chart", "highlight"): "d3-lines",
    ("stacked-area", None): "d3-area",
    ("scatterplot", None): "d3-scatter-plot",
    ("dot-plot", None): "d3-dot-plot",
    ("dot-plot", "paired"): "d3-dot-plot",
    ("slope-chart", None): "d3-arrow-plot",
    ("small-multiples", "line"): "multiple-lines",
    ("small-multiples", "bar"): "multiple-columns",
    ("heatmap", None): "tables",
    ("table", None): "tables",
    ("histogram", None): "column-chart",
}

#: Forms with no Datawrapper equivalent, and why.
NO_EQUIVALENT: dict[str, str] = {
    "strip-plot": "Datawrapper has no strip/jitter plot; its dot plot needs one row per category.",
    "choropleth": "Datawrapper choropleths draw on one of its own basemaps joined by a key column; "
                  "vizier does not pick the basemap. Upload the table and choose the map in the editor.",
    "sentence": "A sentence is text for the page, not a chart.",
    "stat-tile": "Datawrapper has no stat-tile type; put the number in the text or a one-row table.",
    "small-multiples/scatter": "Datawrapper has no multiple-scatter type.",
}

NOTES_ON_TYPE: dict[str, str] = {
    "column-chart": "For a histogram, the CSV holds pre-binned counts; the columns are the bins.",
    "tables": "For a heatmap, turn on heatmap coloring for the value columns in the table editor.",
    "d3-arrow-plot": "An arrow plot is Datawrapper's closest form to a slope chart: one arrow per row, from the first period to the last.",
}


def dw_type(option: Option) -> tuple[str | None, str]:
    """(Datawrapper type id or None, a sentence on the mapping)."""
    key = (option.form, option.variant)
    t = TYPE_MAP.get(key) or TYPE_MAP.get((option.form, None))
    if option.form == "small-multiples" and option.variant == "scatter":
        t = None
    if t:
        return t, NOTES_ON_TYPE.get(t, f"{option.title} maps to Datawrapper's {t}.")
    why = NO_EQUIVALENT.get(f"{option.form}/{option.variant}") or NO_EQUIVALENT.get(option.form) \
        or f"No Datawrapper equivalent for {option.title}."
    return None, why


def _csv(rows: list[list[Any]]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        w.writerow(["" if v is None else (int(v) if isinstance(v, float) and v.is_integer() else v) for v in r])
    return buf.getvalue()


def _num(table: Table, col: str, i: int) -> float | None:
    return parse_number(table.rows[i].get(col))


def _key(table: Table, profile: Profile, col: str, i: int) -> str | None:
    raw = table.rows[i].get(col)
    p = profile.get(col)
    if raw is not None and p is not None and p.role == "time":
        t = parse_time(raw, year_ok=True)
        if t:
            return S.fmt_time(t[0], p.granularity)
    return raw


def _wide(table: Table, profile: Profile, rowcol: str, colcol: str | None, val: str) -> list[list[Any]]:
    """Pivot long rows into a wide CSV: one row per `rowcol`, one column per `colcol`.
    Missing and suppressed values stay empty, never zero."""
    rows_k: list[str] = []
    cols_k: list[str] = []
    cells: dict[tuple[str, str], float | None] = {}
    for i in range(len(table)):
        r = _key(table, profile, rowcol, i)
        c = _key(table, profile, colcol, i) if colcol else profile.get(val).label if profile.get(val) else val
        if r is None or c is None:
            continue
        if r not in rows_k:
            rows_k.append(r)
        if c not in cols_k:
            cols_k.append(c)
        cells[(r, c)] = _num(table, val, i)
    head = [profile.get(rowcol).label if profile.get(rowcol) else rowcol] + cols_k
    return [head] + [[r] + [cells.get((r, c)) for c in cols_k] for r in rows_k]


def dataset(table: Table, profile: Profile, option: Option, *, top: int = 15) -> str:
    """The CSV Datawrapper gets for this form, shaped the way that type reads it."""
    r = option.roles
    f, v = option.form, option.variant
    lab = lambda c: profile.get(c).label if profile.get(c) else c  # noqa: E731
    if f in ("line-chart", "stacked-area") or (f == "small-multiples" and v == "line"):
        y = r["y"]
        if isinstance(y, list):
            head = [lab(r["x"])] + [lab(m) for m in y]
            rows = [[_key(table, profile, r["x"], i)] + [_num(table, m, i) for m in y] for i in range(len(table))]
            return _csv([head] + rows)
        return _csv(_wide(table, profile, r["x"], r.get("facet") or r.get("series"), y))
    if f == "bar-chart" and v == "grouped" or f == "stacked-bar":
        return _csv(_wide(table, profile, r["x"], r.get("series"), r["y"]))
    if f == "small-multiples" and v == "bar":
        return _csv(_wide(table, profile, r["x"], r.get("facet"), r["y"]))
    if f == "heatmap":
        return _csv(_wide(table, profile, r["y"], r["x"], r["value"]))
    if f == "slope-chart":
        times = sorted({t for t in (parse_time(x, year_ok=True) for x in table.column(r["x"])) if t})
        y = r["y"] if isinstance(r["y"], str) else r["y"][0]
        wide = _wide(table, profile, r.get("series") or r["x"], r["x"], y)
        if times:
            first, last = S.fmt_time(times[0][0], times[0][1]), S.fmt_time(times[-1][0], times[-1][1])
            idx = [0] + [j for j, h in enumerate(wide[0]) if h in (first, last)]
            wide = [[row[j] for j in idx] for row in wide]
        return _csv(wide)
    if f == "scatterplot":
        cols = [c for c in (r.get("label"), r["x"], r["y"], r.get("series")) if c]
        return _csv([[lab(c) for c in cols]] + [[table.rows[i].get(c) if profile.get(c).role != "measure" else _num(table, c, i) for c in cols]
                                               for i in range(len(table))])
    if f == "dot-plot":
        ys = r["y"] if isinstance(r["y"], list) else [r["y"]]
        return _csv([[lab(r["x"])] + [lab(m) for m in ys]] + [[table.rows[i].get(r["x"])] + [_num(table, m, i) for m in ys]
                                                              for i in range(len(table))])
    if f == "histogram":
        from statistics import median  # noqa: F401
        X = [x for x in (_num(table, r["x"], i) for i in range(len(table))) if x is not None]
        edges = S.nice_ticks(min(X), max(X), 12)
        counts = [0] * (len(edges) - 1)
        for x in X:
            counts[min(len(counts) - 1, max(0, int((x - edges[0]) / (edges[1] - edges[0]))))] += 1
        u = profile.get(r["x"]).unit
        return _csv([[lab(r["x"]), "Rows"]] + [[f"{S.fmt(edges[k], u)}–{S.fmt(edges[k + 1], u)}", counts[k]] for k in range(len(counts))])
    if f == "bar-chart":
        if v == "measures":
            return _csv([["Measure", "Value"]] + [[lab(m), _num(table, m, 0)] for m in r["measures"]])
        if v == "count":
            counts: dict[str, int] = {}
            for c in table.column(r["x"]):
                if c is not None:
                    counts[c] = counts.get(c, 0) + 1
            return _csv([[lab(r["x"]), "Rows"]] + sorted(([k, n] for k, n in counts.items()), key=lambda t: -t[1]))
        if v == "time":
            return _csv([[lab(r["x"]), lab(r["y"])]] + [[_key(table, profile, r["x"], i), _num(table, r["y"], i)] for i in range(len(table))])
        rows = [[table.rows[i].get(r["x"]), _num(table, r["y"], i)] for i in range(len(table))]
        if v == "median":
            from statistics import median
            g: dict[str, list[float]] = {}
            for k, x in rows:
                if k is not None and x is not None:
                    g.setdefault(k, []).append(x)
            rows = [[k, median(xs)] for k, xs in g.items()]
        rows.sort(key=lambda t: (t[1] is None, -(t[1] or 0)))
        if v == "top":
            rows = rows[:top]
        return _csv([[lab(r["x"]), lab(r["y"])]] + rows)
    cols = [c.name for c in profile.columns if c.role != "geometry"]
    return table.to_csv(cols)


def build_requests(table: Table, profile: Profile, option: Option, words: S.Words, *,
                   publish: bool = False, aria: str = "", top: int = 15) -> dict[str, Any]:
    """The requests `create` would send, in order. Token never included."""
    t, why = dw_type(option)
    if t is None:
        return {"supported": False, "why": why, "requests": []}
    metadata: dict[str, Any] = {
        "describe": {
            "intro": words.subtitle,
            "source-name": words.source,
            "aria-description": aria or words.title,
        },
        "annotate": {"notes": " ".join(words.notes)},
    }
    reqs = [
        {"method": "POST", "path": "/charts", "content_type": "application/json",
         "body": {"title": words.title or option.title, "type": t, "metadata": metadata}},
        {"method": "PUT", "path": "/charts/{id}/data", "content_type": "text/csv",
         "body": dataset(table, profile, option, top=top)},
    ]
    if publish:
        reqs.append({"method": "POST", "path": "/charts/{id}/publish", "content_type": "application/json", "body": {}})
    return {"supported": True, "type": t, "why": why, "requests": reqs}


@dataclass
class DatawrapperClient:
    token: str
    base_url: str = API
    http: httpx.Client | None = None

    def _client(self) -> httpx.Client:
        if self.http is None:
            self.http = httpx.Client(timeout=30)
        return self.http

    def send(self, method: str, path: str, *, body: Any, content_type: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": content_type,
                   "User-Agent": "vizier-show"}
        kw: dict[str, Any] = {"headers": headers}
        if content_type == "application/json":
            kw["json"] = body
        else:
            kw["content"] = body.encode("utf-8") if isinstance(body, str) else body
        resp = self._client().request(method, self.base_url.rstrip("/") + path, **kw)
        if resp.status_code >= 400:
            raise RuntimeError(f"Datawrapper {method} {path} failed: HTTP {resp.status_code} {resp.text[:300]}")
        if not resp.content:
            return {}
        try:
            return resp.json()
        except ValueError:
            return {"text": resp.text}

    def run(self, plan: dict[str, Any]) -> dict[str, Any]:
        """Send a `build_requests` plan; returns the chart id and URLs."""
        chart_id = None
        public_url = None
        for req in plan["requests"]:
            path = req["path"].replace("{id}", chart_id or "{id}")
            out = self.send(req["method"], path, body=req["body"], content_type=req["content_type"])
            if req["path"] == "/charts":
                chart_id = out.get("id") or out.get("publicId")
                if not chart_id:
                    raise RuntimeError(f"Datawrapper returned no chart id: {out}")
            if req["path"].endswith("/publish"):
                public_url = out.get("url") or (out.get("data") or {}).get("publicUrl")
        return {"id": chart_id, "edit_url": EDIT_URL.format(id=chart_id), "public_url": public_url,
                "published": public_url is not None}


def token_from_env() -> str | None:
    return os.environ.get("DATAWRAPPER_API_TOKEN") or None
