// Exercises interactive patterns against the principles in INTERACTIVITY.md.
// Each pattern section verifies the primary affordance (P10), the
// "details on demand" resting state (P2), and the static-mode contract (P4).
// Exit non-zero if any assertion fails.

import { chromium } from 'playwright'
const BASE = process.env.BASE || 'http://localhost:5173'
const browser = await chromium.launch()
const page = await (await browser.newContext({ viewport: { width: 1200, height: 900 } })).newPage()

const errors = []
page.on('pageerror', e => errors.push(`pageerror: ${e.message}`))
page.on('console', m => { if (m.type() === 'error') errors.push(`console: ${m.text()}`) })

const failures = []
function ok(cond, label) {
  const mark = cond ? 'PASS' : 'FAIL'
  if (!cond) failures.push(label)
  console.log(`  ${mark}  ${label}`)
}
async function hoverCenter(selector) {
  const b = await page.$eval(selector, el => {
    const r = el.getBoundingClientRect()
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 }
  })
  await page.mouse.move(b.x, b.y)
  await page.waitForTimeout(200)
  return b
}

async function gotoPattern(family, pattern) {
  await page.goto(`${BASE}/projects/chart-forms-guide/#/family/${family}/${pattern}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(600)
}
async function toggleMode(pattern, label) {
  await page.click(`#pat-${pattern} .mode-btn:not(.is-on)`)
  await page.waitForTimeout(250)
}

// ---------------- scatterplot ----------------
console.log('\nscatterplot · hover-tooltip + click-pin')
await gotoPattern('correlation', 'scatterplot')
let tipOp = await page.$eval('#pat-scatterplot .scatter-tip', el => +getComputedStyle(el).opacity)
ok(tipOp === 0, 'initial: tooltip hidden (P2)')
const sp = await hoverCenter('#pat-scatterplot svg')
tipOp = await page.$eval('#pat-scatterplot .scatter-tip', el => +getComputedStyle(el).opacity)
ok(tipOp === 1, 'hover: tooltip visible (P3)')
const faded = await page.$$eval('#pat-scatterplot .dots circle', ds =>
  ds.filter(d => +d.getAttribute('fill-opacity') < 0.5).length)
ok(faded >= 70, `hover: ${faded}/80 points faded (P7: fade others)`)
await page.mouse.click(sp.x, sp.y); await page.waitForTimeout(150)
await page.mouse.move(sp.x - 300, sp.y + 200); await page.waitForTimeout(150)
tipOp = await page.$eval('#pat-scatterplot .scatter-tip', el => +getComputedStyle(el).opacity)
ok(tipOp === 1, 'pin survives mouse-away (P5: touch via click)')
await page.mouse.click(sp.x, sp.y); await page.waitForTimeout(150)
tipOp = await page.$eval('#pat-scatterplot .scatter-tip', el => +getComputedStyle(el).opacity)
ok(tipOp === 0, 'click again unpins')
await toggleMode('scatterplot')
const hasStaticTip = await page.$('#pat-scatterplot .scatter-tip')
ok(!hasStaticTip, 'static mode: no tooltip element (P4)')

// ---------------- bump-chart ----------------
console.log('\nbump-chart · hover-label-isolate')
await gotoPattern('ranking', 'bump-chart')
const bumpBefore = await page.$$eval('#pat-bump-chart .bump-series path', ps =>
  ps.every(p => +p.getAttribute('stroke-opacity') === 1 || p.getAttribute('stroke-opacity') === null))
ok(bumpBefore, 'initial: all lines full opacity (P2)')
const apple = await page.$('#pat-bump-chart text:has-text("Apple")')
if (apple) {
  const b = await apple.boundingBox()
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(200)
}
const bumpFaded = await page.$$eval('#pat-bump-chart .bump-series path', ps =>
  ps.filter(p => +p.getAttribute('stroke-opacity') < 0.5).length)
ok(bumpFaded === 6, `hover Apple: ${bumpFaded}/7 others faded (P7)`)
await page.mouse.move(10, 10)
await page.waitForTimeout(150)

// ---------------- line-chart ----------------
console.log('\nline-chart · time-cursor + multi-series readout')
await gotoPattern('change-over-time', 'line-chart')
await hoverCenter('#pat-line-chart svg')
const lineState = await page.evaluate(() => {
  const tip = document.querySelector('#pat-line-chart .line-tip')
  const cur = document.querySelector('#pat-line-chart .time-cursor')
  return {
    tipVisible: tip ? +getComputedStyle(tip).opacity === 1 : false,
    cursorVisible: cur ? +getComputedStyle(cur).opacity === 1 : false,
    text: tip?.innerText || '',
  }
})
ok(lineState.tipVisible, 'hover: tooltip visible')
ok(lineState.cursorVisible, 'hover: time cursor visible')
ok(/\d{4}/.test(lineState.text), `tooltip has year: ${lineState.text.slice(0, 40).replace(/\n/g, ' | ')}`)

// ---------------- sankey ----------------
console.log('\nsankey · click-to-isolate')
await gotoPattern('flow', 'sankey')
const sankeyBefore = await page.$$eval('#pat-sankey svg > path', ps =>
  [...new Set(ps.map(p => +p.getAttribute('fill-opacity')))])
ok(sankeyBefore.length === 1 && sankeyBefore[0] === 0.55, `initial: all ribbons at 0.55 (got ${sankeyBefore})`)
const solar = await page.$('#pat-sankey text:has-text("Solar")')
if (solar) {
  const b = await solar.boundingBox()
  await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(200)
}
const sankeyAfter = await page.$$eval('#pat-sankey svg > path', ps => ({
  connected: ps.filter(p => +p.getAttribute('fill-opacity') > 0.5).length,
  dimmed: ps.filter(p => +p.getAttribute('fill-opacity') < 0.2).length,
}))
ok(sankeyAfter.connected === 4 && sankeyAfter.dimmed === 16,
   `pin Solar: ${sankeyAfter.connected} connected + ${sankeyAfter.dimmed} dimmed (dim-don't-hide)`)
if (solar) {
  const b = await solar.boundingBox()
  await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(150)
}
const sankeyRestored = await page.$$eval('#pat-sankey svg > path', ps =>
  [...new Set(ps.map(p => +p.getAttribute('fill-opacity')))])
ok(sankeyRestored.length === 1 && sankeyRestored[0] === 0.55, 'unpin: restored to initial uniform opacity')

// ---------------- heatmap ----------------
console.log('\nheatmap · cross-hair + cell readout')
await gotoPattern('correlation', 'heatmap')
const heatBefore = await page.evaluate(() => {
  const tip = document.querySelector('#pat-heatmap .heatmap-tip')
  const row = document.querySelector('#pat-heatmap .cross-row')
  return {
    tipOp: tip ? +getComputedStyle(tip).opacity : null,
    rowOp: row ? +row.getAttribute('stroke-opacity') : null,
  }
})
ok(heatBefore.tipOp === 0, 'initial: tooltip hidden (P2)')
ok(heatBefore.rowOp === 0, 'initial: cross-hair hidden (P2)')
// Hover a cell in the middle of the grid
const cell = await page.$('#pat-heatmap .cells rect:nth-child(100)')
if (cell) {
  const b = await cell.boundingBox()
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(200)
}
const heatAfter = await page.evaluate(() => {
  const tip = document.querySelector('#pat-heatmap .heatmap-tip')
  const row = document.querySelector('#pat-heatmap .cross-row')
  const col = document.querySelector('#pat-heatmap .cross-col')
  return {
    tipOp: tip ? +getComputedStyle(tip).opacity : null,
    rowOp: row ? +row.getAttribute('stroke-opacity') : null,
    colOp: col ? +col.getAttribute('stroke-opacity') : null,
    tipText: tip?.innerText || '',
  }
})
ok(heatAfter.tipOp === 1, 'hover: tooltip visible')
ok(heatAfter.rowOp > 0 && heatAfter.colOp > 0, 'hover: cross-hair (row + col) visible')
ok(/traffic:/.test(heatAfter.tipText), `tooltip text has value: ${heatAfter.tipText.slice(0, 60).replace(/\n/g, ' | ')}`)

// ---------------- maps pack (hover-for-region-info) ----------------
console.log('\nmaps · hover-for-region-info')
const mapCases = [
  { family: 'spatial', pattern: 'choropleth', hoverSel: '#pat-choropleth .hex-cell[data-state="CA"]', tipSel: '#pat-choropleth .choropleth-tip', expectPart: 'CA' },
  { family: 'spatial', pattern: 'hex-bin-map', hoverSel: '#pat-hex-bin-map .hex-cell[data-state="CA"]', tipSel: '#pat-hex-bin-map .hexbin-tip', expectPart: 'CA' },
  { family: 'spatial', pattern: 'cartogram', hoverSel: '#pat-cartogram .cartogram-node[data-state="CA"]', tipSel: '#pat-cartogram .cartogram-tip', expectPart: 'CA' },
  { family: 'spatial', pattern: 'proportional-symbol-map', hoverSel: '#pat-proportional-symbol-map .prop-symbol[data-id="NYC"]', tipSel: '#pat-proportional-symbol-map .prop-symbol-tip', expectPart: 'NYC' },
]
for (const c of mapCases) {
  await gotoPattern(c.family, c.pattern)
  // Park the cursor off-chart between cases — all spatial patterns live on
  // one family page, so the cursor's last position can trigger the next
  // pattern's hover before we ever check "initial".
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverSel)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverSel} not found`); continue }
  const b = await el.boundingBox()
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(180)
  const state = await page.evaluate(([tipSel, expect]) => {
    const t = document.querySelector(tipSel)
    return {
      op: t ? +getComputedStyle(t).opacity : null,
      text: (t?.innerText || ''),
      matches: (t?.innerText || '').includes(expect),
    }
  }, [c.tipSel, c.expectPart])
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(state.matches, `${c.pattern}: tooltip contains ${c.expectPart} (${state.text.replace(/\n/g, ' | ').slice(0, 50)})`)
}

// ---------------- hover pack: dot-map, flow-map, matrix-plot, calendar-heatmap ----------------
console.log('\nhover pack · dot-map / flow-map / matrix-plot / calendar-heatmap')
const hoverCases = [
  // dot-map uses an SVG-level overlay, not per-mark selectors; hover the center of the SVG
  { family: 'spatial', pattern: 'dot-map', hoverTarget: '#pat-dot-map svg', tipSel: '#pat-dot-map .dot-map-tip', expectMatch: /area/i },
  // flow-map: hover a curved flow path (e.g. LA→AUS)
  { family: 'flow', pattern: 'flow-map', hoverTarget: '#pat-flow-map .flow-path[data-from="LA"][data-to="AUS"]', tipSel: '#pat-flow-map .flow-map-tip', expectMatch: /LA → AUS/ },
  // matrix-plot: hover a specific cell (row 0 col 1)
  { family: 'correlation', pattern: 'matrix-plot', hoverTarget: '#pat-matrix-plot .mp-cell[data-rc="0-1"]', tipSel: '#pat-matrix-plot .matrix-plot-tip', expectMatch: /N\. America/ },
  // calendar-heatmap: hover any cell
  { family: 'change-over-time', pattern: 'calendar-heatmap', hoverTarget: '#pat-calendar-heatmap .ch-cell:nth-of-type(200)', tipSel: '#pat-calendar-heatmap .cal-heat-tip', expectMatch: /commits:/ },
]
for (const c of hoverCases) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  // For SVG <path> elements, bbox center may not intersect the curve.
  // Use getPointAtLength(total/2) in client-rect space for paths.
  const hoverPoint = await el.evaluate(node => {
    if (node.tagName.toLowerCase() === 'path' && typeof node.getTotalLength === 'function') {
      const len = node.getTotalLength()
      const p = node.getPointAtLength(len / 2)
      const svg = node.ownerSVGElement
      const pt = svg.createSVGPoint(); pt.x = p.x; pt.y = p.y
      const screen = pt.matrixTransform(node.getScreenCTM())
      return { x: screen.x, y: screen.y }
    }
    const r = node.getBoundingClientRect()
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 }
  })
  await page.mouse.move(hoverPoint.x, hoverPoint.y)
  await page.waitForTimeout(200)
  const state = await page.evaluate(([tipSel, pattern]) => {
    const t = document.querySelector(tipSel)
    return {
      op: t ? +getComputedStyle(t).opacity : null,
      text: t?.innerText || '',
    }
  }, [c.tipSel, c.pattern])
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- hover pack 2: chord-diagram, mosaic, marimekko, connected-scatter ----------------
console.log('\nhover pack 2 · chord / mosaic / marimekko / connected-scatter')
const hoverCases2 = [
  { family: 'flow', pattern: 'chord-diagram', hoverTarget: '#pat-chord-diagram .chord-ribbon', tipSel: '#pat-chord-diagram .chord-tip', expectMatch: /flow:/ },
  { family: 'part-to-whole', pattern: 'mosaic', hoverTarget: '#pat-mosaic .mosaic-cell[data-smoking="Never"][data-exercise="Often"]', tipSel: '#pat-mosaic .mosaic-tip', expectMatch: /Never smoker · Often/ },
  { family: 'part-to-whole', pattern: 'marimekko', hoverTarget: '#pat-marimekko .mk-cell[data-market="SE Asia"][data-brand="Brand A"]', tipSel: '#pat-marimekko .mk-tip', expectMatch: /Brand A · SE Asia/ },
  { family: 'correlation', pattern: 'connected-scatter', hoverTarget: '#pat-connected-scatter svg', tipSel: '#pat-connected-scatter .cs-tip', expectMatch: /unemployment:/ },
]
for (const c of hoverCases2) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  const hoverPoint = await el.evaluate(node => {
    if (node.tagName.toLowerCase() === 'path' && typeof node.getTotalLength === 'function') {
      const len = node.getTotalLength()
      const p = node.getPointAtLength(len / 2)
      const svg = node.ownerSVGElement
      const pt = svg.createSVGPoint(); pt.x = p.x; pt.y = p.y
      const screen = pt.matrixTransform(node.getScreenCTM())
      return { x: screen.x, y: screen.y }
    }
    const r = node.getBoundingClientRect()
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 }
  })
  await page.mouse.move(hoverPoint.x, hoverPoint.y)
  await page.waitForTimeout(200)
  const state = await page.evaluate(tipSel => {
    const t = document.querySelector(tipSel)
    return { op: t ? +getComputedStyle(t).opacity : null, text: t?.innerText || '' }
  }, c.tipSel)
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- summary-stats pack: boxplot, violin, box-and-jitter-strip ----------------
console.log('\nsummary-stats pack · boxplot / violin / box-and-jitter-strip')
const summaryCases = [
  { family: 'distribution', pattern: 'boxplot', hoverTarget: '#pat-boxplot .bp-hit[data-name="C"]', tipSel: '#pat-boxplot .bp-tip', expectMatch: /Group C/ },
  { family: 'distribution', pattern: 'violin', hoverTarget: '#pat-violin .violin-hit[data-name="A"]', tipSel: '#pat-violin .violin-tip', expectMatch: /modes: .*2/ },
  { family: 'distribution', pattern: 'box-and-jitter-strip', hoverTarget: '#pat-box-and-jitter-strip .bj-hit[data-name="Sparse"]', tipSel: '#pat-box-and-jitter-strip .bj-tip', expectMatch: /n=8/ },
]
for (const c of summaryCases) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  const b = await el.boundingBox()
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(200)
  const state = await page.evaluate(tipSel => {
    const t = document.querySelector(tipSel)
    return { op: t ? +getComputedStyle(t).opacity : null, text: t?.innerText || '' }
  }, c.tipSel)
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- time-cursor + specialized pack: streamgraph, stacked-area, gantt, dendrogram ----------------
console.log('\ntime-cursor + specialized pack · streamgraph / stacked-area / gantt / dendrogram')
const timeSpecCases = [
  { family: 'change-over-time', pattern: 'streamgraph', hoverTarget: '#pat-streamgraph svg', tipSel: '#pat-streamgraph .sg-tip', expectMatch: /Hip-Hop/ },
  { family: 'change-over-time', pattern: 'stacked-area', hoverTarget: '#pat-stacked-area svg', tipSel: '#pat-stacked-area .sa-tip', expectMatch: /Solar/ },
  { family: 'change-over-time', pattern: 'gantt-chart', hoverTarget: '#pat-gantt-chart .gantt-mark[data-task="First-pass edits"]', tipSel: '#pat-gantt-chart .gantt-tip', expectMatch: /First-pass edits/ },
  { family: 'part-to-whole', pattern: 'dendrogram', hoverTarget: '#pat-dendrogram .dg-hit', tipSel: '#pat-dendrogram .dg-tip', expectMatch: /cities/ },
]
for (const c of timeSpecCases) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  const hoverPoint = await el.evaluate(node => {
    if (node.tagName.toLowerCase() === 'path' && typeof node.getTotalLength === 'function') {
      const len = node.getTotalLength()
      const p = node.getPointAtLength(len / 2)
      const svg = node.ownerSVGElement
      const pt = svg.createSVGPoint(); pt.x = p.x; pt.y = p.y
      const screen = pt.matrixTransform(node.getScreenCTM())
      return { x: screen.x, y: screen.y }
    }
    const r = node.getBoundingClientRect()
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 }
  })
  await page.mouse.move(hoverPoint.x, hoverPoint.y)
  await page.waitForTimeout(200)
  const state = await page.evaluate(tipSel => {
    const t = document.querySelector(tipSel)
    return { op: t ? +getComputedStyle(t).opacity : null, text: t?.innerText || '' }
  }, c.tipSel)
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- graph/slope pack: network-diagram, parallel-sets, arc-diagram, slope-chart ----------------
console.log('\ngraph/slope pack · network / parallel-sets / arc / slope')
const graphSlopeCases = [
  { family: 'correlation', pattern: 'network-diagram', hoverTarget: '#pat-network-diagram .net-node[data-id="0"]', tipSel: '#pat-network-diagram .net-tip', expectMatch: /connections:/ },
  { family: 'distribution', pattern: 'parallel-sets', hoverTarget: '#pat-parallel-sets .ps-segment[data-axis="lean"][data-value="Left"]', tipSel: '#pat-parallel-sets .ps-tip', expectMatch: /Left/, action: 'click' },
  { family: 'correlation', pattern: 'arc-diagram', hoverTarget: '#pat-arc-diagram .arc-edge[data-a="0"][data-b="1"]', tipSel: '#pat-arc-diagram .arc-tip', expectMatch: /Alice ↔ Bob/ },
  { family: 'ranking', pattern: 'slope-chart', hoverTarget: '#pat-slope-chart .slope-hit[data-name="Chen"]', tipSel: '#pat-slope-chart .slope-tip', expectMatch: /Chen/ },
]
for (const c of graphSlopeCases) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  const hoverPoint = await el.evaluate(node => {
    if ((node.tagName.toLowerCase() === 'path' || node.tagName.toLowerCase() === 'line') && typeof node.getTotalLength === 'function') {
      const len = node.getTotalLength()
      const p = node.getPointAtLength(len / 2)
      const svg = node.ownerSVGElement
      const pt = svg.createSVGPoint(); pt.x = p.x; pt.y = p.y
      const screen = pt.matrixTransform(node.getScreenCTM())
      return { x: screen.x, y: screen.y }
    }
    const r = node.getBoundingClientRect()
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 }
  })
  if (c.action === 'click') {
    await page.mouse.click(hoverPoint.x, hoverPoint.y)
  } else {
    await page.mouse.move(hoverPoint.x, hoverPoint.y)
  }
  await page.waitForTimeout(200)
  const state = await page.evaluate(tipSel => {
    const t = document.querySelector(tipSel)
    return { op: t ? +getComputedStyle(t).opacity : null, text: t?.innerText || '' }
  }, c.tipSel)
  ok(state.op === 1, `${c.pattern}: tooltip visible on ${c.action || 'hover'}`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- finale: small-multiples, radar-chart ----------------
console.log('\nfinale · small-multiples / radar-chart')
const finaleCases = [
  { family: 'change-over-time', pattern: 'small-multiples', hoverTarget: '#pat-small-multiples .sm-hit[data-name="Seattle"]', tipSel: '#pat-small-multiples .sm-tip', expectMatch: /Seattle/ },
  { family: 'magnitude', pattern: 'radar-chart', hoverTarget: '#pat-radar-chart .radar-vertex[data-player="Scoring specialist"][data-axis="scoring"]', tipSel: '#pat-radar-chart .radar-tip', expectMatch: /Scoring specialist/ },
]
for (const c of finaleCases) {
  await gotoPattern(c.family, c.pattern)
  await page.mouse.move(5, 5); await page.waitForTimeout(150)
  const initialTipOp = await page.$eval(c.tipSel, el => +getComputedStyle(el).opacity)
  ok(initialTipOp === 0, `${c.pattern}: tooltip hidden on load (P2)`)
  const el = await page.$(c.hoverTarget)
  if (!el) { ok(false, `${c.pattern}: target ${c.hoverTarget} not found`); continue }
  const b = await el.boundingBox()
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2)
  await page.waitForTimeout(200)
  const state = await page.evaluate(tipSel => {
    const t = document.querySelector(tipSel)
    return { op: t ? +getComputedStyle(t).opacity : null, text: t?.innerText || '' }
  }, c.tipSel)
  ok(state.op === 1, `${c.pattern}: tooltip visible on hover`)
  ok(c.expectMatch.test(state.text), `${c.pattern}: tooltip matches ${c.expectMatch} (${state.text.replace(/\n/g, ' | ').slice(0, 60)})`)
}

// ---------------- treemap (shared drill-in pattern with sunburst + icicle-plot) ----------------
console.log('\ntreemap · click-to-zoom drill-in')
await gotoPattern('part-to-whole', 'treemap')
const tmRoot = await page.$$eval('#pat-treemap .tm-cells > g', gs => ({
  count: gs.length,
  labels: gs.map(g => (g.querySelector('text')?.textContent || '').trim()),
}))
ok(tmRoot.count === 3, `root: 3 top-level cells (got ${tmRoot.count})`)
ok(tmRoot.labels.some(l => l.startsWith('Mandatory')), 'root: Mandatory cell rendered with drill hint')
// Drill into Mandatory
await page.evaluate(() => {
  const t = [...document.querySelectorAll('#pat-treemap .tm-cells text')].find(el => el.textContent.includes('Mandatory'))
  t?.closest('g')?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
})
await page.waitForTimeout(200)
const tmDrilled = await page.$$eval('#pat-treemap .tm-cells > g', gs => gs.length)
ok(tmDrilled === 5, `after drill Mandatory: 5 child cells (got ${tmDrilled})`)
const bc = await page.$eval('#pat-treemap .tm-breadcrumb', el => el.textContent)
ok(bc.includes('Budget') && bc.includes('Mandatory'), `breadcrumb shows path: ${bc.slice(0, 60).trim()}`)
// Click breadcrumb Budget to go home
await page.evaluate(() => {
  const bc = [...document.querySelectorAll('#pat-treemap .tm-breadcrumb text')].find(el => el.textContent.startsWith('Budget'))
  bc?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
})
await page.waitForTimeout(200)
const tmBack = await page.$$eval('#pat-treemap .tm-cells > g', gs => gs.length)
ok(tmBack === 3, `after breadcrumb click: back to 3 top-level cells (got ${tmBack})`)
// Static mode: no drill hint
await toggleMode('treemap')
const tmStatic = await page.$$eval('#pat-treemap .tm-cells > g', gs => {
  return gs.some(g => (g.querySelector('text')?.textContent || '').includes('↓'))
})
ok(!tmStatic, 'static mode: no "↓" drill hints (P4)')

await browser.close()

console.log()
if (failures.length) {
  console.log(`FAIL: ${failures.length} assertion(s) did not pass:`)
  for (const f of failures) console.log(`  - ${f}`)
}
if (errors.length) {
  console.log(`${errors.length} console/page error(s):`)
  for (const e of errors) console.log(`  - ${e}`)
}
if (failures.length === 0 && errors.length === 0) console.log('all interactive checks pass')
process.exit((failures.length || errors.length) ? 1 : 0)
