#!/usr/bin/env python3
"""
Daily stock data refresh for Tech v3 and Deep-Dive v4 docs.
Uses yahooquery for data fetching.
"""

import re
import sys
import json
from datetime import datetime
from pathlib import Path

from yahooquery import Ticker

TECH_V3 = "Tech_Stock_Basket_May_2026_v3.html"
DEEP_DIVE_V4 = "investment-deep-dive-v4.html"

TECH_TICKERS = [
    "DOCU","SNOW","OKTA","MNDY","VEEV","DDOG","ANET","GLW","AMKR",
    "ETN","LUMN","QCOM","NTAP","AEP","VST","STX","MU","HIMX",
    "AOSL","AMPX","SMCI","ARM","MRVL"
]
DEEP_DIVE_TICKERS = ["FLNC","AAOI","MU","SMCI","SNDK","APH","ANET","AMPX","VST"]
ALL_TICKERS = list(dict.fromkeys(TECH_TICKERS + DEEP_DIVE_TICKERS))

today = datetime.now()
date_str = today.strftime("%B %d %Y")
print(f"{'='*60}")
print(f"Stock data refresh — {date_str}")
print(f"{'='*60}")

# ── 1. Fetch fresh data ──────────────────────────────────────────
print("\nFetching current prices and history...")
t = Ticker(ALL_TICKERS)
prices_raw = t.price

# Fetch full price history for returns
hist = None
try:
    hist = t.history(period="6mo")
    if hist is not None and not hist.empty:
        print(f"  Got {len(hist)} history rows")
    else:
        hist = None
except Exception as e:
    print(f"  History fetch failed: {e}")

prices = {}
for sym in ALL_TICKERS:
    d = prices_raw.get(sym)
    if not d:
        print(f"  WARNING: No data for {sym}")
        continue
    rp = d.get("regularMarketPrice")
    if rp is None:
        print(f"  WARNING: No regularMarketPrice for {sym}")
        continue
    prices[sym] = rp
    prev = d.get("regularMarketPreviousClose")
    chg = d.get("regularMarketChangePercent")
    chg_str = f" (prev ${prev:.2f}, {chg*100:+.2f}%)" if prev and chg else ""
    print(f"  {sym}: ${rp:.2f}{chg_str}")

if not prices:
    sys.exit("FATAL: No prices fetched.")

# ── Pre-compute period returns ───────────────────────────────────
def get_returns(sym):
    """Return {period: return_pct} for a ticker."""
    if hist is None:
        return {}
    try:
        sh = hist.xs(sym, level=0)
    except Exception:
        try:
            sh = hist.xs(sym, level=0)
        except Exception:
            return {}
    if sh.empty:
        return {}
    closes = sh['close'].sort_index()
    if len(closes) < 2:
        return {}

    today_c = closes.iloc[-1]
    r = {}
    for label, days in [("6M", 126), ("90D", 63), ("30D", 21)]:
        if len(closes) > days:
            past = closes.iloc[-(days+1)]
            if past > 0:
                r[label] = (today_c - past) / past * 100
    # YTD
    year_start = "2026-01-01"
    try:
        dates = sh.index.get_level_values('date')
        mask = dates >= year_start
        if mask.any():
            first_idx = mask.argmax()
            ytd_open = closes.iloc[first_idx]
            if ytd_open > 0:
                r["YTD"] = (today_c - ytd_open) / ytd_open * 100
    except Exception:
        pass
    return r

ret_cache = {sym: get_returns(sym) for sym in TECH_TICKERS}
print(f"\n  Returns computed for {sum(1 for v in ret_cache.values() if v)} tickers")

# ── 2. Read files ──────────────────────────────────────────────
with open(TECH_V3, "r", encoding="utf-8") as f:
    tech = f.read()
with open(DEEP_DIVE_V4, "r", encoding="utf-8") as f:
    dive = f.read()

tech_orig = tech
dive_orig = dive

# ── 3. Update Deep-Dive v4: current prices ONLY ────────────────
print("\n--- Deep-Dive v4 ---")
dive_changes = []

for sym in DEEP_DIVE_TICKERS:
    if sym not in prices:
        continue
    np = prices[sym]
    # Format: comma for >= 1000
    nps = f"${np:,.2f}" if np >= 1000 else f"${np:.2f}"
    old_np_str = None

    # 3a. pick-ticker price span
    # Pattern: <div class="pick-ticker">TICKER <span style="font-size:16px;font-weight:500;color:var(--text-dim);margin-left:8px;">$OLD</span></div>
    pt = re.compile(
        rf'(<div class="pick-ticker">{re.escape(sym)} <span style="font-size:16px;font-weight:500;color:var\(--text-dim\);margin-left:8px;">)(\$[0-9,]+\.\d+)(</span></div>)'
    )
    m = pt.search(dive)
    if m:
        ops = m.group(2)
        old_np_str = ops
        if ops != nps:
            dive = dive[:m.start()] + m.group(1) + nps + m.group(3) + dive[m.end():]
            print(f"  {sym} pick-ticker: {ops} -> {nps}")

    # 3b. "(stock at $OLD)" in Wall Street box
    idx = dive.find(f'class="pick-ticker">{sym}')
    if idx >= 0:
        sa = re.search(r'\(stock at (\$[0-9,]+\.[0-9]+)\)', dive[idx:idx+3000])
        if sa:
            ops = sa.group(1)
            if ops != nps:
                sa_start = idx + sa.start()
                sa_end = idx + sa.end()
                dive = dive[:sa_start] + f"(stock at {nps})" + dive[sa_end:]
                print(f"  {sym} wall-st: {ops} -> {nps}")

    # Track changes
    if old_np_str is not None and old_np_str != nps:
        try:
            old_v = float(old_np_str.replace("$","").replace(",",""))
            new_v = float(nps.replace("$","").replace(",",""))
            pct_chg = (new_v - old_v) / old_v * 100
            flag = " **" if abs(pct_chg) > 10 else ""
            dive_changes.append((sym, old_np_str, nps, pct_chg, flag))
        except ValueError:
            pass

# ── 4. Update Tech v3: full refresh ─────────────────────────────
print("\n--- Tech v3 ---")

tech_changes = []

for sym in TECH_TICKERS:
    if sym not in prices:
        continue
    np = prices[sym]
    nps = f"${np:.2f}"
    syml = sym.lower()
    sym_ret = ret_cache.get(sym, {})

    # Find this stock card
    card_tag = f'<details class="stock-card" id="{syml}">'
    cs = tech.find(card_tag)
    if cs == -1:
        print(f"  {sym}: card not found")
        continue
    ce = tech.find("</details>", cs)
    if ce == -1:
        ce = cs + 8000

    old_price_str = None

    # 4a. Ticker price in summary header
    tp = re.compile(
        rf'(<div class="ticker" style="display:inline;margin-right:10px;">{re.escape(sym)} <span style="font-size:14px;font-weight:500;color:var\(--text-dim\);margin-left:6px;">)(\$[0-9]+\.\d+)(</span>)'
    )
    m = tp.search(tech, cs, ce)
    if m:
        ops = m.group(2)
        old_price_str = ops
        if ops != nps:
            tech = tech[:m.start()] + m.group(1) + nps + m.group(3) + tech[m.end():]
            ce += len(nps) - len(ops)
            # print(f"  {sym} ticker: {ops} -> {nps}")

    # 4b. Update metrics (period percentages + dollar subs)
    for period in ["6M", "90D", "30D", "YTD"]:
        ret_val = sym_ret.get(period)
        if ret_val is None:
            continue

        # Find this period's metric block
        card_section = tech[cs:ce]
        lbl_str = f'<div class="metric-lbl">{period}</div>'
        li = card_section.find(lbl_str)
        if li == -1:
            continue

        sub = card_section[li:li+300]
        abs_offset = cs + li

        # Update percentage value
        v = re.search(r'(<div class="metric-val )(up|down)(">)([+-]?\d+\.?\d*)(%</div>)', sub)
        if v:
            is_up = ret_val >= 0
            new_class = "up" if is_up else "down"
            new_val = f"{ret_val:+.1f}" if is_up else f"{ret_val:.1f}"
            new_v_str = f'<div class="metric-val {new_class}">{new_val}%</div>'
            if v.group(0) != new_v_str:
                v_start = abs_offset + v.start()
                v_end = abs_offset + v.end()
                tech = tech[:v_start] + new_v_str + tech[v_end:]

        card_section = tech[cs:ce]
        li = card_section.find(lbl_str)
        if li == -1:
            continue
        sub = card_section[li:li+300]
        abs_offset = cs + li

        # Update dollar sub (current price display next to metric)
        s = re.search(r'(<div class="metric-sub">)(\$[0-9,]+\.[0-9]+)(</div>)', sub)
        if s:
            ops = s.group(2)
            if ops != nps:
                s_start = abs_offset + s.start()
                s_end = abs_offset + s.end()
                tech = tech[:s_start] + s.group(1) + nps + s.group(3) + tech[s_end:]

    # 4c. Sparkline aria-label price
    card_section = tech[cs:ce]
    for sp in re.finditer(r'(aria-label="[^"]*?currently )(\$[0-9,]+\.[0-9]+)(")', card_section):
        ops = sp.group(2)
        if ops != nps:
            sp_start = cs + sp.start()
            sp_end = cs + sp.end()
            tech = tech[:sp_start] + sp.group(1) + nps + sp.group(3) + tech[sp_end:]

    # 4d. Sparkline svg text price
    card_section = tech[cs:ce]
    for tx in re.finditer(
        r'(<text x="120" y="12" text-anchor="end" font-size="8" fill="var\(--text-muted\)">)(\$[0-9,]+\.[0-9]+)(</text>)',
        card_section
    ):
        ops = tx.group(2)
        if ops != nps:
            tx_start = cs + tx.start()
            tx_end = cs + tx.end()
            tech = tech[:tx_start] + tx.group(1) + nps + tx.group(3) + tech[tx_end:]

    # 4e. Update 30d reversal badge
    card_section = tech[cs:ce]
    li30 = card_section.find('<div class="metric-lbl">30D</div>')
    if li30 >= 0:
        sub30 = card_section[li30:li30+200]
        ret30 = sym_ret.get("30D")
        if ret30 is not None:
            badge_match = re.search(r'(<span class="reversal-badge )(up|down)(">)([↑↓] [A-Za-z]+)(</span>)', sub30)
            if badge_match:
                is_up = ret30 >= 0
                new_bdir = "up" if is_up else "down"
                new_arrow = "↑" if is_up else "↓"
                new_label = "Reversal" if is_up else "Downtrend"
                new_badge = f'<span class="reversal-badge {new_bdir}">{new_arrow} {new_label}</span>'
                if badge_match.group(0) != new_badge:
                    ba_start = cs + li30 + badge_match.start()
                    ba_end = cs + li30 + badge_match.end()
                    tech = tech[:ba_start] + new_badge + tech[ba_end:]

    # Track price change
    if old_price_str is not None and old_price_str != nps:
        try:
            old_v = float(old_price_str.replace("$","").replace(",",""))
            new_v = float(nps.replace("$","").replace(",",""))
            pct_chg = (new_v - old_v) / old_v * 100
            flag = " **" if abs(pct_chg) > 10 else ""
            tech_changes.append((sym, old_price_str, nps, pct_chg, flag))
        except ValueError:
            pass

# ── 5. Detect changes & write ──────────────────────────────────
print("\n" + "=" * 60)

any_change = False

# Build change summary
all_changes = []  # (sym, old, new, pct, flag, source)

if dive != dive_orig:
    any_change = True
    print("  Deep-Dive v4: prices updated")
    for c in dive_changes:
        sym, old, new, pct, flag = c
        print(f"  DD {sym}: {old} -> {new} ({pct:+.1f}%){flag}")
        all_changes.append(c + ("dd",))
else:
    print("  Deep-Dive v4: no price changes")

if tech != tech_orig:
    any_change = True
    print("  Tech v3: updated")
    for c in tech_changes:
        sym, old, new, pct, flag = c
        print(f"  Tech {sym}: {old} -> {new} ({pct:+.1f}%){flag}")
        all_changes.append(c + ("tech",))
else:
    print("  Tech v3: no price changes")

if not any_change:
    print("No changes — prices are identical.")
    print("[SILENT]")
    sys.exit(0)

# Write files
with open(TECH_V3, "w", encoding="utf-8") as f:
    f.write(tech)
with open(DEEP_DIVE_V4, "w", encoding="utf-8") as f:
    f.write(dive)

tech_size = len(tech)
dive_size = len(dive)
print(f"\nFiles written: {TECH_V3} ({tech_size}B), {DEEP_DIVE_V4} ({dive_size}B)")

# Build structured commit summary
commit_body_lines = ["auto-refresh: live stock data update"]

if all_changes:
    commit_body_lines.append("")
    commit_body_lines.append("Tickers with price changes:")
    for c in all_changes:
        sym, old, new, pct, flag, src = c
        commit_body_lines.append(f"  {sym}: {old} -> {new} ({pct:+.1f}%){flag}")

    # Check for big movers > 10%
    big_movers = [c for c in all_changes if abs(c[3]) > 10]
    if big_movers:
        commit_body_lines.append("")
        commit_body_lines.append("Movers >10% since last refresh:")
        for c in big_movers:
            sym, old, new, pct, flag, src = c
            commit_body_lines.append(f"  {sym}: {pct:+.1f}% ({old} -> {new})")

commit_body = "\n".join(commit_body_lines)
print(f"\nCommit body:\n{commit_body}")

# Save the commit message
msg_path = "/tmp/stock_refresh_commit_msg.txt"
with open(msg_path, "w") as f:
    f.write(f"auto-refresh: live stock data update [{date_str}]\n")
    f.write("\n")
    f.write(commit_body)
    f.write("\n")

print(f"\nCommit message saved to {msg_path}")
print("Done.")
