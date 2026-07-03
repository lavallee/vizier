"""Structural checks beyond color — the marks-&-anatomy half of the dataviz method,
made computable where it reliably can be.

This is deliberately high-precision, not broad: parsing an arbitrary chart SVG for
every mark-spec violation invites false positives (one chart's "gridline" is
another's annotation). So it flags only what markup can say with confidence. The
flagship is **text wearing the series color** — a `<text>` painted in a data-series
hue, which the marks rules forbid (a light categorical hue is illegible as text;
identity belongs on a swatch beside ink text). It is exactly the class of finding
vizier's own structural-risk axis wants, and it's checkable, not eyeballed.
"""

from __future__ import annotations

import re

from .color import CHROMA_FLOOR, oklch
from .extract import _norm, extract

# a <text ...> opening tag (attrs only — enough to read an inline fill)
_TEXT_TAG = re.compile(r"<text\b[^>]*>", re.IGNORECASE | re.DOTALL)
_FILL = re.compile(r"\bfill\s*[:=]\s*['\"]?\s*(#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\))", re.IGNORECASE)


def _text_fills(svg: str) -> dict[str, int]:
    """Inline fill colors used on <text> elements, first-seen order → count.
    (Class-driven fills aren't visible here — that's fine; we only claim what we
    can see, so there are no false positives from CSS we can't resolve.)"""
    fills: dict[str, int] = {}
    for tag in _TEXT_TAG.findall(svg):
        m = _FILL.search(tag)
        if not m:
            continue
        h = _norm(m.group(1))
        if h:
            fills[h] = fills.get(h, 0) + 1
    return fills


def lint_svg(svg: str, *, surface: str | None = None) -> dict:
    """Structural (non-color) findings from a chart's SVG source. Returns a list of
    findings, each `{check, severity, detail}`, plus the raw text-fill map."""
    findings: list[dict] = []
    data = set(extract(svg, surface=surface).palette)
    tfills = _text_fills(svg)

    text_as_series = sorted(h for h in tfills if h in data)
    chromatic_text = sorted(h for h in tfills if h not in data and oklch(h)[1] >= CHROMA_FLOOR)

    if text_as_series:
        findings.append({
            "check": "text-wears-series-color",
            "severity": "high",
            "detail": (
                f"<text> is painted in data-series colors {text_as_series} — text should "
                "wear ink tokens, never the series color (a light categorical hue is "
                "illegible as text, and it fails WCAG at small sizes). Move identity onto a "
                "swatch beside ink text; keep values/labels in primary/secondary/muted ink."
            ),
        })
    elif chromatic_text:
        findings.append({
            "check": "colored-text",
            "severity": "medium",
            "detail": (
                f"<text> uses chromatic fills {chromatic_text} — check these aren't series "
                "colors doing a label's job. If they encode identity, move the color to a "
                "swatch and put the text in ink."
            ),
        })

    return {"findings": findings, "text_fills": tfills}


def format_findings(findings: list[dict]) -> str:
    """Render structural findings as critique-ready lines (empty string if none)."""
    if not findings:
        return ""
    sev = {"high": "FAIL", "medium": "WARN"}
    return "\n".join(f"- [{sev.get(f['severity'], f['severity'].upper())}] {f['detail']}"
                     for f in findings)
