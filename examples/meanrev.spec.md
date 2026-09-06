# Mean Reversion Sandbox

broker: alpaca
symbols: SPY, QQQ
timeframe: 15m
max_position: 5%
stop_loss: 1.5%

rules:
- buy when price closes two standard deviations below the 30 period mean
- exit at the mean, not at a target
- no new entries in the first ten minutes of the session
