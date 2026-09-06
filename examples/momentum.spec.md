# Momentum Paper Trader

broker: robinhood
symbols: AAPL, MSFT, NVDA
timeframe: 5m
max_position: 10%
stop_loss: 2%
cash: 10000
owner: wast3

rules:
- buy when the 20 period average crosses above the 50
- sell when the 20 period average crosses back below the 50
- never hold more than three open positions at once
- flatten everything fifteen minutes before the close
