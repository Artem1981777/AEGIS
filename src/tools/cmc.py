# src/tools/cmc.py
# CoinMarketCap signal client: live MarketSignals when CMC_API_KEY is set,
# else returns None so callers fall back to synthetic data.
import os

try:
    import httpx
except Exception:
    httpx = None

from src.agents.regime import MarketSignals

BASE = os.getenv("CMC_BASE", "https://pro-api.coinmarketcap.com")
KEY = os.getenv("CMC_API_KEY", "")


def _client():
    if not KEY or httpx is None:
        return None
    return httpx.Client(base_url=BASE, headers={"X-CMC_PRO_API_KEY": KEY, "Accept": "application/json"}, timeout=15.0)


def fear_greed():
    c = _client()
    if c is None:
        return None
    try:
        r = c.get("/v3/fear-and-greed/latest")
        r.raise_for_status()
        data = r.json().get("data", {})
        val = data.get("value")
        return float(val) if val is not None else None
    except Exception:
        return None
    finally:
        c.close()


def quote(symbol):
    c = _client()
    if c is None:
        return None
    try:
        r = c.get("/v2/cryptocurrency/quotes/latest", params={"symbol": symbol})
        r.raise_for_status()
        block = r.json().get("data", {}).get(symbol.upper())
        if isinstance(block, list):
            block = block[0] if block else None
        if not block:
            return None
        usd = block.get("quote", {}).get("USD", {})
        return {"price": usd.get("price"), "pct_1h": usd.get("percent_change_1h"), "pct_24h": usd.get("percent_change_24h"), "pct_7d": usd.get("percent_change_7d")}
    except Exception:
        return None
    finally:
        c.close()


def live_signals(symbol="BNB"):
    q = quote(symbol)
    fg = fear_greed()
    if q is None and fg is None:
        return None
    pct24 = q.get("pct_24h") if q else None
    pct1 = q.get("pct_1h") if q else None
    pct7 = q.get("pct_7d") if q else None
    fear = fg if fg is not None else (50.0 + (pct24 or 0.0))
    fear = max(0.0, min(100.0, fear))
    trend = max(-1.0, min(1.0, (pct24 or 0.0) / 10.0))
    vol = max(0.05, min(1.5, abs(pct1 or pct24 or 0.0) / 5.0 + abs(pct7 or 0.0) / 30.0))
    return MarketSignals(round(fear, 1), round(trend, 3), round(vol, 3))


if __name__ == "__main__":
    print("CMC_API_KEY set:", bool(KEY))
    s = live_signals("BNB")
    if s is None:
        print("no live data (no key/offline) -> caller uses synthetic fallback")
    else:
        print("live BNB:", s.fear_greed, s.trend_strength, s.volatility)
