"""`vizier explore`: the field sheet, ranked relationships and breakdowns, and
exploration's own honesty — all offline, no model.

The synthetic table plants one real relationship (a→b), one confounded pair
(p, q both driven by z), one association made by four extreme rows (u, v), one
group difference (m by g), and a field too sparse to rank (w).
"""

from __future__ import annotations

import json
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from vizier.show.explore import SCHEMA, explore, partial, spearman

FIX = Path(__file__).parent / "fixtures" / "show"


def _synthetic(tmp_path: Path) -> Path:
    rng = random.Random(7)
    rows = []
    for i in range(200):
        a = rng.gauss(0, 1)
        z = rng.gauss(0, 1)
        g = "ABC"[i % 3]
        rows.append({
            "name": f"site {i:03d}",
            "a": round(a, 4),
            "b": round(2 * a + rng.gauss(0, 0.3), 4),
            "z": round(z, 4),
            "p": round(z + rng.gauss(0, 0.6), 4),
            "q": round(z + rng.gauss(0, 0.6), 4),
            # u, v: independent noise on 30 rows, plus 4 rows extreme in both
            "u": round(rng.gauss(0, 1), 4) if i < 30 else "",
            "v": round(rng.gauss(0, 1), 4) if i < 30 else "",
            "w": round(rng.gauss(0, 1), 4) if i < 6 else "",
            "g": g,
            "h": "XY"[rng.randrange(2)],
            "m": round({"A": 0, "B": 3, "C": 6}[g] + rng.gauss(0, 1), 4),
            "people": rng.randrange(10, 900),
        })
    for k, i in enumerate(range(30, 34)):
        rows[i]["u"] = 8 + k
        rows[i]["v"] = 9 + k
    rows[50]["people"] = -4          # impossible for a count
    rows[198]["g"] = "D"             # a group too small to rank
    rows[199]["g"] = "D"
    cols = list(rows[0])
    p = tmp_path / "synthetic.csv"
    p.write_text(",".join(cols) + "\n" + "\n".join(",".join(str(r[c]) for c in cols) for r in rows) + "\n")
    return p


def _views(r, kind=None):
    return [v for v in r["views"] + r.get("undrawn", []) if kind is None or v["kind"] == kind]


def _offline_svg(text: str) -> None:
    ET.fromstring(text)
    urls = re.findall(r"https?://[^\s\"'<>)]+", text)
    assert all(u.startswith("http://www.w3.org/2000/svg") for u in urls), urls
    assert "<script" not in text.lower()


# ------------------------------------------------------------------ statistics

def test_spearman_and_partial_basics():
    xs = list(range(20))
    assert spearman(xs, [x * x for x in xs]) == pytest.approx(1.0)
    assert spearman(xs, [-x for x in xs]) == pytest.approx(-1.0)
    assert partial(0.5, 0.7, 0.7) == pytest.approx((0.5 - 0.49) / 0.51)


# ------------------------------------------------------------------ field sheet

def test_field_sheet_on_messy_fixture(tmp_path):
    r = explore(FIX / "messy.csv", out_dir=tmp_path)
    f = {x["name"]: x for x in r["fields"]}
    assert f["amount"]["role"] == "measure" and f["amount"]["unit"] == "USD"
    assert f["amount"]["missing"] == 2 and f["amount"]["summary"]["max"] == pytest.approx(2500.5)
    assert set(f["amount"]["summary"]) == {"min", "max", "median", "q1", "q3", "mean"}
    assert f["id"]["role"] == "id"
    assert f["county_fips"]["role"] == "geography"
    assert f["date"]["role"] == "time"
    assert f["state"]["top"][0] == {"value": "Alabama", "n": 2}
    assert all(isinstance(x["oddities"], list) for x in r["fields"])
    assert any(v["id"] == "dist-amount" for v in r["views"])


def test_field_sheet_with_datapackage_states(tmp_path):
    r = explore(FIX / "suppressed" / "rates.csv", out_dir=tmp_path)
    rate = next(x for x in r["fields"] if x["name"] == "rate")
    assert rate["unit"] == "%" and rate["description"].startswith("Share of enrolled")
    assert rate["states"] == {"suppressed": 1, "not_collected": 1}
    assert rate["missing"] == 3
    assert r["source"]["datapackage"] is True
    trend = [v for v in r["views"] if v["kind"] == "trend"]
    assert trend and trend[0]["show_args"] == {"x": "year", "y": "rate", "series": "district"}


def test_oddities_flag_impossible_values(tmp_path):
    r = explore(_synthetic(tmp_path), out_dir=tmp_path / "o")
    people = next(x for x in r["fields"] if x["name"] == "people")
    assert any("negative" in o for o in people["oddities"])


# ------------------------------------------------------------------ ranking

def test_relationships_ranked_with_leverage_and_conditioning(tmp_path):
    src = _synthetic(tmp_path)
    r = explore(src, out_dir=tmp_path / "o", max_views=60)
    rels = {tuple(v["fields"]): v for v in _views(r, "relationship")}
    top = min((v for v in rels.values() if v.get("rank")), key=lambda v: v["rank"])
    assert set(top["fields"]) == {"a", "b"}, "the planted relationship ranks first"
    assert top["stat"]["name"] == "spearman_rho" and top["stat"]["n"] == 200
    uv = rels[("u", "v")]
    assert uv["caution"].startswith("Driven by a handful of rows")
    assert abs(uv["stat"]["without_top_rows"]["value"]) < abs(uv["stat"]["value"]) / 2
    # the confounded pair, with p at the centre so it is among the conditioned views
    rf = explore(src, out_dir=tmp_path / "f", focus="p", max_views=60)
    cond = next(v for v in _views(rf, "conditioned") if set(v["fields"][:2]) == {"p", "q"})
    assert cond["fields"][2] == "z"
    assert cond["caution"].startswith("Mostly explained by")
    assert abs(cond["stat"]["value"]) < 0.5 * abs(cond["stat"]["overall"])
    assert len(cond["stat"]["panels"]) == 3


def test_breakdowns_ranked_and_small_groups_withheld(tmp_path):
    r = explore(_synthetic(tmp_path), out_dir=tmp_path / "o", max_views=60)
    brks = [v for v in _views(r, "breakdown") if v.get("rank")]
    best = min(brks, key=lambda v: v["rank"])
    assert best["fields"] == ["m", "g"]
    assert best["stat"]["groups"] == 4 and best["stat"]["groups_ranked"] == 3
    assert "fewer than 5 rows" in best["caution"]
    svg = (tmp_path / "o" / best["file"]).read_text()
    assert "not ranked" in svg  # the small group is labelled with n, and unranked


def test_small_n_pairs_are_withheld_not_hidden(tmp_path):
    r = explore(_synthetic(tmp_path), out_dir=tmp_path / "o", max_views=60)
    w = [v for v in _views(r, "relationship") if "w" in v["fields"]]
    assert w and all(v.get("withheld") and "rank" not in v for v in w)
    assert all(v["stat"]["n"] < 10 for v in w)
    # still drawable on request
    one = explore(_synthetic(tmp_path), out_dir=tmp_path / "v", view=w[0]["id"])
    assert (tmp_path / "v" / one["views"][0]["file"]).exists()


def test_comparisons_counted_and_notes_honest(tmp_path):
    r = explore(_synthetic(tmp_path), out_dir=tmp_path / "o")
    m = 10  # a b z p q u v w m people
    assert r["comparisons_examined"]["pairs"] == m * (m - 1) // 2
    assert r["comparisons_examined"]["breakdowns"] == m * 2  # by g and by h
    joined = " ".join(r["notes"])
    assert f"{m * (m - 1) // 2} pair(s) of measures looked at" in joined
    assert "lead to test, not a finding" in joined
    assert "not cause" in joined
    assert "cause" not in " ".join(v["what"] for v in r["views"]).replace("because", "")
    assert len(r["views"]) <= 24


def test_outliers_view_names_rows(tmp_path):
    r = explore(_synthetic(tmp_path), out_dir=tmp_path / "o", max_views=60)
    out = next(v for v in r["views"] if v["kind"] == "outliers")
    assert out["form"] == "table" and out["file"].endswith(".csv")
    assert "site " in (tmp_path / "o" / out["file"]).read_text()


# ------------------------------------------------------------------ subsets

def test_focus_by_where(tmp_path):
    src = _synthetic(tmp_path)
    f = explore(src, out_dir=tmp_path / "f", focus="m")
    assert f["subset"] == {"focus": "m", "where": []}
    assert f["views"][0]["id"] == "dist-m"
    assert all("m" in v["fields"] for v in f["views"] if v["kind"] in ("relationship", "breakdown"))
    w = explore(src, out_dir=tmp_path / "w", where=["g=A"])
    assert w["source"]["rows"] == 66 and w["subset"]["where"] == ["g=A"]
    b = explore(src, out_dir=tmp_path / "b", by="h", max_views=20)
    assert b["subset"]["by"] == "h"
    assert {v["id"].split("-")[1] for v in b["views"]} == {"x", "y"}
    with pytest.raises(ValueError):
        explore(src, where=["nope=1"])


# ------------------------------------------------------------------ output

def test_json_shape_and_files(tmp_path):
    explore(_synthetic(tmp_path), out_dir=tmp_path / "o")
    on_disk = json.loads((tmp_path / "o" / "explore.json").read_text())
    assert on_disk["schema"] == SCHEMA == "vizier/explore/v1"
    assert set(on_disk) >= {"schema", "vizier_version", "source", "subset", "fields", "views",
                            "comparisons_examined", "notes"}
    assert set(on_disk["source"]) == {"path", "name", "rows", "datapackage"}
    for f in on_disk["fields"]:
        assert {"name", "role", "type", "n", "missing", "distinct", "oddities"} <= set(f)
        assert f["role"] in {"measure", "dimension", "time", "geography", "label", "id"}
    kinds = {"distribution", "missingness", "relationship", "conditioned", "breakdown", "trend", "outliers"}
    for v in on_disk["views"]:
        assert {"id", "kind", "title", "what", "fields", "form", "file", "n", "show_args"} <= set(v)
        assert v["kind"] in kinds
        if v.get("stat"):
            assert {"name", "value", "n"} <= set(v["stat"])
    ids = [v["id"] for v in on_disk["views"]]
    assert len(ids) == len(set(ids))
    html = (tmp_path / "o" / "index.html").read_text()
    for v in on_disk["views"]:
        assert f"id='{v['id']}'" in html
    assert "<script" not in html.lower()


def test_every_svg_well_formed_and_offline(tmp_path):
    explore(_synthetic(tmp_path), out_dir=tmp_path / "o", max_views=60)
    explore(FIX / "suppressed" / "rates.csv", out_dir=tmp_path / "s")
    explore(FIX / "messy.csv", out_dir=tmp_path / "m")
    svgs = list((tmp_path).rglob("*.svg"))
    assert len(svgs) > 20
    for p in svgs:
        _offline_svg(p.read_text())


def test_view_redraws_one_at_larger_size(tmp_path):
    src = _synthetic(tmp_path)
    r = explore(src, out_dir=tmp_path / "o")
    vid = next(v["id"] for v in r["views"] if v["kind"] == "relationship")
    one = explore(src, out_dir=tmp_path / "big", view=vid)
    svg = (tmp_path / "big" / f"{vid}.svg").read_text()
    assert 'width="680"' in svg and f'data-view="{vid}"' in svg
    assert one["views"][0]["id"] == vid


def test_cli_explore(tmp_path):
    from click.testing import CliRunner

    from vizier.cli import main
    src = _synthetic(tmp_path)
    res = CliRunner().invoke(main, ["explore", str(src), "--out", str(tmp_path / "o"), "--max-views", "12"])
    assert res.exit_code == 0, res.output
    assert "pair(s) of measures looked at" in res.output
    res = CliRunner().invoke(main, ["explore", str(src), "--out", str(tmp_path / "o2"), "--json"])
    assert json.loads(res.output)["schema"] == "vizier/explore/v1"
