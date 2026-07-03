"""Parity tests for vizier.analyze.color against the dataviz validate_palette.js.

Expected numbers are the exact outputs the JS validator produced during the
njschooldata palette work (2026-07-02). If these pass, the Python port and the
skill's JS agree on every verdict. Runnable without pytest:

    uv run python tests/test_color.py
"""

from __future__ import annotations

from vizier.analyze import color as C

SURF = "#fafaf7"  # njschooldata light surface
OLD = ["#b4530a", "#6b4ea8", "#2f7d6b", "#2563a8", "#b5497f", "#8a8a8f", "#9a8478"]
NEW7 = ["#e69f00", "#0072b2", "#009e73", "#56b4e9", "#d55e00", "#8a8f2e", "#cc79a7"]
STACK6 = ["#e69f00", "#0072b2", "#009e73", "#56b4e9", "#cc79a7", "#8a8f2e"]
RAMP_OLD = ["#cdddf0", "#9eb0c8", "#6e84a1", "#3f577a", "#102a52"]
RAMP_NEW = ["#8bacd0", "#6c8cb1", "#4e6b91", "#2f4a72", "#102a52"]  # ramp(#8bacd0→#102a52) 5-step


def _close(a: float, b: float, tol: float = 0.1) -> bool:
    return abs(a - b) <= tol


def _check(r: C.Report, name: str) -> C.Check:
    return next(c for c in r.checks if c.name == name)


def test_contrast_matches_js():
    assert _close(C.contrast("#b4530a", SURF), 4.80, 0.02)
    assert _close(C.contrast("#8a8a8f", SURF), 3.29, 0.02)
    assert _close(C.contrast("#6b4ea8", SURF), 6.12, 0.02)
    assert _close(C.contrast("#067a4e", SURF), 5.15, 0.02)  # the pos/neg color fix


def test_old_palette_fails_cvd_and_chroma():
    r = C.validate_categorical(OLD, mode="light", surface=SURF, pairs="all")
    assert not r.ok
    # the blue/violet collapse under deuteranopia
    assert r.worst_cvd["kind"] == "deutan"
    assert _close(r.worst_cvd["delta"], 1.5, 0.2)
    assert {r.worst_cvd["a"], r.worst_cvd["b"]} == {"#2563a8", "#6b4ea8"}
    # three near-gray hues below the chroma floor
    chroma = _check(r, "Chroma floor")
    assert chroma.state == "fail"
    for hexv in ("#2f7d6b", "#8a8a8f", "#9a8478"):
        assert hexv in chroma.detail


def test_new_palette_passes():
    # all-pairs (dot-plot case): floor-band 9.3 (Native olive ↔ Pacific vermillion)
    r = C.validate_categorical(NEW7, mode="light", surface=SURF, pairs="all")
    assert r.ok, C.format_report(r)
    assert _check(r, "Chroma floor").state == "pass"
    assert _check(r, "Lightness band").state == "pass"
    cvd = _check(r, "CVD separation")
    assert cvd.state == "floor"
    assert _close(r.worst_cvd["delta"], 9.3, 0.2)
    assert {r.worst_cvd["a"], r.worst_cvd["b"]} == {"#8a8f2e", "#d55e00"}


def test_new_stack_adjacency_strong():
    # the composition stack: adjacent-only, comfortably above the target
    r = C.validate_categorical(STACK6, mode="light", surface=SURF, pairs="adjacent")
    assert r.ok
    assert _check(r, "CVD separation").state == "pass"
    assert r.worst_cvd["delta"] >= 12.0


def test_ordinal_ramp_light_end():
    old = C.validate_ordinal(RAMP_OLD, mode="light", surface=SURF)
    le = _check(old, "Light-end contrast")
    assert le.state == "fail"
    assert "1.3" in le.detail  # #cdddf0 ≈ 1.32:1
    assert not old.ok

    new = C.validate_ordinal(RAMP_NEW, mode="light", surface=SURF)
    assert new.ok, C.format_report(new)
    assert _check(new, "Light-end contrast").state == "pass"
    assert _check(new, "Lightness monotone").state == "pass"
    assert _check(new, "Single hue").state == "pass"


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
