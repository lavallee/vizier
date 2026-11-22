"""Renderers: real rows in, a finished static SVG out.

One function per form, each taking a `Ctx` (the table, the chosen option's
field roles, the words, the colors) and returning `(body_svg, body_height)`;
`render()` wraps that in the figure frame. The layouts follow the hand-written
d3 demos in `docs/reader/live-examples.js` (horizontal sorted bars, direct
end-labels on lines, ringed scatter dots, ink-colored text), rebuilt here to
take data instead of inventing it.

Missing and suppressed values are never drawn as zero:

- lines break at a gap, and a suppressed point gets a hatched marker on the
  baseline (`class="vz-missing" data-state=...`);
- bars and dots leave the slot empty and print the state ("suppressed",
  "no data") in muted ink;
- heatmap cells and map areas are hatched.

Each renderer records any mechanical fix it applied (folding a tail into
"Other", a zero baseline, small multiples instead of a dual axis) in
`ctx.applied`, so the figure's notes can say what was done.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from statistics import median
from typing import Any

from ..analyze import generate as G
from . import svg as S
from .profile import Profile, parse_number, parse_time
from .rank import Option
from .table import Table


@dataclass
class Ctx:
    table: Table
    profile: Profile
    option: Option
    words: S.Words
    width: int = 680
    zero: bool = False
    geojson: dict | None = None
    geo_key: str | None = None
    applied: list[dict] = field(default_factory=list)
    colors: dict[str, str] = field(default_factory=dict)
    palette_advice: list[str] = field(default_factory=list)
    anchors: dict[str, tuple[float, float]] = field(default_factory=dict)
    top: int = 15
    ramp: list[str] = field(default_factory=list)
    #: exploration hooks — all optional, defaults leave `show` unchanged
    height: int | None = None             # plot height override for compact views
    highlight: set[int] = field(default_factory=set)   # row indices to ring and label
    min_group: int = 0                    # strip: groups smaller than this are listed last, unranked
    label_n: bool = False                 # strip: put n beside every group label
    keep_order: bool = False              # bars: keep row order (e.g. an "other" bar last)

    # ------------------------------------------------------------ data access
    def r(self, key: str):
        return self.option.roles.get(key)

    def num(self, col: str) -> list[float | None]:
        return [parse_number(v) for v in self.table.column(col)]

    def tval(self, col: str) -> list[float | None]:
        p = self.profile.get(col)
        out = []
        for v in self.table.column(col):
            if v is None:
                out.append(None)
                continue
            t = parse_time(v, year_ok=True)
            if t is None:
                n = parse_number(v)
                out.append(n)
            else:
                out.append(t[0])
        if p and p.granularity == "year":
            out = [round(x) if x is not None else None for x in out]
        return out

    def cat(self, col: str) -> list[str | None]:
        return self.table.column(col)

    def state(self, col: str, i: int) -> str | None:
        return self.table.state_of(col, i)

    def unit(self, col: str | None) -> str | None:
        if not col:
            return None
        p = self.profile.get(col)
        return p.unit if p else None

    def label(self, col: str | None) -> str:
        if not col:
            return ""
        p = self.profile.get(col)
        return p.label if p else col

    def gran(self, col: str) -> str | None:
        p = self.profile.get(col)
        return p.granularity if p else None

    def apply(self, check: str, detail: str) -> None:
        if not any(a["check"] == check and a["detail"] == detail for a in self.applied):
            self.applied.append({"check": check, "detail": detail})

    # ------------------------------------------------------------ color
    def series_colors(self, keys: list[str], *, pairs: str = "adjacent", importance: dict[str, float] | None = None) -> dict[str, str]:
        """Validated categorical colors; past the ceiling, the tail goes gray as 'Other'."""
        n = len(keys)
        pal = G.suggest_palette(max(1, n), pairs=pairs)
        colors = pal["palette"]
        if not pal["met"]:
            self.palette_advice = pal["advice"]
            ranked = sorted(keys, key=lambda k: -(importance or {}).get(k, 0)) if importance else list(keys)
            keep = ranked[: len(colors) - 1]
            out = {k: colors[i] for i, k in enumerate(keep)}
            for k in keys:
                out.setdefault(k, S.OTHER)
            self.apply("too-many-series",
                       f"{n} series is more than color can separate; the top {len(keep)} keep a hue "
                       f"and the other {n - len(keep)} are gray ('Other').")
            self.colors.update(out)
            return out
        out = {k: colors[i] for i, k in enumerate(keys)}
        self.colors.update(out)
        return out

    def accent(self) -> str:
        c = G.suggest_palette(1)["palette"][0]
        self.colors.setdefault("_accent", c)
        return c


def _state_label(s: str | None) -> str:
    if not s:
        return "no data"
    return s.replace("_", " ").replace("-", " ")


# ------------------------------------------------------------------ axes

def _y_axis(ticks, ys: S.Linear, x0: float, x1: float, fmtf, *, label: str = "") -> list[str]:
    out = []
    for t in ticks:
        y = ys(t)
        out.append(S.line(x0, y, x1, y, stroke=S.GRID if t != 0 else S.AXIS))
        out.append(S.text(x0 - 6, y + 4, fmtf(t), size=11, fill=S.MUTED, anchor="end"))
    if label:
        out.append(S.text(x0, ys(ticks[-1]) - 10, label, size=12, fill=S.INK2, extra='class="vz-axis-label"'))
    return out


def _x_axis(ticks, xs: S.Linear, y: float, fmtf, *, label: str = "", grid_top: float | None = None, x_end: float | None = None) -> list[str]:
    out = []
    for t in ticks:
        x = xs(t)
        if grid_top is not None:
            out.append(S.line(x, grid_top, x, y, stroke=S.GRID))
        out.append(S.line(x, y, x, y + 4, stroke=S.AXIS))
        out.append(S.text(x, y + 17, fmtf(t), size=11, fill=S.MUTED, anchor="middle"))
    if label:
        out.append(S.text(x_end if x_end is not None else xs(ticks[-1]), y + 34, label, size=12, fill=S.INK2,
                          anchor="end", extra='class="vz-axis-label"'))
    return out


def _left_margin(labels, size=11, floor=36.0, cap=220.0) -> float:
    return min(cap, max(floor, max((S.text_width(s, size) for s in labels), default=0) + 12))


def _annotations(ctx: Ctx, w: float) -> list[str]:
    """Fill annotation slots whose key matches a drawn anchor."""
    out = ['<g class="vz-annotations">']
    for key, note in ctx.words.annotations.items():
        a = ctx.anchors.get(str(key))
        if not a:
            continue
        x, y = a
        tx = min(max(x + 10, 10), w - 10)
        anchor = "start" if x < w * 0.66 else "end"
        tx = x + 10 if anchor == "start" else x - 10
        out.append(S.line(x, y, tx, y - 18, stroke=S.INK2, width=0.8))
        for i, ln in enumerate(S.wrap(note, 11, 180)):
            out.append(S.text(tx, y - 22 + i * 13 - (len(S.wrap(note, 11, 180)) - 1) * 13, ln, size=11, fill=S.INK, anchor=anchor))
    out.append("</g>")
    return out


# ------------------------------------------------------------------ bar

def render_bar(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    variant = o.variant
    if variant == "measures":
        return _bars_simple(ctx, [(ctx.label(m), v[0] if (v := ctx.num(m)) else None, ctx.state(m, 0)) for m in o.roles["measures"]],
                            unit=ctx.unit(o.roles["measures"][0]), sort=True)
    if variant == "count":
        counts: dict[str, int] = {}
        for c in ctx.cat(o.roles["x"]):
            if c is not None:
                counts[c] = counts.get(c, 0) + 1
        return _bars_simple(ctx, [(k, float(v), None) for k, v in counts.items()], unit=None, sort=True,
                            value_label="Rows")
    xcol, ycol = o.roles["x"], o.roles["y"]
    series = o.roles.get("series")
    if series or variant == "grouped":
        return _bars_grouped(ctx, xcol, ycol, series)
    cats = ctx.cat(xcol) if ctx.profile.get(xcol).role != "time" else [S.fmt_time(t, ctx.gran(xcol)) if t is not None else None for t in ctx.tval(xcol)]
    vals = ctx.num(ycol)
    if variant == "median":
        groups: dict[str, list[float]] = {}
        for c, v in zip(cats, vals):
            if c is not None and v is not None:
                groups.setdefault(c, []).append(v)
        items = [(k, median(v), None) for k, v in groups.items()]
        ctx.words.x_label = f"Median {ctx.label(ycol).lower()}{S.unit_suffix(ctx.unit(ycol))}, per {ctx.label(xcol).lower()}"
        return _bars_simple(ctx, items, unit=ctx.unit(ycol), sort=True)
    items = [(c, v, ctx.state(ycol, i)) for i, (c, v) in enumerate(zip(cats, vals)) if c is not None]
    if ctx.profile.get(xcol).role == "time":
        tv = ctx.tval(xcol)
        order = sorted(range(len(items)), key=lambda i: (tv[i] is None, tv[i] or 0))
        return _columns_time(ctx, [items[i] for i in order], unit=ctx.unit(ycol))
    more = 0
    if variant == "top" and len(items) > ctx.top:
        srt = sorted(items, key=lambda t: (t[1] is None, -(t[1] or 0)))
        more = len(items) - ctx.top
        items = srt[: ctx.top]
        ctx.apply("too-many-categories",
                  f"Showing the top {ctx.top} of {ctx.top + more} by {ctx.label(ycol).lower()}; the full list is in the table.")
    return _bars_simple(ctx, items, unit=ctx.unit(ycol), sort=not ctx.keep_order)


def _bars_simple(ctx: Ctx, items, *, unit, sort=True, value_label: str | None = None) -> tuple[str, float]:
    W = ctx.width
    if sort:
        items = sorted(items, key=lambda t: (t[1] is None, -(t[1] or 0)))
    labels = [str(k) for k, _, _ in items]
    left = _left_margin(labels, 12, cap=W * 0.36) + 8
    right = 70
    bar_h = 22 if len(items) <= 12 else (16 if len(items) <= 25 else 12)
    top = 26
    H = top + len(items) * (bar_h + 6) + 30
    present = [v for _, v, _ in items if v is not None]
    lo = min(0.0, min(present, default=0))
    hi = max(0.0, max(present, default=1))
    d0, d1, ticks = S.nice_domain(lo, hi, 5, zero=True)
    xs = S.Linear(d0, d1, left, W - right)
    fmtf = S.tick_formatter(ticks, unit)
    acc = ctx.accent()
    out = []
    ybase = top + len(items) * (bar_h + 6)
    for t in ticks:
        out.append(S.line(xs(t), top - 6, xs(t), ybase, stroke=S.GRID if t != 0 else S.AXIS))
        out.append(S.text(xs(t), ybase + 16, fmtf(t), size=11, fill=S.MUTED, anchor="middle"))
    ylab = ctx.words.x_label or value_label or ""
    if ylab:
        out.append(S.text(W - right, ybase + 32, ylab, size=12, fill=S.INK2, anchor="end", extra='class="vz-axis-label"'))
    for i, (k, v, st) in enumerate(items):
        y = top + i * (bar_h + 6)
        out.append(S.text(left - 8, y + bar_h / 2 + 4, S.truncate(k, 12, left - 12), size=12, fill=S.INK, anchor="end"))
        if v is None:
            out.append(S.rect(xs(0), y + 3, 18, bar_h - 6, S.MISSING_FILL,
                              extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"',
                              tip=f"{k}: {_state_label(st)}"))
            out.append(S.text(xs(0) + 24, y + bar_h / 2 + 4, _state_label(st), size=11, fill=S.MUTED,
                              extra='font-style="italic"'))
            continue
        x0, x1 = sorted((xs(0), xs(v)))
        out.append(S.rect(x0, y, x1 - x0, bar_h, acc, tip=f"{k}: {S.fmt(v, unit)}", extra='class="vz-mark"'))
        lx = x1 + 6 if v >= 0 else x0 - 6
        out.append(S.text(lx, y + bar_h / 2 + 4, S.fmt(v, unit), size=11, fill=S.INK2, anchor="start" if v >= 0 else "end"))
        ctx.anchors[str(k)] = (x1, y + bar_h / 2)
    out += _annotations(ctx, W)
    return "\n".join(out), H


def _columns_time(ctx: Ctx, items, *, unit) -> tuple[str, float]:
    W, H = ctx.width, ctx.height or 300
    left, right, top, bottom = 56, 20, 26, 44
    present = [v for _, v, _ in items if v is not None]
    d0, d1, ticks = S.nice_domain(min(present, default=0), max(present, default=1), 5, zero=True)
    ys = S.Linear(d0, d1, H - bottom, top)
    fmtf = S.tick_formatter(ticks, unit)
    left = _left_margin([fmtf(t) for t in ticks], 11) + 8
    band = S.Band([str(k) for k, _, _ in items], left, W - right, 0.25)
    out = _y_axis(ticks, ys, left, W - right, fmtf, label=ctx.words.y_label)
    acc = ctx.accent()
    every = max(1, math.ceil(len(items) / 12))
    for i, (k, v, st) in enumerate(items):
        x = band(str(k))
        if i % every == 0:
            out.append(S.text(x + band.bandwidth / 2, H - bottom + 16, k, size=11, fill=S.MUTED, anchor="middle"))
        if v is None:
            out.append(S.rect(x, ys(0) - 14, band.bandwidth, 14, S.MISSING_FILL,
                              extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"', tip=f"{k}: {_state_label(st)}"))
            continue
        y0, y1 = sorted((ys(0), ys(v)))
        out.append(S.rect(x, y0, band.bandwidth, y1 - y0, acc, tip=f"{k}: {S.fmt(v, unit)}", extra='class="vz-mark"'))
        if len(items) <= 12:
            out.append(S.text(x + band.bandwidth / 2, y0 - 5, S.fmt(v, unit), size=11, fill=S.INK2, anchor="middle"))
        ctx.anchors[str(k)] = (x + band.bandwidth / 2, y0)
    out += _annotations(ctx, W)
    return "\n".join(out), H


def _bars_grouped(ctx: Ctx, xcol: str, ycol: str, series: str | None, *, stacked: bool = False) -> tuple[str, float]:
    W = ctx.width
    def keyed(col):
        p = ctx.profile.get(col)
        if p and p.role == "time":
            return [S.fmt_time(t, p.granularity) if t is not None else None for t in ctx.tval(col)]
        return ctx.cat(col)
    cats = keyed(xcol)
    sers = keyed(series) if series else ["value"] * len(cats)
    vals = ctx.num(ycol)
    cells: dict[tuple[str, str], tuple[float | None, str | None]] = {}
    for i, (c, s, v) in enumerate(zip(cats, sers, vals)):
        if c is None or s is None:
            continue
        cells[(c, s)] = (v, ctx.state(ycol, i))
    cat_keys = list(dict.fromkeys(c for c, _ in cells))
    ser_keys = list(dict.fromkeys(s for _, s in cells))
    totals = {c: sum((cells.get((c, s), (0, None))[0] or 0) for s in ser_keys) for c in cat_keys}
    imp = {s: sum((cells.get((c, s), (0, None))[0] or 0) for c in cat_keys) for s in ser_keys}
    xp = ctx.profile.get(xcol)
    if xp and xp.role == "time":
        tv = ctx.tval(xcol)
        first = {}
        for c, t in zip(cats, tv):
            if c is not None and t is not None:
                first.setdefault(c, t)
        cat_keys.sort(key=lambda c: first.get(c, 0))
    else:
        cat_keys.sort(key=lambda c: -totals[c])
    colors = ctx.series_colors(ser_keys, importance=imp)
    unit = ctx.unit(ycol)
    labels = [str(c) for c in cat_keys]
    left = _left_margin(labels, 12, cap=W * 0.34) + 8
    right = 60
    leg, leg_h = S.legend([(s, colors[s]) for s in ser_keys if colors[s] != S.OTHER] +
                          ([("Other", S.OTHER)] if S.OTHER in colors.values() else []), left, 0, W - left - right)
    top = leg_h + 14
    per = 1 if stacked else len(ser_keys)
    bar_h = max(6, min(16, 180 / max(1, per * len(cat_keys)) * 3)) if not stacked else 20
    group_h = per * bar_h + 10
    H = top + len(cat_keys) * group_h + 34
    if stacked:
        hi = max([sum(max(0.0, cells.get((c, s), (0, None))[0] or 0) for s in ser_keys) for c in cat_keys] or [1])
        lo = 0.0
    else:
        present = [v for v, _ in cells.values() if v is not None]
        lo, hi = min(0.0, min(present, default=0)), max(present, default=1)
    d0, d1, ticks = S.nice_domain(lo, hi, 5, zero=True)
    xs = S.Linear(d0, d1, left, W - right)
    fmtf = S.tick_formatter(ticks, unit)
    out = [leg]
    ybase = top + len(cat_keys) * group_h
    for t in ticks:
        out.append(S.line(xs(t), top - 4, xs(t), ybase, stroke=S.GRID if t != 0 else S.AXIS))
        out.append(S.text(xs(t), ybase + 16, fmtf(t), size=11, fill=S.MUTED, anchor="middle"))
    lab = ctx.words.x_label or f"{ctx.label(ycol)}{S.unit_suffix(unit)}"
    out.append(S.text(W - right, ybase + 32, lab, size=12, fill=S.INK2, anchor="end", extra='class="vz-axis-label"'))
    for gi, c in enumerate(cat_keys):
        gy = top + gi * group_h
        out.append(S.text(left - 8, gy + (per * bar_h) / 2 + 4, S.truncate(c, 12, left - 12), size=12, fill=S.INK, anchor="end"))
        cursor = xs(0)
        for si, s in enumerate(ser_keys):
            v, st = cells.get((c, s), (None, "no data"))
            y = gy if stacked else gy + si * bar_h
            if v is None:
                if not stacked:
                    out.append(S.rect(xs(0), y + 1, 12, bar_h - 2, S.MISSING_FILL,
                                      extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"',
                                      tip=f"{c} · {s}: {_state_label(st)}"))
                else:
                    out.append(f'<g class="vz-missing" data-state="{S.esc(_state_label(st))}"><title>{S.esc(c)} · {S.esc(s)}: {S.esc(_state_label(st))}</title></g>')
                continue
            if stacked:
                w = xs(max(0.0, v)) - xs(0)
                out.append(S.rect(cursor, y, w, bar_h, colors[s], extra=f'class="vz-mark" stroke="{S.SURFACE}" stroke-width="1"',
                                  tip=f"{c} · {s}: {S.fmt(v, unit)}"))
                cursor += w
            else:
                x0, x1 = sorted((xs(0), xs(v)))
                out.append(S.rect(x0, y + 1, x1 - x0, bar_h - 2, colors[s], extra='class="vz-mark"',
                                  tip=f"{c} · {s}: {S.fmt(v, unit)}"))
                if bar_h >= 11:
                    out.append(S.text(x1 + 4, y + bar_h / 2 + 4, S.fmt(v, unit), size=10, fill=S.INK2))
        if stacked:
            out.append(S.text(cursor + 6, gy + bar_h / 2 + 4, S.fmt(totals[c], unit), size=11, fill=S.INK2))
    if any(cells.get((c, s), (None,))[0] is None for c in cat_keys for s in ser_keys):
        h, hh = S.legend([("no data / suppressed", "")], left, H - 12, W, size=11, kind="hatch")
        out.append(h)
        H += 6
    return "\n".join(out), H


def render_stacked_bar(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    return _bars_grouped(ctx, o.roles["x"], o.roles["y"], o.roles.get("series"), stacked=True)


# ------------------------------------------------------------------ line

def _series_points(ctx: Ctx) -> tuple[dict[str, list[tuple[float, float | None, str | None]]], str | None]:
    o = ctx.option
    xcol = o.roles["x"]
    y = o.roles["y"]
    series = o.roles.get("series")
    xs = ctx.tval(xcol) if ctx.profile.get(xcol).role == "time" else ctx.num(xcol)
    out: dict[str, list] = {}
    if isinstance(y, list):
        for m in y:
            vals = ctx.num(m)
            out[ctx.label(m)] = [(x, v, ctx.state(m, i)) for i, (x, v) in enumerate(zip(xs, vals)) if x is not None]
        unit = ctx.unit(y[0])
    else:
        vals = ctx.num(y)
        keys = ctx.cat(series) if series else ["__one__"] * len(xs)
        for i, (x, v, k) in enumerate(zip(xs, vals, keys)):
            if x is None or k is None:
                continue
            out.setdefault(k, []).append((x, v, ctx.state(y, i)))
        unit = ctx.unit(y)
    for k in out:
        out[k].sort(key=lambda t: t[0])
    return out, unit


def _line_path(pts, xs, ys) -> list[str]:
    """Path segments, broken wherever a value is missing."""
    segs, cur = [], []
    for x, v, _ in pts:
        if v is None:
            if cur:
                segs.append(cur)
            cur = []
            continue
        cur.append((xs(x), ys(v)))
    if cur:
        segs.append(cur)
    return ["M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in s) for s in segs]


def render_line(ctx: Ctx, *, area: bool = False) -> tuple[str, float]:
    o = ctx.option
    W, H = ctx.width, ctx.height or 340
    data, unit = _series_points(ctx)
    keys = list(data)
    last = {k: next((v for _, v, _ in reversed(data[k]) if v is not None), None) for k in keys}
    imp = {k: (last[k] if last[k] is not None else -1e18) for k in keys}
    xcol = o.roles["x"]
    gran = ctx.gran(xcol)
    allx = [x for k in keys for x, _, _ in data[k]]
    ally = [v for k in keys for _, v, _ in data[k] if v is not None]
    if not ally:
        return S.text(20, 30, "No values to draw.", size=13), 50
    if area:
        # stacked: cumulative per x across series
        xs_sorted = sorted(set(allx))
        cum = {x: 0.0 for x in xs_sorted}
        stacks = {}
        for k in keys:
            m = {x: v for x, v, _ in data[k]}
            stacks[k] = [(x, cum[x], cum[x] + (m.get(x) or 0.0), m.get(x)) for x in xs_sorted]
            for x in xs_sorted:
                cum[x] += m.get(x) or 0.0
        ally = list(cum.values()) + [0.0]
    lo, hi = min(ally), max(ally)
    zero = ctx.zero or area or (lo >= 0 and lo <= 0.25 * hi) or lo < 0 < hi
    d0, d1, ticks = S.nice_domain(lo, hi, 5, zero=zero)
    if not zero and lo > 0:
        ctx.apply("axis-not-zero", f"The value axis starts at {S.fmt(d0, unit)}, not zero, and says so; "
                                   "pass --zero to draw it from zero.")
    fmtf = S.tick_formatter(ticks, unit)
    left = _left_margin([fmtf(t) for t in ticks], 11) + 8
    single = len(keys) == 1
    many = len(keys) > 6
    colors: dict[str, str]
    if single:
        colors = {keys[0]: ctx.accent()}
    elif many and o.variant == "highlight":
        top3 = sorted(keys, key=lambda k: -imp[k])[:3]
        pal = ctx.series_colors(top3)
        colors = {k: pal.get(k, S.OTHER) for k in keys}
        ctx.apply("too-many-series", f"{len(keys)} series: the 3 highest at the end keep a hue, the rest are gray.")
    else:
        colors = ctx.series_colors(keys, importance=imp)
    lab_w = 0 if single else min(160, max(S.text_width(k, 11) for k in keys) + 50)
    right = 24 + lab_w
    top, bottom = 28, 44
    x0d, x1d = min(allx), max(allx)
    xs = S.Linear(x0d, x1d, left, W - right)
    ys = S.Linear(d0, d1, H - bottom, top)
    out = _y_axis(ticks, ys, left, W - right, fmtf,
                  label=ctx.words.y_label or f"{ctx.label(o.roles['y'] if isinstance(o.roles['y'], str) else o.roles['y'][0])}{S.unit_suffix(unit)}")
    xt = S.time_ticks(x0d, x1d, gran) if ctx.profile.get(xcol).role == "time" else S.nice_ticks(x0d, x1d, 6)
    xt = [t for t in xt if x0d - 1e-9 <= t <= x1d + 1e-9]
    xfmt = (lambda t: S.fmt_time(t, gran)) if ctx.profile.get(xcol).role == "time" else S.tick_formatter(xt, ctx.unit(xcol))
    out += _x_axis(xt, xs, H - bottom, xfmt, label=ctx.words.x_label if ctx.words.x_label else "", x_end=W - right)
    order = sorted(keys, key=lambda k: colors[k] != S.OTHER)  # gray underneath
    endlabels = []
    gap_marks = []
    for k in order:
        pts = data[k]
        c = colors[k]
        if area:
            st = stacks[k]
            top_pts = " L".join(f"{xs(x):.1f},{ys(t1):.1f}" for x, _, t1, _ in st)
            bot_pts = " L".join(f"{xs(x):.1f},{ys(t0):.1f}" for x, t0, _, _ in reversed(st))
            out.append(S.path(f"M{top_pts} L{bot_pts} Z", fill=c, stroke=S.SURFACE, width=1,
                              extra='class="vz-mark" fill-opacity="0.9"', tip=k))
            mid = st[-1]
            endlabels.append([ys((mid[1] + mid[2]) / 2), k, c, mid[3]])
            continue
        for d in _line_path(pts, xs, ys):
            out.append(S.path(d, stroke=c, width=2.5 if c != S.OTHER else 1.25, extra='class="vz-mark"'))
        n_present = sum(1 for _, v, _ in pts if v is not None)
        for i, (x, v, st) in enumerate(pts):
            if v is None:
                gap_marks.append((x, st, k))
                continue
            isolated = (i == 0 or pts[i - 1][1] is None) and (i == len(pts) - 1 or pts[i + 1][1] is None)
            if isolated or n_present <= 12:
                out.append(S.circle(xs(x), ys(v), 3 if not isolated else 3.5, c,
                                    extra=f'stroke="{S.SURFACE}" stroke-width="1"',
                                    tip=f"{'' if k == '__one__' else k + ' · '}{xfmt(x)}: {S.fmt(v, unit)}"))
            ctx.anchors[f"{xfmt(x)}" if single else f"{k}@{xfmt(x)}"] = (xs(x), ys(v))
        lv = next(((x, v) for x, v, _ in reversed(pts) if v is not None), None)
        if lv and not single:
            endlabels.append([ys(lv[1]), k, c, lv[1]])
            ctx.anchors[k] = (xs(lv[0]), ys(lv[1]))
        elif lv and single:
            out.append(S.text(xs(lv[0]) + 6, ys(lv[1]) - 8, S.fmt(lv[1], unit), size=11, fill=S.INK, anchor="end" if xs(lv[0]) > W - 60 else "start"))
    # direct end labels, pushed apart so they don't overlap
    endlabels.sort(key=lambda t: t[0])
    for i in range(1, len(endlabels)):
        if endlabels[i][0] - endlabels[i - 1][0] < 13:
            endlabels[i][0] = endlabels[i - 1][0] + 13
    shown = [e for e in endlabels if e[2] != S.OTHER]
    for y, k, c, v in shown:
        xe = W - right + 8
        out.append(S.line(xe, y - 3, xe + 10, y - 3, stroke=c, width=3))
        out.append(S.text(xe + 14, y + 1, S.truncate(f"{k} {S.fmt(v, unit)}" if v is not None else k, 11, lab_w - 14),
                          size=11, fill=S.INK))
    others = [e for e in endlabels if e[2] == S.OTHER]
    if others:
        out.append(S.text(W - right + 8, H - bottom + 4, f"gray: {len(others)} other series", size=11, fill=S.MUTED))
    if gap_marks:
        for x, st, k in gap_marks:
            out.append(S.rect(xs(x) - 3, H - bottom - 8, 6, 8, S.MISSING_FILL,
                              extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"',
                              tip=f"{'' if k == '__one__' else k + ' · '}{xfmt(x)}: {_state_label(st)}"))
        h, _ = S.legend([("gap: no data / suppressed", "")], left, H - 12, W, size=11, kind="hatch")
        out.append(h)
        H += 8
    out += _annotations(ctx, W)
    return "\n".join(out), H


def render_stacked_area(ctx: Ctx) -> tuple[str, float]:
    return render_line(ctx, area=True)


# ------------------------------------------------------------------ scatter

def render_scatter(ctx: Ctx, *, panel: tuple[float, float, float, float] | None = None,
                   xcol: str | None = None, ycol: str | None = None, shared: tuple | None = None,
                   shared_x: tuple | None = None, rows: set[int] | None = None,
                   panel_title: str | None = None) -> tuple[str, float]:
    o = ctx.option
    xcol = xcol or o.roles["x"]
    ycol = ycol or o.roles["y"]
    lab = o.roles.get("label")
    series = o.roles.get("series")
    X, Y = ctx.num(xcol), ctx.num(ycol)
    L = ctx.cat(lab) if lab else [None] * len(X)
    C = ctx.cat(series) if series else [None] * len(X)
    pts = [(x, y, l, c, i) for i, (x, y, l, c) in enumerate(zip(X, Y, L, C))
           if x is not None and y is not None and (rows is None or i in rows)]
    dropped = len(X) - len(pts)
    if dropped and rows is None:
        supp = sum(1 for i in range(len(X)) if ctx.state(xcol, i) or ctx.state(ycol, i))
        ctx.apply("missing-not-plotted",
                  f"{dropped} row(s) with a missing {ctx.label(xcol).lower()} or {ctx.label(ycol).lower()} are not plotted"
                  + (f" ({supp} suppressed)" if supp else "") + "; none were drawn as zero.")
    W = ctx.width if panel is None else panel[2]
    H = (ctx.height or 400) if panel is None else panel[3]
    if not pts:
        return S.text(20, 30, "No rows have both values.", size=13), 50
    xu, yu = ctx.unit(xcol), ctx.unit(ycol)
    xd = S.nice_domain(min(p[0] for p in pts), max(p[0] for p in pts), 5, zero=ctx.zero)
    yd = S.nice_domain(min(p[1] for p in pts), max(p[1] for p in pts), 5, zero=ctx.zero)
    if shared:
        yd = shared
    if shared_x:
        xd = shared_x
    yf = S.tick_formatter(yd[2], yu)
    xf = S.tick_formatter(xd[2], xu)
    left = (_left_margin([yf(t) for t in yd[2]], 11) + 8) if panel is None else 44
    right, top, bottom = (24, 24, 50) if panel is None else (10, 18, 34)
    xs = S.Linear(xd[0], xd[1], left, W - right)
    ys = S.Linear(yd[0], yd[1], H - bottom, top)
    out = _y_axis(yd[2], ys, left, W - right, yf,
                  label=(ctx.words.y_label or f"{ctx.label(ycol)}{S.unit_suffix(yu)}") if panel is None else "")
    out += _x_axis(xd[2], xs, H - bottom, xf, label=f"{ctx.label(xcol)}{S.unit_suffix(xu)}", grid_top=top, x_end=W - right)
    if panel_title:
        out.append(S.text(left, 12, panel_title, size=11, fill=S.INK, weight="600"))
    if series:
        keys = list(dict.fromkeys(c for *_, c, _ in pts if c is not None))
        counts = {k: sum(1 for p in pts if p[3] == k) for k in keys}
        colors = ctx.series_colors(keys, pairs="all", importance=counts)
        leg, lh = S.legend([(k, colors[k]) for k in keys if colors[k] != S.OTHER] +
                           ([("Other", S.OTHER)] if S.OTHER in colors.values() else []), left, H, W - left, kind="rect")
    else:
        colors, leg, lh = {}, "", 0
    acc = ctx.accent()
    r = 3.5 if len(pts) < 400 else 2.5
    for x, y, l, c, i in pts:
        fill = colors.get(c, acc) if series else acc
        tip = f"{l + ': ' if l else ''}{ctx.label(xcol)} {S.fmt(x, xu)}, {ctx.label(ycol)} {S.fmt(y, yu)}" + (f" ({c})" if c else "")
        out.append(S.circle(xs(x), ys(y), r, fill, extra=f'class="vz-mark" fill-opacity="0.72" stroke="{S.SURFACE}" stroke-width="0.8"', tip=tip))
        if l:
            ctx.anchors[str(l)] = (xs(x), ys(y))
    for x, y, l, c, i in pts:
        if i in ctx.highlight:
            out.append(S.circle(xs(x), ys(y), r + 2.5, "none", extra=f'class="vz-highlight" stroke="{S.INK}" stroke-width="1.5"'))
            if l:
                anchor = "end" if xs(x) > W * 0.6 else "start"
                out.append(S.text(xs(x) + (-8 if anchor == "end" else 8), ys(y) + 4, S.truncate(l, 10, 120), size=10,
                                  fill=S.INK, anchor=anchor, extra=f'stroke="{S.SURFACE}" stroke-width="3" paint-order="stroke"'))
    # label the extremes so the reader has names to hold on to
    if lab and panel is None and len(pts) >= 3 and not ctx.highlight:
        hi = max(pts, key=lambda p: p[1])
        lo = min(pts, key=lambda p: p[1])
        for p in (hi, lo):
            if p[2] and str(p[2]) not in ctx.words.annotations:
                anchor = "end" if xs(p[0]) > W * 0.7 else "start"
                dx = -7 if anchor == "end" else 7
                out.append(S.text(xs(p[0]) + dx, ys(p[1]) + 4, p[2], size=11, fill=S.INK, anchor=anchor,
                                  extra=f'stroke="{S.SURFACE}" stroke-width="3" paint-order="stroke"'))
    if leg:
        out.append(leg)
        H += lh + 4
    out += _annotations(ctx, W)
    return "\n".join(out), H


# ------------------------------------------------------------------ dot / strip / histogram

def render_dot(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    xcol = o.roles["x"]
    ys_cols = o.roles["y"] if isinstance(o.roles["y"], list) else [o.roles["y"]]
    cats = ctx.cat(xcol)
    series_vals = {m: ctx.num(m) for m in ys_cols}
    rows = [(c, [series_vals[m][i] for m in ys_cols], i) for i, c in enumerate(cats) if c is not None]
    rows.sort(key=lambda r: (r[1][0] is None, -(r[1][0] or 0)))
    unit = ctx.unit(ys_cols[0])
    present = [v for _, vs, _ in rows for v in vs if v is not None]
    d0, d1, ticks = S.nice_domain(min(present, default=0), max(present, default=1), 5, zero=ctx.zero)
    left = _left_margin([r[0] for r in rows], 12, cap=W * 0.34) + 8
    right = 30
    colors = ctx.series_colors([ctx.label(m) for m in ys_cols]) if len(ys_cols) > 1 else {ctx.label(ys_cols[0]): ctx.accent()}
    leg, lh = (S.legend([(ctx.label(m), colors[ctx.label(m)]) for m in ys_cols], left, 0, W - left, kind="rect")
               if len(ys_cols) > 1 else ("", 0))
    top = lh + 16
    row_h = 20 if len(rows) <= 25 else 14
    H = top + len(rows) * row_h + 40
    xs = S.Linear(d0, d1, left, W - right)
    fmtf = S.tick_formatter(ticks, unit)
    out = [leg]
    base = top + len(rows) * row_h
    for t in ticks:
        out.append(S.line(xs(t), top - 6, xs(t), base, stroke=S.GRID))
        out.append(S.text(xs(t), base + 16, fmtf(t), size=11, fill=S.MUTED, anchor="middle"))
    out.append(S.text(W - right, base + 32, ctx.words.x_label or f"{ctx.label(ys_cols[0]) if len(ys_cols) == 1 else 'Value'}{S.unit_suffix(unit)}",
                      size=12, fill=S.INK2, anchor="end", extra='class="vz-axis-label"'))
    for j, (c, vs, i) in enumerate(rows):
        y = top + j * row_h + row_h / 2
        out.append(S.text(left - 8, y + 4, S.truncate(c, 12, left - 12), size=12, fill=S.INK, anchor="end"))
        out.append(S.line(left, y, W - right, y, stroke="#f0efea"))
        pv = [v for v in vs if v is not None]
        if len(pv) >= 2:
            out.append(S.line(xs(min(pv)), y, xs(max(pv)), y, stroke=S.AXIS, width=2))
        for m, v in zip(ys_cols, vs):
            if v is None:
                st = _state_label(ctx.state(m, i))
                out.append(S.text(left + 4, y + 4, st, size=11, fill=S.MUTED, extra=f'font-style="italic" class="vz-missing" data-state="{S.esc(st)}"'))
                continue
            out.append(S.circle(xs(v), y, 5, colors[ctx.label(m)], extra=f'class="vz-mark" stroke="{S.SURFACE}" stroke-width="1"',
                                tip=f"{c} · {ctx.label(m)}: {S.fmt(v, unit)}"))
            ctx.anchors[str(c)] = (xs(v), y)
    out += _annotations(ctx, W)
    return "\n".join(out), H


def _jitter(i: int, n: int) -> float:
    """Deterministic jitter in [-1, 1]: same figure every run."""
    return ((i * 0.6180339887) % 1.0) * 2 - 1


def render_strip(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    xcol = o.roles["x"]
    gcol = o.roles.get("y")
    lab = o.roles.get("label")
    X = ctx.num(xcol)
    G_ = ctx.cat(gcol) if gcol else ["__all__"] * len(X)
    L = ctx.cat(lab) if lab else [None] * len(X)
    groups: dict[str, list[tuple[float, str | None]]] = {}
    for x, g, l in zip(X, G_, L):
        if x is None or g is None:
            continue
        groups.setdefault(g, []).append((x, l))
    dropped = sum(1 for x in X if x is None)
    if dropped:
        ctx.apply("missing-not-plotted", f"{dropped} row(s) with no {ctx.label(xcol).lower()} are not plotted (not drawn as zero).")
    keys = sorted(groups, key=lambda g: (len(groups[g]) < ctx.min_group, -median([v for v, _ in groups[g]])))
    shown = {g: (f"{g} (n={len(groups[g])}{', not ranked' if len(groups[g]) < ctx.min_group else ''})" if ctx.label_n else g)
             for g in keys}
    unit = ctx.unit(xcol)
    allv = [v for g in groups.values() for v, _ in g]
    if not allv:
        return S.text(20, 30, "No values to draw.", size=13), 50
    d0, d1, ticks = S.nice_domain(min(allv), max(allv), 5 if W >= 500 else 3, zero=ctx.zero)
    single = keys == ["__all__"]
    left = 20 if single else _left_margin([shown[k] for k in keys], 11 if ctx.label_n else 12, cap=W * 0.45) + 8
    right = 24
    band = 70 if single else max(16, min(34, 360 / max(1, len(keys))))
    top = 14
    H = top + len(keys) * band + 44
    xs = S.Linear(d0, d1, left, W - right)
    fmtf = S.tick_formatter(ticks, unit)
    acc = ctx.accent()
    out = []
    base = top + len(keys) * band
    for t in ticks:
        out.append(S.line(xs(t), top, xs(t), base, stroke=S.GRID))
        out.append(S.text(xs(t), base + 16, fmtf(t), size=11, fill=S.MUTED, anchor="middle"))
    out.append(S.text(W - right, base + 32, ctx.words.x_label or f"{ctx.label(xcol)}{S.unit_suffix(unit)}", size=12, fill=S.INK2,
                      anchor="end", extra='class="vz-axis-label"'))
    r = 3 if len(allv) < 500 else 2
    for j, g in enumerate(keys):
        cy = top + j * band + band / 2
        if not single:
            small = len(groups[g]) < ctx.min_group
            fs = 11 if ctx.label_n else 12
            out.append(S.text(left - 8, cy + 4, S.truncate(shown[g], fs, left - 12), size=fs,
                              fill=S.MUTED if small else S.INK, anchor="end"))
        for i, (v, l) in enumerate(groups[g]):
            y = cy + _jitter(i, len(groups[g])) * band * 0.32
            out.append(S.circle(xs(v), y, r, acc, extra='class="vz-mark" fill-opacity="0.55"',
                                tip=f"{(l + ': ') if l else ''}{S.fmt(v, unit)}"))
            if l:
                ctx.anchors[str(l)] = (xs(v), y)
        md = median([v for v, _ in groups[g]])
        out.append(S.line(xs(md), cy - band * 0.42, xs(md), cy + band * 0.42, stroke=S.INK, width=2,
                          extra='class="vz-median"'))
        if single or j == 0:
            lbl = f"median {S.fmt(md, unit)}"
            right_room = (W - right) - xs(md) > S.text_width(lbl, 11) + 8
            out.append(S.text(xs(md) + (4 if right_room else -4), cy - band * 0.42 + 2, lbl, size=11, fill=S.INK,
                              anchor="start" if right_room else "end",
                              extra=f'stroke="{S.SURFACE}" stroke-width="3" paint-order="stroke"'))
    out += _annotations(ctx, W)
    return "\n".join(out), H


def render_histogram(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W, H = ctx.width, ctx.height or 300
    xcol = o.roles["x"]
    X = [v for v in ctx.num(xcol) if v is not None]
    dropped = len(ctx.num(xcol)) - len(X)
    if dropped:
        ctx.apply("missing-not-plotted", f"{dropped} row(s) with no {ctx.label(xcol).lower()} are left out of the bins (not counted as zero).")
    unit = ctx.unit(xcol)
    if not X:
        return S.text(20, 30, "No values to bin.", size=13), 50
    nb = max(5, min(30, int(math.ceil(math.log2(len(X)) + 1)) + 2))
    edges = S.nice_ticks(min(X), max(X), nb)
    if len(edges) < 2:
        edges = [min(X), min(X) + 1]
    counts = [0] * (len(edges) - 1)
    for v in X:
        k = min(len(counts) - 1, max(0, int((v - edges[0]) / (edges[1] - edges[0]))))
        counts[k] += 1
    d0, d1, yt = S.nice_domain(0, max(counts), 4, zero=True)
    left, right, top, bottom = 48, 20, 26, 48
    xs = S.Linear(edges[0], edges[-1], left, W - right)
    ys = S.Linear(d0, d1, H - bottom, top)
    out = _y_axis(yt, ys, left, W - right, lambda t: f"{int(t):,}", label="Number of rows")
    acc = ctx.accent()
    for i, c in enumerate(counts):
        x0, x1 = xs(edges[i]), xs(edges[i + 1])
        out.append(S.rect(x0 + 0.5, ys(c), x1 - x0 - 1, ys(0) - ys(c), acc, extra='class="vz-mark"',
                          tip=f"{S.fmt(edges[i], unit)}–{S.fmt(edges[i + 1], unit)}: {c} row(s)"))
    xt = edges if len(edges) <= 8 else edges[:: math.ceil(len(edges) / 8)]
    out += _x_axis(xt, xs, H - bottom, S.tick_formatter(edges, unit), label=f"{ctx.label(xcol)}{S.unit_suffix(unit)}", x_end=W - right)
    md = median(X)
    out.append(S.line(xs(md), top - 4, xs(md), H - bottom, stroke=S.INK, width=1.5, extra='stroke-dasharray="4 3" class="vz-median"'))
    out.append(S.text(xs(md) + 4, top + 6, f"median {S.fmt(md, unit)}", size=11, fill=S.INK,
                      extra=f'stroke="{S.SURFACE}" stroke-width="3" paint-order="stroke"'))
    return "\n".join(out), H


# ------------------------------------------------------------------ slope

def render_slope(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    xcol, ycol, series = o.roles["x"], o.roles["y"], o.roles.get("series")
    if isinstance(ycol, list):
        ycol = ycol[0]
    T = ctx.tval(xcol)
    V = ctx.num(ycol)
    K = ctx.cat(series) if series else ["__one__"] * len(T)
    times = sorted({t for t in T if t is not None})
    t0, t1 = times[0], times[-1]
    pairs: dict[str, list] = {}
    for i, (t, v, k) in enumerate(zip(T, V, K)):
        if k is None or t not in (t0, t1):
            continue
        slot = pairs.setdefault(k, [None, None, None, None])
        j = 0 if t == t0 else 1
        slot[j] = v
        slot[2 + j] = ctx.state(ycol, i)
    unit = ctx.unit(ycol)
    vals = [v for p in pairs.values() for v in p[:2] if v is not None]
    d0, d1, _ = S.nice_domain(min(vals, default=0), max(vals, default=1), 5, zero=ctx.zero)
    lab_w = min(200, max(S.text_width(f"{k} {S.fmt(v, unit)}", 11) for k, p in pairs.items() for v in (p[0] or 0, p[1] or 0)) + 14)
    left, right = lab_w + 10, lab_w + 10
    H = 380
    top, bottom = 40, 20
    ys = S.Linear(d0, d1, H - bottom, top)
    xa, xb = left, W - right
    gran = ctx.gran(xcol)
    out = [S.text(xa, 18, S.fmt_time(t0, gran), size=12, fill=S.INK2, anchor="middle", weight="600"),
           S.text(xb, 18, S.fmt_time(t1, gran), size=12, fill=S.INK2, anchor="middle", weight="600"),
           S.line(xa, top - 10, xa, H - bottom, stroke=S.AXIS), S.line(xb, top - 10, xb, H - bottom, stroke=S.AXIS)]
    keys = list(pairs)
    colors = ctx.series_colors(keys, importance={k: abs((p[1] or 0) - (p[0] or 0)) for k, p in pairs.items()}) if len(keys) <= 8 else None
    if colors is None:
        acc = ctx.accent()
        ranked = sorted(keys, key=lambda k: -abs((pairs[k][1] or 0) - (pairs[k][0] or 0)))
        colors = {k: (acc if k in ranked[:5] else S.OTHER) for k in keys}
        ctx.apply("too-many-series", f"{len(keys)} slopes: the 5 biggest changes are colored, the rest gray.")
    lefts, rights = [], []
    for k, (a, b, sa, sb) in pairs.items():
        c = colors[k]
        if a is not None and b is not None:
            out.append(S.path(f"M{xa:.1f},{ys(a):.1f} L{xb:.1f},{ys(b):.1f}", stroke=c, width=2.5 if c != S.OTHER else 1.2,
                              extra='class="vz-mark"', tip=f"{k}: {S.fmt(a, unit)} → {S.fmt(b, unit)}"))
        for x, v, st, side in ((xa, a, sa, lefts), (xb, b, sb, rights)):
            if v is None:
                out.append(S.text(x, H - bottom + 14, f"{k}: {_state_label(st)}", size=10, fill=S.MUTED, anchor="middle",
                                  extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"'))
                continue
            out.append(S.circle(x, ys(v), 4, c, extra=f'stroke="{S.SURFACE}" stroke-width="1"'))
            if c != S.OTHER or len(keys) <= 12:
                side.append([ys(v), k, v])
        ctx.anchors[str(k)] = (xb, ys(b)) if b is not None else (xa, ys(a or 0))
    for side, x, anchor in ((lefts, xa - 8, "end"), (rights, xb + 8, "start")):
        side.sort(key=lambda t: t[0])
        for i in range(1, len(side)):
            if side[i][0] - side[i - 1][0] < 13:
                side[i][0] = side[i - 1][0] + 13
        for y, k, v in side:
            lbl = S.fmt(v, unit) if k == "__one__" else (f"{k} {S.fmt(v, unit)}" if anchor == "end" else f"{S.fmt(v, unit)} {k}")
            out.append(S.text(x, y + 4, lbl, size=11, fill=S.INK, anchor=anchor))
    out += _annotations(ctx, W)
    return "\n".join(out), H


# ------------------------------------------------------------------ small multiples

def render_small_multiples(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    variant = o.variant or "line"
    if variant == "scatter":
        xs_cols = o.roles["x"]
        cols = len(xs_cols)
        pw = (W - 20) / cols
        ph = 260
        out = []
        for j, xc in enumerate(xs_cols):
            body, h = render_scatter(ctx, panel=(0, 0, pw, ph), xcol=xc, ycol=o.roles["y"])
            out.append(f'<g transform="translate({10 + j * pw:.1f},16)">{body}</g>')
        out.insert(0, S.text(16, 10, f"{ctx.label(o.roles['y'])}{S.unit_suffix(ctx.unit(o.roles['y']))}, against each measure",
                             size=12, fill=S.INK2))
        return "\n".join(out), ph + 24
    facet = o.roles.get("facet") or o.roles.get("series")
    F = ctx.cat(facet)
    keys = list(dict.fromkeys(k for k in F if k is not None))
    ycol = o.roles["y"] if isinstance(o.roles["y"], str) else o.roles["y"][0]
    xcol = o.roles["x"]
    V = ctx.num(ycol)
    unit = ctx.unit(ycol)
    present = [v for v in V if v is not None]
    zero = ctx.zero or variant == "bar" or (min(present, default=0) >= 0 and min(present, default=0) <= 0.25 * max(present, default=1))
    d0, d1, ticks = S.nice_domain(min(present, default=0), max(present, default=1), 3, zero=zero)
    if not zero:
        ctx.apply("axis-not-zero", f"Panels share a value axis starting at {S.fmt(d0, unit)}, not zero.")
    if len(keys) > 30:
        last = {}
        for k, v in zip(F, V):
            if k is not None and v is not None:
                last[k] = v
        keys = sorted(keys, key=lambda k: -last.get(k, -1e18))[:30]
        ctx.apply("too-many-panels", f"Showing 30 of {len(set(F) - {None})} panels (highest last value first); the table has the rest.")
    ncol = 4 if W >= 640 else 3
    if len(keys) <= 4:
        ncol = len(keys)
    pw = (W - 20) / ncol
    ph = 130
    nrow = math.ceil(len(keys) / ncol)
    fmtf = S.tick_formatter(ticks, unit)
    is_time = ctx.profile.get(xcol).role == "time"
    X = ctx.tval(xcol) if is_time else ctx.cat(xcol)
    acc = ctx.accent()
    out = [S.text(16, 12, ctx.words.y_label or f"{ctx.label(ycol)}{S.unit_suffix(unit)} · shared scale", size=12, fill=S.INK2,
                  extra='class="vz-axis-label"')]
    if is_time:
        xv = [x for x in X if x is not None]
        x0d, x1d = min(xv), max(xv)
    else:
        xcats = list(dict.fromkeys(x for x in X if x is not None))
    for n_, k in enumerate(keys):
        r_, c_ = divmod(n_, ncol)
        gx, gy = 10 + c_ * pw, 24 + r_ * (ph + 18)
        il, ir, it, ib = gx + 36, gx + pw - 10, gy + 20, gy + ph - 18
        ys = S.Linear(d0, d1, ib, it)
        out.append(S.text(il, gy + 12, S.truncate(k, 12, pw - 46), size=12, fill=S.INK, weight="600"))
        for t in ticks:
            out.append(S.line(il, ys(t), ir, ys(t), stroke=S.GRID))
            if c_ == 0:
                out.append(S.text(il - 4, ys(t) + 3, fmtf(t), size=9, fill=S.MUTED, anchor="end"))
        rows = [(x, v, i) for i, (x, f_, v) in enumerate(zip(X, F, V)) if f_ == k and x is not None]
        if is_time:
            xs = S.Linear(x0d, x1d, il, ir)
            rows.sort(key=lambda t: t[0])
            pts = [(x, v, ctx.state(ycol, i)) for x, v, i in rows]
            for d in _line_path(pts, xs, ys):
                out.append(S.path(d, stroke=acc, width=1.8, extra='class="vz-mark"'))
            for x, v, st in pts:
                if v is None:
                    out.append(S.rect(xs(x) - 2, ib - 6, 4, 6, S.MISSING_FILL,
                                      extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"'))
            if r_ == nrow - 1 or n_ + ncol >= len(keys):
                out.append(S.text(il, ib + 12, S.fmt_time(x0d, ctx.gran(xcol)), size=9, fill=S.MUTED))
                out.append(S.text(ir, ib + 12, S.fmt_time(x1d, ctx.gran(xcol)), size=9, fill=S.MUTED, anchor="end"))
            lv = next(((x, v) for x, v, _ in reversed(pts) if v is not None), None)
            if lv:
                out.append(S.circle(xs(lv[0]), ys(lv[1]), 2.5, acc))
                out.append(S.text(ir, ys(lv[1]) - 5, S.fmt(lv[1], unit), size=9, fill=S.INK, anchor="end"))
        else:
            band = S.Band(xcats, il, ir, 0.25)
            for x, v, i in rows:
                if v is None:
                    out.append(S.rect(band(x), ib - 6, band.bandwidth, 6, S.MISSING_FILL,
                                      extra=f'class="vz-missing" data-state="{S.esc(_state_label(ctx.state(ycol, i)))}"'))
                    continue
                y0, y1 = sorted((ys(0), ys(v)))
                out.append(S.rect(band(x), y0, band.bandwidth, y1 - y0, acc, extra='class="vz-mark"', tip=f"{k} · {x}: {S.fmt(v, unit)}"))
            if len(xcats) <= 6:
                for xc in xcats:
                    out.append(S.text(band(xc) + band.bandwidth / 2, ib + 11, S.truncate(xc, 9, band.step), size=9, fill=S.MUTED, anchor="middle"))
    H = 24 + nrow * (ph + 18) + 4
    return "\n".join(out), H


# ------------------------------------------------------------------ heatmap

def _classes(values: list[float], k: int) -> list[float]:
    """k-1 nice break points over the data (equal-interval on nice ticks)."""
    lo, hi = min(values), max(values)
    t = S.nice_ticks(lo, hi, k)
    return t


def _ramp(ctx: Ctx, steps: int, hue: str = "blue") -> list[str]:
    r = G.suggest_ramp(max(2, steps), hue=hue)
    if not r["met"]:
        ctx.palette_advice = r["advice"]
        ctx.apply("ramp-steps", f"The color ramp holds {len(r['ramp'])} steps, so values are binned into {len(r['ramp'])} classes.")
    ctx.ramp = list(r["ramp"])
    return r["ramp"]


def _legend_ramp(ctx: Ctx, edges: list[float], ramp: list[str], unit, x, y, label: str) -> tuple[str, float]:
    out = [S.text(x, y + 10, label, size=11, fill=S.INK2)]
    sw = 58
    lx = x + S.text_width(label, 11) + 10
    if lx + sw * len(ramp) + 150 > ctx.width:
        out = [S.text(x, y - 4, label, size=11, fill=S.INK2)]
        lx = x
        y += 6
    for i, c in enumerate(ramp):
        out.append(S.rect(lx + i * sw, y, sw - 2, 10, c))
        out.append(S.text(lx + i * sw, y + 23, S.fmt(edges[i], unit, compact=abs(edges[i]) >= 10000), size=10, fill=S.MUTED))
    out.append(S.text(lx + len(ramp) * sw + 2, y + 23, S.fmt(edges[-1], unit, compact=abs(edges[-1]) >= 10000), size=10, fill=S.MUTED, anchor="end"))
    hx = lx + len(ramp) * sw + 16
    out.append(S.rect(hx, y, 14, 10, S.MISSING_FILL, extra=f'stroke="{S.AXIS}" stroke-width="0.5"'))
    out.append(S.text(hx + 18, y + 9, "no data / suppressed", size=10, fill=S.MUTED))
    return "\n".join(out), 36


def _bin(v: float, edges: list[float]) -> int:
    for i in range(len(edges) - 1):
        if v <= edges[i + 1] + 1e-12:
            return i
    return len(edges) - 2


def render_heatmap(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    xcol, ycol, vcol = o.roles["x"], o.roles["y"], o.roles["value"]
    is_time = ctx.profile.get(xcol).role == "time"
    Xr = ctx.tval(xcol) if is_time else ctx.cat(xcol)
    X = [S.fmt_time(x, ctx.gran(xcol)) if (is_time and x is not None) else x for x in Xr]
    Y = ctx.cat(ycol)
    V = ctx.num(vcol)
    unit = ctx.unit(vcol)
    cells = {}
    for i, (x, y, v) in enumerate(zip(X, Y, V)):
        if x is None or y is None:
            continue
        cells[(x, y)] = (v, ctx.state(vcol, i))
    if is_time:
        order = sorted({(xr, x) for xr, x in zip(Xr, X) if x is not None})
        xkeys = list(dict.fromkeys(x for _, x in order))
    else:
        xkeys = list(dict.fromkeys(x for x in X if x is not None))
    ykeys = list(dict.fromkeys(y for y in Y if y is not None))
    rowmean = {y: (sum(v for (x_, y_), (v, _) in cells.items() if y_ == y and v is not None) /
                   max(1, sum(1 for (x_, y_), (v, _) in cells.items() if y_ == y and v is not None))) for y in ykeys}
    ykeys.sort(key=lambda y: -rowmean[y])
    vals = [v for v, _ in cells.values() if v is not None]
    if not vals:
        return S.text(20, 30, "No values to draw.", size=13), 50
    ramp = _ramp(ctx, 5)
    edges = _classes(vals, len(ramp))
    while len(edges) - 1 > len(ramp):
        edges = S.nice_ticks(min(vals), max(vals), len(edges) - 3)
    ramp = ramp[: len(edges) - 1] if len(edges) - 1 < len(ramp) else ramp
    left = _left_margin(ykeys, 12, cap=W * 0.32) + 8
    right = 12
    cw = (W - left - right) / max(1, len(xkeys))
    ch = 24 if len(ykeys) <= 20 else 16
    top = 24
    out = []
    every = max(1, math.ceil(len(xkeys) / max(1, (W - left) / 48)))
    stagger = every <= 2 and cw >= 28 and max(S.text_width(x, 11) for x in xkeys) > cw - 4
    if stagger:
        every = 1
    if stagger:
        top += 14
    for j, x in enumerate(xkeys):
        if j % every == 0:
            cx = left + j * cw + cw / 2
            room = (2 * cw - 18) if stagger else cw * every - 6
            room = min(room, 2 * (W - cx) - 4)
            dy = (14 if j % 2 == 0 else 0) if stagger else 0
            out.append(S.text(cx, top - 8 - dy, S.truncate(x, 11, room), size=11, fill=S.MUTED, anchor="middle"))
    show_vals = cw >= 34 and ch >= 18
    for i, y in enumerate(ykeys):
        yy = top + i * ch
        out.append(S.text(left - 8, yy + ch / 2 + 4, S.truncate(y, 12, left - 12), size=12, fill=S.INK, anchor="end"))
        for j, x in enumerate(xkeys):
            v, st = cells.get((x, y), (None, "no data"))
            xx = left + j * cw
            if v is None:
                stl = _state_label(st)
                out.append(S.rect(xx, yy, cw - 1, ch - 1, S.MISSING_FILL, extra=f'class="vz-missing" data-state="{S.esc(stl)}"',
                                  tip=f"{y} · {x}: {stl}"))
                continue
            c = ramp[_bin(v, edges)]
            out.append(S.rect(xx, yy, cw - 1, ch - 1, c, extra='class="vz-mark"', tip=f"{y} · {x}: {S.fmt(v, unit)}"))
            if show_vals:
                out.append(S.text(xx + cw / 2, yy + ch / 2 + 4, S.fmt(v, unit, compact=abs(v) >= 10000), size=10,
                                  fill=G.ink_on(c)["ink"], anchor="middle"))
    base = top + len(ykeys) * ch + 14
    leg, lh = _legend_ramp(ctx, edges, ramp, unit, left, base, f"{ctx.label(vcol)}{S.unit_suffix(unit)}")
    out.append(leg)
    return "\n".join(out), base + lh + 6


# ------------------------------------------------------------------ choropleth

_PATH_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _geojson_paths(gj: dict, key: str | None) -> dict[str, list[list[tuple[float, float]]]]:
    feats = gj.get("features") or []
    out: dict[str, list] = {}
    for f in feats:
        props = f.get("properties") or {}
        k = props.get(key) if key else (f.get("id") or props.get("id") or props.get("GEOID") or props.get("name"))
        if k is None:
            continue
        g = f.get("geometry") or {}
        polys = []
        if g.get("type") == "Polygon":
            polys = g["coordinates"]
        elif g.get("type") == "MultiPolygon":
            polys = [ring for poly in g["coordinates"] for ring in poly]
        out.setdefault(str(k), []).extend([[(float(x), float(y)) for x, y, *_ in ring] for ring in polys])
    return out


def _reproject_path(geom: str, tx) -> str:
    """Re-project a pre-projected SVG path (M/L/Z polygons) into the figure's box."""
    dd = []
    for seg in re.split(r"(?=[Mm])", geom.strip()):
        nums = [float(t) for t in _PATH_NUM.findall(seg)]
        ps = list(zip(nums[0::2], nums[1::2]))
        if ps:
            dd.append("M" + " L".join(f"{tx(a, b)[0]:.1f},{tx(a, b)[1]:.1f}" for a, b in ps) + "Z")
    return " ".join(dd)


def render_choropleth(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    vcol = o.roles["value"]
    lab = o.roles.get("label")
    V = ctx.num(vcol)
    L = ctx.cat(lab) if lab else [None] * len(V)
    unit = ctx.unit(vcol)
    shapes: list[tuple[str, Any, float | None, str | None, int]] = []   # (label, geometry, value, state, row)
    gcol = o.roles.get("geometry")
    if gcol and gcol != "__geojson__":
        P = ctx.cat(gcol)
        pts_all = []
        for i, p in enumerate(P):
            if not p:
                continue
            nums = [float(t) for t in _PATH_NUM.findall(p)]
            pts_all.extend(zip(nums[0::2], nums[1::2]))
            shapes.append((L[i] or "", p, V[i], ctx.state(vcol, i), i))
        xs_ = [a for a, _ in pts_all]
        ys_ = [b for _, b in pts_all]
        bx0, bx1, by0, by1 = min(xs_), max(xs_), min(ys_), max(ys_)
        flip = False
    else:
        key = ctx.geo_key or o.roles.get("key")
        polys = _geojson_paths(ctx.geojson or {}, ctx.geo_key)
        K = ctx.cat(key) if key else [None] * len(V)
        allp = [pt for rings in polys.values() for ring in rings for pt in ring]
        if not allp:
            return S.text(20, 30, "No outlines matched the table's keys.", size=13), 50
        lat0 = sum(y for _, y in allp) / len(allp)
        kx = math.cos(math.radians(lat0))
        bx0, bx1 = min(x for x, _ in allp) * kx, max(x for x, _ in allp) * kx
        by0, by1 = min(y for _, y in allp), max(y for _, y in allp)
        flip = True
        matched = 0
        for i, k in enumerate(K):
            if k is None or str(k) not in polys:
                continue
            matched += 1
            rings = polys[str(k)]
            shapes.append((L[i] or str(k), [[(x * kx, y) for x, y in r] for r in rings], V[i], ctx.state(vcol, i), i))
        if matched < len(K):
            ctx.apply("unmatched-areas", f"{len(K) - matched} row(s) had no matching outline and are not on the map.")
    present = [s[2] for s in shapes if s[2] is not None]
    if not present:
        return S.text(20, 30, "No values to map.", size=13), 50
    ramp = _ramp(ctx, 5)
    srt = sorted(present)
    # quantile classes: each color holds about the same number of areas
    edges = [srt[0]] + [srt[min(len(srt) - 1, int(len(srt) * q / len(ramp)))] for q in range(1, len(ramp))] + [srt[-1]]
    edges = sorted(set(edges))
    ramp = ramp[: max(1, len(edges) - 1)]
    avail_w = W - 32
    aspect = (by1 - by0) / max(1e-9, (bx1 - bx0))
    mw = avail_w
    mh = mw * aspect
    if mh > 620:
        mh = 620
        mw = mh / aspect
    sc = mw / max(1e-9, (bx1 - bx0))
    ox = 16 + (avail_w - mw) / 2
    oy = 8

    def tx(x, y):
        return ox + (x - bx0) * sc, oy + ((by1 - y) if flip else (y - by0)) * sc

    out = [f'<g class="vz-map" stroke="{S.SURFACE}" stroke-width="0.4">']
    for name, geom, v, st, i in shapes:
        fill = ramp[_bin(v, edges)] if v is not None else S.MISSING_FILL
        cls = 'class="vz-mark"' if v is not None else f'class="vz-missing" data-state="{S.esc(_state_label(st))}"'
        tip = f"{name}: {S.fmt(v, unit) if v is not None else _state_label(st)}"
        if isinstance(geom, str):
            d = _reproject_path(geom, tx)
        else:
            d = " ".join("M" + " L".join(f"{tx(a, b)[0]:.1f},{tx(a, b)[1]:.1f}" for a, b in ring) + "Z" for ring in geom)
        out.append(S.path(d, fill=fill, stroke=S.SURFACE, width=0.4, extra=cls, tip=tip))
        if name:
            nums2 = [float(t) for t in _PATH_NUM.findall(d)]
            if nums2:
                cx = sum(nums2[0::2]) / len(nums2[0::2])
                cy = sum(nums2[1::2]) / len(nums2[1::2])
                ctx.anchors[str(name)] = (cx, cy)
    out.append("</g>")
    base = oy + mh + 14
    leg, lh = _legend_ramp(ctx, edges, ramp, unit, 16, base, f"{ctx.label(vcol)}{S.unit_suffix(unit)}")
    out.append(leg)
    out.append(S.text(16, base + lh + 10, "Classes hold about equal numbers of areas (quantiles).", size=10, fill=S.MUTED))
    out += _annotations(ctx, W)
    return "\n".join(out), base + lh + 18


# ------------------------------------------------------------------ stat tile

def render_stat_tile(ctx: Ctx) -> tuple[str, float]:
    o = ctx.option
    W = ctx.width
    cols = o.roles.get("values") or [o.roles.get("value")]
    by = o.roles.get("by")
    items = []
    if by:
        for i, (k, v) in enumerate(zip(ctx.cat(by), ctx.num(cols[0]))):
            items.append((str(k), v, ctx.unit(cols[0]), ctx.state(cols[0], i)))
    else:
        for c in cols:
            v = ctx.num(c)[0] if ctx.num(c) else None
            items.append((ctx.label(c), v, ctx.unit(c), ctx.state(c, 0)))
    n = len(items)
    tw = (W - 32 - (n - 1) * 16) / n
    out = []
    for i, (label, v, unit, st) in enumerate(items):
        x = 16 + i * (tw + 16)
        out.append(S.rect(x, 0, tw, 120, "#f3f2ee", extra='rx="6"'))
        if v is None:
            out.append(S.text(x + 16, 62, _state_label(st), size=28, fill=S.MUTED,
                              extra=f'class="vz-missing" data-state="{S.esc(_state_label(st))}"'))
        else:
            out.append(S.text(x + 16, 66, S.fmt(v, unit), size=44 if n == 1 else 34, fill=S.INK, weight="600", extra='class="vz-mark"'))
        for j, ln in enumerate(S.wrap(label, 13, tw - 32)[:2]):
            out.append(S.text(x + 16, 92 + j * 16, ln, size=13, fill=S.INK2))
    return "\n".join(out), 128


RENDERERS = {
    "bar-chart": render_bar,
    "stacked-bar": render_stacked_bar,
    "line-chart": render_line,
    "stacked-area": render_stacked_area,
    "scatterplot": render_scatter,
    "dot-plot": render_dot,
    "strip-plot": render_strip,
    "histogram": render_histogram,
    "slope-chart": render_slope,
    "small-multiples": render_small_multiples,
    "heatmap": render_heatmap,
    "choropleth": render_choropleth,
    "stat-tile": render_stat_tile,
}


def render_svg(ctx: Ctx) -> str:
    """Render the option to a complete, self-contained SVG document."""
    fn = RENDERERS[ctx.option.form]
    body, h = fn(ctx)
    return S.frame(body, h, ctx.words, width=ctx.width, aria=_aria(ctx), form=ctx.option.form)


def _aria(ctx: Ctx) -> str:
    o = ctx.option
    roles = ", ".join(f"{k}: {ctx.label(v) if isinstance(v, str) else ', '.join(ctx.label(x) for x in v)}"
                      for k, v in o.roles.items() if v and isinstance(v, (str, list)) and not str(v).startswith("__"))
    t = ctx.words.title or o.title
    return f"{o.title}. {t}. {roles}."


def spec_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)
