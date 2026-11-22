"""Small, dependency-free SVG toolkit for `vizier show`.

Scales, nice ticks, number formatting, text measurement and wrapping, and the
figure frame (title, subtitle, plot, notes, source). Output is plain SVG 1.1
text: it opens from `file://`, embeds in any page, and is what vizier's own
`analyze` checks read back.

Why Python and not d3: the static SVG is the deliverable that gets embedded and
critiqued, so it has to be produced without a browser. Generating it here keeps
`show` offline, deterministic and testable, and keeps a 280 KB script out of
every figure. Hover detail rides on native SVG `<title>` elements, which need
no script at all.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from html import escape

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
SURFACE = "#fcfcfb"
INK = "#1a1a19"
INK2 = "#5f5e5a"
MUTED = "#8a8984"
GRID = "#e6e5e0"
AXIS = "#b9b8b2"
OTHER = "#a3a29c"
MISSING_FILL = "url(#vz-hatch)"


def esc(s) -> str:
    return escape(str(s), quote=True)


def text_width(s: str, size: float) -> float:
    """Rough rendered width of `s` at `size` px in a sans UI face."""
    w = 0.0
    for ch in str(s):
        if ch in "il.,:;|!'’ ":
            w += 0.3
        elif ch in "mwMW@%":
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.62
        else:
            w += 0.53
    return w * size


def wrap(s: str, size: float, width: float) -> list[str]:
    words = str(s).split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, size) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def truncate(s: str, size: float, width: float) -> str:
    s = str(s)
    if text_width(s, size) <= width:
        return s
    while s and text_width(s + "…", size) > width:
        s = s[:-1]
    return s + "…"


# ---------------------------------------------------------------- numbers

def nice_step(span: float, count: int) -> float:
    if span <= 0 or not math.isfinite(span):
        return 1.0
    raw = span / max(1, count)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    if lo == hi:
        lo, hi = (lo - 1, hi + 1) if lo == 0 else (lo - abs(lo) * 0.1, hi + abs(hi) * 0.1)
    step = nice_step(hi - lo, count)
    start = math.floor(lo / step + 1e-9) * step
    end = math.ceil(hi / step - 1e-9) * step
    ticks = []
    v = start
    while v <= end + step * 1e-6:
        ticks.append(round(v, 10))
        v += step
    return ticks


def nice_domain(lo: float, hi: float, count: int = 5, *, zero: bool = False) -> tuple[float, float, list[float]]:
    if zero:
        lo, hi = min(0.0, lo), max(0.0, hi)
    t = nice_ticks(lo, hi, count)
    return t[0], t[-1], t


def _digits_for(step: float) -> int:
    if step >= 1 or step <= 0:
        return 0
    return min(6, max(0, -math.floor(math.log10(step) + 1e-9)))


def fmt(v: float | None, unit: str | None = None, *, digits: int | None = None, compact: bool = False) -> str:
    """Format a number with its unit: 12.3%, $95,935, 1.2M."""
    if v is None:
        return "–"
    u = (unit or "").strip()
    ul = u.lower()
    a = abs(v)
    if compact and a >= 1000:
        for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
            if a >= div:
                n = v / div
                s = f"{n:.1f}".rstrip("0").rstrip(".") + suf
                break
    else:
        auto = digits is None
        if auto:
            digits = 0 if a >= 100 or float(v).is_integer() else (1 if a >= 10 else (2 if a >= 1 else 3))
        s = f"{v:,.{digits}f}"
        if auto and "." in s:
            s = s.rstrip("0").rstrip(".")
    if ul in ("usd", "$", "dollars"):
        return ("-$" + s[1:]) if s.startswith("-") else "$" + s
    if u == "%" or ul in ("percent", "pct"):
        return s + "%"
    if ul in ("eur", "€"):
        return "€" + s
    if ul in ("gbp", "£"):
        return "£" + s
    return s


def unit_suffix(unit: str | None) -> str:
    """How a unit reads in an axis label: '(µg/m³)', '(%)', '($)'."""
    if not unit:
        return ""
    ul = unit.lower()
    if ul in ("usd", "$", "dollars"):
        return " ($)"
    if unit == "%" or ul in ("percent", "pct"):
        return " (%)"
    return f" ({unit})"


def tick_formatter(ticks: list[float], unit: str | None):
    step = abs(ticks[1] - ticks[0]) if len(ticks) > 1 else 1
    d = _digits_for(step)
    big = max((abs(t) for t in ticks), default=0) >= 10000
    return lambda v: fmt(v, unit, digits=d, compact=big)


def fmt_time(v: float, granularity: str | None) -> str:
    year = int(math.floor(v + 1e-9))
    if granularity in (None, "year"):
        return str(int(round(v)))
    frac = v - year
    if granularity == "quarter":
        return f"{year} Q{int(round(frac * 4)) + 1}"
    if granularity == "month":
        months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
        return f"{months[min(11, int(round(frac * 12)))]} {year}"
    day = int(round(frac * 365.25))
    import datetime as _dt
    d = _dt.date(year, 1, 1) + _dt.timedelta(days=min(day, 364))
    return d.isoformat()


def time_ticks(lo: float, hi: float, granularity: str | None, count: int = 6) -> list[float]:
    if granularity in (None, "year") or hi - lo >= 3:
        step = max(1.0, nice_step(hi - lo, count))
        step = max(1.0, round(step))
        start = math.ceil(lo - 1e-9)
        out = []
        v = start
        while v <= hi + 1e-9:
            out.append(float(v))
            v += step
        return out or [lo, hi]
    return nice_ticks(lo, hi, count)


@dataclass
class Linear:
    d0: float
    d1: float
    r0: float
    r1: float

    def __call__(self, v: float) -> float:
        if self.d1 == self.d0:
            return (self.r0 + self.r1) / 2
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


@dataclass
class Band:
    domain: list[str]
    r0: float
    r1: float
    padding: float = 0.2

    @property
    def step(self) -> float:
        return (self.r1 - self.r0) / max(1, len(self.domain))

    @property
    def bandwidth(self) -> float:
        return self.step * (1 - self.padding)

    def __call__(self, key: str) -> float:
        i = self.domain.index(key)
        return self.r0 + i * self.step + self.step * self.padding / 2


# ---------------------------------------------------------------- elements

def line(x1, y1, x2, y2, stroke=GRID, width=1.0, extra="") -> str:
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{(" " + extra) if extra else ""}/>')


def text(x, y, s, *, size=12, fill=INK2, anchor="start", weight=None, extra="", baseline=None) -> str:
    w = f' font-weight="{weight}"' if weight else ""
    b = f' dominant-baseline="{baseline}"' if baseline else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}"{w}{b}{(" " + extra) if extra else ""}>{esc(s)}</text>')


def rect(x, y, w, h, fill, extra="", tip: str | None = None) -> str:
    w = max(0.0, w)
    h = max(0.0, h)
    body = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{(" " + extra) if extra else ""}'
    if tip:
        return body + f'><title>{esc(tip)}</title></rect>'
    return body + "/>"


def circle(cx, cy, r, fill, extra="", tip: str | None = None) -> str:
    body = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{(" " + extra) if extra else ""}'
    if tip:
        return body + f'><title>{esc(tip)}</title></circle>'
    return body + "/>"


def path(d: str, *, stroke="none", fill="none", width=2.0, extra="", tip: str | None = None) -> str:
    body = (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{(" " + extra) if extra else ""}')
    if tip:
        return body + f'><title>{esc(tip)}</title></path>'
    return body + "/>"


DEFS = (
    '<defs><pattern id="vz-hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)"><rect width="6" height="6" fill="#f1f0ec"/>'
    f'<line x1="0" y1="0" x2="0" y2="6" stroke="{AXIS}" stroke-width="2"/></pattern></defs>'
)


@dataclass
class Words:
    """Every word on the figure. Annotation slots are filled by key."""

    title: str = ""
    subtitle: str = ""
    x_label: str = ""
    y_label: str = ""
    source: str = ""
    notes: list[str] = field(default_factory=list)
    annotations: dict[str, str] = field(default_factory=dict)


def legend(items: list[tuple[str, str]], x: float, y: float, width: float, *, size=12, kind="rect") -> tuple[str, float]:
    """A horizontal swatch legend; wraps. Returns (svg, height)."""
    parts = []
    cx, cy = x, y
    lh = size + 8
    for label, color in items:
        w = 14 + 6 + text_width(label, size) + 16
        if cx + w > x + width and cx > x:
            cx = x
            cy += lh
        if kind == "line":
            parts.append(line(cx, cy + size * 0.45, cx + 14, cy + size * 0.45, stroke=color, width=3))
        elif kind == "hatch":
            parts.append(rect(cx, cy, 14, size * 0.9, MISSING_FILL, extra=f'stroke="{AXIS}" stroke-width="0.5"'))
        else:
            parts.append(rect(cx, cy, 14, size * 0.9, color))
        parts.append(text(cx + 20, cy + size * 0.85, label, size=size, fill=INK2))
        cx += w
    return "\n".join(parts), (cy - y) + lh


def frame(body: str, body_height: float, words: Words, *, width: float, aria: str = "", form: str = "",
          compact: bool = False, view_id: str | None = None) -> str:
    """Wrap a plot body with the title, subtitle, notes and source line.

    `compact` sets smaller headline type for contact-sheet views."""
    pad = 12 if compact else 16
    inner = width - 2 * pad
    ts, ss = (15, 12) if compact else (20, 14)
    parts: list[str] = []
    y = pad
    title_lines = wrap(words.title, ts, inner) if words.title else []
    for ln in title_lines:
        y += ts + 4
        parts.append(text(pad, y, ln, size=ts, fill=INK, weight="600", extra='class="vz-title"'))
    if words.subtitle:
        y += 3
        for ln in wrap(words.subtitle, ss, inner):
            y += ss + 5
            parts.append(text(pad, y, ln, size=ss, fill=INK2, extra='class="vz-subtitle"'))
    y += 14
    parts.append(f'<g class="vz-plot" transform="translate(0,{y:.1f})">{body}</g>')
    y += body_height
    foot: list[str] = []
    if words.notes:
        y += 6
        for i, note in enumerate(words.notes):
            for j, ln in enumerate(wrap(("Note: " if i == 0 and len(words.notes) == 1 else ("Notes: " if i == 0 else "")) + note, 12, inner)):
                y += 16
                foot.append(text(pad, y, ln, size=12, fill=INK2, extra='class="vz-note"'))
    if words.source:
        y += 4
        for ln in wrap("Source: " + words.source, 11, inner):
            y += 15
            foot.append(text(pad, y, ln, size=11, fill=MUTED, extra='class="vz-source"'))
    parts.extend(foot)
    total = y + pad
    label = esc(aria or words.title or form)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {total:.0f}" '
        f'width="{width:.0f}" height="{total:.0f}" role="img" aria-label="{label}" '
        f'font-family="{FONT}" data-form="{esc(form)}"'
        + (f' data-view="{esc(view_id)}"' if view_id else "") + ">"
        f'<title>{esc(words.title or form)}</title><desc>{label}</desc>{DEFS}'
        f'<rect width="100%" height="100%" fill="{SURFACE}"/>'
        + "\n".join(parts)
        + "</svg>"
    )
