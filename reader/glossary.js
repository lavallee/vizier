// Cross-cutting terms that appear across chart-pattern pages. Each entry:
//   { term: canonical spelling, aliases: alt spellings matched in text,
//     short: one-sentence definition, long?: optional fuller note }
// Linkify behaviour in main.js wraps the first occurrence of any term/alias
// in each pattern body with a link to #/glossary/<slug>.

export const GLOSSARY = {
  iqr: {
    term: 'IQR',
    aliases: ['IQR', 'interquartile range'],
    short: 'Interquartile range — the distance from the 25th to the 75th percentile (Q1 to Q3). The width of the "middle half" of the data.',
    long: 'The IQR is the width of the box in a boxplot. It\'s a robust measure of spread: unlike standard deviation, it isn\'t pulled around by a handful of outliers. Boxplot whiskers conventionally extend to 1.5×IQR past each quartile; anything past that gets drawn as an outlier dot.',
  },
  'kernel-density': {
    term: 'Kernel density (KDE)',
    aliases: ['KDE', 'kernel density', 'kernel density estimate'],
    short: 'A smoothed estimate of a distribution\'s shape — the continuous curve that replaces a histogram\'s bars.',
    long: 'KDE draws a small "kernel" (typically a Gaussian) over every data point and sums them, producing a smooth curve that estimates the underlying density. It\'s the shape you see in a violin chart. Sensitive to the bandwidth parameter: too narrow and you see every bump; too wide and you flatten real peaks.',
  },
  bandwidth: {
    term: 'Bandwidth',
    aliases: ['bandwidth'],
    short: 'In a KDE, the width of the smoothing kernel. Too small = spiky noise; too large = real peaks disappear.',
    long: 'Bandwidth is the single knob that determines how much a KDE smooths. Small-bandwidth KDEs hug every data point (every wobble survives). Large-bandwidth KDEs blur over real structure (bimodal distributions look unimodal). Rules of thumb like Silverman\'s exist but the best bandwidth depends on what the chart needs to show.',
  },
  dorling: {
    term: 'Dorling cartogram',
    aliases: ['Dorling'],
    short: 'A cartogram variant that replaces each region with a circle whose area encodes the quantity; positions are nudged to preserve rough geography.',
    long: 'Named after Danny Dorling. The alternative is a "contiguous" cartogram which distorts region shapes to make area proportional to the data; Dorling trades adjacency for clarity. Small regions vanish less than in a choropleth; large but sparsely-populated regions shrink. Use when the metric is per-region and land area would mislead.',
  },
  'force-directed': {
    term: 'Force-directed layout',
    aliases: ['force-directed', 'force simulation'],
    short: 'A physics-style simulation: nodes repel each other, some forces attract them, the layout settles into an equilibrium.',
    long: 'd3-force is the standard implementation. Common forces include `forceX`/`forceY` (pull toward a target coordinate), `forceLink` (springs between connected nodes), `forceCollide` (prevent overlap), and `forceManyBody` (general repulsion). Great for organic network layouts; be careful — identical data can produce different layouts across runs unless you seed the simulation.',
  },
  nodesort: {
    term: 'nodeSort',
    aliases: ['nodeSort'],
    short: 'A d3-sankey option controlling how nodes are ordered within each stage. Defaulting to its automatic sort usually tangles ribbons; pass `null` and supply your own order.',
    long: 'd3-sankey\'s default nodeSort reshuffles nodes by inferred importance, which usually tangles ribbons into a birds-nest. The fix is almost always to call `nodeSort(null)` and provide an explicit order per column (semantic, not alphabetical) — so the dominant pairing reads as a clean diagonal.',
  },
  stageorder: {
    term: 'stageOrder',
    aliases: ['stageOrder', 'stage order'],
    short: 'The within-column ordering of categorical values in a sankey — always an editorial choice.',
    long: 'Alphabetical stageOrder is almost never right. Order the categories within each stage so the dominant ribbon reads as a straight diagonal rather than tangling. For a political-lean diagram that means Left → Center → Right on every axis; for an income bucket, low → high. The order is part of the chart\'s argument.',
  },
  conservation: {
    term: 'Conservation',
    aliases: ['conservation', 'conserved'],
    short: 'The axiom a sankey enforces visually: the left-total equals the right-total. If the underlying quantity isn\'t actually conserved, the chart lies by construction.',
    long: 'A sankey draws ribbons from left-total to right-total and insists they balance. For a user funnel where the missing cohort just "stopped being counted", a sankey fabricates a "Dropped off" bucket to satisfy the constraint — and readers read that bucket as a destination. Only reach for a sankey when the quantity really is conserved (energy, dollars, votes, carbon).',
  },
  'small-multiples': {
    term: 'Small multiples',
    aliases: ['small multiples', 'trellis'],
    short: 'The same encoding repeated across facets, with only the data changing. Lets readers compare shapes at a glance instead of colors.',
    long: 'Coined by Tufte. Instead of overplotting 10 lines on one axis with a 10-color legend, draw 10 small panels — all with the same x/y scales. Readers\' eyes can pick out deviations instantly. Works best when the panels share scales (so sizes are comparable) and when you need to compare shape across groups rather than reading exact values.',
  },
  'log-scale': {
    term: 'Log scale',
    aliases: ['log scale', 'logarithmic'],
    short: 'An axis where equal distances represent equal ratios, not equal differences. Use when the data spans orders of magnitude.',
    long: 'On a log axis, 1 → 10 covers the same distance as 10 → 100. Natural for quantities that grow multiplicatively (populations, prices, viral counts). Zero can\'t be plotted. Readers must be told the axis is log — the distortion is invisible otherwise, and a linear-reading audience will mis-estimate by orders of magnitude.',
  },
  quantile: {
    term: 'Quantile',
    aliases: ['quantile', 'percentile'],
    short: 'A cut point that divides sorted data into groups of equal size. Q1 = 25th percentile; median = 50th; Q3 = 75th.',
  },
  whisker: {
    term: 'Whisker',
    aliases: ['whisker'],
    short: 'In a boxplot, the lines extending past the Q1/Q3 box. Convention is 1.5×IQR past each quartile, clipped to the nearest actual data point.',
  },
  outlier: {
    term: 'Outlier',
    aliases: ['outlier'],
    short: 'A point drawn separately because it sits beyond the whisker (past 1.5×IQR from Q1/Q3). Not a judgment — it\'s a placement rule.',
  },
  'bin-width': {
    term: 'Bin width',
    aliases: ['bin width', 'bin-width'],
    short: 'How wide each bucket is in a histogram. The single most important histogram parameter — change it and the story can change.',
    long: 'Too-narrow bins show noise as structure. Too-wide bins smooth real multimodality into one blob. Rules like Freedman-Diaconis and Scott\'s give defaults based on the data; in practice, try a few widths and pick the one that tells the truth without inventing it.',
  },
  binning: {
    term: 'Binning',
    aliases: ['binning'],
    short: 'Grouping continuous values into discrete buckets. Histograms, heatmaps, and hexbins all bin.',
  },
  jitter: {
    term: 'Jitter',
    aliases: ['jitter'],
    short: 'Random offset added to points along one axis so overlapping marks become visible. Typical in strip plots and dot-plot-over-category charts.',
    long: 'Without jitter, 50 people all rating "7/10" would render as a single overprinted dot. Jitter spreads them out so density becomes legible. Always add enough to break ties; never so much that jitter distance looks like a meaningful difference.',
  },
  collide: {
    term: 'Collision force',
    aliases: ['collide', 'forceCollide'],
    short: 'The d3-force force that prevents marks from overlapping. Each node is given a radius; the simulation pushes overlapping nodes apart.',
  },
}

// For linkify: build a regex that matches any alias, preferring longer
// matches first so "kernel density estimate" wins over "kernel density".
const _aliasToSlug = []
for (const [slug, entry] of Object.entries(GLOSSARY)) {
  for (const a of entry.aliases) _aliasToSlug.push({ alias: a, slug })
}
_aliasToSlug.sort((a, b) => b.alias.length - a.alias.length)

function _escape(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') }

const ALIAS_RE = new RegExp(
  '\\b(' + _aliasToSlug.map(x => _escape(x.alias)).join('|') + ')\\b',
  'gi',
)
const ALIAS_MAP = Object.fromEntries(
  _aliasToSlug.map(x => [x.alias.toLowerCase(), x.slug]),
)

// Walk an element, replacing the first occurrence of each glossary alias
// in text nodes with a link. Subsequent occurrences of the same slug are
// left alone (prevents visual noise).
export function linkifyGlossary(root) {
  const seen = new Set()
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      // Skip text that's already inside a link or the glossary itself.
      let p = node.parentElement
      while (p) {
        if (p.tagName === 'A') return NodeFilter.FILTER_REJECT
        if (p.classList?.contains('glossary')) return NodeFilter.FILTER_REJECT
        p = p.parentElement
      }
      return NodeFilter.FILTER_ACCEPT
    },
  })
  const edits = []
  let n
  while ((n = walker.nextNode())) {
    const t = n.textContent
    if (!t || !ALIAS_RE.test(t)) continue
    ALIAS_RE.lastIndex = 0
    let m
    const ranges = []
    while ((m = ALIAS_RE.exec(t))) {
      const slug = ALIAS_MAP[m[0].toLowerCase()]
      if (seen.has(slug)) continue
      seen.add(slug)
      ranges.push({ start: m.index, end: m.index + m[0].length, slug, text: m[0] })
    }
    if (ranges.length) edits.push({ node: n, ranges })
  }
  for (const { node, ranges } of edits) {
    const t = node.textContent
    const frag = document.createDocumentFragment()
    let cursor = 0
    for (const r of ranges) {
      if (r.start > cursor) frag.appendChild(document.createTextNode(t.slice(cursor, r.start)))
      const a = document.createElement('a')
      a.className = 'g-term'
      a.href = `#/glossary/${r.slug}`
      a.title = GLOSSARY[r.slug].short
      a.textContent = r.text
      frag.appendChild(a)
      cursor = r.end
    }
    if (cursor < t.length) frag.appendChild(document.createTextNode(t.slice(cursor)))
    node.parentNode.replaceChild(frag, node)
  }
}
