#!/usr/bin/env python3
import json, re
from datetime import datetime

with open('/tmp/yf_data.json', 'r') as f:
    data = json.load(f)

def fmt_big(val):
    if val is None: return 'N/A'
    abs_val = abs(val)
    sign = '-' if val < 0 else ''
    if abs_val >= 1e9:
        b = abs_val / 1e9
        return f'{sign}${b:.1f}B' if b >= 10 else f'{sign}${b:.2f}B'
    elif abs_val >= 1e6:
        return f'{sign}${abs_val/1e6:.0f}M'
    else:
        return f'{sign}${abs_val:,.0f}'

def fmt_pct(val):
    if val is None: return 'N/A'
    pct = val * 100
    return f"{'+' if pct >= 0 else ''}{pct:.1f}%"

def fmt_ret(val):
    if val is None: return 'N/A'
    return f"{'+' if val >= 0 else ''}{val:.1f}%"

def get_cls(val): return 'up' if val >= 0 else 'down'
def fmt_price(price): return f'{price:,.2f}'

print('=== Updating Tech v3 ===')
with open('Tech_Stock_Basket_May_2026_v3.html', 'r', encoding='utf-8') as f:
    tech_html = f.read()

tech_tickers = sorted(set(re.findall(r'<div class="ticker"[^>]*>([A-Z]{2,5})', tech_html)))
tech_updated = tech_html
tech_changes = []

for ticker in tech_tickers:
    if ticker not in data: continue
    d = data[ticker]
    price, ret_30d = d['price'], d['ret_30d']
    
    # Match: <div class="ticker" style="...">TICKER <span style="...">$PRICE</span> <span style="...">PERCENT% ARROW
    # Note: The percentage span in Tech v3 has NO closing </span> tag, and there's a newline after the arrow
    pattern = rf'(<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$)[\d,]+\.\d{{2}}(</span>\s+<span[^>]*>)[\-\+]?\d+\.\d+% [↑↓]'
    
    def make_repl(tkr):
        dd = data[tkr]
        def repl(m):
            arrow = chr(8593) if dd['ret_30d'] >= 0 else chr(8595)
            return f'{m.group(1)}{fmt_price(dd["price"])}{m.group(2)}{dd["ret_30d"]:+.1f}% {arrow}'
        return repl
    
    new_html, count = re.subn(pattern, make_repl(ticker), tech_updated)
    if count > 0:
        tech_updated = new_html
        tech_changes.append(ticker)
        print(f'  {ticker}: Header ${fmt_price(price)} ({ret_30d:+.1f}%)')

for ticker in tech_tickers:
    if ticker not in data: continue
    d = data[ticker]
    price = d['price']
    
    ticker_pos = tech_updated.find(f'<div class="ticker" style="display:inline;margin-right:10px;">{ticker}')
    if ticker_pos == -1:
        ticker_pos = tech_updated.find(f'<div class="ticker">{ticker}')
    if ticker_pos == -1: continue
    
    card_end = tech_updated.find('</details>', ticker_pos)
    if card_end == -1: card_end = len(tech_updated)
    
    card_section = tech_updated[ticker_pos:card_end]
    periods = [('6M', d['ret_6m']), ('90D', d['ret_90d']), ('30D', d['ret_30d']), ('YTD', d['ret_6m'])]
    
    metric_matches = list(re.finditer(
        r'(<div class="metric">\s+<div class="metric-lbl">)(\w+)(</div>\s+<div class="metric-val )([\w\-]+)(">)([\-\+]?\d+\.\d+%|N/A)(</div>\s+<div class="metric-sub">)\$?[\d,]+\.\d{2}(<span class="reversal-badge[^>]*>[^<]*</span>)?',
        card_section
    ))
    
    for i, m in enumerate(metric_matches):
        if i < len(periods):
            label, val = periods[i]
            cls = get_cls(val)
            old_text = m.group(0)
            new_text = f'{m.group(1)}{label}{m.group(3)}{cls}{m.group(5)}{fmt_ret(val)}{m.group(7)}${fmt_price(price)}'
            if label == '30D':
                if val > 0 and d['ret_90d'] > 0:
                    badge = '<span class="reversal-badge up">↑ Reversal</span>'
                elif val > 0 and d['ret_90d'] <= 0:
                    badge = '<span class="reversal-badge partial">Basing</span>'
                else:
                    badge = '<span class="reversal-badge down">↓ Downtrend</span>'
                new_text += badge
            card_section = card_section.replace(old_text, new_text, 1)
    
    card_section = re.sub(r'(<text[^>]*>\$)[\d,]+\.\d{2}(</text>)', lambda m: f'{m.group(1)}{fmt_price(price)}{m.group(2)}', card_section)
    
    rev, fcf, gm = d['rev'], d['fcf'], d['gm']
    net_cash = (d['cash'] or 0) - (d['debt'] or 0)
    op_margin, rev_growth = d['opMargin'], d['revGrowth']
    
    card_section = re.sub(r'(<div class="fund-item"><div class="lbl">Revenue</div><div class="val">)[^<]+(</div><div class="sub">)[^<]+(</div></div>)', lambda m: f'{m.group(1)}{fmt_big(rev)}{m.group(2)}{fmt_pct(rev_growth)} YoY{m.group(3)}', card_section, count=1)
    card_section = re.sub(r'(<div class="fund-item"><div class="lbl">Free Cash Flow</div><div class="val">)[^<]+(</div></div>)', lambda m: f'{m.group(1)}{fmt_big(fcf)}{m.group(2)}', card_section, count=1)
    if gm is not None:
        card_section = re.sub(r'(<div class="fund-item"><div class="lbl">Gross Margin</div><div class="val">)[^<]+(</div></div>)', lambda m: f'{m.group(1)}{gm*100:.1f}%{m.group(2)}', card_section, count=1)
    card_section = re.sub(r'(<div class="fund-item"><div class="lbl">Net Cash</div><div class="val">)[^<]+(</div></div>)', lambda m: f'{m.group(1)}{fmt_big(net_cash)}{m.group(2)}', card_section, count=1)
    if op_margin is not None:
        card_section = re.sub(r'(<div class="fund-item"><div class="lbl">Operating Margin</div><div class="val">)[^<]+(</div></div>)', lambda m: f'{m.group(1)}{op_margin*100:.1f}%{m.group(2)}', card_section, count=1)
    
    tech_updated = tech_updated[:ticker_pos] + card_section + tech_updated[card_end:]

with open('Tech_Stock_Basket_May_2026_v3.html', 'w', encoding='utf-8') as f:
    f.write(tech_updated)
print(f'Tech v3 updated: {len(tech_changes)} tickers')

print('\n=== Updating Deep-Dive v4 ===')
with open('investment-deep-dive-v4.html', 'r', encoding='utf-8') as f:
    deep_html = f.read()

deep_tickers = ['FLNC', 'AAOI', 'MU', 'SMCI', 'SNDK', 'APH', 'ANET', 'AMPX', 'VST']
deep_updated = deep_html
deep_changes = []

for ticker in deep_tickers:
    if ticker not in data: continue
    d = data[ticker]
    price = d['price']
    new_price_str = fmt_price(price)
    
    pattern = rf'(<div class="pick-ticker">{re.escape(ticker)}\s+<span[^>]*>\$)[\d,]+(\.\d{{2}})?(</span></div>)'
    
    def make_price_repl(tkr, nps):
        def repl(m):
            return f'{m.group(1)}{nps}{m.group(3)}'
        return repl
    
    new_html, count = re.subn(pattern, make_price_repl(ticker, new_price_str), deep_updated)
    if count > 0:
        deep_updated = new_html
        deep_changes.append(ticker)
        print(f'  {ticker}: pick-ticker -> ${new_price_str}')

for ticker in deep_tickers:
    if ticker not in data: continue
    d = data[ticker]
    price = d['price']
    new_price_str = fmt_price(price)
    
    ticker_match = re.search(rf'<div class="pick-ticker">{re.escape(ticker)}', deep_updated)
    if not ticker_match: continue
    # Find "stock at $X" in the next 2500 chars
    search_start = ticker_match.end()
    search_end = min(search_start + 2500, len(deep_updated))
    search_region = deep_updated[search_start:search_end]
    
    stock_at_pattern = r'(\(stock at \$)[\d,]+(\.\d{2})?(\))'
    
    def make_stock_repl(nps):
        def repl(m):
            return f'{m.group(1)}{nps}{m.group(3)}'
        return repl
    
    new_region, count = re.subn(stock_at_pattern, make_stock_repl(new_price_str), search_region)
    if count > 0:
        deep_updated = deep_updated[:search_start] + new_region + deep_updated[search_end:]
        print(f'  {ticker}: "stock at" -> ${new_price_str}')

with open('investment-deep-dive-v4.html', 'w', encoding='utf-8') as f:
    f.write(deep_updated)
print(f'Deep-Dive v4 updated: {len(deep_changes)} tickers')

print('\n=== Summary ===')
print(f'Tech v3: {len(tech_changes)} tickers updated')
print(f'Deep-Dive v4: {len(deep_changes)} tickers updated')

movers = []
for ticker in deep_tickers:
    if ticker in data:
        ret_30d = data[ticker]['ret_30d']
        if abs(ret_30d) > 10:
            movers.append(f'{ticker}: {ret_30d:+.1f}% (30d)')

if movers:
    print(f'\nMovers >10% (30d):')
    for m in movers:
        print(f'  {m}')

summary = {
    'tech_changes': tech_changes,
    'deep_changes': deep_changes,
    'movers': movers,
    'date': datetime.now().strftime('%B %d %Y')
}
with open('/tmp/refresh_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('\nDone. Ready to commit.')
