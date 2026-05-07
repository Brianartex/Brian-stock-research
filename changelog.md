# Changelog

All notable changes to the [Brian Stock Research Site](https://Brianartex.github.io/Brian-stock-research/) are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Versions are tied to GitHub releases.

---

## [Unreleased]

### Added
- **Orchestration layer** — `project_state.md`, `todo.md`, `changelog.md` for persistent session memory
- **Project state skill** — auto-loads at session start, updates after major tasks

### Changed
- **Tech_Stock_Basket_May_2026_v2.html** — Per-card stats insertion with real yfinance data
  - Replaced placeholder stat-row blocks with live `quick-stats` (price action: 6M/90D/30D/YTD; fundamentals: revenue, FCF margin, gross margin, net cash, GAAP op. margin)
  - Clean CSS replacement: mobile responsive (Galaxy S21/768px breakpoint), hamburger nav, ADA compliance
  - Orphaned `stats-section`/`fund-section` blocks removed (1,786 lines deleted, 369 lines added)
  - Hamburger nav HTML + JS injected (`mobile-topbar`, `nav-overlay`, `hamburger-btn`)
  - 15 of 17 stock cards updated (SKIP cards STX, MU excluded by design)

---

## [2026-05-07] — Major Polish Sprint

### Added
- **ADA compliance** — Skip-to-content link, `aria-label` on sidebar nav, focus ring CSS, labeled external links
- **Mobile responsive CSS** — Galaxy S21 / 768px breakpoint with `padding-left:0` on body, stacked grids, full-width cards
- **Hamburger mobile nav** — `mobile-topbar` fixed to top, `nav-overlay` fullscreen drawer with close button
- **Inline SVG sparklines** — All 14 stocks in visual docs
- **References section** — Full inline citations with working URLs, added to TOC of all docs
- **Price action bar + fundamentals grid** — Visual docs only (v2_visual)
- **CRT scanline background** — Index page styled with retro display effect

### Changed
- All 4 docs (Tech v2, Tech v2_visual, Geo v2, Geo v2_visual) received: desktop TOC fix, mobile hamburger, Galaxy S21 responsiveness, 28 clickable citation links (Geopolitical), references in TOC
- GitHub Pages URL corrected: `https://Brianartex.github.io/Brian-stock-research/`

### Fixed
- Desktop TOC overlap with content (body padding-left:230px)
- Geopolitical docs: `::before` pseudo-element removed from TOC links (overlap fix)
- STX badge: `LATE→SKIP` label corrected

---

## [2026-04-30] — Initial Tech Basket + AVICI Research

### Added
- **Tech_Stock_Basket_Analysis_April_2026.html** — Tier 1 basket analysis: DOCU, OKTA, SNOW, RNG, TEAM, TWLO, ZM, PATH, SMAR
- **Crypto_Deep_Dive_Avici_Clearpool_v2.html** — AVICI token research (Solana/Clearpool), FDV=$11M, ~20-22% MoM growth, SEC Privits risk flagged

### Changed
- `$20K taxable brokerage` identified as liquid investment capital (5+ year horizon)
- Stock basket thesis: "AI eating SaaS" concern documented
