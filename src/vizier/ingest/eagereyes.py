"""Eagereyes ingest.

Robert Kosara's eagereyes.org — deep, academic-practitioner hybrid
critiques and essays about specific visualizations, visualization
research, and visualization culture. 2006-present.

Sitemap-based; filter to /blog/ paths.
"""

from __future__ import annotations

from pathlib import Path

from ._sitemap_blog import BlogConfig, run_sitemap_blog

SOURCE = "eagereyes"


def _is_post(url: str) -> bool:
    # /blog/YYYY/<slug> — skip /blog/ index itself and /blog/YYYY/ archive
    if "/blog/" not in url:
        return False
    tail = url.rsplit("/", 1)[-1]
    if not tail:
        return False
    if tail.isdigit():  # year archive
        return False
    if tail in ("blog", ""):
        return False
    return True


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=["https://eagereyes.org/sitemap.xml"],
    url_filter=_is_post,
    # Eagereyes is custom-built (Eleventy-ish); the article tag is the post body
    article_selectors=["article", "main article", ".post", "main"],
    title_selectors=["h1.post-title", "article h1", "h1"],
    author_selectors=[".author", "[rel=author]"],
    date_selectors=["time[datetime]", ".pubdate"],
    organization="eagereyes",
    default_creators=["Robert Kosara"],
    tags=["eagereyes", "critique", "research"],
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 8) -> dict:
    return run_sitemap_blog(CONFIG, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
