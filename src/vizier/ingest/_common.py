"""Shared ingest utilities.

- `slugify`: stable source-local slug from a title
- `fetch_html`: pluggable cached fetch (see below)
- `soup`: BeautifulSoup with lxml or html.parser fallback

Fetching is pluggable so ingest works with or without an optional richer
fetcher. Resolution order in `fetch_html`:
  1. a custom `FETCHER` callable, if you set one;
  2. an optional richer fetcher (strategy chain + on-disk cache), if you point
     `VIZIER_FETCHER` at an importable module that exposes
     `fetch(url, cache=...) -> obj` with a `.html` attribute;
  3. a plain httpx GET with a browser UA (the bundled default).
Point (2) is the plug point for a heavier fetcher when one is available; (3) is
what every open-source user gets out of the box, with no extra dependencies.
"""

from __future__ import annotations

import importlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Callable

from bs4 import BeautifulSoup


CACHE_DIR = Path(__file__).resolve().parents[3] / ".fetch-cache"
_UA = "vizier/0.1 (+https://github.com/lavallee/vizier; dataviz corpus ingest)"

# Import path of an optional richer fetcher module (see module docstring). Unset
# by default — the bundled httpx fetch below covers the open-source path.
_FETCHER_ENV = "VIZIER_FETCHER"

# Set to a callable(url) -> html|None to override the default fetch entirely.
FETCHER: Callable[[str], str | None] | None = None


def _httpx_fetch(url: str) -> str | None:
    import httpx
    try:
        r = httpx.get(url, headers={"User-Agent": _UA}, timeout=30.0, follow_redirects=True)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def plugin_fetch(url: str, cache_dir: Path | None = None) -> str | None:
    """Try the optional richer fetcher named by `$VIZIER_FETCHER`, else None.

    The named module must expose `fetch(url, cache=...) -> obj` whose result has
    a `.html` attribute. Any import or runtime failure falls through to None so
    the caller can drop back to the bundled httpx fetch.
    """
    mod_name = os.environ.get(_FETCHER_ENV)
    if not mod_name:
        return None
    try:
        mod = importlib.import_module(mod_name)
    except ImportError:
        return None
    try:
        r = mod.fetch(url, cache=cache_dir) if cache_dir else mod.fetch(url)
        return r.html or None
    except Exception:
        return None


def fetch_html(url: str, *, cache: bool = True) -> str | None:
    """Return raw HTML for a URL, or None on failure. Pluggable — see module docstring."""
    if FETCHER is not None:
        return FETCHER(url)
    html = plugin_fetch(url, CACHE_DIR if cache else None)
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
