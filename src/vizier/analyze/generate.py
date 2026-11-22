"""Generation-side dataviz expertise — the computable counterpart to `color`.

Critique answers "is this palette right?"; generation answers "give me one that
is." Same thresholds, so what vizier *suggests* is what vizier would *pass*. This is
what lets a renderer or agent ask vizier for correct colors instead of rolling
its own palette and hoping — vizier owns the decision, the renderer draws it.

Everything here is deterministic and validated before it's returned.
"""

from __future__ import annotations

from . import color as C

# Validated CVD-safe categorical base orders, derived by maximizing the minimum
# adjacent colorblind ΔE (see the dataviz skill's palette reference). Assigned in
# fixed order; a 9th series never gets a generated hue — it folds into "Other".
_THEMES: dict[str, dict[str, list[str]]] = {
    # The reference default — bright, high-separation (worst adjacent ΔE ~24).
    "default": {
        "light": ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"],
        "dark":  ["#3987e5", "#199e70", "#c98500", "#008300", "#9085e9", "#e66767", "#d55181", "#d95926"],
    },
    # Muted / editorial (Okabe-Ito–derived) — calmer on warm surfaces, big fills
    # stay sober. Validated for a light warm surface; the set proven in njschooldata.
    "muted": {
        "light": ["#e69f00", "#0072b2", "#009e73", "#56b4e9", "#d55e00", "#8a8f2e", "#cc79a7"],
    },
}

# Ordinal/sequential ramp anchor pairs (light end already ≥ 2:1 on a light surface,
# dark end deep). Interpolated in sRGB — stays single-hue and monotone in lightness.
_RAMP_ANCHORS: dict[str, tuple[str, str]] = {
    "blue":  ("#86b6ef", "#0d366b"),
    "navy":  ("#8bacd0", "#102a52"),
    "green": ("#589a6b", "#0b4a30"),
    "teal":  ("#4f918d", "#093f3c"),
    "orange": ("#cf8a4a", "#7a3208"),
    "gray":  ("#b0b0ab", "#33332f"),
}


def suggest_palette(
    n: int,
    *,
    mode: str = "light",
    surface: str | None = None,
    theme: str = "default",
    pairs: str = "adjacent",
) -> dict:
    """A CVD-safe categorical palette of `n` colors, validated before return.

    `pairs='all'` when the marks are a scatter/map (any two can neighbor);
    'adjacent' for stacks/bars/lines. Returns the palette, the validation report,
    and whether it passed — so the caller never has to trust it blind.

    A request that can't be met exactly is not an error. Past the validated
    ceiling the answer is the largest palette that passes, `met=False`, and
    `advice` naming what to change (fold the tail into "Other", small multiples,
    direct labels). A theme with no variant for `mode` falls back to the default
    theme's, and says so. Only a malformed request (`n < 1`, an unknown theme
    name) raises."""
    if n < 1:
        raise ValueError("n must be >= 1")
    modes = _THEMES.get(theme)
    if modes is None:
        raise ValueError(f"unknown theme '{theme}'; available: {sorted(_THEMES)}")
    advice: list[str] = []
    used_theme = theme
    base = modes.get(mode)
    if base is None:
        used_theme = "default"
        base = _THEMES["default"][mode]
        advice.append(f"theme '{theme}' has no '{mode}' variant yet (has: {sorted(modes)}); "
                      f"used theme 'default' for {mode}.")
    met = n <= len(base)
    if not met:
        advice += [
            f"{n} categorical hues can't all be told apart; the validated ceiling for "
            f"'{used_theme}/{mode}' is {len(base)}. Returned the {len(base)} that pass.",
            f"Fold the tail into 'Other' (keep the {len(base) - 1} that matter, then one "
            "neutral gray for the rest).",
            "Or facet into small multiples — one panel per series needs no hue at all.",
            "Or direct-label the lines/points and let color carry only a highlight.",
        ]
    pal = base[: min(n, len(base))]
    report = C.validate_categorical(pal, mode=mode, surface=surface, pairs=pairs)
    return {
        "palette": pal,
        "theme": used_theme,
        "mode": mode,
        "requested": n,
        "met": met and used_theme == theme,
        "advice": advice,
        "other": "#a3a29c" if mode == "light" else "#6b6a65",
        "ok": report.ok,
        "report": report.to_dict(),
        "text": C.format_report(report),
    }


def _interp(a: str, b: str, t: float) -> str:
    ah = a.lstrip("#")
    bh = b.lstrip("#")
    ar, ag, ab = (int(ah[i:i + 2], 16) for i in (0, 2, 4))
    br, bg, bb = (int(bh[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (
        round(ar + (br - ar) * t), round(ag + (bg - ag) * t), round(ab + (bb - ab) * t)
    )


def suggest_ramp(
    steps: int,
    *,
    hue: str = "blue",
    light: str | None = None,
    dark: str | None = None,
    mode: str = "light",
    surface: str | None = None,
) -> dict:
    """A one-hue ordinal ramp of `steps`, validated (monotone lightness, visible
    ΔL, a light end that clears the surface). Pass a named `hue` (blue/navy/green/
    teal/orange/gray) or explicit `light`/`dark` anchor hexes.

    When the hue can't hold `steps`, the result is the longest ramp that passes,
    with `met=False` and `advice` — not an error. A returned ramp is always valid."""
    if steps < 2:
        raise ValueError("steps must be >= 2")
    if light and dark:
        a, b = light, dark
    elif hue in _RAMP_ANCHORS:
        a, b = _RAMP_ANCHORS[hue]
    else:
        raise ValueError(f"unknown hue '{hue}'; pass explicit light/dark anchors or one of "
                         f"{sorted(_RAMP_ANCHORS)}")
    ramp = [_interp(a, b, i / (steps - 1)) for i in range(steps)]
    report = C.validate_ordinal(ramp, mode=mode, surface=surface)
    advice: list[str] = []
    met = report.ok
    if not report.ok:
        # Warm hues can't hold a >=2:1 light end AND enough ΔL for many steps.
        # Return the most steps this hue holds, validated, and say what to change.
        hi = steps
        trial, trial_report = ramp, report
        while hi > 2:
            hi -= 1
            trial = [_interp(a, b, i / (hi - 1)) for i in range(hi)]
            trial_report = C.validate_ordinal(trial, mode=mode, surface=surface)
            if trial_report.ok:
                break
        failing_text = C.format_report(report)
        ramp, report = trial, trial_report
        advice = [
            f"'{hue}' can't hold {steps} distinguishable ordered steps on this surface; "
            f"returned the {hi} it can.",
            f"Bin the data into {hi} classes, or use blue/navy/gray, which hold more steps.",
            "Past ~6 ordered classes, label the values (or add a table) rather than "
            "asking color to separate them.",
        ]
        return {
            "ramp": ramp,
            "hue": hue,
            "requested": steps,
            "met": False,
            "advice": advice,
            "ok": report.ok,
            "report": report.to_dict(),
            "text": C.format_report(report),
            "requested_report": failing_text,
        }
    return {
        "ramp": ramp,
        "hue": hue,
        "requested": steps,
        "met": met,
        "advice": advice,
        "ok": report.ok,
        "report": report.to_dict(),
        "text": C.format_report(report),
    }


def ink_on(background: str, *, dark: str = "#111111", light: str = "#ffffff") -> dict:
    """The text/ink color that best clears WCAG on `background` — the computable
    version of the 'compute label color from background luminance, don't eyeball
    it' rule. Returns the ink, its contrast ratio, and AA pass flags."""
    cd, cl = C.contrast(dark, background), C.contrast(light, background)
    ink, ratio = (dark, cd) if cd >= cl else (light, cl)
    return {
        "ink": ink,
        "ratio": round(ratio, 2),
        "aa_normal_text": ratio >= 4.5,
        "aa_large_text": ratio >= 3.0,
        "background": background,
    }
