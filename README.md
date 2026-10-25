# MEXC RSI Heat
Live RSI(14) of every MEXC USDT perpetual on 15m, 1H, 4H, 1D and 1W candles (the forming candle included), with filters for
overbought (RSI ≥ 75 / 80 / 90) and oversold (RSI ≤ 25 / 20 / 10). GitHub Actions recalculates every 30 minutes (a looping run, restarted hourly, because GitHub starts scheduled jobs late) and publishes `site/` to the gh-pages branch, which GitHub Pages serves
(`.github/workflows/rsi.yml`). Data: MEXC public API only. A high RSI describes a strong recent run; it is not advice.
