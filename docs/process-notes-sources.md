# Practitioner walkthroughs — source tiering

> For *why* the corpus draws on these kinds of sources — award juries, structural
> critique, practitioner walkthroughs, canonical theory — and the philosophy behind
> distilling them into a determination, see [`INFLUENCES.md`](../INFLUENCES.md). This
> doc is the operational companion: where that content lives and how to ingest it.

The corpus is well-covered on *what passed* (jury commentary, award tiers,
curated winners). It is under-covered on *how decisions were made* — the
practitioner walkthrough, which is what teaches transferable judgment.
This doc tracks where that content lives, ranked by expected
yield × accessibility × genre breadth. Update as sources are added to
the corpus.

A walkthrough tells us:

- What the maker was trying to show
- What alternatives they considered
- Why they chose the form they chose
- What they compromised on
- What they'd change in hindsight

Compared to jury commentary ("these three won because X"), walkthroughs
teach the underlying reasoning. Vizier's corpus item type for these is
`process_note` (already used for Pudding + weaver). This is the highest-
leverage type to grow for the "1000 graphics → seasoned editor" goal.

## Malofiej-adjacent (the specific ask)

The Malofiej books themselves aren't digitized and are hard to acquire.
But a lot of book-adjacent commentary is retrievable:

| Source | What's there | Accessibility |
|---|---|---|
| **snd-e.com/en/malofiej/premios** | Winners 2010+ with creator descriptions + images | Already partially crawled; deeper pass would capture creator text |
| **Alberto Cairo blog** (thefunctionalart.com) | ~20 posts on Malofiej judging over years; jury-culture commentary | Public, wordpress-style, sitemap-crawlable |
| **YouTube: "Malofiej" / "SND-E"** | Presenter talks from Pamplona summits. Walk-through-your-own-piece format | Captions downloadable; transcripts extractable |
| **Visualoop.com (Wayback)** | Tiago Veloso's annual Malofiej roundups (2013–2017) | Wayback Machine; needs navigation |
| **Presenter post-mortems** | Individual designers (Fragapane, Accurat, Szucs, Wu, Arranz, Lupi) often publish their Malofiej talks as blog posts afterward | Per-author, scattered; build a curated list |
| **Malofiej books (Show, Don't Tell!)** | The gold standard — one book per summit (1993–2020) | Not digitized. Pratt, SVA, Cornell libraries carry some. Treat as aspirational. |

## Tier 1 — high yield, scrapable, genre-broadening

| Source | URL | What it is | Expected volume |
|---|---|---|---|
| **Source** | source.opennews.org | Practitioner case studies from newsrooms, 2012+. Every post answers "we built this, here's how we decided." | 1000+ items |
| **Nightingale** | nightingaledvs.com | Data Visualization Society magazine; interviews, process essays | ~500 items |
| **FT Chart Doctor** | ft.com/chart-doctor | Alan Smith's column, explicit "how we approached this / why this form" | ~150 columns; partially paywalled |
| **Observable** | observablehq.com | Annotated notebooks by top practitioners. Each is a decision-by-decision reveal | Curated list: ~500 high-star notebooks |

**Start here.** These are the biggest win per hour of ingest work.

## Tier 2 — medium yield, focused commentary

| Source | URL | Why it matters |
|---|---|---|
| **Visualising Data** | visualisingdata.com | Andy Kirk's "little of visualisation design" + "best of the visualisation web" + practitioner interviews |
| **Eagereyes** | eagereyes.org | Robert Kosara. Academic-practitioner hybrid. Deep analyses of specific pieces. |
| **Alberto Cairo blog** | thefunctionalart.com | Cairo's commentary + Malofiej-adjacent essays |
| **Junk Charts** | junkcharts.com | Already in corpus — but the *trifecta* posts are walkthrough-shaped and should be flagged as such |
| **ProPublica Nerd Blog** | propublica.org/nerds | Methodology posts from their graphics + data team |
| **NYT Open** (Wayback) | open.nytimes.com | NYT graphics team engineering blog. Archived but accessible. |
| **Reuters Graphics** | graphics.reuters.com | Occasional per-project methodology posts |

## Tier 3 — genre-expanding (not data-journalism-only)

| Source | What it adds |
|---|---|
| **Individual designer portfolios** | Federica Fragapane, Accurat, Pentagram, Shirley Wu, Giorgia Lupi, Krisztina Szucs, Adam Pearce, Adolfo Arranz — self-hosted project writeups. Print-tradition + illustrative + editorial genres missing from data-journalism-heavy sources. |
| **Behance infographic project pages** | Self-published; "project description" field is often extensive; variable quality; broad genre mix |
| **Kantar IIB full submission forms** | We have thin snippets. Full creator-written methodology fields would be richer but aren't public. |
| **Graphis Design Annual** | Paid print; classical information-design tradition |
| **D&AD case studies** | Ad-adjacent but has data-viz work; editorial commentary |

## Tier 4 — adjacent domains, harder to scale

| Source | Notes |
|---|---|
| **Conference talk transcripts** | OpenVisConf, OutlierConf, Tapestry, IEEE VIS, SNDMakes. YouTube auto-captions get us passable transcripts. 50 top-talks = ~30 hours of content. Per-talk work; do a curated pass. |
| **Podcast transcripts** | Data Stories (Bertini/Stefaner), PolicyViz (Schwabish). Interview format; practitioner decision-making. Some auto-transcribed; many need Whisper. |
| **IEEE VIS application papers** | A subset of academic papers are effectively practitioner walkthroughs of real deployed viz. Different register; same DNA. Retrievable from the usual academic indexes (arXiv, Semantic Scholar, OpenAlex, DOI). |

## Storage convention (new for this ingest pass)

For Tier 1+ walkthroughs, we store more than the prose — the original HTML
snapshot + referenced images. This matters because:

- Images in walkthroughs are often the artifact being discussed. Future
  vizier passes may want to feed those images to a captioner, a data-
  claim checker, or a visual-similarity layer.
- HTML preserves link structure, pull-quotes, embedded interactives
  (as `<iframe>` refs), code snippets.
- The markdown we extract is a lossy projection. Keeping the raw lets
  us re-extract under a different schema later without re-fetching.

Layout per item:

    corpus/<source>/
      <item-id>.md                 # primary record (frontmatter + body)
      _raw/<item-id>.html          # raw HTML snapshot (gitignored)
      _images/<item-id>/           # images from the post (gitignored)
        <n>-<slug>.<ext>

The markdown frontmatter carries `raw_html_path` and an `images` list
so downstream readers can find the rich content.

## Parallelism

Tier 1 sources are independent sites with different infrastructure.
Ingest them in parallel (one worker per source, HTTP-bound). Each source
module is self-contained and idempotent against its own cache.

## Priority ordering

For this round, in execution order:

1. **Source (opennews.org/source)** — biggest single win. ~1,129 articles discovered via paginated `/articles/?page=N` (no sitemap).
2. **Eagereyes + Visualising Data + Cairo** — three blogs in parallel. All sitemap-backed.
3. **SND** — category-scoped, not "SND.Ink" literal. The snd.org WordPress
   site has no isolable SND.Ink publication, so we crawl the eleven
   walkthrough-adjacent categories (data-visualization, digital-design,
   multi-media, newspaper/magazine-design, profiles, innovation,
   AR/VR/AI, illustrations, creative-conference-calls). Yields ~180
   unique posts after dedup.
4. **Nightingale** (DVS magazine) — Cloudflare-fronted, so the sitemap fetch
   needs the optional richer fetcher (`$VIZIER_FETCHER`); standard WP after
   that. ~740 posts.
5. **Observable** — notebooks; curated seed (20 practitioner profiles +
   /explore). Extraction parses the Next.js JSON blob to concat md + code
   cells. We drop notebooks with <300 chars of markdown (pure-code
   recipes aren't walkthroughs). ~350 notebooks from the seed.
6. ~~FT Chart Doctor~~ — **deferred**, hard paywall. Every fetch strategy
   fails (direct, googlebot-UA, archive, wayback, headless browser).
   Chart Doctor articles require an FT subscription to render. With
   credentials this could be revisited via a logged-in browser fetch.
7. **Tier 3 and 4** — as-needed, later.

## Ingester implementation notes (what we learned)

- **Sitemap shapes vary.** Eagereyes exposes a flat `/sitemap.xml` (583 URLs); Visualising Data uses a sitemap-index with per-type sub-sitemaps (~1,096 post URLs across two of them); Cairo's custom domain doesn't serve the sitemap, but the underlying `thefunctionalart.blogspot.com/sitemap.xml` does (~734 posts).
- **Source has no sitemap.** Paginated `/articles/?page=N` walks until 404. Pages return ~20 URLs each, tail page is partial; safe cap is page 80.
- **Blogger-era posts use `<div>`+`<br>` rather than `<p>`.** `_fetch_html.html_to_markdown` falls back to `<br>`-split text when structural markdown would be empty — without this Cairo's pre-2020 archive extracts as zero-length.
- **Article selectors are site-specific.** Visualising Data is built on Elementor; the body lives in `.elementor-widget-theme-post-content`, not `article` or `main`. The shared blog ingester's `article_selectors` list is tried in order — keep the Elementor/Blogger/WP-specific selectors up front.
- **Min-body thresholds must bend per-site.** The default 400-char minimum is right for Source/Eagereyes/VisData but drops a third of Cairo's posts (short reflections). Cairo's config drops it to 150.

Update this doc when something ingests well or fails in instructive ways.
