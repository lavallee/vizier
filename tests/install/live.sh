#!/usr/bin/env bash
# Live check — does the plugin actually change what an agent does?
#
# `run.sh` proves the plugin installs and registers. It can't prove the part
# that matters: that `chart-design` fires when someone asks for a chart, and
# that the answer comes from vizier's corpus rather than the model's habits.
# This runs real headless `claude` sessions against a sandbox install and
# reports which skills and tools fired.
#
# It costs tokens and needs you to be logged in, so it is deliberately separate
# from `run.sh` and never runs in CI.
#
# Usage:
#   tests/install/live.sh                    # the standard prompts
#   tests/install/live.sh "your own prompt"  # one prompt of your choosing
#
# Side effects: the plugin is installed at *local* scope inside a temp
# directory, so your user settings are untouched. Claude's shared plugin cache
# (~/.claude/plugins/cache) does get an entry, as it would for any install.

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SANDBOX="$(mktemp -d "${TMPDIR:-/tmp}/vizier-live-test.XXXXXX")"
trap 'rm -rf "$SANDBOX"' EXIT

PASS=0; FAIL=0
say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()  { PASS=$((PASS+1)); printf '  \033[32m✔\033[0m %s\n' "$*"; }
bad() { FAIL=$((FAIL+1)); printf '  \033[31m✘\033[0m %s\n' "$*"; }

command -v claude >/dev/null || { echo "the \`claude\` CLI is required" >&2; exit 70; }
command -v uv >/dev/null || { echo "uv is required" >&2; exit 70; }

say "Sandbox"
mkdir -p "$SANDBOX/work"
echo "  $SANDBOX"

# Install the CLI the plugin's skills drive.
uv build --wheel --out-dir "$SANDBOX/dist" "$REPO" >/dev/null 2>&1
uv venv "$SANDBOX/venv" --python 3.12 >/dev/null 2>&1
VIRTUAL_ENV="$SANDBOX/venv" uv pip install --quiet "$(ls "$SANDBOX"/dist/*.whl | head -1)" >/dev/null 2>&1
export PATH="$SANDBOX/venv/bin:$PATH"
export XDG_CACHE_HOME="$SANDBOX/cache"
vizier recommend-form "smoke" >/dev/null 2>&1   # warm the index outside the timed run

# Stage the working tree as a git repo — marketplace sources are cloned.
SRC="$SANDBOX/plugin-src"
mkdir -p "$SRC"
tar cf - -C "$REPO" --exclude=.git --exclude=.venv --exclude=dist \
    --exclude=.playwright-mcp --exclude=corpus/.vizier.db . 2>/dev/null | tar xf - -C "$SRC"
git -C "$SRC" init -q
git -C "$SRC" add -A >/dev/null 2>&1
git -C "$SRC" -c user.email=live@local -c user.name=live commit -qm live >/dev/null 2>&1

mkdir -p "$SANDBOX/marketplace/.claude-plugin"
cat > "$SANDBOX/marketplace/.claude-plugin/marketplace.json" <<JSON
{
  "name": "vizier-live",
  "description": "Throwaway marketplace for vizier's live check.",
  "owner": { "name": "live check" },
  "plugins": [
    {
      "name": "vizier",
      "description": "live check copy of the vizier plugin",
      "source": { "source": "url", "url": "file://$SRC" },
      "license": "MIT",
      "category": "productivity"
    }
  ]
}
JSON

cd "$SANDBOX/work"
# Local scope: the marketplace and the enablement land in this temp directory's
# .claude/settings.local.json, not in your user settings.
claude plugin marketplace add "$SANDBOX/marketplace" --scope local >/dev/null 2>&1
claude plugin install vizier@vizier-live --scope local >/dev/null 2>&1
claude plugin details vizier 2>/dev/null | grep -q "chart-design" \
  && ok "plugin installed at local scope" || bad "plugin installed at local scope"

ALLOWED=(--allowedTools "Skill" "Bash(vizier:*)" "mcp__plugin_vizier_vizier" "Write" "Read")

# run_prompt <label> <expect-skill|-> <prompt>
run_prompt() {
  local label="$1" expect="$2" prompt="$3"
  say "$label"
  printf '  prompt: %s\n' "$prompt"
  local trace="$SANDBOX/trace.txt"
  timeout 900 claude -p "$prompt" "${ALLOWED[@]}" --max-turns 20 \
    --output-format stream-json --verbose 2>/dev/null \
    | python3 -c "
import json,sys
for line in sys.stdin:
    try: d = json.loads(line)
    except Exception: continue
    msg = d.get('message')
    content = msg.get('content') if isinstance(msg, dict) else None
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'tool_use':
                name = c['name']
                if name == 'Skill':
                    name = 'Skill:' + str((c.get('input') or {}).get('skill'))
                print('TOOL ' + name)
    if d.get('type') == 'result':
        print('RESULT ' + json.dumps(d.get('result') or ''))
" > "$trace"

  grep '^TOOL' "$trace" | sed 's/^TOOL /    · /' | sort -u

  if [ "$expect" != "-" ]; then
    # Plugin skills arrive namespaced as `vizier:<name>`; a bare name is what
    # you see for a skill invoked from a local skills directory.
    grep -qE "^TOOL Skill:(vizier:)?$expect\$" "$trace" \
      && ok "$expect fired" \
      || bad "$expect did not fire (another skill or none won the trigger)"
  fi
  grep -qE "^TOOL (mcp__plugin_vizier_vizier|Bash)" "$trace" \
    && ok "vizier was actually consulted" \
    || bad "vizier was never consulted — the answer came from the model alone"

  python3 - "$trace" <<'PY'
import json, sys
text = ""
for line in open(sys.argv[1]):
    if line.startswith("RESULT "):
        text = json.loads(line[7:])
print("\n  --- answer (first 500 chars) ---")
print("  " + text[:500].replace("\n", "\n  "))
PY
}

if [ "$#" -gt 0 ]; then
  run_prompt "Custom prompt" "-" "$*"
else
  run_prompt "Building a chart" "chart-design" \
    "Build me an HTML chart showing how each of five school districts splits its budget across four funds. Save it as budget.html."
  run_prompt "Choosing a form" "chart-design" \
    "I have monthly revenue for 9 product lines over 3 years. What chart should I use?"
  run_prompt "Critiquing a chart" "chart-critique" \
    "Review budget.html and tell me whether it's misleading."
fi

printf '\n\033[1m%s\033[0m\n' "$PASS passed, $FAIL failed"
exit "$FAIL"
