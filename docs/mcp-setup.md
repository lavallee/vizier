# MCP setup — calling vizier from another project

`vizier mcp` exposes the toolkit and the corpus query layer over stdio as
an MCP server. Once registered, agents in other sessions can call
`recommend_form`, `implementation_guide`, `get_pattern`, `analyze_artifact`,
`suggest_palette`, `search`, and the rest as tools.

> **The plugin does this for you.** `/plugin install vizier@lyra-forge`
> registers the server as part of the install — nothing below is needed
> unless you're wiring up a different client, or running against a source
> checkout. See the [install section](https://lavallee.github.io/vizier/#install).

> **The index is automatic.** vizier builds it from the packaged corpus on
> first use (a few seconds, no network), so `recommend_form` and the pattern
> tools work immediately after install. `vizier doctor` reports the item
> count. Only `find_similar` needs an extra step: `vizier db embed`
> (slower — ~12 min on CPU, and needs the `[search]` extra).

If the consuming project should also see a private or local corpus DB, point
Vizier at it with `VIZIER_PRIVATE_DB` or `VIZIER_EXTENSION_DBS` — one or more
SQLite DB paths separated by the platform path separator (`:` on macOS/Linux,
`;` on Windows). Vizier opens those DBs read-only and merges them into `search`,
`find_similar`, `lookup`, `list_sources`, `list_principles`, `list_rubrics`,
`list_patterns`, `get_pattern`, and `stats`. As a convenience, a DB placed in a
sibling `vizier-private/corpus/vizier-private.db` is auto-discovered without any
env var.

## Claude Code (without the plugin)

With vizier installed (`uv tool install datavizier`), one line from the
project that should consume it:

```sh
cd /path/to/consuming-project
claude mcp add vizier -- vizier mcp
```

Against a source checkout instead of an installed package:

```sh
claude mcp add vizier -- uv --directory /absolute/path/to/vizier run vizier mcp
```

This writes the server into that project's `.claude/settings.json`
under `mcpServers`. Verify with:

```sh
claude mcp list
# → should show `vizier` with the uv command
```

Inside a Claude Code session in that project, the tools appear as
`mcp__vizier__search`, `mcp__vizier__find_similar`, etc. Calling
`list_patterns` or `get_pattern` is a good smoke test.

## Claude Desktop / Cursor / claude.ai

Edit the client's MCP config (Claude Desktop: `~/Library/Application
Support/Claude/claude_desktop_config.json` on macOS) and add:

```json
{
  "mcpServers": {
    "vizier": {
      "command": "/absolute/path/to/vizier",
      "args": ["mcp"],
      "env": {
        "VIZIER_PRIVATE_DB": "/absolute/path/to/private/.vizier.db"
      }
    }
  }
}
```

`which vizier` gives you the absolute path — MCP clients run the command in
their own environment, not your shell's, so a bare `vizier` often won't
resolve. Against a source checkout, use `uv` instead:
`"command": "uv", "args": ["--directory", "/abs/path/to/vizier", "run", "vizier", "mcp"]`.

Omit `env` if an auto-discovered sibling `vizier-private` DB should be used
automatically. Use `"VIZIER_AUTO_PRIVATE": "0"` for a forced public-only run.
Restart the client.
Vizier's tools appear in the tool list.

## What the tools expose

| Tool                | Use for                                           |
|---------------------|---------------------------------------------------|
| `search`            | BM25 full-text across title + body                |
| `find_similar`      | Embedding cosine retrieval (needs `db embed`)     |
| `lookup`            | Fetch one item by `source` + `item_id`            |
| `list_sources`      | Source counts + type breakdown                    |
| `list_patterns`     | Chart-pattern index, optionally filtered by family|
| `get_pattern`       | One chart pattern with alternatives/examples resolved |
| `list_rubrics`      | All rubric items                                  |
| `list_principles`   | All corpus principles, optionally filtered by stage|
| `implementation_guide` | Form recommendation + journalism checks + prior-art signals |
| `stats`             | DB row counts                                     |

## Troubleshooting

**Start with `vizier doctor`.** It reports the corpus root, the index and its
item count, which extras are installed, and which provider keys are visible —
and names the command that fixes each gap. Most of the cases below show up
there first.

**Every query returns nothing.** The index is empty. It builds itself on
first use, so this means the build failed — run `vizier db build` to see the
error. A read-only cache directory is the usual cause; `VIZIER_DB_PATH` puts
the index somewhere writable.

**`list_principles` returns empty.** The weaver ingester pulls
principles from `../weaver/PRINCIPLES.md`, but only if weaver exists
next to vizier. Run `uv run vizier ingest weaver`, then `uv run vizier db build`.

**`find_similar` returns empty.** You haven't run `vizier db embed` yet
(or the DB is otherwise missing embeddings). `vizier db stats` will show
`items` > `embeddings`. See note at the top of this file.

**Private/local corpus items do not appear.** Check that `vizier db stats`
reports the extension DB under `extension_dbs`. If the DB is not in an
auto-discovered sibling `vizier-private/corpus/` location, pass
`VIZIER_PRIVATE_DB` or `VIZIER_EXTENSION_DBS` into the server process.

**`search` errors on queries with punctuation.** Bare hyphens, apostrophes,
commas, semicolons, and slashes are normalized before FTS5 runs. If a query
still errors, quote the exact phrase and check `vizier/db/query.py`.

**MCP client can't find `uv`.** The command runs in the client's
environment, not your shell. Use the absolute path to uv:
`/Users/you/.local/bin/uv` (check `which uv`).

**The plugin's MCP server won't connect.** The plugin launches
`bin/vizier-mcp`, which uses an installed `vizier` if there is one, falls back
to `uvx --from datavizier vizier mcp`, and prints install instructions if
neither is available. Run the launcher by hand to see which branch it takes —
`claude mcp list` shows its path.

## Verifying the server stands up

A real handshake, no client required:

```sh
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1"}}}' \
  | vizier mcp
```

A JSON object with a `result` key means the server is healthy. (This is what
`tests/install/run.sh` asserts.) For a fuller check, point any MCP-aware client
at it and call `stats` — it returns `{items, embeddings, sources}` and is the
cheapest round-trip.
