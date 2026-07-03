"""Sigma Awards ingest.

Sigma publishes their full shortlist + winner data as CSVs in
https://github.com/Sigma-Awards/The-Sigma-Awards-projects-data , one
CSV per year for "single projects" (there are also "portfolios" CSVs;
we skip those — they're career-body submissions, not specific works).

From 2022 onward the CSV has a "Jury's comments" column for tier-bearing
rows. 2020 and 2021 lack that column; we emit items anyway with the
rich self-description fields, and can later attach commentary scraped
from datajournalism.com/awards (2020 host).

We emit one Item per row where `Results` is tier-bearing
(Winner / Co-winner / Honorable Mention / Citation / Shortlist / etc.).
Rows marked "Participant" or blank are skipped — low signal and would
balloon the corpus by an order of magnitude.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from ..schema import Item
from ..storage import corpus_root
from ._common import slugify

SOURCE = "sigma"

RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "sigma-raw"

CSV_BASE = (
    "https://raw.githubusercontent.com/Sigma-Awards/"
    "The-Sigma-Awards-projects-data/main/"
    "The%20Sigma%20Awards%20{year}-single%20projects.csv"
)
KNOWN_YEARS = (2020, 2021, 2022, 2023, 2024, 2025)

# Include only rows where Results marks a quality tier
TIER_KEEP_PATTERNS = (
    r"^winner",           # Winner, Winner (joint), Co-winner
    r"^co-winner",
    r"^honorable mention",
    r"^citation",
    r"^shortlist",
)
_TIER_RE = re.compile("|".join(TIER_KEEP_PATTERNS), re.IGNORECASE)

# Per-year encoding — discovered empirically
ENCODINGS = {
    2020: "utf-8-sig",
    2021: "utf-8-sig",
    2022: "utf-8-sig",
    2023: "latin-1",
    2024: "utf-8-sig",
    2025: "utf-8-sig",
}


def _ensure_raw(year: int) -> Path:
    """Download the year's CSV if not already cached."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{year}-single-projects.csv"
    if not path.exists():
        import httpx
        url = CSV_BASE.format(year=year)
        r = httpx.get(url, follow_redirects=True, timeout=30)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def _normalize_tier(raw: str) -> str:
    r = raw.strip().lower()
    if r.startswith("winner") or r.startswith("co-winner"):
        return "winner"
    if "honorable" in r:
        return "honorable-mention"
    if "citation" in r:
        return "citation"
    if "shortlist" in r:
        return "shortlist"
    return r or "unknown"


def _split_names(raw: str) -> list[str]:
    """Split 'Who made this project' free text into a list.

    Heuristic only — the field is free-form author credits.
    """
    if not raw:
        return []
    # Replace 'and' with comma, split on commas/semicolons/slashes
    raw = re.sub(r"\s+and\s+", ", ", raw)
    parts = re.split(r"[,;/]\s*", raw)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) < 120]


def _links(row: dict) -> list[str]:
    urls: list[str] = []
    for k in ("Link 1", "Link 2", "Link 3", "Link 4", "Link 5", "Link 6", "Link 7"):
        v = (row.get(k) or "").strip()
        if v:
            urls.append(v)
    return urls


def _strip_bom_keys(row: dict) -> dict:
    return {k.lstrip("\ufeff"): v for k, v in row.items()}


@dataclass
class _Entry:
    year: int
    title: str
    tier: str
    organization: str | None
    country: str | None
    category: str | None
    creators: list[str]
    artifact_url: str | None
    other_urls: list[str]
    publication_date: str | None
    tags: list[str]
    tools: list[str]
    description: str
    impact: str
    context: str
    techniques: str
    lessons: str
    jury_comment: str
    languages: str | None


def _split_csv_list(raw: str) -> list[str]:
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


def _row_to_entry(row: dict, year: int) -> _Entry | None:
    row = _strip_bom_keys(row)
    result = row.get("Results", "")
    if not _TIER_RE.match(result.strip()):
        return None
    title = (row.get("Project title") or "").strip()
    if not title:
        return None
    links = _links(row)
    return _Entry(
        year=year,
        title=title,
        tier=_normalize_tier(result),
        organization=(row.get("Publishing organisations") or "").strip() or None,
        country=(row.get("Country") or "").strip() or None,
        category=(row.get("Category") or "").strip() or None,
        creators=_split_names(row.get("Who made this project", "")),
        artifact_url=links[0] if links else None,
        other_urls=links[1:],
        publication_date=(row.get("Publication date") or "").strip() or None,
        tags=_split_csv_list(row.get("Tags", "")),
        tools=_split_csv_list(row.get("Technologies/tools used", "")),
        description=(row.get("A short description of the project") or "").strip(),
        impact=(row.get("What was the impact of the project?") or "").strip(),
        context=next(
            (row.get(k, "").strip() for k in row if k.startswith("What context")),
            "",
        ),
        techniques=next(
            (row.get(k, "").strip() for k in row if k.startswith("What tools, techniques")),
            "",
        ),
        lessons=(row.get("What can other journalists learn from this project?") or "").strip(),
        jury_comment=(row.get("Jury's comments") or "").strip(),
        languages=(row.get("Language") or row.get("Languages") or "").strip() or None,
    )


def _entry_to_item(e: _Entry) -> Item:
    # Body: jury comment (if present) followed by structured self-description
    parts: list[str] = []
    if e.jury_comment:
        parts.append(f"## Jury's comments\n\n{e.jury_comment}")
    if e.description:
        parts.append(f"## Description\n\n{e.description}")
    if e.impact:
        parts.append(f"## Impact\n\n{e.impact}")
    if e.context:
        parts.append(f"## Context\n\n{e.context}")
    if e.techniques:
        parts.append(f"## Tools, techniques, how used\n\n{e.techniques}")
    if e.lessons:
        parts.append(f"## What other journalists can learn\n\n{e.lessons}")
    body = "\n\n".join(parts)

    details = {}
    if e.publication_date:
        details["publication_date"] = e.publication_date
    if e.tools:
        details["tools"] = e.tools
    if e.languages:
        details["languages"] = e.languages
    if e.other_urls:
        details["other_urls"] = e.other_urls
    if e.category:
        details["sigma_category"] = e.category

    return Item(
        id=slugify(f"{e.year}-{e.title}"),
        source=SOURCE,
        type="award_entry",
        title=e.title,
        url=None,
        year=e.year,
        tier=e.tier,
        creators=e.creators,
        organization=e.organization,
        country=e.country,
        artifact_url=e.artifact_url,
        tags=e.tags,
        details=details,
        body=body,
    )


def _ingest_year(year: int) -> list[Item]:
    path = _ensure_raw(year)
    enc = ENCODINGS.get(year, "utf-8-sig")
    with path.open(encoding=enc, errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    items: list[Item] = []
    for row in rows:
        entry = _row_to_entry(row, year)
        if entry:
            items.append(_entry_to_item(entry))
    return items


def run(*, years: list[int] | None = None, root: Path | None = None) -> dict[int, int]:
    years = list(years or KNOWN_YEARS)
    out_root = root or corpus_root()
    # Clean out any previous Sigma items so renames/tier changes don't leave orphans
    sigma_dir = out_root / SOURCE
    if sigma_dir.exists():
        for p in sigma_dir.glob("*.md"):
            p.unlink()
    results: dict[int, int] = {}
    for y in years:
        items = _ingest_year(y)
        for it in items:
            it.write(out_root)
        results[y] = len(items)
    return results


if __name__ == "__main__":
    print(run())
