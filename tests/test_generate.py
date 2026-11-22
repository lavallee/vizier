"""Generation guarantees: what vizier *suggests* must *pass* its own checks.

Runnable without pytest:  uv run python tests/test_generate.py
"""

from __future__ import annotations

from vizier.analyze import generate as G


def _raises(fn, *a, **k) -> bool:
    try:
        fn(*a, **k)
        return False
    except ValueError:
        return True


def test_every_palette_passes():
    for theme in ("default", "muted"):
        for mode in ("light", "dark"):
            for n in range(2, 9):
                try:
                    r = G.suggest_palette(n, mode=mode, theme=theme)
                except ValueError:
                    continue  # theme/mode combo not offered — fine
                assert r["ok"], f"{theme}/{mode} n={n}:\n{r['text']}"


def test_palette_all_pairs_small():
    # a scatter palette (any two can neighbor) still passes at small n
    assert G.suggest_palette(5, pairs="all")["ok"]


def test_common_ramps_pass():
    for hue in ("blue", "navy", "green", "teal", "orange", "gray"):
        for steps in (3, 4, 5):
            assert G.suggest_ramp(steps, hue=hue)["ok"], f"{hue} {steps}"
    for hue in ("blue", "navy", "gray"):
        assert G.suggest_ramp(7, hue=hue)["ok"], f"{hue} 7"


def test_infeasible_ramp_returns_best_valid_with_advice():
    # A returned ramp is always valid. An impossible request no longer errors: it
    # returns the longest ramp the hue can hold, says so, and names what to change.
    r = G.suggest_ramp(7, hue="green")
    assert r["ok"], r["text"]
    assert r["met"] is False
    assert 2 <= len(r["ramp"]) < 7
    assert r["advice"] and "blue/navy/gray" in " ".join(r["advice"])


def test_palette_past_ceiling_returns_best_valid_with_advice():
    r = G.suggest_palette(12)
    assert r["ok"], r["text"]
    assert r["met"] is False and r["requested"] == 12
    assert len(r["palette"]) == 8
    joined = " ".join(r["advice"]).lower()
    assert "other" in joined and "small multiples" in joined


def test_theme_without_mode_falls_back_and_says_so():
    r = G.suggest_palette(4, mode="dark", theme="muted")
    assert r["ok"] and r["theme"] == "default" and r["met"] is False
    assert any("muted" in a for a in r["advice"])


def test_malformed_requests_still_raise():
    assert _raises(G.suggest_palette, 0)
    assert _raises(G.suggest_palette, 4, theme="no-such-theme")
    assert _raises(G.suggest_ramp, 1)


def test_ink_on():
    assert G.ink_on("#102a52")["ink"] == "#ffffff"   # dark fill -> white ink
    assert G.ink_on("#fafaf7")["ink"] == "#111111"   # light surface -> dark ink
    assert G.ink_on("#0072b2")["aa_normal_text"] is True


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
