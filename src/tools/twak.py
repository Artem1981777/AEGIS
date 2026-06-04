import os
import httpx

TWAK_ENDPOINT = os.getenv("TWAK_ENDPOINT", "http://localhost:8787")
WALLET = os.getenv("TWAK_WALLET_ADDRESS", "")


class TWAKClient:
    """Trust Wallet Agent Kit client: local signing + broadcast on BSC.

    Keys never leave the local TWAK service; we only send trade intents.
    """

    def __init__(self, endpoint=TWAK_ENDPOINT, wallet=WALLET, timeout=30):
        self.endpoint = endpoint.rstrip("/")
        self.wallet = wallet
        self._http = httpx.Client(base_url=self.endpoint, timeout=timeout)

    def _post(self, path, payload):
        r = self._http.post(path, json=payload)
        r.raise_for_status()
        return r.json()

    def balances(self):
        return self._post("/balances", {"wallet": self.wallet})

    def swap(self, token_in, token_out, amount_in, max_slippage_bps):
        return self._post("/swap", {"wallet": self.wallet, "tokenIn": token_in, "tokenOut": token_out, "amountIn": amount_in, "maxSlippageBps": max_slippage_bps})

    def register_competition(self, contract):
        return self._post("/competition/register", {"wallet": self.wallet, "contract": contract})

    def close(self):
        self._http.close()


if __name__ == "__main__":
    c = TWAKClient()
    print("TWAK endpoint:", c.endpoint, "| wallet:", c.wallet or "(set TWAK_WALLET_ADDRESS)")
