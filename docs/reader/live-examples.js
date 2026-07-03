// Tiny live renderers for a curated subset of patterns.
//
// Each function takes a DOM container and renders a compact demo
// keyed to the pattern. Data is synthetic on purpose — the point is
// to show the form working, not to present a real dataset.
//
// Registered in DEMO_BY_ID at the bottom; main.js looks up by
// pattern id and calls the renderer if one exists.

import * as d3 from 'd3'

const COLORS = {
  accent: '#6366f1',
  good:   '#22d3ee',
  warm:   '#f59e0b',
  danger: '#f87171',
  green:  '#22c55e',
  purple: '#a78bfa',
  mute:   '#525252',
  grid:   '#1f1f1f',
  text:   '#d4d4d4',
  label:  '#a3a3a3',
  bg:     '#0a0a0a',
}

// --------------------------------------------------------- bar-chart
export function renderBarChartDemo(container) {
  const data = [
    { name: 'Netflix',   value: 215 },
    { name: 'Prime',     value: 175 },
    { name: 'Disney+',   value: 150 },
    { name: 'HBO Max',   value:  93 },
    { name: 'Apple TV+', value:  72 },
    { name: 'Paramount', value:  67 },
    { name: 'Peacock',   value:  33 },
  ].sort((a, b) => b.value - a.value)

  const W = 620, H = 240
  const margin = { top: 12, right: 60, bottom: 12, left: 110 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const y = d3.scaleBand().domain(data.map(d => d.name))
    .range([margin.top, H - margin.bottom]).padding(0.2)
  const x = d3.scaleLinear().domain([0, d3.max(data, d => d.value) * 1.08])
    .range([margin.left, W - margin.right])

  svg.append('g').selectAll('rect').data(data).join('rect')
    .attr('x', x(0)).attr('y', d => y(d.name))
    .attr('width', d => x(d.value) - x(0)).attr('height', y.bandwidth())
    .attr('fill', COLORS.accent)
  svg.append('g').selectAll('text.lab').data(data).join('text').attr('class', 'lab')
    .attr('x', margin.left - 8).attr('y', d => y(d.name) + y.bandwidth() / 2 + 4)
    .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 12)
    .text(d => d.name)
  svg.append('g').selectAll('text.val').data(data).join('text').attr('class', 'val')
    .attr('x', d => x(d.value) + 6).attr('y', d => y(d.name) + y.bandwidth() / 2 + 4)
    .attr('fill', COLORS.label).attr('font-size', 11).text(d => d.value + 'M')
}

// --------------------------------------------------------- stacked-bar
export function renderStackedBarDemo(container) {
  // Budget breakdown across three departments. 100%-stacked so
  // composition is comparable.
  const data = [
    { dept: 'Engineering', Salaries: 6.2, Infra: 1.4, Tools: 0.4, Travel: 0.3 },
    { dept: 'Sales',       Salaries: 3.8, Infra: 0.2, Tools: 0.3, Travel: 1.2 },
    { dept: 'Marketing',   Salaries: 2.1, Infra: 0.3, Tools: 0.7, Travel: 0.4 },
    { dept: 'Ops',         Salaries: 1.5, Infra: 0.8, Tools: 0.2, Travel: 0.2 },
  ]
  const keys = ['Salaries', 'Infra', 'Tools', 'Travel']
  const colors = {
    Salaries: COLORS.accent, Infra: COLORS.good, Tools: COLORS.warm, Travel: COLORS.purple,
  }

  const W = 620, H = 220
  const margin = { top: 28, right: 20, bottom: 12, left: 110 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const totals = data.map(r => keys.reduce((s, k) => s + r[k], 0))
  const xMax = d3.max(totals)
  const x = d3.scaleLinear().domain([0, xMax]).range([margin.left, W - margin.right])
  const y = d3.scaleBand().domain(data.map(d => d.dept))
    .range([margin.top, H - margin.bottom]).padding(0.22)

  for (const [i, row] of data.entries()) {
    let cursor = x(0)
    for (const k of keys) {
      const w = x(row[k]) - x(0)
      svg.append('rect')
        .attr('x', cursor).attr('y', y(row.dept))
        .attr('width', w).attr('height', y.bandwidth())
        .attr('fill', colors[k])
      cursor += w
    }
    svg.append('text')
      .attr('x', margin.left - 8).attr('y', y(row.dept) + y.bandwidth() / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 12)
      .text(row.dept)
  }

  // Legend
  let lx = margin.left
  for (const k of keys) {
    svg.append('rect').attr('x', lx).attr('y', 10)
      .attr('width', 10).attr('height', 10).attr('fill', colors[k])
    svg.append('text').attr('x', lx + 14).attr('y', 19)
      .attr('fill', COLORS.label).attr('font-size', 11).text(k)
    lx += (`${k}`.length) * 7 + 36
  }
}

// --------------------------------------------------------- scatterplot
export function renderScatterplotDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Life expectancy × GDP per capita (synthetic, rough shape). Each
  // point gets a fake country label so the tooltip has something to say.
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(42)
  const countryPool = [
    'Albion', 'Bastia', 'Corvia', 'Dalmar', 'Elior', 'Fenland', 'Gareth', 'Hollin',
    'Iberan', 'Jaron', 'Kestra', 'Loriel', 'Marenia', 'Noskia', 'Oralia', 'Palmyr',
    'Querin', 'Rendal', 'Serova', 'Tirana', 'Ulima', 'Valdor', 'Wendol', 'Xanthe',
    'Yolan', 'Zanth', 'Arvia', 'Bor', 'Cael', 'Darth', 'Eira', 'Foris',
    'Gale', 'Haris', 'Ilsa', 'Jorn', 'Krena', 'Lund', 'Mirn', 'Norr',
    'Osra', 'Prent', 'Quina', 'Raska', 'Solin', 'Tora', 'Uren', 'Velor',
    'Wren', 'Xera', 'Ymla', 'Zora', 'Ara', 'Brio', 'Cova', 'Dren',
    'Era', 'Frev', 'Gyr', 'Hast', 'Iska', 'Joss', 'Kven', 'Lax',
    'Mor', 'Nova', 'Orel', 'Pav', 'Quor', 'Riv', 'Sev', 'Trom',
    'Uist', 'Vass', 'Wyn', 'Xol', 'Yrn', 'Zef', 'Aur', 'Bev', 'Cyr', 'Dax',
  ]
  const data = []
  for (let i = 0; i < 80; i++) {
    const gdp = Math.exp(rng() * 4 + 6)           // 400 - 22000
    const lex = 55 + Math.log(gdp) * 3 + (rng() - 0.5) * 8
    data.push({ gdp, lex, country: countryPool[i] })
  }

  const W = 620, H = 280
  const margin = { top: 14, right: 20, bottom: 36, left: 44 }
  // Relative host so the absolute-positioned tooltip anchors correctly
  d3.select(container).style('position', 'relative')
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const x = d3.scaleLog().domain([300, 30000]).range([margin.left, W - margin.right])
  const y = d3.scaleLinear().domain([50, 85]).range([H - margin.bottom, margin.top])

  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).tickValues([500, 1000, 5000, 20000]).tickFormat(d => '$' + d.toLocaleString()))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  svg.append('text').attr('x', W - margin.right).attr('y', H - 8)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10)
    .text('GDP per capita (log)')
  svg.append('text').attr('x', margin.left).attr('y', margin.top - 3)
    .attr('fill', COLORS.label).attr('font-size', 10).text('Life expectancy')

  // Points. Each point is given a data-index so the hover handler can
  // cheaply flip opacity without rebinding data.
  const dotsLayer = svg.append('g').attr('class', 'dots')
  data.forEach((d, i) => {
    dotsLayer.append('circle')
      .attr('data-idx', i)
      .attr('cx', x(d.gdp)).attr('cy', y(d.lex))
      .attr('r', 3.5).attr('fill', COLORS.good).attr('fill-opacity', 0.65)
  })

  // Static outlier annotation — the chart's editorial point. Present in
  // both static and interactive modes (P4: the static chart is the contract).
  const sorted = [...data].sort((a, b) =>
    (a.lex - Math.log(a.gdp) * 3) - (b.lex - Math.log(b.gdp) * 3)
  )
  const below = sorted[0]
  const cx0 = x(below.gdp), cy0 = y(below.lex)
  svg.append('circle').attr('cx', cx0).attr('cy', cy0).attr('r', 7)
    .attr('fill', 'none').attr('stroke', COLORS.warm).attr('stroke-width', 1.2)
  svg.append('text').attr('x', cx0 + 12).attr('y', cy0 + 4)
    .attr('fill', COLORS.warm).attr('font-size', 10).attr('font-style', 'italic')
    .text('outlier — below the cloud, worth asking why')

  if (!interactive) return

  // INTERACTIVE ENHANCEMENT (P2: details on demand; P10: one affordance)
  // Voronoi hover: nearest-point lookup without having to hit a 3.5px dot.
  const delaunay = d3.Delaunay.from(data, d => x(d.gdp), d => y(d.lex))

  // HTML tooltip — escapes the SVG viewBox so it's crisp at any zoom
  const tooltip = d3.select(container).append('div')
    .attr('class', 'scatter-tip')
    .style('position', 'absolute').style('pointer-events', 'none')
    .style('background', '#0f0f0f').style('border', '1px solid #2a2a2a')
    .style('padding', '6px 9px').style('border-radius', '4px')
    .style('font-size', '11px').style('color', '#e5e5e5')
    .style('opacity', 0).style('transition', 'opacity 120ms')
    .style('transform', 'translate(8px, -100%)')
    .attr('role', 'status').attr('aria-live', 'polite')

  let pinned = false
  let pinnedIdx = -1

  function highlight(idx) {
    // P7: fade others, not spotlight one
    dotsLayer.selectAll('circle').each(function (_, i) {
      // i here is the join index; we stored data-idx attributes separately
      const el = d3.select(this)
      const dataIdx = +el.attr('data-idx')
      const isOn = dataIdx === idx
      el.attr('fill-opacity', isOn ? 1 : 0.18)
        .attr('r', isOn ? 5 : 3.5)
    })
  }
  function clearHighlight() {
    dotsLayer.selectAll('circle').attr('fill-opacity', 0.65).attr('r', 3.5)
  }
  function showTip(idx, pageX, pageY) {
    const d = data[idx]
    const hostRect = container.getBoundingClientRect()
    tooltip.html(
      `<strong>${d.country}</strong><br>` +
      `GDP/capita: $${Math.round(d.gdp).toLocaleString()}<br>` +
      `Life exp: ${d.lex.toFixed(1)} yrs`
    )
    tooltip
      .style('left', (pageX - hostRect.left - window.scrollX) + 'px')
      .style('top', (pageY - hostRect.top - window.scrollY) + 'px')
      .style('opacity', 1)
  }
  function hideTip() {
    tooltip.style('opacity', 0)
  }

  // Transparent overlay captures mouse + touch events across the chart area
  const overlay = svg.append('rect')
    .attr('x', margin.left).attr('y', margin.top)
    .attr('width', W - margin.left - margin.right)
    .attr('height', H - margin.top - margin.bottom)
    .attr('fill', 'transparent')
    .style('cursor', 'crosshair')

  overlay.on('mousemove', function (event) {
    if (pinned) return
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    highlight(idx)
    showTip(idx, event.pageX, event.pageY)
  })
  overlay.on('mouseleave', () => {
    if (pinned) return
    clearHighlight(); hideTip()
  })
  // P5: touch equivalent — tap to pin, tap again (or outside) to unpin
  overlay.on('click', function (event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    if (pinned && pinnedIdx === idx) {
      pinned = false; pinnedIdx = -1
      clearHighlight(); hideTip()
    } else {
      pinned = true; pinnedIdx = idx
      highlight(idx); showTip(idx, event.pageX, event.pageY)
    }
  })
}

// --------------------------------------------------------- bump-chart
export function renderBumpChartDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const years = [2019, 2020, 2021, 2022, 2023]
  const series = [
    { brand: 'Apple',     ranks: [1, 1, 1, 1, 1], color: COLORS.danger },
    { brand: 'Google',    ranks: [2, 2, 2, 2, 2], color: COLORS.good },
    { brand: 'Amazon',    ranks: [3, 3, 3, 4, 5], color: COLORS.warm },
    { brand: 'Microsoft', ranks: [4, 4, 3, 3, 3], color: COLORS.purple },
    { brand: 'Samsung',   ranks: [5, 5, 5, 5, 4], color: COLORS.green },
    { brand: 'Sony',      ranks: [6, 7, 7, 7, 6], color: COLORS.mute },
    { brand: 'IBM',       ranks: [7, 6, 6, 6, 7], color: COLORS.accent },
  ]

  const W = 620, H = 260
  const margin = { top: 16, right: 90, bottom: 28, left: 50 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const x = d3.scaleLinear().domain([years[0], years[years.length - 1]])
    .range([margin.left, W - margin.right])
  const y = d3.scaleLinear().domain([0.5, 7.5])
    .range([margin.top, H - margin.bottom])

  svg.append('g').selectAll('text.r').data([1, 2, 3, 4, 5, 6, 7]).join('text').attr('class', 'r')
    .attr('x', margin.left - 10).attr('y', d => y(d) + 4)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10)
    .text(d => '#' + d)

  svg.append('g').selectAll('text.x').data(years).join('text').attr('class', 'x')
    .attr('x', x).attr('y', H - margin.bottom + 16)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 10).text(d => d)

  const line = d3.line().x((_, i) => x(years[i])).y(d => y(d)).curve(d3.curveMonotoneX)

  // Build per-series DOM refs so interactive mode can flip them cheaply
  const seriesG = svg.append('g').attr('class', 'bump-series')
  const seriesNodes = []
  for (const s of series) {
    const g = seriesG.append('g').attr('data-brand', s.brand)
    const path = g.append('path').datum(s.ranks).attr('d', line)
      .attr('fill', 'none').attr('stroke', s.color).attr('stroke-width', 2)
    const dots = []
    s.ranks.forEach((r, i) => {
      const c = g.append('circle').attr('cx', x(years[i])).attr('cy', y(r))
        .attr('r', 3).attr('fill', s.color)
      dots.push(c)
    })
    const label = svg.append('text')
      .attr('x', x(years[years.length - 1]) + 8)
      .attr('y', y(s.ranks[s.ranks.length - 1]) + 3)
      .attr('fill', s.color).attr('font-size', 11).text(s.brand)
    seriesNodes.push({ s, path, dots, label })
  }

  const crossYear = 2021
  const cXX = x(crossYear), cYY = (y(3) + y(4)) / 2
  svg.append('circle').attr('cx', cXX).attr('cy', cYY).attr('r', 11)
    .attr('fill', 'none').attr('stroke', COLORS.warm)
    .attr('stroke-width', 1).attr('stroke-dasharray', '2 2')
  svg.append('line').attr('x1', cXX).attr('x2', cXX)
    .attr('y1', margin.top + 20).attr('y2', cYY - 12)
    .attr('stroke', COLORS.warm).attr('stroke-opacity', 0.5).attr('stroke-dasharray', '2 2')
  svg.append('text').attr('x', cXX).attr('y', margin.top + 12)
    .attr('text-anchor', 'middle').attr('fill', COLORS.warm)
    .attr('font-size', 10).attr('font-weight', 600)
    .text('MSFT ↗ AMZN ↘')

  if (!interactive) return

  // INTERACTIVE (P10: one affordance — hover-to-isolate-a-brand)
  // Hover a brand's right-edge label or its line to spotlight it.
  // Rest fade to P7's 0.2 contrast. Click label to pin.
  let pinned = null
  function spotlight(brand) {
    for (const n of seriesNodes) {
      const on = n.s.brand === brand
      n.path.attr('stroke-opacity', on ? 1 : 0.18).attr('stroke-width', on ? 2.5 : 2)
      for (const d of n.dots) d.attr('fill-opacity', on ? 1 : 0.18)
      n.label.attr('fill-opacity', on ? 1 : 0.3).attr('font-weight', on ? 700 : 400)
    }
  }
  function clearSpotlight() {
    for (const n of seriesNodes) {
      n.path.attr('stroke-opacity', 1).attr('stroke-width', 2)
      for (const d of n.dots) d.attr('fill-opacity', 1)
      n.label.attr('fill-opacity', 1).attr('font-weight', 400)
    }
  }
  for (const n of seriesNodes) {
    const hoverTargets = [n.path, n.label, ...n.dots]
    for (const t of hoverTargets) {
      t.style('cursor', 'pointer')
      t.on('mouseenter', () => { if (!pinned) spotlight(n.s.brand) })
      t.on('mouseleave', () => { if (!pinned) clearSpotlight() })
    }
    n.label.on('click', (event) => {
      event.stopPropagation()
      if (pinned === n.s.brand) { pinned = null; clearSpotlight() }
      else { pinned = n.s.brand; spotlight(n.s.brand) }
    })
  }
  // Click empty area to unpin (P3: click commits, click background reverts)
  svg.on('click', () => { if (pinned) { pinned = null; clearSpotlight() } })
}

// --------------------------------------------------------- sankey (energy mix)
// A tiny hand-laid sankey rather than pulling d3-sankey — the demo
// stays tight and the layout is predictable.
export function renderSankeyDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const sources = [
    { name: 'Solar',   value: 160, color: COLORS.warm },
    { name: 'Wind',    value: 180, color: COLORS.good },
    { name: 'Nuclear', value: 150, color: COLORS.purple },
    { name: 'Gas',     value: 240, color: COLORS.mute },
    { name: 'Coal',    value: 120, color: '#404040' },
  ]
  const uses = [
    { name: 'Industry',  value: 280, color: COLORS.danger },
    { name: 'Buildings', value: 300, color: COLORS.green },
    { name: 'Transport', value:  70, color: COLORS.accent },
    { name: 'Losses',    value: 200, color: COLORS.mute },
  ]
  const flow = [
    [40, 70, 10, 40],
    [50, 80, 10, 40],
    [40, 60, 10, 40],
    [80, 70, 30, 60],
    [70, 20, 10, 20],
  ]

  const W = 620, H = 280
  const margin = { top: 16, right: 90, bottom: 16, left: 80 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const total = sources.reduce((s, n) => s + n.value, 0)
  const innerH = H - margin.top - margin.bottom
  const padding = 8

  let yCur = margin.top
  const srcY = sources.map(s => {
    const h = (s.value / total) * (innerH - padding * (sources.length - 1))
    const node = { ...s, y0: yCur, y1: yCur + h, h }
    yCur += h + padding
    return node
  })
  yCur = margin.top
  const useY = uses.map(u => {
    const h = (u.value / total) * (innerH - padding * (uses.length - 1))
    const node = { ...u, y0: yCur, y1: yCur + h, h }
    yCur += h + padding
    return node
  })

  const xSrcR = margin.left + 10
  const xUseL = W - margin.right - 10

  // Draw ribbons and keep DOM refs so we can flip opacity cheaply
  const ribbons = []
  const srcOff = srcY.map(s => s.y0)
  const useOff = useY.map(u => u.y0)
  for (let i = 0; i < sources.length; i++) {
    for (let j = 0; j < uses.length; j++) {
      const v = flow[i][j]
      if (!v) continue
      const hs = (v / sources[i].value) * srcY[i].h
      const hu = (v / uses[j].value) * useY[j].h
      const y0 = srcOff[i], y1 = useOff[j]
      srcOff[i] += hs; useOff[j] += hu
      const cx = (xSrcR + xUseL) / 2
      const top = `M ${xSrcR} ${y0} C ${cx} ${y0}, ${cx} ${y1}, ${xUseL} ${y1}`
      const bot = `L ${xUseL} ${y1 + hu} C ${cx} ${y1 + hu}, ${cx} ${y0 + hs}, ${xSrcR} ${y0 + hs} Z`
      const p = svg.append('path').attr('d', top + ' ' + bot)
        .attr('fill', srcY[i].color).attr('fill-opacity', 0.55).attr('stroke', 'none')
      ribbons.push({ path: p, i, j, v })
    }
  }

  // Nodes — keep refs so interactive mode can distinguish clicked from not
  const srcNodes = []
  for (let i = 0; i < srcY.length; i++) {
    const s = srcY[i]
    const rect = svg.append('rect').attr('x', margin.left).attr('y', s.y0)
      .attr('width', 10).attr('height', s.h).attr('fill', s.color)
    const label = svg.append('text').attr('x', margin.left - 6).attr('y', (s.y0 + s.y1) / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11).text(s.name)
    srcNodes.push({ rect, label, side: 'src', idx: i })
  }
  const useNodes = []
  for (let j = 0; j < useY.length; j++) {
    const u = useY[j]
    const rect = svg.append('rect').attr('x', W - margin.right).attr('y', u.y0)
      .attr('width', 10).attr('height', u.h).attr('fill', u.color)
    const label = svg.append('text').attr('x', W - margin.right + 16).attr('y', (u.y0 + u.y1) / 2 + 4)
      .attr('fill', COLORS.text).attr('font-size', 11).text(u.name)
    useNodes.push({ rect, label, side: 'use', idx: j })
  }

  svg.append('text').attr('x', margin.left).attr('y', margin.top - 4)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em').text('SOURCE')
  svg.append('text').attr('x', W - margin.right).attr('y', margin.top - 4)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em').text('END-USE')
  svg.append('text').attr('x', W / 2).attr('y', margin.top - 4)
    .attr('text-anchor', 'middle').attr('fill', COLORS.warm).attr('font-size', 10)
    .attr('font-weight', 600).text(`left total = right total = ${total}`)
  svg.append('text').attr('x', W - 8).attr('y', H - 8)
    .attr('text-anchor', 'end').attr('fill', COLORS.warm)
    .attr('font-size', 9).attr('font-style', 'italic')
    .text('losses closes the balance')

  if (!interactive) return

  // INTERACTIVE (P10: one affordance — click-to-isolate a node's flows)
  // Clicking a source or end-use dims non-connected ribbons to reveal only
  // that node's full flow. Dim-don't-hide (sankey common_mistake) keeps
  // the context — reader can still see the whole story behind the spotlight.
  let selected = null   // {side, idx} | null

  function isRibbonConnected(r, sel) {
    if (!sel) return true
    return (sel.side === 'src' && r.i === sel.idx)
        || (sel.side === 'use' && r.j === sel.idx)
  }
  function applySelection() {
    for (const r of ribbons) {
      const on = isRibbonConnected(r, selected)
      // When nothing is selected, every ribbon is "on" — restore the
      // default 0.55 rather than the highlighted-on 0.8.
      const opacity = selected == null ? 0.55 : (on ? 0.85 : 0.08)
      r.path.attr('fill-opacity', opacity)
    }
    for (const n of [...srcNodes, ...useNodes]) {
      const isSel = selected && n.side === selected.side && n.idx === selected.idx
      // All other nodes dim their label; selected node's label becomes bold.
      n.label.attr('fill-opacity', selected && !isSel ? 0.35 : 1)
        .attr('font-weight', isSel ? 700 : 400)
      // Selected node gets a visible ring; others unchanged.
      n.rect.attr('stroke', isSel ? '#f5f5f5' : 'none').attr('stroke-width', isSel ? 1.5 : 0)
    }
  }
  function clearSelection() { selected = null; applySelection() }

  // Pointer cursors only on interactive surfaces
  for (const n of [...srcNodes, ...useNodes]) {
    n.rect.style('cursor', 'pointer')
    n.label.style('cursor', 'pointer')
    const handler = (event) => {
      event.stopPropagation()
      if (selected && selected.side === n.side && selected.idx === n.idx) {
        clearSelection()
      } else {
        selected = { side: n.side, idx: n.idx }
        applySelection()
      }
    }
    n.rect.on('click', handler)
    n.label.on('click', handler)
  }
  // Click background to clear
  svg.on('click', () => { if (selected) clearSelection() })

  // Small affordance hint (P8: tell the reader what the control does)
  svg.append('text').attr('x', 8).attr('y', H - 8)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('font-style', 'italic')
    .text('click a node to isolate its flow')
}

// --------------------------------------------------------- heatmap
export function renderHeatmapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(7)
  const data = []
  for (const d of days) {
    for (const h of hours) {
      let base = 0
      if (['Mon','Tue','Wed','Thu','Fri'].includes(d) && h >= 8 && h <= 10) base = 70
      else if (['Mon','Tue','Wed','Thu','Fri'].includes(d) && h >= 18 && h <= 22) base = 90
      else if (['Sat','Sun'].includes(d) && h >= 12 && h <= 16) base = 55
      else if (h >= 8 && h <= 22) base = 30
      else base = 8
      data.push({ d, h, v: base + (rng() - 0.5) * 12 })
    }
  }

  const W = 620, H = 220
  const margin = { top: 24, right: 20, bottom: 30, left: 44 }
  d3.select(container).style('position', 'relative')
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const cw = (W - margin.left - margin.right) / 24
  const ch = (H - margin.top - margin.bottom) / 7
  const color = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, d3.max(data, d => d.v)])

  const cells = svg.append('g').attr('class', 'cells').selectAll('rect').data(data).join('rect')
    .attr('x', d => margin.left + d.h * cw)
    .attr('y', d => margin.top + days.indexOf(d.d) * ch)
    .attr('width', cw - 1).attr('height', ch - 1)
    .attr('fill', d => color(d.v))

  svg.append('g').selectAll('text.d').data(days).join('text').attr('class', 'd')
    .attr('x', margin.left - 6).attr('y', (d, i) => margin.top + i * ch + ch / 2 + 4)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10).text(d => d)

  for (const h of [0, 6, 12, 18]) {
    svg.append('text')
      .attr('x', margin.left + h * cw + cw / 2).attr('y', H - margin.bottom + 14)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 10)
      .text(h.toString().padStart(2, '0') + ':00')
  }
  svg.append('text').attr('x', margin.left).attr('y', margin.top - 8)
    .attr('fill', COLORS.label).attr('font-size', 10).attr('letter-spacing', '0.1em')
    .text('WEB TRAFFIC · day × hour')

  if (!interactive) return

  // INTERACTIVE (P10: one affordance — cross-hair + cell readout)
  // Cross-hair row + column highlight reads small-multiples style across
  // the whole day or hour, plus exact value for the cell under the cursor.
  const crossRow = svg.append('rect').attr('class', 'cross-row')
    .attr('x', margin.left).attr('width', W - margin.left - margin.right)
    .attr('height', ch - 1).attr('fill', 'none')
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1).attr('stroke-opacity', 0)
    .style('pointer-events', 'none')
  const crossCol = svg.append('rect').attr('class', 'cross-col')
    .attr('y', margin.top).attr('height', H - margin.top - margin.bottom)
    .attr('width', cw - 1).attr('fill', 'none')
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1).attr('stroke-opacity', 0)
    .style('pointer-events', 'none')

  const tooltip = d3.select(container).append('div')
    .attr('class', 'heatmap-tip')
    .style('position', 'absolute').style('pointer-events', 'none')
    .style('background', '#0f0f0f').style('border', '1px solid #2a2a2a')
    .style('padding', '6px 9px').style('border-radius', '4px')
    .style('font-size', '11px').style('color', '#e5e5e5').style('opacity', 0)
    .style('transition', 'opacity 120ms').style('transform', 'translate(10px, -50%)')
    .attr('role', 'status').attr('aria-live', 'polite')

  function move(d, pageX, pageY) {
    crossRow.attr('y', margin.top + days.indexOf(d.d) * ch).attr('stroke-opacity', 0.6)
    crossCol.attr('x', margin.left + d.h * cw).attr('stroke-opacity', 0.6)
    const hostRect = container.getBoundingClientRect()
    tooltip.html(
      `<strong>${d.d} · ${d.h.toString().padStart(2,'0')}:00</strong><br>` +
      `<span style="color:#a3a3a3">traffic:</span> ${d.v.toFixed(0)}`
    )
      .style('left', (pageX - hostRect.left - window.scrollX) + 'px')
      .style('top', (pageY - hostRect.top - window.scrollY) + 'px')
      .style('opacity', 1)
  }
  function clear() {
    crossRow.attr('stroke-opacity', 0)
    crossCol.attr('stroke-opacity', 0)
    tooltip.style('opacity', 0)
  }

  cells.style('cursor', 'crosshair')
    .on('mousemove', function (event, d) { move(d, event.pageX, event.pageY) })
    .on('mouseleave', clear)
    .on('click', function (event, d) { move(d, event.pageX, event.pageY) }) // P5: tap updates
}

// --------------------------------------------------------- line-chart
export function renderLineChartDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const years = Array.from({ length: 20 }, (_, i) => 2004 + i)
  const series = [
    { name: 'GDP',         color: COLORS.accent,
      values: years.map((_, i) => 100 + i * 2.5 + Math.sin(i / 3) * 5) },
    { name: 'Consumption', color: COLORS.good,
      values: years.map((_, i) => 95 + i * 2.1 + Math.cos(i / 2.5) * 3) },
    { name: 'Investment',  color: COLORS.warm,
      values: years.map((_, i) => 80 + i * 3.2 + (i === 5 || i === 15 ? -14 : 0) + Math.sin(i / 4) * 6) },
  ]

  const W = 620, H = 260
  const margin = { top: 16, right: 110, bottom: 32, left: 44 }
  d3.select(container).style('position', 'relative')
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const x = d3.scaleLinear().domain([years[0], years[years.length - 1]])
    .range([margin.left, W - margin.right])
  const allVals = series.flatMap(s => s.values)
  const y = d3.scaleLinear()
    .domain([d3.min(allVals) - 5, d3.max(allVals) + 5])
    .range([H - margin.bottom, margin.top])

  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  const line = d3.line()
    .x((_, i) => x(years[i])).y(d => y(d)).curve(d3.curveMonotoneX)
  const pathNodes = []
  for (const s of series) {
    const p = svg.append('path').datum(s.values).attr('d', line)
      .attr('fill', 'none').attr('stroke', s.color).attr('stroke-width', 2)
      .attr('data-name', s.name)
    pathNodes.push({ s, path: p })
  }
  const labelData = series
    .map(s => ({
      color: s.color, name: s.name,
      y: y(s.values[s.values.length - 1]),
    }))
    .sort((a, b) => a.y - b.y)
  const minGap = 14
  for (let i = 1; i < labelData.length; i++) {
    if (labelData[i].y - labelData[i - 1].y < minGap) {
      labelData[i].y = labelData[i - 1].y + minGap
    }
  }
  const labelNodes = new Map()
  for (const l of labelData) {
    const t = svg.append('text')
      .attr('x', x(years[years.length - 1]) + 8)
      .attr('y', l.y + 4)
      .attr('fill', l.color).attr('font-size', 11)
      .attr('font-weight', 500).text(l.name)
    labelNodes.set(l.name, t)
  }

  if (!interactive) return

  // INTERACTIVE (P10: one affordance — time-cursor + value-readout across series)
  // Mouse along the x-axis; a vertical cursor snaps to nearest year,
  // and a tooltip shows the value of every series at that x. This is
  // the "voronoi" alternative for 1D line charts — nearest-x is what
  // readers actually want when comparing series.
  const cursorGroup = svg.append('g').attr('class', 'time-cursor')
    .style('opacity', 0).style('pointer-events', 'none')
  const cursorLine = cursorGroup.append('line')
    .attr('y1', margin.top).attr('y2', H - margin.bottom)
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1).attr('stroke-dasharray', '2 3')
  const cursorDots = pathNodes.map(n =>
    cursorGroup.append('circle').attr('r', 4)
      .attr('fill', n.s.color).attr('stroke', '#0a0a0a').attr('stroke-width', 1.5)
  )
  const cursorYear = cursorGroup.append('text')
    .attr('y', margin.top - 4).attr('text-anchor', 'middle')
    .attr('fill', COLORS.label).attr('font-size', 10).attr('font-weight', 600)

  const tooltip = d3.select(container).append('div')
    .attr('class', 'line-tip')
    .style('position', 'absolute').style('pointer-events', 'none')
    .style('background', '#0f0f0f').style('border', '1px solid #2a2a2a')
    .style('padding', '6px 9px').style('border-radius', '4px')
    .style('font-size', '11px').style('color', '#e5e5e5').style('opacity', 0)
    .style('transition', 'opacity 120ms').style('transform', 'translate(10px, -50%)')
    .attr('role', 'status').attr('aria-live', 'polite')

  function yearAt(mx) {
    const yearF = x.invert(mx)
    return Math.max(years[0], Math.min(years[years.length - 1], Math.round(yearF)))
  }
  function update(mx, pageX, pageY) {
    const year = yearAt(mx)
    const idx = year - years[0]
    cursorGroup.style('opacity', 1)
    cursorLine.attr('x1', x(year)).attr('x2', x(year))
    pathNodes.forEach((n, i) =>
      cursorDots[i].attr('cx', x(year)).attr('cy', y(n.s.values[idx]))
    )
    cursorYear.attr('x', x(year)).text(year)

    const rows = pathNodes
      .map(n => ({ name: n.s.name, val: n.s.values[idx], color: n.s.color }))
      .sort((a, b) => b.val - a.val)
    const html = `<div style="font-weight:600;margin-bottom:3px">${year}</div>` +
      rows.map(r =>
        `<div><span style="display:inline-block;width:8px;height:8px;background:${r.color};margin-right:5px;border-radius:2px;"></span>` +
        `<span style="color:#a3a3a3">${r.name}:</span> ${r.val.toFixed(1)}</div>`
      ).join('')
    tooltip.html(html)
    const hostRect = container.getBoundingClientRect()
    tooltip
      .style('left', (pageX - hostRect.left - window.scrollX) + 'px')
      .style('top', (pageY - hostRect.top - window.scrollY) + 'px')
      .style('opacity', 1)
  }
  function clear() {
    cursorGroup.style('opacity', 0)
    tooltip.style('opacity', 0)
  }

  const overlay = svg.append('rect')
    .attr('x', margin.left).attr('y', margin.top)
    .attr('width', W - margin.right - margin.left)
    .attr('height', H - margin.top - margin.bottom)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  overlay.on('mousemove', event => {
    const [mx] = d3.pointer(event, svg.node())
    update(mx, event.pageX, event.pageY)
  })
  overlay.on('mouseleave', clear)
  overlay.on('click', event => {
    // P5: tap-to-pin on touch / tap devices — treat click same as hover,
    // leave state as-is so the reader can tap around
    const [mx] = d3.pointer(event, svg.node())
    update(mx, event.pageX, event.pageY)
  })
}

// --------------------------------------------------------- small-multiples
export function renderSmallMultiplesDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // 9 cities' monthly precipitation patterns — one mini-chart each
  const months = Array.from({ length: 12 }, (_, i) => i)
  const cities = [
    { name: 'Seattle',    peak: 11, amp: 3.5, base: 4.5 },
    { name: 'Los Angeles',peak:  1, amp: 2.5, base: 2.0 },
    { name: 'Denver',     peak:  5, amp: 1.2, base: 1.5 },
    { name: 'Austin',     peak:  4, amp: 1.8, base: 2.2 },
    { name: 'Chicago',    peak:  6, amp: 1.8, base: 3.0 },
    { name: 'New York',   peak:  5, amp: 0.9, base: 3.5 },
    { name: 'Miami',      peak:  8, amp: 4.0, base: 3.0 },
    { name: 'Phoenix',    peak:  8, amp: 0.8, base: 0.7 },
    { name: 'Portland',   peak: 11, amp: 3.0, base: 4.0 },
  ]
  for (const c of cities) {
    c.values = months.map(m => {
      const dist = Math.min(Math.abs(m - c.peak), 12 - Math.abs(m - c.peak))
      return c.base + c.amp * Math.cos((dist / 6) * Math.PI)
    })
  }
  const yMax = d3.max(cities.flatMap(c => c.values)) + 0.5

  const W = 620, H = 360
  const cols = 3, rows = 3
  const padX = 14, padY = 18
  const panelW = (W - padX * (cols + 1)) / cols
  const panelH = (H - padY * (rows + 1)) / rows

  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const panelRefs = []
  for (let i = 0; i < cities.length; i++) {
    const r = Math.floor(i / cols), cIdx = i % cols
    const x0 = padX + cIdx * (panelW + padX)
    const y0 = padY + r * (panelH + padY)
    const c = cities[i]
    const g = svg.append('g').attr('transform', `translate(${x0},${y0})`)

    const x = d3.scaleLinear().domain([0, 11]).range([0, panelW])
    const y = d3.scaleLinear().domain([0, yMax]).range([panelH, 18])

    const bg = g.append('rect').attr('width', panelW).attr('height', panelH)
      .attr('fill', 'none').attr('stroke', COLORS.grid).attr('rx', 3)

    const area = d3.area()
      .x((_, j) => x(j)).y0(panelH).y1(d => y(d)).curve(d3.curveMonotoneX)
    const areaPath = g.append('path').datum(c.values).attr('d', area)
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.18)

    const line = d3.line()
      .x((_, j) => x(j)).y(d => y(d)).curve(d3.curveMonotoneX)
    const linePath = g.append('path').datum(c.values).attr('d', line)
      .attr('fill', 'none').attr('stroke', COLORS.accent).attr('stroke-width', 1.5)

    g.append('text').attr('x', 4).attr('y', 12)
      .attr('fill', COLORS.text).attr('font-size', 10.5)
      .attr('font-weight', 500).attr('pointer-events', 'none').text(c.name)
    panelRefs.push({ c, g, x0, y0, bg, areaPath, linePath, x, y })
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover panel highlights that city + shows peak-month
  // readout; the comparison-across-panels view is what makes small
  // multiples tick, so on hover we foreground one and fade the others)
  const tip = createTooltip(container, { className: 'sm-tip' })
  function spotlight(i) {
    panelRefs.forEach((ref, j) => {
      const on = j === i
      ref.bg.attr('stroke', on ? COLORS.accent : COLORS.grid).attr('stroke-width', on ? 1.5 : 1)
      ref.linePath.attr('stroke-width', on ? 2.2 : 1.5).attr('stroke-opacity', on || i == null ? 1 : 0.3)
      ref.areaPath.attr('fill-opacity', on || i == null ? 0.18 : 0.05)
    })
  }
  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  for (let i = 0; i < panelRefs.length; i++) {
    const ref = panelRefs[i]
    const peakIdx = ref.c.values.indexOf(Math.max(...ref.c.values))
    const troughIdx = ref.c.values.indexOf(Math.min(...ref.c.values))
    const body = `<strong>${ref.c.name}</strong><br>` +
      `<span style="color:#a3a3a3">peak:</span> ${monthNames[peakIdx]} <strong>${ref.c.values[peakIdx].toFixed(1)}"</strong><br>` +
      `<span style="color:#a3a3a3">trough:</span> ${monthNames[troughIdx]} <strong>${ref.c.values[troughIdx].toFixed(1)}"</strong>`
    const hit = svg.append('rect').attr('class', 'sm-hit').attr('data-name', ref.c.name)
      .attr('x', ref.x0).attr('y', ref.y0)
      .attr('width', panelW).attr('height', panelH)
      .attr('fill', 'transparent').style('cursor', 'pointer')
    hit.on('mouseenter', function (event) { spotlight(i); tip.show(event.pageX, event.pageY, body) })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', () => { spotlight(null); tip.hide() })
    hit.on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- slope-chart
export function renderSlopeChartDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Test scores: before → after for 10 students; some moved a lot
  const items = [
    { name: 'Ana',     a: 72, b: 85 },
    { name: 'Ben',     a: 78, b: 82 },
    { name: 'Chen',    a: 65, b: 88 }, // big jump
    { name: 'Dara',    a: 85, b: 87 },
    { name: 'Elise',   a: 62, b: 60 }, // slight drop
    { name: 'Felix',   a: 70, b: 75 },
    { name: 'Grace',   a: 80, b: 79 },
    { name: 'Harish',  a: 55, b: 72 }, // big jump
    { name: 'Iris',    a: 88, b: 91 },
    { name: 'Jae',     a: 68, b: 71 },
  ]

  const W = 620, H = 320
  const margin = { top: 22, right: 110, bottom: 22, left: 110 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const x = d3.scalePoint().domain(['Before', 'After']).range([margin.left, W - margin.right])
  const y = d3.scaleLinear().domain([50, 100]).range([H - margin.bottom, margin.top])

  // Axis labels
  svg.append('text').attr('x', x('Before')).attr('y', margin.top - 6)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label)
    .attr('font-size', 11).attr('letter-spacing', '0.1em').text('BEFORE')
  svg.append('text').attr('x', x('After')).attr('y', margin.top - 6)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label)
    .attr('font-size', 11).attr('letter-spacing', '0.1em').text('AFTER')

  // Highlight the biggest movers
  const movers = new Set(['Chen', 'Harish', 'Elise'])

  // Dodge labels at each end so sibling scores don't overlap
  function dodge(entries, minGap = 14) {
    const sorted = entries.slice().sort((a, b) => a.y - b.y)
    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i].y - sorted[i - 1].y < minGap) {
        sorted[i].y = sorted[i - 1].y + minGap
      }
    }
    return sorted
  }
  const leftLabels = dodge(items.map(d => ({
    d, y: y(d.a), text: `${d.name} ${d.a}`,
  })))
  const rightLabels = dodge(items.map(d => ({
    d, y: y(d.b), text: `${d.b} ${d.name}`,
  })))

  // Lines + points (not dodged; only labels dodge)
  const lineRefs = []
  for (const d of items) {
    const highlight = movers.has(d.name)
    const color = highlight
      ? (d.b > d.a ? COLORS.green : COLORS.danger)
      : COLORS.mute
    const weight = highlight ? 2 : 1
    const line = svg.append('line').attr('class', 'slope-line').attr('data-name', d.name)
      .attr('x1', x('Before')).attr('x2', x('After'))
      .attr('y1', y(d.a)).attr('y2', y(d.b))
      .attr('stroke', color).attr('stroke-width', weight)
      .attr('stroke-opacity', highlight ? 0.95 : 0.5)
    const dotA = svg.append('circle').attr('cx', x('Before')).attr('cy', y(d.a))
      .attr('r', 3).attr('fill', color)
    const dotB = svg.append('circle').attr('cx', x('After')).attr('cy', y(d.b))
      .attr('r', 3).attr('fill', color)
    lineRefs.push({ d, line, dotA, dotB, highlight, color, weight })
  }
  for (const l of leftLabels) {
    const highlight = movers.has(l.d.name)
    const color = highlight ? (l.d.b > l.d.a ? COLORS.green : COLORS.danger) : COLORS.mute
    svg.append('text').attr('x', x('Before') - 8).attr('y', l.y + 4)
      .attr('text-anchor', 'end')
      .attr('fill', highlight ? COLORS.text : COLORS.label)
      .attr('font-size', highlight ? 11 : 10).text(l.text)
  }
  for (const l of rightLabels) {
    const highlight = movers.has(l.d.name)
    const color = highlight ? (l.d.b > l.d.a ? COLORS.green : COLORS.danger) : COLORS.mute
    svg.append('text').attr('x', x('After') + 8).attr('y', l.y + 4)
      .attr('fill', highlight ? COLORS.text : COLORS.label)
      .attr('font-size', highlight ? 11 : 10).text(l.text)
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover a line to isolate it; click-pin for touch.
  // Invisible wider hit-line under each visible line so narrow strokes
  // are easy to target on phones.)
  const tip = createTooltip(container, { className: 'slope-tip' })
  let pinned = null
  function spotlight(name) {
    for (const r of lineRefs) {
      const on = r.d.name === name
      r.line.attr('stroke-opacity', on ? 1 : 0.12).attr('stroke-width', on ? r.weight + 1 : r.weight)
      r.dotA.attr('fill-opacity', on ? 1 : 0.18); r.dotB.attr('fill-opacity', on ? 1 : 0.18)
    }
  }
  function clearSpotlight() {
    for (const r of lineRefs) {
      r.line.attr('stroke-opacity', r.highlight ? 0.95 : 0.5).attr('stroke-width', r.weight)
      r.dotA.attr('fill-opacity', 1); r.dotB.attr('fill-opacity', 1)
    }
  }
  for (const r of lineRefs) {
    const hit = svg.append('line').attr('class', 'slope-hit').attr('data-name', r.d.name)
      .attr('x1', x('Before')).attr('x2', x('After'))
      .attr('y1', y(r.d.a)).attr('y2', y(r.d.b))
      .attr('stroke', 'transparent').attr('stroke-width', 14).style('cursor', 'pointer')
    const delta = r.d.b - r.d.a
    const sign = delta >= 0 ? '+' : ''
    const body = `<strong>${r.d.name}</strong><br>` +
      `<span style="color:#a3a3a3">before:</span> <strong>${r.d.a}</strong> → ` +
      `<span style="color:#a3a3a3">after:</span> <strong>${r.d.b}</strong> ` +
      `<span style="color:${delta > 0 ? '#86efac' : delta < 0 ? '#f87171' : '#737373'}">(${sign}${delta})</span>`
    hit.on('mouseenter', function (event) { if (!pinned) spotlight(r.d.name); tip.show(event.pageX, event.pageY, body) })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', function () { if (!pinned) clearSpotlight(); tip.hide() })
    hit.on('click', function (event) {
      event.stopPropagation()
      if (pinned === r.d.name) { pinned = null; clearSpotlight() }
      else { pinned = r.d.name; spotlight(r.d.name); tip.show(event.pageX, event.pageY, body) }
    })
  }
  svg.on('click', () => { if (pinned) { pinned = null; clearSpotlight() } })
}

// --------------------------------------------------------- histogram
export function renderHistogramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Synthetic skewed distribution of response times (seconds)
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(13)
  const samples = []
  for (let i = 0; i < 500; i++) {
    const u = (rng() + rng() + rng()) / 3
    samples.push(Math.exp(u * 1.5) * 0.9)
  }

  // Interactive slider (omitted in static mode — caller wants chart only)
  const host = d3.select(container)
  let slider = null
  if (interactive) {
    slider = host.append('div').attr('class', 'demo-slider')
    slider.html(`
      <label for="hist-bins">bin count</label>
      <input id="hist-bins" type="range" min="6" max="60" value="24" step="1" />
      <span class="val">24</span>
      <span class="hint">drag to see how bin choice shapes what you see</span>
    `)
  }
  const chartEl = host.append('div').node()

  function draw(binCount) {
    d3.select(chartEl).selectAll('*').remove()
    const W = 620, H = 240
    const margin = { top: 14, right: 20, bottom: 32, left: 44 }
    const svg = d3.select(chartEl).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

    const x = d3.scaleLinear().domain([0, d3.max(samples)]).nice()
      .range([margin.left, W - margin.right])
    const bins = d3.bin().domain(x.domain()).thresholds(binCount)(samples)
    const y = d3.scaleLinear().domain([0, d3.max(bins, b => b.length)]).nice()
      .range([H - margin.bottom, margin.top])

    svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(6))
      .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
    svg.append('g').attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).ticks(4))
      .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

    svg.append('g').selectAll('rect').data(bins).join('rect')
      .attr('x', d => x(d.x0) + 1)
      .attr('y', d => y(d.length))
      .attr('width', d => Math.max(0, x(d.x1) - x(d.x0) - 1))
      .attr('height', d => H - margin.bottom - y(d.length))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.75)

    svg.append('text').attr('x', W - margin.right).attr('y', margin.top - 2)
      .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10)
      .text('response time (s) →')
    svg.append('text').attr('x', margin.left).attr('y', margin.top - 2)
      .attr('fill', COLORS.label).attr('font-size', 10)
      .text(`n = ${samples.length}`)
  }

  if (interactive) {
    const input = slider.select('input').node()
    const val = slider.select('.val').node()
    input.addEventListener('input', () => {
      const v = +input.value
      val.textContent = v
      draw(v)
    })
  }
  draw(24)
}

// --------------------------------------------------------- treemap
export function renderTreemapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // US federal budget — now actually hierarchical (two levels beneath Budget)
  // so zoom-to-subtree has something to do.
  const root = {
    name: 'Budget',
    children: [
      { name: 'Mandatory', children: [
        { name: 'Social Security', value: 1350 },
        { name: 'Medicare',        value:  980 },
        { name: 'Medicaid',        value:  580 },
        { name: 'Income Sec.',     value:  650 },
        { name: 'Veterans',        value:  270 },
      ] },
      { name: 'Discretionary', children: [
        { name: 'Defense',        value: 820 },
        { name: 'Education',      value: 150 },
        { name: 'Transportation', value: 130 },
        { name: 'Other',          value: 340 },
      ] },
      { name: 'Interest', value: 620 },
    ],
  }
  const W = 620, H = 340
  const HEADER = 30
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const topLevel = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value)
  const topPalette = d3.scaleOrdinal()
    .domain(topLevel.children.map(c => c.data.name))
    .range([COLORS.accent, COLORS.warm, COLORS.good])
  // Leaf palette — so leaves still have color identity at focus level
  const leafPalette = d3.scaleOrdinal()
    .domain(topLevel.leaves().map(d => d.data.name))
    .range([COLORS.accent, COLORS.good, COLORS.warm, COLORS.purple, COLORS.green,
            COLORS.danger, COLORS.mute, '#94a3b8', '#fbbf24', '#60a5fa'])

  const breadcrumb = svg.append('g').attr('class', 'tm-breadcrumb')
  const cellsG = svg.append('g').attr('class', 'tm-cells')
  let focus = topLevel

  function render() {
    cellsG.selectAll('*').remove()
    breadcrumb.selectAll('*').remove()

    // Re-layout on the focused subtree so it fills the viewport.
    const sub = focus.copy().sum(d => d.value).sort((a, b) => b.value - a.value)
    d3.treemap().size([W, H - HEADER]).padding(2).round(true)(sub)

    // Render only the *immediate* children of the focus — this is the
    // classic zoomable treemap: root shows 3 big groups; click one → see
    // its 5 children; click breadcrumb → back. Avoids rendering every
    // leaf on top of every parent overlay and the label-collision mess.
    const kids = sub.children || [sub]
    for (const c of kids) {
      const isGroup = !!c.children
      const isDrillable = interactive && isGroup
      const color = isGroup ? topPalette(c.data.name) : leafPalette(c.data.name)
      const g = cellsG.append('g')
        .style('cursor', isDrillable ? 'pointer' : 'default')
      g.append('rect')
        .attr('x', c.x0).attr('y', HEADER + c.y0)
        .attr('width', c.x1 - c.x0).attr('height', c.y1 - c.y0)
        .attr('fill', color).attr('fill-opacity', 0.8)
        .attr('stroke', '#0a0a0a').attr('stroke-width', 1)

      const w = c.x1 - c.x0, h = c.y1 - c.y0
      if (w > 70 && h > 22) {
        g.append('text').attr('x', c.x0 + 8).attr('y', HEADER + c.y0 + 16)
          .attr('fill', '#0a0a0a').attr('font-size', 11.5).attr('font-weight', 700)
          .text(c.data.name + (isDrillable ? '  ↓' : ''))
        if (h > 36) {
          g.append('text').attr('x', c.x0 + 8).attr('y', HEADER + c.y0 + 30)
            .attr('fill', '#0a0a0a').attr('font-size', 10).attr('fill-opacity', 0.7)
            .text('$' + c.value + 'B')
        }
      }
      if (isDrillable) {
        g.on('click', (event) => {
          event.stopPropagation()
          const target = topLevel.descendants().find(d => d.data === c.data)
          if (target) { focus = target; render() }
        })
      }
    }

    // Breadcrumb
    breadcrumb.append('rect').attr('x', 0).attr('y', 0).attr('width', W).attr('height', HEADER)
      .attr('fill', '#0a0a0a').attr('stroke', '#1f1f1f').attr('stroke-width', 0.5)
    const path = focus.ancestors().reverse()
    let cursor = 10
    path.forEach((node, i) => {
      if (i > 0) {
        breadcrumb.append('text').attr('x', cursor).attr('y', 19)
          .attr('fill', '#525252').attr('font-size', 11).text('›')
        cursor += 12
      }
      const isLast = i === path.length - 1
      const text = breadcrumb.append('text').attr('x', cursor).attr('y', 19)
        .attr('fill', isLast ? '#e5e5e5' : '#c7d2fe').attr('font-size', 11)
        .attr('font-weight', isLast ? 600 : 400)
        .text(node.data.name + (node.value != null ? ` · $${node.value}B` : ''))
      if (interactive && !isLast) {
        text.style('cursor', 'pointer')
          .on('click', (event) => { event.stopPropagation(); focus = node; render() })
      }
      cursor += text.node().getComputedTextLength() + 6
    })
    // Hint on the right side of the header
    if (interactive) {
      breadcrumb.append('text').attr('x', W - 10).attr('y', 19)
        .attr('text-anchor', 'end').attr('fill', '#737373').attr('font-size', 9)
        .attr('font-style', 'italic')
        .text(focus.depth === 0
          ? 'click a parent block to zoom in'
          : 'click breadcrumb or outside to zoom out')
    }
  }

  if (interactive) {
    // Click empty space to zoom out one level (unless already at root)
    svg.on('click', () => {
      if (focus.parent) { focus = focus.parent; render() }
    })
  }
  render()
}

// --------------------------------------------------------- diverging-bar
export function renderDivergingBarDemo(container) {
  // Likert-scale survey results across several questions
  const items = [
    { q: 'Clear communication',   sd:  5, d: 10, n: 15, a: 45, sa: 25 },
    { q: 'Good work-life balance',sd: 15, d: 22, n: 20, a: 28, sa: 15 },
    { q: 'Useful tools',           sd:  8, d: 12, n: 18, a: 42, sa: 20 },
    { q: 'Fair compensation',      sd: 20, d: 18, n: 22, a: 28, sa: 12 },
    { q: 'Career growth',          sd: 12, d: 15, n: 30, a: 30, sa: 13 },
    { q: 'Leadership effective',   sd: 18, d: 20, n: 25, a: 25, sa: 12 },
  ]
  const W = 620, H = 260
  const margin = { top: 24, right: 30, bottom: 16, left: 170 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // Each item's "zero" (baseline between neutral and disagree-sides)
  // centers neutral on the axis.
  const y = d3.scaleBand().domain(items.map(d => d.q))
    .range([margin.top, H - margin.bottom]).padding(0.25)
  const maxSide = 60
  const x = d3.scaleLinear().domain([-maxSide, maxSide])
    .range([margin.left, W - margin.right])
  const axisX = (W + margin.left - margin.right) / 2

  // Central axis line
  svg.append('line')
    .attr('x1', x(0)).attr('x2', x(0))
    .attr('y1', margin.top).attr('y2', H - margin.bottom)
    .attr('stroke', COLORS.grid).attr('stroke-dasharray', '2 3')

  const c = { sd: '#7f1d1d', d: '#f87171', n: '#3f3f3f', a: '#60a5fa', sa: '#1e40af' }

  for (const r of items) {
    const yy = y(r.q), h = y.bandwidth()
    // Left side: neutral-half, disagree, strongly-disagree
    let cur = x(0) - (x(r.n / 2) - x(0))
    // neutral straddles zero: half on each side
    svg.append('rect').attr('x', cur).attr('y', yy)
      .attr('width', x(r.n / 2) - x(0)).attr('height', h).attr('fill', c.n)
    cur -= (x(r.d) - x(0))
    svg.append('rect').attr('x', cur).attr('y', yy)
      .attr('width', x(r.d) - x(0)).attr('height', h).attr('fill', c.d)
    cur -= (x(r.sd) - x(0))
    svg.append('rect').attr('x', cur).attr('y', yy)
      .attr('width', x(r.sd) - x(0)).attr('height', h).attr('fill', c.sd)
    // Right side: neutral-half, agree, strongly-agree
    cur = x(0) + (0)
    // skip the left neutral half already drawn; render the right half:
    svg.append('rect').attr('x', x(0)).attr('y', yy)
      .attr('width', x(r.n / 2) - x(0)).attr('height', h).attr('fill', c.n)
    cur = x(0) + (x(r.n / 2) - x(0))
    svg.append('rect').attr('x', cur).attr('y', yy)
      .attr('width', x(r.a) - x(0)).attr('height', h).attr('fill', c.a)
    cur += (x(r.a) - x(0))
    svg.append('rect').attr('x', cur).attr('y', yy)
      .attr('width', x(r.sa) - x(0)).attr('height', h).attr('fill', c.sa)

    svg.append('text')
      .attr('x', margin.left - 10).attr('y', yy + h / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11)
      .text(r.q)
  }

  // Legend
  const lgItems = [
    { label: 'Strongly disagree', color: c.sd },
    { label: 'Disagree',          color: c.d },
    { label: 'Neutral',           color: c.n },
    { label: 'Agree',             color: c.a },
    { label: 'Strongly agree',    color: c.sa },
  ]
  let lx = margin.left
  for (const l of lgItems) {
    svg.append('rect').attr('x', lx).attr('y', 6).attr('width', 10).attr('height', 10).attr('fill', l.color)
    svg.append('text').attr('x', lx + 14).attr('y', 15)
      .attr('fill', COLORS.label).attr('font-size', 10).text(l.label)
    lx += l.label.length * 6 + 30
  }
}

// --------------------------------------------------------- parallel-sets
export function renderParallelSetsDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // 1000 survey respondents crossed by lean × news source × trust
  const axes = [
    { key: 'lean',  label: 'Lean',       values: ['Left', 'Center', 'Right'] },
    { key: 'media', label: 'News source',values: ['Paper', 'TV', 'Social'] },
    { key: 'trust', label: 'Trust gov.', values: ['High', 'Mixed', 'Low'] },
  ]
  const rows = [
    { lean:'Left',   media:'Paper',  trust:'High',  n: 70 },
    { lean:'Left',   media:'Paper',  trust:'Mixed', n: 50 },
    { lean:'Left',   media:'Paper',  trust:'Low',   n: 10 },
    { lean:'Left',   media:'TV',     trust:'High',  n: 40 },
    { lean:'Left',   media:'TV',     trust:'Mixed', n: 60 },
    { lean:'Left',   media:'TV',     trust:'Low',   n: 30 },
    { lean:'Left',   media:'Social', trust:'High',  n: 20 },
    { lean:'Left',   media:'Social', trust:'Mixed', n: 50 },
    { lean:'Left',   media:'Social', trust:'Low',   n: 70 },
    { lean:'Center', media:'Paper',  trust:'High',  n: 30 },
    { lean:'Center', media:'Paper',  trust:'Mixed', n: 25 },
    { lean:'Center', media:'Paper',  trust:'Low',   n: 10 },
    { lean:'Center', media:'TV',     trust:'High',  n: 35 },
    { lean:'Center', media:'TV',     trust:'Mixed', n: 45 },
    { lean:'Center', media:'TV',     trust:'Low',   n: 30 },
    { lean:'Center', media:'Social', trust:'High',  n: 10 },
    { lean:'Center', media:'Social', trust:'Mixed', n: 25 },
    { lean:'Center', media:'Social', trust:'Low',   n: 40 },
    { lean:'Right',  media:'Paper',  trust:'High',  n: 30 },
    { lean:'Right',  media:'Paper',  trust:'Mixed', n: 30 },
    { lean:'Right',  media:'Paper',  trust:'Low',   n: 15 },
    { lean:'Right',  media:'TV',     trust:'High',  n: 60 },
    { lean:'Right',  media:'TV',     trust:'Mixed', n: 55 },
    { lean:'Right',  media:'TV',     trust:'Low',   n: 35 },
    { lean:'Right',  media:'Social', trust:'High',  n: 15 },
    { lean:'Right',  media:'Social', trust:'Mixed', n: 35 },
    { lean:'Right',  media:'Social', trust:'Low',   n: 75 },
  ]
  const total = 1000
  const W = 620, H = 360
  const margin = { top: 90, right: 70, bottom: 18, left: 70 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // DECODER STRIP — axis-is-editorial is the key insight for parallel sets
  const dy = 8, dH = 58
  svg.append('rect').attr('x', margin.left).attr('y', dy)
    .attr('width', W - margin.left - margin.right).attr('height', dH)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', margin.left + 8).attr('y', dy + 11)
    .attr('fill', '#93c5fd').attr('font-size', 8).attr('letter-spacing', '0.1em').text('DECODER')

  // Mini two-axis parallel-set: left stack + right stack + 2 ribbons
  const miniX0 = margin.left + 80, miniX1 = margin.left + 180
  const stackY = dy + 18, stackH = 32
  // left stack: 60/40 split
  svg.append('rect').attr('x', miniX0 - 6).attr('y', stackY)
    .attr('width', 6).attr('height', stackH * 0.6).attr('fill', COLORS.accent).attr('fill-opacity', 0.9)
  svg.append('rect').attr('x', miniX0 - 6).attr('y', stackY + stackH * 0.6)
    .attr('width', 6).attr('height', stackH * 0.4).attr('fill', COLORS.purple).attr('fill-opacity', 0.9)
  // right stack: 35/65 split
  svg.append('rect').attr('x', miniX1).attr('y', stackY)
    .attr('width', 6).attr('height', stackH * 0.35).attr('fill', COLORS.green).attr('fill-opacity', 0.9)
  svg.append('rect').attr('x', miniX1).attr('y', stackY + stackH * 0.35)
    .attr('width', 6).attr('height', stackH * 0.65).attr('fill', COLORS.warm).attr('fill-opacity', 0.9)
  // ribbons
  function miniRibbon(y0, h0, y1, h1, color) {
    const cx = (miniX0 + miniX1) / 2
    const d = `M ${miniX0} ${y0} C ${cx} ${y0}, ${cx} ${y1}, ${miniX1} ${y1} ` +
              `L ${miniX1} ${y1 + h1} C ${cx} ${y1 + h1}, ${cx} ${y0 + h0}, ${miniX0} ${y0 + h0} Z`
    svg.append('path').attr('d', d).attr('fill', color).attr('fill-opacity', 0.3)
  }
  // thicker ribbon (the "dominant" pairing)
  miniRibbon(stackY, stackH * 0.4, stackY + stackH * 0.35, stackH * 0.55, COLORS.accent)
  // thinner ribbon
  miniRibbon(stackY + stackH * 0.4, stackH * 0.2, stackY, stackH * 0.35, COLORS.accent)
  // Labels
  svg.append('text').attr('x', miniX0 - 10).attr('y', stackY + stackH + 11)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 9).text('axis = count')
  svg.append('text').attr('x', miniX1 + 12).attr('y', stackY + stackH + 11)
    .attr('fill', COLORS.label).attr('font-size', 9).text('by category')
  svg.append('text').attr('x', (miniX0 + miniX1) / 2).attr('y', stackY - 5)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
    .text('thickness = subset count')
  // Warning callout — axis order is editorial
  svg.append('text').attr('x', margin.left + 230).attr('y', dy + 22)
    .attr('fill', COLORS.warm).attr('font-size', 9).attr('font-weight', 600)
    .text('within-axis order is editorial —')
  svg.append('text').attr('x', margin.left + 230).attr('y', dy + 36)
    .attr('fill', COLORS.warm).attr('font-size', 9)
    .text('alphabetical is almost never right; pick the order that')
  svg.append('text').attr('x', margin.left + 230).attr('y', dy + 48)
    .attr('fill', COLORS.warm).attr('font-size', 9)
    .text('makes the dominant pairing read as a diagonal')

  const xAxis = d3.scalePoint().domain(axes.map(a => a.key))
    .range([margin.left, W - margin.right])

  function axisPositions(axisKey) {
    const byValue = new Map()
    for (const r of rows) byValue.set(r[axisKey], (byValue.get(r[axisKey]) || 0) + r.n)
    const vals = axes.find(a => a.key === axisKey).values
    const usable = H - margin.top - margin.bottom - 6 * (vals.length - 1)
    let acc = margin.top
    const pos = new Map()
    for (const v of vals) {
      const h = (byValue.get(v) || 0) / total * usable
      pos.set(v, { y0: acc, y1: acc + h, h })
      acc += h + 6
    }
    return pos
  }
  const positions = Object.fromEntries(axes.map(a => [a.key, axisPositions(a.key)]))
  const schemes = {
    lean:  { Left: COLORS.accent, Center: '#8b8b8b', Right: COLORS.danger },
    media: { Paper: COLORS.green, TV: COLORS.warm, Social: COLORS.purple },
    trust: { High: COLORS.good, Mixed: '#8b8b8b', Low: COLORS.danger },
  }

  // Axis nodes (stack segments) — keep refs for interactive click-to-isolate
  const segRefs = []
  for (const a of axes) {
    const x = xAxis(a.key), pos = positions[a.key]
    svg.append('text').attr('x', x).attr('y', margin.top - 10)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 11)
      .attr('font-weight', 500).text(a.label)
    for (const v of a.values) {
      const p = pos.get(v)
      const rect = svg.append('rect').attr('class', 'ps-segment')
        .attr('data-axis', a.key).attr('data-value', v)
        .attr('x', x - 8).attr('y', p.y0)
        .attr('width', 16).attr('height', p.h).attr('fill', schemes[a.key][v])
        .attr('fill-opacity', 0.9)
      const idx = axes.findIndex(aa => aa.key === a.key)
      const isFirst = idx === 0, isLast = idx === axes.length - 1
      const lx = isFirst ? x - 14 : (isLast ? x + 14 : x + 14)
      const anc = isFirst ? 'end' : 'start'
      svg.append('text').attr('x', lx).attr('y', (p.y0 + p.y1) / 2 + 4)
        .attr('text-anchor', anc).attr('fill', COLORS.text).attr('pointer-events', 'none')
        .attr('font-size', 10).text(v)
      segRefs.push({ axis: a.key, value: v, rect })
    }
  }

  // Ribbons per adjacent pair — store refs so interactive mode can dim
  const ribbonRefs = []
  for (let i = 0; i < axes.length - 1; i++) {
    const L = axes[i], R = axes[i + 1]
    const lpos = positions[L.key], rpos = positions[R.key]
    const x0 = xAxis(L.key) + 8, x1 = xAxis(R.key) - 8
    const pair = new Map()
    for (const r of rows) {
      const k = `${r[L.key]}||${r[R.key]}`
      pair.set(k, (pair.get(k) || 0) + r.n)
    }
    const lOff = new Map(L.values.map(v => [v, lpos.get(v).y0]))
    const rOff = new Map(R.values.map(v => [v, rpos.get(v).y0]))
    for (const lv of L.values) {
      for (const rv of R.values) {
        const n = pair.get(`${lv}||${rv}`) || 0
        if (!n) continue
        const hL = n / total * (H - margin.top - margin.bottom - 6 * (L.values.length - 1))
        const hR = n / total * (H - margin.top - margin.bottom - 6 * (R.values.length - 1))
        const y0 = lOff.get(lv), y1 = rOff.get(rv)
        lOff.set(lv, y0 + hL); rOff.set(rv, y1 + hR)
        const cx = (x0 + x1) / 2
        const d = `M ${x0} ${y0} C ${cx} ${y0}, ${cx} ${y1}, ${x1} ${y1} ` +
                  `L ${x1} ${y1 + hR} C ${cx} ${y1 + hR}, ${cx} ${y0 + hL}, ${x0} ${y0 + hL} Z`
        const path = svg.append('path').attr('class', 'ps-ribbon').attr('d', d)
          .attr('fill', schemes[L.key][lv]).attr('fill-opacity', 0.28)
          .attr('stroke', 'none')
        ribbonRefs.push({ lKey: L.key, lv, rKey: R.key, rv, n, path })
      }
    }
  }

  if (!interactive) return

  // INTERACTIVE (P10: click an axis segment to isolate ribbons that touch
  // it — same dim-don't-hide pattern as sankey; reveals what flows through
  // a given category)
  const tip = createTooltip(container, { className: 'ps-tip' })
  let selected = null  // { axis, value }
  function isRibbonOn(r, sel) {
    if (!sel) return true
    return (r.lKey === sel.axis && r.lv === sel.value)
        || (r.rKey === sel.axis && r.rv === sel.value)
  }
  function applySelection() {
    for (const r of ribbonRefs) {
      r.path.attr('fill-opacity', selected == null ? 0.28 : (isRibbonOn(r, selected) ? 0.6 : 0.04))
    }
    for (const s of segRefs) {
      const isSel = selected && s.axis === selected.axis && s.value === selected.value
      s.rect.attr('stroke', isSel ? '#f5f5f5' : 'none').attr('stroke-width', isSel ? 1.5 : 0)
        .attr('fill-opacity', selected && !isSel ? 0.35 : 0.9)
    }
  }
  function clear() { selected = null; applySelection(); tip.hide() }
  for (const s of segRefs) {
    // Compute total for this segment's value (sum across rows)
    const segTotal = rows.filter(r => r[s.axis] === s.value).reduce((a, b) => a + b.n, 0)
    const axisLabel = axes.find(a => a.key === s.axis).label
    const body = `<strong>${axisLabel}: ${s.value}</strong><br>` +
      `<span style="color:#a3a3a3">respondents:</span> <strong>${segTotal}</strong>`
    s.rect.style('cursor', 'pointer')
      .on('click', function (event) {
        event.stopPropagation()
        if (selected && selected.axis === s.axis && selected.value === s.value) {
          clear()
        } else {
          selected = { axis: s.axis, value: s.value }
          applySelection()
          tip.show(event.pageX, event.pageY, body)
        }
      })
      .on('mouseenter', function (event) {
        if (!selected) tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) {
        if (!selected) tip.show(event.pageX, event.pageY, body)
      })
      .on('mouseleave', () => { if (!selected) tip.hide() })
  }
  svg.on('click', () => { if (selected) clear() })

  // Affordance hint
  svg.append('text').attr('x', margin.left).attr('y', H - 4)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('font-style', 'italic')
    .text('click an axis segment to isolate its ribbons')
}

// --------------------------------------------------------- boxplot
export function renderBoxplotDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // 6 groups of synthetic sample data
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(19)
  const groups = [
    { name: 'A', mean: 60, sd: 12 },
    { name: 'B', mean: 72, sd:  9 },
    { name: 'C', mean: 55, sd: 18 },
    { name: 'D', mean: 78, sd: 14 },
    { name: 'E', mean: 65, sd: 10 },
    { name: 'F', mean: 83, sd: 15 },
  ]
  function sampleNormal(mean, sd, n = 80) {
    const out = []
    for (let i = 0; i < n; i++) {
      const z = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
      out.push(mean + sd * z)
    }
    return out
  }
  const data = groups.map(g => ({ ...g, values: sampleNormal(g.mean, g.sd).sort(d3.ascending) }))
  function quantiles(xs) {
    return {
      q1: d3.quantile(xs, 0.25),
      med: d3.quantile(xs, 0.5),
      q3: d3.quantile(xs, 0.75),
      min: xs[0], max: xs[xs.length - 1],
    }
  }
  for (const d of data) {
    d.q = quantiles(d.values)
    const iqr = d.q.q3 - d.q.q1
    d.lo = Math.max(d.q.min, d.q.q1 - 1.5 * iqr)
    d.hi = Math.min(d.q.max, d.q.q3 + 1.5 * iqr)
    d.outliers = d.values.filter(v => v < d.lo || v > d.hi)
  }

  const W = 620, H = 310
  const margin = { top: 48, right: 20, bottom: 32, left: 44 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const x = d3.scaleBand().domain(data.map(d => d.name))
    .range([margin.left, W - margin.right]).padding(0.35)
  const y = d3.scaleLinear().domain([20, 130]).range([H - margin.bottom, margin.top])

  // Horizontal decoder strip at the top
  const dy = 8
  svg.append('rect').attr('x', margin.left).attr('y', dy).attr('width', W - margin.left - margin.right).attr('height', 30)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', margin.left + 8).attr('y', dy + 11)
    .attr('fill', '#93c5fd').attr('font-size', 8).attr('letter-spacing', '0.1em').text('DECODER')
  // Inline exemplar: |──── [Q1-Q3 box] ──── |  with median and outlier to the right
  const strX = margin.left + 60
  // Whiskers
  svg.append('line').attr('x1', strX).attr('x2', strX + 70).attr('y1', dy + 22).attr('y2', dy + 22).attr('stroke', COLORS.text).attr('stroke-width', 0.8)
  svg.append('line').attr('x1', strX).attr('x2', strX).attr('y1', dy + 18).attr('y2', dy + 26).attr('stroke', COLORS.text)
  svg.append('line').attr('x1', strX + 70).attr('x2', strX + 70).attr('y1', dy + 18).attr('y2', dy + 26).attr('stroke', COLORS.text)
  // Box
  svg.append('rect').attr('x', strX + 18).attr('y', dy + 16).attr('width', 34).attr('height', 12)
    .attr('fill', COLORS.accent).attr('fill-opacity', 0.35).attr('stroke', COLORS.accent).attr('stroke-width', 1)
  // Median
  svg.append('line').attr('x1', strX + 33).attr('x2', strX + 33).attr('y1', dy + 16).attr('y2', dy + 28).attr('stroke', '#f5f5f5').attr('stroke-width', 1.5)
  // Labels
  svg.append('text').attr('x', strX - 4).attr('y', dy + 24).attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 9).text('min')
  svg.append('text').attr('x', strX + 74).attr('y', dy + 24).attr('fill', COLORS.label).attr('font-size', 9).text('max')
  svg.append('text').attr('x', strX + 35).attr('y', dy + 12).attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9).text('Q1–Q3')
  svg.append('text').attr('x', strX + 33).attr('y', dy + 42).attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 8.5).text('median')
  // Outlier example
  svg.append('circle').attr('cx', strX + 130).attr('cy', dy + 22).attr('r', 2.5).attr('fill', COLORS.danger).attr('fill-opacity', 0.8)
  svg.append('text').attr('x', strX + 136).attr('y', dy + 24).attr('fill', COLORS.label).attr('font-size', 9).text('outlier (>1.5×IQR)')

  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(6))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  const groupRefs = []
  for (const d of data) {
    const cx = x(d.name) + x.bandwidth() / 2
    const g = svg.append('g').attr('class', 'bp-group').attr('data-name', d.name)
    g.append('line').attr('x1', cx).attr('x2', cx)
      .attr('y1', y(d.lo)).attr('y2', y(d.hi))
      .attr('stroke', COLORS.text).attr('stroke-width', 1)
    g.append('line').attr('x1', cx - 8).attr('x2', cx + 8)
      .attr('y1', y(d.lo)).attr('y2', y(d.lo)).attr('stroke', COLORS.text)
    g.append('line').attr('x1', cx - 8).attr('x2', cx + 8)
      .attr('y1', y(d.hi)).attr('y2', y(d.hi)).attr('stroke', COLORS.text)
    const box = g.append('rect')
      .attr('x', x(d.name)).attr('y', y(d.q.q3))
      .attr('width', x.bandwidth()).attr('height', y(d.q.q1) - y(d.q.q3))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.35)
      .attr('stroke', COLORS.accent).attr('stroke-width', 1.2)
    g.append('line')
      .attr('x1', x(d.name)).attr('x2', x(d.name) + x.bandwidth())
      .attr('y1', y(d.q.med)).attr('y2', y(d.q.med))
      .attr('stroke', COLORS.ink || '#f5f5f5').attr('stroke-width', 2)
    for (const o of d.outliers) {
      g.append('circle').attr('cx', cx).attr('cy', y(o))
        .attr('r', 2.2).attr('fill', COLORS.danger).attr('fill-opacity', 0.75)
    }
    svg.append('text').attr('x', cx).attr('y', H - margin.bottom + 16)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label)
      .attr('font-size', 11).text(d.name)
    groupRefs.push({ d, box, g, cx })
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals group's Q1/median/Q3/IQR/N)
  const tip = createTooltip(container, { className: 'bp-tip' })
  // Transparent overlay per column so the whole group area responds,
  // not just pixels inside the box itself.
  for (const ref of groupRefs) {
    const hitX = x(ref.d.name)
    const hit = svg.append('rect').attr('class', 'bp-hit').attr('data-name', ref.d.name)
      .attr('x', hitX).attr('y', margin.top)
      .attr('width', x.bandwidth())
      .attr('height', H - margin.bottom - margin.top)
      .attr('fill', 'transparent').style('cursor', 'pointer')
    const iqr = ref.d.q.q3 - ref.d.q.q1
    const body = `<strong>Group ${ref.d.name}</strong> <span style="color:#737373">n=${ref.d.values.length}</span><br>` +
      `<span style="color:#a3a3a3">median:</span> <strong>${ref.d.q.med.toFixed(1)}</strong><br>` +
      `<span style="color:#a3a3a3">Q1–Q3:</span> ${ref.d.q.q1.toFixed(1)}–${ref.d.q.q3.toFixed(1)} ` +
      `<span style="color:#737373">(IQR ${iqr.toFixed(1)})</span><br>` +
      `<span style="color:#a3a3a3">whiskers:</span> ${ref.d.lo.toFixed(1)}–${ref.d.hi.toFixed(1)}` +
      (ref.d.outliers.length ? `<br><span style="color:#f87171">outliers:</span> ${ref.d.outliers.length}` : '')
    hit.on('mouseenter', function (event) {
      ref.box.attr('fill-opacity', 0.55).attr('stroke-width', 1.8)
      tip.show(event.pageX, event.pageY, body)
    })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', () => {
      ref.box.attr('fill-opacity', 0.35).attr('stroke-width', 1.2)
      tip.hide()
    })
    hit.on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- violin
export function renderViolinDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Same data idea as boxplot but showing density shape
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(23)
  const groups = [
    // Bimodal!
    { name: 'A', samples: [], modes: [[55, 8], [85, 6]], n: 120 },
    { name: 'B', samples: [], modes: [[72, 10]], n: 120 },
    { name: 'C', samples: [], modes: [[55, 18]], n: 120 },
    { name: 'D', samples: [], modes: [[78, 12]], n: 120 },
    // Bimodal
    { name: 'E', samples: [], modes: [[48, 8], [75, 6]], n: 120 },
    { name: 'F', samples: [], modes: [[83, 12]], n: 120 },
  ]
  function sampleNormal(m, sd) {
    const z = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
    return m + sd * z
  }
  for (const g of groups) {
    for (let i = 0; i < g.n; i++) {
      const [m, sd] = g.modes[Math.floor(rng() * g.modes.length)]
      g.samples.push(sampleNormal(m, sd))
    }
    g.samples.sort(d3.ascending)
  }

  const W = 620, H = 340
  const margin = { top: 58, right: 20, bottom: 52, left: 44 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const x = d3.scaleBand().domain(groups.map(g => g.name))
    .range([margin.left, W - margin.right]).padding(0.3)
  const y = d3.scaleLinear().domain([20, 110]).range([H - margin.bottom, margin.top])

  // DECODER STRIP — bimodal vs unimodal is the thing a violin buys you over a boxplot
  const dy = 8, dH = 40
  svg.append('rect').attr('x', margin.left).attr('y', dy)
    .attr('width', W - margin.left - margin.right).attr('height', dH)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', margin.left + 8).attr('y', dy + 11)
    .attr('fill', '#93c5fd').attr('font-size', 8).attr('letter-spacing', '0.1em').text('DECODER')

  // Mini violin shape generator (symmetric KDE blob)
  function miniViolin(cx, cy, modes) {
    const g = svg.append('g')
    const pts = d3.range(-14, 14.5, 1).map(v => {
      let w = 0
      for (const [m, s] of modes) w += Math.exp(-0.5 * ((v - m) / s) ** 2)
      return { v, w }
    })
    const maxW = d3.max(pts, p => p.w)
    const W2 = 9
    const pathR = d3.area().curve(d3.curveBasis)
      .y(p => cy + p.v).x0(cx).x1(p => cx + (p.w / maxW) * W2)
    const pathL = d3.area().curve(d3.curveBasis)
      .y(p => cy + p.v).x0(cx).x1(p => cx - (p.w / maxW) * W2)
    g.append('path').datum(pts).attr('d', pathR).attr('fill', COLORS.purple).attr('fill-opacity', 0.45)
    g.append('path').datum(pts).attr('d', pathL).attr('fill', COLORS.purple).attr('fill-opacity', 0.45)
  }
  function miniBimodalViolin(cx, cy) {
    const g = svg.append('g')
    const pts = d3.range(-14, 14.5, 1).map(v => {
      const w = Math.exp(-0.5 * ((v + 7) / 3.2) ** 2) + Math.exp(-0.5 * ((v - 7) / 3.2) ** 2)
      return { v, w }
    })
    const maxW = d3.max(pts, p => p.w)
    const W2 = 9
    const pathR = d3.area().curve(d3.curveBasis)
      .y(p => cy + p.v).x0(cx).x1(p => cx + (p.w / maxW) * W2)
    const pathL = d3.area().curve(d3.curveBasis)
      .y(p => cy + p.v).x0(cx).x1(p => cx - (p.w / maxW) * W2)
    g.append('path').datum(pts).attr('d', pathR).attr('fill', COLORS.good).attr('fill-opacity', 0.5)
    g.append('path').datum(pts).attr('d', pathL).attr('fill', COLORS.good).attr('fill-opacity', 0.5)
  }
  // unimodal example
  miniViolin(margin.left + 80, dy + dH / 2 + 1, [[0, 5]])
  svg.append('text').attr('x', margin.left + 96).attr('y', dy + dH / 2 - 2)
    .attr('fill', COLORS.label).attr('font-size', 9).text('unimodal')
  svg.append('text').attr('x', margin.left + 96).attr('y', dy + dH / 2 + 10)
    .attr('fill', '#6b7280').attr('font-size', 8).text('(a boxplot shows this fine)')
  // bimodal example
  miniBimodalViolin(margin.left + 230, dy + dH / 2 + 1)
  svg.append('text').attr('x', margin.left + 246).attr('y', dy + dH / 2 - 2)
    .attr('fill', COLORS.good).attr('font-size', 9).attr('font-weight', 600).text('bimodal')
  svg.append('text').attr('x', margin.left + 246).attr('y', dy + dH / 2 + 10)
    .attr('fill', '#6b7280').attr('font-size', 8).text('(a boxplot would hide this)')
  // median line
  const mx = margin.left + 400
  svg.append('line').attr('x1', mx - 8).attr('x2', mx + 8)
    .attr('y1', dy + dH / 2).attr('y2', dy + dH / 2)
    .attr('stroke', COLORS.text).attr('stroke-width', 1.4)
  svg.append('text').attr('x', mx + 14).attr('y', dy + dH / 2 + 3)
    .attr('fill', COLORS.label).attr('font-size', 9).text('median')
  // width encoding
  svg.append('text').attr('x', mx + 70).attr('y', dy + dH / 2 + 3)
    .attr('fill', COLORS.label).attr('font-size', 9).text('width = density')

  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  // Simple kernel density estimator
  function kde(samples, bandwidth, gridY) {
    const h = bandwidth
    return gridY.map(yi => {
      let s = 0
      for (const v of samples) {
        const u = (yi - v) / h
        s += Math.exp(-0.5 * u * u)
      }
      return s / (samples.length * h * Math.sqrt(2 * Math.PI))
    })
  }
  const gridY = d3.range(20, 110, 1)
  const densities = groups.map(g => kde(g.samples, 4.5, gridY))
  const maxD = d3.max(densities.flat())

  const violinRefs = []
  for (let gi = 0; gi < groups.length; gi++) {
    const g = groups[gi]
    const cx = x(g.name) + x.bandwidth() / 2
    const halfW = x.bandwidth() / 2
    const wScale = d3.scaleLinear().domain([0, maxD]).range([0, halfW])
    const pts = densities[gi].map((d, i) => ({ y: gridY[i], w: wScale(d) }))
    const areaR = d3.area().curve(d3.curveMonotoneY)
      .y(d => y(d.y)).x0(cx).x1(d => cx + d.w)
    const areaL = d3.area().curve(d3.curveMonotoneY)
      .y(d => y(d.y)).x0(cx).x1(d => cx - d.w)
    const isBimodal = g.modes.length > 1
    const fillC = isBimodal ? COLORS.good : COLORS.purple
    const pathR = svg.append('path').datum(pts).attr('d', areaR)
      .attr('fill', fillC).attr('fill-opacity', 0.4)
    const pathL = svg.append('path').datum(pts).attr('d', areaL)
      .attr('fill', fillC).attr('fill-opacity', 0.4)
    const med = d3.quantile(g.samples, 0.5)
    svg.append('line').attr('x1', cx - halfW * 0.5).attr('x2', cx + halfW * 0.5)
      .attr('y1', y(med)).attr('y2', y(med))
      .attr('stroke', COLORS.text).attr('stroke-width', 1.4)
    svg.append('text').attr('x', cx).attr('y', H - margin.bottom + 16)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label)
      .attr('font-size', 11).text(g.name)
    if (isBimodal) {
      svg.append('text').attr('x', cx).attr('y', H - margin.bottom + 30)
        .attr('text-anchor', 'middle').attr('fill', COLORS.good)
        .attr('font-size', 9).attr('font-weight', 600).text('bimodal')
    }
    violinRefs.push({ g, cx, halfW, med, pathR, pathL, isBimodal, fillC })
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals group summary + bimodality call-out)
  const tip = createTooltip(container, { className: 'violin-tip' })
  for (const ref of violinRefs) {
    const hitX = x(ref.g.name)
    const hit = svg.append('rect').attr('class', 'violin-hit').attr('data-name', ref.g.name)
      .attr('x', hitX).attr('y', margin.top)
      .attr('width', x.bandwidth())
      .attr('height', H - margin.bottom - margin.top)
      .attr('fill', 'transparent').style('cursor', 'pointer')
    const q1 = d3.quantile(ref.g.samples, 0.25)
    const q3 = d3.quantile(ref.g.samples, 0.75)
    const body = `<strong>Group ${ref.g.name}</strong> <span style="color:#737373">n=${ref.g.samples.length}</span><br>` +
      `<span style="color:#a3a3a3">median:</span> <strong>${ref.med.toFixed(1)}</strong><br>` +
      `<span style="color:#a3a3a3">Q1–Q3:</span> ${q1.toFixed(1)}–${q3.toFixed(1)}<br>` +
      `<span style="color:${ref.isBimodal ? '#86efac' : '#a3a3a3'}">modes:</span> ` +
      `<strong>${ref.g.modes.length}</strong>${ref.isBimodal ? ' — a boxplot would hide this' : ''}`
    hit.on('mouseenter', function (event) {
      ref.pathR.attr('fill-opacity', 0.7); ref.pathL.attr('fill-opacity', 0.7)
      tip.show(event.pageX, event.pageY, body)
    })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', () => {
      ref.pathR.attr('fill-opacity', 0.4); ref.pathL.attr('fill-opacity', 0.4)
      tip.hide()
    })
    hit.on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- dot-plot
export function renderDotPlotDemo(container) {
  // Median home price by neighborhood (synthetic; 18 neighborhoods)
  const data = [
    { n: 'Oakland Hills', v: 1650 },
    { n: 'Piedmont',     v: 2420 },
    { n: 'Rockridge',    v: 1380 },
    { n: 'Temescal',     v: 1050 },
    { n: 'Berkeley Hills',v: 1720 },
    { n: 'North Berkeley',v: 1450 },
    { n: 'Downtown Oakland',v: 680 },
    { n: 'Fruitvale',    v:  620 },
    { n: 'San Leandro',  v:  810 },
    { n: 'Alameda',      v: 1180 },
    { n: 'El Cerrito',   v: 1040 },
    { n: 'Richmond',     v:  660 },
    { n: 'Albany',       v: 1290 },
    { n: 'Montclair',    v: 1580 },
    { n: 'West Oakland', v:  770 },
    { n: 'East Oakland', v:  590 },
    { n: 'Castro Valley',v: 1020 },
    { n: 'Hayward',      v:  790 },
  ].sort((a, b) => b.v - a.v)
  const W = 620, H = 380
  const margin = { top: 14, right: 50, bottom: 26, left: 130 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const y = d3.scaleBand().domain(data.map(d => d.n))
    .range([margin.top, H - margin.bottom]).padding(0.2)
  const x = d3.scaleLinear().domain([500, 2500]).range([margin.left, W - margin.right])
  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).tickFormat(d => '$' + d + 'K').ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  // Grid lines per row
  svg.append('g').selectAll('line').data(data).join('line')
    .attr('x1', margin.left).attr('x2', W - margin.right)
    .attr('y1', d => y(d.n) + y.bandwidth() / 2)
    .attr('y2', d => y(d.n) + y.bandwidth() / 2)
    .attr('stroke', COLORS.grid).attr('stroke-dasharray', '2 3')
  svg.append('g').selectAll('circle').data(data).join('circle')
    .attr('cx', d => x(d.v))
    .attr('cy', d => y(d.n) + y.bandwidth() / 2)
    .attr('r', 4.5).attr('fill', COLORS.accent)
  svg.append('g').selectAll('text.lab').data(data).join('text').attr('class', 'lab')
    .attr('x', margin.left - 8).attr('y', d => y(d.n) + y.bandwidth() / 2 + 3.5)
    .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11)
    .text(d => d.n)
}

// --------------------------------------------------------- pie-chart (antipattern lesson)
export function renderPieChartDemo(container) {
  // Show SAME data as pie + sorted bars side by side, to demonstrate the form's weakness
  const data = [
    { cat: 'Apple',    v: 28 },
    { cat: 'Samsung',  v: 22 },
    { cat: 'Xiaomi',   v: 14 },
    { cat: 'Oppo',     v: 11 },
    { cat: 'Vivo',     v:  9 },
    { cat: 'Huawei',   v:  8 },
    { cat: 'Other',    v:  8 },
  ]
  const palette = d3.scaleOrdinal().domain(data.map(d => d.cat))
    .range([COLORS.danger, COLORS.warm, COLORS.purple, COLORS.good,
            COLORS.green, COLORS.accent, COLORS.mute])

  const W = 620, H = 280
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // Pie (left)
  const r = 95, cx = 145, cy = H / 2 + 10
  const pie = d3.pie().value(d => d.v).sort(null)
  const arc = d3.arc().innerRadius(0).outerRadius(r)
  const arcs = pie(data)
  svg.append('g').attr('transform', `translate(${cx},${cy})`)
    .selectAll('path').data(arcs).join('path')
    .attr('d', arc).attr('fill', d => palette(d.data.cat))
    .attr('fill-opacity', 0.85).attr('stroke', '#0a0a0a').attr('stroke-width', 1)
  svg.append('text').attr('x', cx).attr('y', 20)
    .attr('text-anchor', 'middle').attr('fill', COLORS.danger)
    .attr('font-size', 10).attr('letter-spacing', '0.08em').text('PIE — hard to compare')

  // Bars (right) — reserve space on the right for % labels
  const barX = 320, rowH = 26
  const barLabelW = 34
  const barW = W - barX - barLabelW - 70
  const maxV = d3.max(data, d => d.v)
  const barXScale = d3.scaleLinear().domain([0, maxV * 1.05])
    .range([0, barW])
  svg.append('text').attr('x', barX).attr('y', 20)
    .attr('fill', COLORS.good).attr('font-size', 10).attr('letter-spacing', '0.08em')
    .text('SORTED BARS — obvious ranking')
  const sorted = [...data].sort((a, b) => b.v - a.v)
  for (let i = 0; i < sorted.length; i++) {
    const d = sorted[i]
    const ty = 40 + i * rowH
    svg.append('rect')
      .attr('x', barX + 70).attr('y', ty)
      .attr('width', barXScale(d.v)).attr('height', rowH - 8)
      .attr('fill', palette(d.cat)).attr('fill-opacity', 0.75)
    svg.append('text').attr('x', barX + 62).attr('y', ty + (rowH - 8) / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11)
      .text(d.cat)
    svg.append('text').attr('x', barX + 70 + barXScale(d.v) + 6)
      .attr('y', ty + (rowH - 8) / 2 + 4)
      .attr('fill', COLORS.label).attr('font-size', 10).text(d.v + '%')
  }
}

// --------------------------------------------------------- waffle-chart
export function renderWaffleChartDemo(container) {
  // 1 in 8 Americans — use a 10×10 waffle
  const pct = 12.5
  const filled = Math.round(pct)
  const W = 620, H = 280
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const grid = 10
  const cellSize = 22, gap = 4
  const gridW = grid * (cellSize + gap) - gap
  const gridX = 70, gridY = 20

  for (let i = 0; i < 100; i++) {
    const row = Math.floor(i / grid)
    const col = i % grid
    const cx = gridX + col * (cellSize + gap)
    const cy = gridY + row * (cellSize + gap)
    svg.append('rect').attr('x', cx).attr('y', cy)
      .attr('width', cellSize).attr('height', cellSize)
      .attr('rx', 2)
      .attr('fill', i < filled ? COLORS.warm : '#1a1a1a')
      .attr('fill-opacity', i < filled ? 0.9 : 1)
  }

  // Labels
  const labelX = gridX + gridW + 30
  svg.append('text').attr('x', labelX).attr('y', 50)
    .attr('fill', COLORS.warm).attr('font-size', 28).attr('font-weight', 600)
    .text('12.5%')
  svg.append('text').attr('x', labelX).attr('y', 72)
    .attr('fill', COLORS.text).attr('font-size', 13).text('or 1 in 8')
  svg.append('text').attr('x', labelX).attr('y', 100)
    .attr('fill', COLORS.label).attr('font-size', 11)
    .text('Households reporting')
  svg.append('text').attr('x', labelX).attr('y', 115)
    .attr('fill', COLORS.label).attr('font-size', 11)
    .text('food insecurity')
}

// --------------------------------------------------------- chord-diagram
export function renderChordDiagramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const names = ['N. America', 'S. America', 'Europe', 'Africa', 'Asia', 'Oceania']
  const matrix = [
    [   0, 180, 320,  40, 260,  30],
    [ 180,   0, 140,  10,  60,   5],
    [ 320, 140,   0, 220, 400,  20],
    [  40,  10, 220,   0, 110,   3],
    [ 260,  60, 400, 110,   0, 180],
    [  30,   5,  20,   3, 180,   0],
  ]
  const palette = [COLORS.accent, COLORS.good, COLORS.warm, COLORS.purple,
                   COLORS.green, COLORS.danger]
  const W = 620, H = 380
  const r = 140, innerR = 125
  const rootSvg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const svg = rootSvg.append('g').attr('transform', `translate(${W / 2},${H / 2 + 10})`)
  // Decoder panel (top-left)
  const dx = 12, dy = 12
  rootSvg.append('rect').attr('x', dx).attr('y', dy).attr('width', 160).attr('height', 78)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  rootSvg.append('text').attr('x', dx + 80).attr('y', dy + 13)
    .attr('text-anchor', 'middle').attr('fill', '#93c5fd').attr('font-size', 8)
    .attr('letter-spacing', '0.1em').text('DECODER')
  // Mini outer arc
  const miniArc = d3.arc().innerRadius(18).outerRadius(22)
    .startAngle(-Math.PI * 0.6).endAngle(-Math.PI * 0.2)
  rootSvg.append('g').attr('transform', `translate(${dx + 26},${dy + 50})`)
    .append('path').attr('d', miniArc()).attr('fill', COLORS.accent)
  rootSvg.append('text').attr('x', dx + 58).attr('y', dy + 32)
    .attr('fill', COLORS.label).attr('font-size', 9).text('outer arc = node total')
  // Mini ribbon (bezier)
  rootSvg.append('path')
    .attr('d', `M ${dx + 16} ${dy + 66} Q ${dx + 30} ${dy + 58}, ${dx + 42} ${dy + 66} L ${dx + 42} ${dy + 71} Q ${dx + 30} ${dy + 63}, ${dx + 16} ${dy + 71} Z`)
    .attr('fill', COLORS.warm).attr('fill-opacity', 0.55)
  rootSvg.append('text').attr('x', dx + 58).attr('y', dy + 72)
    .attr('fill', COLORS.label).attr('font-size', 9).text('ribbon = pair magnitude')
  const chord = d3.chord().padAngle(0.04).sortSubgroups(d3.descending)
  const arcs = chord(matrix)
  const arcGen = d3.arc().innerRadius(innerR).outerRadius(r)
  const ribbon = d3.ribbon().radius(innerR - 2)

  // Ribbons first
  const ribbonPaths = svg.append('g').attr('class', 'chord-ribbons').selectAll('path').data(arcs).join('path')
    .attr('class', 'chord-ribbon')
    .attr('data-source', d => d.source.index).attr('data-target', d => d.target.index)
    .attr('d', ribbon)
    .attr('fill', d => palette[d.source.index])
    .attr('fill-opacity', 0.55)
    .attr('stroke', '#0a0a0a').attr('stroke-width', 0.3)

  // Outer arcs + labels
  const groupG = svg.append('g').attr('class', 'chord-groups').selectAll('g').data(arcs.groups).join('g')
  const arcPaths = groupG.append('path').attr('class', 'chord-arc')
    .attr('data-index', d => d.index)
    .attr('d', arcGen)
    .attr('fill', d => palette[d.index]).attr('fill-opacity', 0.9)
  groupG.append('text')
    .each(d => { d.angle = (d.startAngle + d.endAngle) / 2 })
    .attr('dy', '0.35em')
    .attr('transform', d => `
      rotate(${(d.angle * 180 / Math.PI - 90)})
      translate(${r + 6})
      ${d.angle > Math.PI ? 'rotate(180)' : ''}
    `)
    .attr('text-anchor', d => d.angle > Math.PI ? 'end' : null)
    .attr('pointer-events', 'none')
    .attr('fill', COLORS.text).attr('font-size', 11)
    .text(d => names[d.index])

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals pair or region total)
  // - Ribbon hover: show the pair and the larger of the two directions
  //   (matrix is symmetric in our data, so just show the flow magnitude)
  // - Arc hover: show the region's total outflow
  const tip = createTooltip(container, { className: 'chord-tip' })
  function dim(isOnFn) {
    ribbonPaths.attr('fill-opacity', d => isOnFn(d) ? 0.85 : 0.08)
    arcPaths.attr('fill-opacity', d => isOnFn({ source: { index: d.index }, target: { index: d.index } }) ? 0.9 : 0.35)
  }
  function clear() {
    ribbonPaths.attr('fill-opacity', 0.55)
    arcPaths.attr('fill-opacity', 0.9)
    tip.hide()
  }
  ribbonPaths
    .style('cursor', 'pointer')
    .on('mouseenter', function (event, d) {
      dim(r => (r.source.index === d.source.index && r.target.index === d.target.index) ||
               (r.source.index === d.target.index && r.target.index === d.source.index))
      const v = Math.max(matrix[d.source.index][d.target.index], matrix[d.target.index][d.source.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.source.index]} ↔ ${names[d.target.index]}</strong><br>` +
        `<span style="color:#a3a3a3">flow:</span> <strong>${v}</strong>`)
    })
    .on('mousemove', function (event, d) {
      const v = Math.max(matrix[d.source.index][d.target.index], matrix[d.target.index][d.source.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.source.index]} ↔ ${names[d.target.index]}</strong><br>` +
        `<span style="color:#a3a3a3">flow:</span> <strong>${v}</strong>`)
    })
    .on('mouseleave', clear)
    .on('click', function (event, d) {
      const v = Math.max(matrix[d.source.index][d.target.index], matrix[d.target.index][d.source.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.source.index]} ↔ ${names[d.target.index]}</strong><br>` +
        `<span style="color:#a3a3a3">flow:</span> <strong>${v}</strong>`)
    })
  arcPaths
    .style('cursor', 'pointer')
    .on('mouseenter', function (event, d) {
      dim(r => r.source.index === d.index || r.target.index === d.index)
      const total = d3.sum(matrix[d.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.index]}</strong><br>` +
        `<span style="color:#a3a3a3">total flow:</span> <strong>${total}</strong>`)
    })
    .on('mousemove', function (event, d) {
      const total = d3.sum(matrix[d.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.index]}</strong><br>` +
        `<span style="color:#a3a3a3">total flow:</span> <strong>${total}</strong>`)
    })
    .on('mouseleave', clear)
    .on('click', function (event, d) {
      const total = d3.sum(matrix[d.index])
      tip.show(event.pageX, event.pageY,
        `<strong>${names[d.index]}</strong><br>` +
        `<span style="color:#a3a3a3">total flow:</span> <strong>${total}</strong>`)
    })
}

// --------------------------------------------------------- streamgraph
export function renderStreamgraphDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Music genre share over a decade (synthetic, smooth)
  const years = Array.from({ length: 20 }, (_, i) => 2006 + i)
  const genres = ['Rock', 'Pop', 'Hip-Hop', 'Electronic', 'Country', 'R&B']
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(31)
  const data = years.map((y, i) => {
    const row = { year: y }
    // Hip-hop rises, Rock declines, Pop stays, Electronic rises then plateaus
    row['Rock']       = Math.max(0, 30 - i * 1.2 + (rng() - 0.5) * 3)
    row['Pop']        = 22 + Math.sin(i / 4) * 4 + (rng() - 0.5) * 2
    row['Hip-Hop']    = Math.max(0,  8 + i * 1.8 + (rng() - 0.5) * 3)
    row['Electronic'] = Math.min(14,  2 + i * 0.9) + (rng() - 0.5) * 1.5
    row['Country']    = 18 + Math.cos(i / 5) * 2 + (rng() - 0.5) * 2
    row['R&B']        = 15 - i * 0.2 + Math.sin(i / 3) * 2 + (rng() - 0.5) * 2
    return row
  })

  const W = 620, H = 300
  const margin = { top: 16, right: 90, bottom: 28, left: 36 }
  d3.select(container).style('position', 'relative')
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const stack = d3.stack().keys(genres).offset(d3.stackOffsetWiggle).order(d3.stackOrderInsideOut)
  const series = stack(data)
  const x = d3.scaleLinear().domain([years[0], years[years.length - 1]])
    .range([margin.left, W - margin.right])
  const allLo = d3.min(series, s => d3.min(s, d => d[0]))
  const allHi = d3.max(series, s => d3.max(s, d => d[1]))
  const y = d3.scaleLinear().domain([allLo, allHi])
    .range([H - margin.bottom, margin.top])
  const colors = { Rock: COLORS.danger, Pop: COLORS.warm, 'Hip-Hop': COLORS.purple,
    Electronic: COLORS.good, Country: COLORS.green, 'R&B': COLORS.accent }
  const area = d3.area()
    .x((_, i) => x(years[i])).y0(d => y(d[0])).y1(d => y(d[1]))
    .curve(d3.curveBasis)
  svg.append('g').selectAll('path').data(series).join('path')
    .attr('d', area).attr('fill', d => colors[d.key])
    .attr('fill-opacity', 0.8)

  for (const s of series) {
    const last = s[s.length - 1]
    const ym = (y(last[0]) + y(last[1])) / 2
    svg.append('text').attr('x', W - margin.right + 6).attr('y', ym + 3)
      .attr('pointer-events', 'none')
      .attr('fill', colors[s.key]).attr('font-size', 11).text(s.key)
  }
  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  if (!interactive) return

  // INTERACTIVE (P10: time-cursor reveals each genre's share at a year)
  const cursorG = svg.append('g').attr('class', 'sg-cursor')
    .style('opacity', 0).style('pointer-events', 'none')
  cursorG.append('line').attr('y1', margin.top).attr('y2', H - margin.bottom)
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1).attr('stroke-dasharray', '2 3')
  const yearLabel = cursorG.append('text').attr('y', margin.top - 4)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label)
    .attr('font-size', 10).attr('font-weight', 600)

  const tip = createTooltip(container, { className: 'sg-tip' })
  function update(pageX, pageY, event) {
    const [mx] = d3.pointer(event, svg.node())
    const yearF = x.invert(mx)
    const year = Math.max(years[0], Math.min(years[years.length - 1], Math.round(yearF)))
    const idx = year - years[0]
    cursorG.style('opacity', 1).select('line')
      .attr('x1', x(year)).attr('x2', x(year))
    yearLabel.attr('x', x(year)).text(year)
    const rows = genres
      .map(k => ({ k, v: data[idx][k], color: colors[k] }))
      .sort((a, b) => b.v - a.v)
    const html = `<div style="font-weight:600;margin-bottom:3px">${year}</div>` +
      rows.map(r =>
        `<div><span style="display:inline-block;width:8px;height:8px;background:${r.color};margin-right:5px;border-radius:2px;"></span>` +
        `<span style="color:#a3a3a3">${r.k}:</span> ${r.v.toFixed(1)}</div>`).join('')
    tip.show(pageX, pageY, html)
  }
  const overlay = svg.append('rect')
    .attr('x', margin.left).attr('y', margin.top)
    .attr('width', W - margin.right - margin.left)
    .attr('height', H - margin.top - margin.bottom)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  overlay.on('mousemove', event => update(event.pageX, event.pageY, event))
  overlay.on('mouseleave', () => { cursorG.style('opacity', 0); tip.hide() })
  overlay.on('click', event => update(event.pageX, event.pageY, event))
}

// --------------------------------------------------------- ridgeline
export function renderRidgelineDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Monthly temperature distributions for 12 cities, one per row
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(37)
  const cities = [
    { name: 'Juneau',      m: 35, sd: 10 },
    { name: 'Seattle',     m: 52, sd: 13 },
    { name: 'Minneapolis', m: 45, sd: 25 },
    { name: 'Chicago',     m: 50, sd: 24 },
    { name: 'Denver',      m: 52, sd: 20 },
    { name: 'Boston',      m: 52, sd: 20 },
    { name: 'New York',    m: 55, sd: 18 },
    { name: 'Los Angeles', m: 65, sd:  9 },
    { name: 'San Diego',   m: 66, sd:  7 },
    { name: 'Atlanta',     m: 62, sd: 15 },
    { name: 'Houston',     m: 69, sd: 13 },
    { name: 'Miami',       m: 76, sd:  8 },
  ].sort((a, b) => a.m - b.m)
  function sampleNormal(m, sd) {
    const z = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
    return m + sd * z
  }
  for (const c of cities) {
    c.samples = []
    for (let i = 0; i < 200; i++) c.samples.push(sampleNormal(c.m, c.sd))
  }
  const gridT = d3.range(10, 100, 1)
  function kde(samples, h) {
    return gridT.map(t => {
      let s = 0
      for (const v of samples) { const u = (t - v) / h; s += Math.exp(-0.5 * u * u) }
      return s / (samples.length * h * Math.sqrt(2 * Math.PI))
    })
  }

  // Interactive bandwidth slider (omitted in static mode)
  const host = d3.select(container)
  let slider = null
  if (interactive) {
    slider = host.append('div').attr('class', 'demo-slider')
    slider.html(`
      <label for="ridge-bw">bandwidth</label>
      <input id="ridge-bw" type="range" min="1" max="14" value="4" step="0.5" />
      <span class="val">4</span>
      <span class="hint">low = noisy / high = over-smoothed</span>
    `)
  }
  const chartEl = host.append('div').node()

  function draw(bw) {
    d3.select(chartEl).selectAll('*').remove()
    const densities = cities.map(c => kde(c.samples, bw))
    const maxD = d3.max(densities.flat())

    const W = 620, H = 380
    const margin = { top: 16, right: 18, bottom: 28, left: 110 }
    const svg = d3.select(chartEl).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const rowH = (H - margin.top - margin.bottom) / cities.length
    const overlap = 1.9
    const x = d3.scaleLinear().domain([gridT[0], gridT[gridT.length - 1]])
      .range([margin.left, W - margin.right])
    const yAmplitude = d3.scaleLinear().domain([0, maxD]).range([0, rowH * overlap])

    for (let i = 0; i < cities.length; i++) {
      const baseY = margin.top + i * rowH + rowH
      const pts = densities[i].map((d, j) => ({ x: x(gridT[j]), y: baseY - yAmplitude(d) }))
      const area = d3.area().curve(d3.curveBasis).x(d => d.x).y0(baseY).y1(d => d.y)
      svg.append('path').datum(pts).attr('d', area)
        .attr('fill', COLORS.accent).attr('fill-opacity', 0.35)
      const line = d3.line().curve(d3.curveBasis).x(d => d.x).y(d => d.y)
      svg.append('path').datum(pts).attr('d', line)
        .attr('fill', 'none').attr('stroke', COLORS.accent).attr('stroke-width', 1.2)
      svg.append('text').attr('x', margin.left - 8).attr('y', baseY - 3)
        .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 10)
        .text(cities[i].name)
    }
    svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
      .call(d3.axisBottom(x).ticks(7).tickFormat(d => d + '°F'))
      .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  }

  if (interactive) {
    const input = slider.select('input').node()
    const val = slider.select('.val').node()
    input.addEventListener('input', () => {
      val.textContent = +input.value
      draw(+input.value)
    })
  }
  draw(4)
}

// --------------------------------------------------------- connected-scatter
export function renderConnectedScatterDemo(container, opts = {}) {
  const interactive_cs = opts.interactive !== false
  // Unemployment × inflation trajectory 2000-2023 (synthetic)
  const path = [
    { y: 2000, u: 4.0, i: 3.4 },
    { y: 2001, u: 4.7, i: 2.8 },
    { y: 2002, u: 5.8, i: 1.6 },
    { y: 2003, u: 6.0, i: 2.3 },
    { y: 2004, u: 5.5, i: 2.7 },
    { y: 2005, u: 5.1, i: 3.4 },
    { y: 2006, u: 4.6, i: 3.2 },
    { y: 2007, u: 4.6, i: 2.9 },
    { y: 2008, u: 5.8, i: 3.8 },
    { y: 2009, u: 9.3, i: 0.0 },
    { y: 2010, u: 9.6, i: 1.6 },
    { y: 2011, u: 8.9, i: 3.2 },
    { y: 2012, u: 8.1, i: 2.1 },
    { y: 2013, u: 7.4, i: 1.5 },
    { y: 2014, u: 6.2, i: 1.6 },
    { y: 2015, u: 5.3, i: 0.1 },
    { y: 2016, u: 4.9, i: 1.3 },
    { y: 2017, u: 4.4, i: 2.1 },
    { y: 2018, u: 3.9, i: 2.4 },
    { y: 2019, u: 3.7, i: 1.8 },
    { y: 2020, u: 8.1, i: 1.2 },
    { y: 2021, u: 5.4, i: 4.7 },
    { y: 2022, u: 3.6, i: 8.0 },
    { y: 2023, u: 3.7, i: 4.1 },
  ]
  const W = 620, H = 340
  const margin = { top: 22, right: 22, bottom: 36, left: 44 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const x = d3.scaleLinear().domain([3, 10]).range([margin.left, W - margin.right])
  const y = d3.scaleLinear().domain([-1, 9]).range([H - margin.bottom, margin.top])
  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d + '%'))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5).tickFormat(d => d + '%'))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('text').attr('x', W - margin.right).attr('y', H - 8)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10)
    .text('Unemployment →')
  svg.append('text').attr('x', margin.left).attr('y', margin.top - 6)
    .attr('fill', COLORS.label).attr('font-size', 10).text('Inflation')

  // Color gradient along the path
  const color = d3.scaleLinear().domain([0, path.length - 1])
    .range(['#1e293b', COLORS.good])
  const line = d3.line().x(d => x(d.u)).y(d => y(d.i)).curve(d3.curveCatmullRom)
  svg.append('path').datum(path).attr('d', line)
    .attr('fill', 'none').attr('stroke', COLORS.mute).attr('stroke-width', 1.2)
  const dots = []
  for (let i = 0; i < path.length; i++) {
    const d = path[i]
    const c = svg.append('circle').attr('class', 'cs-dot').attr('data-year', d.y)
      .attr('cx', x(d.u)).attr('cy', y(d.i))
      .attr('r', i === 0 || i === path.length - 1 ? 4 : 2.5).attr('fill', color(i))
    dots.push({ d, circle: c, i })
  }
  for (const tag of [{ y: 2000 }, { y: 2009 }, { y: 2020 }, { y: 2022 }, { y: 2023 }]) {
    const p = path.find(d => d.y === tag.y)
    if (!p) continue
    svg.append('text')
      .attr('x', x(p.u) + 7).attr('y', y(p.i) - 5)
      .attr('pointer-events', 'none')
      .attr('fill', COLORS.text).attr('font-size', 10).text(p.y)
  }

  if (interactive_cs) {
    // INTERACTIVE (P10: voronoi-nearest point — hover reveals year + exact values)
    const pts = dots.map((d, i) => ({ i, x: x(d.d.u), y: y(d.d.i), d: d.d }))
    const delaunay = d3.Delaunay.from(pts, p => p.x, p => p.y)
    const tip = createTooltip(container, { className: 'cs-tip' })
    let hovered = null
    function setHover(idx) {
      if (hovered === idx) return
      if (hovered != null) dots[hovered].circle.attr('r', hovered === 0 || hovered === path.length - 1 ? 4 : 2.5).attr('stroke', null)
      hovered = idx
      if (idx != null) dots[idx].circle.attr('r', 6).attr('stroke', '#f5f5f5').attr('stroke-width', 1.4)
    }
    const overlay = svg.append('rect')
      .attr('x', margin.left).attr('y', margin.top)
      .attr('width', W - margin.left - margin.right)
      .attr('height', H - margin.top - margin.bottom)
      .attr('fill', 'transparent').style('cursor', 'crosshair')
    overlay.on('mousemove', function (event) {
      const [mx, my] = d3.pointer(event, svg.node())
      const idx = delaunay.find(mx, my)
      if (idx == null || idx < 0) return
      setHover(idx)
      const d = path[idx]
      tip.show(event.pageX, event.pageY,
        `<strong>${d.y}</strong><br>` +
        `<span style="color:#a3a3a3">unemployment:</span> <strong>${d.u}%</strong><br>` +
        `<span style="color:#a3a3a3">inflation:</span> <strong>${d.i}%</strong>`)
    })
    overlay.on('mouseleave', () => { setHover(null); tip.hide() })
    overlay.on('click', function (event) {
      const [mx, my] = d3.pointer(event, svg.node())
      const idx = delaunay.find(mx, my)
      if (idx == null || idx < 0) return
      setHover(idx)
      const d = path[idx]
      tip.show(event.pageX, event.pageY,
        `<strong>${d.y}</strong><br>` +
        `<span style="color:#a3a3a3">unemployment:</span> <strong>${d.u}%</strong><br>` +
        `<span style="color:#a3a3a3">inflation:</span> <strong>${d.i}%</strong>`)
    })
  }
}

// --------------------------------------------------------- mosaic
export function renderMosaicDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Smoking × exercise survey (made up)
  // Rows: never/current/former smoker; cols: never/sometimes/often exercise
  const data = [
    { smoking: 'Never',   exercise: 'Often',     n: 220 },
    { smoking: 'Never',   exercise: 'Sometimes', n: 180 },
    { smoking: 'Never',   exercise: 'Never',     n: 100 },
    { smoking: 'Former',  exercise: 'Often',     n:  95 },
    { smoking: 'Former',  exercise: 'Sometimes', n: 120 },
    { smoking: 'Former',  exercise: 'Never',     n:  60 },
    { smoking: 'Current', exercise: 'Often',     n:  30 },
    { smoking: 'Current', exercise: 'Sometimes', n:  55 },
    { smoking: 'Current', exercise: 'Never',     n: 140 },
  ]
  const smokingLevels = ['Never', 'Former', 'Current']
  const exerciseLevels = ['Often', 'Sometimes', 'Never']
  const rowTotals = {}
  for (const s of smokingLevels) {
    rowTotals[s] = data.filter(d => d.smoking === s).reduce((a, b) => a + b.n, 0)
  }
  const grandTotal = Object.values(rowTotals).reduce((a, b) => a + b, 0)

  const W = 620, H = 340
  const margin = { top: 58, right: 20, bottom: 26, left: 110 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom

  // Compute row heights from row totals
  const rowH = {}
  let yCur = margin.top
  for (const s of smokingLevels) {
    rowH[s] = (rowTotals[s] / grandTotal) * plotH
  }

  // Colors: diverging for "overrepresented / underrepresented vs independence"
  const expectedRatio = { Often: 345 / grandTotal, Sometimes: 355 / grandTotal, Never: 300 / grandTotal }
  const maxDev = 0.25
  const colorFor = (s, e, n) => {
    const rowN = rowTotals[s]
    const actual = n / rowN
    const expected = expectedRatio[e]
    const dev = (actual - expected) / maxDev
    const clamped = Math.max(-1, Math.min(1, dev))
    const baseHue = clamped > 0 ? 142 : 0  // green for over, red for under
    const sat = Math.abs(clamped) * 75 + 20
    return `hsl(${baseHue}, ${sat}%, 45%)`
  }

  let yPos = margin.top
  const cellRefs = []
  for (const s of smokingLevels) {
    const h = rowH[s]
    let xPos = margin.left
    const cellsInRow = data.filter(d => d.smoking === s)
    const rowTotal = rowTotals[s]
    for (const e of exerciseLevels) {
      const cell = cellsInRow.find(c => c.exercise === e)
      if (!cell) continue
      const w = (cell.n / rowTotal) * plotW
      const rect = svg.append('rect').attr('class', 'mosaic-cell')
        .attr('data-smoking', s).attr('data-exercise', e)
        .attr('x', xPos).attr('y', yPos)
        .attr('width', w - 1).attr('height', h - 1)
        .attr('fill', colorFor(s, e, cell.n))
        .attr('fill-opacity', 0.8)
      if (w > 30 && h > 20) {
        svg.append('text').attr('x', xPos + w / 2).attr('y', yPos + h / 2 + 4)
          .attr('text-anchor', 'middle').attr('fill', '#0a0a0a').attr('pointer-events', 'none')
          .attr('font-size', 11).attr('font-weight', 600).text(cell.n)
      }
      cellRefs.push({ s, e, n: cell.n, rect })
      xPos += w
    }
    svg.append('text').attr('x', margin.left - 10).attr('y', yPos + h / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11)
      .text(s + ' smoker')
    yPos += h
  }
  // Column headers
  let xHdr = margin.left
  for (const e of exerciseLevels) {
    // Use the first row's column width as proxy (they differ per row but headers are a rough indicator)
    const firstRow = smokingLevels[0]
    const cell = data.find(d => d.smoking === firstRow && d.exercise === e)
    const w = (cell.n / rowTotals[firstRow]) * plotW
    svg.append('text').attr('x', xHdr + w / 2).attr('y', margin.top - 18)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 10)
      .attr('font-weight', 500).text(e)
    xHdr += w
  }
  svg.append('text').attr('x', margin.left + plotW / 2).attr('y', margin.top - 38)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
    .attr('letter-spacing', '0.12em').text('EXERCISE FREQUENCY')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals the joint cell's count + row/col
  // totals + the expected-under-independence baseline that shades it)
  const tip = createTooltip(container, { className: 'mosaic-tip' })
  const colTotals = {}
  for (const e of exerciseLevels) {
    colTotals[e] = data.filter(d => d.exercise === e).reduce((a, b) => a + b.n, 0)
  }
  for (const ref of cellRefs) {
    const expected = Math.round(rowTotals[ref.s] * (colTotals[ref.e] / grandTotal))
    const deviation = ref.n - expected
    const devSign = deviation >= 0 ? '+' : ''
    const body = `<strong>${ref.s} smoker · ${ref.e}</strong><br>` +
      `<span style="color:#a3a3a3">observed:</span> <strong>${ref.n}</strong> ` +
      `<span style="color:#a3a3a3">(expected ~${expected}, ${devSign}${deviation})</span>`
    ref.rect.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        ref.rect.attr('stroke', '#f5f5f5').attr('stroke-width', 1.5)
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', () => { ref.rect.attr('stroke', null).attr('stroke-width', null); tip.hide() })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- dot-map (stylized CONUS)
export function renderDotMapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // 1854-Snow-esque dot map with synthetic incident clusters
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(41)
  const metros = [
    { id: 'SF Bay',   lon: -122.4, lat: 37.8, n: 70 },
    { id: 'LA',       lon: -118.3, lat: 34.0, n: 90 },
    { id: 'Chicago',  lon: -87.6,  lat: 41.9, n: 80 },
    { id: 'NYC',      lon: -74.0,  lat: 40.7, n:130 },
    { id: 'DC',       lon: -77.0,  lat: 38.9, n: 60 },
    { id: 'Austin',   lon: -97.7,  lat: 30.3, n: 55 },
    { id: 'Atlanta',  lon: -84.4,  lat: 33.7, n: 50 },
    { id: 'Miami',    lon: -80.2,  lat: 25.8, n: 45 },
    { id: 'Seattle',  lon: -122.3, lat: 47.6, n: 45 },
    { id: 'Denver',   lon: -104.9, lat: 39.7, n: 30 },
  ]
  const points = []
  for (const m of metros) {
    for (let i = 0; i < m.n; i++) {
      const r1 = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
      const r2 = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
      points.push({ lon: m.lon + r1 * 1.2, lat: m.lat + r2 * 0.8 })
    }
  }

  const W = 620, H = 320
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    .style('background', '#0a0a0a')
  const bounds = { lat: [24, 50], lon: [-125, -66] }
  const proj = ([lon, lat]) => [
    ((lon - bounds.lon[0]) / (bounds.lon[1] - bounds.lon[0])) * (W - 40) + 20,
    H - 30 - ((lat - bounds.lat[0]) / (bounds.lat[1] - bounds.lat[0])) * (H - 60),
  ]

  svg.append('rect').attr('x', 20).attr('y', 20)
    .attr('width', W - 40).attr('height', H - 40)
    .attr('fill', 'none').attr('stroke', '#1a1a1a').attr('stroke-dasharray', '3 4')

  svg.append('g').selectAll('circle').data(points).join('circle')
    .attr('cx', d => proj([d.lon, d.lat])[0])
    .attr('cy', d => proj([d.lon, d.lat])[1])
    .attr('r', 2.4).attr('fill', COLORS.warm).attr('fill-opacity', 0.55)
    .attr('pointer-events', 'none')

  for (const m of metros) {
    const [cx, cy] = proj([m.lon, m.lat])
    svg.append('text').attr('x', cx + 8).attr('y', cy + 3)
      .attr('fill', COLORS.text).attr('font-size', 9)
      .attr('font-weight', 500)
      .text(m.n > 80 ? '●' : '')
  }
  svg.append('text').attr('x', 22).attr('y', 15)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em')
    .text('SYNTHETIC INCIDENTS · CONUS')

  if (!interactive) return

  // INTERACTIVE (P10: voronoi over metro centers — hover reveals which
  // cluster the cursor sits over and its count, the story this chart tells)
  const centers = metros.map(m => ({ m, p: proj([m.lon, m.lat]) }))
  const delaunay = d3.Delaunay.from(centers, c => c.p[0], c => c.p[1])
  const tip = createTooltip(container, { className: 'dot-map-tip' })
  const ringG = svg.append('g').attr('class', 'dot-map-ring')
  const overlay = svg.append('rect')
    .attr('x', 20).attr('y', 20).attr('width', W - 40).attr('height', H - 40)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  function update(pageX, pageY, event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    const c = centers[idx]
    ringG.selectAll('*').remove()
    ringG.append('circle').attr('cx', c.p[0]).attr('cy', c.p[1]).attr('r', 22)
      .attr('fill', 'none').attr('stroke', '#f5f5f5').attr('stroke-width', 1.4)
      .attr('stroke-dasharray', '3 3')
    tip.show(pageX, pageY,
      `<strong>${c.m.id} area</strong><br><span style="color:#a3a3a3">incidents in cluster:</span> <strong>${c.m.n}</strong>`)
  }
  overlay.on('mousemove', event => update(event.pageX, event.pageY, event))
  overlay.on('mouseleave', () => { ringG.selectAll('*').remove(); tip.hide() })
  overlay.on('click', event => update(event.pageX, event.pageY, event))
}

// ============================================================
// Shared stylized-US helpers for the spatial demos
// ============================================================
// Hex-grid US layout — 50 states + DC as [col, row] pairs in a
// ~12×8 grid roughly matching US geography. Exact positions don't
// matter for a demo; readers recognize it as "US-shaped."
const HEX_US_GRID = [
  // Alaska / Hawaii offset
  { s: 'AK', col:  0, row: 0 },
  { s: 'HI', col:  0, row: 6 },
  // Pacific
  { s: 'WA', col:  1, row: 0 }, { s: 'OR', col:  1, row: 1 }, { s: 'CA', col:  1, row: 3 },
  // Mountain West
  { s: 'MT', col:  2, row: 0 }, { s: 'ID', col:  2, row: 1 }, { s: 'NV', col:  2, row: 2 },
  { s: 'UT', col:  3, row: 3 }, { s: 'AZ', col:  2, row: 4 },
  // Rockies / Plains west
  { s: 'ND', col:  3, row: 0 }, { s: 'SD', col:  3, row: 1 }, { s: 'WY', col:  3, row: 2 },
  { s: 'CO', col:  4, row: 3 }, { s: 'NM', col:  3, row: 4 },
  // Plains
  { s: 'MN', col:  4, row: 0 }, { s: 'IA', col:  4, row: 1 }, { s: 'NE', col:  5, row: 2 },
  { s: 'KS', col:  5, row: 3 }, { s: 'OK', col:  4, row: 4 },
  // South-central
  { s: 'TX', col:  3, row: 5 }, { s: 'LA', col:  4, row: 5 }, { s: 'AR', col:  5, row: 4 },
  { s: 'MS', col:  6, row: 4 }, { s: 'AL', col:  7, row: 4 },
  // Midwest
  { s: 'WI', col:  5, row: 0 }, { s: 'IL', col:  6, row: 1 }, { s: 'MO', col:  6, row: 2 },
  { s: 'MI', col:  6, row: 0 }, { s: 'IN', col:  7, row: 1 }, { s: 'KY', col:  7, row: 2 },
  { s: 'OH', col:  8, row: 1 }, { s: 'TN', col:  7, row: 3 }, { s: 'WV', col:  8, row: 2 },
  // East
  { s: 'PA', col:  9, row: 1 }, { s: 'VA', col:  8, row: 3 }, { s: 'NC', col:  8, row: 4 },
  { s: 'SC', col:  9, row: 4 }, { s: 'GA', col:  8, row: 5 }, { s: 'FL', col:  9, row: 5 },
  { s: 'NY', col:  9, row: 0 }, { s: 'NJ', col: 10, row: 1 }, { s: 'DE', col: 11, row: 3 },
  { s: 'MD', col:  9, row: 3 }, { s: 'DC', col: 10, row: 3 },
  // New England
  { s: 'ME', col: 11, row: 0 }, { s: 'VT', col: 10, row: 0 },
  { s: 'NH', col: 11, row: 1 }, { s: 'MA', col: 11, row: 2 }, { s: 'RI', col: 11, row: 4 },
  { s: 'CT', col: 10, row: 2 },
]

// Draw the hex-grid US. Calls cellFn(state) for each cell's fill/label.
function drawHexUS(svg, { W, H, marginX = 20, marginY = 20, hexR = 16, cellFn }) {
  const cols = 12, rows = 7
  const cellW = hexR * Math.sqrt(3)
  const cellH = hexR * 1.5
  const gridW = cols * cellW
  const gridH = (rows + 1) * cellH
  const ox = (W - gridW) / 2 + cellW / 2
  const oy = marginY + hexR

  function hexPath(cx, cy, r) {
    const pts = []
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 2 + i * Math.PI / 3
      pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)])
    }
    return 'M ' + pts.map(p => p.join(',')).join(' L ') + ' Z'
  }

  const cells = []
  for (const cell of HEX_US_GRID) {
    const offsetX = (cell.row % 2) * (cellW / 2)
    const cx = ox + cell.col * cellW + offsetX
    const cy = oy + cell.row * cellH
    const opts = cellFn(cell.s) || {}
    const path = svg.append('path')
      .attr('class', 'hex-cell')
      .attr('data-state', cell.s)
      .attr('d', hexPath(cx, cy, hexR * 0.92))
      .attr('fill', opts.fill || '#1a1a1a')
      .attr('stroke', opts.stroke || '#0a0a0a')
      .attr('stroke-width', opts.strokeW || 1)
    const text = svg.append('text')
      .attr('class', 'hex-label').attr('data-state', cell.s)
      .attr('x', cx).attr('y', cy + 3.5)
      .attr('text-anchor', 'middle').attr('pointer-events', 'none')
      .attr('fill', opts.textColor || '#f5f5f5')
      .attr('font-size', 9).attr('font-weight', 600)
      .text(cell.s)
    cells.push({ s: cell.s, cx, cy, path, text, opts })
  }
  return { gridW, gridH, ox, oy, cellW, cellH, hexR, cells }
}

// Shared HTML tooltip helper for hover affordances. Creates a
// position-absolute div pinned to the container; respects
// prefers-reduced-motion for the opacity transition (P9).
function createTooltip(container, { className = 'chart-tip' } = {}) {
  d3.select(container).style('position', 'relative')
  const reduced = typeof window !== 'undefined' && window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const tip = d3.select(container).append('div')
    .attr('class', className)
    .style('position', 'absolute').style('pointer-events', 'none')
    .style('background', '#0f0f0f').style('border', '1px solid #2a2a2a')
    .style('padding', '6px 9px').style('border-radius', '4px')
    .style('font-size', '11px').style('color', '#e5e5e5')
    .style('opacity', 0).style('max-width', '260px')
    .style('transition', reduced ? 'none' : 'opacity 120ms')
    .style('transform', 'translate(10px, -50%)')
    .attr('role', 'status').attr('aria-live', 'polite')
  function show(pageX, pageY, html) {
    const rect = container.getBoundingClientRect()
    tip.html(html)
      .style('left', (pageX - rect.left - window.scrollX) + 'px')
      .style('top', (pageY - rect.top - window.scrollY) + 'px')
      .style('opacity', 1)
  }
  function hide() { tip.style('opacity', 0) }
  return { node: tip, show, hide }
}

// Metros for outline-style map demos. lon/lat, projected simply.
const US_METROS = [
  { id: 'SF',  name: 'San Francisco', lat: 37.77, lon: -122.42 },
  { id: 'LA',  name: 'Los Angeles',   lat: 34.05, lon: -118.24 },
  { id: 'SEA', name: 'Seattle',       lat: 47.60, lon: -122.33 },
  { id: 'DEN', name: 'Denver',        lat: 39.74, lon: -104.99 },
  { id: 'AUS', name: 'Austin',        lat: 30.27, lon:  -97.74 },
  { id: 'HOU', name: 'Houston',       lat: 29.76, lon:  -95.37 },
  { id: 'CHI', name: 'Chicago',       lat: 41.88, lon:  -87.63 },
  { id: 'ATL', name: 'Atlanta',       lat: 33.75, lon:  -84.39 },
  { id: 'NYC', name: 'New York',      lat: 40.71, lon:  -74.00 },
  { id: 'DC',  name: 'Washington',    lat: 38.90, lon:  -77.04 },
  { id: 'MIA', name: 'Miami',         lat: 25.76, lon:  -80.19 },
  { id: 'BOS', name: 'Boston',        lat: 42.36, lon:  -71.06 },
]
function projConus(W, H, { padX = 20, padY = 20 } = {}) {
  const bounds = { lat: [24, 50], lon: [-125, -66] }
  return ([lon, lat]) => [
    ((lon - bounds.lon[0]) / (bounds.lon[1] - bounds.lon[0])) * (W - 2 * padX) + padX,
    H - padY - ((lat - bounds.lat[0]) / (bounds.lat[1] - bounds.lat[0])) * (H - 2 * padY),
  ]
}

// --------------------------------------------------------- choropleth
export function renderChoroplethDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const values = {
    MA: 45, MD: 40, CT: 39, VT: 39, NJ: 41, NH: 37, NY: 37, VA: 38, MN: 36, CO: 41, WA: 36,
    IL: 35, RI: 34, CA: 34, HI: 33, DE: 33, OR: 34, DC: 60, ME: 31, KS: 34, PA: 32, UT: 34,
    NE: 31, ND: 30, WI: 29, MT: 31, GA: 31, AZ: 30, NC: 31, FL: 29, TX: 30, IA: 28, MI: 29,
    SD: 27, SC: 28, ID: 26, MO: 29, OH: 28, WY: 26, AK: 29, IN: 26, NM: 27, TN: 26, OK: 25,
    LA: 23, AL: 25, NV: 24, KY: 24, AR: 23, MS: 21, WV: 21,
  }
  const W = 620, H = 360
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const vMax = d3.max(Object.values(values))
  const vMin = d3.min(Object.values(values))
  const color = d3.scaleSequential(d3.interpolateViridis).domain([vMin - 2, vMax + 2])

  const { cells } = drawHexUS(svg, { W, H, cellFn: s => {
    const v = values[s]
    if (v == null) return { fill: '#1a1a1a', textColor: '#333' }
    const c = d3.color(color(v))
    const lightness = c.r * 0.299 + c.g * 0.587 + c.b * 0.114
    return { fill: color(v), textColor: lightness > 140 ? '#0a0a0a' : '#f5f5f5', stroke: '#0a0a0a' }
  } })
  const legX = 20, legY = H - 28
  svg.append('text').attr('x', legX).attr('y', legY - 2)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em')
    .text('% BACHELOR\'S+')
  const steps = 20
  for (let i = 0; i < steps; i++) {
    svg.append('rect')
      .attr('x', legX + i * 6).attr('y', legY + 6).attr('width', 6).attr('height', 10)
      .attr('fill', color(vMin + (vMax - vMin) * i / (steps - 1)))
  }
  svg.append('text').attr('x', legX).attr('y', legY + 28).attr('fill', COLORS.label).attr('font-size', 9).text(`${Math.round(vMin)}%`)
  svg.append('text').attr('x', legX + steps * 6).attr('y', legY + 28).attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 9).text(`${Math.round(vMax)}%`)

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals exact state value)
  const tip = createTooltip(container, { className: 'choropleth-tip' })
  for (const c of cells) {
    const v = values[c.s]
    c.path.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        c.path.attr('stroke', '#f5f5f5').attr('stroke-width', 1.8)
        const body = v == null
          ? '<span style="color:#737373">no data</span>'
          : `<span style="color:#a3a3a3">bachelor's+:</span> <strong>${v}%</strong>`
        tip.show(event.pageX, event.pageY, `<strong>${c.s}</strong><br>${body}`)
      })
      .on('mousemove', function (event) {
        if (v != null) tip.show(event.pageX, event.pageY,
          `<strong>${c.s}</strong><br><span style="color:#a3a3a3">bachelor's+:</span> <strong>${v}%</strong>`)
      })
      .on('mouseleave', () => {
        c.path.attr('stroke', c.opts.stroke || '#0a0a0a').attr('stroke-width', 1)
        tip.hide()
      })
      // P5: tap shows tooltip on touch devices
      .on('click', function (event) {
        if (v == null) return
        tip.show(event.pageX, event.pageY,
          `<strong>${c.s}</strong><br><span style="color:#a3a3a3">bachelor's+:</span> <strong>${v}%</strong>`)
      })
  }
}

// --------------------------------------------------------- hex-bin-map
// Use the same hex grid; make each state uniformly-weighted visually
// and color-encode a different metric.
export function renderHexBinMapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const margin = {
    CA: +23, OR: +13, WA: +17, NV: +3,  UT: -22, AZ: -1, CO: +9, NM: +5, MT: -18, ID: -30, WY: -40,
    ND: -33, SD: -28, NE: -20, KS: -16, OK: -33, TX: -12, LA: -21, AR: -27, MS: -18, AL: -25,
    MN: +5, IA: -7, MO: -18, WI: +0.5, IL: +12, MI: +1, IN: -18, KY: -25, TN: -24, GA: -2,
    FL: -13, OH: -11, PA: -1, NY: +14, NJ: +6, CT: +13, RI: +14, MA: +25, ME: +7, VT: +35,
    NH: +4, VA: +6, WV: -42, NC: -3, SC: -18, DC: +80, DE: +13, MD: +30, HI: +25, AK: -14,
  }
  const W = 620, H = 360
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const color = d3.scaleDiverging()
    .domain([-45, 0, 45]).interpolator(d3.interpolateRdBu)

  const { cells } = drawHexUS(svg, { W, H, cellFn: s => {
    const v = margin[s]
    if (v == null) return { fill: '#262626', textColor: '#555' }
    const c = d3.color(color(v))
    const lightness = c.r * 0.299 + c.g * 0.587 + c.b * 0.114
    return { fill: color(v), textColor: lightness > 140 ? '#0a0a0a' : '#f5f5f5' }
  } })
  const legX = 20, legY = H - 28
  svg.append('text').attr('x', legX).attr('y', legY - 2)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em')
    .text('2024 MARGIN')
  const steps = 30
  for (let i = 0; i < steps; i++) {
    svg.append('rect')
      .attr('x', legX + i * 5).attr('y', legY + 6).attr('width', 5).attr('height', 10)
      .attr('fill', color(-45 + 90 * i / (steps - 1)))
  }
  svg.append('text').attr('x', legX).attr('y', legY + 28).attr('fill', COLORS.label).attr('font-size', 9).text('R+45')
  svg.append('text').attr('x', legX + steps * 5).attr('y', legY + 28).attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 9).text('D+45')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals exact margin)
  const tip = createTooltip(container, { className: 'hexbin-tip' })
  for (const c of cells) {
    const v = margin[c.s]
    const body = v == null
      ? '<span style="color:#737373">no data</span>'
      : `<span style="color:#a3a3a3">2024 margin:</span> <strong>${v > 0 ? 'D+' : 'R+'}${Math.abs(v)}</strong>`
    c.path.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        c.path.attr('stroke', '#f5f5f5').attr('stroke-width', 1.8)
        tip.show(event.pageX, event.pageY, `<strong>${c.s}</strong><br>${body}`)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, `<strong>${c.s}</strong><br>${body}`) })
      .on('mouseleave', () => {
        c.path.attr('stroke', c.opts.stroke || '#0a0a0a').attr('stroke-width', 1)
        tip.hide()
      })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, `<strong>${c.s}</strong><br>${body}`) })
  }
}

// --------------------------------------------------------- cartogram (Dorling-style)
export function renderCartogramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // State population-sized circles placed at roughly-geographic positions
  const pop = {
    CA: 39, TX: 30, FL: 22, NY: 19, PA: 13, IL: 12, OH: 12, GA: 11, NC: 11, MI: 10,
    NJ:  9, VA:  9, WA:  8, AZ:  7, TN:  7, MA:  7, IN:  7, MD:  6, MO:  6, WI:  6,
    CO:  6, MN:  6, SC:  5, AL:  5, LA:  5, KY:  4, OR:  4, OK:  4, CT:  4, UT:  3,
    IA:  3, NV:  3, AR:  3, MS:  3, KS:  3, NM:  2, NE:  2, ID:  2, WV:  2, HI:  1,
    NH:  1, ME:  1, MT:  1, RI:  1, DE:  1, SD:  1, ND:  1, AK:  0.7, VT:  0.65, WY: 0.58,
    DC: 0.7,
  }
  const W = 620, H = 380
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // DECODER STRIP — the cartogram trades geography for magnitude
  const dy = 8, dH = 46
  svg.append('rect').attr('x', 20).attr('y', dy)
    .attr('width', W - 40).attr('height', dH)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', 28).attr('y', dy + 11)
    .attr('fill', '#93c5fd').attr('font-size', 8).attr('letter-spacing', '0.1em').text('DECODER')

  // Small circle + big circle + labels
  const cRow = dy + dH / 2 + 2
  svg.append('circle').attr('cx', 75).attr('cy', cRow).attr('r', 4)
    .attr('fill', '#8b5cf6').attr('fill-opacity', 0.82)
  svg.append('text').attr('x', 85).attr('y', cRow + 3)
    .attr('fill', COLORS.label).attr('font-size', 9).text('small pop')
  svg.append('circle').attr('cx', 175).attr('cy', cRow).attr('r', 14)
    .attr('fill', '#f59e0b').attr('fill-opacity', 0.82)
  svg.append('text').attr('x', 194).attr('y', cRow + 3)
    .attr('fill', COLORS.label).attr('font-size', 9).text('big pop')
  // Encoding
  svg.append('text').attr('x', 250).attr('y', cRow - 5)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('font-weight', 600)
    .text('circle area = population (sqrt-scaled radius)')
  svg.append('text').attr('x', 250).attr('y', cRow + 7)
    .attr('fill', COLORS.label).attr('font-size', 9)
    .text('position ≈ geography; overlap resolved by collision')
  // Warning about what the form trades away
  svg.append('text').attr('x', 250).attr('y', cRow + 19)
    .attr('fill', COLORS.warm).attr('font-size', 9).attr('font-style', 'italic')
    .text('shape is NOT geography — reach for it when land area would lie')

  // Rough positions per state (approximate lat/lon centroid)
  const posLonLat = {
    AL:[-86.8,32.8], AK:[-152,63], AZ:[-112,34], AR:[-92,34.9], CA:[-119.7,36.7],
    CO:[-105.5,39], CT:[-72.7,41.6], DE:[-75.5,39], FL:[-81.5,27.7], GA:[-83.6,32.7],
    HI:[-155.5,20], ID:[-114.4,44], IL:[-89.2,40], IN:[-86.3,39.8], IA:[-93.5,42],
    KS:[-98.5,38.5], KY:[-84.9,37.8], LA:[-92,31.2], ME:[-69.4,45.4], MD:[-76.8,39.1],
    MA:[-71.8,42.3], MI:[-84.5,44.3], MN:[-94.3,46.3], MS:[-89.7,32.7], MO:[-92.5,38.5],
    MT:[-110,47], NE:[-99.8,41.5], NV:[-116.8,39.3], NH:[-71.6,43.7], NJ:[-74.7,40.3],
    NM:[-106.1,34.5], NY:[-75.5,42.9], NC:[-79.8,35.6], ND:[-100.5,47.5], OH:[-82.7,40.3],
    OK:[-97.5,35.6], OR:[-120.6,44], PA:[-77.5,40.9], RI:[-71.5,41.7], SC:[-80.9,33.8],
    SD:[-99.9,44.3], TN:[-86.7,35.8], TX:[-99,31.5], UT:[-111.9,39.3], VT:[-72.7,44],
    VA:[-78.2,37.8], WA:[-120.4,47.4], WV:[-80.9,38.5], WI:[-89.6,44.3], WY:[-107.3,43],
    DC:[-77,38.9],
  }
  const mapTop = dy + dH + 10
  const proj = projConus(W, H - mapTop, { padX: 30, padY: 26 })
  // Circles sized by area-proportional radius
  const rScale = d3.scaleSqrt().domain([0, 40]).range([0, 34])
  const palette = d3.scaleSequential(d3.interpolatePlasma).domain([0, 40])

  // Use force simulation to nudge overlapping circles apart (Dorling-style)
  const nodes = Object.entries(pop).map(([s, v]) => {
    if (!posLonLat[s]) return null
    const [x0, y0raw] = proj(posLonLat[s])
    const y0 = y0raw + mapTop
    return { s, v, x: x0, y: y0, x0, y0, r: rScale(v) + 0.5 }
  }).filter(Boolean)
  const sim = d3.forceSimulation(nodes)
    .force('x', d3.forceX(d => d.x0).strength(0.3))
    .force('y', d3.forceY(d => d.y0).strength(0.3))
    .force('collide', d3.forceCollide(d => d.r + 0.5).iterations(3))
    .stop()
  for (let i = 0; i < 160; i++) sim.tick()

  svg.append('rect').attr('x', 15).attr('y', mapTop)
    .attr('width', W - 30).attr('height', H - mapTop - 15)
    .attr('fill', 'none').attr('stroke', '#1a1a1a').attr('stroke-dasharray', '3 4')

  for (const n of nodes) {
    n.circle = svg.append('circle').attr('class', 'cartogram-node').attr('data-state', n.s)
      .attr('cx', n.x).attr('cy', n.y).attr('r', n.r)
      .attr('fill', palette(n.v)).attr('fill-opacity', 0.82).attr('stroke', '#0a0a0a').attr('stroke-width', 0.8)
    if (n.r > 12) {
      svg.append('text').attr('x', n.x).attr('y', n.y + 3.5)
        .attr('text-anchor', 'middle').attr('fill', '#0a0a0a').attr('font-size', 9)
        .attr('font-weight', 600).attr('pointer-events', 'none').text(n.s)
    }
  }
  svg.append('text').attr('x', 20).attr('y', H - 4)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em')
    .text('STATE POPULATION · circles sized by millions')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals state + population)
  const tip = createTooltip(container, { className: 'cartogram-tip' })
  for (const n of nodes) {
    const body = `<span style="color:#a3a3a3">pop:</span> <strong>${n.v}M</strong>`
    n.circle.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        n.circle.attr('stroke', '#f5f5f5').attr('stroke-width', 1.8)
        tip.show(event.pageX, event.pageY, `<strong>${n.s}</strong><br>${body}`)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, `<strong>${n.s}</strong><br>${body}`) })
      .on('mouseleave', () => {
        n.circle.attr('stroke', '#0a0a0a').attr('stroke-width', 0.8)
        tip.hide()
      })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, `<strong>${n.s}</strong><br>${body}`) })
  }
}

// --------------------------------------------------------- proportional-symbol-map
export function renderProportionalSymbolMapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Metro areas sized by 2020 population (approximate, in millions)
  const metros = [
    { id: 'NYC', lat: 40.71, lon: -74.0,   v: 19.3 },
    { id: 'LA',  lat: 34.05, lon: -118.24, v: 13.2 },
    { id: 'CHI', lat: 41.88, lon: -87.63,  v:  9.5 },
    { id: 'DAL', lat: 32.78, lon: -96.80,  v:  7.6 },
    { id: 'HOU', lat: 29.76, lon: -95.37,  v:  7.1 },
    { id: 'DC',  lat: 38.90, lon: -77.04,  v:  6.3 },
    { id: 'MIA', lat: 25.76, lon: -80.19,  v:  6.1 },
    { id: 'PHI', lat: 39.95, lon: -75.17,  v:  6.1 },
    { id: 'ATL', lat: 33.75, lon: -84.39,  v:  6.1 },
    { id: 'BOS', lat: 42.36, lon: -71.06,  v:  4.9 },
    { id: 'SF',  lat: 37.77, lon: -122.42, v:  4.7 },
    { id: 'PHX', lat: 33.45, lon: -112.07, v:  4.9 },
    { id: 'RVR', lat: 33.95, lon: -117.40, v:  4.7 },
    { id: 'DET', lat: 42.33, lon: -83.05,  v:  4.4 },
    { id: 'SEA', lat: 47.60, lon: -122.33, v:  4.0 },
    { id: 'MIN', lat: 44.98, lon: -93.27,  v:  3.7 },
    { id: 'SD',  lat: 32.72, lon: -117.16, v:  3.3 },
    { id: 'TPA', lat: 27.95, lon: -82.46,  v:  3.2 },
    { id: 'DEN', lat: 39.74, lon: -104.99, v:  3.0 },
    { id: 'STL', lat: 38.63, lon: -90.20,  v:  2.8 },
    { id: 'BAL', lat: 39.29, lon: -76.61,  v:  2.8 },
    { id: 'CLT', lat: 35.23, lon: -80.84,  v:  2.7 },
    { id: 'ORL', lat: 28.54, lon: -81.38,  v:  2.7 },
    { id: 'SAT', lat: 29.42, lon: -98.49,  v:  2.6 },
    { id: 'POR', lat: 45.52, lon: -122.68, v:  2.5 },
    { id: 'AUS', lat: 30.27, lon: -97.74,  v:  2.4 },
    { id: 'PIT', lat: 40.44, lon: -79.99,  v:  2.3 },
    { id: 'SAC', lat: 38.58, lon: -121.49, v:  2.4 },
    { id: 'LV',  lat: 36.17, lon: -115.14, v:  2.3 },
  ]
  const W = 620, H = 320
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    .style('background', '#0a0a0a')
  const proj = projConus(W, H, { padX: 30, padY: 30 })
  svg.append('rect').attr('x', 15).attr('y', 15)
    .attr('width', W - 30).attr('height', H - 30)
    .attr('fill', 'none').attr('stroke', '#1a1a1a').attr('stroke-dasharray', '3 4')
  // Area-scaled radius
  const rScale = d3.scaleSqrt().domain([0, d3.max(metros, m => m.v)]).range([0, 24])
  // Draw from largest to smallest so smaller dots stay on top? Actually from smallest to largest
  // so big blobs surround smaller ones visibly.
  const sorted = [...metros].sort((a, b) => b.v - a.v)
  const circleRefs = []
  for (const m of sorted) {
    const [cx, cy] = proj([m.lon, m.lat])
    const c = svg.append('circle').attr('class', 'prop-symbol').attr('data-id', m.id)
      .attr('cx', cx).attr('cy', cy).attr('r', rScale(m.v))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.32)
      .attr('stroke', COLORS.accent).attr('stroke-width', 0.8)
    circleRefs.push({ m, cx, cy, circle: c })
  }
  // Label the biggest 5
  for (const m of sorted.slice(0, 5)) {
    const [cx, cy] = proj([m.lon, m.lat])
    svg.append('text').attr('x', cx).attr('y', cy - rScale(m.v) - 3)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 9)
      .attr('font-weight', 600).attr('pointer-events', 'none').text(m.id)
  }
  // Legend (nested circles) — placed in bottom-left corner so it doesn't
  // fall off the SVG's right edge
  const legX = 50, legY = H - 24
  svg.append('text').attr('x', legX).attr('y', legY - rScale(19) * 2 - 6)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em').text('METRO POP (M)')
  for (const ref of [4, 10, 19]) {
    const r = rScale(ref)
    svg.append('circle').attr('cx', legX).attr('cy', legY - r)
      .attr('r', r).attr('fill', 'none').attr('stroke', COLORS.accent).attr('stroke-opacity', 0.8)
    svg.append('text').attr('x', legX + 30).attr('y', legY - 2 * r + 5)
      .attr('fill', COLORS.label).attr('font-size', 9).text(`${ref}`)
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals metro + population)
  // Voronoi-backed nearest-center lookup: hovering inside a big circle
  // attributes to the big circle's metro even when smaller circles overlay
  // it in draw order. Avoids "hovering NYC gives you Philadelphia" bugs.
  const tip = createTooltip(container, { className: 'prop-symbol-tip' })
  const points = circleRefs.map(r => ({ ref: r, cx: r.cx, cy: r.cy }))
  const delaunay = d3.Delaunay.from(points, p => p.cx, p => p.cy)
  let hovered = null
  function setHover(idx) {
    if (hovered === idx) return
    if (hovered != null) circleRefs[hovered].circle.attr('fill-opacity', 0.32).attr('stroke-width', 0.8)
    hovered = idx
    if (idx != null) circleRefs[idx].circle.attr('fill-opacity', 0.55).attr('stroke-width', 1.6)
  }
  const overlay = svg.append('rect')
    .attr('x', 15).attr('y', 15).attr('width', W - 30).attr('height', H - 30)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  overlay.on('mousemove', function (event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    setHover(idx)
    const m = circleRefs[idx].m
    tip.show(event.pageX, event.pageY,
      `<strong>${m.id}</strong><br><span style="color:#a3a3a3">metro pop:</span> <strong>${m.v}M</strong>`)
  })
  overlay.on('mouseleave', () => { setHover(null); tip.hide() })
  overlay.on('click', function (event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    setHover(idx)
    const m = circleRefs[idx].m
    tip.show(event.pageX, event.pageY,
      `<strong>${m.id}</strong><br><span style="color:#a3a3a3">metro pop:</span> <strong>${m.v}M</strong>`)
  })
}

// --------------------------------------------------------- flow-map
export function renderFlowMapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const metros = [
    { id: 'SF',  lat: 37.77, lon: -122.42 },
    { id: 'LA',  lat: 34.05, lon: -118.24 },
    { id: 'SEA', lat: 47.60, lon: -122.33 },
    { id: 'DEN', lat: 39.74, lon: -104.99 },
    { id: 'AUS', lat: 30.27, lon:  -97.74 },
    { id: 'CHI', lat: 41.88, lon:  -87.63 },
    { id: 'NYC', lat: 40.71, lon:  -74.00 },
    { id: 'MIA', lat: 25.76, lon:  -80.19 },
  ]
  const flows = [
    { from: 'SF',  to: 'AUS', v: 16 },
    { from: 'SF',  to: 'SEA', v: 11 },
    { from: 'SF',  to: 'LA',  v:  9 },
    { from: 'LA',  to: 'AUS', v: 22 },
    { from: 'LA',  to: 'DEN', v:  8 },
    { from: 'NYC', to: 'MIA', v: 25 },
    { from: 'NYC', to: 'AUS', v: 10 },
    { from: 'CHI', to: 'AUS', v:  7 },
    { from: 'CHI', to: 'DEN', v:  9 },
    { from: 'SEA', to: 'DEN', v:  5 },
  ]
  const W = 620, H = 320
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    .style('background', '#0a0a0a')
  const proj = projConus(W, H, { padX: 20, padY: 20 })
  svg.append('rect').attr('x', 20).attr('y', 20)
    .attr('width', W - 40).attr('height', H - 40)
    .attr('fill', 'none').attr('stroke', '#262626').attr('stroke-dasharray', '3 4')

  const byId = Object.fromEntries(metros.map(m => [m.id, m]))
  const wScale = d3.scaleLinear().domain([0, d3.max(flows, d => d.v)]).range([1, 6])

  const flowPaths = svg.append('g').attr('class', 'flow-paths')
    .selectAll('path').data(flows).join('path')
    .attr('class', 'flow-path')
    .attr('data-from', d => d.from).attr('data-to', d => d.to)
    .attr('d', d => {
      const a = proj([byId[d.from].lon, byId[d.from].lat])
      const b = proj([byId[d.to].lon, byId[d.to].lat])
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2
      const dx = b[0] - a[0], dy = b[1] - a[1]
      const len = Math.hypot(dx, dy) || 1
      const off = Math.min(60, len * 0.2)
      const cx = mx + -dy / len * off
      const cy = my + dx / len * off
      return `M ${a[0]} ${a[1]} Q ${cx} ${cy} ${b[0]} ${b[1]}`
    })
    .attr('fill', 'none').attr('stroke', COLORS.good).attr('stroke-opacity', 0.6)
    .attr('stroke-linecap', 'round').attr('stroke-width', d => wScale(d.v))

  // Arrowheads
  svg.append('g').selectAll('polygon').data(flows).join('polygon')
    .attr('points', d => {
      const a = proj([byId[d.from].lon, byId[d.from].lat])
      const b = proj([byId[d.to].lon, byId[d.to].lat])
      const t = 0.72
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2
      const dx = b[0] - a[0], dy = b[1] - a[1]
      const len = Math.hypot(dx, dy) || 1
      const off = Math.min(60, len * 0.2)
      const cx = mx + -dy / len * off
      const cy = my + dx / len * off
      const px = (1 - t) * (1 - t) * a[0] + 2 * (1 - t) * t * cx + t * t * b[0]
      const py = (1 - t) * (1 - t) * a[1] + 2 * (1 - t) * t * cy + t * t * b[1]
      const tx = 2 * (1 - t) * (cx - a[0]) + 2 * t * (b[0] - cx)
      const ty = 2 * (1 - t) * (cy - a[1]) + 2 * t * (b[1] - cy)
      const tlen = Math.hypot(tx, ty) || 1
      const ux = tx / tlen, uy = ty / tlen
      const size = 4 + wScale(d.v) * 0.4
      return [
        [px + ux * size, py + uy * size],
        [px - ux * size * 0.3 - uy * size * 0.55, py - uy * size * 0.3 + ux * size * 0.55],
        [px - ux * size * 0.3 + uy * size * 0.55, py - uy * size * 0.3 - ux * size * 0.55],
      ].map(p => p.join(',')).join(' ')
    })
    .attr('fill', COLORS.good).attr('fill-opacity', 0.85)

  svg.append('g').selectAll('circle').data(metros).join('circle')
    .attr('cx', d => proj([d.lon, d.lat])[0]).attr('cy', d => proj([d.lon, d.lat])[1])
    .attr('r', 3.5).attr('fill', '#fafafa').attr('stroke', '#0a0a0a')
    .attr('pointer-events', 'none')
  svg.append('g').selectAll('text').data(metros).join('text')
    .attr('x', d => proj([d.lon, d.lat])[0] + 6)
    .attr('y', d => proj([d.lon, d.lat])[1] + 3.5)
    .attr('fill', COLORS.text).attr('font-size', 10).attr('pointer-events', 'none').text(d => d.id)

  if (!interactive) return

  // INTERACTIVE (P10: hover a flow curve — reveals origin/destination/volume)
  const tip = createTooltip(container, { className: 'flow-map-tip' })
  flowPaths.each(function (d) {
    const path = d3.select(this)
    const body = `<span style="color:#a3a3a3">${d.from} → ${d.to}:</span> <strong>${d.v}</strong> <span style="color:#737373">k migrants/yr</span>`
    path.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        // P7: fade others, foreground this one
        flowPaths.attr('stroke-opacity', f => f === d ? 1 : 0.12)
        path.attr('stroke-width', wScale(d.v) + 1.5)
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', function () {
        flowPaths.attr('stroke-opacity', 0.6)
        path.attr('stroke-width', wScale(d.v))
        tip.hide()
      })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  })
}

// --------------------------------------------------------- strip-plot (with beeswarm)
export function renderStripPlotDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Salaries for 4 roles (small sample each; 15-30 per group)
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(47)
  function sampleNormal(m, sd) {
    const z = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
    return Math.max(30, m + sd * z)
  }
  const groups = [
    { name: 'Junior',   m:  75, sd: 12, n: 18 },
    { name: 'Mid',      m: 110, sd: 18, n: 24 },
    { name: 'Senior',   m: 155, sd: 30, n: 20 },
    { name: 'Staff',    m: 210, sd: 45, n: 14 },
  ]
  for (const g of groups) {
    g.samples = Array.from({ length: g.n }, () => sampleNormal(g.m, g.sd))
  }

  // Interactive layout slider (omitted in static mode)
  const host = d3.select(container)
  let slider = null
  if (interactive) {
    slider = host.append('div').attr('class', 'demo-slider')
    slider.html(`
      <label for="strip-r">collide radius</label>
      <input id="strip-r" type="range" min="0" max="6" value="3.5" step="0.25" />
      <span class="val">3.5</span>
      <span class="hint">0 = raw (overplotted) / high = beeswarm layout</span>
    `)
  }
  const chartEl = host.append('div').node()
  const palette = ['#22d3ee', '#6366f1', '#f59e0b', '#f87171']

  function draw(collideR) {
    d3.select(chartEl).selectAll('*').remove()
    const W = 620, H = 280
    const margin = { top: 18, right: 20, bottom: 32, left: 80 }
    const svg = d3.select(chartEl).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const y = d3.scaleBand().domain(groups.map(g => g.name))
      .range([margin.top, H - margin.bottom]).padding(0.2)
    const x = d3.scaleLinear().domain([30, 300]).range([margin.left, W - margin.right])

    svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
      .call(d3.axisBottom(x).tickFormat(d => '$' + d + 'K').ticks(6))
      .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
    svg.append('g').selectAll('text.lab').data(groups).join('text').attr('class', 'lab')
      .attr('x', margin.left - 10).attr('y', d => y(d.name) + y.bandwidth() / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11)
      .text(d => d.name)

    for (let gi = 0; gi < groups.length; gi++) {
      const g = groups[gi]
      const yc = y(g.name) + y.bandwidth() / 2
      const nodes = g.samples.map(v => ({ v, x: x(v), y: yc }))
      if (collideR > 0.1) {
        const sim = d3.forceSimulation(nodes)
          .force('x', d3.forceX(d => x(d.v)).strength(0.9))
          .force('y', d3.forceY(yc).strength(0.03))
          .force('collide', d3.forceCollide(collideR).iterations(4))
          .stop()
        for (let i = 0; i < 70; i++) sim.tick()
      } else {
        // Raw overplotted — all points at y=yc exactly
        for (const n of nodes) { n.x = x(n.v); n.y = yc }
      }
      for (const n of nodes) {
        svg.append('circle').attr('cx', n.x).attr('cy', n.y)
          .attr('r', 3).attr('fill', palette[gi % palette.length]).attr('fill-opacity', 0.7)
      }
      const med = d3.quantile([...g.samples].sort(d3.ascending), 0.5)
      svg.append('line')
        .attr('x1', x(med)).attr('x2', x(med))
        .attr('y1', yc - y.bandwidth() / 2 + 4).attr('y2', yc + y.bandwidth() / 2 - 4)
        .attr('stroke', '#f5f5f5').attr('stroke-width', 1.5).attr('stroke-dasharray', '3 3')
    }
    svg.append('text').attr('x', W - margin.right).attr('y', margin.top - 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 10)
      .text('n = 76 · median shown as dashed line')
  }

  if (interactive) {
    const input = slider.select('input').node()
    const val = slider.select('.val').node()
    input.addEventListener('input', () => {
      val.textContent = (+input.value).toFixed(2)
      draw(+input.value)
    })
  }
  draw(3.5)
}

// --------------------------------------------------------- arc-diagram
export function renderArcDiagramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Characters in a novel, ordered by first appearance, with co-occurrence arcs
  const chars = ['Alice','Bob','Carl','Dana','Eve','Finn','Greta','Hank','Iris','Jack','Kate','Lou']
  const edges = [
    [0,1, 6], [0,2, 3], [0,3, 8], [0,7, 2], [0,10, 4],
    [1,2, 5], [1,4, 3], [1,5, 2],
    [2,5, 4], [2,6, 3], [2,8, 5],
    [3,4, 6], [3,7, 2],
    [4,6, 4], [4,9, 3],
    [5,6, 5], [5,8, 2],
    [6,9, 4], [6,11, 3],
    [7,10, 5], [7,11, 2],
    [8,9, 3], [8,11, 4],
    [9,10, 3],
    [10,11, 5],
  ]
  const W = 620, H = 300
  const margin = { top: 20, right: 30, bottom: 26, left: 30 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const x = d3.scalePoint().domain(d3.range(chars.length))
    .range([margin.left, W - margin.right])
  const yBase = H - margin.bottom

  // Arcs (draw first) — keep refs for hover
  const maxDist = chars.length - 1
  const wScale = d3.scaleLinear().domain([1, 8]).range([1, 3])
  const arcRefs = []
  for (const [a, b, v] of edges) {
    const x1 = x(a), x2 = x(b)
    const r = Math.abs(x2 - x1) / 2
    const dist = Math.abs(b - a)
    const color = d3.interpolateViridis(dist / maxDist)
    const path = svg.append('path').attr('class', 'arc-edge')
      .attr('data-a', a).attr('data-b', b)
      .attr('d', `M ${x1} ${yBase} A ${r} ${r} 0 0 1 ${x2} ${yBase}`)
      .attr('fill', 'none').attr('stroke', color).attr('stroke-opacity', 0.7)
      .attr('stroke-width', wScale(v))
    arcRefs.push({ a, b, v, path, color, width: wScale(v) })
  }
  svg.append('line').attr('x1', margin.left).attr('x2', W - margin.right)
    .attr('y1', yBase).attr('y2', yBase).attr('stroke', COLORS.grid)
  for (let i = 0; i < chars.length; i++) {
    svg.append('circle').attr('cx', x(i)).attr('cy', yBase).attr('r', 3.5)
      .attr('fill', '#f5f5f5').attr('stroke', '#0a0a0a')
    svg.append('text').attr('x', x(i)).attr('y', yBase + 16)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 10)
      .text(chars[i])
  }
  svg.append('text').attr('x', margin.left).attr('y', margin.top)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.1em')
    .text('CHARACTER CO-OCCURRENCE · ordered by first appearance')

  if (!interactive) return

  // INTERACTIVE (P10: hover an arc to reveal its pair + co-occurrence count)
  const tip = createTooltip(container, { className: 'arc-tip' })
  for (const ref of arcRefs) {
    const body = `<strong>${chars[ref.a]} ↔ ${chars[ref.b]}</strong><br>` +
      `<span style="color:#a3a3a3">co-occurrences:</span> <strong>${ref.v}</strong> ` +
      `<span style="color:#737373">· distance ${Math.abs(ref.b - ref.a)}</span>`
    ref.path.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        arcRefs.forEach(r => r.path.attr('stroke-opacity', r === ref ? 1 : 0.1))
        ref.path.attr('stroke-width', ref.width + 1.5)
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', function () {
        arcRefs.forEach(r => r.path.attr('stroke-opacity', 0.7))
        ref.path.attr('stroke-width', ref.width)
        tip.hide()
      })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- network-diagram
export function renderNetworkDiagramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Synthetic collaboration network with 3 clusters
  const clusters = [
    { name: 'design',  n: 6 },
    { name: 'engineering', n: 7 },
    { name: 'research', n: 5 },
  ]
  let id = 0
  const nodes = []
  for (const c of clusters) {
    for (let i = 0; i < c.n; i++) {
      nodes.push({ id: id++, cluster: c.name, label: c.name[0] + i })
    }
  }
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(53)
  const links = []
  // Dense within cluster
  for (const c of clusters) {
    const members = nodes.filter(n => n.cluster === c.name)
    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        if (rng() < 0.55) links.push({ source: members[i].id, target: members[j].id, inter: false })
      }
    }
  }
  // Sparse between clusters
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      if (nodes[i].cluster !== nodes[j].cluster && rng() < 0.06) {
        links.push({ source: nodes[i].id, target: nodes[j].id, inter: true })
      }
    }
  }

  const W = 620, H = 320
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const color = d3.scaleOrdinal().domain(clusters.map(c => c.name))
    .range([COLORS.accent, COLORS.good, COLORS.warm])
  // Make links use node references
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]))
  for (const l of links) { l.source = byId[l.source]; l.target = byId[l.target] }

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).distance(35).strength(l => l.inter ? 0.1 : 0.9))
    .force('charge', d3.forceManyBody().strength(-80))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .force('collide', d3.forceCollide(10))
    .stop()
  for (let i = 0; i < 250; i++) sim.tick()
  // Clamp inside
  for (const n of nodes) {
    n.x = Math.max(20, Math.min(W - 20, n.x))
    n.y = Math.max(20, Math.min(H - 20, n.y))
  }

  const linkSel = svg.append('g').selectAll('line').data(links).join('line')
    .attr('class', 'net-link')
    .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    .attr('stroke', d => d.inter ? COLORS.mute : '#3f3f3f')
    .attr('stroke-opacity', d => d.inter ? 0.7 : 0.5)
    .attr('stroke-width', d => d.inter ? 1 : 0.8)

  const nodeSel = svg.append('g').selectAll('circle').data(nodes).join('circle')
    .attr('class', 'net-node').attr('data-id', d => d.id)
    .attr('cx', d => d.x).attr('cy', d => d.y).attr('r', 8)
    .attr('fill', d => color(d.cluster)).attr('fill-opacity', 0.85)
    .attr('stroke', '#0a0a0a').attr('stroke-width', 1)
  svg.append('g').selectAll('text').data(nodes).join('text')
    .attr('x', d => d.x).attr('y', d => d.y + 3)
    .attr('text-anchor', 'middle').attr('fill', '#0a0a0a').attr('pointer-events', 'none')
    .attr('font-size', 8).attr('font-weight', 600).text(d => d.label)

  let lx = 20
  for (const c of clusters) {
    svg.append('circle').attr('cx', lx + 5).attr('cy', H - 10).attr('r', 5).attr('fill', color(c.name))
    svg.append('text').attr('x', lx + 14).attr('y', H - 7)
      .attr('fill', COLORS.label).attr('font-size', 10).text(c.name)
    lx += 14 + c.name.length * 7 + 16
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover a node — highlight it + its edges + neighbors,
  // fade everything else; tooltip shows degree + cluster)
  const tip = createTooltip(container, { className: 'net-tip' })
  // Build adjacency once
  const adjacency = new Map()
  for (const n of nodes) adjacency.set(n.id, new Set([n.id]))
  for (const l of links) {
    adjacency.get(l.source.id).add(l.target.id)
    adjacency.get(l.target.id).add(l.source.id)
  }
  function degree(nodeId) {
    return [...adjacency.get(nodeId)].length - 1  // minus self
  }
  function spotlight(node) {
    const neighbors = adjacency.get(node.id)
    nodeSel.attr('fill-opacity', n => neighbors.has(n.id) ? 1 : 0.12)
      .attr('stroke', n => n.id === node.id ? '#f5f5f5' : '#0a0a0a')
      .attr('stroke-width', n => n.id === node.id ? 2 : 1)
    linkSel.attr('stroke-opacity', l =>
      (l.source.id === node.id || l.target.id === node.id)
        ? (l.inter ? 0.95 : 0.9) : 0.05)
      .attr('stroke-width', l =>
        (l.source.id === node.id || l.target.id === node.id)
          ? (l.inter ? 1.6 : 1.4) : (l.inter ? 1 : 0.8))
  }
  function clearSpotlight() {
    nodeSel.attr('fill-opacity', 0.85).attr('stroke', '#0a0a0a').attr('stroke-width', 1)
    linkSel.attr('stroke-opacity', d => d.inter ? 0.7 : 0.5)
      .attr('stroke-width', d => d.inter ? 1 : 0.8)
  }
  nodeSel.style('cursor', 'pointer')
    .on('mouseenter', function (event, d) {
      spotlight(d)
      const body = `<strong>${d.label}</strong> <span style="color:#737373">· ${d.cluster}</span><br>` +
        `<span style="color:#a3a3a3">connections:</span> <strong>${degree(d.id)}</strong>`
      tip.show(event.pageX, event.pageY, body)
    })
    .on('mousemove', function (event, d) {
      const body = `<strong>${d.label}</strong> <span style="color:#737373">· ${d.cluster}</span><br>` +
        `<span style="color:#a3a3a3">connections:</span> <strong>${degree(d.id)}</strong>`
      tip.show(event.pageX, event.pageY, body)
    })
    .on('mouseleave', () => { clearSpotlight(); tip.hide() })
    .on('click', function (event, d) {
      event.stopPropagation()
      spotlight(d)
      const body = `<strong>${d.label}</strong> <span style="color:#737373">· ${d.cluster}</span><br>` +
        `<span style="color:#a3a3a3">connections:</span> <strong>${degree(d.id)}</strong>`
      tip.show(event.pageX, event.pageY, body)
    })
}

// --------------------------------------------------------- matrix-plot
export function renderMatrixPlotDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const rowNames = ['N. America', 'S. America', 'Europe', 'Africa', 'Asia', 'Oceania']
  const colNames = ['N.Am', 'S.Am', 'Eur', 'Afr', 'Asia', 'Oce']
  const names = rowNames
  const matrix = [
    [  0, 180, 320,  40, 260,  30],
    [180,   0, 140,  10,  60,   5],
    [320, 140,   0, 220, 400,  20],
    [ 40,  10, 220,   0, 110,   3],
    [260,  60, 400, 110,   0, 180],
    [ 30,   5,  20,   3, 180,   0],
  ]
  const W = 620, H = 360
  const margin = { top: 64, right: 250, bottom: 18, left: 100 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const cw = Math.min((W - margin.left - margin.right) / names.length,
                     (H - margin.top - margin.bottom) / names.length)
  const maxV = d3.max(matrix.flat())
  const color = d3.scaleSequential(d3.interpolateYlOrBr).domain([0, maxV])
  // Decoder panel to the right of the matrix
  const dx = W - 240, dy = 70
  svg.append('rect').attr('x', dx).attr('y', dy).attr('width', 230).attr('height', 76)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', dx + 115).attr('y', dy + 13)
    .attr('text-anchor', 'middle').attr('fill', '#93c5fd').attr('font-size', 8)
    .attr('letter-spacing', '0.1em').text('DECODER')
  // Mini 3×3 matrix
  const mx = dx + 10, my = dy + 22
  const mc = 12
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 3; c++) {
      if (r === c) {
        svg.append('rect').attr('x', mx + c * mc).attr('y', my + r * mc).attr('width', mc).attr('height', mc)
          .attr('fill', '#111').attr('stroke', '#262626')
        svg.append('line').attr('x1', mx + c * mc).attr('y1', my + r * mc)
          .attr('x2', mx + c * mc + mc).attr('y2', my + r * mc + mc).attr('stroke', '#333')
      } else {
        svg.append('rect').attr('x', mx + c * mc).attr('y', my + r * mc).attr('width', mc).attr('height', mc)
          .attr('fill', color(maxV * (0.3 + Math.abs(r - c) * 0.2))).attr('fill-opacity', 0.8)
      }
    }
  }
  svg.append('text').attr('x', mx + 46).attr('y', my + 10)
    .attr('fill', COLORS.label).attr('font-size', 9).text('rows = cols = same set')
  svg.append('text').attr('x', mx + 46).attr('y', my + 22)
    .attr('fill', COLORS.label).attr('font-size', 9).text('diagonal = self-loop')
  svg.append('text').attr('x', mx + 46).attr('y', my + 34)
    .attr('fill', COLORS.label).attr('font-size', 9).text('color = pair weight')

  const cells = []
  for (let r = 0; r < names.length; r++) {
    for (let c = 0; c < names.length; c++) {
      const v = matrix[r][c]
      const cx = margin.left + c * cw
      const cy = margin.top + r * cw
      if (r === c) {
        svg.append('rect').attr('x', cx).attr('y', cy).attr('width', cw).attr('height', cw)
          .attr('fill', '#111').attr('stroke', '#262626')
        svg.append('line').attr('x1', cx).attr('y1', cy).attr('x2', cx + cw).attr('y2', cy + cw)
          .attr('stroke', '#262626')
      } else {
        const rect = svg.append('rect').attr('class', 'mp-cell').attr('data-rc', `${r}-${c}`)
          .attr('x', cx).attr('y', cy).attr('width', cw).attr('height', cw)
          .attr('fill', color(v)).attr('stroke', '#0a0a0a')
        if (v > 100) {
          svg.append('text').attr('x', cx + cw / 2).attr('y', cy + cw / 2 + 3)
            .attr('text-anchor', 'middle').attr('fill', v > maxV / 2 ? '#0a0a0a' : '#e5e5e5')
            .attr('pointer-events', 'none').attr('font-size', 10).text(v)
        }
        cells.push({ r, c, v, rect, x: cx, y: cy })
      }
    }
  }
  for (let r = 0; r < names.length; r++) {
    svg.append('text').attr('x', margin.left - 8).attr('y', margin.top + r * cw + cw / 2 + 4)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 11).text(names[r])
  }
  for (let c = 0; c < names.length; c++) {
    const tx = margin.left + c * cw + cw / 2
    svg.append('text').attr('x', tx).attr('y', margin.top - 8)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 10).text(colNames[c])
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals cross-hair row/col + exact value)
  const crossRow = svg.append('rect').attr('class', 'mp-cross-row')
    .attr('x', margin.left).attr('width', names.length * cw)
    .attr('height', cw).attr('fill', 'none').attr('stroke', '#f5f5f5')
    .attr('stroke-width', 1).attr('stroke-opacity', 0).style('pointer-events', 'none')
  const crossCol = svg.append('rect').attr('class', 'mp-cross-col')
    .attr('y', margin.top).attr('height', names.length * cw)
    .attr('width', cw).attr('fill', 'none').attr('stroke', '#f5f5f5')
    .attr('stroke-width', 1).attr('stroke-opacity', 0).style('pointer-events', 'none')
  const tip = createTooltip(container, { className: 'matrix-plot-tip' })
  for (const cell of cells) {
    cell.rect.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        crossRow.attr('y', cell.y).attr('stroke-opacity', 0.6)
        crossCol.attr('x', cell.x).attr('stroke-opacity', 0.6)
        tip.show(event.pageX, event.pageY,
          `<strong>${names[cell.r]} → ${names[cell.c]}</strong><br>` +
          `<span style="color:#a3a3a3">flow:</span> <strong>${cell.v}</strong>`)
      })
      .on('mousemove', function (event) {
        tip.show(event.pageX, event.pageY,
          `<strong>${names[cell.r]} → ${names[cell.c]}</strong><br>` +
          `<span style="color:#a3a3a3">flow:</span> <strong>${cell.v}</strong>`)
      })
      .on('mouseleave', () => {
        crossRow.attr('stroke-opacity', 0); crossCol.attr('stroke-opacity', 0); tip.hide()
      })
      .on('click', function (event) {
        tip.show(event.pageX, event.pageY,
          `<strong>${names[cell.r]} → ${names[cell.c]}</strong><br>` +
          `<span style="color:#a3a3a3">flow:</span> <strong>${cell.v}</strong>`)
      })
  }
}

// --------------------------------------------------------- sunburst
export function renderSunburstDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const root = {
    name: 'Budget',
    children: [
      { name: 'Mandatory', children: [
        { name: 'Social Security', value: 1350 },
        { name: 'Medicare',        value:  980 },
        { name: 'Medicaid',        value:  580 },
        { name: 'Income Sec.',     value:  650 },
        { name: 'Veterans',        value:  270 },
      ] },
      { name: 'Discretionary', children: [
        { name: 'Defense',        value: 820 },
        { name: 'Education',      value: 150 },
        { name: 'Transportation', value: 130 },
        { name: 'Other',          value: 340 },
      ] },
      { name: 'Interest', value: 620 },
    ],
  }
  const W = 620, H = 380
  const HEADER = 30
  const r = 150
  const rootSvg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // Decoder panel (top-right, keeps top-left free for breadcrumb)
  const dx = W - 156, dy = HEADER + 6
  rootSvg.append('rect').attr('x', dx).attr('y', dy).attr('width', 144).attr('height', 78)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  rootSvg.append('text').attr('x', dx + 72).attr('y', dy + 13)
    .attr('text-anchor', 'middle').attr('fill', '#93c5fd').attr('font-size', 8)
    .attr('letter-spacing', '0.1em').text('DECODER')
  const mg = rootSvg.append('g').attr('transform', `translate(${dx + 24},${dy + 50})`)
  const innerArc = d3.arc().innerRadius(6).outerRadius(14).startAngle(-Math.PI * 0.8).endAngle(-Math.PI * 0.15)
  const outerArc = d3.arc().innerRadius(14).outerRadius(22).startAngle(-Math.PI * 0.8).endAngle(-Math.PI * 0.5)
  const outerArc2 = d3.arc().innerRadius(14).outerRadius(22).startAngle(-Math.PI * 0.5).endAngle(-Math.PI * 0.15)
  mg.append('path').attr('d', innerArc()).attr('fill', COLORS.accent).attr('fill-opacity', 0.7)
  mg.append('path').attr('d', outerArc()).attr('fill', COLORS.accent).attr('fill-opacity', 0.4)
  mg.append('path').attr('d', outerArc2()).attr('fill', COLORS.accent).attr('fill-opacity', 0.55)
  rootSvg.append('text').attr('x', dx + 56).attr('y', dy + 38)
    .attr('fill', COLORS.label).attr('font-size', 9).text('inner ring = parent')
  rootSvg.append('text').attr('x', dx + 56).attr('y', dy + 50)
    .attr('fill', COLORS.label).attr('font-size', 9).text('outer ring = children')
  rootSvg.append('text').attr('x', dx + 56).attr('y', dy + 62)
    .attr('fill', COLORS.label).attr('font-size', 9).text('angle = value')

  const topLevel = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value)
  const palette = d3.scaleOrdinal().range([COLORS.accent, COLORS.warm, COLORS.good, COLORS.purple])

  const breadcrumb = rootSvg.append('g').attr('class', 'sb-breadcrumb')
  const plotG = rootSvg.append('g').attr('class', 'sb-plot')
    .attr('transform', `translate(${W / 2 - 60}, ${HEADER + H / 2})`)
  // Offset center so the decoder panel doesn't crowd the circle.
  let focus = topLevel

  function render() {
    plotG.selectAll('*').remove()
    breadcrumb.selectAll('*').remove()

    const sub = focus.copy().sum(d => d.value).sort((a, b) => b.value - a.value)
    d3.partition().size([2 * Math.PI, r])(sub)
    const arc = d3.arc()
      .startAngle(d => d.x0).endAngle(d => d.x1)
      .innerRadius(d => d.y0).outerRadius(d => d.y1 - 1)

    // depth-0 of sub = focus itself, skip
    for (const d of sub.descendants().slice(1)) {
      // Family color: depth-1 within sub
      let top = d
      while (top.depth > 1) top = top.parent
      const isDrillable = interactive && d.children && d.depth === 1
      const g = plotG.append('g').style('cursor', isDrillable ? 'pointer' : 'default')
      g.append('path').attr('d', arc(d))
        .attr('fill', palette(top.data.name))
        .attr('fill-opacity', 0.72 - (d.depth - 1) * 0.15)
        .attr('stroke', '#0a0a0a').attr('stroke-width', 1)
      if ((d.x1 - d.x0) > 0.22) {
        const a = (d.x0 + d.x1) / 2 - Math.PI / 2
        const ry = (d.y0 + d.y1) / 2
        const flip = (d.x0 + d.x1) / 2 > Math.PI
        g.append('text')
          .attr('transform', `rotate(${a * 180 / Math.PI}) translate(${ry}) rotate(${flip ? 180 : 0})`)
          .attr('text-anchor', 'middle').attr('dy', '0.35em')
          .attr('fill', '#0a0a0a').attr('font-size', 9).attr('font-weight', 600)
          .text(d.data.name)
      }
      if (isDrillable) {
        g.on('click', (event) => {
          event.stopPropagation()
          const target = topLevel.descendants().find(n => n.data === d.data)
          if (target) { focus = target; render() }
        })
      }
    }

    // Center label: focus's name (and total). Clicking the center zooms out.
    const centerText = plotG.append('g').style('cursor', focus.parent ? 'pointer' : 'default')
    centerText.append('circle').attr('r', 36).attr('fill', '#0a0a0a').attr('fill-opacity', 0.85)
    centerText.append('text').attr('text-anchor', 'middle').attr('y', -4)
      .attr('fill', '#e5e5e5').attr('font-size', 11).attr('font-weight', 600)
      .text(focus.data.name)
    centerText.append('text').attr('text-anchor', 'middle').attr('y', 10)
      .attr('fill', COLORS.label).attr('font-size', 9)
      .text('$' + focus.value + 'B')
    if (interactive && focus.parent) {
      centerText.append('text').attr('text-anchor', 'middle').attr('y', 24)
        .attr('fill', '#6366f1').attr('font-size', 9).text('↑ back')
      centerText.on('click', (event) => {
        event.stopPropagation()
        focus = focus.parent; render()
      })
    }

    // Breadcrumb
    breadcrumb.append('rect').attr('x', 0).attr('y', 0).attr('width', W).attr('height', HEADER)
      .attr('fill', '#0a0a0a').attr('stroke', '#1f1f1f').attr('stroke-width', 0.5)
    const path = focus.ancestors().reverse()
    let cursor = 10
    path.forEach((node, i) => {
      if (i > 0) {
        breadcrumb.append('text').attr('x', cursor).attr('y', 19)
          .attr('fill', '#525252').attr('font-size', 11).text('›')
        cursor += 12
      }
      const isLast = i === path.length - 1
      const text = breadcrumb.append('text').attr('x', cursor).attr('y', 19)
        .attr('fill', isLast ? '#e5e5e5' : '#c7d2fe').attr('font-size', 11)
        .attr('font-weight', isLast ? 600 : 400)
        .text(node.data.name + (node.value != null ? ` · $${node.value}B` : ''))
      if (interactive && !isLast) {
        text.style('cursor', 'pointer')
          .on('click', (event) => { event.stopPropagation(); focus = node; render() })
      }
      cursor += text.node().getComputedTextLength() + 6
    })
    if (interactive) {
      breadcrumb.append('text').attr('x', W - 170).attr('y', 19)
        .attr('text-anchor', 'end').attr('fill', '#737373').attr('font-size', 9)
        .attr('font-style', 'italic')
        .text(focus.depth === 0 ? 'click a wedge to zoom in' : 'click center ↑ to zoom out')
    }
  }

  if (interactive) {
    rootSvg.on('click', () => {
      if (focus.parent) { focus = focus.parent; render() }
    })
  }
  render()
}

// --------------------------------------------------------- icicle-plot
export function renderIciclePlotDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const root = {
    name: 'Budget',
    children: [
      { name: 'Mandatory', children: [
        { name: 'Social Security', value: 1350 },
        { name: 'Medicare',        value:  980 },
        { name: 'Medicaid',        value:  580 },
        { name: 'Income Sec.',     value:  650 },
        { name: 'Veterans',        value:  270 },
      ] },
      { name: 'Discretionary', children: [
        { name: 'Defense',        value: 820 },
        { name: 'Education',      value: 150 },
        { name: 'Transportation', value: 130 },
        { name: 'Other',          value: 340 },
      ] },
      { name: 'Interest', value: 620 },
    ],
  }
  const W = 620, H = 310
  const HEADER = 30
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const topLevel = d3.hierarchy(root).sum(d => d.value).sort((a, b) => b.value - a.value)
  const palette = d3.scaleOrdinal()
    .domain(topLevel.children.map(c => c.data.name))
    .range([COLORS.accent, COLORS.warm, COLORS.good, COLORS.purple])

  const breadcrumb = svg.append('g').attr('class', 'ic-breadcrumb')
  const plotG = svg.append('g').attr('class', 'ic-plot')
  let focus = topLevel

  function render() {
    plotG.selectAll('*').remove()
    breadcrumb.selectAll('*').remove()
    const sub = focus.copy().sum(d => d.value).sort((a, b) => b.value - a.value)
    d3.partition().size([W, H - HEADER])(sub)

    for (const d of sub.descendants().slice(1)) {
      let top = d
      while (top.depth > 1) top = top.parent
      const isDrillable = interactive && d.children && d.depth === 1
      const g = plotG.append('g').style('cursor', isDrillable ? 'pointer' : 'default')
      g.append('rect')
        .attr('x', d.x0).attr('y', HEADER + d.y0)
        .attr('width', d.x1 - d.x0).attr('height', d.y1 - d.y0)
        .attr('fill', palette(top.data.name))
        .attr('fill-opacity', 0.78 - (d.depth - 1) * 0.16)
        .attr('stroke', '#0a0a0a').attr('stroke-width', 1)
      if ((d.x1 - d.x0) > 42) {
        g.append('text').attr('x', d.x0 + 6).attr('y', HEADER + d.y0 + 14)
          .attr('fill', '#0a0a0a').attr('font-size', 10).attr('font-weight', 600)
          .text(d.data.name + (isDrillable ? '  ↓' : ''))
      }
      if (isDrillable) {
        g.on('click', (event) => {
          event.stopPropagation()
          const target = topLevel.descendants().find(n => n.data === d.data)
          if (target) { focus = target; render() }
        })
      }
    }

    // Breadcrumb
    breadcrumb.append('rect').attr('x', 0).attr('y', 0).attr('width', W).attr('height', HEADER)
      .attr('fill', '#0a0a0a').attr('stroke', '#1f1f1f').attr('stroke-width', 0.5)
    const path = focus.ancestors().reverse()
    let cursor = 10
    path.forEach((node, i) => {
      if (i > 0) {
        breadcrumb.append('text').attr('x', cursor).attr('y', 19)
          .attr('fill', '#525252').attr('font-size', 11).text('›')
        cursor += 12
      }
      const isLast = i === path.length - 1
      const text = breadcrumb.append('text').attr('x', cursor).attr('y', 19)
        .attr('fill', isLast ? '#e5e5e5' : '#c7d2fe').attr('font-size', 11)
        .attr('font-weight', isLast ? 600 : 400)
        .text(node.data.name + (node.value != null ? ` · $${node.value}B` : ''))
      if (interactive && !isLast) {
        text.style('cursor', 'pointer')
          .on('click', (event) => { event.stopPropagation(); focus = node; render() })
      }
      cursor += text.node().getComputedTextLength() + 6
    })
    if (interactive) {
      breadcrumb.append('text').attr('x', W - 10).attr('y', 19)
        .attr('text-anchor', 'end').attr('fill', '#737373').attr('font-size', 9)
        .attr('font-style', 'italic')
        .text(focus.depth === 0 ? 'click a parent band to zoom in' : 'click breadcrumb or outside to zoom out')
    }
  }

  if (interactive) {
    svg.on('click', () => {
      if (focus.parent) { focus = focus.parent; render() }
    })
  }
  render()
}

// --------------------------------------------------------- stacked-area
export function renderStackedAreaDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Energy-source share over 20 years (synthetic, meaningful trends)
  const years = Array.from({ length: 20 }, (_, i) => 2006 + i)
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(61)
  const data = years.map((y, i) => {
    // Renewables rise; coal falls; gas grows; nuclear steady; hydro steady
    const coal = Math.max(1, 35 - i * 1.5) + (rng() - 0.5) * 1.5
    const gas = 20 + i * 0.8 + (rng() - 0.5) * 1.5
    const nuclear = 18 + (rng() - 0.5) * 0.8
    const hydro = 7 + (rng() - 0.5) * 0.5
    const wind = Math.min(18, i * 0.9) + (rng() - 0.5) * 0.8
    const solar = Math.min(14, Math.max(0, (i - 4) * 1.0)) + (rng() - 0.5) * 0.4
    return { year: y, Coal: coal, Gas: gas, Nuclear: nuclear, Hydro: hydro, Wind: wind, Solar: solar }
  })
  const keys = ['Coal', 'Gas', 'Nuclear', 'Hydro', 'Wind', 'Solar']
  const colors = {
    Coal: '#404040', Gas: COLORS.mute, Nuclear: COLORS.purple,
    Hydro: COLORS.accent, Wind: COLORS.good, Solar: COLORS.warm,
  }
  const W = 620, H = 260
  const margin = { top: 16, right: 80, bottom: 28, left: 40 }
  d3.select(container).style('position', 'relative')
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const stack = d3.stack().keys(keys)
  const series = stack(data)
  const x = d3.scaleLinear().domain([years[0], years[years.length - 1]])
    .range([margin.left, W - margin.right])
  const y = d3.scaleLinear()
    .domain([0, d3.max(series, s => d3.max(s, d => d[1]))])
    .range([H - margin.bottom, margin.top])

  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5).tickFormat(d => d))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(4).tickFormat(d => d + '%'))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  const area = d3.area()
    .x((_, i) => x(years[i])).y0(d => y(d[0])).y1(d => y(d[1]))
    .curve(d3.curveMonotoneX)
  svg.append('g').selectAll('path').data(series).join('path')
    .attr('d', area).attr('fill', d => colors[d.key])
    .attr('fill-opacity', 0.85)

  for (const s of series) {
    const last = s[s.length - 1]
    const ym = (y(last[0]) + y(last[1])) / 2
    svg.append('text').attr('x', W - margin.right + 6).attr('y', ym + 3)
      .attr('fill', colors[s.key]).attr('font-size', 11).attr('pointer-events', 'none').text(s.key)
  }

  if (!interactive) return

  // INTERACTIVE (P10: time-cursor reveals each layer's share at a year)
  const cursorG = svg.append('g').attr('class', 'sa-cursor')
    .style('opacity', 0).style('pointer-events', 'none')
  cursorG.append('line').attr('y1', margin.top).attr('y2', H - margin.bottom)
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1).attr('stroke-dasharray', '2 3')
  const yearLabel = cursorG.append('text').attr('y', margin.top - 4)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label)
    .attr('font-size', 10).attr('font-weight', 600)

  const tip = createTooltip(container, { className: 'sa-tip' })
  function update(pageX, pageY, event) {
    const [mx] = d3.pointer(event, svg.node())
    const yearF = x.invert(mx)
    const year = Math.max(years[0], Math.min(years[years.length - 1], Math.round(yearF)))
    const idx = year - years[0]
    cursorG.style('opacity', 1).select('line')
      .attr('x1', x(year)).attr('x2', x(year))
    yearLabel.attr('x', x(year)).text(year)
    const rows = keys
      .map(k => ({ k, v: data[idx][k], color: colors[k] }))
      .sort((a, b) => b.v - a.v)
    const html = `<div style="font-weight:600;margin-bottom:3px">${year}</div>` +
      rows.map(r =>
        `<div><span style="display:inline-block;width:8px;height:8px;background:${r.color};margin-right:5px;border-radius:2px;"></span>` +
        `<span style="color:#a3a3a3">${r.k}:</span> ${r.v.toFixed(1)}%</div>`).join('')
    tip.show(pageX, pageY, html)
  }
  const overlay = svg.append('rect')
    .attr('x', margin.left).attr('y', margin.top)
    .attr('width', W - margin.right - margin.left)
    .attr('height', H - margin.top - margin.bottom)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  overlay.on('mousemove', event => update(event.pageX, event.pageY, event))
  overlay.on('mouseleave', () => { cursorG.style('opacity', 0); tip.hide() })
  overlay.on('click', event => update(event.pageX, event.pageY, event))
}

// ============================================================
// Comparison cards — same data rendered in multiple forms.
// Each function takes the three sub-containers and renders mini
// versions of the form's chart into each.
// ============================================================

// -------- Distribution triad: histogram / boxplot / violin --------
// Same bimodal sample rendered three ways.
export function renderDistributionTriad(elHist, elBox, elViolin) {
  const rng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(67)
  function sampleNormal(m, sd) {
    const z = Math.sqrt(-2 * Math.log(rng())) * Math.cos(2 * Math.PI * rng())
    return m + sd * z
  }
  // Intentionally bimodal
  const samples = []
  for (let i = 0; i < 400; i++) {
    samples.push(sampleNormal(rng() < 0.55 ? 60 : 85, 8))
  }
  samples.sort(d3.ascending)

  function hist(el) {
    const W = 300, H = 180, m = { top: 10, right: 10, bottom: 24, left: 34 }
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const x = d3.scaleLinear().domain([30, 110]).range([m.left, W - m.right])
    const bins = d3.bin().domain(x.domain()).thresholds(22)(samples)
    const y = d3.scaleLinear().domain([0, d3.max(bins, b => b.length)]).nice()
      .range([H - m.bottom, m.top])
    svg.append('g').attr('transform', `translate(0,${H - m.bottom})`)
      .call(d3.axisBottom(x).ticks(4)).call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 9))
    svg.append('g').selectAll('rect').data(bins).join('rect')
      .attr('x', d => x(d.x0) + 1).attr('y', d => y(d.length))
      .attr('width', d => Math.max(0, x(d.x1) - x(d.x0) - 1))
      .attr('height', d => H - m.bottom - y(d.length))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.75)
    svg.append('text').attr('x', m.left).attr('y', m.top + 6)
      .attr('fill', COLORS.label).attr('font-size', 9).text('bimodal — two peaks visible')
  }

  function box(el) {
    const W = 300, H = 180, m = { top: 14, right: 16, bottom: 24, left: 36 }
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const y = d3.scaleLinear().domain([30, 110]).range([H - m.bottom, m.top])
    svg.append('g').attr('transform', `translate(${m.left},0)`)
      .call(d3.axisLeft(y).ticks(4)).call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 9))
    const cx = (m.left + W - m.right) / 2
    const q1 = d3.quantile(samples, 0.25), med = d3.quantile(samples, 0.5), q3 = d3.quantile(samples, 0.75)
    const iqr = q3 - q1
    const lo = Math.max(samples[0], q1 - 1.5 * iqr), hi = Math.min(samples[samples.length - 1], q3 + 1.5 * iqr)
    svg.append('line').attr('x1', cx).attr('x2', cx).attr('y1', y(lo)).attr('y2', y(hi)).attr('stroke', COLORS.text)
    svg.append('line').attr('x1', cx - 10).attr('x2', cx + 10).attr('y1', y(lo)).attr('y2', y(lo)).attr('stroke', COLORS.text)
    svg.append('line').attr('x1', cx - 10).attr('x2', cx + 10).attr('y1', y(hi)).attr('y2', y(hi)).attr('stroke', COLORS.text)
    svg.append('rect').attr('x', cx - 22).attr('y', y(q3)).attr('width', 44).attr('height', y(q1) - y(q3))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.35).attr('stroke', COLORS.accent)
    svg.append('line').attr('x1', cx - 22).attr('x2', cx + 22).attr('y1', y(med)).attr('y2', y(med))
      .attr('stroke', '#f5f5f5').attr('stroke-width', 1.5)
    svg.append('text').attr('x', m.left).attr('y', m.top + 6)
      .attr('fill', COLORS.danger).attr('font-size', 9).text('bimodality → hidden')
  }

  function violin(el) {
    const W = 300, H = 180, m = { top: 14, right: 16, bottom: 24, left: 36 }
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const y = d3.scaleLinear().domain([30, 110]).range([H - m.bottom, m.top])
    svg.append('g').attr('transform', `translate(${m.left},0)`)
      .call(d3.axisLeft(y).ticks(4)).call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
      .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 9))
    const cx = (m.left + W - m.right) / 2
    const gridY = d3.range(30, 110, 1)
    function kde(h) {
      return gridY.map(t => {
        let s = 0
        for (const v of samples) { const u = (t - v) / h; s += Math.exp(-0.5 * u * u) }
        return s / (samples.length * h * Math.sqrt(2 * Math.PI))
      })
    }
    const d = kde(3.5)
    const maxD = d3.max(d)
    const halfW = 70
    const w = d3.scaleLinear().domain([0, maxD]).range([0, halfW])
    const pts = d.map((dd, i) => ({ y: gridY[i], w: w(dd) }))
    const areaR = d3.area().curve(d3.curveMonotoneY).y(v => y(v.y)).x0(cx).x1(v => cx + v.w)
    const areaL = d3.area().curve(d3.curveMonotoneY).y(v => y(v.y)).x0(cx).x1(v => cx - v.w)
    svg.append('path').datum(pts).attr('d', areaR).attr('fill', COLORS.good).attr('fill-opacity', 0.4)
    svg.append('path').datum(pts).attr('d', areaL).attr('fill', COLORS.good).attr('fill-opacity', 0.4)
    svg.append('text').attr('x', m.left).attr('y', m.top + 6)
      .attr('fill', COLORS.good).attr('font-size', 9).text('bimodality → revealed')
  }

  hist(elHist); box(elBox); violin(elViolin)
}

// --------------------------------------------------------- marimekko
// Beverage-industry analogue: 5 regional markets (column widths = market
// size in $B) × 4 brands (within-column stacks = share). Consistent stack
// order across columns; big cells called out; desaturated palette so the
// "big cell in big column" reads as the headline.
export function renderMarimekkoDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // region -> total market size ($B)
  const markets = [
    { name: 'North America', size: 48 },
    { name: 'Europe',        size: 36 },
    { name: 'China',         size: 28 },
    { name: 'LATAM',         size: 14 },
    { name: 'SE Asia',       size: 10 },
  ]
  // shares[region][brand] = fraction (rows in consistent order)
  const brands = ['Brand A', 'Brand B', 'Brand C', 'Others']
  const brandColors = {
    'Brand A': COLORS.accent,      // the "our brand" — saturated
    'Brand B': '#6b7280',
    'Brand C': '#4b5563',
    'Others':  '#374151',
  }
  const shares = {
    'North America': { 'Brand A': 0.08, 'Brand B': 0.32, 'Brand C': 0.22, 'Others': 0.38 },
    'Europe':        { 'Brand A': 0.18, 'Brand B': 0.25, 'Brand C': 0.15, 'Others': 0.42 },
    'China':         { 'Brand A': 0.04, 'Brand B': 0.08, 'Brand C': 0.30, 'Others': 0.58 },
    'LATAM':         { 'Brand A': 0.35, 'Brand B': 0.20, 'Brand C': 0.12, 'Others': 0.33 },
    'SE Asia':       { 'Brand A': 0.42, 'Brand B': 0.18, 'Brand C': 0.10, 'Others': 0.30 },
  }

  const W = 620, H = 360
  const margin = { top: 42, right: 20, bottom: 58, left: 40 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const totalSize = d3.sum(markets, m => m.size)
  const plotW = W - margin.left - margin.right
  const plotH = H - margin.top - margin.bottom
  const totalGap = (markets.length - 1) * 2
  const usableW = plotW - totalGap

  // x-positions per market
  let cursor = margin.left
  for (const m of markets) {
    m.x0 = cursor
    m.w = (m.size / totalSize) * usableW
    m.x1 = m.x0 + m.w
    cursor = m.x1 + 2
  }

  // Draw stacks — consistent brand order across columns (crucial)
  const cellRefs = []
  for (const m of markets) {
    let y0 = margin.top
    for (const b of brands) {
      const h = shares[m.name][b] * plotH
      const rect = svg.append('rect').attr('class', 'mk-cell')
        .attr('data-market', m.name).attr('data-brand', b)
        .attr('x', m.x0).attr('y', y0)
        .attr('width', m.w).attr('height', h)
        .attr('fill', brandColors[b])
        .attr('fill-opacity', b === 'Brand A' ? 0.88 : 0.78)
      if (b === 'Brand A' && m.w * h > 1600) {
        svg.append('text')
          .attr('x', m.x0 + m.w / 2).attr('y', y0 + h / 2 + 3)
          .attr('text-anchor', 'middle').attr('fill', '#0a0a0a').attr('pointer-events', 'none')
          .attr('font-size', 11).attr('font-weight', 600)
          .text(`${Math.round(shares[m.name][b] * 100)}%`)
      }
      cellRefs.push({ m, b, share: shares[m.name][b], rect })
      y0 += h
    }
  }

  // Column labels (market name + size) below
  for (const m of markets) {
    svg.append('text')
      .attr('x', m.x0 + m.w / 2).attr('y', H - margin.bottom + 14)
      .attr('text-anchor', 'middle').attr('fill', COLORS.text).attr('font-size', 10)
      .text(m.name)
    svg.append('text')
      .attr('x', m.x0 + m.w / 2).attr('y', H - margin.bottom + 26)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
      .text(`$${m.size}B`)
  }

  // Y-axis for stack percentages (0-100%) on the left
  const yScale = d3.scaleLinear().domain([0, 100]).range([plotH, 0])
  svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)
    .call(d3.axisLeft(yScale).ticks(4).tickFormat(d => `${d}%`))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 9))

  // Title / eyebrow
  svg.append('text').attr('x', margin.left).attr('y', 16)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('letter-spacing', '0.08em')
    .text('COLUMN WIDTH = MARKET SIZE · STACK HEIGHT = BRAND SHARE')
  svg.append('text').attr('x', margin.left).attr('y', 30)
    .attr('fill', '#6b7280').attr('font-size', 9).attr('font-style', 'italic')
    .text('Brand A dominates SE Asia + LATAM — our "small market, big share" footprint')

  // Legend bottom-right (just Brand A swatch — the narrative subject)
  const lgY = H - 14
  const lgX = W - 200
  svg.append('rect').attr('x', lgX).attr('y', lgY - 8).attr('width', 14).attr('height', 10)
    .attr('fill', brandColors['Brand A']).attr('fill-opacity', 0.88)
  svg.append('text').attr('x', lgX + 20).attr('y', lgY)
    .attr('fill', COLORS.text).attr('font-size', 10).text('Brand A')
  svg.append('text').attr('x', lgX + 68).attr('y', lgY)
    .attr('fill', COLORS.label).attr('font-size', 10).text('· (others desaturated)')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals cell's market + brand + share + absolute magnitude)
  const tip = createTooltip(container, { className: 'mk-tip' })
  for (const ref of cellRefs) {
    const magnitude = (ref.share * ref.m.size).toFixed(1)
    const body = `<strong>${ref.b} · ${ref.m.name}</strong><br>` +
      `<span style="color:#a3a3a3">share:</span> <strong>${Math.round(ref.share * 100)}%</strong> ` +
      `<span style="color:#a3a3a3">· magnitude:</span> <strong>$${magnitude}B</strong>`
    ref.rect.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        ref.rect.attr('stroke', '#f5f5f5').attr('stroke-width', 1.4)
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', () => { ref.rect.attr('stroke', null).attr('stroke-width', null); tip.hide() })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- gantt-chart
// Synthetic 12-task "publish a magazine issue" schedule. Critical-path
// tasks highlighted amber; completed-portion shaded inside the planned
// outline; milestones as diamonds; a "today" vertical line.
export function renderGanttChartDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Tasks with start/end (day index from project start), status, critical-path flag
  const tasks = [
    { n: 'Pitch meeting',       s: 0,  e: 2,  done: 1.0, crit: true,  kind: 'task' },
    { n: 'Commission writers',  s: 2,  e: 6,  done: 1.0, crit: true,  kind: 'task' },
    { n: 'Art direction brief', s: 3,  e: 7,  done: 1.0, crit: false, kind: 'task' },
    { n: 'Drafts in',           s: 7,  e: 7,  done: 1.0, crit: true,  kind: 'milestone' },
    { n: 'First-pass edits',    s: 7,  e: 14, done: 0.7, crit: true,  kind: 'task' },
    { n: 'Photo shoots',        s: 6,  e: 12, done: 0.5, crit: false, kind: 'task' },
    { n: 'Layout design',       s: 10, e: 18, done: 0.3, crit: false, kind: 'task' },
    { n: 'Copy edit',           s: 14, e: 19, done: 0.0, crit: true,  kind: 'task' },
    { n: 'Fact-check',          s: 15, e: 19, done: 0.0, crit: false, kind: 'task' },
    { n: 'Final layout',        s: 18, e: 22, done: 0.0, crit: true,  kind: 'task' },
    { n: 'Proofs → printer',    s: 22, e: 22, done: 0.0, crit: true,  kind: 'milestone' },
    { n: 'On newsstands',       s: 30, e: 30, done: 0.0, crit: true,  kind: 'milestone' },
  ]
  const todayDay = 11

  const W = 620, H = 410
  const margin = { top: 30, right: 20, bottom: 70, left: 140 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const y = d3.scaleBand().domain(tasks.map(t => t.n))
    .range([margin.top, H - margin.bottom]).padding(0.25)
  const x = d3.scaleLinear().domain([0, 32]).range([margin.left, W - margin.right])

  // x-axis: day labels + week markers
  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(8).tickFormat(d => `day ${d}`))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 9))

  // Week gridlines (every 7 days)
  for (let d = 0; d <= 32; d += 7) {
    svg.append('line').attr('x1', x(d)).attr('x2', x(d))
      .attr('y1', margin.top).attr('y2', H - margin.bottom)
      .attr('stroke', COLORS.grid).attr('stroke-width', 0.5).attr('stroke-dasharray', '2 3')
  }

  // Bars + milestones — capture refs for hover handlers
  const taskRefs = []
  for (const t of tasks) {
    const cy = y(t.n) + y.bandwidth() / 2
    if (t.kind === 'milestone') {
      const cx = x(t.s)
      const r = 6
      const shape = svg.append('polygon').attr('class', 'gantt-mark').attr('data-task', t.n)
        .attr('points', `${cx},${cy - r} ${cx + r},${cy} ${cx},${cy + r} ${cx - r},${cy}`)
        .attr('fill', t.crit ? COLORS.warm : COLORS.accent)
        .attr('stroke', '#0a0a0a').attr('stroke-width', 1)
      taskRefs.push({ t, shape, cx, cy })
    } else {
      const barY = y(t.n), barH = y.bandwidth()
      const x0 = x(t.s), x1 = x(t.e)
      const color = t.crit ? COLORS.warm : COLORS.accent
      const shape = svg.append('rect').attr('class', 'gantt-mark').attr('data-task', t.n)
        .attr('x', x0).attr('y', barY)
        .attr('width', x1 - x0).attr('height', barH).attr('rx', 2)
        .attr('fill', 'none').attr('stroke', color).attr('stroke-width', 1.3)
        .attr('pointer-events', 'all')
      if (t.done > 0) {
        svg.append('rect').attr('x', x0).attr('y', barY)
          .attr('width', (x1 - x0) * t.done).attr('height', barH).attr('rx', 2)
          .attr('fill', color).attr('fill-opacity', 0.55)
          .attr('pointer-events', 'none')
      }
      taskRefs.push({ t, shape, barY, barH, color })
    }
  }

  // Task labels on the left
  for (const t of tasks) {
    svg.append('text').attr('x', margin.left - 8)
      .attr('y', y(t.n) + y.bandwidth() / 2 + 3.5)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 10)
      .text(t.n)
  }

  // "Today" vertical line
  svg.append('line').attr('x1', x(todayDay)).attr('x2', x(todayDay))
    .attr('y1', margin.top - 4).attr('y2', H - margin.bottom)
    .attr('stroke', '#f5f5f5').attr('stroke-width', 1.5)
  svg.append('text').attr('x', x(todayDay)).attr('y', margin.top - 8)
    .attr('text-anchor', 'middle').attr('fill', '#f5f5f5').attr('font-size', 9)
    .attr('font-weight', 600).text('today')

  // Legend — below the x-axis to keep the chart top clear for "today"
  const lgY = H - 18
  // Critical-path swatch
  svg.append('rect').attr('x', margin.left).attr('y', lgY - 6).attr('width', 14).attr('height', 8)
    .attr('fill', COLORS.warm).attr('fill-opacity', 0.55).attr('stroke', COLORS.warm).attr('stroke-width', 1)
  svg.append('text').attr('x', margin.left + 18).attr('y', lgY + 1)
    .attr('fill', COLORS.label).attr('font-size', 9).text('critical path')
  // Non-critical swatch
  svg.append('rect').attr('x', margin.left + 110).attr('y', lgY - 6).attr('width', 14).attr('height', 8)
    .attr('fill', COLORS.accent).attr('fill-opacity', 0.55).attr('stroke', COLORS.accent).attr('stroke-width', 1)
  svg.append('text').attr('x', margin.left + 128).attr('y', lgY + 1)
    .attr('fill', COLORS.label).attr('font-size', 9).text('other task')
  // Milestone
  const msX = margin.left + 220, r = 5
  svg.append('polygon')
    .attr('points', `${msX},${lgY - r} ${msX + r},${lgY} ${msX},${lgY + r} ${msX - r},${lgY}`)
    .attr('fill', COLORS.warm).attr('stroke', '#0a0a0a').attr('stroke-width', 1)
  svg.append('text').attr('x', msX + 10).attr('y', lgY + 3)
    .attr('fill', COLORS.label).attr('font-size', 9).text('milestone')

  if (!interactive) return

  // INTERACTIVE (P10: hover task reveals dates, duration, status)
  const tip = createTooltip(container, { className: 'gantt-tip' })
  for (const ref of taskRefs) {
    const t = ref.t
    const dur = t.kind === 'milestone' ? 0 : (t.e - t.s)
    const status = t.kind === 'milestone'
      ? 'milestone'
      : (t.done === 0 ? 'not started' : t.done >= 1 ? 'complete' : `${Math.round(t.done * 100)}% done`)
    const body = `<strong>${t.n}</strong> ${t.crit ? '<span style="color:#fbbf24">· critical path</span>' : ''}<br>` +
      (t.kind === 'milestone'
        ? `<span style="color:#a3a3a3">day:</span> ${t.s}<br><span style="color:#a3a3a3">status:</span> ${status}`
        : `<span style="color:#a3a3a3">days ${t.s}–${t.e}</span> <span style="color:#737373">(${dur}d)</span><br>` +
          `<span style="color:#a3a3a3">status:</span> ${status}`)
    ref.shape.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        if (t.kind === 'milestone') {
          ref.shape.attr('stroke-width', 1.8).attr('stroke', '#f5f5f5')
        } else {
          ref.shape.attr('stroke-width', 2.2)
        }
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', () => {
        if (t.kind === 'milestone') {
          ref.shape.attr('stroke-width', 1).attr('stroke', '#0a0a0a')
        } else {
          ref.shape.attr('stroke-width', 1.3)
        }
        tip.hide()
      })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- dendrogram
// Synthetic hierarchical clustering of 12 cities on two features (avg temp
// + avg rainfall, standardized). We hand-roll agglomerative clustering via
// single-linkage so the tree structure is deterministic and readable.
// Y-axis encodes merge distance — the form's whole point.
export function renderDendrogramDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // 12 cities with (standardized-ish) temperature / rainfall scores
  const cities = [
    { n: 'Seattle',  t: -1.0, r:  1.6 },
    { n: 'Portland', t: -0.8, r:  1.4 },
    { n: 'SF',       t:  0.2, r:  0.5 },
    { n: 'LA',       t:  0.9, r: -0.4 },
    { n: 'Phoenix',  t:  1.9, r: -1.8 },
    { n: 'Denver',   t: -0.5, r: -1.0 },
    { n: 'Minneapolis', t: -1.5, r: -0.2 },
    { n: 'Chicago',  t: -0.9, r:  0.2 },
    { n: 'NYC',      t: -0.3, r:  0.7 },
    { n: 'Atlanta',  t:  1.1, r:  1.0 },
    { n: 'Miami',    t:  1.8, r:  1.9 },
    { n: 'Houston',  t:  1.5, r:  0.9 },
  ]

  // Agglomerative single-linkage clustering
  const dist = (a, b) => Math.hypot(a.t - b.t, a.r - b.r)
  const clusters = cities.map((c, i) => ({
    id: i, leaves: [i], height: 0, kids: null, members: [c],
  }))
  const merges = []
  while (clusters.length > 1) {
    // Find the closest pair by single-linkage distance
    let best = null
    for (let i = 0; i < clusters.length; i++) {
      for (let j = i + 1; j < clusters.length; j++) {
        // single-linkage: min distance between any pair across clusters
        let minD = Infinity
        for (const a of clusters[i].members) {
          for (const b of clusters[j].members) {
            const d = dist(a, b)
            if (d < minD) minD = d
          }
        }
        if (best == null || minD < best.d) best = { i, j, d: minD }
      }
    }
    const a = clusters[best.i], b = clusters[best.j]
    const merged = {
      id: cities.length + merges.length,
      leaves: [...a.leaves, ...b.leaves],
      height: best.d,
      kids: [a, b],
      members: [...a.members, ...b.members],
    }
    merges.push(merged)
    clusters.splice(best.j, 1)
    clusters.splice(best.i, 1)
    clusters.push(merged)
  }
  const root = clusters[0]

  // Traverse for leaf order (left-to-right in the drawing)
  const leafOrder = []
  function visit(n) {
    if (!n.kids) { leafOrder.push(n.leaves[0]); return }
    visit(n.kids[0]); visit(n.kids[1])
  }
  visit(root)

  const W = 620, H = 380
  const margin = { top: 42, right: 60, bottom: 72, left: 54 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const leafX = new Map()
  const plotW = W - margin.left - margin.right
  const step = plotW / (leafOrder.length - 1)
  leafOrder.forEach((idx, pos) => leafX.set(idx, margin.left + pos * step))

  const maxH = root.height
  const y = d3.scaleLinear().domain([0, maxH * 1.1]).range([H - margin.bottom, margin.top])

  // y-axis: merge distance
  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(4))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('text').attr('x', 8).attr('y', margin.top - 4)
    .attr('fill', COLORS.label).attr('font-size', 10)
    .text('merge dist')

  // Draw tree — for each internal node, draw the U: two verticals + one horizontal
  function xOf(n) {
    if (!n.kids) return leafX.get(n.leaves[0])
    const l = xOf(n.kids[0]), r = xOf(n.kids[1])
    return (l + r) / 2
  }
  // Collect internal-node horizontals so interactive mode can hit-target them
  const nodeRefs = []
  function drawNode(n, parentHeight) {
    if (!n.kids) {
      const x = leafX.get(n.leaves[0])
      svg.append('line').attr('x1', x).attr('x2', x)
        .attr('y1', y(0)).attr('y2', y(parentHeight))
        .attr('stroke', COLORS.text).attr('stroke-width', 1)
      return
    }
    const lX = xOf(n.kids[0]), rX = xOf(n.kids[1])
    const yH = y(n.height)
    const horiz = svg.append('line').attr('class', 'dg-merge')
      .attr('x1', lX).attr('x2', rX)
      .attr('y1', yH).attr('y2', yH)
      .attr('stroke', COLORS.text).attr('stroke-width', 1)
    const lTop = n.kids[0].kids ? y(n.kids[0].height) : y(0)
    svg.append('line').attr('x1', lX).attr('x2', lX)
      .attr('y1', yH).attr('y2', lTop)
      .attr('stroke', COLORS.text).attr('stroke-width', 1)
    const rTop = n.kids[1].kids ? y(n.kids[1].height) : y(0)
    svg.append('line').attr('x1', rX).attr('x2', rX)
      .attr('y1', yH).attr('y2', rTop)
      .attr('stroke', COLORS.text).attr('stroke-width', 1)
    nodeRefs.push({ n, horiz, lX, rX, yH })
    drawNode(n.kids[0], n.height)
    drawNode(n.kids[1], n.height)
  }
  drawNode(root, root.height)

  // Cut-line example at height ≈ 0.9 → reveals ~4 clusters
  const cutHeight = 1.2
  svg.append('line').attr('x1', margin.left).attr('x2', W - margin.right)
    .attr('y1', y(cutHeight)).attr('y2', y(cutHeight))
    .attr('stroke', COLORS.warm).attr('stroke-dasharray', '3 3').attr('stroke-width', 1.2)
  svg.append('text').attr('x', W - margin.right + 4).attr('y', y(cutHeight) + 3)
    .attr('fill', COLORS.warm).attr('font-size', 9).text('cut')

  // Leaf labels — rotated with end-anchor so text extends down-left from
  // the pivot; avoids right-edge clipping even on the rightmost leaf.
  for (const idx of leafOrder) {
    const x = leafX.get(idx)
    svg.append('text')
      .attr('text-anchor', 'end')
      .attr('transform', `translate(${x}, ${H - margin.bottom + 12}) rotate(-55)`)
      .attr('fill', COLORS.text).attr('font-size', 10)
      .text(cities[idx].n)
  }

  // Linkage-method footnote — above chart, well clear of y-axis label
  svg.append('text').attr('x', 90).attr('y', 14)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('font-style', 'italic')
    .text('single-linkage, 12 US cities clustered by (temp, rainfall)')
  svg.append('text').attr('x', 90).attr('y', 27)
    .attr('fill', COLORS.label).attr('font-size', 9).attr('font-style', 'italic')
    .text('dashed cut-line shows ~4 clusters')

  if (!interactive) return

  // INTERACTIVE (P10: hover a merge to reveal its members + merge distance)
  // Overlay invisible wider hit-lines over each internal node's horizontal
  // so narrow strokes are easy to target. Also paint a bracket underneath
  // the cluster's leaves on hover so the reader sees what's "in" it.
  const tip = createTooltip(container, { className: 'dg-tip' })
  const highlightG = svg.append('g').attr('class', 'dg-highlight').style('pointer-events', 'none')
  for (const ref of nodeRefs) {
    const { n, horiz, lX, rX, yH } = ref
    // Wide invisible hit-line covering the merge horizontal
    const hit = svg.append('line').attr('class', 'dg-hit')
      .attr('x1', lX).attr('x2', rX).attr('y1', yH).attr('y2', yH)
      .attr('stroke', 'transparent').attr('stroke-width', 10)
      .style('cursor', 'pointer')
    const memberNames = n.members.map(m => m.n)
    const body = `<strong>${memberNames.length} cities</strong> <span style="color:#737373">merge distance: ${n.height.toFixed(2)}</span><br>` +
      `<span style="color:#a3a3a3">${memberNames.join(', ')}</span>`
    hit.on('mouseenter', function (event) {
      horiz.attr('stroke', COLORS.warm).attr('stroke-width', 2)
      // Bracket underneath the cluster's leaves
      highlightG.selectAll('*').remove()
      const members = n.leaves.map(i => leafX.get(i))
      const minX = Math.min(...members), maxX = Math.max(...members)
      const baseY = y(0) + 4
      highlightG.append('line').attr('x1', minX - 4).attr('x2', maxX + 4)
        .attr('y1', baseY).attr('y2', baseY).attr('stroke', COLORS.warm).attr('stroke-width', 1.3)
      highlightG.append('line').attr('x1', minX - 4).attr('x2', minX - 4)
        .attr('y1', baseY).attr('y2', baseY + 4).attr('stroke', COLORS.warm).attr('stroke-width', 1.3)
      highlightG.append('line').attr('x1', maxX + 4).attr('x2', maxX + 4)
        .attr('y1', baseY).attr('y2', baseY + 4).attr('stroke', COLORS.warm).attr('stroke-width', 1.3)
      tip.show(event.pageX, event.pageY, body)
    })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', function () {
      horiz.attr('stroke', COLORS.text).attr('stroke-width', 1)
      highlightG.selectAll('*').remove()
      tip.hide()
    })
    hit.on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- box-and-jitter-strip
// Five groups with deliberately varying N and shape: uniform, bimodal,
// long-tail, sparse, skewed. Boxplot overlay is semitransparent so
// dots behind remain legible.
export function renderBoxAndJitterStripDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const rng = (seed => () => {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff
    return (seed >>> 0) / 0x100000000
  })(71)
  const normal = (m, sd) => {
    const z = Math.sqrt(-2 * Math.log(rng() + 1e-9)) * Math.cos(2 * Math.PI * rng())
    return m + sd * z
  }
  const groups = [
    { name: 'Uniform\n(n=40)',   gen: () => 45 + rng() * 30,         n: 40 },
    { name: 'Bimodal\n(n=35)',   gen: () => rng() < 0.5 ? normal(55, 4) : normal(82, 4), n: 35 },
    { name: 'Long-tail\n(n=45)', gen: () => 48 + Math.pow(rng(), 3) * 50, n: 45 },
    { name: 'Sparse\n(n=8)',     gen: () => normal(65, 10),           n: 8 },
    { name: 'Skewed\n(n=60)',    gen: () => 40 + Math.pow(rng(), 0.35) * 50, n: 60 },
  ]
  for (const g of groups) {
    g.values = []
    for (let i = 0; i < g.n; i++) g.values.push(g.gen())
    g.values.sort(d3.ascending)
    g.q1 = d3.quantile(g.values, 0.25)
    g.med = d3.quantile(g.values, 0.5)
    g.q3 = d3.quantile(g.values, 0.75)
    const iqr = g.q3 - g.q1
    g.lo = Math.max(g.values[0], g.q1 - 1.5 * iqr)
    g.hi = Math.min(g.values[g.values.length - 1], g.q3 + 1.5 * iqr)
  }

  const W = 620, H = 340
  const margin = { top: 32, right: 20, bottom: 46, left: 40 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
  const x = d3.scaleBand().domain(groups.map(g => g.name))
    .range([margin.left, W - margin.right]).padding(0.35)
  const y = d3.scaleLinear().domain([30, 100]).range([H - margin.bottom, margin.top])

  svg.append('g').attr('transform', `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))

  // Fixed-seed jitter per point (deterministic)
  const jrng = (seed => () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff
    return seed / 0x7fffffff
  })(101)

  const bjRefs = []
  for (const g of groups) {
    const cx = x(g.name) + x.bandwidth() / 2
    const boxW = x.bandwidth() * 0.5
    const jitterW = x.bandwidth() * 0.45

    for (const v of g.values) {
      const dx = (jrng() - 0.5) * jitterW
      svg.append('circle').attr('cx', cx + dx).attr('cy', y(v))
        .attr('r', 2.2).attr('fill', COLORS.label).attr('fill-opacity', 0.6)
        .attr('pointer-events', 'none')
    }

    svg.append('line').attr('x1', cx).attr('x2', cx)
      .attr('y1', y(g.lo)).attr('y2', y(g.hi))
      .attr('stroke', COLORS.text).attr('stroke-width', 1)
    svg.append('line').attr('x1', cx - 7).attr('x2', cx + 7)
      .attr('y1', y(g.lo)).attr('y2', y(g.lo)).attr('stroke', COLORS.text)
    svg.append('line').attr('x1', cx - 7).attr('x2', cx + 7)
      .attr('y1', y(g.hi)).attr('y2', y(g.hi)).attr('stroke', COLORS.text)
    const box = svg.append('rect')
      .attr('x', cx - boxW / 2).attr('y', y(g.q3))
      .attr('width', boxW).attr('height', y(g.q1) - y(g.q3))
      .attr('fill', COLORS.accent).attr('fill-opacity', 0.3)
      .attr('stroke', COLORS.accent).attr('stroke-width', 1.2)
    svg.append('line')
      .attr('x1', cx - boxW / 2).attr('x2', cx + boxW / 2)
      .attr('y1', y(g.med)).attr('y2', y(g.med))
      .attr('stroke', '#f5f5f5').attr('stroke-width', 2)

    const lines = g.name.split('\n')
    for (let li = 0; li < lines.length; li++) {
      svg.append('text').attr('x', cx).attr('y', H - margin.bottom + 14 + li * 11)
        .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 10)
        .text(lines[li])
    }

    bjRefs.push({ g, cx, box })
  }

  svg.append('text').attr('x', margin.left).attr('y', 16)
    .attr('fill', COLORS.label).attr('font-size', 10)
    .text('Box = summary. Dots = every observation.')
  svg.append('text').attr('x', margin.left).attr('y', 28)
    .attr('fill', '#6b7280').attr('font-size', 9).attr('font-style', 'italic')
    .text('The sparse group\'s 8 dots tell you what its boxplot alone could never say.')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals group summary + N — the hybrid's
  // whole story: small N is visible as sparse dots, large N as packed)
  const tip = createTooltip(container, { className: 'bj-tip' })
  for (const ref of bjRefs) {
    const hitX = x(ref.g.name)
    const hit = svg.append('rect').attr('class', 'bj-hit').attr('data-name', ref.g.name.split('\n')[0])
      .attr('x', hitX).attr('y', margin.top)
      .attr('width', x.bandwidth())
      .attr('height', H - margin.bottom - margin.top)
      .attr('fill', 'transparent').style('cursor', 'pointer')
    const iqr = ref.g.q3 - ref.g.q1
    const shortName = ref.g.name.split('\n')[0]
    const body = `<strong>${shortName}</strong> <span style="color:#737373">n=${ref.g.values.length}</span><br>` +
      `<span style="color:#a3a3a3">median:</span> <strong>${ref.g.med.toFixed(1)}</strong><br>` +
      `<span style="color:#a3a3a3">Q1–Q3:</span> ${ref.g.q1.toFixed(1)}–${ref.g.q3.toFixed(1)} ` +
      `<span style="color:#737373">(IQR ${iqr.toFixed(1)})</span>`
    hit.on('mouseenter', function (event) {
      ref.box.attr('fill-opacity', 0.5).attr('stroke-width', 1.7)
      tip.show(event.pageX, event.pageY, body)
    })
    hit.on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
    hit.on('mouseleave', () => {
      ref.box.attr('fill-opacity', 0.3).attr('stroke-width', 1.2)
      tip.hide()
    })
    hit.on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- lollipop-chart
// 24 synthetic country CO2-per-capita values. Stems hair-thin; dots are
// the figure. Sorted high→low. Zero-based x-axis (the form requires it).
export function renderLollipopChartDemo(container) {
  const data = [
    { n: 'Qatar',        v: 37.0 },
    { n: 'Kuwait',       v: 24.8 },
    { n: 'Brunei',       v: 22.1 },
    { n: 'UAE',          v: 21.4 },
    { n: 'Oman',         v: 19.2 },
    { n: 'Australia',    v: 15.2 },
    { n: 'USA',          v: 14.9 },
    { n: 'Saudi Arabia', v: 14.7 },
    { n: 'Canada',       v: 14.2 },
    { n: 'Kazakhstan',   v: 13.8 },
    { n: 'Russia',       v: 11.4 },
    { n: 'South Korea',  v: 11.0 },
    { n: 'Japan',        v:  8.4 },
    { n: 'Germany',      v:  7.7 },
    { n: 'China',        v:  7.5 },
    { n: 'Poland',       v:  7.2 },
    { n: 'Iran',         v:  6.8 },
    { n: 'UK',           v:  5.0 },
    { n: 'France',       v:  4.5 },
    { n: 'Mexico',       v:  3.0 },
    { n: 'Brazil',       v:  2.1 },
    { n: 'India',        v:  1.9 },
    { n: 'Nigeria',      v:  0.5 },
    { n: 'Ethiopia',     v:  0.15 },
  ].sort((a, b) => b.v - a.v)

  const W = 620, H = 440
  const margin = { top: 28, right: 56, bottom: 32, left: 120 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  const y = d3.scaleBand().domain(data.map(d => d.n))
    .range([margin.top, H - margin.bottom]).padding(0.15)
  const x = d3.scaleLinear().domain([0, 40])
    .range([margin.left, W - margin.right])

  // x-axis at bottom
  svg.append('g').attr('transform', `translate(0,${H - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(5))
    .call(g => g.selectAll('.domain, line').attr('stroke', COLORS.grid))
    .call(g => g.selectAll('text').attr('fill', COLORS.label).attr('font-size', 10))
  svg.append('text').attr('x', W / 2).attr('y', H - 6)
    .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 10)
    .text('tCO₂ per capita (2022, approx)')

  // Hair-thin stems from zero to the dot
  for (const d of data) {
    const cy = y(d.n) + y.bandwidth() / 2
    svg.append('line')
      .attr('x1', x(0)).attr('x2', x(d.v))
      .attr('y1', cy).attr('y2', cy)
      .attr('stroke', '#525252').attr('stroke-width', 1)
  }
  // Dots — these are the figure
  for (const d of data) {
    const cy = y(d.n) + y.bandwidth() / 2
    svg.append('circle').attr('cx', x(d.v)).attr('cy', cy).attr('r', 4.5)
      .attr('fill', COLORS.accent)
  }
  // Row labels on the left
  for (const d of data) {
    svg.append('text').attr('x', margin.left - 8)
      .attr('y', y(d.n) + y.bandwidth() / 2 + 3.5)
      .attr('text-anchor', 'end').attr('fill', COLORS.text).attr('font-size', 10)
      .text(d.n)
  }
  // Value labels on the right
  for (const d of data) {
    svg.append('text').attr('x', x(d.v) + 8)
      .attr('y', y(d.n) + y.bandwidth() / 2 + 3.5)
      .attr('fill', COLORS.label).attr('font-size', 9)
      .text(d.v.toFixed(1))
  }
}

// --------------------------------------------------------- calendar-heatmap
// GitHub-style 7×N grid: 7 rows (day of week) × ~52 columns (weeks).
// Synthetic "commits per day" with a clear weekday/weekend rhythm and a
// summer trough so the cyclic structure is obvious. Month labels on top,
// day-of-week labels on the left. Monotone green scale — cycling color
// scales would fight the pattern.
export function renderCalendarHeatmapDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  const rng = (seed => () => {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff
    return (seed >>> 0) / 0x100000000
  })(1042)
  const W = 620, H = 300
  const margin = { top: 28, right: 16, bottom: 16, left: 36 }
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // Build ~52 weeks × 7 days of synthetic "commits per day"
  const start = new Date(2025, 0, 6) // Mon 2025-01-06 — week-aligned
  const weeks = 52
  const cellW = Math.floor((W - margin.left - margin.right) / weeks)
  const cellH = Math.floor((H - margin.top - margin.bottom) / 7)
  const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  const cells = []
  for (let w = 0; w < weeks; w++) {
    for (let d = 0; d < 7; d++) {
      const date = new Date(start); date.setDate(start.getDate() + w * 7 + d)
      const month = date.getMonth()
      const isWeekend = d >= 5
      // Summer trough: fewer commits in July-August (months 6,7)
      const seasonal = (month === 6 || month === 7) ? 0.35 : 1.0
      const weekendFactor = isWeekend ? 0.25 : 1.0
      // Holiday dips (late December)
      const isHoliday = (month === 11 && date.getDate() > 22)
      const holidayFactor = isHoliday ? 0.2 : 1.0
      let v = 4 + rng() * 12
      v *= weekendFactor * seasonal * holidayFactor
      // Occasional big days
      if (!isWeekend && rng() < 0.03) v *= 3.2
      cells.push({ w, d, date, v, month, isWeekend, isHoliday })
    }
  }

  const maxV = d3.max(cells, c => c.v)
  // Monotone green scale — GitHub-style, single-hue
  const color = d3.scaleSequential(d3.interpolateYlGn).domain([0, maxV])

  // Month labels along the top
  const seen = new Set()
  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  for (const c of cells) {
    if (c.d !== 0) continue
    if (seen.has(c.month)) continue
    seen.add(c.month)
    svg.append('text')
      .attr('x', margin.left + c.w * cellW)
      .attr('y', margin.top - 8)
      .attr('fill', COLORS.label).attr('font-size', 10)
      .text(monthNames[c.month])
  }

  // Day-of-week labels (every other to avoid clutter)
  for (let d = 0; d < 7; d++) {
    if (d % 2 !== 0 && d !== 5) continue
    svg.append('text')
      .attr('x', margin.left - 6).attr('y', margin.top + d * cellH + cellH - 3)
      .attr('text-anchor', 'end')
      .attr('fill', COLORS.label).attr('font-size', 9)
      .text(dayLabels[d])
  }

  // Cells
  for (const c of cells) {
    c.rect = svg.append('rect').attr('class', 'ch-cell')
      .attr('x', margin.left + c.w * cellW)
      .attr('y', margin.top + c.d * cellH)
      .attr('width', cellW - 2).attr('height', cellH - 2).attr('rx', 1.5)
      .attr('fill', color(c.v))
      .attr('stroke', c.isWeekend ? 'none' : 'none')
  }

  // Subtle quarter separators — vertical lines every 13 weeks to anchor reader
  for (let q = 13; q < weeks; q += 13) {
    svg.append('line')
      .attr('x1', margin.left + q * cellW - 1)
      .attr('x2', margin.left + q * cellW - 1)
      .attr('y1', margin.top).attr('y2', margin.top + 7 * cellH - 2)
      .attr('stroke', '#1f1f1f').attr('stroke-width', 0.6).attr('stroke-dasharray', '2 2')
  }

  // Color-scale legend at bottom-right
  const legN = 5
  const legW = 70, legH = 8
  // Leave ~30px past the swatch row for the trailing "more" label
  const legX = W - margin.right - legW - 30
  const legY = H - 8
  svg.append('text').attr('x', legX - 10).attr('y', legY + 6)
    .attr('text-anchor', 'end').attr('fill', COLORS.label).attr('font-size', 9)
    .text('less')
  for (let i = 0; i < legN; i++) {
    svg.append('rect')
      .attr('x', legX + i * (legW / legN))
      .attr('y', legY).attr('width', legW / legN - 1).attr('height', legH)
      .attr('fill', color((i + 0.5) / legN * maxV))
  }
  svg.append('text').attr('x', legX + legW + 4).attr('y', legY + 6)
    .attr('fill', COLORS.label).attr('font-size', 9)
    .text('more')

  if (!interactive) return

  // INTERACTIVE (P10: hover reveals date + count)
  const dowFull = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const tip = createTooltip(container, { className: 'cal-heat-tip' })
  function fmt(d) { return d.toISOString().slice(0, 10) }
  for (const c of cells) {
    const body = `<strong>${dowFull[c.d]} ${fmt(c.date)}</strong><br>` +
      `<span style="color:#a3a3a3">commits:</span> <strong>${c.v.toFixed(0)}</strong>`
    c.rect.style('cursor', 'pointer')
      .on('mouseenter', function (event) {
        c.rect.attr('stroke', '#f5f5f5').attr('stroke-width', 1.2)
        tip.show(event.pageX, event.pageY, body)
      })
      .on('mousemove', function (event) { tip.show(event.pageX, event.pageY, body) })
      .on('mouseleave', () => { c.rect.attr('stroke', 'none').attr('stroke-width', 0); tip.hide() })
      .on('click', function (event) { tip.show(event.pageX, event.pageY, body) })
  }
}

// --------------------------------------------------------- radar-chart
// Showing the form in its ONE defensible use: standardized-score archetype
// comparison across a small set of axes, axis order clustering related
// attributes. Outlined polygons (not filled) so area-encoding doesn't lie.
export function renderRadarChartDemo(container, opts = {}) {
  const interactive = opts.interactive !== false
  // Two player archetypes, all stats standardized to 0–100 percentile rank
  const axes = [
    { key: 'scoring',   label: 'Scoring' },
    { key: 'shooting',  label: 'Shooting' },
    { key: 'passing',   label: 'Passing' },
    { key: 'playmake',  label: 'Playmaking' },
    { key: 'defense',   label: 'Defense' },
    { key: 'rebound',   label: 'Rebounding' },
  ]
  const players = [
    {
      name: 'All-rounder',
      color: COLORS.accent,
      // Balanced shape (all near 70)
      values: { scoring: 72, shooting: 70, passing: 75, playmake: 78, defense: 68, rebound: 65 },
    },
    {
      name: 'Scoring specialist',
      color: COLORS.warm,
      // Pointy shape, spike on scoring/shooting
      values: { scoring: 92, shooting: 88, passing: 55, playmake: 48, defense: 42, rebound: 40 },
    },
  ]
  const W = 620, H = 460
  const cx = W / 2, cy = H / 2 - 6, radius = 140
  const svg = d3.select(container).append('svg').attr('viewBox', `0 0 ${W} ${H}`)

  // DECODER / caveat strip at top — axis-order and no-fill are the form's defensibility
  const dy = 8, dH = 42
  svg.append('rect').attr('x', 30).attr('y', dy)
    .attr('width', W - 60).attr('height', dH)
    .attr('fill', '#0a1020').attr('stroke', '#1f2a3a').attr('rx', 4)
  svg.append('text').attr('x', 38).attr('y', dy + 11)
    .attr('fill', '#93c5fd').attr('font-size', 8).attr('letter-spacing', '0.1em').text('RADAR · USED CORRECTLY')
  svg.append('text').attr('x', 38).attr('y', dy + 24)
    .attr('fill', COLORS.label).attr('font-size', 9)
    .text('all axes on a shared 0–100 percentile scale · 6 axes · ≤3 entities · outlined, not filled (area would lie)')
  svg.append('text').attr('x', 38).attr('y', dy + 35)
    .attr('fill', COLORS.warm).attr('font-size', 9).attr('font-style', 'italic')
    .text('change the axis order → "shape" changes. The shape only carries signal when the clockwise order is semantic.')

  const n = axes.length
  const angle = i => -Math.PI / 2 + (i * 2 * Math.PI) / n
  // Polar→cartesian for a value v in [0, 100]
  const point = (v, i) => [
    cx + Math.cos(angle(i)) * (v / 100) * radius,
    cy + Math.sin(angle(i)) * (v / 100) * radius,
  ]

  // Gridlines at 25/50/75/100
  for (const level of [25, 50, 75, 100]) {
    const pts = d3.range(n).map(i => point(level, i))
    svg.append('polygon')
      .attr('points', pts.map(p => p.join(',')).join(' '))
      .attr('fill', 'none')
      .attr('stroke', level === 100 ? COLORS.grid : '#1a1a1a')
      .attr('stroke-width', level === 100 ? 1 : 0.6)
  }
  // Level labels on the top spoke
  for (const level of [25, 50, 75, 100]) {
    const [x, y] = point(level, 0)
    svg.append('text').attr('x', x + 4).attr('y', y + 2)
      .attr('fill', '#525252').attr('font-size', 8).text(level)
  }
  // Spokes + axis labels
  for (let i = 0; i < n; i++) {
    const [x, y] = point(100, i)
    svg.append('line').attr('x1', cx).attr('y1', cy).attr('x2', x).attr('y2', y)
      .attr('stroke', COLORS.grid).attr('stroke-width', 0.6)
    const lx = cx + Math.cos(angle(i)) * (radius + 18)
    const ly = cy + Math.sin(angle(i)) * (radius + 18)
    const anchor = Math.abs(lx - cx) < 4 ? 'middle' : (lx > cx ? 'start' : 'end')
    svg.append('text').attr('x', lx).attr('y', ly + 4)
      .attr('text-anchor', anchor).attr('fill', COLORS.text).attr('font-size', 11)
      .text(axes[i].label)
  }

  // Player polygons — OUTLINED only (no fill!). Dots at each vertex for readability.
  const vertexRefs = []
  for (const p of players) {
    const pts = axes.map((a, i) => point(p.values[a.key], i))
    svg.append('polygon')
      .attr('points', pts.map(q => q.join(',')).join(' '))
      .attr('fill', 'none')
      .attr('stroke', p.color).attr('stroke-width', 2)
    for (let i = 0; i < pts.length; i++) {
      const [px, py] = pts[i]
      const dot = svg.append('circle').attr('class', 'radar-vertex')
        .attr('data-player', p.name).attr('data-axis', axes[i].key)
        .attr('cx', px).attr('cy', py).attr('r', 2.8)
        .attr('fill', p.color)
      vertexRefs.push({ p, axis: axes[i], value: p.values[axes[i].key], dot, px, py })
    }
  }

  const lgY = H - 24
  let lgX = 40
  for (const p of players) {
    svg.append('rect').attr('x', lgX).attr('y', lgY - 9).attr('width', 14).attr('height', 3)
      .attr('fill', p.color)
    svg.append('text').attr('x', lgX + 20).attr('y', lgY)
      .attr('fill', COLORS.text).attr('font-size', 11).text(p.name)
    lgX += 190
  }

  if (!interactive) return

  // INTERACTIVE (P10: hover vertex to reveal exact axis value per player —
  // the radar's precise readings are hard to estimate by eye, so this fills
  // the gap. Voronoi so small dots have generous hit targets.)
  const tip = createTooltip(container, { className: 'radar-tip' })
  const pts = vertexRefs.map(r => ({ x: r.px, y: r.py }))
  const delaunay = d3.Delaunay.from(pts, p => p.x, p => p.y)
  let hovered = null
  function setHover(idx) {
    if (hovered === idx) return
    if (hovered != null) vertexRefs[hovered].dot.attr('r', 2.8).attr('stroke', null)
    hovered = idx
    if (idx != null) vertexRefs[idx].dot.attr('r', 5).attr('stroke', '#f5f5f5').attr('stroke-width', 1.4)
  }
  const overlay = svg.append('rect')
    .attr('x', 20).attr('y', dy + dH + 4)
    .attr('width', W - 40).attr('height', H - (dy + dH + 4) - 36)
    .attr('fill', 'transparent').style('cursor', 'crosshair')
  overlay.on('mousemove', function (event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    setHover(idx)
    const ref = vertexRefs[idx]
    tip.show(event.pageX, event.pageY,
      `<strong>${ref.p.name}</strong><br>` +
      `<span style="color:#a3a3a3">${ref.axis.label}:</span> <strong>${ref.value}</strong> <span style="color:#737373">/ 100</span>`)
  })
  overlay.on('mouseleave', () => { setHover(null); tip.hide() })
  overlay.on('click', function (event) {
    const [mx, my] = d3.pointer(event, svg.node())
    const idx = delaunay.find(mx, my)
    if (idx == null || idx < 0) return
    setHover(idx)
    const ref = vertexRefs[idx]
    tip.show(event.pageX, event.pageY,
      `<strong>${ref.p.name}</strong><br>` +
      `<span style="color:#a3a3a3">${ref.axis.label}:</span> <strong>${ref.value}</strong> <span style="color:#737373">/ 100</span>`)
  })
}

// -------- Spatial triad: choropleth / cartogram / proportional-symbol --------
// State population rendered three ways.
export function renderSpatialTriad(elChoro, elCarto, elSymbol) {
  const pop = {  // millions
    CA: 39, TX: 30, FL: 22, NY: 19, PA: 13, IL: 12, OH: 12, GA: 11, NC: 11, MI: 10,
    NJ:  9, VA:  9, WA:  8, AZ:  7, TN:  7, MA:  7, IN:  7, MD:  6, MO:  6, WI:  6,
    CO:  6, MN:  6, SC:  5, AL:  5, LA:  5, KY:  4, OR:  4, OK:  4, CT:  4, UT:  3,
    IA:  3, NV:  3, AR:  3, MS:  3, KS:  3, NM:  2, NE:  2, ID:  2, WV:  2, HI:  1,
    NH:  1, ME:  1, MT:  1, RI:  1, DE:  1, SD:  1, ND:  1, AK: 0.7, VT: 0.65, WY: 0.58,
    DC: 0.7,
  }
  // Choropleth (hex grid) — color by pop
  function choro(el) {
    const W = 280, H = 180
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const color = d3.scaleSequential(d3.interpolatePlasma).domain([0, 40])
    drawHexUS(svg, { W, H, hexR: 9, marginY: 10, cellFn: s => {
      const v = pop[s]
      if (v == null) return { fill: '#1a1a1a', textColor: '#333' }
      const c = d3.color(color(v))
      const l = c.r * 0.299 + c.g * 0.587 + c.b * 0.114
      return { fill: color(v), textColor: l > 140 ? '#0a0a0a' : '#f5f5f5' }
    } })
    svg.append('text').attr('x', W / 2).attr('y', H - 6)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
      .text('area = geography, color = population')
  }

  // Cartogram (Dorling)
  function carto(el) {
    const W = 280, H = 180
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
    const posLonLat = {
      AL:[-86.8,32.8], AK:[-152,63], AZ:[-112,34], AR:[-92,34.9], CA:[-119.7,36.7],
      CO:[-105.5,39], CT:[-72.7,41.6], DE:[-75.5,39], FL:[-81.5,27.7], GA:[-83.6,32.7],
      HI:[-155.5,20], ID:[-114.4,44], IL:[-89.2,40], IN:[-86.3,39.8], IA:[-93.5,42],
      KS:[-98.5,38.5], KY:[-84.9,37.8], LA:[-92,31.2], ME:[-69.4,45.4], MD:[-76.8,39.1],
      MA:[-71.8,42.3], MI:[-84.5,44.3], MN:[-94.3,46.3], MS:[-89.7,32.7], MO:[-92.5,38.5],
      MT:[-110,47], NE:[-99.8,41.5], NV:[-116.8,39.3], NH:[-71.6,43.7], NJ:[-74.7,40.3],
      NM:[-106.1,34.5], NY:[-75.5,42.9], NC:[-79.8,35.6], ND:[-100.5,47.5], OH:[-82.7,40.3],
      OK:[-97.5,35.6], OR:[-120.6,44], PA:[-77.5,40.9], RI:[-71.5,41.7], SC:[-80.9,33.8],
      SD:[-99.9,44.3], TN:[-86.7,35.8], TX:[-99,31.5], UT:[-111.9,39.3], VT:[-72.7,44],
      VA:[-78.2,37.8], WA:[-120.4,47.4], WV:[-80.9,38.5], WI:[-89.6,44.3], WY:[-107.3,43],
      DC:[-77,38.9],
    }
    const proj = projConus(W, H, { padX: 14, padY: 14 })
    const rScale = d3.scaleSqrt().domain([0, 40]).range([0, 18])
    const palette = d3.scaleSequential(d3.interpolatePlasma).domain([0, 40])
    const nodes = Object.entries(pop).map(([s, v]) => {
      if (!posLonLat[s]) return null
      const [x0, y0] = proj(posLonLat[s])
      return { s, v, x: x0, y: y0, x0, y0, r: rScale(v) + 0.5 }
    }).filter(Boolean)
    const sim = d3.forceSimulation(nodes)
      .force('x', d3.forceX(d => d.x0).strength(0.35))
      .force('y', d3.forceY(d => d.y0).strength(0.35))
      .force('collide', d3.forceCollide(d => d.r + 0.5).iterations(3))
      .stop()
    for (let i = 0; i < 140; i++) sim.tick()
    for (const n of nodes) {
      svg.append('circle').attr('cx', n.x).attr('cy', n.y).attr('r', n.r)
        .attr('fill', palette(n.v)).attr('fill-opacity', 0.85).attr('stroke', '#0a0a0a').attr('stroke-width', 0.5)
    }
    svg.append('text').attr('x', W / 2).attr('y', H - 6)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
      .text('area = population, position ~ geography')
  }

  // Proportional-symbol (circles on real-geographic layout)
  function symbol(el) {
    const W = 280, H = 180
    const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`)
      .style('background', '#0a0a0a')
    svg.append('rect').attr('x', 8).attr('y', 8).attr('width', W - 16).attr('height', H - 16)
      .attr('fill', 'none').attr('stroke', '#1a1a1a').attr('stroke-dasharray', '2 3')
    const posLonLat = {
      CA:[-119.7,36.7], TX:[-99,31.5], FL:[-81.5,27.7], NY:[-75.5,42.9], PA:[-77.5,40.9],
      IL:[-89.2,40], OH:[-82.7,40.3], GA:[-83.6,32.7], NC:[-79.8,35.6], MI:[-84.5,44.3],
      NJ:[-74.7,40.3], VA:[-78.2,37.8], WA:[-120.4,47.4], AZ:[-112,34], TN:[-86.7,35.8],
      MA:[-71.8,42.3], IN:[-86.3,39.8], MD:[-76.8,39.1], MO:[-92.5,38.5], WI:[-89.6,44.3],
      CO:[-105.5,39], MN:[-94.3,46.3],
    }
    const proj = projConus(W, H, { padX: 14, padY: 14 })
    const rScale = d3.scaleSqrt().domain([0, 40]).range([0, 14])
    // Draw larger states on top
    const sorted = Object.entries(pop)
      .filter(([s]) => posLonLat[s])
      .sort((a, b) => b[1] - a[1])
    for (const [s, v] of sorted) {
      const [cx, cy] = proj(posLonLat[s])
      svg.append('circle').attr('cx', cx).attr('cy', cy).attr('r', rScale(v))
        .attr('fill', COLORS.accent).attr('fill-opacity', 0.32)
        .attr('stroke', COLORS.accent).attr('stroke-width', 0.6)
    }
    svg.append('text').attr('x', W / 2).attr('y', H - 6)
      .attr('text-anchor', 'middle').attr('fill', COLORS.label).attr('font-size', 9)
      .text('position = geography, area = population')
  }

  choro(elChoro); carto(elCarto); symbol(elSymbol)
}

// --------------------------------------------------------- registry
export const DEMO_BY_ID = {
  'bar-chart':      renderBarChartDemo,
  'stacked-bar':    renderStackedBarDemo,
  'scatterplot':    renderScatterplotDemo,
  'bump-chart':     renderBumpChartDemo,
  'sankey':         renderSankeyDemo,
  'heatmap':        renderHeatmapDemo,
  'line-chart':     renderLineChartDemo,
  'small-multiples':renderSmallMultiplesDemo,
  'slope-chart':    renderSlopeChartDemo,
  'histogram':      renderHistogramDemo,
  'treemap':        renderTreemapDemo,
  'diverging-bar':  renderDivergingBarDemo,
  'parallel-sets':  renderParallelSetsDemo,
  'boxplot':        renderBoxplotDemo,
  'violin':         renderViolinDemo,
  'dot-plot':       renderDotPlotDemo,
  'pie-chart':      renderPieChartDemo,
  'waffle-chart':   renderWaffleChartDemo,
  'chord-diagram':  renderChordDiagramDemo,
  'streamgraph':    renderStreamgraphDemo,
  'ridgeline':      renderRidgelineDemo,
  'connected-scatter': renderConnectedScatterDemo,
  'mosaic':         renderMosaicDemo,
  'dot-map':        renderDotMapDemo,
  'choropleth':     renderChoroplethDemo,
  'hex-bin-map':    renderHexBinMapDemo,
  'cartogram':      renderCartogramDemo,
  'proportional-symbol-map': renderProportionalSymbolMapDemo,
  'flow-map':       renderFlowMapDemo,
  'strip-plot':     renderStripPlotDemo,
  'arc-diagram':    renderArcDiagramDemo,
  'network-diagram':renderNetworkDiagramDemo,
  'matrix-plot':    renderMatrixPlotDemo,
  'sunburst':       renderSunburstDemo,
  'icicle-plot':    renderIciclePlotDemo,
  'stacked-area':   renderStackedAreaDemo,
  'radar-chart':    renderRadarChartDemo,
  'calendar-heatmap': renderCalendarHeatmapDemo,
  'lollipop-chart': renderLollipopChartDemo,
  'box-and-jitter-strip': renderBoxAndJitterStripDemo,
  'dendrogram':     renderDendrogramDemo,
  'gantt-chart':    renderGanttChartDemo,
  'marimekko':      renderMarimekkoDemo,
}

// Patterns whose renderer respects opts.interactive — i.e. they have a
// meaningful static/interactive distinction. Used by the reader to decide
// whether to show a static/interactive toggle above the demo.
//
// A pattern belongs here when ALL of the following are true:
//  - Static render is a valid chart on its own (P4: static-is-the-contract).
//  - Interactive render adds a primary affordance (P10) like hover-tooltip,
//    click-to-isolate, or parameter slider.
//  - Renderer reads `opts.interactive` and skips handler wiring when false.
//
// Patterns that are always-interactive (sliders are the raison d'être)
// stay out of this set — they don't benefit from a "static mode" toggle.
export const INTERACTIVE_PATTERNS = new Set([
  'scatterplot',
  'bump-chart',
  'line-chart',
  'sankey',
  'heatmap',
  'treemap',
  'sunburst',
  'icicle-plot',
  'choropleth',
  'hex-bin-map',
  'cartogram',
  'proportional-symbol-map',
  'dot-map',
  'flow-map',
  'matrix-plot',
  'calendar-heatmap',
  'chord-diagram',
  'mosaic',
  'marimekko',
  'connected-scatter',
  'boxplot',
  'violin',
  'box-and-jitter-strip',
  'streamgraph',
  'stacked-area',
  'gantt-chart',
  'dendrogram',
  'network-diagram',
  'parallel-sets',
  'arc-diagram',
  'slope-chart',
  'small-multiples',
  'radar-chart',
])
