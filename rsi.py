"""
Live RSI(14) for every MEXC crypto USDT perpetual on 15m, 1H, 4H, 1D and 1W candles - the candle still forming included, so the
value moves with the live price. Writes site/data.json for the page in site/index.html.
Run every 30 minutes by GitHub Actions (.github/workflows/rsi.yml), which also publishes the site to GitHub Pages.
"""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://contract.mexc.com/api/v1/contract"
TRADFI_TAG = "mc-trade-zone-tradfi"
FRAMES = {"15m": ("Min15", 900), "1H": ("Min60", 3600), "4H": ("Hour4", 4 * 3600), "1D": ("Day1", 86400),
          "1W": ("Week1", 7 * 86400)}
BARS, PERIOD = 120, 14                        # 120 candles is enough for Wilder's smoothing to settle
MIN_BARS = 20                                 # fewer candles (a new listing): no RSI yet
RATE = 9.0                                    # requests per second (public limit: 20 per 2 s)
OUT = Path(__file__).parent / "site" / "data.json"
_lock, _next = threading.Lock(), [0.0]


def get(url, params=None):
    for attempt in range(4):
        with _lock:
            wait = _next[0] - time.time()
            _next[0] = max(_next[0], time.time()) + 1.0 / RATE
        if wait > 0:
            time.sleep(wait)
        try:
            body = requests.get(url, params=params, timeout=15).json()
            if body.get("success"):
                return body["data"]
        except Exception:
            pass
        time.sleep(1 + 2 * attempt)
    return None


def rsi(closes, n=PERIOD):
    """Wilder's RSI of the last value (the forming candle's close = current price)."""
    if len(closes) < MIN_BARS:
        return None
    gains = [max(b - a, 0.0) for a, b in zip(closes, closes[1:])]
    losses = [max(a - b, 0.0) for a, b in zip(closes, closes[1:])]
    g, l = sum(gains[:n]) / n, sum(losses[:n]) / n
    for gi, li in zip(gains[n:], losses[n:]):
        g, l = (g * (n - 1) + gi) / n, (l * (n - 1) + li) / n
    if l == 0:
        return 100.0 if g > 0 else 50.0
    return round(100 - 100 / (1 + g / l), 1)


def coin(sym, now):
    out = {"coin": sym.replace("_USDT", "")}
    for tf, (interval, sec) in FRAMES.items():
        d = get(f"{BASE}/kline/{sym}", {"interval": interval, "start": now - sec * BARS})
        closes = [float(c) for c in (d or {}).get("close", [])]
        out[tf] = rsi(closes)
    return out


def main():
    t0, now = time.time(), int(time.time())
    detail = get(f"{BASE}/detail") or []
    syms = sorted(r["symbol"] for r in detail if r.get("quoteCoin") == "USDT" and r.get("settleCoin") == "USDT"
                  and TRADFI_TAG not in (r.get("conceptPlate") or []) and r.get("state") == 0
                  and not r["symbol"].endswith("STOCK_USDT"))          # tokenized stocks are not crypto
    tick = {t["symbol"]: t for t in (get(f"{BASE}/ticker") or [])}
    with ThreadPoolExecutor(10) as ex:
        rows = [r for r in ex.map(lambda s: coin(s, now), syms) if any(r[tf] is not None for tf in FRAMES)]
    for r in rows:
        t = tick.get(r["coin"] + "_USDT", {})
        r["price"] = float(t.get("lastPrice") or 0)
        r["chg24"] = round(float(t.get("riseFallRate") or 0) * 100, 2)
        r["vol24"] = round(float(t.get("amount24") or 0))
        r["funding"] = t.get("fundingRate")
    if len(rows) < 100:
        raise SystemExit(f"only {len(rows)} coins - MEXC API problem, keeping the previous page")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "period": PERIOD, "coins": rows}, separators=(",", ":")))
    hot = {tf: sum(1 for r in rows if r[tf] is not None and r[tf] >= 75) for tf in FRAMES}
    cold = {tf: sum(1 for r in rows if r[tf] is not None and r[tf] <= 25) for tf in FRAMES}
    print(f"{len(rows)} coins in {time.time() - t0:.0f}s; RSI >= 75: {hot}; RSI <= 25: {cold}")


if __name__ == "__main__":
    main()
