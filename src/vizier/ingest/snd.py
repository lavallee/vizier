"""Society for News Design (snd.org) ingest.

snd.org is a WordPress site with ~4,000 posts across governance, events,
competitions, and a long tail of design walkthroughs. Most of the site is
announcement/governance content; walkthroughs concentrate in a few
categories. We scope the crawl to those categories and dedup.

This covers what the ingest tiering doc calls "SND.Ink" — SND has never
had a crisply-isolatable walkthrough publication, so we approximate with
the data-viz / design / profiles-adjacent categories.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ._common import fetch_html
from ._sitemap_blog import BlogConfig, run_blog_ingest

SOURCE = "snd"

# The data-viz / walkthrough-adjacent categories. /category/<cat>/page/N/
# pagination is WP-standard.
CATEGORIES = (
    "data-visualization",
    "design/multi-media",
    "news/profiles",
    "design/digital-design",
    "design/newspaper-design",
    "design/magazine-design",
    "design/innovation",
    "design/ar-vr-xr",
    "design/artificial-intelligence",
    "visuals/illustrations",
    "creative-conference-calls",
)

POST_HREF_RE = re.compile(r'href="(https://snd\.org/[a-z0-9\-]+/)"')
MAX_PAGES = 40  # safety cap per category


def _discover_urls_for_category(cat: str, workers: int = 4) -> set[str]:
    """Walk /category/<cat>/page/N/ until a page yields no new posts."""
    seen: set[str] = set()

    def fetch_page(n: int) -> set[str]:
        url = f"https://snd.org/category/{cat}/" if n == 1 \
            else f"https://snd.org/category/{cat}/page/{n}/"
        html = fetch_html(url)
        if not html:
            return set()
        urls = set(POST_HREF_RE.findall(html))
        # Drop obvious non-post snd.org pages (nav, archives, utility)
        return {
            u for u in urls
            if "/category/" not in u and "/tag/" not in u
            and "/author/" not in u and "/about-us" not in u
            and "/events" not in u and "/get-involved" not in u
            and "/join-snd" not in u and "/best-of" not in u
            and "/jobs" not in u and "/home-v5" not in u
        }

    # Walk serially but with per-page parallelism left to caller; cat-level
    # discovery only talks to one URL at a time so pagination-awareness
    # (stopping when a page returns nothing new) is straightforward.
    for n in range(1, MAX_PAGES + 1):
        page_urls = fetch_page(n)
        new = page_urls - seen
        if not new:
            break
        seen |= new
    return seen


def _discover_all(workers: int = 4) -> list[str]:
    all_urls: set[str] = set()
    # Category-level parallelism is safe — each is a different URL path.
    with ThreadPoolExecutor(max_workers=min(workers, len(CATEGORIES))) as pool:
        futures = {pool.submit(_discover_urls_for_category, c): c for c in CATEGORIES}
        for fut in as_completed(futures):
            cat = futures[fut]
            urls = fut.result()
            print(f"  [{SOURCE}] {cat}: {len(urls)} posts", flush=True)
            all_urls |= urls
    return sorted(all_urls)


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=[],
    # SND uses a standard WP single-post template
    article_selectors=[
        ".entry-content", "article .post-content", "main article",
        "article", "main",
    ],
    title_selectors=["h1.entry-title", "article h1", "h1"],
    author_selectors=[".author a", ".byline a", "[rel=author]"],
    date_selectors=["time[datetime]", ".entry-date", ".posted-on time"],
    organization="Society for News Design",
    default_creators=[],
    tags=["snd", "design", "newsroom"],
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 8) -> dict:
    print(f"[{SOURCE}] discovering URLs across {len(CATEGORIES)} categories...", flush=True)
    urls = _discover_all(workers=workers)
    print(f"[{SOURCE}] {len(urls)} total unique URLs discovered", flush=True)
    return run_blog_ingest(CONFIG, urls, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
