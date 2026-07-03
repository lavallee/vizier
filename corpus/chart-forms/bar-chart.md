---
id: bar-chart
source: chart-forms
type: chart_pattern
title: Bar chart
tags: [bar, magnitude, categorical, default]
details:
  purpose_families: [Magnitude, Ranking]
  capsule: >
    The default form for comparing magnitudes across categories. Length
    along a shared axis is the strongest visual encoding humans have.
    Horizontal bars work best for ranked labels; vertical for ordered
    categories like time bins.
  when_to_use:
    - Comparing magnitudes across a discrete set of categories
    - Values should be read precisely — length on a shared axis is the most accurate encoding
    - Categories are nameable (not continuous) and few enough to fit on an axis
    - Reader wants "which is biggest?" answered at a glance
  when_not_to_use:
    - Values are best understood as parts of a whole — use stacked bar
    - The pattern is about change over continuous time — use a line chart
    - You have too many categories to fit readable labels (>~25) — switch to strip plot or ranked list
    - Categories are really continuous-binned data — use a histogram
  reading_checklist:
    - Does the value axis start at zero? If truncated, the bar-length comparison is misleading.
    - Are bars sorted by magnitude or by some meaningful order — or alphabetically (= wasted)?
    - Highlight color — is one bar singled out as the subject? Or are all bars equal weight?
    - Labels — inside the bars or outside? Do they fit at the shortest bar?
  common_mistakes:
    - Y-axis truncated without disclosure — readers compare lengths, so cutting the baseline deceives
    - Alphabetical category order — sort by magnitude unless the categories have a semantic order
    - Vertical bars with long labels — use horizontal bars
    - Color used to encode magnitude (already on the length) — save color for a second dimension or an accent
    - Evenly-spaced categories on the x-axis when they represent unequal time intervals — use a time-axis chart instead
    - A single-bar "chart" — the number is the story; use a stat tile / hero figure, not one lonely bar
  alternatives:
    - id: dot-plot
      when: Many categories, small magnitudes — dots are tidier than many thin bars
    - id: stacked-bar
      when: Each bar splits into meaningful parts
    - id: line-chart
      when: The x-axis is really continuous time
    - id: histogram
      when: The "categories" are actually value bins
    - id: pie-chart
      when: Exactly 2-3 slices, dominant one is the only story (rare)
    - id: slope-chart
      when: Two time points for many categories; slope lines show change
  canonical_examples:
    - visualising-data/five-ways-to-present-bar-charts
    - eagereyes/evaluation-of-the-impact-of-visual-embellishments-in-bar-charts
    - junkcharts/when-should-we-use-bar-charts
  antipattern_examples:
    - eagereyes/stacked-bars-are-the-worst
    - cairo-blog/was-this-done-on-purpose-html
  related_principles: []
---
The bar chart is the form most reached for and most deserving of being
reached for. Humans read length on a shared axis more accurately than
any other visual encoding — better than angle (pie), area (bubble),
color intensity (heatmap), or position in 2D (scatter). If a bar chart
works for your data, use one; the novelty tax of picking something
else is rarely worth it.

**Works when**: you have a discrete set of nameable categories and
you want readers to compare magnitudes. Horizontal bars are usually
better than vertical for readable labels (names read left-to-right
naturally), and almost always better when categories need to be
sorted by magnitude.

**Fails when**: the data isn't actually categorical. A "bar chart of
temperature over the year" should be a line chart — the x-axis is
continuous. A "bar chart of test scores" should be a histogram — the
bars represent value bins, and the distribution's shape is the story.

**When to sort by magnitude**: almost always. Alphabetical ordering
is a default to resist unless the categories have a meaningful
sequence (months, ballot order, supply-chain stages). Magnitude order
lets readers answer "which is biggest?" by scanning top-to-bottom.

**Cosmetic choices**: (a) y-axis starts at zero — non-negotiable for
bar charts. Bar length encodes magnitude, so truncation is a
misrepresentation, not an editorial choice. (b) bar width should
fill most of its slot; thin bars waste the visual channel. (c) one
accent color against neutrals when a single bar is the subject of
the story.
