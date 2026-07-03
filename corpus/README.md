# corpus/

Flat, file-backed store. One markdown file per corpus item; YAML
frontmatter holds structured fields; body holds free text (judges'
commentary, process writeup, critique body, principle text).

Layout:

    corpus/
      <source>/
        <item-slug>.md
      rubrics/
        <rubric-slug>.md  (for source='cairo', source='ft-vocab', ...)

Schema is defined in `src/vizier/schema.py` (pydantic). Item types:

| type | example source | what the body holds |
|---|---|---|
| `award_entry` | sigma, kantar, malofiej, snd | judges' / committee commentary |
| `process_note` | pudding, nyt, reuters, bloomberg | the practitioner's writeup |
| `critique` | junkcharts, eagereyes | the critique itself |
| `rubric` | cairo, ft-vocab | rubric description + axes in frontmatter |
| `principle` | weaver | principle body (from PRINCIPLES.md sections) |
| `artifact` | standalone | optional caption only |

**Rebuilding:** every item comes from a runnable ingest script in
`src/vizier/ingest/`. Don't hand-edit files — edit the script and re-ingest.
Following weaver's ingest convention.

**Caching:** HTML fetches are cached under `.fetch-cache/`, scoped to this repo
and git-ignored. Re-running an ingest is cheap.
