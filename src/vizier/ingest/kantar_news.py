"""Kantar news ingest — jury commentary from annual winners posts.

Kantar's showcase detail pages carry no jury commentary. But the annual
`/news/*-announcing-the-YYYY-winners` blog posts include quoted judge
commentary for special-award winners (Impressive Individual, Outstanding
Studio, Rising Star, Test of Time, Most Impactful Community Leader,
Most Beautiful). Main Gold/Silver/Bronze category winners are listed
without per-item quotes.

We do two things:
1. For each h3 that has following commentary paragraphs, match (by year
   + slugified title) to an existing Kantar item in the corpus and
   append `## Jury commentary` to its body.
2. Items that don't match an existing showcase entry (special-award
   people/studios like "Rising Star: Mandy Spaltman") are written as
   fresh Items with `tier=<special-award-name>`.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urljoin

import frontmatter
from bs4 import BeautifulSoup

from ..schema import Item
from ..storage import corpus_root, iter_items
from ._common import fetch_html, slugify, soup

SOURCE = "kantar"
BASE = "https://www.informationisbeautifulawards.com"

# Only posts where per-winner commentary is extractable. 2022 and 2023
# use plain <p> lines with no commentary; including them produces only
# false-positive "category as entry" matches.
WINNER_POSTS = {
    2024: f"{BASE}/news/680-announcing-the-2024-winners",
}

# Tier prefixes that appear in h3 lines like "Gold: <title> by <authors>"
TIER_PREFIXES = ("Gold:", "Silver:", "Bronze:", "Winner:")

# Special-award h2 headings — items under these don't live in the
# showcase, so we create them fresh instead of enriching.
SPECIAL_AWARDS = {
    "Impressive Individual": "impressive-individual",
    "Outstanding Studio": "outstanding-studio",
    "Rising Star": "rising-star",
    "Test of Time": "test-of-time",
    "Most Impactful Community Leader": "most-impactful-community-leader",
    "Most Beautiful": "most-beautiful",
    "Community Vote": "community-vote",
}


def _strip_tier(line: str) -> tuple[str, str]:
    """From 'Gold: <title> by <authors>' → ('gold', '<title> by <authors>')."""
    for prefix in TIER_PREFIXES:
        if line.startswith(prefix):
            return prefix.rstrip(":").lower(), line[len(prefix):].strip()
    return "", line.strip()


def _strip_authors(text: str) -> str:
    """From '<title> by <authors>' → '<title>'."""
    # Case-insensitive split on " by "
    m = re.split(r"\s+[Bb]y\s+", text, maxsplit=1)
    return m[0].strip() if m else text.strip()


def _parse_post(url: str, year: int) -> list[dict]:
    """Return a list of entries from one announcement post.

    Each entry: {year, category, tier, raw_title_line, title, commentary}.
    """
    html = fetch_html(url)
    if not html:
        return []
    s = soup(html)
    main = s.select_one("main") or s
    elements = main.find_all(["h2", "h3", "p"])
    entries: list[dict] = []
    current_h2: str | None = None
    for i, el in enumerate(elements):
        if el.name == "h2":
            current_h2 = el.get_text(strip=True)
            continue
        if el.name != "h3":
            continue
        title_line = el.get_text(" ", strip=True)
        tier, title_and_authors = _strip_tier(title_line)
        if not tier and current_h2 in SPECIAL_AWARDS:
            # Non-Gold/Silver/Bronze special-award heading e.g. "Mandy Spaltman"
            tier = SPECIAL_AWARDS[current_h2]
            title_and_authors = title_line
        title = _strip_authors(title_and_authors)
        # Collect following <p> until next h2/h3
        commentary_parts: list[str] = []
        for sib in elements[i + 1:]:
            if sib.name in ("h2", "h3"):
                break
            if sib.name == "p":
                t = sib.get_text(" ", strip=True)
                if t and len(t) > 15:
                    commentary_parts.append(t)
        commentary = "\n\n".join(commentary_parts).strip()
        entries.append({
            "year": year,
            "category": current_h2,
            "tier": tier,
            "raw_title_line": title_line,
            "title": title,
            "title_and_authors": title_and_authors,
            "commentary": commentary,
        })
    return entries


def _index_existing(root: Path) -> dict[tuple[int, str], Path]:
    """Map (year, slugified-title) → Path for existing Kantar items."""
    idx: dict[tuple[int, str], Path] = {}
    for item in iter_items(source=SOURCE, root=root):
        if item.year is None:
            continue
        idx[(item.year, slugify(item.title))] = item.path(root)
    return idx


def _append_commentary(path: Path, commentary: str, category: str) -> None:
    post = frontmatter.load(str(path))
    body = post.content or ""
    # Don't double-append on re-runs
    if commentary.strip() in body:
        return
    addition = f"\n\n## Jury commentary\n\n_Category: {category}_\n\n{commentary}"
    post.content = body + addition
    path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")


def _special_award_item(entry: dict) -> Item:
    base_title = entry["title_and_authors"]
    return Item(
        id=slugify(f"{entry['year']}-special-{entry['tier']}-{base_title}"),
        source=SOURCE,
        type="award_entry",
        title=base_title,
        url=WINNER_POSTS.get(entry["year"]),
        year=entry["year"],
        tier=entry["tier"],
        category=entry["category"],
        body=entry["commentary"],
    )


def run(*, root: Path | None = None) -> dict:
    out_root = root or corpus_root()
    # Index existing items for enrichment
    existing = _index_existing(out_root)

    enriched = 0
    created = 0
    no_match = 0
    for year, url in sorted(WINNER_POSTS.items()):
        entries = _parse_post(url, year)
        for e in entries:
            if not e["commentary"]:
                continue
            if e["category"] in SPECIAL_AWARDS:
                item = _special_award_item(e)
                item.write(out_root)
                created += 1
                continue
            # Main category — enrich existing Kantar item
            key = (e["year"], slugify(e["title"]))
            path = existing.get(key)
            if not path:
                no_match += 1
                continue
            _append_commentary(path, e["commentary"], e["category"] or "")
            enriched += 1
    return {"enriched": enriched, "created": created, "no_match": no_match}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
