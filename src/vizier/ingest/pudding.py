"""Pudding process-writeup ingest.

The Pudding doesn't publish a single hub page listing every `/process/`
article — we seed with a known list plus discovered URLs from /resources/
and the homepage, then BFS-expand one hop.

Each `/process/<slug>/` page is a practitioner writeup about craft:
scrollytelling techniques, pivoting stories, chart choices, etc. We
ingest each as a process_note item.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..schema import Item
from ..storage import corpus_root
from ._common import fetch_html, slugify, soup

SOURCE = "pudding"

SEED_URLS = [
    "https://pudding.cool/resources/",
    "https://pudding.cool/about",
    "https://pudding.cool/",
]
# Known slugs discovered from search — included so we don't depend on
# whether they happen to be linked from seeds.
KNOWN_SLUGS = (
    "how-to-make-dope-shit-part-1",
    "how-to-make-dope-shit-part-2",
    "how-to-make-dope-shit-part-3",
    "pivot-continue-down",
    "pudding-awards-2018",
    "speaker-rider",
)
PROCESS_RE = re.compile(r"https?://pudding\.cool/process/([a-z0-9-]+)/?")


def _discover_urls() -> set[str]:
    """Seed + 1-hop BFS of /process/ URLs across seed pages."""
    found: set[str] = {f"https://pudding.cool/process/{s}" for s in KNOWN_SLUGS}
    for seed in SEED_URLS:
        html = fetch_html(seed)
        if not html:
            continue
        for m in PROCESS_RE.finditer(html):
            found.add(m.group(0).rstrip("/"))
    # One-hop: each known process URL may link to siblings
    for url in list(found):
        html = fetch_html(url)
        if not html:
            continue
        for m in PROCESS_RE.finditer(html):
            found.add(m.group(0).rstrip("/"))
    return found


def _extract_article(html: str) -> tuple[str, str, str | None]:
    """Return (title, body_text, authors)."""
    s = soup(html)
    title_el = s.select_one("h1, .title, title")
    title = title_el.get_text(strip=True) if title_el else "Untitled"
    # Body: the main article content. Pudding uses various layouts; take
    # all <p> under main/article or fallback to .article / #content.
    container = s.select_one("article") or s.select_one("main") or s.select_one(".article") or s
    paragraphs = []
    for p in container.find_all(["p", "h2", "h3", "h4", "li"]):
        txt = p.get_text(" ", strip=True)
        if not txt or len(txt) < 3:
            continue
        if p.name in ("h2", "h3", "h4"):
            paragraphs.append("\n## " + txt + "\n")
        elif p.name == "li":
            paragraphs.append("- " + txt)
        else:
            paragraphs.append(txt)
    body = "\n\n".join(paragraphs).strip()

    author_el = s.select_one(".author, [rel=author], .byline")
    authors = author_el.get_text(" ", strip=True) if author_el else None
    return title, body, authors


def _url_to_item(url: str) -> Item | None:
    html = fetch_html(url)
    if not html:
        return None
    title, body, authors = _extract_article(html)
    if len(body) < 400:
        return None
    slug = url.rsplit("/", 1)[-1]
    return Item(
        id=slugify(f"process-{slug}"),
        source=SOURCE,
        type="process_note",
        title=title,
        url=url,
        creators=[authors] if authors else [],
        organization="The Pudding",
        tags=["process", "pudding"],
        body=body,
    )


def run(*, root: Path | None = None) -> dict[str, int]:
    out_root = root or corpus_root()
    pdir = out_root / SOURCE
    if pdir.exists():
        for p in pdir.glob("*.md"):
            p.unlink()
    urls = _discover_urls()
    written = 0
    for u in sorted(urls):
        item = _url_to_item(u)
        if item:
            item.write(out_root)
            written += 1
    return {"urls_found": len(urls), "items_written": written}


if __name__ == "__main__":
    print(run())
