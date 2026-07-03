# MCP setup — calling vizier from another Claude Code project

`vizier mcp` exposes the corpus query layer over stdio as an MCP server.
Once registered, agents in other sessions can call `search`,
`find_similar`, `get_pattern`, `list_patterns`, `list_principles`, etc.
as tools, instead of reading `corpus/<source>/*.md` files directly.

> **Before you register:** make sure `vizier db build` has run on this
> machine. The MCP tools all read from `corpus/.vizier.db`; if the DB is
> empty, every query returns nothing. `db build` is fast (~seconds)
> since v2. If you also want `find_similar` to work, run
> `vizier db embed` (slower — ~12 min on CPU).

## Claude Code (from another project)

The fastest path is `claude mcp add`. Run from the project that should
consume vizier:

```sh
cd /path/to/consuming-project
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
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/vizier", "run", "vizier", "mcp"]
    }
  }
}
```

Restart the client. Vizier's tools appear in the tool list.

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
| `list_principles`   | All weaver principles, optionally filtered by stage|
| `stats`             | DB row counts                                     |

## Troubleshooting

**`list_principles` returns empty.** The weaver ingester pulls
principles from `../weaver/PRINCIPLES.md`, but only if weaver exists
next to vizier. Run `uv run vizier ingest weaver`, then `uv run vizier db build`.

**`find_similar` returns empty.** You haven't run `vizier db embed` yet
(or the DB is otherwise missing embeddings). `vizier db stats` will show
`items` > `embeddings`. See note at the top of this file.

**`search` errors on queries with punctuation.** FTS5 treats hyphens
and apostrophes as tokens. Quote compound terms (`"forecast-cone"`) or
strip punctuation before querying. See `db_search` in `vizier/db/query.py`.

**MCP client can't find `uv`.** The command runs in the client's
environment, not your shell. Use the absolute path to uv:
`/Users/you/.local/bin/uv` (check `which uv`).

## Verifying the server stands up

```sh
# From vizier/:
uv run vizier mcp &
# The server speaks MCP-over-stdio; it logs nothing on success.
# Kill it: `kill %1`.
```

For a more thorough check, point any MCP-aware client at it and call
`stats` — it returns `{items, embeddings, sources}` and is the cheapest
round-trip.
