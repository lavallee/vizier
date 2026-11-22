"""`vizier show`: profiling, ranking, rendering, notes — all offline, no model.

Runnable: uv run pytest tests/test_show.py -q
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from vizier.show import show
from vizier.show import render as R
from vizier.show import svg as S
from vizier.show.profile import profile_table
from vizier.show.rank import Option, rank_forms
from vizier.show.table import load_table, table_from_records

FIX = Path(__file__).parent / "fixtures" / "show"


def _csv(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text)
    return p


def _well_formed(svg: str) -> ET.Element:
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    return root


def _offline(text: str) -> None:
    """No fetches: the only URL allowed is the SVG namespace declaration."""
    urls = re.findall(r"https?://[^\s\"'<>)]+", text)
    assert all(u.startswith("http://www.w3.org/2000/svg") for u in urls), urls
    assert "<script" not in text.lower()


# ------------------------------------------------------------------ profiler

def test_profiler_reads_messy_csv():
    t = load_table(FIX / "messy.csv")
    p = profile_table(t)
    col = {c.name: c for c in p.columns}
    assert p.n_rows == 5  # trailing blank line ignored, BOM stripped from the header
    assert col["id"].role == "identifier"
    assert col["county_fips"].role == "geography" and col["county_fips"].geo == "fips-county"
    assert col["state"].geo == "us-state"
    assert col["lat"].geo == "lat" and col["lon"].geo == "lon"
    assert col["date"].role == "time" and col["date"].granularity == "day"
    assert col["month"].role == "time" and col["month"].granularity == "month"
    assert col["amount"].role == "measure" and col["amount"].unit == "USD"
    assert col["amount"].n_missing == 2  # "-" and "NA" are missing tokens, not zero
    assert col["amount"].max == pytest.approx(2500.5)
    assert col["share"].unit == "%" and col["share"].n_missing == 1


def test_profiler_respects_datapackage_and_state_columns():
    t = load_table(FIX / "suppressed" / "rates.csv")
    assert "rate__state" not in t.columns  # lifted out and attached to `rate`
    p = profile_table(t)
    rate = p.get("rate")
    assert rate.label == "Chronic absence rate" and rate.unit == "%"
    assert rate.description.startswith("Share of enrolled")
    # suppressed row held a 0 placeholder: it must become a gap, never a zero
    assert rate.min > 0
    assert rate.states == {"suppressed": 1, "not_collected": 1}
    assert rate.n_missing == 3  # suppressed, not collected, and the datapackage's -99
    assert p.get("year").role == "time" and p.get("year").granularity == "year"
    assert any("never as zero" in n for n in p.notes)


def test_profiler_flattens_nested_json(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"id": "a", "values": {"x": 1, "y": 2}}, {"id": "b", "values": {"x": 3, "y": None}}]))
    t = load_table(p)
    assert t.columns == ["id", "x", "y"]
    prof = profile_table(t)
    assert prof.get("y").n_missing == 1


# ------------------------------------------------------------------ ranking

def _rank(rows):
    t = table_from_records(rows)
    opts, _ = rank_forms(profile_table(t))
    return opts


def test_rank_one_number_offers_tile_and_sentence():
    opts = _rank([{"total": 1520}])
    assert opts[0].form == "stat-tile"
    assert "sentence" in [o.form for o in opts]


def test_rank_two_numbers_sentence_first_but_chart_offered_and_drawn(tmp_path):
    p = _csv(tmp_path, "two.csv", "group,value\nA,41\nB,57\n")
    r = show(p, out_dir=tmp_path / "out")
    forms = [o["form"] for o in r["options"]]
    assert forms[0] == "sentence"
    assert r["options"][0]["text"].startswith("Value is 41 for A and 57 for B")
    rendered = [o for o in r["options"] if o["rendered"]]
    assert any(o["is_chart"] for o in rendered), "a drawable chart must never be withheld"
    assert (tmp_path / "out" / "02-bar-chart.svg").exists()


def test_rank_time_series_line_first():
    rows = [{"year": y, "value": v} for y, v in zip(range(2010, 2020), range(10))]
    assert _rank(rows)[0].form == "line-chart"


def test_rank_many_categories_offers_folded_bars_strip_and_table():
    rows = [{"name": f"place {i:02d}", "value": i * 1.5} for i in range(60)]
    opts = _rank(rows)
    forms = {(o.form, o.variant) for o in opts}
    assert ("bar-chart", None) not in forms  # 60 bars won't fit; the top-N variant is offered
    assert ("bar-chart", "top") in forms or ("strip-plot", None) in forms
    assert ("table", None) in forms


def test_rank_two_measures_scatter_first():
    rows = [{"x": i, "y": i * 2 + (i % 3)} for i in range(30)]
    assert _rank(rows)[0].form == "scatterplot"


def test_rank_suppressed_table_is_drawn_with_gaps(tmp_path):
    r = show(FIX / "suppressed" / "rates.csv", out_dir=tmp_path)
    top = r["options"][0]
    assert top["form"] in ("line-chart", "slope-chart")
    checks = {n["check"] for n in top["notes"]}
    assert "suppressed-values" in checks
    svg = (tmp_path / top["files"]["svg"]).read_text()
    assert 'data-state="suppressed"' in svg and 'data-state="not collected"' in svg


def test_scatter_axes_follow_the_claim():
    rows = [{"asthma": 8 + (i % 5), "diesel": i / 10, "income": 40000 + i * 500} for i in range(30)]
    p = profile_table(table_from_records(rows))
    opts, _ = rank_forms(p, "How does asthma relate to diesel and income?")
    assert (opts[0].roles["x"], opts[0].roles["y"]) == ("diesel", "asthma")
    opts, _ = rank_forms(p, "Diesel, income and asthma")
    assert (opts[0].roles["x"], opts[0].roles["y"]) == ("diesel", "asthma")


def test_rank_claim_routes_family():
    rows = [{"visits": i, "wait_days": (i * 7) % 11, "staff": i % 4} for i in range(40)]
    opts, f = rank_forms(profile_table(table_from_records(rows)), "How are wait days distributed?")
    assert opts[0].form in ("histogram", "strip-plot")


def test_map_without_geometry_says_what_it_needs():
    rows = [{"state": s, "value": i} for i, s in enumerate(["Ohio", "Texas", "Maine", "Utah", "Iowa"])]
    opts, _ = rank_forms(profile_table(table_from_records(rows)), "where is it highest on a map")
    maps = [o for o in opts if o.form == "choropleth"]
    assert maps and not maps[0].drawable and "--geometry" in maps[0].needs
    assert opts[0].drawable


# ------------------------------------------------------------------ renderers

def _ctx(rows, form, roles, variant=None, **kw):
    t = table_from_records(rows)
    p = profile_table(t)
    o = Option(form=form, title=form, score=1, reason="", roles=roles, variant=variant)
    return R.Ctx(table=t, profile=p, option=o, words=S.Words(title=f"{form} test", source="test"), **kw)


SERIES = [{"year": y, "region": r, "value": (None if (r == "B" and y == 2013) else v + y % 3),
           "value__state": ("suppressed" if (r == "B" and y == 2013) else "")}
          for r, v in (("A", 10), ("B", 20), ("C", 15)) for y in range(2010, 2018)]
CATS = [{"name": n, "value": v, "other": (v * 0.8 if v is not None else 9), "value__state": "suppressed" if v is None else ""}
        for n, v in (("North", 30), ("South", 12), ("East", None), ("West", 21))]
XY = [{"label": f"p{i}", "x": i * 1.3, "y": (i * 7) % 13 + 2, "g": "abc"[i % 3]} for i in range(40)]
CROSS = [{"row": r, "col": c, "value": (None if (r, c) == ("r2", "c3") else i * 3 + j)}
         for i, r in enumerate(["r1", "r2", "r3"]) for j, c in enumerate(["c1", "c2", "c3", "c4"])]

RENDER_CASES = [
    ("bar-chart", CATS, {"x": "name", "y": "value"}, None, True),
    ("bar-chart", SERIES, {"x": "region", "y": "value", "series": "year"}, "grouped", True),
    ("bar-chart", SERIES[:8], {"x": "year", "y": "value"}, "time", False),
    ("stacked-bar", CROSS, {"x": "row", "y": "value", "series": "col"}, None, True),
    ("line-chart", SERIES, {"x": "year", "y": "value", "series": "region"}, None, True),
    ("stacked-area", [r for r in SERIES if r["value"] is not None], {"x": "year", "y": "value", "series": "region"}, None, False),
    ("scatterplot", XY, {"x": "x", "y": "y", "label": "label", "series": "g"}, None, False),
    ("dot-plot", CATS, {"x": "name", "y": ["value", "other"]}, "paired", True),
    ("strip-plot", XY, {"x": "y", "y": "g", "label": "label"}, None, False),
    ("histogram", XY, {"x": "y"}, None, False),
    ("slope-chart", [r for r in SERIES if r["year"] in (2010, 2017)], {"x": "year", "y": "value", "series": "region"}, None, False),
    ("small-multiples", SERIES, {"x": "year", "y": "value", "facet": "region"}, "line", True),
    ("small-multiples", CROSS, {"x": "col", "y": "value", "facet": "row"}, "bar", True),
    ("heatmap", CROSS, {"x": "col", "y": "row", "value": "value"}, None, True),
    ("stat-tile", [{"total": 1520}], {"value": "total"}, None, False),
]


@pytest.mark.parametrize("form,rows,roles,variant,has_gap", RENDER_CASES,
                         ids=[f"{c[0]}-{c[3] or 'base'}" for c in RENDER_CASES])
def test_every_renderer_draws_well_formed_offline_svg(form, rows, roles, variant, has_gap):
    ctx = _ctx(rows, form, roles, variant)
    svg = R.render_svg(ctx)
    root = _well_formed(svg)
    _offline(svg)
    assert root.get("data-form") == form
    assert 'class="vz-mark"' in svg, "no data marks drawn"
    if has_gap:
        assert 'class="vz-missing"' in svg, "a missing/suppressed value must be marked, not zeroed"


def test_bar_does_not_draw_suppressed_as_zero():
    svg = R.render_svg(_ctx(CATS, "bar-chart", {"x": "name", "y": "value"}))
    assert "East: suppressed" in svg
    assert "East: 0" not in svg


def test_line_breaks_at_gap():
    rows = [{"year": y, "v": (None if y == 2013 else y - 2000)} for y in range(2010, 2017)]
    svg = R.render_svg(_ctx(rows, "line-chart", {"x": "year", "y": "v"}))
    marks = re.findall(r'<path d="(M[^"]+)"[^>]*class="vz-mark"', svg)
    assert len(marks) == 2, "the line should be two segments either side of the gap"


def test_choropleth_from_geojson_and_from_svg_paths():
    gj = json.loads((FIX / "areas.geojson").read_text())
    rows = [{"code": "A", "v": 1.0}, {"code": "B", "v": None, "v__state": "suppressed"}, {"code": "C", "v": 3.0}]
    ctx = _ctx(rows, "choropleth", {"value": "v", "geometry": "__geojson__", "key": "code", "label": "code"},
               geojson=gj, geo_key="code")
    svg = R.render_svg(ctx)
    _well_formed(svg)
    assert svg.count('class="vz-mark"') == 2 and 'data-state="suppressed"' in svg
    rows2 = [{"name": "a", "v": 1, "path": "M0,0 10,0 10,10 0,10Z"}, {"name": "b", "v": 2, "path": "M10,0 20,0 20,10 10,10Z"}]
    svg2 = R.render_svg(_ctx(rows2, "choropleth", {"value": "v", "geometry": "path", "label": "name"}))
    _well_formed(svg2)
    assert svg2.count('class="vz-mark"') == 2


def test_show_with_geojson_draws_the_map(tmp_path):
    p = _csv(tmp_path, "m.csv", "code,v\nA,1\nB,2\nC,3\n")
    r = show(p, claim="where is v highest on the map", geometry=FIX / "areas.geojson", geo_key="code",
             out_dir=tmp_path / "o", top=6)
    m = next(o for o in r["options"] if o["form"] == "choropleth")
    assert m["drawable"] and m["rendered"]


# ------------------------------------------------------------------ palette fallback, notes, words

def test_too_many_series_falls_back_instead_of_erroring():
    rows = [{"year": y, "s": f"s{k:02d}", "v": k + y % 5} for k in range(12) for y in range(2000, 2010)]
    ctx = _ctx(rows, "line-chart", {"x": "year", "y": "v", "series": "s"})
    svg = R.render_svg(ctx)
    _well_formed(svg)
    assert any(a["check"] == "too-many-series" for a in ctx.applied)
    assert S.OTHER in ctx.colors.values()
    assert ctx.palette_advice and any("Other" in a for a in ctx.palette_advice)


def test_honesty_notes_attach_and_apply(tmp_path):
    rows = "year,v\n" + "\n".join(f"{y},{100 + y % 7}" for y in range(2000, 2012))
    r = show(_csv(tmp_path, "t.csv", rows), out_dir=tmp_path / "o")
    line = r["options"][0]
    axis = next(n for n in line["notes"] if n["check"] == "axis-not-zero")
    assert axis["applied"] and axis["misread"] and axis["fix"]


def test_small_sample_and_rate_without_denominator(tmp_path):
    rows = "name,poverty_rate,income\n" + "\n".join(f"n{i},{10 + i}%,{40000 + i * 900}" for i in range(9))
    r = show(_csv(tmp_path, "s.csv", rows), claim="poverty rate and income", out_dir=tmp_path / "o")
    sc = next(o for o in r["options"] if o["form"] == "scatterplot")
    checks = {n["check"] for n in sc["notes"]}
    assert "small-sample" in checks and "rate-without-denominator" in checks
    assert "n = 9" in sc["words"]["subtitle"]


def test_dual_axis_is_never_drawn(tmp_path):
    rows = "year,price,volume\n" + "\n".join(f"{y},{y - 1990}.5,{(y * 37) % 900}" for y in range(2000, 2012))
    p = _csv(tmp_path, "d.csv", rows)
    pkg = {"resources": [{"path": "d.csv", "schema": {"fields": [
        {"name": "year", "type": "year"}, {"name": "price", "type": "number", "unit": "USD"},
        {"name": "volume", "type": "number", "unit": "tonnes"}]}}]}
    (tmp_path / "datapackage.json").write_text(json.dumps(pkg))
    r = show(p, overrides={"y": "price,volume"}, out_dir=tmp_path / "o")
    lines = [o for o in r["options"] if o["form"] == "line-chart"]
    assert len(lines) == 2 and {lines[0]["roles"]["y"], lines[1]["roles"]["y"]} == {"price", "volume"}
    assert any(n["check"] == "dual-axis" and n["applied"] for n in lines[0]["notes"])


def test_words_on_figure_title_units_source_caveats(tmp_path):
    cav = tmp_path / "cav.json"
    cav.write_text(json.dumps([{"effect": "Rates are modeled estimates",
                                "misuse": "ranking individual districts",
                                "instead": "compare groups of districts"}]))
    r = show(FIX / "suppressed" / "rates.csv", claim="Absence fell in Cedar", caveats=cav, out_dir=tmp_path / "o")
    top = r["options"][0]
    svg = (tmp_path / "o" / top["files"]["svg"]).read_text()
    assert "Absence fell in Cedar" in svg                       # title states the finding
    assert "Chronic absence rate (%)" in svg                     # axis label + unit from the datapackage
    assert "Example State Department of Education" in svg        # source line from the datapackage
    assert "Rates are modeled estimates" in svg and "ranking individual districts" in svg


def test_question_becomes_subtitle_not_title(tmp_path):
    r = show(FIX / "suppressed" / "rates.csv", claim="How did absence change by district?", out_dir=tmp_path / "o")
    w = r["options"][0]["words"]
    assert w["title"] != "How did absence change by district?"
    assert w["subtitle"].startswith("How did absence change")


def test_annotation_slot_is_filled(tmp_path):
    p = _csv(tmp_path, "b.csv", "name,v\nA,3\nB,9\nC,5\n")
    r = show(p, annotations={"B": "Doubled after the 2019 rule"}, out_dir=tmp_path / "o", top=2)
    bar = next(o for o in r["options"] if o["form"] == "bar-chart")
    assert "Doubled after the 2019 rule" in (tmp_path / "o" / bar["files"]["svg"]).read_text()


def test_html_page_is_self_contained_and_checks_run(tmp_path):
    r = show(FIX / "suppressed" / "rates.csv", out_dir=tmp_path / "o")
    html = (tmp_path / "o" / "index.html").read_text()
    _offline(html)
    assert "<svg" in html and "Honesty notes" in html and "The full ranking" in html
    for o in r["options"]:
        if o.get("checks"):
            assert o["checks"]["well_formed"] is True
            assert o["checks"]["structure"] == []  # no text in series colors
    spec = json.loads((tmp_path / "o" / "spec.json").read_text())
    assert spec["schema"] == "vizier/show-spec/v1"


def test_cli_show_and_spec(tmp_path):
    from click.testing import CliRunner

    from vizier.cli import main
    p = _csv(tmp_path, "c.csv", "year,v\n2020,1\n2021,3\n2022,2\n2023,5\n")
    res = CliRunner().invoke(main, ["show", str(p), "--out", str(tmp_path / "o")])
    assert res.exit_code == 0, res.output
    assert "Line chart" in res.output and "index.html" in res.output
    res = CliRunner().invoke(main, ["show", str(p), "--format", "spec"])
    assert res.exit_code == 0, res.output
    spec = json.loads(res.output)
    assert spec["schema"] == "vizier/show-spec/v1"
    assert spec["chosen"]["form"] == "line-chart"
    assert spec["chosen"]["roles"]["x"] == "year"
    assert set(spec["chosen"]) >= {"words", "colors", "notes", "datawrapper"}
