"""Kantar Information is Beautiful Awards ingest.

Source: informationisbeautifulawards.com

The showcase is paginated and filterable by year and award tier. We
iterate all (year, tier) pairs for the tiers we care about and extract
one Item per entry from the listing page. Detail pages don't carry
jury commentary, so the listing is sufficient — we get:

    title, tier, year, snippet description, artifact URL.

Tiers kept (high-signal): gold, silver, bronze, winner, short-list.
Skipped: long-list (too many, weakest signal).

Years: 2012-2019, 2022-2024 (2020, 2021, 2025 skipped by Kantar).
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..schema import Item
from ..storage import corpus_root
from ._common import fetch_html, slugify

SOURCE = "kantar"
BASE = "https://www.informationisbeautifulawards.com"
KNOWN_YEARS = (2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024)
KEEP_TIERS = ("gold", "silver", "bronze", "winner", "short-list")

MAX_PAGES = 20  # safety cap — no legitimate year+tier has gone past this


def _listing_url(year: int, tier: str, page: int) -> str:
    return (
        f"{BASE}/showcase?action=index&award={year}&controller=showcase"
        f"&page={page}&pcategory={tier}&type=awards"
    )


def _normalize_tier(raw: str) -> str:
    """Map Kantar's tier token to vizier's convention."""
    r = raw.strip().lower().replace("-", "")
    return {
        "shortlist": "shortlist",
    }.get(r, raw.strip().lower())


def _parse_block(block, year: int, tier: str) -> dict | None:
    title_a = block.select_one(".title h4 a, .title a")
    if not title_a:
        return None
    title = title_a.get_text(strip=True)
    detail_href = title_a.get("href") or ""
    detail_url = urljoin(BASE, detail_href)
    snippet_el = block.select_one(".text")
    description = snippet_el.get_text(" ", strip=True) if snippet_el else ""
    # External artifact URL — the footer link points to the hosting site
    ext_a = block.select_one(".footer .link a[href]")
    artifact_url = ext_a["href"].strip() if ext_a else None
    if artifact_url and not artifact_url.startswith(("http://", "https://")):
        artifact_url = f"https://{artifact_url}"
    return {
        "title": title,
        "detail_url": detail_url,
        "description": description,
        "artifact_url": artifact_url,
        "tier": _normalize_tier(tier),
        "year": year,
    }


def _entries_for_year_tier(year: int, tier: str) -> list[dict]:
    out: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        url = _listing_url(year, tier, page)
        html = fetch_html(url)
        if not html:
            break
        s = BeautifulSoup(html, "lxml")
        blocks = s.find_all("li", class_="block")
        if not blocks:
            break
        for b in blocks:
            parsed = _parse_block(b, year, tier)
            if parsed:
                out.append(parsed)
        if len(blocks) < 30:
            break
    return out


def _entry_to_item(e: dict) -> Item:
    return Item(
        id=slugify(f"{e['year']}-{e['title']}"),
        source=SOURCE,
        type="award_entry",
        title=e["title"],
        url=e["detail_url"],
        year=e["year"],
        tier=e["tier"],
        artifact_url=e["artifact_url"],
        body=e["description"],
    )


def run(*, years: list[int] | None = None, tiers: list[str] | None = None, root: Path | None = None) -> dict:
    years = list(years or KNOWN_YEARS)
    tiers = list(tiers or KEEP_TIERS)
    out_root = root or corpus_root()
    kdir = out_root / SOURCE
    if kdir.exists():
        for p in kdir.glob("*.md"):
            p.unlink()

    # Dedup across tiers — a single entry can appear at its highest tier only.
    # If the same (year, title) shows up with both winner and gold (it shouldn't,
    # but just in case), keep the higher.
    tier_rank = {"gold": 5, "silver": 4, "bronze": 3, "winner": 2, "shortlist": 1}
    best: dict[tuple[int, str], dict] = {}

    counts: dict[str, int] = {}
    for year in years:
        for tier in tiers:
            got = _entries_for_year_tier(year, tier)
            counts[f"{year}-{tier}"] = len(got)
            for e in got:
                key = (e["year"], e["title"])
                cur = best.get(key)
                if cur is None or tier_rank.get(e["tier"], 0) > tier_rank.get(cur["tier"], 0):
                    best[key] = e

    for e in best.values():
        _entry_to_item(e).write(out_root)
    counts["total_written"] = len(best)
    return counts


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
