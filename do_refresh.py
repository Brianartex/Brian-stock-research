#!/usr/bin/env python3
"""Daily stock data refresh for Tech v3 and Deep-Dive v4 docs."""

import json, os, re, sys
import yfinance as yf
from datetime import datetime

TECH_FILE = 'Tech_Stock_Basket_May_2026_v3.html'
DEEP_FILE = 'investment-deep-dive-v4.html'

# Step 1: Extract tickers
with open(TECH_FILE, 'r', encoding='utf-8') as f:
    tech_html = f.read()
with open(DEEP_FILE, 'r', encoding='utf-8') as f:
    deep_html = f.read()

tech_tickers = sorted(set(re.findall(r'<div class="ticker"[^>]*>([A-Z]{2,5})', tech_html)))
deep_tickers = re.findall(r'<div class="pick-ticker">(\w+)', deep_html)

print('Tech v3 tickers:', tech_tickers)
print('Deep-dive v4 tickers:', deep_tickers)

# Step 2: Fetch fresh data
all_tickers = sorted(set(tech_tickers + deep_tickers))
print('Fetching data for:', all_tickers)

data = {}
for ticker in all_tickers:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="6mo")
        info = t.info
        if hist.empty:
            print(f'  {ticker}: NO DATA')
            continue
        price = float(hist['Close'].iloc[-1])
        price_30d = float(hist['Close'].iloc[-22]) if len(hist) >= 22 else float(hist['Close'].iloc[0])
        price_90d = float(hist['Close'].iloc[-65]) if len(hist) >= 65 else float(hist['Close'].iloc[0])
        price_6m = float(hist['Close'].iloc[0])
        ret_30d = (price / price_30d - 1) * 100
        ret_90d = (price / price_90d - 1) * 100
        ret_6m = (price / price_6m - 1) * 100
        data[ticker] = {
            'price': price,
            'ret_30d': ret_30d,
            'ret_90d': ret_90d,
            'ret_6m': ret_6m,
            'rev': info.get('totalRevenue'),
            'fcf': info.get('freeCashflow'),
            'gm': info.get('grossMargins'),
            'cash': info.get('totalCash'),
            'debt': info.get('totalDebt'),
            'opMargin': info.get('operatingMargins'),
            'revGrowth': info.get('revenueGrowth'),
        }
        print(f'  {ticker}: ${price:.2f} (30d={ret_30d:+.1f}%, 90d={ret_90d:+.1f}%, 6m={ret_6m:+.1f}%)')
    except Exception as e:
        print(f'  {ticker}: ERROR {e}')

# Helper functions
def fmt_big(val):
    if val is None:
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000_000:
        b = abs_val / 1_000_000_000
        return f"{sign}${b:.1f}B" if b >= 10 else f"{sign}${b:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{sign}${abs_val/1_000_000:.0f}M"
    else:
        return f"{sign}${abs_val:,.0f}"

def fmt_pct(val):
    if val is None:
        return "N/A"
    pct = val * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"

def fmt_ret(val):
    if val is None:
        return "N/A"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"

def get_cls(val):
    return "up" if val >= 0 else "down"

# Step 3: Update Tech v3 doc
print('\n--- Updating Tech v3 ---')
tech_updated = tech_html
tech_changes = []

for ticker in tech_tickers:
    if ticker not in data:
        continue
    d = data[ticker]
    price = d['price']
    ret_30d = d['ret_30d']
    
    # Update ticker header: price and 30d change
    # Pattern: <div class="ticker" ...>TICKER <span style="...">$OLD</span> <span style="...">OLD% ↑/↓</span>
    pattern = rf'(<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$)[\d,]+\.\d{{2}}(</span>\s+<span[^>]*>)[\-\+]?\d+\.\d+%\s*[↑↓](</span>)'
    replacement = rf'\1{price:,.2f}\2{ret_30d:+.1f}% {"\u2191" if ret_30d >= 0 else "\u2193"}\3'
    new_html, count = re.subn(pattern, replacement, tech_updated)
    if count > 0:
        tech_updated = new_html
        tech_changes.append(ticker)
        print(f'  {ticker}: Header ${price:,.2f} ({ret_30d:+.1f}%)')

# Update metrics, sparklines, and fundamentals within each card
for ticker in tech_tickers:
    if ticker not in data:
        continue
    d = data[ticker]
    price = d['price']
    
    # Find card section
    ticker_pos = tech_updated.find(f'<div class="ticker" style="display:inline;margin-right:10px;">{ticker}')
    if ticker_pos == -1:
        ticker_pos = tech_updated.find(f'<div class="ticker">{ticker}')
    if ticker_pos == -1:
        print(f'  {ticker}: Card not found')
        continue
    
    card_end = tech_updated.find('</details>', ticker_pos)
    if card_end == -1:
        card_end = len(tech_updated)
    
    card_section = tech_updated[ticker_pos:card_end]
    original_section = card_section
    
    # Update metric values in order: 6M, 90D, 30D, YTD
    periods = [
        ('6M', d['ret_6m']),
        ('90D', d['ret_90d']),
        ('30D', d['ret_30d']),
        ('YTD', d['ret_6m']),
    ]
    
    # Find each metric cell and update
    metric_matches = list(re.finditer(
        r'(<div class="metric">\s+<div class="metric-lbl">)(\w+)(</div>\s+<div class="metric-val )([\w\-]+)(">)([\-\+]?\d+\.\d+%|N/A)(</div>\s+<div class="metric-sub">)\$?[\d,]+\.\d{2}',
        card_section
    ))
    
    for i, m in enumerate(metric_matches):
        if i < len(periods):
            label, val = periods[i]
            cls = get_cls(val)
            old_text = m.group(0)
            new_text = f'{m.group(1)}{label}{m.group(3)}{cls}{m.group(5)}{fmt_ret(val)}{m.group(7)}${price:,.2f}'
            # Add reversal badge for 30D if present
            if label == '30D':
                if val > 0 and d['ret_90d'] > 0:
                    badge = '<span class="reversal-badge up">↑ Reversal</span>'
                elif val > 0 and d['ret_90d'] <= 0:
                    badge = '<span class="reversal-badge partial">Basing</span>'
                else:
                    badge = '<span class="reversal-badge down">↓ Downtrend</span>'
                # Replace the old badge if present
                old_text_with_badge = old_text
                new_text_with_badge = new_text + badge
                card_section = card_section.replace(old_text_with_badge, new_text_with_badge, 1)
            else:
                card_section = card_section.replace(old_text, new_text, 1)
    
    # Update sparkline price label
    card_section = re.sub(
        r'(<text[^>]*>\$)[\d,]+\.\d{2}(</text>)',
        rf'\1{price:,.2f}\2',
        card_section
    )
    
    # Update fundamentals
    rev = d['rev']
    fcf = d['fcf']
    gm = d['gm']
    net_cash = (d['cash'] or 0) - (d['debt'] or 0)
    op_margin = d['opMargin']
    rev_growth = d['revGrowth']
    
    card_section = re.sub(
        r'(<div class="fund-item"><div class="lbl">Revenue</div><div class="val">)[^<]+(</div><div class="sub">)[^<]+(</div></div>)',
        rf'\1{fmt_big(rev)}\2{fmt_pct(rev_growth)} YoY\3',
        card_section, count=1
    )
    card_section = re.sub(
        r'(<div class="fund-item"><div class="lbl">Free Cash Flow</div><div class="val">)[^<]+(</div></div>)',
        rf'\1{fmt_big(fcf)}\2',
        card_section, count=1
    )
    if gm is not None:
        card_section = re.sub(
            r'(<div class="fund-item"><div class="lbl">Gross Margin</div><div class="val">)[^<]+(</div></div>)',
            rf'\1{gm*100:.1f}%\2',
            card_section, count=1
        )
    card_section = re.sub(
        r'(<div class="fund-item"><div class="lbl">Net Cash</div><div class="val">)[^<]+(</div></div>)',
        rf'\1{fmt_big(net_cash)}\2',
        card_section, count=1
    )
    if op_margin is not None:
        card_section = re.sub(
            r'
