import re

with open('Tech_Stock_Basket_May_2026_v3.html', 'r') as f:
    html = f.read()

# Test pattern on DOCU
ticker = 'DOCU'

# Test simpler patterns first
print("Testing simpler patterns:")
p1 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}'
m1 = re.search(p1, html)
print(f"Pattern 1 (ticker div): {'MATCH' if m1 else 'NO MATCH'}")

p2 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$[\d,]+\.\d{{2}}'
m2 = re.search(p2, html)
print(f"Pattern 2 (ticker + price): {'MATCH' if m2 else 'NO MATCH'}")

p3 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$[\d,]+\.\d{{2}}</span>'
m3 = re.search(p3, html)
print(f"Pattern 3 (ticker + price + </span>): {'MATCH' if m3 else 'NO MATCH'}")

p4 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$[\d,]+\.\d{{2}}</span>\s+<span'
m4 = re.search(p4, html)
print(f"Pattern 4 (ticker + price + </span> + <span): {'MATCH' if m4 else 'NO MATCH'}")

p5 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$[\d,]+\.\d{{2}}</span>\s+<span[^>]*>[\-\+]?\d+\.\d+%'
m5 = re.search(p5, html)
print(f"Pattern 5 (ticker + price + pct): {'MATCH' if m5 else 'NO MATCH'}")

p6 = rf'<div class="ticker"[^>]*>{re.escape(ticker)}\s+<span[^>]*>\$[\d,]+\.\d{{2}}</span>\s+<span[^>]*>[\-\+]?\d+\.\d+%\s*[↑↓]'
m6 = re.search(p6, html)
print(f"Pattern 6 (full pattern): {'MATCH' if m6 else 'NO MATCH'}")

if m6:
    print(f"Matched: {m6.group(0)}")
