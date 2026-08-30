# Install tests

`pytest` runs inside the source checkout, where the corpus is on disk, the
dependency versions are pinned by `uv.lock`, and the plugin is just some files
in the repo. A user has none of those things. Every bug this harness exists to
catch was invisible to the unit suite and total in the wild:

- the wheel shipped without the chart-pattern corpus, so every form
  recommendation on a `pip install` returned nothing, quietly;
- `vizier mcp` imported a module the MCP SDK had renamed, so the server died
  on any install that didn't have the locked SDK version;
- `vizier critique` raised `ModuleNotFoundError: somm` at the user instead of
  naming the extra to install.

```bash
tests/install/run.sh                  # core + plugin, a couple of minutes
tests/install/run.sh --with-critique  # also installs the [critique] extra
tests/install/run.sh --keep           # leave the sandbox around to poke at
```

Exit code is the number of failed checks.

## What it does

Provisions a throwaway sandbox — its own `CLAUDE_CONFIG_DIR`, `XDG_CACHE_HOME`,
and venv — so it can't read or damage your real Claude config, plugin cache, or
corpus index. Then, in order:

1. **Builds and installs the wheel** into a clean venv, and asserts the
   authored corpus travelled with it (43 patterns) while no third-party source
   did.
2. **Exercises the computable core** the way a new user would: form
   recommendation, the pattern library, the journalism checks, palettes,
   contrast, `doctor`. The first call has to build the index into the cache dir
   on its own.
3. **Starts the MCP server** and completes a real MCP `initialize` handshake.
4. **Checks the critique path's failure modes** — missing extra, missing
   provider key, missing vision key, bad input — all of which must be messages
   naming the fix, never tracebacks.
5. **Installs the Claude Code plugin through a marketplace**, from a staged git
   copy of the working tree, and asserts both skills and the bundled MCP server
   are registered and that the launcher starts.

Sections self-skip when a prerequisite is absent (no `claude` CLI → the plugin
section skips), so the harness stays runnable in CI and on a bare machine.

The unit suite separately checks both manifest versions and that the Codex
manifest declares `.mcp.json`. Before publishing a release through
`lyra-forge/marketplace`, also create a temporary marketplace with a unique
name, install `vizier` with `codex plugin add vizier@<temporary-name>`, and
confirm the installed component inventory in a new Codex session. Remove the
temporary plugin and marketplace afterward. That smoke test is deliberately
kept separate because Codex marketplace configuration is user state.

## The live check

`run.sh` proves the Claude Code plugin installs and registers. It can't prove
the thing that actually matters — that the skills *fire*, and that the answer
comes from vizier's corpus rather than the model's habits. `live.sh` runs real
headless `claude` sessions against a sandbox install and reports which skills
and tools fired:

```bash
tests/install/live.sh                    # three standard prompts
tests/install/live.sh "your own prompt"  # one prompt of your choosing
```

It costs tokens and needs you logged in, so it's separate from `run.sh` and
never runs in CI. The plugin is installed at *local* scope inside a temp
directory, so your user settings are untouched.

Read the trace, not just the pass/fail. A skill that doesn't fire is usually
losing the trigger to another skill with an overlapping description — Claude
Code ships a `dataviz` skill covering the same ground from the styling side,
and which one wins is decided by the two descriptions. That is a real finding
about the plugin, not a flaw in the test.

**Measured, 2026-08-11 (Opus 5, Claude Code 2.1.227):**

| prompt | skill that fired | vizier consulted |
|---|---|---|
| "Build me an HTML chart… save it as budget.html" | bundled `dataviz` | yes — `recommend_form`, `validate_palette`, `ink_on`, `analyze_artifact` |
| "9 product lines over 3 years, what chart should I use?" | none | yes — `recommend_form` |
| "Review budget.html, is it misleading?" | `vizier:chart-critique` | yes |

So the plugin steers the outcome even when it loses the skill trigger: with the
MCP server registered, the form decision still comes from vizier's corpus, and
the answers cite it ("the documented form for comparing composition across
several wholes", fixed segment order, sorted by share rather than
alphabetically). `chart-design` losing the *invocation* to the bundled skill on
an explicit build request is the open item — sharpening its description narrowed
the gap but didn't close it. Re-measure here before and after any change to
either description.

## Adding a check

`check <name> <expected-substring> <cmd...>` and
`check_exit <name> <expected-code> <cmd...>` are the two helpers. Assert on
behaviour a user would notice, and put the "why" in a comment — a check whose
failure nobody can interpret gets deleted rather than fixed.
