import re
with open('Tech_Stock_Basket_May_2026_v3.html','r') as f:
    h = f.read()
# Find all ticker + price patterns
m = re.findall(r'<div class="ticker"[^>]*>([A-Z]{2,5})\s+<span[^>]*>\$([\d,]+\.\d{2})</span>', h)
for t, p in m:
    print(f'{t}: ${p}')
print('Total price entries found:', len(m))
