"""Profile a table: what each column is and what role it can play in a figure.

Deterministic, no model. For every column: a kind (number, integer, date,
category, text, identifier, boolean, geometry), a role (measure, dimension,
time, geography, identifier, label, geometry), ranges, missingness, recorded
absence-states (suppressed / not collected), and geography hints (FIPS, ZIP/
ZCTA, ISO country codes, US state names or postal codes, latitude/longitude).

The profile is the input to the form ranking, and it is also returned to the
caller as-is: it is a useful thing to read on its own.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any

from .table import Table

US_STATES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut",
    "delaware", "district of columbia", "florida", "georgia", "hawaii", "idaho", "illinois",
    "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine", "maryland",
    "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana",
    "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania",
    "rhode island", "south carolina", "south dakota", "tennessee", "texas", "utah",
    "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming",
    "puerto rico",
}
US_POSTAL = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT",
    "VT", "VA", "WA", "WV", "WI", "WY", "PR",
}

_NUM_STRIP = re.compile(r"[,$€£¥%\s]")
_NUM = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
_YEAR = re.compile(r"^(1[5-9]\d\d|20\d\d|21\d\d)$")
_YM = re.compile(r"^(\d{4})[-/](\d{1,2})$")
_YQ = re.compile(r"^(\d{4})[- ]?[Qq]([1-4])$")
_YMD = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})")
_MDY = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
_SVG_PATH = re.compile(r"^\s*[Mm]\s*-?\d")

_TIME_NAME = re.compile(r"(^|[_\s.-])(year|yr|date|month|quarter|period|week|day|time|fy|when)([_\s.-]|$)", re.I)
_ID_NAME = re.compile(r"(^|[_\s.-])(id|key|code|uuid|slug|geoid|fips|zcta|zip|zipcode)([_\s.-]|$)|_id$|^id$", re.I)
_LABEL_NAME = re.compile(r"(^|[_\s.-])(name|label|title|place|area|town|city|municipality)([_\s.-]|$)", re.I)
_LAT = re.compile(r"^(lat|latitude|y_lat)$", re.I)
_LON = re.compile(r"^(lon|lng|long|longitude|x_lon)$", re.I)
_GEOM_NAME = re.compile(r"^(path|d|svg_path|geometry|shape|geom)$", re.I)


def parse_number(s: str | None) -> float | None:
    if s is None:
        return None
    t = s.strip()
    neg = t.startswith("(") and t.endswith(")")
    if neg:
        t = t[1:-1]
    t = _NUM_STRIP.sub("", t)
    if not _NUM.match(t):
        return None
    try:
        v = float(t)
    except ValueError:
        return None
    if math.isinf(v) or math.isnan(v):
        return None
    return -v if neg else v


def _decimal_year(d: date) -> float:
    start = date(d.year, 1, 1)
    days = (date(d.year + 1, 1, 1) - start).days
    return d.year + (d - start).days / days


def parse_time(s: str | None, *, year_ok: bool = True) -> tuple[float, str] | None:
    """(decimal year, granularity) for a date-like string, else None."""
    if s is None:
        return None
    t = s.strip()
    if year_ok and _YEAR.match(t):
        return float(t), "year"
    m = _YQ.match(t)
    if m:
        return int(m.group(1)) + (int(m.group(2)) - 1) / 4, "quarter"
    m = _YM.match(t)
    if m and 1 <= int(m.group(2)) <= 12:
        return int(m.group(1)) + (int(m.group(2)) - 1) / 12, "month"
    m = _YMD.match(t)
    if m:
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
        gran = "datetime" if len(t) > 10 and ("T" in t or ":" in t) else "day"
        if gran == "datetime":
            try:
                dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
                return _decimal_year(dt.date()) + (dt.hour * 3600 + dt.minute * 60) / (86400 * 365.25), gran
            except ValueError:
                pass
        return _decimal_year(d), gran
    m = _MDY.match(t)
    if m:
        try:
            d = date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            return None
        return _decimal_year(d), "day"
    return None


@dataclass
class ColumnProfile:
    name: str
    label: str
    kind: str            # number | integer | date | category | text | identifier | boolean | geometry
    role: str            # measure | dimension | time | geography | identifier | label | geometry
    n: int
    n_missing: int
    n_distinct: int
    unit: str | None = None
    description: str | None = None
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    median: float | None = None
    granularity: str | None = None   # for time columns
    geo: str | None = None           # fips-state | fips-county | zcta | iso2 | iso3 | us-state | us-postal | lat | lon
    states: dict[str, int] = field(default_factory=dict)   # absence-state -> count
    examples: list[str] = field(default_factory=list)
    top: list[tuple[str, int]] = field(default_factory=list)  # most frequent categories

    @property
    def n_suppressed(self) -> int:
        return sum(self.states.values())

    @property
    def n_present(self) -> int:
        return self.n - self.n_missing

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["n_suppressed"] = self.n_suppressed
        d["top"] = [list(t) for t in self.top]
        return {k: v for k, v in d.items() if v not in (None, [], {})}


@dataclass
class Profile:
    name: str
    source: str
    n_rows: int
    columns: list[ColumnProfile]
    notes: list[str] = field(default_factory=list)

    def by_role(self, *roles: str) -> list[ColumnProfile]:
        return [c for c in self.columns if c.role in roles]

    def get(self, name: str) -> ColumnProfile | None:
        for c in self.columns:
            if c.name == name:
                return c
        return None

    @property
    def measures(self) -> list[ColumnProfile]:
        return self.by_role("measure")

    @property
    def times(self) -> list[ColumnProfile]:
        return self.by_role("time")

    @property
    def dimensions(self) -> list[ColumnProfile]:
        return self.by_role("dimension")

    @property
    def geographies(self) -> list[ColumnProfile]:
        return self.by_role("geography")

    @property
    def geometry(self) -> ColumnProfile | None:
        g = self.by_role("geometry")
        return g[0] if g else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "n_rows": self.n_rows,
            "columns": [c.to_dict() for c in self.columns],
            "notes": self.notes,
        }


def _frac(xs: list[bool]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _geo_hint(name: str, vals: list[str]) -> str | None:
    nl = name.lower()
    if not vals:
        return None
    if _LAT.match(name):
        return "lat"
    if _LON.match(name):
        return "lon"
    if _frac([v.strip().lower() in US_STATES for v in vals]) >= 0.9:
        return "us-state"
    if _frac([v.strip() in US_POSTAL for v in vals]) >= 0.95 and ("state" in nl or "st" == nl or len(set(vals)) > 3):
        return "us-postal"
    digits = _frac([v.isdigit() for v in vals]) >= 0.98
    lens = {len(v) for v in vals}
    if digits and ("zcta" in nl or "zip" in nl) and lens <= {5}:
        return "zcta"
    if digits and ("fips" in nl or "geoid" in nl or "county" in nl):
        if lens <= {5}:
            return "fips-county"
        if lens <= {2}:
            return "fips-state"
        if lens <= {11}:
            return "fips-tract"
    if digits and lens <= {5} and any(v.startswith("0") for v in vals) and ("id" in nl or "code" in nl):
        # 5-digit zero-padded codes: ZIP/ZCTA or county FIPS. Say which is ambiguous.
        return "zcta-or-fips"
    upper = _frac([v.isalpha() and v.isupper() for v in vals]) >= 0.98
    if upper and lens <= {3} and ("iso" in nl or "country" in nl):
        return "iso3"
    if upper and lens <= {2} and ("iso" in nl or "country" in nl):
        return "iso2"
    if "county" in nl or "state" in nl or "country" in nl or "region" in nl or "district" in nl:
        return "named-area"
    return None


def profile_column(table: Table, name: str) -> ColumnProfile:
    raw = table.column(name)
    n = len(raw)
    present = [v for v in raw if v is not None]
    meta = table.meta.get(name)
    states: dict[str, int] = {}
    if name in table.states:
        for i in range(n):
            s = table.state_of(name, i)
            if s:
                states[s] = states.get(s, 0) + 1
    distinct = list(dict.fromkeys(present))
    base = dict(
        name=name,
        label=table.label(name),
        n=n,
        n_missing=n - len(present),
        n_distinct=len(distinct),
        unit=table.unit(name),
        description=meta.description if meta else None,
        states=states,
        examples=distinct[:4],
    )

    declared = (meta.type or "").lower() if meta else ""

    # Geometry: SVG path strings (pre-projected outlines) carried in a column.
    if present and (_GEOM_NAME.match(name) or _frac([bool(_SVG_PATH.match(v)) for v in present[:50]]) > 0.9) \
            and _frac([bool(_SVG_PATH.match(v)) for v in present[:50]]) > 0.9:
        base["examples"] = [present[0][:40] + "…"]
        return ColumnProfile(kind="geometry", role="geometry", **base)

    nums = [parse_number(v) for v in present]
    num_frac = _frac([x is not None for x in nums]) if present else 0.0
    looks_time_name = bool(_TIME_NAME.search(name))
    looks_id_name = bool(_ID_NAME.search(name))
    geo = _geo_hint(name, present[:500])

    # Time: declared, or values parse as dates; bare 4-digit years only when the
    # name says time (a column of 4-digit numbers is otherwise just numbers).
    is_time_declared = declared in ("date", "datetime", "year", "yearmonth", "time")
    times = [parse_time(v, year_ok=looks_time_name or is_time_declared) for v in present]
    time_frac = _frac([t is not None for t in times]) if present else 0.0
    zero_padded = any(v[:1] == "0" and len(v) > 1 and v.isdigit() for v in present[:200])
    if present and (is_time_declared or time_frac >= 0.95) and not zero_padded and not geo:
        ts = [t for t in times if t]
        grans = {g for _, g in ts}
        gran = next((g for g in ("datetime", "day", "month", "quarter", "year") if g in grans), None)
        vals = [v for v, _ in ts]
        return ColumnProfile(kind="date", role="time", granularity=gran,
                             min=min(vals) if vals else None, max=max(vals) if vals else None, **base)

    if present and declared in ("boolean",) or (present and {v.lower() for v in distinct} <= {"true", "false", "yes", "no", "y", "n"} and len(distinct) <= 2):
        return ColumnProfile(kind="boolean", role="dimension", top=_top(present), **base)

    # Lat / lon are numbers, but they place, they don't measure.
    if geo in ("lat", "lon") and num_frac >= 0.95:
        vals = [x for x in nums if x is not None]
        return ColumnProfile(kind="number", role="geography", geo=geo, min=min(vals), max=max(vals), **base)

    # Numbers: zero-padded codes and code-named columns are identifiers, not measures.
    if present and num_frac >= 0.95 and declared not in ("string",):
        if zero_padded or (looks_id_name and not declared.startswith(("number", "integer"))) or geo in ("zcta", "fips-county", "fips-state", "fips-tract", "zcta-or-fips"):
            role = "geography" if geo else "identifier"
            return ColumnProfile(kind="identifier", role=role, geo=geo, **base)
        vals = [x for x in nums if x is not None]
        is_int = all(float(x).is_integer() for x in vals)
        srt = sorted(vals)
        mid = len(srt) // 2
        median = srt[mid] if len(srt) % 2 else (srt[mid - 1] + srt[mid]) / 2
        unit = base.pop("unit") or _unit_hint(name, present)
        if looks_time_name and is_int and vals and 1500 <= min(vals) and max(vals) <= 2200:
            return ColumnProfile(kind="date", role="time", granularity="year", unit=unit,
                                 min=min(vals), max=max(vals), **base)
        return ColumnProfile(
            kind="integer" if is_int else "number", role="measure", unit=unit,
            min=srt[0], max=srt[-1], mean=sum(vals) / len(vals), median=median, **base,
        )

    if not present:
        # An all-missing column: if it carries states it is a measure with no
        # usable values; otherwise there's nothing to place.
        role = "measure" if states else "identifier"
        return ColumnProfile(kind="number" if states else "text", role=role, **base)

    # Strings.
    if geo:
        role = "geography"
        kind = "category" if len(distinct) < n else "identifier"
        return ColumnProfile(kind=kind, role=role, geo=geo, top=_top(present), **base)
    unique = len(distinct) == len(present) and len(present) > 1
    if unique and (looks_id_name or _frac([any(ch.isdigit() for ch in v) for v in present]) > 0.8 and not _LABEL_NAME.search(name)):
        return ColumnProfile(kind="identifier", role="identifier", **base)
    if unique and len(present) > 30:
        return ColumnProfile(kind="text", role="label", **base)
    # Mostly-distinct names (places, people) label rows; they don't group them.
    if len(present) > 30 and len(distinct) > 0.5 * len(present):
        return ColumnProfile(kind="text", role="label", **base)
    avg_len = sum(len(v) for v in present) / len(present)
    if avg_len > 60 and unique:
        return ColumnProfile(kind="text", role="label", **base)
    if avg_len > 80:
        return ColumnProfile(kind="text", role="label", **base)
    return ColumnProfile(kind="category", role="dimension", top=_top(present), **base)


def _top(vals: list[str], k: int = 8) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def _unit_hint(name: str, vals: list[str]) -> str | None:
    nl = name.lower()
    if any("%" in v for v in vals[:50]) or re.search(r"(^|_)(pct|percent|share|rate_pct)(_|$)", nl):
        return "%"
    if any(v.strip().startswith("$") for v in vals[:50]) or re.search(r"(usd|dollars|income|salary|wage|revenue|cost|price|spend)", nl):
        return "USD"
    return None


def profile_table(table: Table) -> Profile:
    cols = [profile_column(table, c) for c in table.columns]
    notes: list[str] = []
    # A single text column alongside identifiers is a label, not a category of one.
    for c in cols:
        if c.role == "dimension" and c.n_distinct == c.n and c.n > 12:
            c.role = "label"
            c.kind = "text"
    supp = [c for c in cols if c.n_suppressed]
    for c in supp:
        notes.append(
            f"{c.label}: {c.n_suppressed} value(s) recorded as "
            + ", ".join(f"{k} ({v})" for k, v in c.states.items())
            + " — drawn as gaps or marked, never as zero."
        )
    for c in cols:
        if c.n_missing and c.role in ("measure", "time") and c.n_missing > c.n_suppressed:
            notes.append(f"{c.label}: {c.n_missing - c.n_suppressed} of {c.n} value(s) missing.")
    if any(c.geo == "zcta-or-fips" for c in cols):
        notes.append("A 5-digit zero-padded code could be a ZIP/ZCTA or a county FIPS; "
                     "say which in the column name or datapackage so a map joins the right outlines.")
    return Profile(name=table.name, source=table.source, n_rows=len(table), columns=cols, notes=notes)
