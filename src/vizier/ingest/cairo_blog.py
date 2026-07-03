"""Alberto Cairo blog ingest (thefunctionalart.com).

Cairo's blog is hosted on Blogger (thefunctionalart.blogspot.com). The
custom domain `www.thefunctionalart.com` is a thin redirect; the canonical
feed + sitemap live on the blogspot.com origin. We crawl the Blogger
sitemap (served as Atom) and filter to individual post URLs.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from ._sitemap_blog import BlogConfig, run_sitemap_blog

SOURCE = "cairo-blog"

# Blogger posts look like /YYYY/MM/<slug>.html
_POST_RE = re.compile(r"^/\d{4}/\d{2}/[^/]+\.html$")


def _is_post(url: str) -> bool:
    return bool(_POST_RE.match(urlparse(url).path))


CONFIG = BlogConfig(
    source=SOURCE,
    sitemap_urls=[
        "https://thefunctionalart.blogspot.com/sitemap.xml",
    ],
    url_filter=_is_post,
    # Blogger exposes the post body inside .post-body / .entry-content
    article_selectors=[
        ".post-body", ".entry-content", "article .post", "article", "main",
    ],
    title_selectors=[".post-title", "h1.entry-title", "h3.post-title", "h1"],
    author_selectors=[".post-author", ".author", "[rel=author]"],
    date_selectors=[".post-timestamp abbr", ".published", "abbr.published", "time[datetime]"],
    organization="The Functional Art",
    default_creators=["Alberto Cairo"],
    tags=["cairo", "functional-art", "critique"],
    # Cairo writes short blogger posts; drop the threshold so walkthroughs
    # aren't filtered as "too short".
    min_body_chars=150,
)


def run(*, root: Path | None = None, limit: int | None = None, workers: int = 6) -> dict:
    return run_sitemap_blog(CONFIG, root=root, limit=limit, workers=workers)


if __name__ == "__main__":
    import json
    print(json.dumps(run(limit=3), indent=2))
