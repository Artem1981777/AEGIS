# src/chain/trader.py
# Maps a run_cycle decision to an on-chain action on BSC mainnet via TWAK.
# Competition wallet is TWAK-managed (no private key); trades go through twak swap.
import os

from src.chain import twak_swap
from src.chain.portfolio import live_portfolio_state, baseline_equity, stable_balance
try:
    from src.tools import safe_allowance
except Exception:
    safe_allowance = None

TRADE_NOTIONAL_BNB = float(os.getenv("TRADE_NOTIONAL_BNB", "0.05"))
MIN_TRADE_BNB = float(os.getenv("MIN_TRADE_BNB", "0.005"))
TRADE_TOKEN = os.getenv("TRADE_TOKEN", "USDT")
BNB_PRICE_USD = float(os.getenv("BNB_PRICE_USD","0") or 0)
TREASURY_GATE_FAIL_CLOSED = os.getenv("TREASURY_GATE_FAIL_CLOSED","0") in ("1","true")


def _amount_for(decision):
    pct = float(decision.get("final_size_pct") or 0.0)
    amt = TRADE_NOTIONAL_BNB * pct / 100.0
    if amt < MIN_TRADE_BNB:
        amt = MIN_TRADE_BNB
    return round(amt, 6)


def _token_out(quote_res):
    if not quote_res.get("ok") or not quote_res.get("data"):
        return None
    raw = str(quote_res["data"].get("output", "")).strip().split(" ")[0]
    try:
        val = float(raw)
    except ValueError:
        return None
    return val if val > 0 else None


def _execute_raw(decision, live=False):
    verdict = decision.get("verdict")
    side = (decision.get("side") or "").upper()
    if verdict not in ("APPROVE", "RESIZE"):
        return {"executed": False, "reason": "blocked by risk: " + str(verdict)}
    amount = _amount_for(decision)
    token = TRADE_TOKEN
    fallback = False
    if side == "SELL":
        q = _token_out(twak_swap.quote(amount, "BNB", token))
        avail = stable_balance(token)
        sell_amt = round(min(q or 0.0, avail * 0.5), 6)
        if q and sell_amt >= 0.3:
            res = twak_swap.execute(sell_amt, token, "BNB") if live else twak_swap.quote(sell_amt, token, "BNB")
            pair = token + "->BNB"
        else:
            fallback = True  # not enough USDT to SELL: keep daily activity + replenish USDT
            res = twak_swap.execute(amount, "BNB", token) if live else twak_swap.quote(amount, "BNB", token)
            pair = "BNB->" + token
    else:
        res = twak_swap.execute(amount, "BNB", token) if live else twak_swap.quote(amount, "BNB", token)
        pair = "BNB->" + token
    res["executed"] = bool(res.get("ok"))
    res["mode"] = "live_swap" if live else "dry_quote"
    res["side"] = side
    res["pair"] = pair
    res["amount_bnb"] = amount
    res["intended_token"] = decision.get("token")
    res["fallback_rebalance"] = fallback
    return res


def decide_and_execute(signals, token, portfolio, live=False, **kw):
    from src.graph.graph import run_cycle
    decision = run_cycle(signals, token, portfolio, publish=False, **kw)
    decision["execution"] = execute(decision, live=live)
    return decision


def execute(decision, live=False):
    amt = _amount_for(decision)
    nusd = float(decision.get("notional_usd") or 0) or (amt * BNB_PRICE_USD if BNB_PRICE_USD > 0 else 0.0)
    treasury = {"checked": False}
    if safe_allowance is not None:
        try:
            ok, reason, snap = safe_allowance.treasury_gate(nusd)
            treasury = {"checked": True, "ok": ok, "reason": reason, "notional_usd": nusd, "remaining_usdt": (snap or {}).get("remaining_usdt")}
            if not ok and TREASURY_GATE_FAIL_CLOSED:
                return {"executed": False, "reason": "blocked by treasury: " + reason, "treasury": treasury}
        except Exception as e:
            treasury = {"checked": False, "error": str(e)}
            if TREASURY_GATE_FAIL_CLOSED:
                return {"executed": False, "reason": "treasury error: " + str(e), "treasury": treasury}
    res = _execute_raw(decision, live=live)
    if isinstance(res, dict):
        res["treasury"] = treasury
    return res


if __name__ == "__main__":
    import sys
    from src.agents.regime import MarketSignals
    from src.risk.sentinel import PortfolioState
    live = "--live" in sys.argv
    sig = None  # live CMC signals via resolve_signals(token)
    port = live_portfolio_state()
    out = decide_and_execute(sig, "BNB", port, live=live)
    print("verdict:", out["verdict"], "| side:", out["side"], "| size:", out["final_size_pct"])
    print("execution:", out["execution"])
