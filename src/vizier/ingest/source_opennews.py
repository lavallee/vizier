"""Source (opennews.org/source) ingest.

Source is the OpenNews practitioner publication — every post answers
"we built this, here's how we decided." This is the single richest
practitioner-walkthrough corpus on the open web for news graphics work.

No sitemap is exposed; discover URLs via the paginated /articles/
index (~57 pages × 20 posts ≈ 1140 articles).
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ._common import fetch_html
from ._sitemap_blog import BlogConfig, run_blog_ingest

SOURCE = "source-opennews"

INDEX_URL_TMPL = "https://source.opennews.org/articles/?page={n}"
POST_HREF_RE = re.compile(r'href="(/articles/[a-z0-9\-]+/?)"')
MAX_PAGES = 80  # safety cap


def _discover_urls(max_pages: int = MAX_PAGES, workers: int = 8) -> list[str]:
    """Walk the paginated index until a page returns no new URLs."""
    seen: set[str] = set()

    def fetch_page(n: int) -> set[str]:
        html = fetch_html(INDEX_URL_TMPL.format(n=n))
        if not html:
            return set()
        return {
            "https://source.opennews.org" + m
            for m in POST_HREF_RE.findall(html)
        }

    # First pass: fetch pages in parallel but stop once we see a page with 0 URLs
    urls: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(fetch_page, n): n for n in range(1, max_pages + 1)}
        for fut in as_completed(futures):
            page_urls = fut.result()
            for u in page_urls:
                if u not in seen:
                    seen.add(u)
                    urls.append(u)
    return sorted(urls)


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=[],  # unused; URLs discovered via pagination
    # Source is a Jekyll/Hugo-style static site; the main article content
    # sits under <main> with an <article> wrapper.
    # Source is statically generated; the article body is under <main>.
    # The top-of-page metadata block (title/author/lead) is in
    # `.article-matter-front`; skip it by targeting `.article-matter-body`.
    article_selectors=[
        "main .article-matter-body", "main", "article", ".article", "#main",
    ],
    title_selectors=["h1.page-title-lead", "main h1", ".article-matter-front h1"],
    author_selectors=[".article-matter-byline a", ".article-matter-byline", ".byline a"],
    date_selectors=["time[datetime]", ".article-matter-date"],
    organization="Source / OpenNews",
    default_creators=[],
    tags=["source", "opennews", "newsroom"],
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 8) -> dict:
    print(f"[{SOURCE}] discovering URLs across paginated index...", flush=True)
    urls = _discover_urls(workers=workers)
    print(f"[{SOURCE}] found {len(urls)} article URLs", flush=True)
    return run_blog_ingest(CONFIG, urls, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
