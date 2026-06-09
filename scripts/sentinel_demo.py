import json
import os
import sys
from src.risk.sentinel import RiskConfig, TradeProposal, PortfolioState, RiskSentinel

cfg = RiskConfig(
    max_drawdown_pct=10.0,
    per_trade_max_pct=3.0,
    max_slippage_bps=50,
    daily_trade_limit=2,
    vol_target_annual=0.40,
    allowlist=frozenset({"BNB", "WBNB", "USDT", "USDC"}),
)
sentinel = RiskSentinel(cfg)

scenarios = [
    {"name": "Normal momentum buy", "proposal": TradeProposal(token="BNB", side="buy", size_pct=2.0, est_slippage_bps=20, token_vol_annual=0.40), "state": PortfolioState(equity=100.0, peak_equity=100.0, trades_today=0), "expect": "APPROVE"},
    {"name": "High-volatility sizing", "proposal": TradeProposal(token="BNB", side="buy", size_pct=5.0, est_slippage_bps=20, token_vol_annual=0.80), "state": PortfolioState(equity=100.0, peak_equity=100.0, trades_today=0), "expect": "RESIZE"},
    {"name": "Slippage spike", "proposal": TradeProposal(token="BNB", side="buy", size_pct=2.0, est_slippage_bps=120, token_vol_annual=0.40), "state": PortfolioState(equity=100.0, peak_equity=100.0, trades_today=0), "expect": "VETO"},
    {"name": "Unknown token", "proposal": TradeProposal(token="SCAMCOIN", side="buy", size_pct=2.0, est_slippage_bps=20, token_vol_annual=0.40), "state": PortfolioState(equity=100.0, peak_equity=100.0, trades_today=0), "expect": "VETO"},
    {"name": "Drawdown breach", "proposal": TradeProposal(token="BNB", side="buy", size_pct=2.0, est_slippage_bps=20, token_vol_annual=0.40), "state": PortfolioState(equity=88.0, peak_equity=100.0, trades_today=0), "expect": "KILL"},
]

icons = {"APPROVE": "[OK]", "RESIZE": "[~]", "VETO": "[X]", "KILL": "[KILL]"}
results = []
print("AEGIS Risk Sentinel - deterministic guardrail demo")
print("config: max_dd=" + str(cfg.max_drawdown_pct) + "pct per_trade_max=" + str(cfg.per_trade_max_pct) + "pct slippage_cap=" + str(cfg.max_slippage_bps) + "bps daily_limit=" + str(cfg.daily_trade_limit))
print("-" * 60)
for sc in scenarios:
    p = sc["proposal"]
    s = sc["state"]
    verdict, size, reason = sentinel.review(p, s)
    v = verdict.name
    print(icons.get(v, "[?]") + " " + sc["name"] + " -> " + v + " (size " + format(size, ".2f") + "pct) " + reason)
    print("    token=" + p.token + " req_size=" + format(p.size_pct, ".2f") + "pct slippage=" + str(p.est_slippage_bps) + "bps vol=" + format(p.token_vol_annual, ".2f") + " drawdown=" + format(s.drawdown_pct, ".2f") + "pct")
    results.append({"scenario": sc["name"], "token": p.token, "requested_size_pct": p.size_pct, "slippage_bps": p.est_slippage_bps, "token_vol_annual": p.token_vol_annual, "drawdown_pct": round(s.drawdown_pct, 2), "verdict": v, "approved_size_pct": round(size, 4), "reason": reason, "expected": sc["expect"], "match": v == sc["expect"]})
print("-" * 60)
passed = sum(1 for r in results if r["match"])
print("verdicts matched expectations: " + str(passed) + "/" + str(len(results)))
os.makedirs("dashboard", exist_ok=True)
out = {"title": "AEGIS Risk Sentinel demo", "config": {"max_drawdown_pct": cfg.max_drawdown_pct, "per_trade_max_pct": cfg.per_trade_max_pct, "max_slippage_bps": cfg.max_slippage_bps, "daily_trade_limit": cfg.daily_trade_limit, "vol_target_annual": cfg.vol_target_annual}, "results": results, "passed": passed, "total": len(results)}
open("dashboard/sentinel_demo.json", "w").write(json.dumps(out, indent=2))
print("artifact written: dashboard/sentinel_demo.json")
sys.exit(0 if passed == len(results) else 2)
