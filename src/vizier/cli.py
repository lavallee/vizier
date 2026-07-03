"""vizier CLI.

Current commands:

    vizier stats                  counts per-source + per-tier/type
    vizier ingest <source>        run a per-source ingest
    vizier ingest all             run all known ingest scripts in order
"""

from __future__ import annotations

import importlib
import sys
from collections import Counter

import click

from . import manifest, storage

# Registered ingest modules. Order matters only for `vizier ingest all`.
INGEST_MODULES = (
    "sigma",
    "kantar",
    "kantar_news",  # must run after `kantar` — enriches its items
    "ft_vocab",
    "pudding",
    "junkcharts",
    "weaver",
    "rubrics",
    # Practitioner-walkthrough blogs (Tier 1+2 from docs/process-notes-sources.md)
    "source_opennews",
    "eagereyes",
    "visualising_data",
    "cairo_blog",
    "nightingale",
    "snd",
    "observable",
)


def _load(name: str):
    return importlib.import_module(f"vizier.ingest.{name}")


@click.group()
def main():
    """vizier — discovery and synthesis for viz judgment."""


@main.command()
def stats():
    """Print corpus counts by source, type, and tier."""
    counts = storage.count_by_source()
    if not counts:
        click.echo("corpus is empty. run `vizier ingest all`.")
        return
    click.echo("items by source:")
    total = 0
    for source, n in sorted(counts.items(), key=lambda x: -x[1]):
        click.echo(f"  {n:6d}  {source}")
        total += n
    click.echo(f"  {total:6d}  total")

    # Per-source tier and type breakdowns for anything with > 10 items
    for source, n in counts.items():
        if n < 10:
            continue
        types = Counter()
        tiers = Counter()
        years = Counter()
        for item in storage.iter_items(source=source):
            types[item.type] += 1
            if item.tier:
                tiers[item.tier] += 1
            if item.year:
                years[item.year] += 1
        click.echo(f"\n{source}:")
        click.echo("  types: " + ", ".join(f"{t}={c}" for t, c in types.most_common()))
        if tiers:
            click.echo("  tiers: " + ", ".join(f"{t}={c}" for t, c in tiers.most_common()))
        if years:
            yspan = f"{min(years)}–{max(years)}"
            click.echo(f"  years: {yspan} ({len(years)} years covered)")


@main.command()
@click.argument("source")
def ingest(source: str):
    """Run a per-source ingest. Use `all` to run every registered source.

    Always writes corpus/manifest.json after a successful run so corpus
    state is snapshot-addressable by hash.
    """
    if source == "all":
        for name in INGEST_MODULES:
            click.echo(f"\n=== {name} ===")
            mod = _load(name)
            try:
                click.echo(mod.run())
            except Exception as e:
                click.echo(f"FAILED: {e}", err=True)
        out = manifest.write()
        click.echo(f"\nwrote manifest: {out}")
        return
    if source not in INGEST_MODULES:
        click.echo(f"unknown source: {source!r}. available: {INGEST_MODULES}", err=True)
        sys.exit(2)
    mod = _load(source)
    click.echo(mod.run())
    out = manifest.write()
    click.echo(f"wrote manifest: {out}")


@main.command()
def snapshot():
    """Rewrite corpus/manifest.json without running any ingest."""
    out = manifest.write()
    click.echo(f"wrote manifest: {out}")


@main.group()
def db():
    """Manage the SQLite-backed corpus index."""


@db.command("build")
@click.option("--embed/--no-embed", default=False,
              help="Also (re-)embed items. Default: skip — BM25 search works "
                   "immediately; run `vizier db embed` later to backfill.")
def db_build(embed: bool):
    """Walk corpus/ and populate (or refresh) corpus/.vizier.db.

    By default this is fast (~seconds): items + FTS5 index only. Semantic
    search via `find_similar` needs embeddings — run `vizier db embed`
    separately, or pass `--embed` to do both in one pass.
    """
    from . import db as D
    import json as _json
    info = D.build.populate(embed=embed)
    click.echo(_json.dumps(info, indent=2))
    if not embed:
        # Hint only on fresh-ish builds where a meaningful number of items
        # probably don't have embeddings yet.
        from .db.query import stats as _stats
        s = _stats()
        missing = s["items"] - s["embeddings"]
        if missing > 50:
            click.echo(
                f"note: {missing} items lack embeddings. "
                f"`find_similar` returns empty until you run `vizier db embed`.",
                err=True,
            )


@db.command("embed")
def db_embed():
    """Backfill embeddings for any items missing them.

    Separate from `db build` because embedding is slow (~12 min for a
    fresh 6.7k-item corpus on CPU). Re-running is cheap — only items
    whose body hash changed get re-embedded.
    """
    from . import db as D
    import json as _json
    info = D.build.populate_embeddings_only()
    click.echo(_json.dumps(info, indent=2))


@db.command("stats")
def db_stats():
    """Item + embedding counts from the DB."""
    from . import db as D
    import json as _json
    click.echo(_json.dumps(D.query.stats(), indent=2))


@db.command("search")
@click.argument("query")
@click.option("-k", default=10, type=int)
@click.option("--source", default=None)
@click.option("--tier", default=None)
@click.option("--year-from", default=None, type=int)
@click.option("--year-to", default=None, type=int)
def db_search(query: str, k: int, source: str | None,
              tier: str | None, year_from: int | None, year_to: int | None):
    """Full-text (BM25) search across title + body."""
    from . import db as D
    hits = D.query.search(
        query, k=k, source=source, tier=tier,
        year_from=year_from, year_to=year_to,
    )
    for h in hits:
        click.echo(f"{h.score:6.2f}  {h.source}/{h.item_id}")
        click.echo(f"        {h.title}")


@db.command("similar")
@click.argument("text")
@click.option("-k", default=8, type=int)
@click.option("--min-sim", default=0.25, type=float)
@click.option("--source", default=None)
def db_similar(text: str, k: int, min_sim: float, source: str | None):
    """Embedding-based semantic retrieval."""
    from . import db as D
    hits = D.query.find_similar(text, k=k, min_sim=min_sim, source=source)
    for h in hits:
        click.echo(f"{h.score:.3f}  {h.source}/{h.item_id}")
        click.echo(f"        {h.title}")


@main.command()
def mcp():
    """Run the vizier MCP server (stdio). For use with Claude Desktop, Cursor, etc."""
    from .mcp_server import main as run_mcp
    run_mcp()


@main.command()
@click.argument("colors")
@click.option("--mode", type=click.Choice(["light", "dark"]), default="light")
@click.option("--surface", default=None, help="Chart surface hex (default: per mode).")
@click.option("--pairs", type=click.Choice(["adjacent", "all"]), default="adjacent",
              help="adjacent = stacks/bars/lines; all = scatter/bubble/maps/small-multiples.")
@click.option("--ordinal", is_flag=True, default=False,
              help="Validate as a one-hue ordinal ramp (funnel stages, tiers, buckets).")
def validate(colors: str, mode: str, surface: str | None, pairs: str, ordinal: bool):
    """Run the computable color checks on a palette. COLORS is comma-separated hex.

    Deterministic — Machado-2009 colorblind ΔE, WCAG contrast, OKLCH band/chroma.
    Exit 1 on any hard FAIL (WARN bands still exit 0).

        vizier validate "#e69f00,#0072b2,#009e73,#56b4e9" --pairs all
    """
    from .analyze import color as C
    pal = [c.strip() for c in colors.split(",") if c.strip()]
    if not pal:
        click.echo("no colors given", err=True)
        sys.exit(2)
    r = (C.validate_ordinal(pal, mode=mode, surface=surface) if ordinal
         else C.validate_categorical(pal, mode=mode, surface=surface, pairs=pairs))
    click.echo(C.format_report(r))
    sys.exit(0 if r.ok else 1)


@main.command()
@click.argument("artifact", type=click.Path(exists=True, dir_okay=False))
@click.option("--mode", type=click.Choice(["light", "dark"]), default="light")
@click.option("--surface", default=None, help="Chart surface hex to exclude (default: per mode).")
@click.option("--pairs", type=click.Choice(["adjacent", "all"]), default="all",
              help="all (default — extracted order isn't reliable) or adjacent.")
def analyze(artifact: str, mode: str, surface: str | None, pairs: str):
    """Extract the palette from an SVG/HTML chart file and run the color checks.

    The one path where vizier gets *exact* swatches. Splits chromatic data colors
    from achromatic chrome (axis/grid/text) via the OKLCH chroma floor.
    """
    from pathlib import Path
    from .analyze import color as C, extract as X, structure as St
    text = Path(artifact).read_text(encoding="utf-8", errors="ignore")
    ex = X.extract(text, surface=surface)
    click.echo(f"data palette ({len(ex.palette)}): {', '.join(ex.palette) or '—'}")
    if ex.achromatic:
        click.echo(f"chrome/gray ({len(ex.achromatic)}): {', '.join(ex.achromatic)}")
    click.echo()
    if ex.palette:
        click.echo(C.format_report(C.validate_categorical(ex.palette, mode=mode, surface=surface, pairs=pairs)))
    else:
        click.echo("no chromatic data colors found — is this a chart SVG/HTML?", err=True)
    struct = St.lint_svg(text, surface=surface)["findings"]
    if struct:
        click.echo("\nstructural findings:")
        click.echo(St.format_findings(struct))


@main.command("suggest-palette")
@click.argument("n", type=int)
@click.option("--mode", type=click.Choice(["light", "dark"]), default="light")
@click.option("--surface", default=None)
@click.option("--theme", type=click.Choice(["default", "muted"]), default="default",
              help="default = bright/high-separation; muted = editorial (light only).")
@click.option("--pairs", type=click.Choice(["adjacent", "all"]), default="adjacent")
def suggest_palette_cmd(n: int, mode: str, surface: str | None, theme: str, pairs: str):
    """Generate a CVD-safe categorical palette of N colors, validated before print.

    The generation counterpart to `vizier validate`.
    """
    from .analyze import generate as G
    try:
        r = G.suggest_palette(n, mode=mode, surface=surface, theme=theme, pairs=pairs)
    except ValueError as e:
        click.echo(str(e), err=True)
        sys.exit(2)
    click.echo(",".join(r["palette"]))
    click.echo()
    click.echo(r["text"])


@main.command("suggest-ramp")
@click.argument("steps", type=int)
@click.option("--hue", default="blue",
              help="blue/navy/green/teal/orange/gray, or use --light/--dark anchors.")
@click.option("--light", default=None, help="Explicit light-end hex anchor.")
@click.option("--dark", default=None, help="Explicit dark-end hex anchor.")
@click.option("--mode", type=click.Choice(["light", "dark"]), default="light")
@click.option("--surface", default=None)
def suggest_ramp_cmd(steps: int, hue: str, light: str | None, dark: str | None,
                     mode: str, surface: str | None):
    """Generate a one-hue ordinal ramp of STEPS, validated (or a clear error)."""
    from .analyze import generate as G
    try:
        r = G.suggest_ramp(steps, hue=hue, light=light, dark=dark, mode=mode, surface=surface)
    except ValueError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    click.echo(",".join(r["ramp"]))
    click.echo()
    click.echo(r["text"])


@main.command()
@click.argument("background")
def ink(background: str):
    """The text/ink color (dark or light) that best clears WCAG on a BACKGROUND."""
    from .analyze import generate as G
    r = G.ink_on(background)
    click.echo(f"{r['ink']}  ({r['ratio']}:1, AA normal-text={r['aa_normal_text']})")


@main.command("recommend-form")
@click.argument("job", required=False)
@click.option("--family", default=None, help="FT family, e.g. 'Part-to-whole', 'Flow', 'Ranking'.")
@click.option("--n-series", type=int, default=None,
              help="Series/category count — drives the 'is it even a chart?' guards.")
@click.option("-k", default=4, type=int, help="How many forms to return.")
def recommend_form_cmd(job: str | None, family: str | None, n_series: int | None, k: int):
    """Recommend chart form(s) for a data-job. JOB is a free-text data-question.

        vizier recommend-form "composition of a total over time" --n-series 5
        vizier recommend-form --family Flow
    """
    from .analyze import forms as F
    try:
        r = F.recommend_form(job, family=family, n_series=n_series, k=k)
    except ValueError as e:
        click.echo(str(e), err=True)
        sys.exit(2)
    click.echo(F.format_recommendation(r))


@main.group()
def patterns():
    """Work with the chart_pattern corpus."""


@patterns.command("list")
@click.option("--family", default=None, help="FT family filter, e.g. 'Flow'.")
def patterns_list(family: str | None):
    """List available chart patterns."""
    from . import db as D
    for p in D.query.list_patterns(purpose_family=family):
        fams = ", ".join(p["purpose_families"])
        click.echo(f"{p['id']:22s}  [{fams}]")
        click.echo(f"    {p['capsule'][:100]}")


@patterns.command("export")
@click.option("-o", "--out", type=click.Path(dir_okay=False, writable=True),
              default="-", help="Output JSON path; '-' for stdout.")
def patterns_export(out: str):
    """Dump all chart_pattern items with transclusion resolved.

    Intended as input to the bundled chart-forms guide (docs/reader/data.json).
    Emits one JSON object: { patterns: {id: {...resolved...}}, families: [...] }.
    """
    from . import db as D
    import json as _json
    listing = D.query.list_patterns()
    patterns_obj: dict = {}
    families: set[str] = set()
    for p in listing:
        full = D.query.get_pattern(p["id"], transclude=True)
        if full is None:
            continue
        patterns_obj[p["id"]] = full
        for f in full.get("purpose_families") or []:
            families.add(f)
    payload = {
        "patterns": patterns_obj,
        "families": sorted(families),
        "count": len(patterns_obj),
    }
    text = _json.dumps(payload, indent=2, ensure_ascii=False)
    if out == "-":
        click.echo(text)
    else:
        from pathlib import Path as _Path
        _Path(out).write_text(text + "\n", encoding="utf-8")
        click.echo(f"wrote {out}  ({len(patterns_obj)} patterns, {len(families)} families)")


@main.command()
@click.argument("image_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--backend", default=None,
              type=click.Choice(["ollama", "minimax_mcp"]),
              help="Captioner backend. Default: minimax_mcp "
                   "(override via VIZIER_VISION_BACKEND env var).")
@click.option("--model", default=None,
              help="Override model. For ollama: any vision model name. "
                   "For minimax_mcp: pseudo-id (MiniMax doesn't disclose "
                   "the backing model).")
@click.option("--no-cache", is_flag=True, default=False,
              help="Bypass the cache and re-caption.")
def caption(image_path: str, backend: str | None, model: str | None, no_cache: bool):
    """Caption a single image via the chosen backend.

    Writes the result to evals/captions/<sha>.<backend>.<model>.<version>.md
    and prints the caption to stdout. Subsequent calls on the same image
    + backend + model + prompt version serve from cache instantly.
    """
    from . import vision as V
    kwargs = {"use_cache": not no_cache, "backend": backend or V.DEFAULT_BACKEND}
    if model:
        kwargs["model"] = model
    cap = V.caption(image_path, **kwargs)
    src = "cache" if cap.cached else f"{cap.backend} {cap.model}"
    click.echo(f"# {src} · {cap.duration_s:.1f}s · sha={cap.sha[:12]}")
    click.echo()
    click.echo(cap.text)


@main.command()
@click.argument("image_path")
@click.option("--pattern", "pattern_id", default=None,
              help="Chart pattern id (e.g. `sankey`, `violin`). If omitted, "
                   "vizier classifies the chart via the LLM.")
@click.option("--context", default=None,
              help="Surrounding context — headline, deck, or caption that "
                   "accompanies the chart. Optional but improves the critique.")
@click.option("--palette", default=None,
              help="Comma-separated hex colors of the chart's series. When given, "
                   "vizier runs the deterministic color checks (colorblind ΔE, "
                   "contrast) and folds the computed findings into the critique.")
@click.option("--vision-backend", default=None,
              type=click.Choice(["ollama", "minimax_mcp"]),
              help="Captioner backend. Default: minimax_mcp "
                   "(override via VIZIER_VISION_BACKEND env var).")
@click.option("--model", default=None,
              help="LLM model override (default: gemini-2.5-pro).")
@click.option("--json", "as_json_out", is_flag=True, default=False,
              help="Emit JSON instead of markdown.")
def critique(image_path: str, pattern_id: str | None, context: str | None,
             palette: str | None, vision_backend: str | None, model: str | None,
             as_json_out: bool):
    """Critique a chart image — retrieve relevant patterns + prior art, then synthesize a review.

    IMAGE_PATH may be a local file (.png/.jpg/.jpeg/.webp) or a direct
    http(s) image URL (not an HTML page — download the chart image
    manually for those). Convert SVGs with `rsvg-convert` or `cairosvg`
    first.
    """
    from . import vision as V
    from .critique import adhoc
    kwargs: dict = {
        "pattern_id": pattern_id,
        "context": context,
        "palette": palette,
        "vision_backend": vision_backend or V.DEFAULT_BACKEND,
    }
    if model:
        kwargs["model"] = model
    r = adhoc.critique(image_path, **kwargs)
    if as_json_out:
        click.echo(adhoc.as_json(r))
    else:
        click.echo(adhoc.as_markdown(r))


@main.group()
def eval():
    """Run evaluation harnesses and inspect their output."""


@eval.command("naive")
@click.option("--model", default=None,
              help="Override the naive model (default: gemini-2.5-pro, free).")
@click.option("--provider", default=None, help="Force a specific somm provider.")
def eval_naive(model: str | None, provider: str | None):
    """Run the naive critique baseline against every case in evals/cases/.

    A plain LLM call with no corpus retrieval and no named rubrics. Each
    run is stamped with the current corpus_hash so future informed runs
    can be compared against the exact corpus state they were evaluated
    against.
    """
    from .critique import naive
    kwargs = {}
    if model:
        kwargs["model"] = model
    if provider:
        kwargs["provider"] = provider
    click.echo(naive.run(**kwargs))


@eval.command("informed")
@click.option("--style", default="multi",
              type=click.Choice(["multi", "ft", "nyt", "pudding", "junkcharts"]),
              help="Named critique style to overlay on the base rubric.")
@click.option("--resilient", is_flag=True, default=False,
              help="Use cross-provider fallback (OR → MiniMax) with retries. "
                   "Run output records fallback_trace. Off by default so eval "
                   "reproducibility is preserved.")
@click.option("--model", default=None,
              help="Override the model (e.g. 'gemini-2.5-pro', "
                   "'anthropic/claude-sonnet-4.6'). Default: Opus 4.7 via OR.")
@click.option("--provider", default=None,
              help="Force a specific somm provider (e.g. 'gemini', 'openrouter', "
                   "'minimax'). Default: let somm route by the model string.")
@click.option("--no-vision", is_flag=True, default=False,
              help="Skip the vision captioner even if a case has an image.")
@click.option("--vision-backend", default=None,
              type=click.Choice(["ollama", "minimax_mcp"]),
              help="Captioner backend when a case has an image. "
                   "Default: minimax_mcp (override via VIZIER_VISION_BACKEND).")
def eval_informed(
    style: str,
    resilient: bool,
    model: str | None,
    provider: str | None,
    no_vision: bool,
    vision_backend: str | None,
):
    """Run the informed critique against every case in evals/cases/.

    Retrieves corpus context (weaver principles, FT vocab, Cairo rubric,
    tag-matched prior art) and applies Cairo's five-pillar framework
    explicitly. With --style, layers a publication's house-style lens
    on top (ft, nyt, pudding, junkcharts). Stamped with the same
    corpus_hash scheme as naive so runs can be diffed per case.

    Use --model / --provider to run the informed critique on a non-
    default backend (e.g. Gemini) for head-to-head comparisons. The
    run directory is suffixed with the model tag so parallel runs
    don't collide.
    """
    from . import vision as V
    from .critique import informed
    kwargs = {
        "style": style,
        "resilient": resilient,
        "use_vision": not no_vision,
        "vision_backend": vision_backend or V.DEFAULT_BACKEND,
    }
    if model:
        kwargs["model"] = model
    if provider:
        kwargs["provider"] = provider
    click.echo(informed.run(**kwargs))


@eval.command("judge")
@click.argument("run_a")
@click.argument("run_b")
@click.option("-n", "--n-runs", default=1, type=int,
              help="Judge passes per case; aggregated by median axis score + "
                   "majority winner. N=3 cuts judge variance ~1.7× at 3× cost.")
@click.option("--model", default=None,
              help="Override judge model (e.g. 'gemini-2.5-pro'). Default: "
                   "anthropic/claude-opus-4.7 via OpenRouter.")
@click.option("--provider", default=None,
              help="Force a specific somm provider (e.g. 'gemini').")
def eval_judge(run_a: str, run_b: str, n_runs: int, model: str | None, provider: str | None):
    """Judge two critique runs against each other, per case, against ground truth.

    A/B labels are randomized per case so the judge can't position-bias.
    Winner attribution is mapped back to the run's directory name.
    Writes a per-case markdown + aggregate index.json to evals/judge/.
    """
    from .critique import judge
    kwargs = {"n": n_runs}
    if model:
        kwargs["model"] = model
    if provider:
        kwargs["provider"] = provider
    click.echo(judge.run(run_a, run_b, **kwargs))


@eval.command("full")
@click.option("--style", default="multi",
              type=click.Choice(["multi", "ft", "nyt", "pudding", "junkcharts"]),
              help="Named critique style for the informed run.")
@click.option("-n", "--n-runs", default=3, type=int,
              help="Judge passes per case (default 3 for lower variance).")
@click.option("--resilient", is_flag=True, default=False,
              help="Use cross-provider fallback for the informed run.")
@click.option("--model", default=None,
              help="Override the informed model (e.g. 'gemini-2.5-pro').")
@click.option("--provider", default=None,
              help="Force a specific somm provider for informed.")
def eval_full(style: str, n_runs: int, resilient: bool, model: str | None, provider: str | None):
    """Run the full eval pipeline: naive → informed → judge → results.

    One command. Every step is stamped with the current corpus_hash so
    the combined run is a single snapshot-addressable eval cycle.
    """
    from .critique import informed, judge, naive
    click.echo("\n=== naive ===")
    naive_info = naive.run()
    click.echo(naive_info)

    click.echo("\n=== informed ===")
    informed_kwargs = {"style": style, "resilient": resilient}
    if model:
        informed_kwargs["model"] = model
    if provider:
        informed_kwargs["provider"] = provider
    informed_info = informed.run(**informed_kwargs)
    click.echo(informed_info)

    # Extract just the run-dir basename from the returned absolute paths
    from pathlib import Path as _P
    naive_name = _P(naive_info["run_dir"]).name
    informed_name = _P(informed_info["run_dir"]).name

    click.echo(f"\n=== judge (n={n_runs}) ===")
    judge_info = judge.run(naive_name, informed_name, n=n_runs)
    click.echo(judge_info)

    click.echo("\n=== results ===")
    _print_judge_results(judge_info["judge_dir"])


def _print_judge_results(judge_dir: str):
    """Shared results printer for `eval results` and `eval full`."""
    import json as _json
    from pathlib import Path as _Path
    data = _json.loads((_Path(judge_dir) / "index.json").read_text())
    a, b = data["run_a"], data["run_b"]
    totals = data["totals_by_winner"]
    click.echo(f"judge: {_Path(judge_dir).name}")
    click.echo(f"A: {a}")
    click.echo(f"B: {b}\n")
    click.echo("wins:")
    for name, n in totals.items():
        click.echo(f"  {n:>3}  {name}")
    click.echo("\nmean axis scores:")
    for run, axes in data["mean_axis_scores"].items():
        label = "A" if run == a else "B"
        click.echo(f"  [{label}] {run}")
        for ax, v in axes.items():
            click.echo(f"       {ax:<18} {v:.2f}")
    click.echo("\ndelta (B − A):")
    for ax, v in data["axis_delta_b_minus_a"].items():
        sign = "+" if v >= 0 else ""
        click.echo(f"  {ax:<18} {sign}{v:.2f}")
    click.echo("\nper-case:")
    for c in data["cases"]:
        winner = "A" if c["winner_source"] == a else ("B" if c["winner_source"] == b else c["winner_source"])
        click.echo(f"  {c['case_id']:<40} → {winner}")


@eval.command("results")
@click.option("--judge-dir", default=None, help="Specific judge dir (default: latest).")
def eval_results(judge_dir: str | None):
    """Print a summary of the latest (or specified) judge run."""
    from pathlib import Path as _Path
    base = _Path(__file__).resolve().parents[2] / "evals" / "judge"
    if judge_dir:
        target = _Path(judge_dir) if _Path(judge_dir).is_absolute() else base / judge_dir
    else:
        dirs = sorted(p for p in base.iterdir() if p.is_dir())
        if not dirs:
            click.echo("no judge runs yet. run `vizier eval judge <run-a> <run-b>`.")
            return
        target = dirs[-1]
    _print_judge_results(str(target))


if __name__ == "__main__":
    main()
