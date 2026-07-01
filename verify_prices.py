import yfinance as yf
for t in ['FLNC','AAOI','MU','SMCI','SNDK','APH','ANET','AMPX','VST']:
    tick = yf.Ticker(t)
    info = tick.info
    print(f'{t}: ${info.get("currentPrice")}')
