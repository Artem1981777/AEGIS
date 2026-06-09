# src/graph/graph.py
# AEGIS cognition cycle: regime -> strategy -> risk sentinel -> dashboard state.
import json
import os

from src.agents.regime import classify_regime, MarketSignals
from src.agents.strategy import propose_trade
from src.risk.sentinel import RiskConfig, RiskSentinel, PortfolioState, Verdict
from src.config import SETTINGS
from src.tools import cmc


REGIME_LABELS = {"risk_off": "RISK-OFF", "trend": "TREND", "range": "RANGE"}


def _round(x, n=2):
    try:
        return round(float(x), n)
    except (TypeError, ValueError):
        return 0.0


def _clamp_pct(x):
    return _round(max(0.0, min(100.0, x)), 1)


def _confidence(signals, regime):
    score = 50.0 + abs(signals.trend_strength) * 35.0 + (signals.fear_greed - 50.0) * 0.2
    if regime == "range":
        score -= 12.0
    return int(max(5, min(95, round(score))))


def build_state(result, portfolio, signals, cfg, start_equity=None,
                equity_series=None, positions=None, trades=None):
    dd = float(portfolio.drawdown_pct)
    vol_pct = int(round(signals.volatility * 100))
    trend_txt = ("+" if signals.trend_strength >= 0 else "") + str(_round(signals.trend_strength, 2))
    fund_txt = ("+" if signals.funding_rate >= 0 else "") + str(_round(signals.funding_rate, 3)) + "%"
    regime_label = REGIME_LABELS.get(result["regime"], str(result["regime"]).upper())
    state = {
        "equity": _round(portfolio.equity),
        "drawdown": _round(dd, 1),
        "tradesToday": int(portfolio.trades_today),
        "regime": regime_label,
        "decision": {
            "token": result["token"],
            "side": str(result["side"]).upper(),
            "size": _round(result["final_size_pct"]),
            "confidence": int(result.get("confidence", 0)),
            "verdict": str(result["verdict"]).upper(),
            "reason": result["reason"],
        },
        "risk": {
            "drawdownUsed": _clamp_pct(dd / cfg.max_drawdown_pct * 100.0 if cfg.max_drawdown_pct else 0.0),
            "exposure": _round(result.get("final_size_pct", 0.0), 1),
            "dailyTradesUsed": _clamp_pct(portfolio.trades_today / cfg.daily_trade_limit * 100.0 if cfg.daily_trade_limit else 0.0),
        },
        "signals": [
            {"name": "Fear & Greed", "value": str(signals.fear_greed)},
            {"name": "Trend strength", "value": trend_txt},
            {"name": "Volatility (ann)", "value": str(vol_pct) + "%"},
            {"name": "Funding rate", "value": fund_txt},
        ],
        "reasoning": [
            "Regime=" + regime_label + " (F&G " + str(signals.fear_greed) + ", trend " + trend_txt + ").",
            "Strategy proposes " + str(result["side"]).upper() + " " + str(result["token"]) + " at base " + str(_round(result["proposed_size_pct"])) + "%.",
            "Sentinel " + str(result["verdict"]).upper() + ": " + str(result["reason"]) + ".",
            "Final size " + str(_round(result["final_size_pct"])) + "% of equity.",
        ],
    }
    if start_equity:
        pnl = portfolio.equity - start_equity
        state["pnlValue"] = _round(pnl)
        state["pnlPct"] = _round(pnl / start_equity * 100.0)
    if equity_series:
        state["equitySeries"] = [_round(v) for v in equity_series]
    if positions is not None:
        state["positions"] = positions
    if trades is not None:
        state["trades"] = trades
    state["x402BtcUsd"] = result.get("x402_btc_usd")
    return state


def write_state(state, path=None):
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(os.path.dirname(here))
        path = os.path.join(root, "dashboard", "state.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path


def run_cycle(signals, token, portfolio, cfg=None, publish=True,
              start_equity=None, equity_series=None, positions=None, trades=None):
    if cfg is None:
        cfg = SETTINGS.risk_config()
    if signals is None:
        signals = resolve_signals(token)
    regime = classify_regime(signals)
    proposal = propose_trade(regime, token, signals.volatility)
    verdict, size, reason = RiskSentinel(cfg).review(proposal, portfolio)
    final_size = size if verdict in (Verdict.APPROVE, Verdict.RESIZE) else 0.0
    try:
        from src.tools.x402 import btc, price_usd
        x402_btc_usd = price_usd(btc())
    except Exception as _e:
        x402_btc_usd = None
        print("x402 skipped:", _e)
    result = {
        "token": token,
        "regime": regime,
        "side": proposal.side,
        "proposed_size_pct": proposal.size_pct,
        "verdict": verdict.name,
        "final_size_pct": _round(final_size),
        "confidence": _confidence(signals, regime),
        "reason": reason,
        "x402_btc_usd": x402_btc_usd,
    }
    if publish:
        write_state(build_state(result, portfolio, signals, cfg,
                                start_equity=start_equity,
                                equity_series=equity_series,
                                positions=positions, trades=trades))
    return result


if __name__ == "__main__":
    sig = MarketSignals(fear_greed=62, trend_strength=0.58, volatility=0.47, funding_rate=0.012)
    pf = PortfolioState(equity=10250.0, peak_equity=10500.0, trades_today=3)
    out = run_cycle(sig, "CAKE", pf, start_equity=10000.0)
    print("regime  :", out["regime"])
    print("side    :", out["side"], "->", out["final_size_pct"], "%")
    print("verdict :", out["verdict"], "-", out["reason"])
    print("wrote dashboard/state.json")


def _synthetic_signals():
    return MarketSignals(50.0, 0.0, 0.40)


def resolve_signals(token, fallback=None):
    sig = None
    try:
        sig = cmc.live_signals(token)
    except Exception:
        sig = None
    if sig is not None:
        return sig
    return fallback if fallback is not None else _synthetic_signals()
