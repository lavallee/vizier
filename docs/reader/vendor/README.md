# Vendored dependencies

- **`d3.min.js`** — D3.js v7.9.0, a self-contained ES-module bundle (all
  submodules inlined; no external imports). Vendored so the chart-forms guide
  serves as static files with no build step and no CDN dependency. D3 is
  © Mike Bostock, ISC License — <https://github.com/d3/d3/blob/main/LICENSE>.

Regenerate with:

```bash
curl -sL "https://esm.sh/d3@7/es2022/d3.bundle.mjs" -o d3.min.js
```
