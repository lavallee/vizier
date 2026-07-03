"""Turn computed checks into critique-ready evidence.

The bridge between the deterministic analysis (`color`, `structure`) and the LLM
critique. Given an artifact's SVG/HTML source or an explicit palette, it runs the
checks and renders a block that (a) shows the raw report and (b) translates each
hard finding into vizier's structural-risk language — because "color-only encoding"
and "text wearing the series color" are exactly the kind of structural risk vizier's
own principles prize, and a measured ΔE (or a matched hex) is the sharpest
possible version of one.

Injected into a critique prompt, this gives the model ground truth it cannot fake;
surfaced in output, it gives the reader a fact instead of a hunch. Covers more than
color now: an SVG also gets the marks-&-anatomy structural checks.
"""

from __future__ import annotations

from . import color as C, extract as X


def computed_color_findings(
    *,
    markup: str | None = None,
    palette: str | list[str] | None = None,
    mode: str = "light",
    surface: str | None = None,
    pairs: str | None = None,
) -> str | None:
    """Critique-ready computed findings, or None if nothing is measurable. Pass
    `palette` (explicit hexes) or `markup` (SVG/HTML source). For markup, both the
    color checks and the structural marks checks run."""
    pal: list[str] | None = None
    achromatic: list[str] = []
    source = ""
    struct: list[dict] = []
    if palette:
        items = palette.split(",") if isinstance(palette, str) else palette
        pal = [c.strip() for c in items if c and c.strip()]
        source = "the provided palette"
    elif markup and X.looks_like_markup(markup):
        ex = X.extract(markup, surface=surface)
        pal, achromatic = ex.palette, ex.achromatic
        source = "the artifact's SVG/HTML colors"
        from . import structure as St
        struct = St.lint_svg(markup, surface=surface)["findings"]

    report = None
    if pal:
        # all-pairs is the honest default for a critique: a colorblind reader can
        # confuse ANY two legend swatches, not just adjacent bands.
        report = C.validate_categorical(pal, mode=mode, surface=surface, pairs=pairs or "all")

    if report is None and not struct:
        return None
    return _render(report, source or "the artifact", achromatic, struct)


def _render(report: C.Report | None, source: str, achromatic: list[str], struct: list[dict]) -> str:
    lines: list[str] = []
    if report is not None:
        lines += [
            f"## Computed color findings (deterministic — measured from {source}, "
            "not the vision model's guess)",
            "",
            C.format_report(report),
            "",
        ]
        interp: list[str] = []
        for c in report.checks:
            if c.name == "CVD separation" and c.state in ("fail", "floor"):
                w = report.worst_cvd or {}
                sev = ("collapse to nearly the same color" if c.state == "fail"
                       else "sit in the 8–12 floor band (distinct only with a second channel)")
                cvd_name = {"protan": "protanopia", "deutan": "deuteranopia",
                            "tritan": "tritanopia"}.get(w.get("kind"), str(w.get("kind")))
                interp.append(
                    f"- **Colorblind separation:** {w.get('a')} and {w.get('b')} {sev} under "
                    f"{cvd_name} (ΔE {w.get('delta')}; target ≥ 12). If color alone tells these "
                    "series apart, red-green colorblind readers can't — the 'color-only encoding' "
                    "structural risk. Fix with a redundant channel (direct labels, position, "
                    "texture) or a re-derived CVD-safe palette."
                )
            elif c.name == "Chroma floor" and c.state == "fail":
                interp.append(
                    "- **Reads as gray:** " + c.detail.split(":", 1)[1].strip()
                    + " — below the OKLCH chroma floor, so they don't do identity work."
                )
            elif c.name == "Lightness band" and c.state == "fail":
                interp.append("- **Lightness:** " + c.detail + " — outside the legible band for this surface.")
            elif c.name == "Contrast vs surface" and c.state == "relief":
                interp.append(
                    "- **Contrast:** some marks sit below 3:1 on the surface — legible only with a "
                    "relief channel (visible direct labels or a table view); flag if neither is present."
                )
        if interp:
            lines.append("What this means for the critique:")
            lines.extend(interp)
        else:
            lines.append("No hard color failures — the palette is CVD-safe and legible on this surface.")
        if achromatic:
            lines += [
                "",
                f"(Treated as chrome, not data: {', '.join(achromatic)}. If any is a real data "
                "series shown in gray, that itself is a color-encoding risk worth naming.)",
            ]

    if struct:
        from . import structure as St
        if lines:
            lines.append("")
        lines += [
            "## Computed structural findings (deterministic — from the SVG markup)",
            "",
            St.format_findings(struct),
        ]

    return "\n".join(lines)
