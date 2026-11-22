"""The non-chart forms and the page: sentences, tables, and the offline HTML."""

from __future__ import annotations

from html import escape
from statistics import median
from typing import Any

from . import svg as S
from .profile import Profile, parse_number, parse_time
from .rank import Option
from .table import Table


def _v(table: Table, col: str, i: int) -> float | None:
    return parse_number(table.rows[i].get(col))


def _label(profile: Profile, col: str) -> str:
    p = profile.get(col)
    return p.label if p else col


def _unit(profile: Profile, col: str) -> str | None:
    p = profile.get(col)
    return p.unit if p else None


def _diff_phrase(a: float, b: float, unit: str | None) -> str:
    d = b - a
    word = "higher" if d > 0 else "lower"
    if d == 0:
        return "the same"
    head = f"{S.fmt(abs(d), unit if unit != '%' else None)}{' percentage points' if unit == '%' else ''} {word}"
    if a not in (0, None) and unit != "%":
        return f"{head} ({abs(d) / abs(a) * 100:.0f}%)"
    return head


def sentence(table: Table, profile: Profile, option: Option) -> str:
    """Write the sentence the ranking offered. Plain, exact, with units."""
    s = _sentence(table, profile, option)
    return s[:1].upper() + s[1:] if s else s


def _sentence(table: Table, profile: Profile, option: Option) -> str:
    r = option.roles
    vals = r.get("values") or []
    n = len(table)
    if r.get("by") and vals:
        col, by = vals[0], r["by"]
        unit = _unit(profile, col)
        items = [(table.rows[i].get(by), _v(table, col, i)) for i in range(n)]
        if len(items) == 2 and all(v is not None for _, v in items):
            (k1, a), (k2, b) = items
            return (f"{_label(profile, col)} is {S.fmt(a, unit)} for {k1} and {S.fmt(b, unit)} for {k2} — "
                    f"{k2} is {_diff_phrase(a, b, unit)}.")
    if r.get("time") and vals:
        col, tcol = vals[0], r["time"]
        unit = _unit(profile, col)
        gran = profile.get(tcol).granularity if profile.get(tcol) else None
        pts = []
        for i in range(n):
            t = parse_time(table.rows[i].get(tcol), year_ok=True)
            tv = t[0] if t else parse_number(table.rows[i].get(tcol))
            v = _v(table, col, i)
            if tv is not None and v is not None:
                pts.append((tv, v))
        pts.sort()
        if len(pts) >= 2:
            (t0, a), (t1, b) = pts[0], pts[-1]
            verb = "rose" if b > a else ("fell" if b < a else "held")
            s = (f"{_label(profile, col)} {verb} from {S.fmt(a, unit)} in {S.fmt_time(t0, gran)} "
                 f"to {S.fmt(b, unit)} in {S.fmt_time(t1, gran)}")
            if verb != "held":
                s += f" ({_diff_phrase(a, b, unit)})"
            if len(pts) > 2:
                tm, vm = max(pts, key=lambda p: p[1])
                if tm not in (t0, t1):
                    s += f", peaking at {S.fmt(vm, unit)} in {S.fmt_time(tm, gran)}"
            return s + "."
    if n == 1 and vals:
        parts = [f"{_label(profile, c)} is {S.fmt(_v(table, c, 0), _unit(profile, c))}" for c in vals]
        if len(parts) == 2:
            a, b = (_v(table, c, 0) for c in vals)
            same_unit = _unit(profile, vals[0]) == _unit(profile, vals[1])
            tail = ""
            if same_unit and a is not None and b is not None:
                tail = f" — the second is {_diff_phrase(a, b, _unit(profile, vals[0]))}"
            return f"{parts[0]}; {parts[1][0].lower() + parts[1][1:]}{tail}."
        return "; ".join(parts) + "."
    if vals:
        col = vals[0]
        unit = _unit(profile, col)
        label_col = next((c.name for c in profile.columns if c.role in ("label", "dimension", "identifier")), None)
        pts = [(table.rows[i].get(label_col) if label_col else None, _v(table, col, i)) for i in range(n)]
        pts = [(k, v) for k, v in pts if v is not None]
        if not pts:
            return f"No usable values of {_label(profile, col)}."
        lo = min(pts, key=lambda p: p[1])
        hi = max(pts, key=lambda p: p[1])
        md = median(v for _, v in pts)
        name = lambda p: f" ({p[0]})" if p[0] else ""  # noqa: E731
        return (f"Across {len(pts)} rows, {_label(profile, col).lower()} ranges from {S.fmt(lo[1], unit)}{name(lo)} "
                f"to {S.fmt(hi[1], unit)}{name(hi)}, with a median of {S.fmt(md, unit)}.")
    return ""


def table_html(table: Table, profile: Profile, *, sort_by: str | None = None, limit: int = 200) -> str:
    cols = [c for c in profile.columns if c.role != "geometry"]
    idx = list(range(len(table)))
    if sort_by:
        idx.sort(key=lambda i: (_v(table, sort_by, i) is None, -(_v(table, sort_by, i) or 0)))
    head = "".join(
        f'<th class="{"num" if c.role == "measure" else ""}">{escape(c.label)}'
        f'{escape(S.unit_suffix(c.unit)) if c.unit else ""}</th>' for c in cols)
    body = []
    for i in idx[:limit]:
        tds = []
        for c in cols:
            raw = table.rows[i].get(c.name)
            st = table.state_of(c.name, i)
            if raw is None:
                tds.append(f'<td class="{"num" if c.role == "measure" else ""} gap">{escape(st or "–")}</td>')
            elif c.role == "measure":
                tds.append(f'<td class="num">{escape(S.fmt(parse_number(raw), None))}</td>')
            else:
                tds.append(f"<td>{escape(raw)}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    more = f'<p class="muted">Showing {limit} of {len(table)} rows.</p>' if len(table) > limit else ""
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>{more}'


CSS = """
:root{--ink:#1a1a19;--ink2:#5f5e5a;--muted:#8a8984;--rule:#e6e5e0;--surface:#fcfcfb;--tint:#f3f2ee;--accent:#2a78d6}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--ink);font:15px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 20px 80px}h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:40px 0 8px;padding-top:16px;border-top:1px solid var(--rule)}
h3{font-size:15px;margin:20px 0 6px}.muted{color:var(--muted)}.lede{color:var(--ink2);margin:0 0 20px}
figure{margin:12px 0 8px}figure svg{max-width:100%;height:auto;display:block}
.rank{display:inline-block;min-width:1.6em;padding:0 6px;border-radius:10px;background:var(--tint);color:var(--ink2);font-size:13px;text-align:center;margin-right:6px}
.why{margin:4px 0 8px}.tradeoffs{display:grid;grid-template-columns:7em 1fr;gap:2px 12px;font-size:14px;color:var(--ink2);margin:6px 0}
.tradeoffs dt{color:var(--muted)}.tradeoffs dd{margin:0}
.sentence{font-size:20px;line-height:1.4;padding:16px 20px;background:var(--tint);border-radius:6px;margin:10px 0}
.notes{font-size:14px;padding-left:18px}.notes li{margin:4px 0}.tag{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin-right:4px}
.applied{color:#1d6b3f}.files{font-size:13px;color:var(--muted)}.files a{color:var(--ink2)}
.tbl{overflow-x:auto;max-height:480px;overflow-y:auto;border:1px solid var(--rule);border-radius:4px}
table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:4px 8px;border-bottom:1px solid var(--rule);text-align:left;white-space:nowrap}
th{position:sticky;top:0;background:var(--surface);font-weight:600}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}td.gap{color:var(--muted);font-style:italic}
details{margin:8px 0}summary{cursor:pointer;color:var(--ink2)}code{font-size:13px;background:var(--tint);padding:1px 4px;border-radius:3px}
"""


def _tradeoffs(o: dict[str, Any]) -> str:
    rows = []
    if o.get("shows"):
        rows.append(f"<dt>Shows well</dt><dd>{escape(o['shows'])}</dd>")
    if o.get("hides"):
        rows.append(f"<dt>Hides</dt><dd>{escape(o['hides'])}</dd>")
    for i, m in enumerate(o.get("mistakes") or []):
        rows.append(f"<dt>{'Common mistakes' if i == 0 else ''}</dt><dd>{escape(m)}</dd>")
    return f'<dl class="tradeoffs">{"".join(rows)}</dl>'


def _notes_html(notes: list[dict[str, Any]]) -> str:
    if not notes:
        return ""
    items = []
    for n in notes:
        tag = '<span class="tag applied">applied</span>' if n.get("applied") else f'<span class="tag">{escape(n.get("severity", ""))}</span>'
        detail = f" <em>{escape(n['detail'])}</em>" if n.get("detail") else ""
        items.append(f"<li>{tag}<strong>{escape(n['check'])}</strong> — could be misread: {escape(n['misread'])} "
                     f"Fix: {escape(n['fix'])}{detail}</li>")
    return f'<h3>Honesty notes</h3><ul class="notes">{"".join(items)}</ul>'


def page(result: dict[str, Any], *, svgs: dict[int, str], sentences: dict[int, str], tables: dict[int, str],
         data_table: str, profile: Profile) -> str:
    """A single offline HTML page: best option first, then the others, then the ranking."""
    opts = result["options"]
    claim = result.get("claim")
    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>{escape(result['source']['name'])} — vizier show</title><style>{CSS}</style></head><body><main>",
           f"<h1>How to show {escape(result['source']['name'])}</h1>",
           f"<p class=lede>{result['source']['rows']} rows · {len(profile.columns)} columns"
           + (f" · for: <em>{escape(claim)}</em>" if claim else "") + "</p>"]
    rendered = [o for o in opts if o.get("rendered")]
    for k, o in enumerate(rendered):
        i = o["rank"] - 1
        if k == 0:
            out.append("<h2>Best first</h2>")
        elif k == 1:
            out.append("<h2>Other ways to show it</h2>")
        out.append(f"<h3><span class=rank>{o['rank']}</span>{escape(o['title'])}</h3>")
        out.append(f"<p class=why>{escape(o['reason'])}</p>")
        if i in svgs:
            out.append(f"<figure>{svgs[i]}</figure>")
        if i in sentences:
            out.append(f"<p class=sentence>{escape(sentences[i])}</p>")
        if i in tables:
            out.append(tables[i])
        out.append(_tradeoffs(o))
        out.append(_notes_html(o.get("notes") or []))
        files = o.get("files") or {}
        if files:
            out.append("<p class=files>" + " · ".join(f'<a href="{escape(v)}">{escape(v)}</a>' for v in files.values()) + "</p>")
        if o.get("checks") and o["checks"].get("summary"):
            out.append(f"<p class=files>Checks on the drawn SVG: {escape(o['checks']['summary'])}</p>")
    out.append("<h2>The full ranking</h2><table><thead><tr><th>#</th><th>Form</th><th>Why</th></tr></thead><tbody>")
    for o in opts:
        why = o["reason"] + (f" Needs: {o['needs']}" if o.get("needs") else "")
        out.append(f"<tr><td>{o['rank']}</td><td>{escape(o['title'])}{'' if o.get('drawable', True) else ' <span class=muted>(not drawable yet)</span>'}</td>"
                   f"<td style='white-space:normal'>{escape(why)}</td></tr>")
    out.append("</tbody></table>")
    out.append("<h2>What's in the table</h2><table><thead><tr><th>Column</th><th>Kind</th><th>Role</th><th>Range / values</th><th>Missing</th></tr></thead><tbody>")
    for c in profile.columns:
        rng = (f"{S.fmt(c.min, c.unit)} – {S.fmt(c.max, c.unit)}" if c.min is not None and c.role == "measure"
               else (f"{c.n_distinct} distinct" + (f" · {c.granularity}" if c.granularity else "") + (f" · {c.geo}" if c.geo else "")))
        miss = str(c.n_missing) + (f" ({c.n_suppressed} suppressed / not collected)" if c.n_suppressed else "")
        out.append(f"<tr><td>{escape(c.label)}</td><td>{c.kind}</td><td>{c.role}</td><td style='white-space:normal'>{escape(rng)}</td><td>{escape(miss)}</td></tr>")
    out.append("</tbody></table>")
    for note in profile.notes:
        out.append(f"<p class=muted>{escape(note)}</p>")
    out.append(f"<details><summary>The data</summary>{data_table}</details>")
    out.append(f"<p class=muted>Made by vizier {escape(result.get('vizier_version', ''))} · works offline, no scripts.</p>")
    out.append("</main></body></html>")
    return "\n".join(out)
