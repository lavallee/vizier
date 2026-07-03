"""Computable data-viz color checks — a Python port of the `dataviz` skill's
`validate_palette.js`.

Design-system-agnostic: feed it any palette's hex values plus the mode and
surface, and it *computes* — never eyeballs — the checks that can be measured
from color alone:

    lightness band   — OKLCH L within the mode's band
    chroma floor     — OKLCH C >= floor (below it a hue reads as gray)
    CVD separation   — Machado-2009 ΔE between slots (protan/deutan/tritan);
                       adjacent pairs by default, pairs="all" for scatter/maps
    contrast         — WCAG ratio of each mark against the chart surface

An ordinal ramp (funnel stages, tiers, buckets) takes the ramp checks instead
(`validate_ordinal`): monotone lightness, visible ΔL between steps, a light end
that still clears the surface, one hue.

Thresholds and transforms are kept byte-identical to `validate_palette.js` so
vizier's computed verdict never disagrees with that skill's. Pure stdlib math (no
numpy) so the float sequence mirrors the JS line for line.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

# ── thresholds (identical to validate_palette.js) ────────────────────────────
BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}  # OKLCH L
CHROMA_FLOOR = 0.10  # OKLCH C
CVD_TARGET = 12.0
CVD_FLOOR = 8.0  # CIE76 ΔE on adjacent pairs
CONTRAST_MIN = 3.0  # WCAG vs surface
DEFAULT_SURFACE = {"light": "#fcfcfb", "dark": "#1a1a19"}
ORDINAL_MIN_DL = 0.06  # min OKLCH ΔL between adjacent steps
ORDINAL_LIGHT_FLOOR = 2.0  # lightest step: WCAG contrast vs surface

# Machado, Oliveira & Fernandes (2009) CVD transforms at severity 1.0 (linear RGB).
MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779),
               (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900)),
}


# ── color conversions ────────────────────────────────────────────────────────
def _hex2srgb(h: str) -> tuple[float, float, float]:
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _s2lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lin(h: str) -> tuple[float, float, float]:
    r, g, b = _hex2srgb(h)
    return _s2lin(r), _s2lin(g), _s2lin(b)


def _rel_lum(h: str) -> float:
    r, g, b = _lin(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio between two hex colors (order-independent)."""
    hi, lo = sorted((_rel_lum(a), _rel_lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _oklab(h: str) -> tuple[float, float, float]:
    r, g, b = _lin(h)
    l = math.pow(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b, 1 / 3)
    m = math.pow(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b, 1 / 3)
    s = math.pow(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b, 1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def oklch(h: str) -> tuple[float, float]:
    """(L, C) in OKLCH."""
    L, a, b = _oklab(h)
    return L, math.hypot(a, b)


def _okhue(h: str) -> float:
    _, a, b = _oklab(h)
    return (math.degrees(math.atan2(b, a)) % 360 + 360) % 360


def _lin2lab(r: float, g: float, b: float) -> tuple[float, float, float]:
    X = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    Y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    Z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b

    def f(t: float) -> float:
        return math.pow(t, 1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(X / 0.95047), f(Y / 1.0), f(Z / 1.08883)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def _simulate(h: str, kind: str) -> tuple[float, float, float]:
    r, g, b = _lin(h)
    M = MACHADO[kind]

    def clamp(c: float) -> float:
        return max(0.0, min(1.0, c))

    return (
        clamp(M[0][0] * r + M[0][1] * g + M[0][2] * b),
        clamp(M[1][0] * r + M[1][1] * g + M[1][2] * b),
        clamp(M[2][0] * r + M[2][1] * g + M[2][2] * b),
    )


def delta_e(h1: str, h2: str, kind: str | None = None) -> float:
    """CIE76 ΔE between two hexes, optionally under a CVD simulation
    (kind in {'protan','deutan','tritan'}); kind=None = normal vision."""
    a = _lin2lab(*(_simulate(h1, kind) if kind else _lin(h1)))
    b = _lin2lab(*(_simulate(h2, kind) if kind else _lin(h2)))
    return math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2])


# ── result types ─────────────────────────────────────────────────────────────
@dataclass
class Check:
    name: str
    state: str  # "pass" | "fail" | "floor" | "relief"
    detail: str

    @property
    def glyph(self) -> str:
        return {"pass": "PASS", "fail": "FAIL", "floor": "WARN", "relief": "WARN"}.get(self.state, self.state.upper())


@dataclass
class Report:
    checks: list[Check]
    ok: bool
    kind: str  # "categorical" | "ordinal"
    mode: str
    surface: str
    n: int
    worst_cvd: dict | None = None  # {delta, kind, a, b} for programmatic use
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "kind": self.kind,
            "mode": self.mode,
            "surface": self.surface,
            "n": self.n,
            "checks": [{"name": c.name, "state": c.state, "glyph": c.glyph, "detail": c.detail}
                       for c in self.checks],
            "worst_cvd": self.worst_cvd,
            **self.meta,
        }


def _pairs(n: int, pairs: str) -> list[tuple[int, int]]:
    if pairs == "all":
        return [(i, j) for i in range(n) for j in range(i + 1, n)]
    return [(i, i + 1) for i in range(n - 1)]


# ── categorical checks ───────────────────────────────────────────────────────
def validate_categorical(
    palette: Sequence[str],
    *,
    mode: str = "light",
    surface: str | None = None,
    pairs: str = "adjacent",
) -> Report:
    palette = [c.strip() for c in palette if c and c.strip()]
    surface = surface or DEFAULT_SURFACE[mode]
    lo, hi = BAND[mode]
    checks: list[Check] = []
    ok = True

    # lightness band
    offband = [(c, round(oklch(c)[0], 3)) for c in palette if not (lo <= oklch(c)[0] <= hi)]
    if offband:
        ok = False
    checks.append(Check("Lightness band", "fail" if offband else "pass",
                        f"outside band: {offband}" if offband else f"all {len(palette)} inside L {lo}–{hi}"))

    # chroma floor
    lowc = [(c, round(oklch(c)[1], 3)) for c in palette if oklch(c)[1] < CHROMA_FLOOR]
    if lowc:
        ok = False
    checks.append(Check("Chroma floor", "fail" if lowc else "pass",
                        f"below floor (reads gray): {lowc}" if lowc else f"all {len(palette)} >= {CHROMA_FLOOR}"))

    # CVD separation — adjacent by default; all-pairs for scatter/bubble/maps
    pairlist = _pairs(len(palette), pairs)
    label = "all-pairs" if pairs == "all" else "adjacent"
    worst = None
    for kind in ("protan", "deutan"):
        for i, j in pairlist:
            d = delta_e(palette[i], palette[j], kind)
            if worst is None or d < worst[0]:
                worst = (d, kind, palette[i], palette[j])
    tri = min((delta_e(palette[i], palette[j], "tritan") for i, j in pairlist), default=99.0)
    nor = min((delta_e(palette[i], palette[j]) for i, j in pairlist), default=99.0)
    wd = worst[0] if worst else 99.0
    cvd_state = "pass" if wd >= CVD_TARGET else "floor" if wd >= CVD_FLOOR else "fail"
    if cvd_state == "fail":
        ok = False
    worst_cvd = {"delta": round(wd, 1), "kind": worst[1], "a": worst[2], "b": worst[3]} if worst else None
    checks.append(Check("CVD separation", cvd_state,
                        (f"worst {label} {worst[3]}↔{worst[2]} ΔE {wd:.1f} ({worst[1]}) · "
                         f"tritan {tri:.1f} · normal {nor:.1f}") if worst else "n/a"))

    # contrast vs surface — sub-3:1 is a documented relief band, not a hard fail
    low = [(c, round(contrast(c, surface), 2)) for c in palette if contrast(c, surface) < CONTRAST_MIN]
    checks.append(Check("Contrast vs surface", "relief" if low else "pass",
                        (f"below {CONTRAST_MIN}:1 — relief required (visible labels or table view): {low}")
                        if low else f"all {len(palette)} >= {CONTRAST_MIN}:1"))

    return Report(checks, ok, "categorical", mode, surface, len(palette), worst_cvd)


# ── ordinal-ramp checks ──────────────────────────────────────────────────────
def validate_ordinal(
    palette: Sequence[str],
    *,
    mode: str = "light",
    surface: str | None = None,
) -> Report:
    palette = [c.strip() for c in palette if c and c.strip()]
    surface = surface or DEFAULT_SURFACE[mode]
    checks: list[Check] = []
    ok = True
    Ls = [oklch(c)[0] for c in palette]

    # monotone lightness
    order = sorted(range(len(Ls)), key=lambda i: Ls[i])
    fwd = all(v == i for i, v in enumerate(order))
    rev = all(v == len(Ls) - 1 - i for i, v in enumerate(order))
    mono = fwd or rev
    if not mono:
        ok = False
    checks.append(Check("Lightness monotone", "pass" if mono else "fail",
                        "steps read light→dark" if mono
                        else f"out of order — L values {[round(l, 3) for l in Ls]}"))

    # adjacent ΔL
    gaps = [abs(Ls[i + 1] - Ls[i]) for i in range(len(Ls) - 1)]
    thin = [(palette[i], palette[i + 1], round(g, 3)) for i, g in enumerate(gaps) if g < ORDINAL_MIN_DL]
    if thin:
        ok = False
    checks.append(Check("Adjacent ΔL", "fail" if thin else "pass",
                        f"steps too close: {thin}" if thin else f"all gaps >= {ORDINAL_MIN_DL}"))

    # lightest step vs surface
    by_l = sorted(palette, key=lambda c: oklch(c)[0])
    lightest = by_l[-1] if mode == "light" else by_l[0]
    cr = contrast(lightest, surface)
    passed = cr >= ORDINAL_LIGHT_FLOOR
    if not passed:
        ok = False
    checks.append(Check("Light-end contrast", "pass" if passed else "fail",
                        f"{lightest} at {cr:.2f}:1 vs surface"
                        + ("" if passed else f" — below {ORDINAL_LIGHT_FLOOR}:1 floor")))

    # single hue
    hues = [_okhue(c) for c in palette]
    spread = (max(hues) - min(hues)) if hues else 0.0
    if spread > 180:
        spread = 360 - spread
    one_hue = spread <= 40
    if not one_hue:
        ok = False
    checks.append(Check("Single hue", "pass" if one_hue else "fail",
                        f"hue spread {spread:.0f}°" + ("" if one_hue else " — >40°, not a one-hue ramp")))

    return Report(checks, ok, "ordinal", mode, surface, len(palette), None)


# ── formatting (mirrors validate_palette.js printReport) ─────────────────────
def format_report(r: Report) -> str:
    lines = [f"Palette ({r.mode}, surface {r.surface}, {r.kind}"
             + (" ramp" if r.kind == "ordinal" else "") + f"): {r.n} slots"]
    for c in r.checks:
        lines.append(f"  [{c.glyph:<4}] {c.name:<22} {c.detail}")
    if r.kind == "ordinal":
        tail = "  (ordinal: one hue, monotone L, visible step gaps, light end clears surface)"
    else:
        tail = ("  (CVD in the 8–12 floor band is legal ONLY with secondary encoding: "
                "direct labels, gaps, or texture)")
    lines.append("")
    lines.append(("  → ALL CHECKS PASS" if r.ok else "  → FAILED — fix the marked checks") + tail)
    return "\n".join(lines)
