# Releasing vizier

This checklist is the canonical release path. If anything here is wrong or
missing, fix this file *first*, then run the release. It follows the same
conventions as the sibling `somm` package so the two release the same way.

## Versioning

vizier follows [semantic versioning](https://semver.org). The version lives in
**two** places that move in lockstep:

- `pyproject.toml` → `version`
- `src/vizier/__init__.py` → `__version__`

Bump rules:

- **Patch (0.1.0 → 0.1.1)** — bug fixes, doc updates, corpus refreshes, new
  chart patterns or rubrics. No change to the CLI/MCP/library surface.
- **Minor (0.1.1 → 0.2.0)** — new backward-compatible surface: a new CLI
  command, MCP tool, analyze/critique capability, or a new optional extra.
- **Major (0.x → 1.0)** — breaking changes to the CLI flags, MCP tool
  signatures, the `vizier/chart-spec` schema, or the computable thresholds.

The color-math thresholds (`src/vizier/analyze/color.py`) are a faithful port of
the `dataviz` method's validator. Treat a threshold change as **breaking** — it
changes what vizier passes and suggests — and call it out explicitly in the
changelog.

## The checklist

1. **Tests and lint pass locally.**
   ```bash
   uv run pytest -q          # 17 tests
   uv run ruff check src/ tests/
   ```
   Any failure blocks the release. (These are also the CI gate — see
   `.github/workflows/ci.yml`.)

2. **Bump the version in both places.**
   ```bash
   OLD=0.1.0; NEW=0.2.0
   sed -i "s/^version = \"$OLD\"/version = \"$NEW\"/" pyproject.toml
   sed -i "s/__version__ = \"$OLD\"/__version__ = \"$NEW\"/" src/vizier/__init__.py
   ```

3. **Refresh the bundled chart-pattern data** if any pattern, rubric, or the
   taxonomy changed. The guide ships a snapshot that goes stale otherwise:
   ```bash
   uv run vizier db build
   uv run vizier patterns export -o docs/reader/data.json
   ```

4. **Update `CHANGELOG.md`.** Add a dated heading at the top:
   ```markdown
   ## [X.Y.Z] — YYYY-MM-DD

   ### Added
   - …

   ### Changed / Fixed
   - …
   ```
   Be specific — future-you reads this.

5. **Update the landing page** (`docs/index.html`). It's a hand-maintained
   marketing surface, not generated. Minimum edits per release:
   - `<span class="mark-sub">/ vX.Y.Z</span>` in the header
   - the "Status" section version line near the bottom
   - any new user-visible capability added to "What it decides"

6. **Run the suite once more** (the version bump can touch version tests), then
   **commit** — a `chore(release): X.Y.Z` commit for the version + changelog +
   landing, so the tag points at a clean state.

7. **Tag and push.**
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z — one-line summary"
   git push origin main
   git push origin vX.Y.Z
   ```

8. **Create the GitHub release.**
   ```bash
   gh release create vX.Y.Z \
     --title "vX.Y.Z — short tagline" \
     --notes "$(cat <<'EOF'
   ## Highlights
   …

   **Full diff:** https://github.com/lavallee/vizier/compare/vX.Y.Z-1...vX.Y.Z
   EOF
   )"
   ```

9. **Publish to PyPI.**
   ```bash
   uv build
   uv publish            # needs a PyPI token (UV_PUBLISH_TOKEN) or ~/.pypirc
   ```
   Verify the new version at <https://pypi.org/project/vizier/>. When PyPI
   trusted publishing is configured for this project, this step can move to a
   `publish.yml` workflow triggered by the GitHub release (as `somm` does).

## Post-release

- Confirm the release at <https://github.com/lavallee/vizier/releases>.
- If `docs/` changed, wait ~1 minute for GitHub Pages to deploy, then verify
  the site version badge and the guide at `/reader/`.
- `pip install "vizier[critique]"` resolves `somm`/`somm-core` from PyPI; if you
  bumped the `somm` pin, sanity-check the resolve.

## Conventions worth keeping (the family template)

These are the packaging patterns vizier and somm share; carry them to any new
sibling package:

- **Light core, optional extras.** The default install has no proprietary and
  no heavyweight dependencies. Retrieval, LLM critique, and corpus rebuild are
  opt-in extras (`[search]`, `[critique]`, `[ingest]`). Heavy imports
  (`fastembed`/onnx) are lazy so the core stays turn-key.
- **Pluggable proprietary bits.** Where a private tool would help (e.g. a richer
  fetcher), depend on a *plug point* (an env var / callable), never on the
  private package by name. The open-source path always has a working default.
- **MIT + author metadata** in `pyproject.toml`; `LICENSE` at the root.
- **CI on every PR and push to main** — `ruff check` + `pytest`, on the
  supported Python range.
- **CHANGELOG + git tags + GitHub releases** for every version; the tag points
  at a clean release commit.
- **A GitHub Pages site under `docs/`** with `.nojekyll`, sharing the sibling
  design system, that leads with the product story.
