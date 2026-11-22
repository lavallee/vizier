"""Load a table for `vizier show`: CSV or JSON rows, plus an optional
Frictionless `datapackage.json` beside it.

Deterministic and dependency-free (stdlib `csv` / `json`). The loader keeps
cells as strings; typing is the profiler's job, so the two can be tested apart.

What the loader *does* own:

- **Missing tokens.** A datapackage's `missingValues` (schema- or
  resource-level) replaces the defaults, exactly as Frictionless specifies.
  Without one, a conservative default set is used.
- **State columns.** A column named `<field>__state` marks, row by row, why a
  value of `<field>` is absent ("suppressed", "not_collected", …). Those
  columns are lifted out of the table and attached to their field, so a
  suppressed value is never mistaken for a zero or silently dropped.
- **Nested JSON records.** `{"id": .., "values": {"a": 1}}` flattens one level
  (`a`, or `values.a` when that would collide).
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_MISSING = ("", "NA", "N/A", "n/a", "na", "null", "NULL", "None", "NaN", "nan", "-", "..", ".")

#: State values that mean "the value is present and usable".
PRESENT_STATES = {"", "ok", "observed", "valid", "present", "reported", "measured", "available"}

STATE_SUFFIX = "__state"


@dataclass
class FieldMeta:
    """What a datapackage says about one field (all optional)."""

    name: str
    type: str | None = None
    format: str | None = None
    title: str | None = None
    description: str | None = None
    unit: str | None = None


@dataclass
class Table:
    columns: list[str]
    rows: list[dict[str, str | None]]  # raw cells; None = a missing token
    source: str = ""
    name: str = ""
    meta: dict[str, FieldMeta] = field(default_factory=dict)
    #: field -> per-row state string (None where the row has no state recorded)
    states: dict[str, list[str | None]] = field(default_factory=dict)
    package: dict[str, Any] | None = None
    missing_values: tuple[str, ...] = DEFAULT_MISSING

    def __len__(self) -> int:
        return len(self.rows)

    def column(self, name: str) -> list[str | None]:
        return [r.get(name) for r in self.rows]

    def state_of(self, name: str, i: int) -> str | None:
        """The recorded absence-state of row `i`'s `name` value, if any."""
        st = self.states.get(name)
        if not st:
            return None
        s = st[i]
        if s is None or s.strip().lower() in PRESENT_STATES:
            return None
        return s.strip()

    def label(self, name: str) -> str:
        m = self.meta.get(name)
        return (m.title if m and m.title else name)

    def unit(self, name: str) -> str | None:
        m = self.meta.get(name)
        return m.unit if m else None

    def to_csv(self, columns: list[str] | None = None) -> str:
        cols = columns or self.columns
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator="\n")
        w.writerow(cols)
        for r in self.rows:
            w.writerow(["" if r.get(c) is None else r.get(c) for c in cols])
        return buf.getvalue()


def _flatten(rec: dict[str, Any], taken: set[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in rec.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if isinstance(v2, (dict, list)):
                    continue
                key = k2 if (k2 not in rec and k2 not in taken) else f"{k}.{k2}"
                out[key] = v2
        elif isinstance(v, list):
            continue  # nested lists aren't tabular; leave them out
        else:
            out[k] = v
    return out


def _records_from_json(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, dict):
        for key in ("data", "rows", "records", "items", "features"):
            if isinstance(obj.get(key), list):
                obj = obj[key]
                break
        else:
            # {col: [values...]} column-oriented
            if obj and all(isinstance(v, list) for v in obj.values()):
                n = max(len(v) for v in obj.values())
                return [{k: (v[i] if i < len(v) else None) for k, v in obj.items()} for i in range(n)]
            return [obj]
    if not isinstance(obj, list):
        raise ValueError("JSON table must be a list of records (or {data: [...]})")
    recs: list[dict[str, Any]] = []
    for r in obj:
        if isinstance(r, dict) and r.get("type") == "Feature" and isinstance(r.get("properties"), dict):
            r = r["properties"]
        if isinstance(r, dict):
            recs.append(r)
    return recs


def _cell(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v != v:  # NaN
        return None
    return str(v)


def _find_package(path: Path) -> Path | None:
    p = path.parent / "datapackage.json"
    return p if p.exists() else None


def _apply_package(pkg: dict[str, Any], path: Path) -> tuple[dict[str, FieldMeta], tuple[str, ...] | None, str]:
    resources = pkg.get("resources") or []
    res = None
    for r in resources:
        rp = r.get("path")
        paths = rp if isinstance(rp, list) else [rp]
        if any(p and Path(p).name == path.name for p in paths) or r.get("name") == path.stem:
            res = r
            break
    if res is None and len(resources) == 1:
        res = resources[0]
    if res is None:
        return {}, None, ""
    schema = res.get("schema") or {}
    if isinstance(schema, str):  # a path to a schema file
        sp = path.parent / schema
        schema = json.loads(sp.read_text()) if sp.exists() else {}
    meta: dict[str, FieldMeta] = {}
    for f in schema.get("fields") or []:
        name = f.get("name")
        if not name:
            continue
        meta[name] = FieldMeta(
            name=name,
            type=f.get("type"),
            format=f.get("format"),
            title=f.get("title"),
            description=f.get("description"),
            unit=f.get("unit") or f.get("units") or (f.get("constraints") or {}).get("unit"),
        )
    mv = schema.get("missingValues", res.get("missingValues", pkg.get("missingValues")))
    missing = tuple(str(x) for x in mv) if isinstance(mv, list) else None
    title = res.get("title") or pkg.get("title") or ""
    return meta, missing, title


def load_table(path: str | Path, *, datapackage: str | Path | None = None) -> Table:
    """Read a CSV / JSON table and its datapackage (if one sits beside it)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    pkg_path = Path(datapackage) if datapackage else _find_package(path)
    pkg = json.loads(pkg_path.read_text()) if pkg_path and pkg_path.exists() else None
    meta, missing, title = _apply_package(pkg, path) if pkg else ({}, None, "")
    missing_values = missing if missing is not None else DEFAULT_MISSING

    if path.suffix.lower() in (".json", ".geojson") or text.lstrip()[:1] in "[{":
        recs = _records_from_json(json.loads(text))
        taken: set[str] = set()
        flat = []
        for r in recs:
            fr = _flatten(r, taken)
            flat.append(fr)
        columns: list[str] = []
        for r in flat:
            for k in r:
                if k not in columns:
                    columns.append(k)
        raw_rows = [{c: _cell(r.get(c)) for c in columns} for r in flat]
    else:
        dialect = csv.excel
        try:
            dialect = csv.Sniffer().sniff(text[:4096], delimiters=",\t;|")
        except csv.Error:
            pass
        reader = csv.reader(io.StringIO(text), dialect)
        all_rows = [r for r in reader if any(c.strip() for c in r)]
        if not all_rows:
            raise ValueError(f"{path}: no rows")
        header = [h.strip() for h in all_rows[0]]
        columns = [h or f"column_{i + 1}" for i, h in enumerate(header)]
        raw_rows = []
        for r in all_rows[1:]:
            raw_rows.append({c: (r[i] if i < len(r) else None) for i, c in enumerate(columns)})

    miss = set(missing_values)
    rows: list[dict[str, str | None]] = []
    for r in raw_rows:
        rows.append({c: (None if v is None or v.strip() in miss else v.strip()) for c, v in r.items()})

    states: dict[str, list[str | None]] = {}
    for c in list(columns):
        if c.endswith(STATE_SUFFIX):
            base = c[: -len(STATE_SUFFIX)]
            states[base] = [r.get(c) for r in rows]
            columns.remove(c)
            for r in rows:
                r.pop(c, None)
    # A state column also turns the matching value into a gap even if the
    # cell held a placeholder like 0 — "suppressed" is never a zero.
    for base, st in states.items():
        if base not in columns:
            continue
        for i, s in enumerate(st):
            if s is not None and s.strip().lower() not in PRESENT_STATES:
                rows[i][base] = None

    return Table(
        columns=columns,
        rows=rows,
        source=str(path),
        name=title or path.stem,
        meta=meta,
        states=states,
        package=pkg,
        missing_values=tuple(missing_values),
    )


def table_from_records(records: list[dict[str, Any]], *, name: str = "table",
                       meta: dict[str, FieldMeta] | None = None) -> Table:
    """Build a Table from in-memory records (MCP / library callers)."""
    taken: set[str] = set()
    flat = [_flatten(r, taken) for r in records]
    columns: list[str] = []
    for r in flat:
        for k in r:
            if k not in columns:
                columns.append(k)
    miss = set(DEFAULT_MISSING)
    rows = []
    for r in flat:
        row = {}
        for c in columns:
            v = _cell(r.get(c))
            row[c] = None if v is None or v.strip() in miss else v.strip()
        rows.append(row)
    states: dict[str, list[str | None]] = {}
    for c in list(columns):
        if c.endswith(STATE_SUFFIX):
            base = c[: -len(STATE_SUFFIX)]
            states[base] = [r.get(c) for r in rows]
            columns.remove(c)
            for r in rows:
                r.pop(c, None)
    for base, st in states.items():
        for i, s in enumerate(st):
            if base in columns and s is not None and s.strip().lower() not in PRESENT_STATES:
                rows[i][base] = None
    return Table(columns=columns, rows=rows, name=name, meta=meta or {}, states=states)
