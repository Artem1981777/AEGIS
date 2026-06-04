import os
import httpx

CMC_API_KEY = os.getenv("CMC_API_KEY", "")
CMC_BASE = os.getenv("CMC_BASE", "https://pro-api.coinmarketcap.com")


class CMCClient:
    """CoinMarketCap AI Agent Hub client: market features for the agent."""

    def __init__(self, api_key=CMC_API_KEY, base=CMC_BASE, timeout=30):
        self.base = base.rstrip("/")
        self._http = httpx.Client(base_url=self.base, headers={"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"}, timeout=timeout)

    def _get(self, path, params=None):
        r = self._http.get(path, params=params or {})
        r.raise_for_status()
        return r.json()

    def quotes(self, symbols):
        return self._get("/v1/cryptocurrency/quotes/latest", {"symbol": ",".join(symbols)})

    def fear_greed(self):
        return self._get("/v3/fear-and-greed/latest")

    def features(self, symbols):
        return {"quotes": self.quotes(symbols), "fear_greed": self.fear_greed()}

    def close(self):
        self._http.close()


if __name__ == "__main__":
    print("CMC base:", CMCClient().base, "| key set:", bool(CMC_API_KEY))
