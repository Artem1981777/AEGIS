# src/chain/trader.py
# Maps a run_cycle decision to an on-chain action on BSC testnet.
# Heartbeat = WBNB wrap/unwrap (guaranteed); real DEX swap when token+liquidity available.
import os

from src.chain import wallet, dex

TRADE_NOTIONAL_BNB = float(os.getenv("TRADE_NOTIONAL_BNB", "0.05"))
MIN_TRADE_BNB = float(os.getenv("MIN_TRADE_BNB", "0.005"))

def _amount_for(decision):
    pct = float(decision.get("final_size_pct") or 0.0)
    amt = TRADE_NOTIONAL_BNB * pct / 100.0
    if amt < MIN_TRADE_BNB:
        amt = MIN_TRADE_BNB
    return round(amt, 6)


def execute(decision, live=False):
    verdict = decision.get("verdict")
    side = (decision.get("side") or "").upper()
    if verdict not in ("APPROVE", "RESIZE"):
        return {"executed": False, "reason": "blocked by risk: " + str(verdict)}
    if not wallet.address():
        return {"executed": False, "reason": "no wallet"}
    amount = _amount_for(decision)
    token_addr = os.getenv("TRADE_TOKEN_ADDRESS", "")
    if side == "BUY" and token_addr:
        q = dex.quote_out(amount, token_addr)
        if isinstance(q, int) and q > 0:
            res = dex.swap_bnb_for_token(token_addr, amount, dry_run=not live)
            res["executed"] = bool(res.get("ok"))
            res["mode"] = "swap"
            res["intended_token"] = decision.get("token")
            return res
    if side == "SELL":
        res = dex.unwrap(amount, dry_run=not live)
        res["mode"] = "heartbeat_unwrap"
    else:
        res = dex.wrap(amount, dry_run=not live)
        res["mode"] = "heartbeat_wrap"
    res["executed"] = bool(res.get("ok"))
    res["intended_token"] = decision.get("token")
    res["amount_bnb"] = amount
    return res


def decide_and_execute(signals, token, portfolio, live=False, **kw):
    from src.graph.graph import run_cycle
    decision = run_cycle(signals, token, portfolio, publish=False, **kw)
    decision["execution"] = execute(decision, live=live)
    return decision


if __name__ == "__main__":
    import sys
    from src.agents.regime import MarketSignals
    from src.risk.sentinel import PortfolioState
    live = "--live" in sys.argv
    sig = MarketSignals(62, 0.58, 0.47, 0.012)
    port = PortfolioState(10250.0, 10500.0, 3)
    out = decide_and_execute(sig, "CAKE", port, live=live)
    print("verdict:", out["verdict"], "| side:", out["side"], "| size:", out["final_size_pct"])
    print("execution:", out["execution"])
