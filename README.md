# MEXC RSI Heat
Live RSI(14) of every MEXC USDT perpetual on 1H, 4H and 1D candles (the forming candle included), with filters for
RSI ≥ 75 / 80 / 90. GitHub Actions recalculates every 30 minutes (a looping run, restarted hourly, because GitHub starts scheduled jobs late) and publishes `site/` to the gh-pages branch, which GitHub Pages serves
(`.github/workflows/rsi.yml`). Data: MEXC public API only. A high RSI describes a strong recent run; it is not advice.
