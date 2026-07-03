"""Nightingale ingest.

nightingaledvs.com — the Data Visualization Society's online magazine.
Long-form interviews, essays, and process posts from practitioners and
researchers. WordPress, Cloudflare-fronted (so the sitemap fetch uses
fetch's strategy chain via `_fetch_sitemap_xml`).
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from ._sitemap_blog import BlogConfig, run_sitemap_blog

SOURCE = "nightingale"

_IMG_EXT_RE = re.compile(r"\.(png|jpg|jpeg|gif|webp|svg|pdf)(\?.*)?$", re.IGNORECASE)
_NON_POST_PATHS = {
    "", "about", "contact", "membership", "submissions", "privacy-policy",
    "jobs", "events", "newsletter",
}


def _is_post(url: str) -> bool:
    """Nightingale posts live at /<slug>/ — filter out attachments and site pages."""
    p = urlparse(url)
    if p.netloc != "nightingaledvs.com" and not p.netloc.endswith(".nightingaledvs.com"):
        return False
    if _IMG_EXT_RE.search(p.path):
        return False
    if "/wp-content/" in p.path:
        return False
    parts = [x for x in p.path.split("/") if x]
    if len(parts) != 1:
        return False
    if parts[0] in _NON_POST_PATHS:
        return False
    return True


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=["https://nightingaledvs.com/wp-sitemap.xml"],
    url_filter=_is_post,
    # Nightingale's <article> is just the post-card wrapper; the actual
    # body is under .entry-content (outside <article> on many templates).
    article_selectors=[
        ".entry-content", ".elementor-widget-theme-post-content",
        "main article", "article", "main",
    ],
    title_selectors=["h1.entry-title", "article h1", "h1"],
    author_selectors=[".entry-meta .author a", ".author-name", ".byline a"],
    date_selectors=["time[datetime]", ".entry-date", ".posted-on time"],
    organization="Nightingale (Data Visualization Society)",
    default_creators=[],
    tags=["nightingale", "dvs", "magazine"],
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 8) -> dict:
    return run_sitemap_blog(CONFIG, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
