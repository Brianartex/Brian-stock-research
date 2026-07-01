#!/usr/bin/env python3
import re
with open('Tech_Stock_Basket_May_2026_v3.html','r') as f:
    h = f.read()
tickers = re.findall(r'<span class="stock-ticker">(\w+)</span>', h)
print('Tech v3 tickers:', len(tickers), tickers)
with open('investment-deep-dive-v4.html','r') as f:
    h2 = f.read()
tickers2 = re.findall(r'<div class="pick-ticker">(\w+)', h2)
print('Deep v4 tickers:', len(tickers2), tickers2)
prices = re.findall(r'<div class="pick-ticker">(\w+)\s+<span[^>]*>\$([^<]+)</span>', h2)
print('Deep prices:', prices)
