"""Datawrapper output, against a fake server. Nothing here touches the live API."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from vizier.show import show
from vizier.show import datawrapper as DW
from vizier.show.rank import Option

FIX = Path(__file__).parent / "fixtures" / "show"


class FakeDatawrapper:
    """Records requests and answers like the v3 API's create / data / publish."""

    def __init__(self):
        self.calls: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        path = request.url.path
        if request.method == "POST" and path == "/v3/charts":
            body = json.loads(request.content)
            return httpx.Response(201, json={"id": "aB3dE", "publicId": "aB3dE", "type": body["type"],
                                             "title": body["title"]})
        if request.method == "PUT" and path == "/v3/charts/aB3dE/data":
            return httpx.Response(204)
        if request.method == "POST" and path == "/v3/charts/aB3dE/publish":
            return httpx.Response(200, json={"data": {}, "version": 1, "url": "https://datawrapper.dwcdn.net/aB3dE/1/"})
        return httpx.Response(404, json={"message": "not found"})


def _client(fake):
    return DW.DatawrapperClient(token="test-token", http=httpx.Client(transport=httpx.MockTransport(fake)))


def test_type_mapping():
    def t(form, variant=None):
        return DW.dw_type(Option(form=form, title=form, score=0, reason="", variant=variant))[0]
    assert t("bar-chart") == "d3-bars"
    assert t("bar-chart", "grouped") == "d3-bars-grouped"
    assert t("bar-chart", "time") == "column-chart"
    assert t("stacked-bar") == "d3-bars-stacked"
    assert t("line-chart") == "d3-lines"
    assert t("scatterplot") == "d3-scatter-plot"
    assert t("dot-plot", "paired") == "d3-dot-plot"
    assert t("slope-chart") == "d3-arrow-plot"
    assert t("small-multiples", "line") == "multiple-lines"
    assert t("heatmap") == "tables"
    assert t("table") == "tables"
    for none in ("strip-plot", "choropleth", "sentence", "stat-tile"):
        typ, why = DW.dw_type(Option(form=none, title=none, score=0, reason=""))
        assert typ is None and why


def test_no_token_is_a_dry_run_with_exact_payloads(tmp_path, monkeypatch):
    monkeypatch.delenv("DATAWRAPPER_API_TOKEN", raising=False)
    r = show(FIX / "suppressed" / "rates.csv", claim="Absence fell in Cedar", datawrapper=True, out_dir=tmp_path)
    dw = r["datawrapper"]
    assert dw["sent"] is False and dw["dry_run"] is True and "DATAWRAPPER_API_TOKEN" in dw["message"]
    create, data = dw["requests"][:2]
    assert create["method"] == "POST" and create["path"] == "/charts"
    assert create["body"]["type"] == dw["type"] == "d3-lines"
    assert create["body"]["title"] == "Absence fell in Cedar"
    assert create["body"]["metadata"]["describe"]["source-name"] == "Example State Department of Education"
    assert data["method"] == "PUT" and data["content_type"] == "text/csv"
    lines = data["body"].strip().splitlines()
    assert lines[0] == "School year,Alder,Birch,Cedar"
    # suppressed / not collected values travel as empty cells, never 0
    assert lines[3] == "2023,,10.4,19.5"
    assert lines[2] == "2022,15.1,,"
    assert all("publish" not in q["path"] for q in dw["requests"])
    assert "token" not in json.dumps(dw).lower().replace("datawrapper_api_token", "")


def test_fake_server_create_upload_draft(tmp_path):
    fake = FakeDatawrapper()
    p = tmp_path / "b.csv"
    p.write_text("name,v\nA,3\nB,9\nC,5\n")
    r = show(p, datawrapper=True, dw_client=_client(fake))
    dw = r["datawrapper"]
    assert dw["sent"] and dw["id"] == "aB3dE" and dw["published"] is False
    assert dw["edit_url"] == "https://app.datawrapper.de/chart/aB3dE/visualize"
    assert [(c.method, c.url.path) for c in fake.calls] == [("POST", "/v3/charts"), ("PUT", "/v3/charts/aB3dE/data")]
    assert fake.calls[0].headers["authorization"] == "Bearer test-token"
    assert fake.calls[1].headers["content-type"] == "text/csv"
    assert fake.calls[1].content.decode().splitlines() == ["name,v", "B,9", "C,5", "A,3"]
    assert "@" not in fake.calls[0].headers["user-agent"]


def test_fake_server_publish(tmp_path):
    fake = FakeDatawrapper()
    p = tmp_path / "b.csv"
    p.write_text("name,v\nA,3\nB,9\nC,5\n")
    r = show(p, datawrapper=True, publish=True, dw_client=_client(fake))
    assert [c.url.path for c in fake.calls][-1] == "/v3/charts/aB3dE/publish"
    assert r["datawrapper"]["public_url"] == "https://datawrapper.dwcdn.net/aB3dE/1/"


def test_sentence_first_falls_through_to_a_chart_type(tmp_path, monkeypatch):
    monkeypatch.delenv("DATAWRAPPER_API_TOKEN", raising=False)
    p = tmp_path / "two.csv"
    p.write_text("group,value\nA,41\nB,57\n")
    dw = show(p, datawrapper=True)["datawrapper"]
    assert dw["form"] == "bar-chart" and dw["type"] == "d3-bars"
    assert dw["skipped"][0]["form"] == "sentence"


def test_server_error_is_raised_not_swallowed():
    def broken(request):
        return httpx.Response(401, json={"message": "unauthorized"})
    cl = DW.DatawrapperClient(token="x", http=httpx.Client(transport=httpx.MockTransport(broken)))
    with pytest.raises(RuntimeError, match="HTTP 401"):
        cl.run({"requests": [{"method": "POST", "path": "/charts", "content_type": "application/json", "body": {}}]})
