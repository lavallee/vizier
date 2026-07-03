// Headless regression check for the chart-forms-guide #/review harness.
// Navigates a headless browser to the review page, waits for every demo
// to render + run its automated issue check, reads the total count off
// the DOM, and exits non-zero if any issues are flagged.
//
// Usage:
//   BASE=http://localhost:5176 node projects/chart-forms-guide/check-review.mjs
//   (defaults BASE to http://localhost:5173 if unset)

import { chromium } from 'playwright'

const BASE = process.env.BASE || 'http://localhost:5173'
const URL = `${BASE}/projects/chart-forms-guide/#/review`

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 } })
const page = await ctx.newPage()

const consoleErrors = []
page.on('console', msg => {
  if (msg.type() === 'error') consoleErrors.push(msg.text())
})
page.on('pageerror', err => consoleErrors.push(`pageerror: ${err.message}`))

await page.goto(URL, { waitUntil: 'networkidle' })

// Each demo schedules a setTimeout(300) for its check. Give a generous
// margin — force sims settle, d3 transitions, kde computations.
await page.waitForTimeout(2500)

// Read totals directly from the DOM. The harness emits either
// "✓ automated checks clean" or "N issues flagged:" per demo.
const result = await page.evaluate(() => {
  const lis = Array.from(document.querySelectorAll('li'))
  let flagged = 0
  let clean = 0
  const perDemo = []
  for (const li of lis) {
    const txt = (li.textContent || '')
    const m = txt.match(/^(\d+) issues flagged:/)
    if (m) {
      flagged += parseInt(m[1], 10)
      const sec = li.closest('section.pattern')
      perDemo.push({
        id: sec?.id?.replace('review-', '') || '?',
        count: parseInt(m[1], 10),
      })
    } else if (txt.includes('automated checks clean')) {
      clean += 1
    }
  }
  const demos = document.querySelectorAll('section.pattern').length
  return { flagged, clean, demos, perDemo }
})

console.log(`chart-forms-guide review harness → ${result.demos} demos, ${result.clean} clean, ${result.flagged} flagged issue${result.flagged === 1 ? '' : 's'}`)
if (result.clean + (result.perDemo.length) !== result.demos) {
  console.log(`WARNING: ${result.demos - result.clean - result.perDemo.length} demos didn't report status (render error?)`)
}
if (result.flagged > 0) {
  for (const d of result.perDemo) console.log(`  ${d.id}: ${d.count}`)
}
if (consoleErrors.length) {
  console.log(`${consoleErrors.length} console errors:`)
  for (const e of consoleErrors) console.log(`  ${e}`)
}

await browser.close()
const missing = result.demos - result.clean - result.perDemo.length
process.exit(result.flagged > 0 || consoleErrors.length > 0 || missing > 0 ? 1 : 0)
