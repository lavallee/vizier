"""Visualising Data ingest.

Andy Kirk's visualisingdata.com — "little of visualisation design",
practitioner interviews, and the long-running "best of the visualisation
web" series. WordPress, sitemap index at /sitemap_index.xml.

We crawl the post sitemaps (post-sitemap.xml, post-sitemap2.xml) and
ingest every individual post as a process_note.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from ._sitemap_blog import BlogConfig, run_sitemap_blog

SOURCE = "visualising-data"


def _is_post(url: str) -> bool:
    # Post permalinks look like /YYYY/MM/slug/ on visualisingdata.com
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) < 3:
        return False
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return False
    return True


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=["https://www.visualisingdata.com/sitemap_index.xml"],
    url_filter=_is_post,
    article_selectors=[
        # Visualising Data runs on Elementor; the post body lives in the
        # theme-post-content widget.
        ".elementor-widget-theme-post-content",
        "[data-elementor-type=single-post]",
        ".post",
        "article", "main",
    ],
    title_selectors=["h1.entry-title", "article h1", "h1"],
    author_selectors=[".author a", ".byline a", ".author-name", "[rel=author]"],
    date_selectors=["time[datetime]", ".entry-date", ".post-date"],
    organization="Visualising Data",
    default_creators=["Andy Kirk"],
    tags=["visualising-data", "practitioner"],
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 8) -> dict:
    return run_sitemap_blog(CONFIG, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
