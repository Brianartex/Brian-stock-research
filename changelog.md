# Changelog

All notable changes to the [Brian Stock Research Site](https://Brianartex.github.io/Brian-stock-research/) are documented here.

Format inspired by [Keep a Changelog](https://keepachangelog.com/). Versions are tied to GitHub releases.

---

## [Unreleased] — 2026-05-07

### Fixed — All Docs
- **Tech v2 + v2_visual:** Remove orphaned stats-blocks (138 lines each, positioned outside `<details>` elements). Insert `quick-stats` price-action grid + fundamentals grid in 15 active stock cards. Replace CSS with clean consolidated stylesheet. Add hamburger nav for mobile. ([21bb0e5](https://github.com/Brianartex/Brian-stock-research/commit/21bb0e5))
- **Tech v3 + v4:** Clean CSS refresh (removed stale mobile overrides). Add hamburger nav for mobile. Cards already had complete `price-action-bar` + `fundamentals-grid` — no content surgery needed. ([21bb0e5](https://github.com/Brianartex/Brian-stock-research/commit/21bb0e5))
- **Geopolitical v2 + v2_visual:** Clean CSS refresh (CSS shrank ~5KB by removing redundant rules). Add hamburger nav for mobile. Visual preserves Chart.js, sectorChart, spikeChart. ([21bb0e5](https://github.com/Brianartex/Brian-stock-research/commit/21bb0e5))

### Added — Orchestration Layer
- **`.project_state.json`** — Machine-readable project state. Loaded first at every session start via `project-state` skill. Tracks file status, blockers, approach, and pending work.
- **`todo.md`** — Roadmap of all active projects. Updated on every state commit.
- **`changelog.md`** — Append-only changelog. Generated from git commits. Follows Keep a Changelog format.
- **`project-state` skill** — Loads `project_state.json` at session start, enforces state update after complex tasks.

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

## [2026-05-12] — v5 Deep-Dive: PENG Added + Prices Refreshed

### Added
- **PENG (Penguin Solutions)** — Added to deep-dive v5 as Pick #11 ($200 / 10%). Photonic Memory Appliance (PMA) for Marvell using Celestial AI silicon. Rosenblatt Buy rating, $54 target (up from $32). SK Telecom $200M investment at $32.80. H1 FY26 AI-driven revenue >50% YoY. Needham conference confirmed CXL-based KV Cache product.
- **investment-deep-dive-v5.html** — 10-pick asymmetric basket with macro dashboard, performance tracker, position sizing, earnings calendar, stop-losses. FLNC overhang alert added post S-3ASR. SIVE added as 10th pick (CPO/photonics).
- **Morgan action sheet** — Discord-only actionable doc with allocations, entries, stops, and buying sequence. Sent to #investment.
- **index.html** — Archive restructured: hierarchical by document → month → week with version links. External section removed.
- **archive.html** — Full version history page with all historical releases, dates, and version numbers.
- **Tech doc v3** — Watchlist section added with AMBA (edge AI/robot vision, $60–65 target) and VICR (power modules, scouting). Scouting list for WYFI/NBIS/CRWV.
- **project_state.json** — Created with machine-readable state of all docs, blockers, upcoming dates, and pending work.

### Changed
- **Deep-dive v5 rebalanced** — FLNC trimmed $200→$100 (shelf overhang), MU $300→$250, ANET $250→$200, VST $200→$150, SIVE $200→$150. Total stays $2,000.
- **Deep-dive v5 prices refreshed** — All 11 pick prices updated to May 12 close. Performance tracker updated.
- **Tech doc v3** — All 23 inline prices refreshed to May 12 afternoon. QCOM re-rated to WATCH after -11.5% broad-tech drop (no company-specific news). P/E compressed to 19.8x forward. Entry target revised to $175–180.
- **Morgan approved** for Discord bot pairing (user ID: 894243263777763389).

### Fixed
- **Vision API** — Permanently fixed by removing `api_key: ''` from config.yaml auxiliary.vision. Now resolves from .env via `get_env_value()`.
- Desktop nav bar TOC overlap — shifted right by `--toc-width` so nav links are fully clickable.
- SIVE card nesting — added missing `</div>` closures so SIVE renders as sibling to VST, not child.
- Orphaned risk-meter dots removed from below SIVE card.
- Archive TOC clipping — removed inline `max-height:0` constraints; expanded groups use 2000px.

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
