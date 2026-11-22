"""The gate: a parse failure is a failure; every drop says what to show instead."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from vizier import gate as Gt


@dataclass
class _Result:
    text: str
    provider: str = "fake"
    model: str = "fake-1"
    cost_usd: float = 0.0
    call_id: str = "c1"


class FakeLLM:
    def __init__(self, text: str):
        self.text = text
        self.prompts: list[tuple[str, str]] = []

    def generate(self, *, prompt, system, **kw):
        self.prompts.append((system, prompt))
        return _Result(self.text)


def _bundle(tmp_path: Path, candidates: list[dict]) -> Path:
    (tmp_path / "draft").mkdir(parents=True)
    (tmp_path / "metadata").mkdir()
    (tmp_path / "metadata" / "artifact.json").write_text(json.dumps({"name": "test piece"}))
    (tmp_path / "draft" / "current.md").write_text("Costs rose from $4 to $9 between 2019 and 2024.")
    (tmp_path / "draft" / "annotations.json").write_text(json.dumps({"chart_candidates": candidates}))
    return tmp_path


CANDS = [{"title": "Cost over time"}, {"title": "Ecosystem diagram"}]


def test_parse_failure_is_reported_as_failure(tmp_path):
    d = Gt.needs_charts(_bundle(tmp_path, CANDS), llm=FakeLLM("Sure! Here are my thoughts: keep the first."))
    assert d.status == "error" and not d.ok
    assert d.needs_charts is None, "an unreadable reply must not read as 'no charts'"
    assert "parse" in d.error
    assert d.raw_response.startswith("Sure!")
    assert d.to_dict()["ok"] is False


def test_drop_without_alternative_gets_one_and_keep_gets_improvements(tmp_path):
    reply = {
        "needs_charts": True,
        "summary": "One chart, one sentence.",
        "verdicts": [
            {"candidate_index": 1, "keep": True, "confidence": 0.9, "reason": "trend",
             "chart_spec": {"kind": "line"}, "improve": ["Label the 2024 endpoint"]},
            {"candidate_index": 2, "keep": False, "confidence": 0.8, "reason": "no numbers"},
        ],
    }
    d = Gt.needs_charts(_bundle(tmp_path, CANDS), llm=FakeLLM("```json\n" + json.dumps(reply) + "\n```"))
    assert d.ok and d.status == "ok" and d.needs_charts is True and d.n_kept == 1
    keep, drop = d.verdicts
    assert keep.improve == ["Label the 2024 endpoint"] and keep.instead is None
    assert drop.instead and drop.instead["form"] in Gt.SHOW_FORMS and drop.instead_source == "default"


def test_model_supplied_instead_is_kept(tmp_path):
    reply = {"needs_charts": False, "summary": "s", "verdicts": [
        {"candidate_index": 1, "keep": False, "confidence": 0.7, "reason": "two numbers",
         "instead": {"form": "sentence", "why": "two numbers", "how": "Costs rose from $4 to $9."}}]}
    d = Gt.needs_charts(_bundle(tmp_path, CANDS[:1]), llm=FakeLLM(json.dumps(reply)))
    assert d.verdicts[0].instead["form"] == "sentence" and d.verdicts[0].instead_source == "model"


def test_no_candidates_has_its_own_status(tmp_path):
    d = Gt.needs_charts(_bundle(tmp_path, []), llm=FakeLLM("{}"))
    assert d.status == "no_candidates" and d.needs_charts is False and d.ok


def test_prompt_asks_for_alternatives_and_drops_the_sneer(tmp_path):
    llm = FakeLLM(json.dumps({"needs_charts": False, "verdicts": []}))
    Gt.needs_charts(_bundle(tmp_path, CANDS), llm=llm)
    system, prompt = llm.prompts[0]
    assert "Be strict" not in system and "prose alone is often enough" not in system
    assert "instead" in prompt and "improve" in prompt
    assert "sentence" in prompt and "table" in prompt


def test_cli_exits_nonzero_on_failure(tmp_path, monkeypatch):
    from vizier import __main__gate as M
    b = _bundle(tmp_path, CANDS)
    monkeypatch.setattr(M, "needs_charts", lambda bd: Gt.needs_charts(bd, llm=FakeLLM("not json")))
    assert M.main([str(b)]) == 1
    written = json.loads((b / "draft" / "vizier-decision.json").read_text())
    assert written["status"] == "error" and written["needs_charts"] is None
