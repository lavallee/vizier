"""vizier MCP server — example provider over the corpus DB.

Exposes a small, purpose-built toolset for visualization-critique
workflows. Clients can ask: "show me prior art like this", "how did
anyone tackle a racing bar chart", "list the house principles for the
Narrate stage", or "fetch that specific kantar 2019 shortlist item."

Transport: stdio (the usual MCP wiring for local clients like Claude
Desktop, Cursor, Claude Code).

Tools mirror the query module, but are tuned for model ergonomics —
bodies truncated by default, one-line `why` string per hit, sources
listed in the description so the model knows what's queryable.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import Field

from .db import query as Q

# The server class was renamed in the MCP SDK 2.0: `mcp.server.fastmcp.FastMCP`
# became `mcp.server.mcpserver.MCPServer`. The surface vizier uses — the
# constructor kwargs, `.tool(description=...)`, `.run()` — is the same in both,
# so support either rather than pinning users to one SDK generation.
try:
    from mcp.server.mcpserver import MCPServer as _Server  # SDK >= 2.0
except ModuleNotFoundError:  # pragma: no cover - exercised by the older SDK
    from mcp.server.fastmcp import FastMCP as _Server  # SDK 1.x


mcp = _Server(
    "vizier",
    instructions=(
        "vizier shows people how to visualize their data, and judges the result. "
        "START with `show` when someone has a table and wants to see it: it ranks the "
        "ways to show it (including a sentence or table when those serve better), "
        "draws the best ones, and attaches honesty notes. Before there is a claim, "
        "`explore` shows what is in the table as a contact sheet of small views. "
        "COMPUTABLE color/form decisions (deterministic, no LLM): when building a "
        "chart, `suggest_palette` for CVD-safe series colors, `suggest_ramp` for a "
        "one-hue ordinal ramp, `ink_on` for a legible label color, and "
        "`implementation_guide` for form + journalism checks; to check an "
        "existing chart, `validate_palette`, `analyze_artifact` (SVG/HTML), or "
        "`check_contrast`. What these suggest is what they would pass — call them "
        "instead of rolling your own color math. "
        "CORPUS (for judgment/prior art): `search` for keyword/BM25 lookup, "
        "`find_similar` for semantically close prior art, `lookup` for a known "
        "(source, item_id); `list_principles` / `list_rubrics` for canonical "
        "frameworks (Cairo, FT Vocab, the dataviz method); `list_patterns` / "
        "`get_pattern` for the 43-form chart taxonomy. Sources include kantar and "
        "sigma (awards), junkcharts (critiques), the house principles, and "
        "seven practitioner blogs (source-opennews, eagereyes, visualising-data, "
        "cairo-blog, nightingale, snd, observable)."
    ),
)


def _hit_to_json(hit: Q.Hit, *, body_chars: int = 1200) -> dict[str, Any]:
    return hit.to_dict(body_chars=body_chars)


@mcp.tool(
    description=(
        "Keyword/BM25 search across titles and bodies. Good for named "
        "things ('bar chart race', 'small multiples', 'Mercator'). "
        "Filter with source, tier, year_from/year_to, or tags."
    ),
)
def search(
    q: Annotated[str, Field(description="FTS5 query (bare tokens ANDed; 'OR' allowed; \"phrase\" supported)")],
    k: Annotated[int, Field(ge=1, le=50, description="Max hits")] = 10,
    source: Annotated[str | None, Field(description="Restrict to one source (e.g. 'junkcharts')")] = None,
    tier: Annotated[str | None, Field(description="Award tier (gold/silver/bronze/...)")] = None,
    year_from: Annotated[int | None, Field(description="Earliest year (inclusive)")] = None,
    year_to: Annotated[int | None, Field(description="Latest year (inclusive)")] = None,
    tags: Annotated[list[str] | None, Field(description="Any-tag match (OR)")] = None,
    body_chars: Annotated[int, Field(ge=0, le=8000, description="Truncate hit bodies")] = 1200,
) -> list[dict[str, Any]]:
    hits = Q.search(
        q, k=k, source=source, tier=tier,
        year_from=year_from, year_to=year_to, tags=tags,
    )
    return [_hit_to_json(h, body_chars=body_chars) for h in hits]


@mcp.tool(
    description=(
        "Embedding-cosine similarity against a free-form description or "
        "case body. Use this when you don't have the exact words, e.g. "
        "'choropleth of voting behavior that confuses area with magnitude'."
    ),
)
def find_similar(
    text: Annotated[str, Field(description="Free text: describe the artifact or case")],
    k: Annotated[int, Field(ge=1, le=50)] = 8,
    min_sim: Annotated[float, Field(ge=0.0, le=1.0, description="Drop hits below this cosine similarity")] = 0.25,
    source: Annotated[str | None, Field(description="Restrict to one source")] = None,
    type: Annotated[str | None, Field(description="Restrict to one item type (process_note, critique, principle, ...)")] = None,
    tier: Annotated[str | None, Field(description="Award tier")] = None,
    year_from: Annotated[int | None, Field()] = None,
    year_to: Annotated[int | None, Field()] = None,
    tags: Annotated[list[str] | None, Field(description="Any-tag match (OR)")] = None,
    body_chars: Annotated[int, Field(ge=0, le=8000)] = 1200,
) -> list[dict[str, Any]]:
    hits = Q.find_similar(
        text, k=k, min_sim=min_sim, source=source, type=type, tier=tier,
        year_from=year_from, year_to=year_to, tags=tags,
    )
    return [_hit_to_json(h, body_chars=body_chars) for h in hits]


@mcp.tool(description="Fetch a single item in full by (source, item_id).")
def lookup(
    source: str,
    item_id: str,
    body_chars: Annotated[int, Field(ge=0, le=200000)] = 0,  # 0 = full body
) -> dict[str, Any] | None:
    hit = Q.lookup(source, item_id)
    if hit is None:
        return None
    return _hit_to_json(hit, body_chars=body_chars or None)


@mcp.tool(
    description=(
        "Return vizier's house principles (its own working rubric). Pass `stage` "
        "to filter by workflow stage (Explore, Frame, Ingest, Sketch, "
        "Build, Narrate, Critique, Ship, Retrospect, or "
        "'Cross-cutting meta-principles')."
    ),
)
def list_principles(
    stage: Annotated[str | None, Field(description="Workflow stage filter")] = None,
    body_chars: Annotated[int, Field(ge=0, le=8000)] = 2000,
) -> list[dict[str, Any]]:
    hits = Q.list_principles(stage=stage)
    return [_hit_to_json(h, body_chars=body_chars) for h in hits]


@mcp.tool(
    description=(
        "Return canonical evaluation rubrics (Cairo five-pillar framework, "
        "FT Visual Vocabulary, any other `rubrics` items)."
    ),
)
def list_rubrics(
    body_chars: Annotated[int, Field(ge=0, le=8000)] = 4000,
) -> list[dict[str, Any]]:
    hits = Q.list_rubrics()
    return [_hit_to_json(h, body_chars=body_chars) for h in hits]


@mcp.tool(
    description=(
        "Enumerate available corpus sources with item counts and type "
        "breakdowns. Useful before narrowing a search by source."
    ),
)
def list_sources() -> list[dict[str, Any]]:
    return Q.list_sources()


@mcp.tool(description="DB-level stats (item count, embedding count, per-source counts).")
def stats() -> dict[str, Any]:
    return Q.stats()


@mcp.tool(
    description=(
        "List chart-form patterns in the corpus. Each entry carries a "
        "one-line capsule and its FT-Vocab purpose families (Flow, "
        "Part-to-whole, Ranking, Distribution, Change over time, "
        "Magnitude, Spatial, Correlation, Deviation). Pass "
        "`purpose_family` to narrow to one. Use this first when you "
        "have a data-question and don't yet know which form to reach for."
    ),
)
def list_patterns(
    purpose_family: Annotated[str | None, Field(
        description="FT Visual Vocabulary family, e.g. 'Flow', 'Ranking'"
    )] = None,
) -> list[dict[str, Any]]:
    return Q.list_patterns(purpose_family=purpose_family)


@mcp.tool(
    description=(
        "Return a chart_pattern with its graph neighbors resolved: every "
        "alternative's capsule inlined, canonical example URLs resolved, "
        "principles hydrated. One call, full context. Pass "
        "`transclude=False` for bare references."
    ),
)
def get_pattern(
    pattern_id: Annotated[str, Field(description="Pattern id, e.g. 'sankey', 'parallel-sets'")],
    transclude: Annotated[bool, Field(description="Inline alternatives' capsules + example titles")] = True,
) -> dict[str, Any] | None:
    return Q.get_pattern(pattern_id, transclude=transclude)


@mcp.tool(
    description=(
        "Run the COMPUTABLE data-viz color checks on a categorical palette — "
        "deterministic ground truth, not an LLM guess. Computes Machado-2009 "
        "colorblind separation (ΔE under protan/deutan/tritan), WCAG contrast vs "
        "the surface, and OKLCH lightness-band / chroma-floor. Use pairs='all' for "
        "scatter/bubble/maps/small-multiples (any two marks can neighbor) and "
        "'adjacent' for stacks/bars/lines (only neighbors touch). Set ordinal=true "
        "for a one-hue ramp (funnel stages, tiers, buckets) — it switches to the "
        "ramp checks. Thresholds match the `dataviz` skill's validator exactly."
    ),
)
def validate_palette(
    colors: Annotated[str, Field(description="Comma-separated hex colors, in the order they appear (stack/legend order)")],
    mode: Annotated[str, Field(description="'light' or 'dark' — sets the lightness band + default surface")] = "light",
    surface: Annotated[str | None, Field(description="Chart surface hex; default #fcfcfb (light) / #1a1a19 (dark)")] = None,
    pairs: Annotated[str, Field(description="'adjacent' (stacks/bars/lines) or 'all' (scatter/maps)")] = "adjacent",
    ordinal: Annotated[bool, Field(description="Validate as a one-hue ordinal ramp instead of categorical")] = False,
) -> dict[str, Any]:
    from .analyze import color as C
    pal = [c.strip() for c in colors.split(",") if c.strip()]
    r = (C.validate_ordinal(pal, mode=mode, surface=surface) if ordinal
         else C.validate_categorical(pal, mode=mode, surface=surface, pairs=pairs))
    out = r.to_dict()
    out["report"] = C.format_report(r)
    return out


@mcp.tool(
    description=(
        "WCAG contrast ratio between two colors, with AA/AAA pass flags for normal "
        "and large text. Use to check whether a label, axis tick, or in-bar value is "
        "legible on its background (normal text needs 4.5:1, large/bold 3:1)."
    ),
)
def check_contrast(
    foreground: Annotated[str, Field(description="Text/mark hex color")],
    background: Annotated[str, Field(description="Background/surface hex color")],
) -> dict[str, Any]:
    from .analyze import color as C
    ratio = C.contrast(foreground, background)
    return {
        "ratio": round(ratio, 2),
        "aa_normal_text": ratio >= 4.5,
        "aa_large_text": ratio >= 3.0,
        "aaa_normal_text": ratio >= 7.0,
        "aaa_large_text": ratio >= 4.5,
    }


@mcp.tool(
    description=(
        "Extract the color palette from SVG or HTML chart SOURCE and run the color "
        "checks on it — the one path where vizier can get *exact* swatches (a raster "
        "image can't). Returns the chromatic data palette, the achromatic chrome "
        "(axis/grid/text/surface), and the validation report. For a raster image, "
        "recover the palette another way and call validate_palette."
    ),
)
def analyze_artifact(
    markup: Annotated[str, Field(description="SVG or HTML source text of the chart")],
    mode: Annotated[str, Field(description="'light' or 'dark'")] = "light",
    surface: Annotated[str | None, Field(description="Chart surface hex to exclude; default per mode")] = None,
    pairs: Annotated[str, Field(description="'all' (default — extracted order isn't reliable) or 'adjacent'")] = "all",
) -> dict[str, Any]:
    from .analyze import color as C, extract as X, structure as St
    ex = X.extract(markup, surface=surface)
    out = ex.to_dict()
    if ex.palette:
        r = C.validate_categorical(ex.palette, mode=mode, surface=surface, pairs=pairs)
        out["validation"] = r.to_dict()
        out["report"] = C.format_report(r)
    out["structure"] = St.lint_svg(markup, surface=surface)["findings"]  # marks-&-anatomy checks
    return out


@mcp.tool(
    description=(
        "GENERATE a CVD-safe categorical palette of `n` colors, validated before "
        "return — the generation counterpart to validate_palette. What vizier suggests "
        "is what vizier would pass. Assigned in a fixed CVD-safe order; past 8 it "
        "returns the 8 that pass with met=false and advice (fold the tail into "
        "'Other', small multiples, direct labels). theme='default' is bright/high-separation; "
        "'muted' is editorial (calmer on warm surfaces, light mode only). pairs='all' "
        "if the marks are a scatter/map. Use this when building a chart and you need "
        "series colors."
    ),
)
def suggest_palette(
    n: Annotated[int, Field(ge=1, le=64, description="Number of categorical series")],
    mode: Annotated[str, Field(description="'light' or 'dark'")] = "light",
    surface: Annotated[str | None, Field(description="Chart surface hex; default per mode")] = None,
    theme: Annotated[str, Field(description="'default' (bright) or 'muted' (editorial, light only)")] = "default",
    pairs: Annotated[str, Field(description="'adjacent' (stacks/bars/lines) or 'all' (scatter/maps)")] = "adjacent",
) -> dict[str, Any]:
    from .analyze import generate as G
    try:
        return G.suggest_palette(n, mode=mode, surface=surface, theme=theme, pairs=pairs)
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool(
    description=(
        "GENERATE a one-hue ordinal/sequential ramp of `steps`, validated (monotone "
        "lightness, visible ΔL, a light end that clears the surface). hue is one of "
        "blue/navy/green/teal/orange/gray, or pass explicit light/dark anchor hexes. "
        "If the hue can't hold that many steps it returns the longest ramp that passes, "
        "with met=false and advice (bin into fewer classes, or use blue/navy/gray)."
    ),
)
def suggest_ramp(
    steps: Annotated[int, Field(ge=2, le=12, description="Number of ordered steps")],
    hue: Annotated[str, Field(description="blue/navy/green/teal/orange/gray")] = "blue",
    light: Annotated[str | None, Field(description="Explicit light-end hex anchor")] = None,
    dark: Annotated[str | None, Field(description="Explicit dark-end hex anchor")] = None,
    mode: Annotated[str, Field(description="'light' or 'dark'")] = "light",
    surface: Annotated[str | None, Field(description="Chart surface hex; default per mode")] = None,
) -> dict[str, Any]:
    from .analyze import generate as G
    try:
        return G.suggest_ramp(steps, hue=hue, light=light, dark=dark, mode=mode, surface=surface)
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool(
    description=(
        "The text/ink color (dark or light) that best clears WCAG contrast on a "
        "background fill — compute the label color from the background, don't eyeball "
        "it. Use for in-bar labels, chips, or any text sitting on a colored fill."
    ),
)
def ink_on(
    background: Annotated[str, Field(description="Background/fill hex color")],
) -> dict[str, Any]:
    from .analyze import generate as G
    return G.ink_on(background)


@mcp.tool(
    description=(
        "Recommend chart FORM(s) for a data-job — the generation counterpart to "
        "critiquing a chart against its pattern. Pass a free-text `job` ('part-to-"
        "whole over time, 5 series') and/or an FT `family`, plus optional `n_series`. "
        "Returns ranked patterns (capsule, when-to / when-not, alternatives, common "
        "mistakes) and form-heuristic notes — including when a stat tile or a table "
        "would serve alongside or instead (a single value; more than ~7 classes). Use "
        "before drawing to pick the form; use `show` to have it drawn."
    ),
)
def recommend_form(
    job: Annotated[str | None, Field(description="Free-text data-question / job")] = None,
    family: Annotated[str | None, Field(description="FT family: Deviation/Correlation/Ranking/Distribution/Change over time/Magnitude/Part-to-whole/Spatial/Flow")] = None,
    n_series: Annotated[int | None, Field(description="Series/category count — drives the stat-tile / table notes")] = None,
    k: Annotated[int, Field(ge=1, le=10, description="How many forms to return")] = 4,
) -> dict[str, Any]:
    from .analyze import forms as F
    try:
        return F.recommend_form(job, family=family, n_series=n_series, k=k)
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool(
    description=(
        "Guide a chart implementation before building it. Combines deterministic "
        "form recommendations with a journalism checklist (reader decision, "
        "headline claim, fair comparison, denominator, counter-reading, accessibility) "
        "and corpus prior-art signals. Uses configured extension DBs, so private/local "
        "editorial corpora can enrich guidance without hard-coding them."
    ),
)
def implementation_guide(
    job: Annotated[str, Field(description="Free-text chart/data job")],
    context: Annotated[str | None, Field(description="Headline, caption, source, or implementation context")] = None,
    family: Annotated[str | None, Field(description="Optional FT family override")] = None,
    n_series: Annotated[int | None, Field(description="Series/category count for form guards")] = None,
    k_forms: Annotated[int, Field(ge=1, le=10, description="How many form candidates to return")] = 4,
    k_prior: Annotated[int, Field(ge=0, le=20, description="How many corpus signals to return")] = 5,
    semantic: Annotated[bool, Field(description="Also use embedding retrieval if the search extra is installed")] = False,
) -> dict[str, Any]:
    from .analyze import guidance as G
    try:
        return G.implementation_guide(
            job,
            context=context,
            family=family,
            n_series=n_series,
            k_forms=k_forms,
            k_prior=k_prior,
            semantic=semantic,
        )
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool(
    description=(
        "SHOW how to visualize a table — the front door. Give a CSV/JSON `path` (a "
        "datapackage.json beside it is read for units, descriptions and missing values) "
        "or inline `rows` (a list of records), and optionally `claim`: the claim or "
        "question the figure should serve. vizier profiles the columns, ranks the ways "
        "to show it — charts, and a sentence, stat tile or table when one serves "
        "better (each with what it shows, what it hides, and common mistakes) — and "
        "draws the top `top` options from the real rows as offline SVG + HTML with "
        "title, axis units, source and honesty notes (truncated axis, too many series, "
        "small sample, rate without denominator, suppressed values) attached, applying "
        "mechanical fixes itself. Never refuses. No model, no network. Pass `out_dir` "
        "to write files; `include_svg` to get the SVG text back. Returns the "
        "vizier/show-spec/v1 result (chosen form, field roles, colors, words, notes)."
    ),
)
def show(
    path: Annotated[str | None, Field(description="Path to a CSV or JSON table")] = None,
    rows: Annotated[list[dict[str, Any]] | None, Field(description="Inline records, instead of a path")] = None,
    claim: Annotated[str | None, Field(description="The claim or question the figure should serve")] = None,
    x: Annotated[str | None, Field(description="Column for the x axis / categories")] = None,
    y: Annotated[str | None, Field(description="Measure column(s), comma-separated")] = None,
    series: Annotated[str | None, Field(description="Column that splits series")] = None,
    label: Annotated[str | None, Field(description="Column that names each row")] = None,
    top: Annotated[int, Field(ge=1, le=10, description="How many ranked options to draw")] = 3,
    out_dir: Annotated[str | None, Field(description="Directory to write index.html, SVGs and spec.json")] = None,
    caveats: Annotated[list[dict[str, str]] | None, Field(description="Dataset caveats: [{effect, misuse, instead}]")] = None,
    zero: Annotated[bool, Field(description="Start every value axis at zero")] = False,
    include_svg: Annotated[bool, Field(description="Return each drawn SVG's text in the result")] = False,
) -> dict[str, Any]:
    from .show import show as _show
    from .show.table import table_from_records
    if not path and not rows:
        return {"error": "give a `path` to a CSV/JSON table, or inline `rows`"}
    source = path if path else table_from_records(rows or [], name="rows")
    try:
        r = _show(source, claim=claim, overrides={"x": x, "y": y, "series": series, "label": label},
                  out_dir=out_dir, top=top, caveats=caveats, zero=zero)
    except (ValueError, OSError) as e:
        return {"error": str(e)}
    if include_svg:
        if out_dir:
            from pathlib import Path
            for o in r["options"]:
                f = (o.get("files") or {}).get("svg")
                if f:
                    o["svg"] = (Path(out_dir) / f).read_text(encoding="utf-8")
        else:
            r["note"] = "include_svg needs out_dir (SVGs are returned from the written files)."
    if not include_svg:
        r.pop("profile", None)  # keep the default reply small; the spec carries the fields chosen
    return r


@mcp.tool(
    description=(
        "EXPLORE a table before there is a claim — what is in it? Look first; then show. "
        "Give a CSV/JSON `path` (a datapackage.json beside it is read). Returns the "
        "vizier/explore/v1 result: a field sheet (distribution, missing / suppressed "
        "counts, range, median and oddities per field), missingness, relationships "
        "between measures ranked by Spearman rho (with a leverage check and a view "
        "conditioned on the likeliest confounder), breakdowns by group ranked by "
        "epsilon-squared, trends and outliers. Notes say how many comparisons were "
        "looked at; a pattern found by looking at many is a lead, not a finding. Each "
        "view carries `show_args` to hand to `show`. `out_dir` writes index.html (a "
        "static contact sheet), the SVGs and explore.json. No model, no network."
    ),
)
def explore(
    path: Annotated[str, Field(description="Path to a CSV or JSON table")],
    out_dir: Annotated[str | None, Field(description="Directory for index.html, SVGs and explore.json")] = None,
    max_views: Annotated[int, Field(ge=1, le=200, description="How many views to draw")] = 24,
    focus: Annotated[str | None, Field(description="Field to put at the centre")] = None,
    by: Annotated[str | None, Field(description="Re-run the sheet per group of this column")] = None,
    where: Annotated[list[str] | None, Field(description="Row filters, each 'COL=VALUE' or 'COL!=VALUE'")] = None,
    view: Annotated[str | None, Field(description="Redraw one view by id, larger")] = None,
) -> dict[str, Any]:
    from .show.explore import explore as _explore
    try:
        return _explore(path, out_dir=out_dir, max_views=max_views, focus=focus, by=by, where=where or [], view=view)
    except (ValueError, OSError) as e:
        return {"error": str(e)}


def main() -> None:
    """Launch the stdio MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
