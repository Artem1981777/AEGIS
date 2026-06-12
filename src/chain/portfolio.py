# src/chain/portfolio.py
# Build PortfolioState from the REAL competition wallet so the dashboard is honest.
import json, os, subprocess
from src.risk.sentinel import PortfolioState

CHAIN = "bsc"
WALLET = (os.getenv("COMPETITION_WALLET") or os.getenv("SAFE_ADDRESS")
          or "0xA7a448F0093c3e5cC1930031cAe4184E5BdDB67E")
STABLES = {
    "USDT": "0x55d398326f99059fF775485246999027B3197955",
    "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
}
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PEAK_FILE = os.path.join(_ROOT, "dashboard", "peak.json")

def _usd(extra):
    try:
        p = subprocess.run(["twak", "balance", "--chain", CHAIN] + extra + ["--json"],
                           capture_output=True, text=True, timeout=45)
        d = json.loads(p.stdout or "{}")
        v = d.get("totalUsd")
        if v is None:
            v = d.get("raw", {}).get("amounts", {}).get("totalInFiat")
        return float(v or 0)
    except Exception:
        return 0.0

def wallet_equity(address=None):
    addr = address or WALLET
    total = _usd(["--address", addr])
    for c in STABLES.values():
        total += _usd(["--address", addr, "--token", c])
    return round(total, 2)

def _read():
    try:
        with open(_PEAK_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def _write(d):
    try:
        os.makedirs(os.path.dirname(_PEAK_FILE), exist_ok=True)
        with open(_PEAK_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

def baseline_equity(current=None):
    env = os.getenv("START_EQUITY_USD")
    if env:
        try:
            return float(env)
        except ValueError:
            pass
    st = _read()
    if "baseline_equity" in st:
        return float(st["baseline_equity"])
    cur = current if current is not None else wallet_equity()
    st["baseline_equity"] = round(cur, 2)
    _write(st)
    return round(cur, 2)

def live_portfolio_state(trades_today=0):
    eq = wallet_equity()
    st = _read()
    peak = max(float(st.get("peak_equity", 0)), eq)
    st["peak_equity"] = round(peak, 2)
    if "baseline_equity" not in st and not os.getenv("START_EQUITY_USD"):
        st["baseline_equity"] = round(eq, 2)
    _write(st)
    return PortfolioState(eq, peak, trades_today)

if __name__ == "__main__":
    ps = live_portfolio_state()
    print("equity:", ps.equity, "peak:", ps.peak_equity,
          "baseline:", baseline_equity(ps.equity), "trades_today:", ps.trades_today)
