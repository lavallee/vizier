"""One-shot ad-hoc chart critique — `vizier critique <image>`.

Difference from `informed` (which runs against the evals/cases/ corpus):

- Takes an image file directly, no pre-built case required.
- Lighter retrieval: pulls the target pattern's `reading_checklist` +
  `common_mistakes` + `related_principles` + a few BM25-search hits.
- Returns structured markdown (or JSON) the user can read at the CLI.

v1 scope: PNG/JPG input only. SVG support and URL input deferred —
rasterizing SVG is nontrivial (headless chromium / cairosvg) and URL
fetching involves mime sniffing + page-to-image.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import somm
from dotenv import load_dotenv

from .. import vision as V
from ..analyze.findings import computed_color_findings
from ..db import query as Q

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


MODEL = "gemini-2.5-pro"
DEFAULT_PROVIDER: str | None = "gemini"
WORKLOAD = "critique_adhoc"
PROJECT = "vizier"

SYSTEM = """\
You are an information-design critic in the tradition of the Financial \
Times visual-journalism team, the NYT graphics desk, Alberto Cairo's \
Truthful Art framework, and the Junk Charts school of structural \
critique.

You'll be given:
1. A vision caption of the chart being critiqued.
2. Optional surrounding context (headline, deck, caption).
3. The chart's documented form (its reading checklist, common mistakes, \
related principles).
4. A few retrieved critique/prior-art snippets from the corpus.

Work in this order:
- **Form fit** — is this the right chart form for the reader's task? \
Cite the documented `when_to_use` / `when_not_to_use` in your judgment.
- **Reading checklist** — answer each checklist question against the \
image evidence. Say "can't tell from the image" when the caption is \
thin, don't invent.
- **Common mistakes** — flag any documented cosmetic/config traps that \
apply here.
- **Strengths** — be specific. What's this chart doing well?
- **Concerns & fixes** — 3–5 concrete, actionable improvements.

Be specific. Cite retrieved prior art by short title when a piece \
sharpens a point. If the caption is too thin to judge something, say \
so — don't paper over it.
"""


@dataclass
class AdhocCritique:
    """Result of one adhoc critique run."""

    critique: str
    pattern_id: str
    pattern_title: str
    caption_text: str
    retrieved: list[dict]
    computed: str | None = None
    meta: dict = field(default_factory=dict)


def _classify_pattern(caption_text: str, llm: somm.SommLLM) -> tuple[str, str]:
    """Ask the LLM to pick the best-matching chart pattern id.

    Returns (pattern_id, reasoning). If the model hedges or names
    something that isn't a known pattern, falls back to "unknown".
    """
    patterns = Q.list_patterns()
    menu = "\n".join(
        f"- {p['id']} — {p.get('title','')} [{', '.join(p.get('purpose_families') or [])}]"
        for p in patterns
    )
    prompt = (
        "Here is a vision-model description of a chart:\n\n"
        f"{caption_text}\n\n"
        "From this menu of documented chart patterns, which single "
        "pattern does it most closely match? Reply with two lines:\n"
        "PATTERN: <id-from-the-menu>\n"
        "REASON: <one sentence>\n\n"
        f"Menu:\n{menu}"
    )
    r = llm.generate(
        prompt=prompt,
        system="You identify chart patterns. Reply only in the requested two-line format.",
        workload=WORKLOAD,
        max_tokens=400,
        temperature=0.0,
    )
    text = (r.text or "").strip()
    pid = ""
    reason = ""
    for line in text.splitlines():
        if line.upper().startswith("PATTERN:"):
            pid = line.split(":", 1)[1].strip()
        elif line.upper().startswith("REASON:"):
            reason = line.split(":", 1)[1].strip()
    valid = {p["id"] for p in patterns}
    if pid not in valid:
        return "unknown", reason or text[:200]
    return pid, reason


def _related_snippets(pattern_id: str, k: int = 4) -> list[dict]:
    """Pull a handful of related corpus items to cite as prior art.

    Uses BM25 search for the pattern title + any tags. Kept small to
    keep prompt tokens in check.
    """
    pat = Q.get_pattern(pattern_id, transclude=False)
    if not pat:
        return []
    query_bits = [pat.get("title") or pattern_id]
    query_bits.extend(pat.get("tags") or [])
    query = " ".join(query_bits[:6])
    hits = Q.search(query, k=k, exclude_sources=["chart-forms"])
    return [
        {
            "key": h.key,
            "title": h.title,
            "source": h.source,
            "url": h.url,
            "snippet": (h.body or "")[:320].replace("\n", " "),
        }
        for h in hits
    ]


def _build_user_prompt(
    caption_text: str,
    context: str | None,
    pat: dict,
    snippets: list[dict],
    computed: str | None = None,
) -> str:
    parts = [
        "# Chart caption (from vision model)",
        caption_text.strip(),
    ]
    if context:
        parts.extend(["# Surrounding context", context.strip()])

    if computed:
        parts.append(
            "# Computed color findings (deterministic ground truth)\n"
            "_Measured from the chart's exact colors — correct by construction, not "
            "the vision model's guess. Fold any failures into your critique and cite "
            "the numbers._\n\n" + computed
        )

    parts.append(f"# Documented form: {pat.get('title', pat.get('id'))}")
    if pat.get("capsule"):
        parts.append(pat["capsule"].strip())
    if pat.get("when_to_use"):
        parts.append("**When to reach for it**\n" +
                     "\n".join(f"- {s}" for s in pat["when_to_use"]))
    if pat.get("when_not_to_use"):
        parts.append("**When not**\n" +
                     "\n".join(f"- {s}" for s in pat["when_not_to_use"]))
    if pat.get("reading_checklist"):
        parts.append("**Reading checklist**\n" +
                     "\n".join(f"- {s}" for s in pat["reading_checklist"]))
    if pat.get("common_mistakes"):
        parts.append("**Common mistakes**\n" +
                     "\n".join(f"- {s}" for s in pat["common_mistakes"]))

    if snippets:
        sn_lines = ["# Retrieved prior art / critique"]
        for s in snippets:
            url = f" ({s['url']})" if s.get("url") else ""
            sn_lines.append(f"- **{s['title']}**{url} · `{s['key']}`\n  > {s['snippet']}")
        parts.append("\n".join(sn_lines))

    parts.append(
        "# Your critique\n"
        "Follow the ordering from the system prompt. Cite retrieved "
        "prior art by short title when a piece sharpens a point."
    )
    return "\n\n".join(parts)


_IMAGE_MIMES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}
_SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _fetch_image_to_tmp(url: str) -> Path:
    """Download a direct image URL to a tempfile and return the path.

    Only direct image URLs — mime-checked. Page URLs (HTML) need
    a headless browser; we return a clear error pointing the user
    to download the image manually, for now.
    """
    import tempfile
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "vizier/adhoc-critique"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        ctype = (resp.headers.get("content-type") or "").split(";")[0].strip().lower()
        if ctype not in _IMAGE_MIMES:
            raise ValueError(
                f"URL served {ctype or 'unknown'} — vizier critique needs a direct image URL. "
                f"For an HTML page, download the chart image manually (right-click → save) "
                f"and pass the local path instead."
            )
        data = resp.read()
    suffix = _IMAGE_MIMES[ctype]
    fd = tempfile.NamedTemporaryFile(prefix="vizier-critique-", suffix=suffix, delete=False)
    fd.write(data)
    fd.close()
    return Path(fd.name)


def _resolve_input(image_or_url: str | Path) -> Path:
    """Accept a local path or http(s) URL; return a local path."""
    s = str(image_or_url)
    if s.startswith(("http://", "https://")):
        return _fetch_image_to_tmp(s)
    p = Path(s).resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def critique(
    image_path: str | Path,
    *,
    pattern_id: str | None = None,
    context: str | None = None,
    palette: str | None = None,
    model: str = MODEL,
    provider: str | None = DEFAULT_PROVIDER,
    vision_backend: str = V.DEFAULT_BACKEND,
    snippets_k: int = 4,
) -> AdhocCritique:
    """One-shot critique of a chart image.

    `image_path` may be a local file path or a direct http(s) image
    URL (not an HTML page — download that manually). If `pattern_id`
    is omitted, runs a quick classifier pass to pick the closest
    documented pattern.
    """
    img = _resolve_input(image_path)
    if img.suffix.lower() not in _SUPPORTED_SUFFIXES:
        raise ValueError(
            f"Unsupported image format: {img.suffix}. "
            "v1 accepts raster images (.png/.jpg/.jpeg/.webp). "
            "Convert SVGs with `rsvg-convert` or `cairosvg` first."
        )

    cap = V.caption(img, backend=vision_backend)
    llm = somm.SommLLM(project=PROJECT)

    if not pattern_id:
        pattern_id, _ = _classify_pattern(cap.text, llm)

    pat = Q.get_pattern(pattern_id, transclude=True) if pattern_id != "unknown" else None
    if pat is None:
        # Fall back to a minimal shell so the critique still runs.
        pat = {"id": "unknown", "title": "Unclassified chart form"}

    snippets = _related_snippets(pattern_id, k=snippets_k) if pat.get("id") != "unknown" else []

    computed = computed_color_findings(palette=palette) if palette else None
    user_prompt = _build_user_prompt(cap.text, context, pat, snippets, computed=computed)
    result = llm.generate(
        prompt=user_prompt,
        system=SYSTEM,
        workload=WORKLOAD,
        max_tokens=6000,
        temperature=0.3,
        model=model,
        provider=provider,
    )
    meta: dict[str, Any] = {
        "call_id": result.call_id,
        "provider": result.provider,
        "model": result.model,
        "tokens_in": result.tokens_in,
        "tokens_out": result.tokens_out,
        "cost_usd": result.cost_usd,
        "outcome": getattr(result.outcome, "value", str(result.outcome)),
        "vision": {
            "backend": cap.backend,
            "model": cap.model,
            "cached": cap.cached,
        },
    }
    return AdhocCritique(
        critique=(result.text or "").strip(),
        pattern_id=pat.get("id") or pattern_id,
        pattern_title=pat.get("title", ""),
        caption_text=cap.text,
        retrieved=snippets,
        computed=computed,
        meta=meta,
    )


def as_markdown(r: AdhocCritique) -> str:
    """Render the critique as a readable markdown blob."""
    lines = [
        f"# Critique: {r.pattern_title or r.pattern_id}",
        "",
        f"*Pattern match: `{r.pattern_id}`. "
        f"Vision backend: `{r.meta.get('vision',{}).get('backend','?')}`.*",
        "",
        "## Vision caption",
        "",
        r.caption_text,
        "",
    ]
    if r.computed:
        lines.extend([r.computed, ""])
    lines.extend([
        "## Critique",
        "",
        r.critique,
    ])
    if r.retrieved:
        lines.extend(["", "## Retrieved prior art (cited inline above)", ""])
        for s in r.retrieved:
            url = f" — {s['url']}" if s.get("url") else ""
            lines.append(f"- **{s['title']}**{url} · `{s['key']}`")
    return "\n".join(lines)


def as_json(r: AdhocCritique) -> str:
    return json.dumps(
        {
            "pattern_id": r.pattern_id,
            "pattern_title": r.pattern_title,
            "caption": r.caption_text,
            "computed": r.computed,
            "critique": r.critique,
            "retrieved": r.retrieved,
            "meta": r.meta,
        },
        indent=2,
        ensure_ascii=False,
    )
