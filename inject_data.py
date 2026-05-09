#!/usr/bin/env python3
"""Inject price action bars and fundamentals grids into Tech v2 HTML files."""

import json
import os
import re

# ── Load yfinance data ──
with open('/tmp/yf_data.json', 'r') as f:
    data = json.load(f)

# ── CSS to inject ──
INJECT_CSS = """\
.price-action-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border-bottom:1px solid var(--border)}
.pa-cell{background:var(--surface2);padding:10px 12px;text-align:center}
.pa-cell-label{font-size:9px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted);margin-bottom:3px}
.pa-cell-value{font-size:13px;font-weight:600}
.pa-cell-value.up{color:var(--accent-green)}
.pa-cell-value.down{color:var(--accent-red)}
.pa-cell-sub{font-size:9px;color:var(--text-muted);margin-top:1px}
.reversal-badge{display:inline-block;font-size:9px;font-weight:700;letter-spacing:.04em;padding:2px 6px;border-radius:3px;margin-top:4px}
.reversal-badge.up{background:rgba(63,185,80,.15);color:var(--accent-green);border:1px solid rgba(63,185,80,.3)}
.reversal-badge.down{background:rgba(248,81,73,.15);color:var(--accent-red);border:1px solid rgba(248,81,73,.3)}
.reversal-badge.partial{background:rgba(210,153,34,.15);color:var(--accent-yellow);border:1px solid rgba(210,153,34,.3)}
.fundamentals-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--border);border-bottom:1px solid var(--border)}
.fund-cell{background:var(--surface);padding:10px 12px}
.fund-cell-label{font-size:9px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted);margin-bottom:3px}
.fund-cell-value{font-size:13px;font-weight:600;color:var(--text-primary)}
.fund-cell-sub{font-size:9px;color:var(--text-muted);margin-top:1px}
@media(max-width:768px){.price-action-bar{grid-template-columns:repeat(2,1fr)}.fundamentals-grid{grid-template-columns:repeat(2,1fr)}}"""


def fmt_big(val):
    """Format large numbers: $X.XXB for billions, $XX.XB for 10B+, $XXXM for millions."""
    if val is None:
        return "N/A"
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000_000:
        b = abs_val / 1_000_000_000
        # Handle 10B+ vs single digit billions
        if b >= 10:
            return f"{sign}${b:.1f}B"
        else:
            return f"{sign}${b:.2f}B"
    elif abs_val >= 1_000_000:
        m = abs_val / 1_000_000
        return f"{sign}${m:.0f}M"
    else:
        return f"{sign}${abs_val:,.0f}"


def fmt_pct(val):
    """Format a decimal (0.078) as percentage (+7.8%)."""
    if val is None:
        return "N/A"
    pct = val * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def fmt_ret(val):
    """Format a return percentage (already in percent, e.g. -31.2) as {+X.X}%."""
    if val is None:
        return "N/A"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.1f}%"


def get_direction_class(val):
    """Return 'up' if val >= 0, else 'down'."""
    return "up" if val >= 0 else "down"


def build_price_action_bar(ticker_data):
    """Build the price action bar HTML for a stock."""
    price = ticker_data.get("price", 0)
    ret_6m = ticker_data.get("ret_6m", 0)
    ret_90d = ticker_data.get("ret_90d", 0)
    ret_30d = ticker_data.get("ret_30d", 0)
    # YTD is approx same as 4-5 months, we use 6m as the longest available
    # Task says columns: 6M, 90-Day, 30-Day, YTD
    # YTD = ret_6m (since it's roughly YTD for May data)

    periods = [
        ("6M", ret_6m),
        ("90-Day", ret_90d),
        ("30-Day", ret_30d),
        ("YTD", ret_6m),  # YTD is same as 6M given data available
    ]

    cells = []
    for label, ret_val in periods:
        cls = get_direction_class(ret_val)
        formatted = fmt_ret(ret_val)

        # Add reversal badge on 30-Day cell
        badge_html = ""
        if label == "30-Day":
            if ret_30d > 0 and ret_90d > 0:
                badge_html = '<div class="reversal-badge up">↑ Reversal</div>'
            elif ret_30d > 0 and ret_90d <= 0:
                badge_html = '<div class="reversal-badge partial">Basing</div>'
            else:
                badge_html = '<div class="reversal-badge down">↓ Downtrend</div>'

        cells.append(f'''    <div class="pa-cell">
      <div class="pa-cell-label">{label}</div>
      <div class="pa-cell-value {cls}">{formatted}</div>
      <div class="pa-cell-sub">${price:.2f}</div>
      {badge_html}
    </div>''')

    # Join cells without trailing newline on last
    cells_str = "\n".join(cells)

    return f'''<div class="price-action-bar">
{cells_str}
  </div>'''


def build_fundamentals_grid(ticker_data):
    """Build the fundamentals grid HTML for a stock."""
    rev = ticker_data.get("rev", 0)
    fcf = ticker_data.get("fcf", 0)
    gm = ticker_data.get("gm", 0)
    cash = ticker_data.get("cash", 0)
    debt = ticker_data.get("debt", 0)
    net_cash = cash - debt
    op_margin = ticker_data.get("opMargin", 0)
    rev_growth = ticker_data.get("revGrowth", 0)

    cols = [
        ("Revenue / FY25", rev, rev_growth),
        ("FCF / FY25", fcf, None),  # No YoY for FCF
        ("Gross Margin", gm, None),
        ("Net Cash", net_cash, None),
        ("GAAP Op Margin", op_margin, None),
    ]

    cells = []
    for label, val, growth in cols:
        if label == "Revenue / FY25":
            formatted_val = fmt_big(val)
            growth_str = f"<div class=\"fund-cell-sub\">{fmt_pct(growth)} YoY</div>" if growth is not None else ""
        elif label == "FCF / FY25":
            formatted_val = fmt_big(val)
            growth_str = ""
        elif label == "Gross Margin":
            formatted_val = f"{val*100:.1f}%"
            growth_str = ""
        elif label == "Net Cash":
            formatted_val = fmt_big(val)
            growth_str = ""
        elif label == "GAAP Op Margin":
            formatted_val = f"{val*100:.1f}%"
            growth_str = ""
        else:
            formatted_val = fmt_big(val)
            growth_str = ""

        cells.append(f'''    <div class="fund-cell">
      <div class="fund-cell-label">{label}</div>
      <div class="fund-cell-value">{formatted_val}</div>
      {growth_str}
    </div>''')

    cells_str = "\n".join(cells)

    return f'''<div class="fundamentals-grid">
{cells_str}
  </div>'''


def get_ticker_from_header(lines, body_line_idx):
    """Look backwards from the stock-card-body line to find the stock-ticker span."""
    for i in range(body_line_idx - 1, max(body_line_idx - 30, 0), -1):
        line = lines[i]
        m = re.search(r'<span class="stock-ticker">(\w+)</span>', line)
        if m:
            return m.group(1)
    return None


def inject_css(lines):
    """Inject CSS rules before the </style> tag. Returns modified lines."""
    result = []
    injected = False
    for line in lines:
        if not injected and line.strip() == '</style>':
            result.append(INJECT_CSS)
            result.append('')
            result.append(line)
            injected = True
        else:
            result.append(line)
    return result


def process_file(filepath):
    """Process a single HTML file: inject CSS and stock data."""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # Step 1: Inject CSS
    lines = inject_css(lines)

    # Step 2: Find all stock-card-body lines
    body_positions = []
    for i, line in enumerate(lines):
        if '<div class="stock-card-body">' in line:
            ticker = get_ticker_from_header(lines, i)
            body_positions.append((i, ticker))

    print(f"Found {len(body_positions)} stock card bodies")

    # Step 3: Inject price action + fundamentals bars (END to START)
    count = 0
    for line_idx, ticker in reversed(body_positions):
        if ticker not in data:
            print(f"  WARNING: Ticker {ticker} not found in yf_data.json — skipping")
            continue

        ticker_data = data[ticker]
        pa_bar = build_price_action_bar(ticker_data)
        fund_grid = build_fundamentals_grid(ticker_data)

        # Lines to inject after <div class="stock-card-body">
        injection_lines = [pa_bar, fund_grid]

        # Insert after the stock-card-body line
        # Stock-card-body line is at line_idx
        # We insert right after this line
        insert_pos = line_idx + 1
        for j, inj_line in enumerate(injection_lines):
            lines.insert(insert_pos + j, inj_line)

        print(f"  ✓ {ticker}: Injected price action + fundamentals (line {line_idx+1})")
        count += 1

    print(f"\nTotal cards injected: {count}")

    # Write back
    result = '\n'.join(lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(result)

    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size:,} bytes")
    return count


# ── Main ──
if __name__ == '__main__':
    files = [
        '/tmp/Brian-stock-research/Tech_Stock_Basket_May_2026_v2.html',
        '/tmp/Brian-stock-research/Tech_Stock_Basket_May_2026_v2_visual.html',
    ]

    for fpath in files:
        cnt = process_file(fpath)

    print(f"\n{'='*60}")
    print("DONE: All injections complete.")
