"""Shared ingest helpers for HTML + image storage.

Used by practitioner-walkthrough sources (Source, Eagereyes, etc.) that
store richer content alongside the markdown record:

    corpus/<source>/
      <item-id>.md             # primary record; frontmatter references the rest
      _raw/<item-id>.html      # raw HTML snapshot (gitignored)
      _images/<item-id>/       # fetched images (gitignored)
        <n>-<slug>.<ext>

The markdown's frontmatter carries `raw_html_path`, `images` (list of
{path, src_url, alt, caption}), and `source_url` so the rich content
is discoverable from any reader of the corpus.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import Tag

from ..storage import corpus_root
from ._common import fetch_html as _fetch_html_cached, slugify


_IMG_EXT_RE = re.compile(r"\.(png|jpg|jpeg|gif|webp|svg)(\?.*)?$", re.IGNORECASE)


@dataclass
class FetchedImage:
    src_url: str
    local_path: str        # relative to the corpus root
    alt: str = ""
    caption: str = ""
    bytes_size: int = 0


@dataclass
class RichFetch:
    """A fetched-and-extracted item ready to write to corpus.

    `body_md` is the cleaned markdown projection of the article.
    `raw_html_path` and `images` are optional rich-storage artifacts.
    """

    source_url: str
    title: str
    body_md: str
    raw_html_path: str | None = None
    images: list[FetchedImage] = field(default_factory=list)
    author: str | None = None
    publication_date: str | None = None
    meta: dict = field(default_factory=dict)


def _raw_dir(source: str) -> Path:
    return corpus_root() / source / "_raw"


def _image_dir(source: str, item_id: str) -> Path:
    return corpus_root() / source / "_images" / item_id


def save_raw_html(source: str, item_id: str, html: str) -> str:
    """Write the raw HTML snapshot and return the path relative to corpus root."""
    path = _raw_dir(source) / f"{item_id}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path.relative_to(corpus_root()))


def _ext_from_url(url: str, fallback: str = ".png") -> str:
    parsed = urlparse(url)
    m = _IMG_EXT_RE.search(parsed.path)
    if m:
        return "." + m.group(1).lower()
    return fallback


def _safe_name(n: int, alt_or_src: str) -> str:
    # Hash+slug keeps filenames stable per image URL
    h = hashlib.sha1(alt_or_src.encode("utf-8", errors="replace")).hexdigest()[:6]
    slug = slugify(alt_or_src, maxlen=40) or "img"
    return f"{n:03d}-{h}-{slug}"


def _img_tags_in_article(article: Tag) -> list[Tag]:
    imgs: list[Tag] = []
    for img in article.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if not src:
            continue
        # Skip tracking pixels, tiny logos, and site-chrome icons by size hint
        w = img.get("width")
        if w and w.isdigit() and int(w) < 80:
            continue
        imgs.append(img)
    return imgs


def fetch_images(
    source: str,
    item_id: str,
    article: Tag,
    base_url: str,
    *,
    client: httpx.Client | None = None,
    max_images: int = 20,
    min_bytes: int = 2048,
) -> list[FetchedImage]:
    """Download every <img> under `article`, dedup by src, return records.

    Enforces a max count and a min byte threshold to filter spacers.
    Images land under `corpus/<source>/_images/<item_id>/`.
    """
    out: list[FetchedImage] = []
    seen_urls: set[str] = set()
    own_client = client is None
    if own_client:
        client = httpx.Client(timeout=20, follow_redirects=True,
                              headers={"User-Agent": "vizier/0.1 (+ingest)"})
    try:
        dest_dir = _image_dir(source, item_id)
        imgs = _img_tags_in_article(article)
        for n, img in enumerate(imgs):
            if len(out) >= max_images:
                break
            src = img.get("src") or img.get("data-src") or ""
            if not src:
                continue
            abs_url = urljoin(base_url, src)
            if abs_url in seen_urls:
                continue
            seen_urls.add(abs_url)
            try:
                r = client.get(abs_url)
                if r.status_code != 200 or len(r.content) < min_bytes:
                    continue
            except Exception:
                continue
            ext = _ext_from_url(abs_url, fallback=".png")
            name = _safe_name(n, img.get("alt") or abs_url) + ext
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / name).write_bytes(r.content)
            local_path = str((dest_dir / name).relative_to(corpus_root()))
            out.append(FetchedImage(
                src_url=abs_url,
                local_path=local_path,
                alt=(img.get("alt") or "").strip(),
                caption=_nearby_caption(img),
                bytes_size=len(r.content),
            ))
    finally:
        if own_client:
            client.close()
    return out


def _nearby_caption(img: Tag) -> str:
    """Heuristic caption lookup — look at <figcaption>, title attr, or next sibling."""
    fig = img.find_parent("figure")
    if fig is not None:
        cap = fig.find("figcaption")
        if cap:
            return cap.get_text(" ", strip=True)
    title = img.get("title") or ""
    return title.strip()


def html_to_markdown(article: Tag) -> str:
    """Cheap markdown projection of an article <article>/<main>-ish element.

    We keep structure (headings, paragraphs, lists, blockquotes, images,
    links) and drop the rest. Falls back to `<br>`-split plaintext when
    the article uses Blogger-style inline HTML (no <p>/<h*> tags).

    A proper html2markdown library would be richer but this is sufficient
    for corpus ingest.
    """
    parts: list[str] = []
    for el in article.find_all(
        ["h1", "h2", "h3", "h4", "h5", "p", "ul", "ol", "li",
         "blockquote", "figure", "pre", "img", "a", "hr"],
        recursive=True,
    ):
        # Avoid double-emitting when parent already captured children
        if el.find_parent(["li", "blockquote"]) and el.name not in ("li", "blockquote"):
            continue
        name = el.name
        if name == "h1":
            parts.append(f"# {el.get_text(' ', strip=True)}")
        elif name == "h2":
            parts.append(f"## {el.get_text(' ', strip=True)}")
        elif name == "h3":
            parts.append(f"### {el.get_text(' ', strip=True)}")
        elif name == "h4":
            parts.append(f"#### {el.get_text(' ', strip=True)}")
        elif name == "p":
            t = el.get_text(" ", strip=True)
            if t:
                parts.append(t)
        elif name in ("ul", "ol"):
            items = [li.get_text(" ", strip=True) for li in el.find_all("li", recursive=False)]
            for i, it in enumerate(items, 1):
                prefix = "- " if name == "ul" else f"{i}. "
                if it:
                    parts.append(prefix + it)
        elif name == "blockquote":
            t = el.get_text(" ", strip=True)
            if t:
                parts.append("> " + t.replace("\n", "\n> "))
        elif name == "pre":
            code = el.get_text("\n", strip=False).rstrip()
            if code:
                parts.append(f"```\n{code}\n```")
        elif name == "figure":
            cap = el.find("figcaption")
            if cap:
                parts.append(f"_Figure: {cap.get_text(' ', strip=True)}_")
        elif name == "hr":
            parts.append("---")

    md = "\n\n".join(parts).strip()

    # Blogger-style fallback: posts using <div> + <br> without structured
    # tags produce empty markdown above. Split on double-<br> (or fall back
    # to raw text) so the content survives.
    raw_text_len = len(article.get_text(" ", strip=True))
    if len(md) < max(200, raw_text_len // 3) and raw_text_len > 200:
        import copy
        clone = copy.copy(article)
        for br in clone.find_all("br"):
            br.replace_with("\n")
        chunks = [
            c.strip() for c in clone.get_text().split("\n\n")
            if c.strip()
        ]
        # Collapse runs of single-\n (within a paragraph) to spaces
        normalized = [
            " ".join(p.split()) for p in chunks if p.strip()
        ]
        if normalized:
            md = "\n\n".join(normalized)
    return md


def fetch_item(url: str, *, cache: bool = True) -> str | None:
    """Thin wrapper around `_common.fetch_html` so every ingester routes through the same cache."""
    return _fetch_html_cached(url, cache=cache)
