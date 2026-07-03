"""Junk Charts ingest.

Kaiser Fung's long-running critique blog, now at junkcharts.com (Ghost)
after the typepad.com host migrated in 2025. Each post is a critique of
a specific chart from the wild — invaluable for calibrating the *voice*
and *axes* of visualization critique.

We crawl the sitemap for every post URL, then fetch each and extract
title + body as a critique item. Junk Charts covers 2006-present; a
full crawl is ~600 posts.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ..schema import Item
from ..storage import corpus_root
from ._common import fetch_html, slugify, soup

SOURCE = "junkcharts"
SITEMAP_URL = "https://www.junkcharts.com/sitemap-posts.xml"


def _post_urls() -> list[str]:
    """Pull all post URLs from the sitemap, filtering out image entries."""
    r = httpx.get(SITEMAP_URL, follow_redirects=True, timeout=30)
    r.raise_for_status()
    s = BeautifulSoup(r.text, "xml")
    urls: list[str] = []
    for loc in s.find_all("loc"):
        u = loc.text.strip()
        parsed = urlparse(u)
        if "junkcharts.com" not in parsed.netloc:
            continue
        if parsed.path.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")):
            continue
        if "/content/images/" in parsed.path or "images.unsplash.com" in u:
            continue
        if parsed.path in ("/", ""):
            continue
        urls.append(u.rstrip("/"))
    # Dedup preserving order
    seen = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _extract_post(url: str, html: str) -> Item | None:
    s = soup(html)
    article = s.select_one("article") or s
    title_el = s.select_one("h1") or s.select_one(".post-title") or s.select_one("title")
    title = title_el.get_text(strip=True) if title_el else "Untitled"

    # Body: prefer article content, exclude navigation
    paragraphs: list[str] = []
    container = s.select_one("article .gh-content") or article
    for el in container.find_all(["p", "h2", "h3", "h4", "li", "blockquote"]):
        txt = el.get_text(" ", strip=True)
        if not txt or len(txt) < 3:
            continue
        if el.name in ("h2", "h3", "h4"):
            paragraphs.append(f"\n## {txt}\n")
        elif el.name == "li":
            paragraphs.append(f"- {txt}")
        elif el.name == "blockquote":
            paragraphs.append(f"> {txt}")
        else:
            paragraphs.append(txt)
    body = "\n\n".join(paragraphs).strip()
    if len(body) < 200:
        return None

    # Publication date from time element
    date_el = s.select_one("time[datetime]")
    pub_date = date_el["datetime"] if date_el and date_el.get("datetime") else None

    slug = url.rstrip("/").rsplit("/", 1)[-1]
    details = {}
    if pub_date:
        details["publication_date"] = pub_date

    return Item(
        id=slugify(slug),
        source=SOURCE,
        type="critique",
        title=title,
        url=url,
        creators=["Kaiser Fung"],
        organization="Junk Charts",
        details=details,
        body=body,
    )


def _fetch_and_extract(url: str) -> tuple[str, Item | None]:
    html = fetch_html(url)
    if not html:
        return url, None
    return url, _extract_post(url, html)


def run(
    *,
    root: Path | None = None,
    limit: int | None = None,
    workers: int = 12,
) -> dict:
    out_root = root or corpus_root()
    jdir = out_root / SOURCE
    if jdir.exists():
        for p in jdir.glob("*.md"):
            p.unlink()

    urls = _post_urls()
    if limit:
        urls = urls[:limit]

    written = 0
    skipped = 0
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_fetch_and_extract, u): u for u in urls}
        for fut in as_completed(futures):
            _u, item = fut.result()
            if item:
                item.write(out_root)
                written += 1
            else:
                skipped += 1
            done += 1
            if done % 50 == 0:
                print(f"  ... {done}/{len(urls)} (written={written} skipped={skipped})", flush=True)
    return {"urls": len(urls), "written": written, "skipped": skipped}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
