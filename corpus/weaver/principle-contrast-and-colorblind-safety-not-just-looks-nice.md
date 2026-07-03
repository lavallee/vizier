---
details:
  origin: weaver/PRINCIPLES.md
  stage: Build
fetched_at: '2026-04-18T19:23:27.593522Z'
id: principle-contrast-and-colorblind-safety-not-just-looks-nice
source: weaver
tags:
- build
title: Contrast and colorblind-safety, not just "looks nice"
type: principle
---

Every bar-on-color label has to pass contrast *algorithmically*, not by eye.
Designers-eyes lie; dark text on teal looks fine to most but fails against
tritanopia or low-vision readers, and SVG attribute/CSS interactions
routinely swap your text color without you noticing.

Discipline:

- **Compute text color from background luminance.** Use a helper like
  `onBarText(hex)` that returns near-black or near-white based on WCAG
  relative luminance. Target ≥ 4.5:1 contrast (WCAG AA for normal text).
  In this project: `onBarText()` at ~55% luminance threshold.
- **Prefer `.style('fill', ...)` over `.attr('fill', ...)` on SVG text.**
  A CSS class (e.g., `.bar-value { fill: #a3a3a3 }`) silently wins
  against an SVG `fill` attribute. Inline `style` beats both. If you
  see unexpectedly gray text on a colored bar, this is almost always
  the cause.
- **Encode information with more than color.** Don't rely on
  red-vs-green alone — protanopia/deuteranopia wipes that distinction
  for ~8% of men. In this project, race tiers are encoded by color
  *and* by consistent vertical position within each community block, so
  the cliff is legible even if the bars all looked the same color.
- **Prefer cyan/orange/purple over red/green** when you only have color
  to work with. These pairs are distinguishable for the common
  colorblindness patterns.
- **Test in grayscale.** If your viz loses meaning when screenshotted
  and desaturated, it's over-relying on color.
- **Honor `prefers-reduced-motion` and `prefers-contrast`.** Don't
  animate for readers who asked you not to; offer higher-contrast
  palettes where you can.

---
