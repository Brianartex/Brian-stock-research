import yfinance as yf
for t in ['MU','SNDK','STX','ARM','MRVL','AAOI','FLNC','SMCI']:
    tick = yf.Ticker(t)
    info = tick.info
    print(f"{t}:")
    print(f"  currentPrice: {info.get('currentPrice')}")
    print(f"  lastSplitFactor: {info.get('lastSplitFactor')}")
    print(f"  lastSplitDate: {info.get('lastSplitDate')}")
    # Check history for splits
    hist = tick.history(period='3mo')
    splits = hist[hist['Stock Splits'] != 0]['Stock Splits']
    if not splits.empty:
        print(f"  Recent splits: {splits.to_dict()}")
    else:
        print(f"  No recent splits in 3mo")
    print()
