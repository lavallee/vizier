"""Shared ingest utilities.

- `slugify`: stable source-local slug from a title
- `fetch_html`: pluggable cached fetch (see below)
- `soup`: BeautifulSoup with lxml or html.parser fallback

Fetching is pluggable so ingest works with or without a proprietary fetcher.
Resolution order in `fetch_html`:
  1. a custom `FETCHER` callable, if you set one;
  2. the `fetch` package (rich strategy chain + on-disk cache), if installed;
  3. a plain httpx GET with a browser UA (the bundled default).
Point (2) is how the maintainers wire in a proprietary fetcher; (3) is what every
open-source user gets out of the box.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Callable

from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parents[3] / ".fetch-cache"
_UA = "vizier/0.1 (+https://github.com/lavallee/vizier; dataviz corpus ingest)"

# Set to a callable(url) -> html|None to override the default fetch entirely.
FETCHER: Callable[[str], str | None] | None = None


def _httpx_fetch(url: str) -> str | None:
    import httpx
    try:
        r = httpx.get(url, headers={"User-Agent": _UA}, timeout=30.0, follow_redirects=True)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def _fetch_fetch(url: str, cache_dir: Path | None) -> str | None:
    try:
        import fetch  # optional — proprietary fetcher, not required for OSS use
    except ImportError:
        return None
    try:
        r = fetch.fetch(url, cache=cache_dir) if cache_dir else fetch.fetch(url)
        return r.html or None
    except Exception:
        return None


def fetch_html(url: str, *, cache: bool = True) -> str | None:
    """Return raw HTML for a URL, or None on failure. Pluggable — see module docstring."""
    if FETCHER is not None:
        return FETCHER(url)
    html = _fetch_fetch(url, CACHE_DIR if cache else None)
    return html if html is not None else _httpx_fetch(url)


def soup(html: str) -> BeautifulSoup:
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


_slug_re = re.compile(r"[^a-z0-9]+")


def slugify(text: str, *, maxlen: int = 80) -> str:
    """Stable slug: ascii-lower, non-alnum to '-', collapsed, trimmed."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = _slug_re.sub("-", text).strip("-")
    if len(text) > maxlen:
        text = text[:maxlen].rstrip("-")
    return text or "untitled"
