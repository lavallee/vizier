---
details:
  origin: weaver/PRINCIPLES.md
  stage: Ingest
fetched_at: '2026-04-18T19:23:27.592301Z'
id: principle-the-data-file-is-a-frozen-contract
source: weaver
tags:
- ingest
title: The data file is a frozen contract
type: principle
---

Once `data.json` is built, don't edit it by hand. All changes go
through `ingest`. This sounds pedantic; it's not — hand-edits silently
drift from the script, and six months later the script doesn't
reproduce the file.

Test: `ingest && diff` comes back clean. If it doesn't, the file has
been touched and the script is lying.

---
