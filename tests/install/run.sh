#!/usr/bin/env bash
# Install test — does vizier actually work for someone who just installed it?
#
# The unit suite runs against the source checkout, where the corpus is on disk,
# the venv is pinned by uv.lock, and the plugin is just some files in the repo.
# None of that is true for a user. This harness reproduces the user's situation
# in a throwaway sandbox and asserts the things that broke silently before:
#
#   - a wheel install has the chart-pattern library and builds its own index
#   - the MCP server actually starts and speaks MCP
#   - the plugin installs from a marketplace and exposes its skills + server
#   - the critique path explains what's missing instead of tracebacking
#
# Nothing here touches your real Claude config, your real cache, or PyPI: the
# sandbox gets its own CLAUDE_CONFIG_DIR, XDG_CACHE_HOME, and HOME-shaped state.
#
# Usage:
#   tests/install/run.sh                 # core + plugin checks (no keys, no network beyond deps)
#   tests/install/run.sh --with-critique # also install the [critique] extra and check the key prompt
#   tests/install/run.sh --keep          # leave the sandbox in place for poking at
#
# Exit code is the number of failed checks.

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WITH_CRITIQUE=0
KEEP=0
for arg in "$@"; do
  case "$arg" in
    --with-critique) WITH_CRITIQUE=1 ;;
    --keep) KEEP=1 ;;
    -h|--help) sed -n '2,25p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "unknown flag: $arg" >&2; exit 64 ;;
  esac
done

SANDBOX="$(mktemp -d "${TMPDIR:-/tmp}/vizier-install-test.XXXXXX")"
cleanup() {
  if [ "$KEEP" = "1" ]; then
    echo "sandbox kept at $SANDBOX"
  else
    rm -rf "$SANDBOX"
  fi
}
trap cleanup EXIT

PASS=0; FAIL=0; SKIP=0
say()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()   { PASS=$((PASS+1)); printf '  \033[32m✔\033[0m %s\n' "$*"; }
bad()  { FAIL=$((FAIL+1)); printf '  \033[31m✘\033[0m %s\n' "$*"; }
skip() { SKIP=$((SKIP+1)); printf '  \033[33m–\033[0m %s\n' "$*"; }

# check <name> <expected-substring> <cmd...>  — runs cmd, greps combined output
check() {
  local name="$1" want="$2"; shift 2
  local out; out="$("$@" 2>&1)"
  if printf '%s' "$out" | grep -qF -- "$want"; then
    ok "$name"
  else
    bad "$name (expected to find: $want)"
    printf '%s\n' "$out" | sed 's/^/      | /' | head -12
  fi
}

# check_exit <name> <expected-code> <cmd...>
check_exit() {
  local name="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1
  local got=$?
  [ "$got" = "$want" ] && ok "$name" || bad "$name (exit $got, wanted $want)"
}

need() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------------------
say "Sandbox"
export XDG_CACHE_HOME="$SANDBOX/cache"          # the index must build here, not in yours
export CLAUDE_CONFIG_DIR="$SANDBOX/claude"      # plugin install must not touch yours
export VIZIER_AUTO_PRIVATE=0                    # no sibling vizier-private discovery
unset VIZIER_CORPUS_ROOT VIZIER_DB_PATH VIZIER_EXTENSION_DBS VIZIER_EXTRA_DB_PATHS
mkdir -p "$XDG_CACHE_HOME" "$CLAUDE_CONFIG_DIR"
echo "  $SANDBOX"

if ! need uv; then
  echo "uv is required (https://docs.astral.sh/uv/). Aborting." >&2
  exit 70
fi

# ---------------------------------------------------------------------------
say "Build + install the wheel into a clean venv"
rm -rf "$REPO/dist"
uv build --wheel --out-dir "$SANDBOX/dist" "$REPO" >/dev/null 2>&1 \
  && ok "wheel builds" || { bad "wheel builds"; exit 1; }
WHEEL="$(ls "$SANDBOX"/dist/*.whl | head -1)"

VENV="$SANDBOX/venv"
uv venv "$VENV" --python 3.12 >/dev/null 2>&1
VIRTUAL_ENV="$VENV" uv pip install --quiet "$WHEEL" >/dev/null 2>&1 \
  && ok "wheel installs (no extras)" || bad "wheel installs (no extras)"
VZ="$VENV/bin/vizier"
[ -x "$VZ" ] && ok "vizier is on PATH after install" || bad "vizier is on PATH after install"

# The corpus has to travel inside the wheel. Before 0.2.0 it didn't, and every
# form recommendation silently returned nothing.
check "wheel carries the authored corpus" "chart-forms" \
  bash -c "unzip -l '$WHEEL' | grep -o 'vizier/corpus/[a-z-]*' | sort -u"
PATTERNS_IN_WHEEL="$(unzip -l "$WHEEL" | grep -c 'vizier/corpus/chart-forms/.*\.md')"
[ "$PATTERNS_IN_WHEEL" = "43" ] \
  && ok "43 chart-form patterns in the wheel" \
  || bad "43 chart-form patterns in the wheel (found $PATTERNS_IN_WHEEL)"
check_exit "no third-party corpus redistributed" 1 \
  bash -c "unzip -l '$WHEEL' | grep -qE 'vizier/corpus/(junkcharts|kantar|sigma|pudding|eagereyes|cairo-blog|nightingale|snd|observable|visualising-data|source-opennews)/'"

# ---------------------------------------------------------------------------
say "The computable core, on a fresh install with no keys"

# First read builds the index into the cache dir — that's the whole point.
check "recommend-form answers (index self-builds)" "stacked-area" \
  "$VZ" recommend-form "composition of a total over time" --n-series 5
[ -f "$XDG_CACHE_HOME/vizier/corpus.db" ] \
  && ok "index landed in the cache dir, not site-packages" \
  || bad "index landed in the cache dir, not site-packages"

N_PATTERNS="$("$VZ" patterns list 2>/dev/null | grep -cE '^[a-z0-9-]+ +\[')"
[ "$N_PATTERNS" = "43" ] \
  && ok "patterns list returns all 43 forms" \
  || bad "patterns list returns all 43 forms (got $N_PATTERNS)"

check "patterns show carries the reading checklist" "Reading checklist" \
  "$VZ" patterns show stacked-bar
check "guide runs the journalism checks" "Fair comparison" \
  "$VZ" guide "share of district budget by fund over time" --n-series 5
check "suggest-palette returns validated hexes" "#" "$VZ" suggest-palette 6
check_exit "validate passes a known-good palette" 0 \
  "$VZ" validate "#e69f00,#0072b2,#009e73,#56b4e9" --pairs all
check_exit "validate fails a known-bad palette" 1 \
  "$VZ" validate "#ff0000,#00ff00" --pairs all
check "ink picks a legible label color" "#" "$VZ" ink "#0072b2"

# The 0.1.0 → 0.2.0 upgrade trap: 0.1.0 left an empty `corpus/` beside
# site-packages, and an existence-only check reads that as a source checkout,
# so the upgraded install serves an empty corpus while the packaged one sits
# unused. Simulate the leftover directory and confirm it's ignored.
PKG_DIR="$("$VENV/bin/python" -c 'import os, vizier; print(os.path.dirname(vizier.__file__))')"
STALE_CORPUS="$(dirname "$(dirname "$PKG_DIR")")/corpus"   # the parents[2]/corpus 0.1.0 created
mkdir -p "$STALE_CORPUS" && : > "$STALE_CORPUS/.vizier.db"
check "a leftover empty corpus dir is not read as a checkout" '"corpus_packaged": true' \
  "$VZ" doctor --json
check "the packaged corpus still answers after the upgrade trap" "stacked-area" \
  "$VZ" recommend-form "composition of a total over time" --n-series 5
rm -rf "$STALE_CORPUS"

check "doctor reports a healthy core" "corpus" "$VZ" doctor
check_exit "doctor exits 0 on a core-only install" 0 "$VZ" doctor
check "doctor sees the packaged corpus" '"corpus_packaged": true' "$VZ" doctor --json
check "doctor counts the indexed items" '"items": 88' "$VZ" doctor --json

# ---------------------------------------------------------------------------
say "MCP server"
INIT='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"install-test","version":"1"}}}'
MCP_OUT="$(printf '%s\n' "$INIT" | timeout 60 "$VZ" mcp 2>&1 | head -c 2000)"
printf '%s' "$MCP_OUT" | grep -q '"result"' \
  && ok "vizier mcp completes an MCP initialize handshake" \
  || { bad "vizier mcp completes an MCP initialize handshake"; printf '%s\n' "$MCP_OUT" | sed 's/^/      | /' | head -8; }

# ---------------------------------------------------------------------------
say "Critique path — missing pieces must explain themselves"
check "critique names the extra to install" "datavizier[critique]" \
  "$VZ" critique /nonexistent.png
check_exit "critique exits 2, not a traceback" 2 "$VZ" critique /nonexistent.png
check_exit "critique never tracebacks" 1 \
  bash -c "'$VZ' critique /nonexistent.png 2>&1 | grep -q Traceback"

if [ "$WITH_CRITIQUE" = "1" ]; then
  VIRTUAL_ENV="$VENV" uv pip install --quiet "$WHEEL[critique]" >/dev/null 2>&1 \
    && ok "[critique] extra installs" || bad "[critique] extra installs"
  check "doctor sees the critique extra" '"critique": true' "$VZ" doctor --json

  # Run from inside the sandbox: vizier reads `.env` from the working directory
  # upward, and this repo's own environment must not leak into the check.
  keyless() {
    ( cd "$SANDBOX" && env -u GEMINI_API_KEY -u OPENROUTER_API_KEY \
        -u ANTHROPIC_API_KEY -u OPENAI_API_KEY -u MINIMAX_API_KEY \
        -u DEEPSEEK_API_KEY HOME="$SANDBOX" "$@" )
  }
  # No keys at all: the ask must be specific about which key and where to put it.
  check "critique asks for a provider key" "GEMINI_API_KEY" \
    keyless "$VZ" critique /nonexistent.png
  check "critique points at .env" ".env" \
    keyless "$VZ" critique /nonexistent.png
  # With a text key but no vision key, the ask must move on to the captioner
  # rather than dying halfway through a paid call.
  check "critique asks for the vision key next" "MINIMAX_API_KEY" \
    keyless env GEMINI_API_KEY=test-not-a-real-key "$VZ" critique /nonexistent.png
  # And a fully-keyed run must get past preflight into the real work, where bad
  # input is still a message rather than a traceback.
  : > "$SANDBOX/chart.gif"
  check "a keyed run reaches the image check" "Unsupported image format" \
    keyless env GEMINI_API_KEY=test-not-a-real-key MINIMAX_API_KEY=test-not-a-real-key \
      "$VZ" critique "$SANDBOX/chart.gif"
  check "a missing image is a message, not a traceback" "No such image" \
    keyless env GEMINI_API_KEY=test-not-a-real-key MINIMAX_API_KEY=test-not-a-real-key \
      "$VZ" critique "$SANDBOX/not-here.png"
else
  skip "[critique] extra checks (pass --with-critique; pulls somm + onnxruntime)"
fi

# ---------------------------------------------------------------------------
say "Claude Code plugin"
if ! need claude; then
  skip "plugin checks (the \`claude\` CLI is not installed)"
elif ! need git; then
  skip "plugin checks (git is required to stage the plugin source)"
else
  # A marketplace source is cloned, so the test has to run against a commit,
  # not a dirty worktree. Stage the current tree as a throwaway repo.
  SRC="$SANDBOX/plugin-src"
  git -C "$REPO" ls-files -z | (cd "$REPO" && xargs -0 tar cf - 2>/dev/null) | (mkdir -p "$SRC" && tar xf - -C "$SRC")
  # include not-yet-committed plugin files so a dev run tests what's on disk
  for extra in .claude-plugin .mcp.json bin skills; do
    [ -e "$REPO/$extra" ] && cp -r "$REPO/$extra" "$SRC/" 2>/dev/null
  done
  git -C "$SRC" init -q 2>/dev/null
  git -C "$SRC" add -A >/dev/null 2>&1
  git -C "$SRC" -c user.email=install-test@local -c user.name=install-test \
      commit -qm "install-test staging" >/dev/null 2>&1 \
    && ok "plugin source staged as a git repo" || bad "plugin source staged as a git repo"

  MKT="$SANDBOX/marketplace/.claude-plugin"
  mkdir -p "$MKT"
  cat > "$MKT/marketplace.json" <<JSON
{
  "name": "install-test",
  "description": "Throwaway marketplace used by vizier's install test.",
  "owner": { "name": "install test" },
  "plugins": [
    {
      "name": "vizier",
      "description": "install-test copy of the vizier plugin",
      "source": { "source": "url", "url": "file://$SRC" },
      "license": "MIT",
      "category": "productivity"
    }
  ]
}
JSON

  check "plugin manifest validates" "Validation passed" \
    claude plugin validate "$SRC" --strict
  check "marketplace entry validates" "Validation passed" \
    claude plugin validate "$SANDBOX/marketplace" --strict
  check "marketplace adds" "Successfully added marketplace" \
    claude plugin marketplace add "$SANDBOX/marketplace"
  check "plugin installs" "Successfully installed plugin" \
    claude plugin install vizier@install-test
  check "plugin is enabled" "enabled" claude plugin list
  check "both skills are present" "chart-critique, chart-design" \
    claude plugin details vizier
  check "the MCP server is registered" "MCP servers (1)" \
    claude plugin details vizier

  # The bundled server has to start from the plugin's own launcher, with only
  # what a user would have on PATH.
  LAUNCHER="$(find "$CLAUDE_CONFIG_DIR/plugins/cache" -name vizier-mcp -type f 2>/dev/null | head -1)"
  if [ -n "$LAUNCHER" ] && [ -x "$LAUNCHER" ]; then
    ok "plugin launcher is executable after install"
    OUT="$(printf '%s\n' "$INIT" | PATH="$VENV/bin:$PATH" timeout 60 "$LAUNCHER" 2>&1 | head -c 2000)"
    printf '%s' "$OUT" | grep -q '"result"' \
      && ok "plugin launcher starts the MCP server" \
      || { bad "plugin launcher starts the MCP server"; printf '%s\n' "$OUT" | sed 's/^/      | /' | head -8; }
    # And it must say something useful when neither vizier nor uvx is reachable
    # — the launcher's own error path, with an empty PATH to force it.
    OUT="$(PATH="$SANDBOX/nothing-here" "$LAUNCHER" 2>&1; true)"
    printf '%s' "$OUT" | grep -q "uv tool install datavizier" \
      && ok "launcher explains itself when nothing is installed" \
      || { bad "launcher explains itself when nothing is installed"; printf '%s\n' "$OUT" | sed 's/^/      | /' | head -6; }
  else
    bad "plugin launcher is executable after install"
  fi

  claude plugin marketplace remove install-test >/dev/null 2>&1
fi

# ---------------------------------------------------------------------------
printf '\n\033[1m%s\033[0m\n' "$PASS passed, $FAIL failed, $SKIP skipped"
exit "$FAIL"
