"""Observable notebook ingest.

Observable notebooks embed their full state as JSON on the server-rendered
landing page (Next.js `__NEXT_DATA__`). We:

1. Discover notebook URLs from a curated seed:
   - /explore (trending/featured notebooks)
   - Known practitioner profile pages (@d3, @mbostock, @fil, ...)

2. For each notebook, parse the JSON to get `nodes` (cells). We concat
   markdown cells as prose and code cells as fenced code blocks. That
   gives a walkthrough-shaped document even when the rendered UI would
   show interactive widgets.

3. Skip notebooks with too little markdown (pure-code recipes aren't
   walkthroughs in the sense we care about).
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ..schema import Item
from ..storage import corpus_root
from ._common import fetch_html, slugify, soup
from ._fetch_html import save_raw_html

SOURCE = "observable"

# Curated seed: practitioners whose notebooks lean walkthrough/essay rather
# than utility. Skewed to people who write prose around their charts.
SEED_USERS = (
    "d3", "mbostock", "observablehq", "fil", "tomlarkworthy",
    "nkatz", "jashkenas", "sandra-becker", "pearmill", "veltman",
    "zachlieberman", "joewdavies", "spenczar", "enjalot",
    "yurivish", "bcardiff", "asg017", "randomfractals", "observablehq/featured",
)
SEED_PAGES = (
    "https://observablehq.com/explore",
    "https://observablehq.com/recommended",
)

_NOTEBOOK_PATH_RE = re.compile(r"/@([A-Za-z0-9_\-]+)/([A-Za-z0-9_\-]+)")
# Avoid /@user-only links (profile pages) and /@user/ without slug
_SKIP_SLUGS = {"notebooks", "collections", "about", "likes", "forks"}


def _discover_notebook_urls(workers: int = 6, max_per_user: int = 40) -> list[str]:
    """Collect notebook URLs from curated seed pages + user profiles.

    Observable profile pages render ~30-60 notebooks per profile as visible
    links. Good enough as a seed; a more systematic approach would use the
    auth'd API, which we can't hit without a token.
    """
    urls: set[str] = set()

    def discover(url: str) -> set[str]:
        html = fetch_html(url)
        if not html:
            return set()
        found: set[str] = set()
        for user, slug in _NOTEBOOK_PATH_RE.findall(html):
            if slug in _SKIP_SLUGS:
                continue
            found.add(f"https://observablehq.com/@{user}/{slug}")
        return found

    seeds = list(SEED_PAGES) + [f"https://observablehq.com/@{u}" for u in SEED_USERS]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(discover, u): u for u in seeds}
        for fut in as_completed(futures):
            seed = futures[fut]
            found = fut.result()
            print(f"  [observable] {seed[:60]}: {len(found)} notebook URLs",
                  flush=True)
            urls |= found
    return sorted(urls)


def _parse_notebook_json(html: str) -> dict | None:
    """Extract the Next.js page data blob. Contains the full notebook graph."""
    s = soup(html)
    for script in s.find_all("script"):
        t = script.string or ""
        if '"initialNotebook"' in t and t.lstrip().startswith("{"):
            try:
                return json.loads(t)
            except Exception:
                return None
    return None


def _md_text(html_fragment: str) -> str:
    """Observable md cells can contain inline HTML. Strip tags for corpus text."""
    s = BeautifulSoup(html_fragment or "", "lxml")
    return s.get_text(" ", strip=True)


def _nodes_to_body(nodes: list[dict]) -> tuple[str, int]:
    """Render cells into a walkthrough-shaped markdown body.

    Returns (body, md_char_count) so the caller can filter out
    low-prose notebooks.
    """
    parts: list[str] = []
    md_chars = 0
    for n in nodes:
        mode = n.get("mode")
        value = n.get("value") or ""
        if not value:
            continue
        if mode == "md":
            text = _md_text(value)
            if text:
                parts.append(text)
                md_chars += len(text)
        elif mode == "js":
            # Code cells are part of the walkthrough — they're the artifact.
            parts.append(f"```js\n{value.rstrip()}\n```")
        elif mode == "html":
            text = _md_text(value)
            if text:
                parts.append(text)
        # Skip `tex`, `fileAttachment`, unknown modes
    return "\n\n".join(parts).strip(), md_chars


def _url_to_item(url: str, *, min_md_chars: int = 300) -> Item | None:
    html = fetch_html(url)
    if not html:
        return None
    data = _parse_notebook_json(html)
    if not data:
        return None
    nb = data.get("props", {}).get("pageProps", {}).get("initialNotebook") or {}
    nodes = nb.get("nodes", []) or []
    if not nodes:
        return None
    title = nb.get("title") or nb.get("slug") or "Untitled"
    desc = (nb.get("description") or "").strip()
    body, md_chars = _nodes_to_body(nodes)
    if md_chars < min_md_chars:
        return None

    parsed = urlparse(url)
    # /@user/slug → id = user__slug so ids are globally unique on Observable
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) != 2 or not parts[0].startswith("@"):
        return None
    user = parts[0].lstrip("@")
    slug = parts[1]
    item_id = slugify(f"{user}-{slug}")

    # Prepend the description as the first paragraph if present and not
    # already reflected in md.
    if desc and desc not in body[:500]:
        body = desc + "\n\n" + body

    raw_path = save_raw_html(SOURCE, item_id, html)
    details = {
        "source_url": url,
        "raw_html_path": raw_path,
        "likes": nb.get("likes"),
        "forks": nb.get("forks"),
        "publish_level": nb.get("publish_level"),
        "categories": nb.get("categories", []),
    }
    if nb.get("published_at"):
        details["publication_date"] = nb["published_at"]

    return Item(
        id=item_id,
        source=SOURCE,
        type="process_note",
        title=title,
        url=url,
        creators=[user],
        organization="Observable",
        tags=["observable", "notebook"] + [
            t for t in (nb.get("categories") or []) if isinstance(t, str)
        ],
        details=details,
        body=body,
    )


def run(
    *,
    root: Path | None = None,
    limit: int | None = None,
    workers: int = 6,
) -> dict:
    out_root = root or corpus_root()
    odir = out_root / SOURCE
    if odir.exists():
        for p in odir.glob("*.md"):
            p.unlink()
        import shutil
        for sub in ("_raw", "_images"):
            d = out_root / SOURCE / sub
            if d.exists():
                shutil.rmtree(d)

    print(f"[{SOURCE}] discovering notebook URLs from curated seed...", flush=True)
    urls = _discover_notebook_urls(workers=workers)
    print(f"[{SOURCE}] {len(urls)} unique notebook URLs", flush=True)
    if limit:
        urls = urls[:limit]

    written = 0
    skipped = 0
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_url_to_item, u): u for u in urls}
        for fut in as_completed(futures):
            try:
                item = fut.result()
            except Exception as e:
                print(f"  extract failed for {futures[fut]}: {e}", flush=True)
                item = None
            if item:
                item.write(out_root)
                written += 1
            else:
                skipped += 1
            done += 1
            if done % 25 == 0:
                print(f"  [observable] {done}/{len(urls)} "
                      f"(written={written} skipped={skipped})", flush=True)

    return {"source": SOURCE, "urls": len(urls),
            "written": written, "skipped": skipped}


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(run(limit=10), indent=2))
