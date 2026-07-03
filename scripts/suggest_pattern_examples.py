"""Suggest corpus items as canonical examples for each chart_pattern.

Strategy per pattern:
  1. Semantic (find_similar) query against the pattern's capsule,
     excluding the chart-forms source itself and meta sources.
  2. FTS (keyword) query for the pattern title as a fallback / complement.
  3. Merge, dedup, surface top-N with source distribution info.

Output is a text report that a human (or me) curates before adding
canonical_examples[] entries to the pattern markdown.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vizier.db import query as Q  # noqa: E402


EXCLUDE_SOURCES = ["chart-forms", "weaver", "rubrics", "ft-vocab"]

PATTERN_KEYWORDS = {
    # Additional keyword queries beyond the capsule, for patterns where
    # find_similar misses the on-the-nose matches.
    "sankey": ["sankey", "alluvial"],
    "parallel-sets": ["parallel sets", "parallel coordinates", "alluvial"],
    "stacked-bar": ["stacked bar", "100% bar"],
    "stacked-area": ["stacked area", "streamgraph"],
    "bump-chart": ["bump chart", "rank chart"],
    "slope-chart": ["slope chart", "slope graph"],
    "flow-map": ["flow map", "migration map", "trade map"],
    "line-chart": ["line chart", "time series"],
    "small-multiples": ["small multiples", "trellis", "facet"],
    "scatterplot": ["scatterplot", "scatter plot", "bubble chart"],
    "connected-scatter": ["connected scatter", "trajectory"],
    "choropleth": ["choropleth", "election map"],
    "cartogram": ["cartogram"],
    "hex-bin-map": ["hex map", "hexagon map"],
    "proportional-symbol-map": ["proportional symbol", "bubble map"],
    "pie-chart": ["pie chart", "donut chart"],
    "bar-chart": ["bar chart"],
    "dot-plot": ["dot plot", "dumbbell"],
    "histogram": ["histogram"],
    "boxplot": ["boxplot", "box plot"],
    "violin": ["violin plot"],
    "heatmap": ["heatmap", "heat map"],
    "treemap": ["treemap"],
    "waffle-chart": ["waffle"],
    "chord-diagram": ["chord diagram"],
    "diverging-bar": ["diverging", "surplus deficit"],
    "streamgraph": ["streamgraph"],
}


def _suggest_for_pattern(pattern_id: str, k: int = 8) -> list[tuple[str, str, float, str]]:
    """Return [(key, title, score, how)] suggestions for one pattern."""
    pat = Q.get_pattern(pattern_id, transclude=False)
    if pat is None:
        return []
    capsule = (pat.get("capsule") or "").strip()
    title = pat.get("title") or ""

    seen: dict[str, tuple[str, float, str]] = {}

    def _record(key: str, item_title: str, score: float, how: str):
        if key in seen:
            # keep higher score
            prev = seen[key]
            if score > prev[1]:
                seen[key] = (item_title, score, how)
        else:
            seen[key] = (item_title, score, how)

    # Semantic (similarity on capsule)
    if capsule:
        hits = Q.find_similar(
            capsule + "\n\n" + title,
            k=k * 2,
            min_sim=0.35,
            exclude_sources=EXCLUDE_SOURCES,
        )
        for h in hits:
            _record(h.key, h.title, h.score, f"sim={h.score:.3f}")

    # FTS with pattern-specific keywords
    for kw in PATTERN_KEYWORDS.get(pattern_id, [title.lower()]):
        try:
            hits = Q.search(
                f'"{kw}"',  # phrase search
                k=k,
                exclude_sources=EXCLUDE_SOURCES,
            )
        except Exception:
            # FTS5 rejects some syntactic noise — fall back to bare token
            try:
                hits = Q.search(kw, k=k, exclude_sources=EXCLUDE_SOURCES)
            except Exception:
                continue
        for h in hits:
            _record(h.key, h.title, max(0.0, min(1.0, h.score / 15)), f"fts:{kw}")

    # Sort by score
    sorted_hits = sorted(
        [(k, t, sc, how) for k, (t, sc, how) in seen.items()],
        key=lambda x: -x[2],
    )
    return sorted_hits[:k * 2]


def main():
    pattern_ids = [p["id"] for p in Q.list_patterns()]
    for pid in pattern_ids:
        pat = Q.get_pattern(pid, transclude=False)
        existing = set(pat.get("canonical_examples") or [])  # str or list of keys
        # get_pattern returns resolved list with transclude=False as plain keys
        if existing and isinstance(next(iter(existing)), dict):
            existing = {e.get("key") or f"{e.get('source')}/{e.get('id')}" for e in existing}
        existing_str = {str(e) for e in existing if e}

        print(f"\n### {pid} — {pat['title']}")
        print(f"   existing: {len(existing_str)}")
        suggestions = _suggest_for_pattern(pid)
        for key, title, score, how in suggestions[:10]:
            mark = " [*existing*]" if key in existing_str else ""
            title_short = (title or "")[:70]
            print(f"   {score:.3f}  {how:<20}  {key}{mark}")
            print(f"            {title_short}")


if __name__ == "__main__":
    main()
