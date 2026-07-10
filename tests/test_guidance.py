"""Implementation guidance. Runnable: uv run python tests/test_guidance.py"""

from __future__ import annotations

from vizier.analyze import guidance as G


def test_budget_guide_includes_forms_and_domain_checks():
    guide = G.implementation_guide(
        "district profile budget module combining per-pupil cost trend over years "
        "and operating revenue source mix",
        n_series=5,
        k_forms=5,
        k_prior=0,
    )
    ids = [f["id"] for f in guide["forms"]]
    check_ids = [c["id"] for c in guide["checks"]]
    assert "line-chart" in ids[:4], ids
    assert "stacked-bar" in ids[:4], ids
    assert "money-basis" in check_ids
    assert "fund-scope" in check_ids
    assert "published-metric" in check_ids
    assert "part-to-whole-total" in check_ids


def test_format_guide_mentions_reader_and_prior_art_section_when_present():
    guide = G.implementation_guide(
        "one total split into four non-hierarchical categories",
        n_series=4,
        k_forms=3,
        k_prior=1,
    )
    text = G.format_guide(guide)
    assert "Reader decision" in text
    assert "Stacked bar chart" in text
    if guide["prior_art"]:
        assert "Prior-art signals:" in text


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
