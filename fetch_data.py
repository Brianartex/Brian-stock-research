#!/usr/bin/env python3
"""Fetch fresh stock data and write to /tmp/yf_data.json for auto_refresh_today.py"""

import json
import yfinance as yf
import re
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TECH_FILE = 'Tech_Stock_Basket_May_2026_v3.html'
DEEP_FILE = 'investment-deep-dive-v4.html'

with open(TECH_FILE, 'r', encoding='utf-8') as f:
    tech_html = f.read()
with open(DEEP_FILE, 'r', encoding='utf-8') as f:
    deep_html = f.read()

tech_tickers = sorted(set(re.findall(r'<div class="ticker"[^>]*>([A-Z]{2,5})', tech_html)))
deep_tickers = ['FLNC', 'AAOI', 'MU', 'SMCI', 'SNDK', 'APH', 'ANET', 'AMPX', 'VST']

all_tickers = sorted(set(tech_tickers + deep_tickers))
print(f'Fetching data for {len(all_tickers)} tickers: {all_tickers}')

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
        print(f'  {ticker}: ${price:,.2f} (30d={ret_30d:+.1f}%, 90d={ret_90d:+.1f}%, 6m={ret_6m:+.1f}%)')
    except Exception as e:
        print(f'  {ticker}: ERROR {e}')

with open('/tmp/yf_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'\nWrote data for {len(data)} tickers to /tmp/yf_data.json')
