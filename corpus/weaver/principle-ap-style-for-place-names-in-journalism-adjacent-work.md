---
details:
  origin: weaver/PRINCIPLES.md
  stage: Narrate
fetched_at: '2026-04-18T19:23:27.594628Z'
id: principle-ap-style-for-place-names-in-journalism-adjacent-work
source: weaver
tags:
- narrate
title: AP style for place names in journalism-adjacent work
type: principle
---

If the output reads like reporting, use AP style consistently in charts,
tooltips, copy, and the prose:

- `Cupertino, Calif.` (not `Cupertino, CA`)
- `Ashtabula, Ohio` (not `Ashtabula, OH` — Ohio and Texas never abbreviated)
- `Maplewood, N.J.`

A one-line helper makes this free:

```js
const AP_STATE = { AL: 'Ala.', CA: 'Calif.', NJ: 'N.J.', OH: 'Ohio', TX: 'Texas', ... }
function apLabel(c) { return `${c.name}, ${AP_STATE[c.state] || c.state}` }
```

Then use `apLabel(c)` everywhere. Swapping conventions later is a
thousand tiny edits.
