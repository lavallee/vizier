"""Generic sitemap-based blog ingester.

Most practitioner-walkthrough blogs expose a sitemap (WordPress does by
default). This module gives source modules a common spine:

    run_sitemap_blog(
        source="eagereyes",
        sitemap_urls=[...],
        url_filter=lambda u: ...,
        article_selectors=["article", "main", ".post"],
        ...
    )

handles: sitemap crawl → dedup → per-URL fetch → article extraction →
raw HTML snapshot → image download → markdown projection → Item write.

Rich artifacts (raw_html_path, images list, source_url) land in
`Item.details` so downstream readers don't need to re-fetch.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, Tag

from ..schema import Item
from ..storage import corpus_root
from ._common import fetch_html, plugin_fetch, slugify, soup
from ._fetch_html import (
    fetch_images,
    html_to_markdown,
    save_raw_html,
)


@dataclass
class BlogConfig:
    """Per-source configuration for the generic blog ingester."""

    source: str                           # corpus dir name, e.g. "eagereyes"
    sitemap_urls: list[str]               # one or more sitemap.xml URLs
    article_selectors: list[str]          # CSS selectors tried in order to find the article body
    title_selectors: list[str] = field(
        default_factory=lambda: ["h1.entry-title", "h1", ".post-title", "title"]
    )
    author_selectors: list[str] = field(
        default_factory=lambda: [".author a", ".byline a", "[rel=author]", ".author"]
    )
    date_selectors: list[str] = field(
        default_factory=lambda: ["time[datetime]", ".published", ".post-date"]
    )
    url_filter: Callable[[str], bool] | None = None
    organization: str | None = None
    default_creators: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    min_body_chars: int = 400
    max_images_per_post: int = 20
    fetch_images_flag: bool = True


def _fetch_sitemap_xml(url: str) -> str | None:
    """Fetch a sitemap XML, falling back to the richer fetcher if httpx 403s.

    Cloudflare-fronted sites (some WP hosts) block naive UAs. When a heavier
    fetcher is wired in via `$VIZIER_FETCHER` (see `_common.plugin_fetch`), its
    UA-rotating strategies get through where a bare httpx GET does not.
    """
    try:
        r = httpx.get(url, follow_redirects=True, timeout=30,
                      headers={"User-Agent": "vizier/0.1 (+ingest)"})
        if r.status_code == 200 and r.text.lstrip().startswith("<"):
            return r.text
    except Exception:
        pass
    try:
        html = plugin_fetch(url)
        if html and html.lstrip().startswith("<"):
            return html
    except Exception as e:
        print(f"  sitemap fallback failed: {url}: {e}", flush=True)
    return None


def fetch_sitemap_urls(sitemap_urls: list[str]) -> list[str]:
    """Return every <loc> found across one or more sitemap URLs or sitemap indexes.

    Handles nested sitemap indexes (sitemap → sitemap → pages) and falls
    back to the optional richer fetcher when a direct httpx fetch is blocked.
    """
    all_urls: list[str] = []
    seen: set[str] = set()
    to_crawl = list(sitemap_urls)
    visited_sitemaps: set[str] = set()

    while to_crawl:
        sm = to_crawl.pop(0)
        if sm in visited_sitemaps:
            continue
        visited_sitemaps.add(sm)
        xml = _fetch_sitemap_xml(sm)
        if not xml:
            print(f"  sitemap fetch failed: {sm}", flush=True)
            continue
        s = BeautifulSoup(xml, "xml")
        is_index = s.find("sitemapindex") is not None
        if is_index:
            for loc in s.find_all("loc"):
                to_crawl.append(loc.text.strip())
            continue
        for loc in s.find_all("loc"):
            u = loc.text.strip()
            if u in seen:
                continue
            seen.add(u)
            all_urls.append(u)
    return all_urls


def _first_text(s: BeautifulSoup | Tag, selectors: list[str]) -> str:
    for sel in selectors:
        el = s.select_one(sel)
        if el:
            t = el.get_text(" ", strip=True)
            if t:
                return t
    return ""


def _first_tag(s: BeautifulSoup | Tag, selectors: list[str]) -> Tag | None:
    for sel in selectors:
        el = s.select_one(sel)
        if el is not None:
            return el
    return None


def _extract_date(s: BeautifulSoup | Tag, selectors: list[str]) -> str | None:
    for sel in selectors:
        el = s.select_one(sel)
        if el is None:
            continue
        # Prefer datetime attr, fall back to text
        if el.has_attr("datetime"):
            return str(el["datetime"]).strip()
        t = el.get_text(" ", strip=True)
        if t:
            return t
    return None


def _item_id_from_url(url: str) -> str:
    """Stable item id from the last path segment of a post URL."""
    path = urlparse(url).path.rstrip("/")
    slug = path.rsplit("/", 1)[-1] or "index"
    return slugify(slug)


def _extract_post(
    url: str,
    html: str,
    config: BlogConfig,
    *,
    img_client: httpx.Client | None,
) -> Item | None:
    s = soup(html)

    article = _first_tag(s, config.article_selectors)
    if article is None:
        return None

    title = _first_text(s, config.title_selectors) or "Untitled"
    author = _first_text(s, config.author_selectors) if config.author_selectors else ""
    pub_date = _extract_date(s, config.date_selectors) if config.date_selectors else None

    body_md = html_to_markdown(article)
    if len(body_md) < config.min_body_chars:
        return None

    item_id = _item_id_from_url(url)

    # Raw HTML + images — strictly additive metadata
    raw_path = save_raw_html(config.source, item_id, html)

    images = []
    if config.fetch_images_flag:
        try:
            images = fetch_images(
                config.source, item_id, article, url,
                client=img_client,
                max_images=config.max_images_per_post,
            )
        except Exception as e:
            print(f"  image fetch failed for {url}: {e}", flush=True)

    creators: list[str] = []
    if author:
        creators.append(author)
    if config.default_creators:
        for c in config.default_creators:
            if c not in creators:
                creators.append(c)

    details = {
        "raw_html_path": raw_path,
        "source_url": url,
    }
    if pub_date:
        details["publication_date"] = pub_date
    if images:
        details["images"] = [
            {"path": i.local_path, "src_url": i.src_url, "alt": i.alt, "caption": i.caption}
            for i in images
        ]

    return Item(
        id=item_id,
        source=config.source,
        type="process_note",
        title=title,
        url=url,
        creators=creators,
        organization=config.organization,
        tags=list(config.tags),
        details=details,
        body=body_md,
    )


def _fetch_and_extract(
    url: str,
    config: BlogConfig,
    img_client: httpx.Client | None,
) -> tuple[str, Item | None]:
    html = fetch_html(url)
    if not html:
        return url, None
    try:
        return url, _extract_post(url, html, config, img_client=img_client)
    except Exception as e:
        print(f"  extract failed for {url}: {e}", flush=True)
        return url, None


def run_blog_ingest(
    config: BlogConfig,
    urls: list[str],
    *,
    root: Path | None = None,
    limit: int | None = None,
    workers: int = 8,
    wipe: bool = True,
) -> dict:
    """Run the per-post fetch/extract/write pipeline on a given URL list.

    Non-sitemap sources (e.g. paginated index pages, Atom feeds) can use
    this directly after discovering URLs by whatever means they prefer.
    `run_sitemap_blog` is the sitemap-based convenience wrapper.
    """
    out_root = root or corpus_root()
    sdir = out_root / config.source

    if wipe and sdir.exists():
        for p in sdir.glob("*.md"):
            p.unlink()
        for sub in ("_raw", "_images"):
            d = out_root / config.source / sub
            if d.exists():
                import shutil
                shutil.rmtree(d)

    if config.url_filter is not None:
        urls = [u for u in urls if config.url_filter(u)]
    urls = sorted(set(urls))
    if limit:
        urls = urls[:limit]
    print(f"[{config.source}] {len(urls)} candidate URLs", flush=True)

    # Shared image client so connection pool is reused across all posts.
    img_client = httpx.Client(
        timeout=20, follow_redirects=True,
        headers={"User-Agent": "vizier/0.1 (+ingest)"},
    )

    written = 0
    skipped = 0
    done = 0
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_fetch_and_extract, u, config, img_client): u for u in urls
            }
            for fut in as_completed(futures):
                _u, item = fut.result()
                if item:
                    item.write(out_root)
                    written += 1
                else:
                    skipped += 1
                done += 1
                if done % 25 == 0:
                    print(f"  [{config.source}] {done}/{len(urls)} "
                          f"(written={written} skipped={skipped})", flush=True)
    finally:
        img_client.close()

    return {
        "source": config.source,
        "urls": len(urls),
        "written": written,
        "skipped": skipped,
    }


def run_sitemap_blog(
    config: BlogConfig,
    *,
    root: Path | None = None,
    limit: int | None = None,
    workers: int = 8,
    wipe: bool = True,
) -> dict:
    """Convenience wrapper: discover URLs from config.sitemap_urls, then run."""
    print(f"[{config.source}] crawling sitemap(s)...", flush=True)
    urls = fetch_sitemap_urls(config.sitemap_urls)
    return run_blog_ingest(
        config, urls, root=root, limit=limit, workers=workers, wipe=wipe,
    )
