// Chart-forms guide — hash-routed multi-view reader.
//
// Routes:
//   #/                               — root: family grid TOC
//   #/family/<slug>                  — family page: all patterns in that family
//   #/family/<slug>/<pattern-id>     — same page, scrolled to that pattern
//
// Cross-family "jump →" links resolve to the target pattern's primary
// (first-listed) family, so `#/family/<primary-family>/<target-pat>`.
//
// Reader's mental model: arrive at TOC, pick a purpose, read the
// handful of patterns under it in full. "Instead, reach for..."
// alternatives transclude their capsules AND link to the right page.

import data from './data.json'
import { DEMO_BY_ID, INTERACTIVE_PATTERNS, renderDistributionTriad, renderSpatialTriad } from './live-examples.js'
import { GLOSSARY, linkifyGlossary } from './glossary.js'
import interactivityMdRaw from './INTERACTIVITY.md?raw'

// Caption text to display under each live demo.
const DEMO_CAPTIONS = {
  'bar-chart':      'Streaming subscribers (M). Bars sorted by magnitude — that\'s the work a bar chart does.',
  'stacked-bar':    'Department budgets ($M) split by cost category. Widths share a baseline so cross-department totals read first.',
  'scatterplot':    'Life expectancy × GDP per capita (log scale, synthetic sample of 80). The relationship — and the spread around it — is the story.',
  'bump-chart':     'Brand rank over five years. The crossings are the story; line 3/4/5 reshuffle while the top two stay fixed.',
  'sankey':         'Electricity mix: five sources → four end-uses, with the inevitable Losses bucket. Total left = total right.',
  'heatmap':        'Web traffic heatmap — day of week × hour of day. The evening weekday surge and weekend afternoon pocket pop immediately.',
  'line-chart':     'Three macro series over 20 years. Right-edge labels (not a legend) so the reader never loses track of which line is which.',
  'small-multiples':'Monthly rainfall for 9 cities — same axes across panels lets climate contrasts pop (Seattle + Portland winter rains vs Miami summer spike vs Phoenix flatline).',
  'slope-chart':    'Test scores before → after a curriculum change. Big movers highlighted (green climbs, red drop); the rest muted so the story stays legible.',
  'histogram':      'Synthetic response times (n=500). The right-skew is visible instantly; bin count chosen to reveal the peak without sawtooth noise.',
  'treemap':        'US federal outlay by category — a big-picture hierarchy. Squarified layout keeps tiles close to square so small categories stay readable.',
  'diverging-bar':  'Employee survey, Likert 1–5. Neutral straddles the axis, disagree to the left, agree to the right. Items sorted or not — color does the work.',
  'parallel-sets':  '1,000 survey respondents crossed by political lean × news source × trust. Ribbons show joint frequencies; axis order is editorial, not causal.',
  'boxplot':        'Six synthetic groups. Boxes = Q1–Q3, white line = median, whiskers = 1.5×IQR, red dots = outliers. Shape collapses — that\'s the tradeoff.',
  'violin':         'Same 6 groups; groups A and E are secretly bimodal. Violins reveal the two modes where a boxplot would report a single blob.',
  'dot-plot':       'Median home price across 18 Bay Area neighborhoods. Many-category comparison where a bar chart would feel visually heavy.',
  'pie-chart':      'Same smartphone market share shown two ways. Left: pie (angles hard to compare). Right: sorted bars (ranking obvious).',
  'waffle-chart':   '"1 in 8" is abstract; 12 filled squares out of 100 is concrete. Narrative forms win on human scale even when they lose on precision.',
  'chord-diagram':  'Bilateral migration between 6 regions. Arc width = regional outflow; ribbons show the pair volumes. Ring layout avoids hairball at N=6.',
  'streamgraph':    '20 years of music genre share. Rock declines, Hip-Hop rises, Electronic emerges — envelope shape is the feature, precise values beside the point.',
  'ridgeline':      'Annual temperature distributions across 12 US cities, sorted by mean. Visible at a glance: Miami\'s tight band, Minneapolis\'s long tails.',
  'connected-scatter': 'Unemployment × inflation, US 2000–2023. 2009 and 2020–2022 are visibly different from steady-state years; the path is the story.',
  'mosaic':         'Smoking × exercise survey. Cell sizes encode joint frequency; diverging hues shade by departure from independence (green over, red under).',
  'dot-map':        'Synthetic incident clusters across CONUS. Each dot is one observation — no aggregation, no invented structure. Clusters around metros pop.',
  'choropleth':     'Hex-grid US with synthetic %-bachelor\'s-or-higher per state. Equal-area layout sidesteps the "Wyoming eats California" trap.',
  'hex-bin-map':    'Same hex grid, different story: 2024 presidential margin per state. Each state one cell — Wyoming and California visually equal.',
  'cartogram':      'Dorling-style: circles sized by state population, placed at roughly-geographic positions and nudged apart. Area = the metric; location = "close enough to geography."',
  'proportional-symbol-map': '29 largest US metros, circles area-scaled to population. Real geography kept; magnitudes encoded as area rather than via area-distortion.',
  'flow-map':       'Stylized interstate migration between 8 metros — thickness = migrants/year. Geography is the substrate; arrowheads scale with stroke.',
  'strip-plot':     'Salaries across four levels (n=76). Beeswarm layout shows every point; dashed median line per group. Better than a boxplot at small sample sizes.',
  'arc-diagram':    '12 novel characters ordered by first appearance; arcs are co-occurrences, thickness by frequency, color by distance between characters.',
  'network-diagram':'3 cluster-dense collaboration network (design, engineering, research). Intra-cluster edges are thick/dark, inter-cluster edges thin — community structure emerges from the force layout.',
  'matrix-plot':    'Adjacency matrix of bilateral migration between 6 regions (same data as the chord-diagram demo). Precise pair reading; diagonal blanked to mark self-loops.',
  'sunburst':       'US federal budget laid out radially: inner ring Mandatory/Discretionary/Interest; outer ring the categories. Depth-encoded by ring.',
  'icicle-plot':    'Same US federal budget hierarchy, rectangular layout. Reader scans top-down instead of radially — easier to read precise widths.',
  'stacked-area':   'Energy-source share over 20 years. Renewables rise, coal declines. Zero-based baseline keeps magnitudes legible; right-edge labels never drop.',
  'radar-chart':    'Two basketball archetypes across six percentile-rank axes. Outlined (not filled!) — the fill area would lie, as the polygon shape already overstates differences. This is the rare case the form earns its keep.',
  'calendar-heatmap':'One year of synthetic "commits per day". The weekday/weekend rhythm pops as horizontal bands; the July-August trough shows seasonality; holiday week in late December reads as a distinct gap. Monotone green, not rainbow.',
  'lollipop-chart': 'CO₂ per capita across 24 countries. Stems hair-thin so dots do the work; sorted high→low. Zero-based — the stems would lie otherwise. A bar chart of 24 bars would feel like a wall; a dot plot alone loses the baseline anchor.',
  'box-and-jitter-strip': 'Five groups with varying N and shape — uniform, bimodal, long-tail, sparse (n=8), skewed. The sparse column especially shows the hybrid\'s value: 8 dots tell you what the boxplot alone could never.',
  'dendrogram':     '12 US cities clustered by (temperature, rainfall) with single-linkage. Branch height = merge distance. The dashed cut-line at distance 1.2 groups them into ~4 clusters: Pacific NW, coastal CA, Southwest/Midwest, Southeast.',
  'gantt-chart':    'Synthetic 12-task magazine-issue schedule. Critical-path tasks amber, others blue; completion shaded inside planned-outline bars; milestones as diamonds. A "today" line at day 11 anchors the reader.',
  'marimekko':      'Beverage-industry view: 5 markets (column widths = $B) × 4 brands (stack heights = share). Brand A owns small markets (SE Asia 42%) but barely shows in China. Consistent stack order across columns; desaturated palette so the saturated Brand A reads as the headline.',
}

// ------------------------------ taxonomy
const FAMILY_QUESTIONS = {
  Flow:              "What moves, from where to where?",
  "Part-to-whole":   "How does this split up?",
  Ranking:           "What's the order?",
  Distribution:      "What does the spread look like?",
  "Change over time":"How has it changed?",
  Magnitude:         "Which is bigger?",
  Spatial:           "Where?",
  Correlation:       "Do these move together?",
  Deviation:         "How far from a reference?",
}
const FAMILY_ORDER = [
  "Flow", "Part-to-whole", "Ranking", "Change over time",
  "Magnitude", "Distribution", "Correlation", "Spatial", "Deviation",
]
const ANTIPATTERN_IDS = new Set(["pie-chart"])

const slug = name => name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const FAMILY_BY_SLUG = Object.fromEntries(FAMILY_ORDER.map(f => [slug(f), f]))
const slugOf = name => slug(name)

function primaryFamily(pat) {
  return (pat.purpose_families && pat.purpose_families[0]) || null
}
function patternHref(pat) {
  const f = primaryFamily(pat)
  if (!f) return `#/`
  return `#/family/${slugOf(f)}/${pat.id}`
}
function familyHref(name) { return `#/family/${slugOf(name)}` }

// ------------------------------ DOM helpers
const page = document.getElementById('page')
const crumb = document.getElementById('breadcrumb')

function el(tag, attrs = {}, children = []) {
  const n = document.createElement(tag)
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'className') n.className = v
    else if (k === 'html') n.innerHTML = v
    else if (k.startsWith('on')) n.addEventListener(k.slice(2).toLowerCase(), v)
    else if (v != null) n.setAttribute(k, v)
  }
  for (const c of [].concat(children)) {
    if (c == null) continue
    n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c)
  }
  return n
}

// Guard against YAML accidentally parsing a bullet with `foo: bar` as a
// dict — coerce anything non-string back to a string so the reader
// never shows "[object Object]".
function stringify(v) {
  if (typeof v === 'string') return v
  if (v && typeof v === 'object') {
    return Object.entries(v).map(([k, val]) => `${k}: ${val}`).join(' ')
  }
  return String(v)
}

function mdBodyToHtml(body) {
  const paras = (body || '').split(/\n\n+/).map(s => s.trim()).filter(Boolean)
  return paras.map(p => {
    let html = p
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
    return `<p>${html}</p>`
  }).join('')
}

// Richer markdown renderer for prose docs (INTERACTIVITY.md, etc). Handles
// h1–h4, bullet + numbered lists, horizontal rules, blockquotes, paragraphs,
// inline code, bold, italic, and [text](url) links. Not a full implementation;
// just enough for our working-doc style.
function mdDocToHtml(src) {
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  function inline(s) {
    // Escape first, then re-parse specific patterns (they use escaped chars).
    let t = esc(s)
    // Inline code must come before italic/bold so `*foo*` inside code doesn't parse
    t = t.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`)
    t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    t = t.replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Links [text](url)
    t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) =>
      `<a href="${url}" target="_blank" rel="noopener">${text}</a>`)
    return t
  }

  const lines = src.split('\n')
  const out = []
  let para = []
  let list = null       // { type: 'ul' | 'ol', items: [] }
  let listItem = null   // current item (string[])
  let quote = null      // blockquote lines

  function flushPara() {
    if (para.length) {
      out.push(`<p>${inline(para.join(' '))}</p>`)
      para = []
    }
  }
  function flushList() {
    if (!list) return
    if (listItem) { list.items.push(listItem.join(' ')); listItem = null }
    const tag = list.type
    out.push(`<${tag}>${list.items.map(x => `<li>${inline(x)}</li>`).join('')}</${tag}>`)
    list = null
  }
  function flushQuote() {
    if (quote && quote.length) {
      out.push(`<blockquote>${inline(quote.join(' '))}</blockquote>`)
      quote = null
    }
  }
  function flushAll() { flushPara(); flushList(); flushQuote() }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i]
    const line = raw.trimEnd()
    // Horizontal rule
    if (/^\s*---+\s*$/.test(line)) {
      flushAll()
      out.push('<hr>')
      continue
    }
    // Heading
    const h = line.match(/^(#{1,4})\s+(.*)$/)
    if (h) {
      flushAll()
      const level = h[1].length
      out.push(`<h${level}>${inline(h[2])}</h${level}>`)
      continue
    }
    // Bullet list
    const ul = line.match(/^\s*[-*]\s+(.*)$/)
    if (ul) {
      flushPara(); flushQuote()
      if (!list || list.type !== 'ul') { flushList(); list = { type: 'ul', items: [] } }
      if (listItem) list.items.push(listItem.join(' '))
      listItem = [ul[1]]
      continue
    }
    // Numbered list
    const ol = line.match(/^\s*\d+\.\s+(.*)$/)
    if (ol) {
      flushPara(); flushQuote()
      if (!list || list.type !== 'ol') { flushList(); list = { type: 'ol', items: [] } }
      if (listItem) list.items.push(listItem.join(' '))
      listItem = [ol[1]]
      continue
    }
    // Blockquote
    const bq = line.match(/^>\s?(.*)$/)
    if (bq) {
      flushPara(); flushList()
      quote = quote || []
      quote.push(bq[1])
      continue
    }
    // Continuation of current list item (indented, within a list)
    if (list && listItem && /^\s+\S/.test(line)) {
      listItem.push(line.trim())
      continue
    }
    // Blank line — close current block
    if (line.trim() === '') {
      flushAll()
      continue
    }
    // Plain paragraph content
    flushList(); flushQuote()
    para.push(line)
  }
  flushAll()
  return out.join('\n')
}

// ------------------------------ renderers

function setBreadcrumb(parts) {
  crumb.innerHTML = ''
  parts.forEach((p, i) => {
    if (i) crumb.appendChild(el('span', { className: 'sep' }, '›'))
    if (p.href) crumb.appendChild(el('a', { href: p.href }, p.label))
    else crumb.appendChild(el('span', {}, p.label))
  })
}

// Primary recommendations per family — opinionated "what to reach for
// first." A reader asking the family question wants a 1-3 item shortlist,
// not the full roster. The family grid below still shows the full list.
const PRIMARY_RECOMMENDATIONS = {
  Flow:              ["sankey", "flow-map", "chord-diagram"],
  "Part-to-whole":   ["stacked-bar", "waffle-chart", "treemap"],
  Ranking:           ["bar-chart", "slope-chart", "bump-chart"],
  "Change over time":["line-chart", "small-multiples", "slope-chart"],
  Magnitude:         ["bar-chart", "dot-plot"],
  Distribution:      ["histogram", "boxplot", "violin"],
  Correlation:       ["scatterplot", "heatmap", "connected-scatter"],
  Spatial:           ["choropleth", "proportional-symbol-map", "hex-bin-map"],
  Deviation:         ["diverging-bar"],
}

function renderDecideLadder() {
  const wrap = el('div', { className: 'decide-ladder' }, [
    el('h3', {}, 'Decide by question'),
    el('p', { className: 'intro', html:
      'Start from what your reader is asking. These are the ' +
      'primary forms for each question; jump to a family card below ' +
      'for the full roster. See also: <a href="#/compare" style="color:#c7d2fe;text-decoration:underline;">same data, different forms</a>.'
    }),
  ])
  for (const fam of FAMILY_ORDER) {
    const ids = PRIMARY_RECOMMENDATIONS[fam] || []
    const patterns = ids.map(id => data.patterns[id]).filter(Boolean)
    if (!patterns.length) continue
    const row = el('div', { className: 'decide-row' }, [
      el('div', { className: 'decide-q' }, [
        document.createTextNode(FAMILY_QUESTIONS[fam] || ''),
        el('span', { className: 'fam' }, [
          el('a', { href: familyHref(fam) }, fam + ' →'),
        ]),
      ]),
      el('span', { className: 'decide-arrow' }, '→'),
    ])
    const chips = el('div', { className: 'decide-chips' })
    for (const p of patterns) {
      const isAnti = ANTIPATTERN_IDS.has(p.id)
      chips.appendChild(el('a', {
        className: 'pattern-chip' + (isAnti ? ' antipattern' : ''),
        href: `#/family/${slugOf(fam)}/${p.id}`,
      }, p.title))
    }
    row.appendChild(chips)
    wrap.appendChild(row)
  }
  return wrap
}

// Lazy thumbnail rendering. Each pattern card has a .thumb-host with
// a data-pattern-id; the observer renders the demo into the host as
// it scrolls into view. Always passes interactive:false — thumbnails
// don't want hover handlers OR slider widgets, even for demos that
// aren't toggle-aware on family pages (histogram/ridgeline/strip).
let thumbObserver = null
function ensureThumbObserver() {
  if (thumbObserver) return thumbObserver
  thumbObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue
      const host = entry.target
      thumbObserver.unobserve(host)
      const id = host.dataset.patternId
      const fn = DEMO_BY_ID[id]
      if (!fn) continue
      try {
        fn(host, { interactive: false })
      } catch (e) {
        console.error('thumbnail render failed', id, e)
      }
    }
  }, { rootMargin: '300px 0px' })
  return thumbObserver
}

function renderPatternCard(pat) {
  const isAnti = ANTIPATTERN_IDS.has(pat.id)
  const card = el('a', {
    className: 'pattern-thumb-card' + (isAnti ? ' antipattern' : ''),
    href: patternHref(pat),
  })
  const thumb = el('div', { className: 'thumb' })
  const host = el('div', { className: 'thumb-host', 'data-pattern-id': pat.id })
  // Placeholder text until the observer fires; swapped for SVG on render.
  if (!DEMO_BY_ID[pat.id]) {
    host.appendChild(el('div', { className: 'thumb-empty' }, '— no demo —'))
  }
  thumb.appendChild(host)
  card.appendChild(thumb)
  const body = el('div', { className: 'card-body' }, [
    el('div', { className: 'card-title' }, pat.title),
  ])
  if (pat.capsule) {
    body.appendChild(el('div', { className: 'card-capsule' }, (pat.capsule || '').trim()))
  }
  if (isAnti) {
    body.appendChild(el('div', { className: 'card-flag' }, 'antipattern'))
  }
  card.appendChild(body)
  if (DEMO_BY_ID[pat.id]) ensureThumbObserver().observe(host)
  return card
}

function renderRoot() {
  setBreadcrumb([{ label: 'Chart forms' }])
  page.innerHTML = ''

  // Opinionated decide-by-question ladder first
  page.appendChild(renderDecideLadder())

  // Bucket each pattern under its primary family for the roster grid.
  // Cross-family relevance is preserved on each pattern page (the
  // "Also relevant for" line) and via the decide-ladder above; the
  // root grid is honest about each pattern having one home.
  const primaryByFamily = {}
  for (const p of Object.values(data.patterns)) {
    const f = primaryFamily(p)
    if (!f) continue
    if (!primaryByFamily[f]) primaryByFamily[f] = []
    primaryByFamily[f].push(p)
  }
  for (const f of Object.keys(primaryByFamily)) {
    primaryByFamily[f].sort((a, b) => a.title.localeCompare(b.title))
  }

  // Roster heading
  page.appendChild(el('div', { className: 'roster-heading' }, [
    el('h2', {}, 'Full roster — browse by purpose family'),
    el('div', { className: 'roster-sub' },
      'Each card is a pattern with its one-line capsule and a static demo. ' +
      'Click in for the live, interactive version, when-to / when-not, common mistakes, and alternatives.'
    ),
  ]))

  // Family TOC pill row — scroll-jumps to the section anchors below.
  // Doesn't change the URL hash so it doesn't fight the route() handler.
  const toc = el('div', { className: 'family-toc' })
  toc.appendChild(el('span', { className: 'family-toc-label' }, 'Jump to'))
  for (const f of FAMILY_ORDER) {
    if (!primaryByFamily[f]?.length) continue
    const anchor = `fam-${slugOf(f)}`
    toc.appendChild(el('a', {
      className: 'family-toc-pill',
      href: `#${anchor}`,
      onClick: (e) => {
        e.preventDefault()
        document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      },
    }, f))
  }
  page.appendChild(toc)

  // Family sections with thumbnail card grids
  for (const f of FAMILY_ORDER) {
    const patterns = primaryByFamily[f] || []
    if (!patterns.length) continue
    const sec = el('section', { className: 'family-section', id: `fam-${slugOf(f)}` })
    sec.appendChild(el('div', { className: 'fam-head' }, [
      el('h3', {}, [
        el('a', { href: familyHref(f) }, f),
      ]),
      el('div', { className: 'fam-q' }, FAMILY_QUESTIONS[f] || ''),
    ]))
    const grid = el('div', { className: 'pattern-grid' })
    for (const p of patterns) grid.appendChild(renderPatternCard(p))
    sec.appendChild(grid)
    page.appendChild(sec)
  }

  // Cross-cutting reference links
  page.appendChild(el('div', {
    className: 'reference-links',
    style: 'margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid #1a1a1a;display:flex;gap:1.8rem;flex-wrap:wrap;font-size:0.85rem;',
  }, [
    el('a', { href: '#/compare', style: 'color:#c7d2fe;text-decoration:none;' }, 'Compare · same data, different forms →'),
    el('a', { href: '#/glossary', style: 'color:#c7d2fe;text-decoration:none;' }, 'Glossary · cross-cutting terms →'),
    el('a', {
      href: '#/interactivity',
      style: 'color:#c7d2fe;text-decoration:none;',
    }, 'Interactivity principles →'),
  ]))
}

function renderPatternSection(pat) {
  const sec = el('section', { className: 'pattern', id: `pat-${pat.id}` })

  // Header (eyebrow + title)
  sec.appendChild(el('div', { className: 'pattern-header' }, [
    el('div', { className: 'pattern-eyebrow' }, pat.purpose_families?.flatMap((f, i) => {
      const a = el('a', {
        href: familyHref(f),
        style: 'color:inherit;text-decoration:none;',
      }, f)
      return i === 0 ? [a] : [el('span', { className: 'fam-sep' }, '·'), a]
    }) || []),
    el('h2', {}, pat.title),
  ]))

  // Capsule
  if (pat.capsule) {
    sec.appendChild(el('div', { className: 'capsule' }, (pat.capsule || '').trim()))
  }

  // Live demo (if a renderer is registered for this pattern id)
  const demoFn = DEMO_BY_ID[pat.id]
  if (demoFn) {
    const isInteractive = INTERACTIVE_PATTERNS.has(pat.id)
    const header = el('div', { className: 'demo-header' }, [
      el('div', { className: 'eyebrow' }, 'Live demo'),
    ])
    // Static / interactive toggle — only when the renderer supports both.
    // Default is interactive (P2: reader opts out, not in).
    let currentMode = 'interactive'
    const host = el('div')
    if (isInteractive) {
      const toggle = el('div', { className: 'mode-toggle' })
      const btnI = el('button', { className: 'mode-btn is-on', type: 'button' }, 'interactive')
      const btnS = el('button', { className: 'mode-btn', type: 'button' }, 'static')
      function setMode(mode) {
        if (mode === currentMode) return
        currentMode = mode
        btnI.classList.toggle('is-on', mode === 'interactive')
        btnS.classList.toggle('is-on', mode === 'static')
        host.innerHTML = ''
        try {
          demoFn(host, { interactive: mode === 'interactive' })
        } catch (e) { console.error('demo failed', pat.id, e) }
      }
      btnI.addEventListener('click', () => setMode('interactive'))
      btnS.addEventListener('click', () => setMode('static'))
      toggle.appendChild(btnI); toggle.appendChild(btnS)
      header.appendChild(toggle)
    }
    const block = el('div', { className: 'live-demo' }, [header])
    block.appendChild(host)
    const caption = DEMO_CAPTIONS[pat.id]
    if (caption) block.appendChild(el('div', { className: 'hint' }, caption))
    sec.appendChild(block)
    // Defer render so container has layout
    requestAnimationFrame(() => {
      try {
        demoFn(host, isInteractive ? { interactive: currentMode === 'interactive' } : undefined)
      } catch (e) { console.error('demo failed', pat.id, e) }
    })
  }

  // wu/wn
  if ((pat.when_to_use?.length) || (pat.when_not_to_use?.length)) {
    sec.appendChild(el('div', { className: 'wu-wn' }, [
      el('div', { className: 'wu', html:
        `<h4>When to reach for it</h4><ul>${
          (pat.when_to_use || []).map(s => `<li>${stringify(s)}</li>`).join('')
        }</ul>` }),
      el('div', { className: 'wn', html:
        `<h4>When not</h4><ul>${
          (pat.when_not_to_use || []).map(s => `<li>${stringify(s)}</li>`).join('')
        }</ul>` }),
    ]))
  }

  // body
  if (pat.body) {
    sec.appendChild(el('div', { className: 'body', html: mdBodyToHtml(pat.body) }))
  }

  // reading_checklist — decoding questions the reader should ask
  if (pat.reading_checklist?.length) {
    sec.appendChild(el('div', { className: 'checklist', html:
      `<h4>How to read it · questions to ask</h4><ol>${
        (pat.reading_checklist || []).map(s => `<li>${stringify(s)}</li>`).join('')
      }</ol>`
    }))
  }

  // common_mistakes (cosmetic/config traps, separate from "when not to use")
  if (pat.common_mistakes?.length) {
    sec.appendChild(el('div', { className: 'mistakes', html:
      `<h4>Common mistakes (even when the form fits)</h4><ul>${
        (pat.common_mistakes || []).map(s => `<li>${stringify(s)}</li>`).join('')
      }</ul>`
    }))
  }

  // alternatives
  if (pat.alternatives?.length) {
    const wrap = el('div', { className: 'alternatives' }, [
      el('h4', {}, 'Instead, reach for'),
    ])
    for (const a of pat.alternatives) {
      const alt = el('div', { className: 'alt' })
      const title = a.title || `(not yet documented: ${a.id})`
      const hdr = el('div', { className: 'alt-hdr' }, [
        el('strong', {}, title),
        a.when ? el('span', { className: 'when' }, ' — ' + a.when) : null,
      ])
      if (a.title) {
        // Link to the target pattern on its primary family's page.
        const targetPat = data.patterns[a.id]
        if (targetPat) {
          hdr.appendChild(el('a', {
            className: 'jump',
            href: patternHref(targetPat),
          }, 'jump →'))
        }
      }
      alt.appendChild(hdr)
      if (a.capsule) {
        alt.appendChild(el('div', { className: 'alt-capsule' }, (a.capsule || '').trim()))
      }
      wrap.appendChild(alt)
    }
    sec.appendChild(wrap)
  }

  // examples (canonical + antipattern)
  if ((pat.canonical_examples?.length) || (pat.antipattern_examples?.length)) {
    const ex = el('div', { className: 'examples' })
    if (pat.canonical_examples?.length) {
      ex.appendChild(el('h4', {}, 'Canonical examples'))
      const ul = el('ul')
      for (const e of pat.canonical_examples) {
        const li = el('li')
        li.innerHTML = e.url
          ? `<a href="${e.url}" target="_blank" rel="noopener">${e.title}</a> <span style="color:#525252;">· ${e.key}</span>`
          : `${e.title} · ${e.key}`
        ul.appendChild(li)
      }
      ex.appendChild(ul)
    }
    if (pat.antipattern_examples?.length) {
      const anti = el('div', { className: 'anti' })
      anti.appendChild(el('h4', {}, 'Antipattern examples (what went wrong)'))
      const ul = el('ul')
      for (const e of pat.antipattern_examples) {
        const li = el('li')
        li.innerHTML = e.url
          ? `<a href="${e.url}" target="_blank" rel="noopener">${e.title}</a> <span style="color:#525252;">· ${e.key}</span>`
          : `${e.title} · ${e.key}`
        ul.appendChild(li)
      }
      anti.appendChild(ul)
      ex.appendChild(anti)
    }
    sec.appendChild(ex)
  }

  // related_projects — deeper-dive sibling projects on this exact form
  if (pat.related_projects?.length) {
    const rp = el('div', { className: 'related-projects' })
    rp.appendChild(el('h4', {}, 'Go deeper'))
    for (const p of pat.related_projects) {
      const row = el('div', { className: 'rel-proj' })
      const link = el('a', {
        href: p.href,
        target: '_blank',
        rel: 'noopener',
      }, p.title)
      row.appendChild(link)
      if (p.blurb) {
        row.appendChild(el('div', { className: 'rel-proj-blurb' }, (p.blurb || '').trim()))
      }
      rp.appendChild(row)
    }
    sec.appendChild(rp)
  }

  // "Also appears in" if the pattern is cross-family
  const fams = pat.purpose_families || []
  if (fams.length > 1) {
    const others = fams.slice(1)
    const line = el('div', { className: 'other-families' })
    line.appendChild(document.createTextNode('Also relevant for: '))
    others.forEach((f, i) => {
      if (i) line.appendChild(document.createTextNode(', '))
      line.appendChild(el('a', { href: familyHref(f) }, f))
    })
    sec.appendChild(line)
  }

  sec.appendChild(el('a', { className: 'back-to-top', href: '#/' }, '↑ back to TOC'))

  // Auto-link cross-cutting glossary terms (first occurrence per section).
  // Scoped to body + checklist + mistakes so it never touches demo labels
  // or "Instead, reach for" cross-links.
  for (const sel of ['.body', '.checklist', '.mistakes']) {
    const target = sec.querySelector(sel)
    if (target) linkifyGlossary(target)
  }

  return sec
}

function renderFamily(familyName, patIdToScroll) {
  setBreadcrumb([
    { label: 'Chart forms', href: '#/' },
    { label: familyName },
  ])
  page.innerHTML = ''

  // Patterns in this family, primary-first then alphabetical
  const patterns = Object.values(data.patterns)
    .filter(p => (p.purpose_families || []).includes(familyName))
    .sort((a, b) => {
      const ap = primaryFamily(a) === familyName ? 0 : 1
      const bp = primaryFamily(b) === familyName ? 0 : 1
      if (ap !== bp) return ap - bp
      return a.title.localeCompare(b.title)
    })

  page.appendChild(el('div', { className: 'family-header' }, [
    el('div', { className: 'tag' }, 'Family'),
    el('h2', {}, familyName),
    el('p', { className: 'q' }, FAMILY_QUESTIONS[familyName] || ''),
  ]))

  if (!patterns.length) {
    page.appendChild(el('p', {}, 'No patterns tagged for this family yet.'))
    return
  }

  for (const pat of patterns) {
    page.appendChild(renderPatternSection(pat))
  }

  // Scroll to specific pattern if requested (after paint)
  if (patIdToScroll) {
    requestAnimationFrame(() => {
      const target = document.getElementById(`pat-${patIdToScroll}`)
      if (target) target.scrollIntoView({ behavior: 'instant', block: 'start' })
    })
  } else {
    window.scrollTo({ top: 0 })
  }
}

function renderCompare() {
  setBreadcrumb([
    { label: 'Chart forms', href: '#/' },
    { label: 'Same data, different forms' },
  ])
  page.innerHTML = ''

  page.appendChild(el('div', { className: 'family-header' }, [
    el('div', { className: 'tag' }, 'Comparisons'),
    el('h2', {}, 'Same data, different forms'),
    el('p', { className: 'q' }, 'Each card shows the same dataset rendered in two or three forms, with a note on what each form claims. The forms that disagree are teaching the most.'),
  ]))

  // Distribution triad
  const distSec = el('section', { className: 'pattern', id: 'cmp-distribution' }, [
    el('div', { className: 'pattern-header' }, [
      el('div', { className: 'pattern-eyebrow' }, 'DISTRIBUTION COMPARISON'),
      el('h2', {}, 'Histogram vs boxplot vs violin'),
    ]),
    el('div', { className: 'capsule' }, 'A deliberately-bimodal sample, n=400. The boxplot collapses the two peaks into a single box; histogram and violin reveal the structure. Form choice is the story.'),
  ])
  const triad1 = el('div', { className: 'triad' })
  const hH = el('div'), bB = el('div'), vV = el('div')
  triad1.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Histogram'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, hH),
  ]))
  triad1.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Boxplot'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, bB),
  ]))
  triad1.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Violin'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, vV),
  ]))
  distSec.appendChild(triad1)
  distSec.appendChild(el('p', { className: 'body', html: `
    <p><strong>The boxplot is wrong here</strong> — not decoratively wrong, structurally wrong. Its five-number summary (min, Q1, median, Q3, max) is unchanged by bimodality; two samples with the same quartiles can have completely different shapes. When the shape is the story (drug-response patterns, multi-cohort survey data, anomaly detection), reach for histogram or violin.</p>
    <p><strong>The histogram</strong> shows raw counts, which is usually the most honest form. <strong>The violin</strong> shows density, which normalizes across sample sizes and is more compact when comparing many groups.</p>
  ` }))
  page.appendChild(distSec)

  // Spatial triad
  const spaSec = el('section', { className: 'pattern', id: 'cmp-spatial' }, [
    el('div', { className: 'pattern-header' }, [
      el('div', { className: 'pattern-eyebrow' }, 'SPATIAL COMPARISON'),
      el('h2', {}, 'Choropleth vs cartogram vs proportional-symbol'),
    ]),
    el('div', { className: 'capsule' }, 'US state population (2024, in millions). Three spatial forms, three different claims about the same numbers.'),
  ])
  const triad2 = el('div', { className: 'triad' })
  const c1 = el('div'), c2 = el('div'), c3 = el('div')
  triad2.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Choropleth (hex)'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, c1),
  ]))
  triad2.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Cartogram (Dorling)'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, c2),
  ]))
  triad2.appendChild(el('div', {}, [
    el('div', { className: 'label', style: 'font-size:0.72rem;color:#8a8a8a;margin-bottom:0.35rem;letter-spacing:0.08em;text-transform:uppercase;' }, 'Proportional symbol'),
    el('div', { className: 'viz-block', style: 'padding:0.5rem;' }, c3),
  ]))
  spaSec.appendChild(triad2)
  spaSec.appendChild(el('p', { className: 'body', html: `
    <p><strong>The hex choropleth</strong> treats every state equal-weight; area carries no meaning, color carries population. Easy to read but loses geographic intuition.</p>
    <p><strong>The Dorling cartogram</strong> uses area to encode population while keeping approximate geographic layout. Deformation is the form's message — small rural states shrink, coastal states dominate.</p>
    <p><strong>The proportional-symbol map</strong> keeps real geography and uses circle area for population. Best when readers need to anchor to real places AND see magnitude; worst when symbols collide.</p>
    <p>All three are "right" for the same data. Each answers a slightly different question: which has most? (choropleth), which dominates visually? (cartogram), where does population pool? (prop-symbol).</p>
  ` }))
  page.appendChild(spaSec)

  page.appendChild(el('a', { className: 'back-to-top', href: '#/' }, '↑ back to TOC'))

  requestAnimationFrame(() => {
    try { renderDistributionTriad(hH, bB, vV) } catch (e) { console.error(e) }
    try { renderSpatialTriad(c1, c2, c3) } catch (e) { console.error(e) }
  })
}

function renderInteractivityDoc() {
  setBreadcrumb([
    { label: 'Chart forms', href: '#/' },
    { label: 'Interactivity principles' },
  ])
  page.innerHTML = ''
  page.appendChild(el('div', { className: 'family-header' }, [
    el('div', { className: 'tag' }, 'Reference'),
    el('h2', {}, 'Interactivity principles'),
    el('p', { className: 'q' }, 'How we decide when a chart earns an interactive affordance, and what touch and mobile do to the design. A working doc — the evolution log captures what each implementation taught us.'),
  ]))
  page.appendChild(el('div', {
    className: 'prose-doc',
    html: mdDocToHtml(interactivityMdRaw),
  }))
  page.appendChild(el('a', { className: 'back-to-top', href: '#/' }, '↑ back to TOC'))
}

function renderGlossary(scrollToSlug) {
  setBreadcrumb([
    { label: 'Chart forms', href: '#/' },
    { label: 'Glossary' },
  ])
  page.innerHTML = ''
  page.appendChild(el('div', { className: 'family-header' }, [
    el('div', { className: 'tag' }, 'Reference'),
    el('h2', {}, 'Glossary'),
    el('p', { className: 'q' }, 'Cross-cutting terms that show up on multiple pattern pages. Term names link back from inline occurrences on the first mention in each pattern.'),
  ]))
  const list = el('div', { className: 'glossary' })
  // Sort entries alphabetically by term name for lookup reliability.
  const entries = Object.entries(GLOSSARY).sort((a, b) =>
    a[1].term.localeCompare(b[1].term)
  )
  for (const [slug, entry] of entries) {
    const item = el('div', { className: 'g-entry', id: `g-${slug}` })
    item.appendChild(el('h3', {}, entry.term))
    item.appendChild(el('p', { className: 'g-short' }, entry.short))
    if (entry.long) {
      item.appendChild(el('p', { className: 'g-long' }, entry.long))
    }
    list.appendChild(item)
  }
  page.appendChild(list)
  page.appendChild(el('a', { className: 'back-to-top', href: '#/' }, '↑ back to TOC'))
  if (scrollToSlug) {
    const t = document.getElementById(`g-${scrollToSlug}`)
    if (t) {
      requestAnimationFrame(() => {
        t.scrollIntoView({ block: 'start' })
        t.classList.add('flash')
        setTimeout(() => t.classList.remove('flash'), 1600)
      })
    }
  }
}

function renderReview() {
  setBreadcrumb([
    { label: 'Chart forms', href: '#/' },
    { label: 'Review harness' },
  ])
  page.innerHTML = ''
  page.appendChild(el('div', { className: 'family-header' }, [
    el('div', { className: 'tag' }, 'Internal'),
    el('h2', {}, 'Demo review harness'),
    el('p', { className: 'q' }, 'Every pattern\'s live demo rendered in sequence. The automated check flags SVG text that extends past the viewBox; visual issues (overlap, contrast, misplaced decoders) require eyeballing. Issues caught during review are listed per demo.'),
  ]))

  const patternIds = Object.keys(DEMO_BY_ID).sort()
  const issueCount = { total: 0 }

  for (const pid of patternIds) {
    const pat = data.patterns[pid]
    if (!pat) continue
    const sec = el('section', { className: 'pattern', id: `review-${pid}` })
    sec.appendChild(el('div', { className: 'pattern-header' }, [
      el('div', { className: 'pattern-eyebrow' }, pid.toUpperCase().replace(/-/g, ' ')),
      el('h2', {}, pat.title),
    ]))
    // Demo host
    const host = el('div')
    const issueList = el('ul', {
      style: 'list-style:none;padding:0;margin:0.6rem 0 0;font-size:0.8rem;',
    })
    sec.appendChild(el('div', { className: 'viz-block' }, host))
    sec.appendChild(issueList)
    page.appendChild(sec)

    // Render demo + check
    requestAnimationFrame(() => {
      try {
        DEMO_BY_ID[pid](host)
        // Defer the check so d3 force sims etc. settle
        setTimeout(() => {
          const issues = checkDemoIssues(host)
          issueCount.total += issues.length
          const statusEl = el('li', {
            style: issues.length
              ? 'color:#fca5a5;padding:0.35rem 0;'
              : 'color:#86efac;padding:0.35rem 0;',
          }, issues.length ? `${issues.length} issues flagged:` : '✓ automated checks clean (visual review still needed)')
          issueList.appendChild(statusEl)
          for (const issue of issues) {
            issueList.appendChild(el('li', {
              style: 'color:#d4d4d4;font-size:0.78rem;padding:0.15rem 0 0.15rem 1.4rem;position:relative;',
              html: `<span style="position:absolute;left:0;color:#fca5a5;">⚠</span>${issue}`,
            }))
          }
        }, 300)
      } catch (e) {
        issueList.appendChild(el('li', {
          style: 'color:#f87171;font-size:0.8rem;padding:0.35rem 0;',
        }, `render error: ${e.message}`))
      }
    })
  }
}

// Automated checks for rendering issues in a demo's viz-block.
// Uses viewport-relative bounding rects (which account for all
// ancestor transforms) and compares against the SVG element's own
// bounding rect. Structural issues (text past SVG edge, label-label
// overlap) only; contrast and decoder placement still need eyeballing.
function checkDemoIssues(container) {
  const issues = []
  const svgs = container.querySelectorAll('svg')
  for (const svg of svgs) {
    const svgRect = svg.getBoundingClientRect()
    // A small tolerance to avoid noise from antialiasing + 1-px edges.
    const tol = 3
    const textEls = svg.querySelectorAll('text')
    const boxes = []
    for (const t of textEls) {
      const r = t.getBoundingClientRect()
      if (r.width === 0 && r.height === 0) continue
      const content = (t.textContent || '').trim().slice(0, 30)
      if (r.right < svgRect.left - tol || r.left > svgRect.right + tol ||
          r.bottom < svgRect.top - tol || r.top > svgRect.bottom + tol ||
          r.left < svgRect.left - tol || r.right > svgRect.right + tol ||
          r.top < svgRect.top - tol || r.bottom > svgRect.bottom + tol) {
        const dLeft = Math.round(svgRect.left - r.left)
        const dRight = Math.round(r.right - svgRect.right)
        const dTop = Math.round(svgRect.top - r.top)
        const dBottom = Math.round(r.bottom - svgRect.bottom)
        const edges = []
        if (dLeft > tol) edges.push(`left -${dLeft}`)
        if (dRight > tol) edges.push(`right +${dRight}`)
        if (dTop > tol) edges.push(`top -${dTop}`)
        if (dBottom > tol) edges.push(`bottom +${dBottom}`)
        if (edges.length) {
          issues.push(`text "${content}" clips edge (${edges.join(', ')})`)
        }
      }
      boxes.push({ r, content, el: t })
    }
    // Text-text overlap via viewport rects (picks up real visual overlaps
    // regardless of parent transforms).
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i].r, b = boxes[j].r
        const overlapX = Math.min(a.right, b.right) - Math.max(a.left, b.left)
        const overlapY = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top)
        if (overlapX > tol && overlapY > tol) {
          issues.push(`text overlap: "${boxes[i].content}" ↔ "${boxes[j].content}"`)
        }
      }
    }
  }
  return issues
}

// ------------------------------ router
function route() {
  const hash = location.hash || '#/'
  // strip leading '#'
  const parts = hash.replace(/^#\/?/, '').split('/').filter(Boolean)
  if (parts.length === 0) return renderRoot()
  if (parts[0] === 'compare') return renderCompare()
  if (parts[0] === 'review') return renderReview()
  if (parts[0] === 'glossary') return renderGlossary(parts[1] || null)
  if (parts[0] === 'interactivity') return renderInteractivityDoc()
  if (parts[0] === 'family' && parts[1]) {
    const family = FAMILY_BY_SLUG[parts[1]]
    if (!family) return renderRoot()
    const patId = parts[2] || null
    return renderFamily(family, patId)
  }
  // unknown route → root
  renderRoot()
}

window.addEventListener('hashchange', route)
route()
