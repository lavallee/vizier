"""`vizier show` — someone asked to see their data; show them how.

Profile the table, rank the ways to show it (charts, and a sentence, a stat
tile or a table when one of those serves better), draw the best few from the
real rows, put the words on them, attach the honesty notes, check the drawn
SVG with vizier's own analyzers, and optionally build the chart in
Datawrapper. Works with no model and no network.

    from vizier.show import show
    result = show("table.csv", claim="Asthma is higher where diesel is", out_dir="out/")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .. import __version__
from . import compose as Cm
from . import datawrapper as DW
from . import notes as N
from . import render as R
from . import svg as S
from .profile import Profile, profile_table
from .rank import Option, rank_forms
from .table import Table, load_table

SPEC_SCHEMA = "vizier/show-spec/v1"

__all__ = ["show", "load_table", "profile_table", "rank_forms", "SPEC_SCHEMA"]


def _is_question(claim: str | None) -> bool:
    if not claim:
        return False
    c = claim.strip().lower()
    return c.endswith("?") or c.split(" ", 1)[0] in ("how", "what", "where", "which", "who", "when", "why", "does", "do", "is", "are", "did")


def _sentence_case(s: str) -> str:
    s = s.strip()
    return s[:1].upper() + s[1:] if s else s


def _lab(profile: Profile, c: Any) -> str:
    if isinstance(c, list):
        return ", ".join(_lab(profile, x) for x in c)
    p = profile.get(c) if isinstance(c, str) else None
    return p.label if p else str(c or "")


def _auto_title(profile: Profile, o: Option) -> str:
    r = o.roles
    f = o.form
    if f == "scatterplot":
        return f"{_lab(profile, r['y'])} against {_lab(profile, r['x']).lower()}"
    if f in ("histogram", "strip-plot"):
        return f"How {_lab(profile, r['x']).lower()} is distributed"
    if f in ("line-chart", "stacked-area", "slope-chart"):
        return f"{_lab(profile, r['y'])} over time"
    if f == "small-multiples":
        return f"{_lab(profile, r['y'])} by {_lab(profile, r.get('facet') or r.get('series') or r.get('x')).lower()}"
    if f == "heatmap":
        return f"{_lab(profile, r['value'])} by {_lab(profile, r['y']).lower()} and {_lab(profile, r['x']).lower()}"
    if f == "choropleth":
        return f"{_lab(profile, r['value'])}, mapped"
    if f in ("bar-chart", "stacked-bar", "dot-plot") and r.get("x") and r.get("y") and not str(r["x"]).startswith("__"):
        return f"{_lab(profile, r['y'])} by {_lab(profile, r['x']).lower()}"
    if f == "stat-tile":
        return _lab(profile, r.get("values") or r.get("value"))
    return o.title


def _source_line(table: Table, explicit: str | None) -> str:
    if explicit:
        return explicit
    pkg = table.package or {}
    srcs = pkg.get("sources") or []
    for res in pkg.get("resources") or []:
        srcs = srcs or res.get("sources") or []
    names = [s.get("title") or s.get("path") for s in srcs if isinstance(s, dict)]
    names = [n for n in names if n]
    if names:
        return "; ".join(names)
    return Path(table.source).name if table.source else ""


def _subtitle(table: Table, profile: Profile, o: Option, claim: str | None, explicit: str | None) -> str:
    if explicit:
        return explicit
    parts = []
    if claim and _is_question(claim):
        parts.append(_sentence_case(claim))
    r = o.roles
    if o.form == "scatterplot":
        n = _n_plotted(table, [r.get("x"), r.get("y")])
        parts.append(f"Each dot is one row ({n:,} of {profile.n_rows:,} have both values)." if n < profile.n_rows
                     else f"Each dot is one row ({n:,} rows).")
    elif o.form == "strip-plot":
        n = _n_plotted(table, [r.get("x")])
        parts.append(f"Each dot is one row ({n:,} rows).")
    if o.form == "choropleth":
        parts.append(f"{profile.n_rows:,} areas, shaded by {_lab(profile, r['value']).lower()}.")
    seen = set()
    for c in (r.get("y"), r.get("value"), r.get("x")):
        p = profile.get(c) if isinstance(c, str) else None
        if p and p.description and p.role == "measure" and c not in seen and o.form not in ("sentence", "table"):
            seen.add(c)
            parts.append(f"{p.label}: {p.description.rstrip('.')}.")
    return " ".join(parts)


def _n_plotted(table: Table, cols: list) -> int:
    """Rows with a usable number in every one of `cols`."""
    from .profile import parse_number
    cs = [c for c in cols if isinstance(c, str)]
    return sum(1 for r in table.rows if all(parse_number(r.get(c)) is not None for c in cs))


def _checks(svg: str, ramp: list[str] | None = None) -> dict[str, Any]:
    """Run vizier's own artifact checks on the SVG it just drew.

    A figure colored by a sequential ramp is checked as an ordinal ramp (monotone
    lightness, visible steps); categorical colors are checked pairwise."""
    from ..analyze import color as C, extract as X, structure as St
    ex = X.extract(svg)
    out: dict[str, Any] = {"palette": ex.palette, "achromatic": ex.achromatic}
    if ramp:
        rep = C.validate_ordinal(ramp)
        out["ramp"] = ramp
        out["color_ok"] = rep.ok
        out["color_report"] = C.format_report(rep)
    elif ex.palette:
        rep = C.validate_categorical(ex.palette, pairs="all") if len(ex.palette) > 1 else None
        if rep is not None:
            out["color_ok"] = rep.ok
            out["color_report"] = C.format_report(rep)
    st = St.lint_svg(svg)["findings"]
    out["structure"] = st
    bits = [f"{len(ramp)}-step ordinal ramp" if ramp else f"{len(ex.palette)} data color(s)"]
    if "color_ok" in out:
        what = "ramp" if ramp else "palette"
        bits.append(f"{what} passes the {'ordinal' if ramp else 'colorblind/contrast'} checks" if out["color_ok"]
                    else f"{what} has a FAIL in the color checks (see report)")
    bits.append("no structural findings" if not st else f"{len(st)} structural finding(s): " + "; ".join(f["check"] for f in st))
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(svg)
        bits.append("well-formed SVG")
        out["well_formed"] = True
    except ET.ParseError as e:  # pragma: no cover - would be a renderer bug
        bits.append(f"NOT well-formed: {e}")
        out["well_formed"] = False
    out["summary"] = ", ".join(bits)
    return out


def _dual_axis(profile: Profile, overrides: dict[str, Any]) -> tuple[str, str] | None:
    y = (overrides or {}).get("y")
    if not y or "," not in str(y):
        return None
    cols = [profile.get(c.strip()) for c in str(y).split(",") if c.strip()]
    cols = [c for c in cols if c is not None and c.role == "measure"]
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            if (cols[i].unit or "") != (cols[j].unit or ""):
                return cols[i].name, cols[j].name
    return None


def _pick(options: list[Option], top: int) -> list[Option]:
    drawable = [o for o in options if o.drawable]
    pick = drawable[:top]
    charts = [o for o in drawable if o.is_chart]
    if charts and not any(o.is_chart for o in pick):
        pick = pick[: max(0, top - 1)] + [charts[0]]
    return pick


def show(
    source: str | Path | Table,
    *,
    claim: str | None = None,
    overrides: dict[str, Any] | None = None,
    out_dir: str | Path | None = None,
    top: int = 3,
    caveats: list[dict[str, str]] | str | Path | None = None,
    geometry: str | Path | dict | None = None,
    geo_key: str | None = None,
    zero: bool = False,
    width: int = 680,
    title: str | None = None,
    subtitle: str | None = None,
    source_line: str | None = None,
    annotations: dict[str, str] | None = None,
    datawrapper: bool = False,
    publish: bool = False,
    dw_client: DW.DatawrapperClient | None = None,
    datapackage: str | Path | None = None,
    bar_top: int = 15,
) -> dict[str, Any]:
    """Profile, rank, render and annotate. Returns the `vizier/show-spec/v1` dict."""
    table = source if isinstance(source, Table) else load_table(source, datapackage=datapackage)
    profile = profile_table(table)
    gj = None
    if geometry is not None:
        gj = geometry if isinstance(geometry, dict) else json.loads(Path(geometry).read_text())
    overrides = {k: v for k, v in (overrides or {}).items() if v}
    options, fields = rank_forms(profile, claim, overrides=overrides,
                                 geometry_available=(profile.geometry is not None or gj is not None))
    if gj is not None:
        for o in options:
            if o.form == "choropleth":
                o.drawable = True
                o.needs = None
                o.roles["geometry"] = "__geojson__"
                o.roles.setdefault("key", geo_key)
        options.sort(key=lambda o: (not o.drawable, -o.score))
        for i, o in enumerate(options, 1):
            o.rank = i
    cav = N.load_caveats(caveats) if isinstance(caveats, (str, Path)) else list(caveats or [])
    dual = _dual_axis(profile, overrides)
    if dual and fields.time is not None:
        # Never two y-axes: the second measure gets a figure of its own.
        second = profile.get(dual[1])
        base = next((o for o in options if o.form == "line-chart"), None)
        if base is not None and second is not None:
            extra = Option(form="line-chart", title=base.title, score=base.score - 0.5,
                           reason=f"{second.label} in its own figure, on its own axis — not a second y-axis.",
                           roles={**base.roles, "y": second.name}, shows=base.shows, hides=base.hides,
                           mistakes=list(base.mistakes), variant="second-measure")
            base.roles["y"] = dual[0]
            options.insert(options.index(base) + 1, extra)
            for i, o in enumerate(options, 1):
                o.rank = i

    picked = _pick(options, top)
    out = Path(out_dir) if out_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    svgs: dict[int, str] = {}
    sentences: dict[int, str] = {}
    tables: dict[int, str] = {}
    entries: list[dict[str, Any]] = []
    words_by_rank: dict[int, S.Words] = {}
    primary = fields.measures[0].name if fields.measures else None

    for o in options:
        e = o.to_dict()
        e["rendered"] = o in picked
        t, why = DW.dw_type(o)
        e["datawrapper"] = {"type": t, "why": why}
        entries.append(e)
        if o not in picked:
            continue
        i = o.rank - 1
        words = S.Words(
            title=title or (_sentence_case(claim) if claim and not _is_question(claim) else _sentence_case(_auto_title(profile, o))),
            subtitle=_subtitle(table, profile, o, claim, subtitle),
            source=_source_line(table, source_line),
            annotations=dict(annotations or {}),
        )
        if o.form in ("bar-chart", "dot-plot", "strip-plot") and isinstance(o.roles.get("y"), str) and o.variant not in ("time",):
            ycol = o.roles["y"] if o.form != "strip-plot" else o.roles["x"]
            p = profile.get(ycol)
            if p:
                words.x_label = f"{p.label}{S.unit_suffix(p.unit)}"
        e["words"] = None
        if o.form == "sentence":
            sentences[i] = Cm.sentence(table, profile, o)
            e["text"] = sentences[i]
            e["notes"] = []
        elif o.form == "table":
            tables[i] = Cm.table_html(table, profile, sort_by=primary)
            e["notes"] = N.honesty_notes(profile, fields, o, applied=[])
            e["notes"] = [n for n in e["notes"] if n["check"] in ("suppressed-values", "rate-without-denominator")]
        else:
            ctx = R.Ctx(table=table, profile=profile, option=o, words=words, width=width, zero=zero,
                        geojson=gj, geo_key=geo_key, top=bar_top)
            body, h = R.RENDERERS[o.form](ctx)
            notes = N.honesty_notes(profile, fields, o, applied=ctx.applied,
                                    dual_axis=dual if o.form == "line-chart" else None)
            if any(n["check"] == "small-sample" for n in notes):
                k = next(n for n in notes if n["check"] == "small-sample")["detail"]
                words.subtitle = (words.subtitle + " " if words.subtitle else "") + k.replace(" is stated on the figure.", "") + "."
            words.notes = N.figure_notes(notes, cav)
            svg = S.frame(body, h, words, width=width, aria=R._aria(ctx), form=o.form)
            svgs[i] = svg
            e["notes"] = notes
            e["colors"] = {k: v for k, v in ctx.colors.items()}
            if ctx.palette_advice:
                e["palette_advice"] = ctx.palette_advice
            e["checks"] = _checks(svg, ctx.ramp or None)
        if o.form in ("sentence", "table") and cav:
            e.setdefault("notes", [])
        e["words"] = {"title": words.title, "subtitle": words.subtitle, "x_label": words.x_label,
                      "y_label": words.y_label, "source": words.source, "notes": words.notes,
                      "annotations": words.annotations}
        words_by_rank[o.rank] = words
        if out:
            files = {}
            stem = f"{o.rank:02d}-{o.form}" + (f"-{o.variant}" if o.variant else "")
            if i in svgs:
                (out / f"{stem}.svg").write_text(svgs[i], encoding="utf-8")
                files["svg"] = f"{stem}.svg"
            if i in sentences:
                (out / f"{stem}.txt").write_text(sentences[i] + "\n", encoding="utf-8")
                files["text"] = f"{stem}.txt"
            if i in tables:
                (out / f"{stem}.csv").write_text(table.to_csv([c.name for c in profile.columns if c.role != "geometry"]), encoding="utf-8")
                files["csv"] = f"{stem}.csv"
            e["files"] = files

    result: dict[str, Any] = {
        "schema": SPEC_SCHEMA,
        "vizier_version": __version__,
        "source": {"path": table.source, "name": table.name, "rows": len(table),
                   "datapackage": bool(table.package)},
        "claim": claim,
        "fields": fields.names(),
        "profile": profile.to_dict(),
        "chosen": next((e["rank"] for e in entries if e["rendered"]), 1),
        "options": entries,
        "caveats": cav,
    }

    if datawrapper:
        result["datawrapper"] = _datawrapper(table, profile, options, picked, words_by_rank, publish, dw_client, bar_top)

    if out:
        result["files"] = {"html": "index.html", "spec": "spec.json"}
        html = Cm.page(result, svgs=svgs, sentences=sentences, tables=tables,
                       data_table=Cm.table_html(table, profile, sort_by=primary), profile=profile)
        (out / "index.html").write_text(html, encoding="utf-8")
        (out / "spec.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        result["out_dir"] = str(out)
    return result


def _datawrapper(table, profile, options, picked, words_by_rank, publish, client, bar_top) -> dict[str, Any]:
    chosen = None
    skipped = []
    for o in picked + [x for x in options if x not in picked and x.drawable]:
        t, why = DW.dw_type(o)
        if t:
            chosen = o
            break
        skipped.append({"form": o.form, "why": why})
    if chosen is None:
        return {"sent": False, "why": "None of the ranked forms has a Datawrapper equivalent.", "skipped": skipped}
    words = words_by_rank.get(chosen.rank) or S.Words(title=chosen.title, source=_source_line(table, None))
    plan = DW.build_requests(table, profile, chosen, words, publish=publish, top=bar_top)
    out = {"form": chosen.form, "variant": chosen.variant, "type": plan.get("type"), "why": plan.get("why"),
           "skipped": skipped, "requests": plan["requests"]}
    token = client.token if client else DW.token_from_env()
    if not token:
        out["sent"] = False
        out["dry_run"] = True
        out["message"] = ("DATAWRAPPER_API_TOKEN is not set, so nothing was sent. These are the exact requests "
                          "vizier would make (plus an Authorization: Bearer header).")
        return out
    cl = client or DW.DatawrapperClient(token=token)
    out.update(cl.run(plan))
    out["sent"] = True
    out["dry_run"] = False
    return out
