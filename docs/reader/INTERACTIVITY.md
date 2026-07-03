# Interactivity principles for chart-forms-guide demos

*A working document. Each principle names the question it answers;
the rest is examples and tradeoffs. As we add interactive versions of
more patterns, we evolve this doc with what survived the test of
implementation.*

---

## P1. Interactivity must earn its keep

The default is static. Every interactive affordance adds surface area
for bugs, accessibility requirements, mobile-touch equivalents,
keyboard nav, and the reader's cognitive load ("wait, is this
clickable? hoverable?"). Add interactivity only when it unlocks
something the static form genuinely can't show:

- **High-resolution inspection** — scatterplot with 500 points; hover
  reveals the individual observation
- **Many series, few visible at once** — line chart with 10 lines;
  hover one to foreground it
- **Parameter exploration** — histogram where bin width changes the
  story; slider lets the reader see the bin-width dependence directly
- **Hierarchical drill-in** — sunburst where a click zooms to a
  subtree

If the static chart already answers the primary question, *don't*
decorate it with tooltips that just restate what the eye already
saw. A bar-chart tooltip showing "value = 42" on a bar labeled "42"
is pure noise.

## P2. Details on demand, overview by default

Shneiderman's visual-information-seeking mantra: *overview first, zoom
and filter, then details on demand*. The chart loads in overview
state. The reader asks for details — they don't receive an onslaught
of them unprompted.

- No tooltip visible on load
- No highlighted series on load
- No modal/popover open on load

When the reader acts (hover, click, drag), the chart responds.
Resting state = static chart.

## P3. Hover reveals, click commits, drag explores

Affordances are layered by reversibility:

- **Hover** is ephemeral — the reader is browsing, not deciding.
  Tooltips, soft highlights. No state change persists after
  mouseout.
- **Click** commits — the reader has chosen to focus. Filter,
  isolate, expand. Visible "you are here" signal. Click again or
  click background to revert.
- **Drag** is continuous exploration — brush-select, slider,
  pan/zoom. Snap behavior and ghosting to show what's changing.

Don't stack affordances within a chart unless each serves a distinct
task. A scatterplot that does hover-tooltip AND click-isolate AND
drag-to-brush is usually one affordance too many. Pick the one that
matches the primary question this chart is answering.

## P4. The static version is the contract

If interactivity fails — JS disabled, print, screenshot, email
forward, accessibility tool, very old browser — the static chart
must still tell the primary story. Interactivity is enhancement,
never dependency.

Practically:

- No data lives only in tooltips. If the ten biggest values matter,
  label them directly.
- Axes, titles, keys, color meanings — all present in the static
  render.
- The reader who ignores every interactive affordance gets the
  headline.

This is the single biggest difference between journalism-grade charts
(NYT, FT, Reuters graphics) and dashboard-grade charts. Dashboards
often require interaction to learn anything. A journalism chart must
work as a picture.

## P5. Touch is not hover

Every hover interaction needs an explicit touch path. If "hover to
see exact value" is the only way to get the value, ~40% of readers
(mobile, tablet) can't read the chart.

Options in rough order of quality:

- **Tap-to-pin**: first tap shows the tooltip, second tap or tap
  elsewhere dismisses. Works everywhere.
- **Always-on labels** on the most important points, with hover for
  the rest. Degrades to "at least the important stuff is labeled".
- **Summary panel beside chart** that updates on tap/hover.
  Graceful when no tooltip support.

Don't ship "hover to see values" without a touch equivalent — you're
designing for the keyboard you're typing on, not the readers you're
reaching.

## P6. Response budget: ~100ms

Interactive feedback must feel immediate. If the reader drags a
slider and the chart lags 300ms behind, the feel of "I moved my
finger, the chart moved with it" is broken. The interaction becomes
the thing, not the data.

- Pre-compute anything that can be pre-computed (all bin widths, all
  states of a brush-linked chart).
- For expensive recomputation, show an intermediate/approximate
  frame; never a blank.
- 60fps is the target; 30fps tolerable; anything slower is worth
  re-engineering.

If you can't meet the budget, consider whether the interaction was
earning its keep in the first place (see P1).

## P7. Highlight by fading others, not spotlighting one

When the reader selects a series or a subset:

- Keep the non-selected stuff visible but muted (20-30% opacity,
  gray-ish)
- The selection comes forward by contrast, not by being the only
  thing drawn
- Readers retain the comparison context that was the whole point of
  the multi-series chart

Counter-case: when there are so many series that even muted they
create visual noise, hide them. But even then, provide an obvious
"show all" signal.

## P8. Reveal the rule, not just the example

When a control changes the chart, show the reader what the control
maps to in the chart's vocabulary:

- "Bin width = 5" next to a histogram slider
- "Showing years 2010–2020" next to a brush
- "Sorted by: revenue ↓" next to a sort button

The reader should leave knowing something about the encoding, not
just having seen three different-looking charts. Teach, don't just
toggle.

## P9. Accessibility is structural, not decorative

- Every interactive element reachable by keyboard (Tab order,
  Enter/Space activation, arrow keys for continuous controls)
- Visible focus ring — not the default browser dotted line, but a
  styled ring that fits the design
- `aria-label` on interactive SVG elements; hidden live region for
  value-changes when screen reader is active
- `prefers-reduced-motion` respected: no bouncy transitions, no
  ambient animation
- Color-not-the-only-signal: selection, highlight, error all carry
  a shape or pattern cue in addition to color

This is work that has to be designed in from the start; retrofitting
is painful and usually partial.

## P10. One primary affordance per chart

Charts in the guide are teaching examples, not dashboards. Pick the
single affordance that best demonstrates what makes this form
interactive, and make that one affordance excellent:

- Scatterplot → hover-tooltip (P1: high-res inspection)
- Line chart (many series) → voronoi-hover to select a line
- Bump chart → click or hover to isolate one line's trajectory
- Sankey → click a node to dim non-connected flows
- Heatmap → hover for cross-hair + value
- Treemap / sunburst → click a cell to zoom in
- Histogram → slider for bin width (parameter exploration)
- Boxplot / violin → hover for summary stats

Resist adding "and also click for legend toggle, and also
double-click to reset, and also drag to...". The teaching chart
should demonstrate the affordance, not the full feature surface of
an imaginary product.

## P11. Form-fit the viewport: three modes for mobile

A chart loaded on a phone is not a smaller copy of the desktop chart.
It's a different reader's encounter with the same data: shorter
dwell time, no hover, imprecise touch targets, a viewport that's
often narrower than some charts' meaningful minimum. Every chart
needs an explicit answer to "what happens on a 375px-wide screen?".

Four answers, in rough order of effort:

**1. Responsive — the chart works as-is.** Bars, lines, small
multiples (if you drop to 1-2 columns), pie/waffle, strip plots,
histograms — forms where the encoding doesn't depend on dozens of
visible marks. Adjust label density, tick count, and legend
placement to the viewport; everything else scales. Most of this
guide's 43 patterns sit here.

**2. Graceful degradation — the chart works with reduced
affordances.** On desktop, a scatterplot has hover-tooltip over 500
points. On mobile, the voronoi tap targets are too small for
fingers and hover doesn't exist. Ship the static chart + a short
list of labeled "worth-looking-at" points (the outliers already
annotated in the static contract, P4). The reader loses
high-resolution inspection but keeps the headline and the notable
cases. Clearly communicate the reduction ("Tap a highlighted point
for detail" beats silent failure).

**3. Alternate form — ship a different chart.** When the underlying
form genuinely cannot be legible below some width, don't pretend.
Detect the viewport and render a form that was designed for it.
Canonical example: an NCAA-tournament bracket. At desktop width,
64 teams fan out across seven rounds; at phone width, that bracket
is a microfiche. The right mobile answer is not a scrollable,
pinch-to-zoom desktop bracket — it's a round-by-round slideshow, or
a "pick a region" drill-in, or a stack of matchups ordered by
game time. Same data, different form, each designed for its
reader.

**4. Escape hatch — when alternate-form isn't practical.** If
(3) isn't feasible — a commissioned one-off, a deadline, a dashboard
whose cell complexity doesn't have a reasonable mobile cousin — do
not ship a "try harder on mobile, sorry" experience. Ship an
explicit signal: a full-viewport panel that says "this visual is
designed for wider screens — rotate your phone, or open on a
tablet / laptop" with a thumbnail and a summary of what the chart
shows. A one-sentence summary the mobile reader takes away, a link
for when they're back at a bigger screen. Silent squishing is the
worst of all four options.

### Deciding which mode

Start by asking: **below what viewport width does the chart stop
being legible?** Then:

- If that width is under ~360px: mode 1 (responsive). Just tidy the
  labels.
- 360-480px: mode 2 (degradation). Drop hover affordances, label the
  notable points, keep the story.
- 480-640px: mode 3 (alternate form) *if* the alternate is
  well-trodden and shipping it costs less than the ongoing support
  cost of a cramped chart. Otherwise mode 4 with a good
  summary.
- Above ~640px unusable: mode 4 (escape hatch) is honest. Don't
  promise what you can't deliver.

### Implementation tactics

- Feature-test touch, not viewport width alone: a desktop browser at
  375px wide is a dev tool, a 1024px Surface Pro might be the user's
  touch device. Use `matchMedia('(pointer: coarse)')` for input type
  and `matchMedia('(max-width: ...)')` for space.
- `prefers-reduced-motion` matters more on mobile (often paired with
  battery-saving modes and smaller-device fatigue). Already in P9.
- Respect safe areas (notches, bottom bars) when the chart is
  full-viewport.
- Network: mobile sessions often include one-bar connections. If
  interactive assets are heavy, ensure the server-rendered / static
  fallback is the first paint.

### Regression

Viewport-specific regressions need their own check — the review
harness currently renders at 1200×900 (desktop). Adding a
phone-sized pass (375×667) would catch label clipping and
illegible-at-small patterns before they ship. Open TODO.

---

## How we apply these in the guide

**Default render mode is interactive** for patterns that have an
interactive version. The reader can flip to "static" via a toggle
above the demo (for print, accessibility preference, or curiosity
about what the static contract looks like).

**Static-only patterns** still exist — not every form benefits from
interactivity, and that's fine. The toggle only appears where there's
a meaningful static/interactive distinction to make.

**Interactive affordance = one per chart** (P10). If we find a second
natural one, we note it in the pattern's prose ("you could also
...") rather than implementing it.

**Regression coverage**: the `#/review` harness renders the *default
(interactive) mode, settled state* of every demo. It doesn't
synthesize interaction events. What it verifies is P4 — that the
visible, resting state of an interactive chart is a valid static
chart.

---

## Evolution log

*Changes to this doc as we implement. Dated entries so we can trace
what learned-through-doing.*

- **2026-04-23 (draft)** — initial ten principles, based on
  Shneiderman 1996, Segel/Heer 2010, working practice at NYT/FT/
  Reuters graphics teams, and accessibility guidelines (WCAG 2.2
  targets for interactive charts). To be tested against real
  implementations starting with scatterplot.

- **2026-04-23 (after 3 implementations)** — Scatterplot (hover +
  click-pin), bump chart (hover-label-isolate + click-pin), line chart
  (time-cursor + multi-series readout). All three hold up. Refinements:

  - **P3 note**: "click commits" doesn't always mean hide-others
    permanently. On scatterplot, click-pin is about persistence
    (tooltip survives mouse-move-away), not about hiding the rest.
    The selected point stays highlighted; the other points stay
    faded; pressing-click-again restores. The reader is "parking"
    their attention, not filtering.

  - **P5 added nuance**: line chart's "tap to move the cursor" is
    different from scatterplot's "tap to pin". For continuous-input
    interactions (sliders, time cursors), tap-and-stay doesn't really
    make sense — the reader wants *to move the control*. Touch
    support = treat tap like mouse-down-and-drag, not like click-pin.

  - **P10 corollary**: the static/interactive toggle itself is an
    affordance. Count it. A chart with slider + hover-tooltip + the
    toggle is really three affordances. For now the toggle is light
    enough (one of two states, at the top, not competing with the
    chart) that it doesn't blow the budget.

  - **Architecture decision**: renderer signature is
    `renderFooDemo(container, opts={})` where `opts.interactive`
    defaults to `true`. Static-only renderers ignore `opts`. An
    `INTERACTIVE_PATTERNS` set in `live-examples.js` is the source of
    truth for which demos show the toggle.

  - **Regression**: review harness (`npm run check:chart-forms`)
    renders in default (interactive) mode, resting state — which
    must match the static visual contract (P4). The separate
    `npm run check:chart-forms:interactive` script exercises events.
    Adding new interactive patterns means adding them to both the
    INTERACTIVE_PATTERNS set and (ideally) the interactive check
    script.

  - **TODO surfaced, not yet implemented**: keyboard nav to
    individual data points in scatterplot (arrow keys cycle the
    voronoi, Enter pins). P9 aspiration, not currently met — only
    the mode-toggle itself is keyboard-reachable. Same gap on bump
    and line charts. Fix when we do the next round, or accept that
    rich keyboard nav for 500-point scatterplots is a different
    kind of chart than we're building here (tables work better).

- **2026-04-23 (mobile / viewport refinement)** — Added P11 to make
  explicit what P5 only implied: mobile is a different reader, not a
  smaller screen. Four modes (responsive / graceful degradation /
  alternate form / escape hatch). The NCAA-bracket example is the
  reference case for "alternate form": don't squish a 64-team
  tournament bracket onto 375px — ship a round-by-round or
  pick-a-region mobile experience instead.

  Implications for this guide's current demos:

  - All 43 demos use SVG + `viewBox` so they auto-scale. Most are
    mode 1 (responsive) and currently fine.
  - Interactive demos (scatterplot, bump, line) rely on hover. On
    touch the `.on('click', ...)` handlers work as fallback pin
    controls, but this is degradation-by-accident, not by design.
    A real P11 pass would explicitly implement mode 2: detect
    `(pointer: coarse)` and either swap the affordance or annotate
    the "look at these points" set more prominently.
  - Some patterns (sankey with many nodes, dendrogram with 12 leaves,
    matrix-plot with a 10×10 grid, the four full-CONUS maps) will
    cross into mode 2 or 3 territory below ~480px. Currently they
    silently squish.

  None of this is yet implemented — this entry captures the
  principle and the known gaps so the next pass (or the next
  iteration's CEO/design review) has a concrete target.

  Also added: `matchMedia('(pointer: coarse)')` as the recommended
  feature-test, not viewport width alone. A 1024px tablet with a
  finger is still "touch mode"; a 375px-wide desktop dev window is
  not. This refinement makes our future mobile work avoid the
  classic "responsive CSS fooled us" trap.

- **2026-04-23 (after 5 implementations)** — Added sankey
  click-to-isolate (with "dim don't hide" — the roadmap's specific
  sankey ask) and heatmap cross-hair + cell readout. Five interactive
  patterns now covered: scatterplot, bump, line, sankey, heatmap.
  The `check:chart-forms:interactive` script grew into a 21-assertion
  suite across those five, structured with a shared `ok()` helper so
  adding more patterns is one section of copy-paste.

  Refinements:

  - **"Restore to default" is its own state.** Sankey ribbons render
    at opacity 0.55 by default; when a node is selected, connected
    ribbons go to 0.85 and others fade to 0.08. Un-pinning can't just
    "clear the highlight" — it has to know the default value.
    Initially I wrote `isRibbonConnected(r, null) → true → opacity =
    0.85`, which left every ribbon at 0.85 after unpin (test caught
    it). The fix: branch explicitly on `selected == null ? 0.55 :
    (on ? 0.85 : 0.08)`. Generalize: interactive renderers need a
    clear model of *three* states (default, highlight-on, highlight-
    off), not two.

  - **Reserve layout gutters for interactivity hints up front (P8).**
    The sankey "click a node to isolate its flow" hint initially
    landed on top of the existing "losses closes the balance"
    caption. They shared `y = H-8` with different `text-anchor`s —
    static visually they'd probably not overlap, but the regression
    checker flags any overlap-risk. Lesson: reserve a designated
    "hint zone" in the viewBox layout rather than adding hints
    wherever space looks free after the fact.

  - **P10 discipline holds up.** Sankey's click-to-isolate didn't
    need a hover preview. Heatmap's cross-hair didn't need
    click-to-pin. Resisting the temptation to stack affordances kept
    each chart's interaction legible; a reader who learns "click
    sankey nodes" doesn't also have to learn "hover sankey ribbons
    for value". The teaching chart stays a teaching chart.

  - **Touch turns out to partition naturally.** Of the five: two are
    click/tap primary (sankey, scatterplot-via-pin), three are
    hover-with-tap-fallback (bump, line, heatmap). Both classes work
    on touch because the `.on('click', ...)` handler fires on tap.
    No pattern here needed explicit touch-event plumbing — but a
    genuine brush-or-drag affordance would (P11 mode 2 territory).

- **2026-04-24 (33/43 — interactivity pass complete)** — 33 patterns
  now carry a static/interactive toggle, verified by a 100-assertion
  suite. Three patterns (histogram, ridgeline, strip-plot) are
  always-interactive via parameter sliders and stay out of the set.
  Seven patterns (bar, stacked-bar, diverging-bar, dot-plot,
  lollipop, pie, waffle) were intentionally skipped: their static
  rendering already labels every value directly, so a hover tooltip
  would just restate what the eye already saw — P1 "earn its keep"
  fails.

  Patterns that demanded special care (not just "hover for tooltip"):

  - **treemap, sunburst, icicle-plot**: click-to-zoom drill-in via
    re-layout on the focused subtree. Breadcrumb navigation;
    click-background-to-zoom-out. Three renderers, shared model.

  - **sankey, parallel-sets**: click-to-isolate with "dim don't hide"
    so the comparison context survives (sankey common_mistake). Three
    visual states (default / highlight-on / highlight-off) — treating
    "clear selection" as "remove highlights" breaks, since the
    default opacity differs from both selection states.

  - **proportional-symbol-map**: voronoi-backed nearest-center lookup
    so hovering the interior of NYC's big blob gives you NYC, not
    Philadelphia on top of it. Real UX bug, not just a test artifact.

  - **network-diagram**: hover node spotlights node + edges + one-hop
    neighbors, fading the rest. Degree count in tooltip.

  - **connected-scatter / scatterplot / radar / dot-map**: voronoi
    hover so small dot targets stay usable — generous hit areas
    driven by nearest-center, not mark bounding-box.

  Testing tactics that paid off:

  - Per-pattern selectors (`.chord-ribbon[data-source="0"]`, etc) let
    the check suite hover specific marks without mouse-coordinate
    math.

  - SVG `<path>` bbox-center often isn't on the curve — the checker
    uses `getPointAtLength(total/2)` projected through `getScreenCTM`
    to find a pixel on the curve.

  - Multiple patterns rendering on one family page means the cursor
    from a prior test can trigger the next pattern's hover before
    we check "initial hidden". Fix: park cursor at (5,5) between
    each test case.

  - Overlay rectangles at the SVG level (voronoi-style) work better
    than per-mark handlers when marks overlap (proportional-symbol)
    or have thin strokes (slope-chart, dendrogram merges) that are
    hard to hit with a finger. Hit-target size is an explicit design
    decision, not a side effect of mark size.

  - `fill=none` stroke-only SVG elements need `pointer-events: all`
    to receive hovers over their interior. Found via a gantt test
    failure.
