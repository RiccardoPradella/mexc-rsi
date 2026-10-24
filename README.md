# MEXC RSI Heat
Live RSI(14) of every MEXC USDT perpetual on 1H, 4H and 1D candles (the forming candle included), with filters for
RSI ≥ 75 / 80 / 90. GitHub Actions runs `rsi.py` every 30 minutes and publishes `site/` to GitHub Pages
(`.github/workflows/rsi.yml`). Data: MEXC public API only. A high RSI describes a strong recent run; it is not advice.
