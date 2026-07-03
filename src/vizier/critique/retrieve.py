"""Corpus retrieval for informed critique.

First-pass retrieval is intentionally simple:

- Always include *all* weaver principles (38 items, ~10K tokens) —
  they are vizier's lived-through rubric; excluding any would mean vizier
  can't recall its own principles.
- Always include named rubrics (Cairo 5-pillars, FT Visual Vocabulary).
- For each other source, score items by (a) tag overlap with the case,
  and (b) keyword hits in title + body against terms extracted from
  the case tags + artifact_title + first paragraph. Take top-K per
  source.

Why this over embeddings: zero infrastructure to maintain, fully
deterministic given a corpus_hash, and good enough for ~2K items.
Swap in embeddings later if signal demands it.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from ..ingest._common import slugify
from ..schema import Item
from ..storage import iter_items
from . import embed as E

# Per-source retrieval caps for tag-matched items
TOP_K = {
    "sigma": 6,
    "kantar": 4,
    "junkcharts": 8,  # highest-signal for critique voice calibration
}

# Sources always included in full
ALWAYS_INCLUDE = ("weaver", "ft-vocab", "rubrics")

# Minimum score a non-weaver item must clear to be included. Tuned so that
# pure-body keyword matches (which accumulate fractional scores) don't
# qualify — an item must have a tag overlap, a title hit, or a tier bonus
# combined with body signal.
MIN_SCORE = {
    "sigma": 3.0,
    "kantar": 3.0,
    "junkcharts": 2.0,  # lower bar since junkcharts items have no tags
}

# Stopwords filtered when extracting keywords from case text. Includes
# viz-domain words that match everywhere and carry no discriminative
# signal (visual, data, story, news, etc.).
_STOPWORDS = set("""
a an and are as at be but by for from has have i in is it its of on or that
the this to was were will with you your not they their them there these those
above below which what how when where why who whose all any some each such
one two three
audience reader readers shown see look specific specifically using via about
also across along among around because before between both during if into many
more most much only other our own over same than through under where while
would make made makes making
data graphic chart charts graph graphs visualization visualizations viz piece
pieces project projects story stories news author authors credit credits title
year years interactive static image images figure figures plot plots form forms
encoding encodings layout layouts design designer designers dataset datasets
article articles work works published publishing published publisher readers
analysis value values
""".split())

_WORD_RE = re.compile(r"[a-z][a-z0-9\-]{2,}", re.IGNORECASE)


def _keywords(text: str, *, limit: int = 40) -> list[str]:
    """Lowercased, stopworded content words — rough keyword set."""
    seen: set[str] = set()
    out: list[str] = []
    for w in _WORD_RE.findall(text):
        lw = w.lower()
        if lw in _STOPWORDS or lw in seen:
            continue
        seen.add(lw)
        out.append(lw)
        if len(out) >= limit:
            break
    return out


@dataclass
class ScoredItem:
    item: Item
    score: float
    why: str  # short human-readable reason


def _word_set(text: str) -> set[str]:
    """Tokenize into a set of lowercased content words (whole-word only)."""
    return {w.lower() for w in _WORD_RE.findall(text)}


def _retrieve_keyword(
    case: dict, excluded: set[str], *, root: Path | None
) -> tuple[dict[str, list[ScoredItem]], list[str]]:
    case_tags, case_kws = _case_signal(case)
    scored_by_source: dict[str, list[ScoredItem]] = {}
    excluded_hits: list[str] = []
    for source, k in TOP_K.items():
        threshold = MIN_SCORE.get(source, 0.0)
        pool: list[ScoredItem] = []
        for item in iter_items(source=source, root=root):
            item_urls = {
                (item.url or "").rstrip("/"),
                (item.artifact_url or "").rstrip("/"),
            }
            if (item_urls & excluded) or _title_matches_case(case, item):
                excluded_hits.append(f"{source}/{item.id}")
                continue
            s, why = _score(case_tags, case_kws, item)
            if s >= threshold:
                pool.append(ScoredItem(item=item, score=s, why=why))
        pool.sort(key=lambda si: -si.score)
        scored_by_source[source] = pool[:k]
    return scored_by_source, excluded_hits


# Hybrid thresholds: minimum cosine similarity below which an item is
# discarded regardless of tag or tier bonuses. Tuned so that most
# picks are topically related, not just "close in embedding space."
_HYBRID_MIN_SIM = {
    "sigma": 0.30,
    "kantar": 0.30,
    "junkcharts": 0.30,
}


def _retrieve_hybrid(
    case: dict,
    excluded: set[str],
) -> tuple[dict[str, list[ScoredItem]], list[str]]:
    """Score by cosine similarity with tag + tier bonuses on top."""
    case_tags, _case_kws = _case_signal(case)
    case_text = (
        f"{case.get('artifact_title','')}\n\n"
        f"{case.get('body','')[:3000]}\n\n"
        f"Tags: {', '.join(sorted(case_tags))}"
    )
    case_vec = E.embed_query(case_text)

    tier_bonus = {
        "gold": 0.06,
        "winner": 0.04,
        "silver": 0.04,
        "bronze": 0.03,
        "citation": 0.02,
        "honorable-mention": 0.02,
    }

    scored_by_source: dict[str, list[ScoredItem]] = {}
    excluded_hits: list[str] = []
    for source, k in TOP_K.items():
        index = E.build_source_index(source)
        min_sim = _HYBRID_MIN_SIM.get(source, 0.25)
        pool: list[ScoredItem] = []
        for emb, sim in E.iter_scores(case_vec, index):
            item = emb.item
            item_urls = {
                (item.url or "").rstrip("/"),
                (item.artifact_url or "").rstrip("/"),
            }
            if (item_urls & excluded) or _title_matches_case(case, item):
                excluded_hits.append(f"{source}/{item.id}")
                continue
            if sim < min_sim:
                continue
            score = sim
            reasons = [f"sim={sim:.2f}"]
            item_tags = {t.lower() for t in (item.tags or [])}
            tag_hits = case_tags & item_tags
            if tag_hits:
                score += 0.08 * len(tag_hits)
                reasons.append(f"tags={sorted(tag_hits)}")
            if item.tier in tier_bonus:
                score += tier_bonus[item.tier]
                reasons.append(f"tier={item.tier}")
            pool.append(ScoredItem(item=item, score=score, why="; ".join(reasons)))
        pool.sort(key=lambda si: -si.score)
        scored_by_source[source] = pool[:k]
    return scored_by_source, excluded_hits


def _score(case_tags: set[str], case_kws: set[str], item: Item) -> tuple[float, str]:
    """Score an item against case tags + keywords. Returns (score, reason).

    All keyword matches are whole-word (via tokenization) to avoid
    spurious hits like "ring" matching "tearing". Body-only matches
    contribute weakly — we want tag or title signal to carry the
    retrieval.
    """
    reasons: list[str] = []
    score = 0.0

    # Tag overlap — highest signal when it occurs
    item_tags = {t.lower() for t in (item.tags or [])}
    tag_hits = case_tags & item_tags
    if tag_hits:
        score += 5.0 * len(tag_hits)
        reasons.append(f"tags={sorted(tag_hits)}")

    # Title keyword match (whole-word)
    title_words = _word_set(item.title or "")
    title_hits = case_kws & title_words
    if title_hits:
        # Require ≥2 hits to score — one-word coincidences are mostly noise.
        if len(title_hits) >= 2:
            score += 2.0 * len(title_hits)
            reasons.append(f"title~{sorted(title_hits)[:3]}")
        else:
            score += 0.5
            reasons.append(f"title1={next(iter(title_hits))}")

    # Body keyword match — require multiple distinct hits to register
    body_words = _word_set((item.body or "")[:6000])
    body_hits = case_kws & body_words
    if len(body_hits) >= 3:
        # Cap at 8 so a long body can't dominate a genuine tag match
        score += min(len(body_hits), 8) * 0.25
        reasons.append(f"body_kws={len(body_hits)}")

    # Tier bonus — only if the item already has other signal
    tier_bonus = {
        "gold": 1.0,
        "winner": 0.7,
        "silver": 0.5,
        "bronze": 0.3,
        "citation": 0.2,
        "honorable-mention": 0.2,
    }.get(item.tier or "", 0.0)
    if score > 0:
        score += tier_bonus

    return score, "; ".join(reasons) if reasons else "tier-bonus"


def _case_signal(case: dict) -> tuple[set[str], set[str]]:
    """Return (tags, keywords) for the case."""
    tags = {t.lower() for t in (case.get("tags") or [])}
    kws = set(
        _keywords(
            f"{case.get('artifact_title','')}\n{case.get('body','')[:2000]}",
            limit=60,
        )
    )
    # Expand with tag tokens as keywords too
    for t in tags:
        for part in re.split(r"[-_\s]", t):
            if part and len(part) > 2:
                kws.add(part.lower())
    return tags, kws


def _excluded_urls(case: dict) -> set[str]:
    """URLs we must exclude from retrieval to keep eval honest.

    When the case's ground truth lives in the corpus (a Sigma/Kantar/
    JunkCharts item whose `url` or `artifact_url` matches the case),
    including that exact item as retrieved context means the informed
    critique is quoting the ground truth rather than reasoning about
    similar prior art. Drop those items before scoring.
    """
    targets: set[str] = set()
    for key in ("artifact_url", "url"):
        v = (case.get(key) or "").strip().rstrip("/")
        if v:
            targets.add(v)
    return targets


def _title_matches_case(case: dict, item: Item) -> bool:
    """True when the item describes the same artifact as the case.

    URL matching handles most cases, but some corpus entries reference
    an artifact via a news-post URL (e.g., Kantar special-award
    items) with `artifact_url=None`. Fall back to slug similarity:
    if the case's artifact title is a substring of the item title
    (or vice-versa, for the short direction), treat them as the same.
    """
    case_slug = slugify(case.get("artifact_title", ""))
    if not case_slug or len(case_slug) < 12:
        return False
    item_slug = slugify(item.title or "")
    if not item_slug or len(item_slug) < 12:
        return False
    return case_slug in item_slug or item_slug in case_slug


def retrieve(case: dict, *, root: Path | None = None, strategy: str = "hybrid") -> dict:
    """Retrieve corpus items for one case.

    `strategy`:
      - "keyword" — tag overlap + whole-word keyword match (original).
      - "hybrid"  — embeddings (cosine similarity) combined with tag
                    and tier bonuses. Requires OPENAI_API_KEY.

    Returns a dict with:
      - `always`: list[Item] — weaver + rubrics, in full
      - `scored`: dict[str, list[ScoredItem]] — top-K per other source
      - `retrieval_summary`: dict for logging
    """
    always: list[Item] = []
    for src in ALWAYS_INCLUDE:
        always.extend(iter_items(source=src, root=root))

    excluded = _excluded_urls(case)

    if strategy == "hybrid":
        scored_by_source, excluded_hits = _retrieve_hybrid(case, excluded)
    elif strategy == "keyword":
        scored_by_source, excluded_hits = _retrieve_keyword(case, excluded, root=root)
    else:
        raise ValueError(f"unknown retrieval strategy: {strategy!r}")

    case_tags, case_kws = _case_signal(case)

    summary = {
        "strategy": strategy,
        "case_tags": sorted(case_tags),
        "case_keywords": sorted(case_kws)[:20],
        "always_count": len(always),
        "excluded_ground_truth_items": excluded_hits,
        "scored_counts": {
            src: len(items) for src, items in scored_by_source.items()
        },
        "picks": {
            src: [
                {"id": si.item.id, "title": si.item.title, "score": round(si.score, 2), "why": si.why}
                for si in items
            ]
            for src, items in scored_by_source.items()
        },
    }
    return {
        "always": always,
        "scored": scored_by_source,
        "retrieval_summary": summary,
    }


def format_for_prompt(retrieval: dict) -> str:
    """Render retrieval result as the context block for the informed prompt."""
    parts: list[str] = []

    # Group `always` items by source for readability
    always_by_src: dict[str, list[Item]] = {}
    for it in retrieval["always"]:
        always_by_src.setdefault(it.source, []).append(it)

    if "rubrics" in always_by_src:
        parts.append("## Rubrics (canonical evaluation axes)\n")
        for it in always_by_src["rubrics"]:
            parts.append(f"### {it.title}")
            for axis in it.axes or []:
                parts.append(f"- **{axis.get('name')}**: {axis.get('description')}")
            parts.append(it.body)
            parts.append("")

    if "ft-vocab" in always_by_src:
        parts.append("## FT Visual Vocabulary (chart-family → sub-type lookup)\n")
        for it in always_by_src["ft-vocab"]:
            for axis in it.axes or []:
                parts.append(f"### {axis.get('name')}")
                parts.append(axis.get("description", ""))
                types = axis.get("chart_types") or []
                if types:
                    parts.append("Sub-types: " + ", ".join(types))
                parts.append("")

    if "weaver" in always_by_src:
        parts.append("## Internal weaver principles (lived rubric)\n")
        # Group by stage to keep it scannable
        by_stage: dict[str, list[Item]] = {}
        for it in always_by_src["weaver"]:
            stage = (it.details or {}).get("stage") or it.type
            by_stage.setdefault(stage, []).append(it)
        for stage in [
            "Cross-cutting meta-principles", "Explore", "Frame", "Ingest",
            "Sketch", "Build", "Narrate", "Critique", "Ship", "Retrospect",
            "process_note",
        ]:
            if stage not in by_stage:
                continue
            parts.append(f"### Stage: {stage}")
            for it in by_stage[stage]:
                parts.append(f"**{it.title}**")
                parts.append(it.body)
                parts.append("")

    # Scored (per source)
    for src, picks in retrieval["scored"].items():
        if not picks:
            continue
        parts.append(f"## Retrieved from `{src}`\n")
        for si in picks:
            it = si.item
            header = f"### {it.title}"
            if it.tier:
                header += f"  (tier: {it.tier})"
            if it.year:
                header += f"  — {it.year}"
            parts.append(header)
            if it.organization or it.country:
                parts.append(f"_{it.organization or ''}{' · ' + it.country if it.country else ''}_")
            if it.artifact_url:
                parts.append(f"Artifact: {it.artifact_url}")
            parts.append(it.body)
            parts.append("")

    return "\n".join(parts)


def token_estimate(text: str) -> int:
    """Very rough token count (4 chars ≈ 1 token)."""
    return len(text) // 4
