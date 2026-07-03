"""Form recommendation + structural lint. Runnable: uv run python tests/test_forms_structure.py

test_recommend_* touch the SQLite corpus index (they need `vizier db build`).
"""

from __future__ import annotations

from vizier.analyze import forms as F, structure as St


def _raises(fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
        return False
    except ValueError:
        return True


def test_recommend_form_routes_to_expected():
    ids = [f["id"] for f in F.recommend_form("composition of a total over time", n_series=5)["forms"]]
    assert "stacked-area" in ids or "stacked-bar" in ids, ids


def test_recommend_form_guards():
    assert any("stat tile" in n for n in F.recommend_form("one KPI", n_series=1)["notes"])
    assert any("table" in n for n in F.recommend_form("many categories", n_series=9)["notes"])


def test_recommend_form_family_route():
    ids = [f["id"] for f in F.recommend_form(family="Flow", k=4)["forms"]]
    assert ids, "family route returned nothing"


def test_recommend_form_needs_input():
    assert _raises(F.recommend_form)


def test_lint_flags_text_in_series_color():
    svg = '<svg><rect fill="#0072b2"/><text fill="#0072b2">B -39</text></svg>'
    findings = St.lint_svg(svg)["findings"]
    assert findings and findings[0]["check"] == "text-wears-series-color"


def test_lint_passes_ink_text():
    svg = '<svg><rect fill="#0072b2"/><text fill="#111827">label</text></svg>'
    assert St.lint_svg(svg)["findings"] == []


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    import traceback
    passed = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
    print(f"\n{passed}/{len(TESTS)} passed")
    raise SystemExit(0 if passed == len(TESTS) else 1)
