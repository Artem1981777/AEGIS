# src/backtest/backtest.py
# Stdlib-only backtest: replays regime -> strategy -> risk sentinel over a price series.
import math
import random

from src.agents.regime import MarketSignals
from src.risk.sentinel import PortfolioState
from src.config import SETTINGS
from src.graph.graph import run_cycle

WINDOW = 12
TREND_SCALE = 120.0
VOL_SCALE = 14.0


def synthetic_prices(n=240, seed=7, start=100.0):
    rnd = random.Random(seed)
    prices = [start]
    for i in range(1, n):
        phase = i / n
        if phase < 0.4:
            drift, sigma = 0.004, 0.012
        elif phase < 0.7:
            drift, sigma = 0.0, 0.02
        else:
            drift, sigma = -0.005, 0.03
        ret = drift + rnd.gauss(0, sigma)
        prices.append(round(prices[-1] * (1 + ret), 4))
    return prices


def signal_at(prices, i):
    window = prices[max(0, i - WINDOW):i + 1]
    if len(window) < 3:
        return MarketSignals(50.0, 0.0, 0.4)
    rets = [window[k] / window[k - 1] - 1.0 for k in range(1, len(window))]
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / max(1, len(rets) - 1)
    std = math.sqrt(var)
    trend = max(-1.0, min(1.0, mean * TREND_SCALE))
    vol = max(0.1, min(1.2, std * VOL_SCALE))
    fg = max(0.0, min(100.0, 50.0 + trend * 45.0))
    return MarketSignals(round(fg, 1), round(trend, 3), round(vol, 3))


def run_backtest(prices=None, token="CAKE", cfg=None, start_equity=10000.0, bars_per_day=24):
    prices = prices or synthetic_prices()
    cfg = cfg or SETTINGS.risk_config()
    equity = peak = start_equity
    trades_today = 0
    rets, trades = [], []
    equity_series = [round(equity, 2)]
    wins = losses = 0
    for i in range(len(prices) - 1):
        if i and i % bars_per_day == 0:
            trades_today = 0
        sig = signal_at(prices, i)
        dec = run_cycle(sig, token, PortfolioState(equity, peak, trades_today), cfg=cfg, publish=False)
        size = float(dec.get("final_size_pct") or 0.0)
        side, verdict = dec.get("side"), dec.get("verdict")
        fwd = prices[i + 1] / prices[i] - 1.0
        step = 0.0
        if size > 0.0 and verdict in ("APPROVE", "RESIZE"):
            step = (size / 100.0) * (1.0 if side == "buy" else -1.0) * fwd
            pnl = equity * step
            equity += pnl
            trades_today += 1
            wins, losses = (wins + 1, losses) if pnl >= 0 else (wins, losses + 1)
            trades.append({"i": i, "regime": dec.get("regime"), "side": side, "size": round(size, 2), "price": round(prices[i], 4), "pnl": round(pnl, 2), "verdict": verdict})
        peak = max(peak, equity)
        rets.append(step)
        equity_series.append(round(equity, 2))
    return metrics(start_equity, equity, equity_series, rets, trades, wins, losses, bars_per_day)


def metrics(start_equity, equity, equity_series, rets, trades, wins, losses, bars_per_day):
    peak, max_dd = equity_series[0], 0.0
    for e in equity_series:
        peak = max(peak, e)
        max_dd = max(max_dd, (peak - e) / peak * 100.0 if peak else 0.0)
    sharpe = 0.0
    if len(rets) > 1:
        mean = sum(rets) / len(rets)
        var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
        std = math.sqrt(var)
        if std > 0:
            sharpe = mean / std * math.sqrt(bars_per_day * 365)
    n = len(trades)
    return {"start_equity": round(start_equity, 2), "end_equity": round(equity, 2), "total_return_pct": round((equity / start_equity - 1.0) * 100.0, 2), "max_drawdown_pct": round(max_dd, 2), "sharpe": round(sharpe, 2), "win_rate": round(wins / n * 100.0, 1) if n else 0.0, "trades": n, "wins": wins, "losses": losses, "equity_series": equity_series, "trade_log": trades}


if __name__ == "__main__":
    r = run_backtest()
    print("bars        :", len(r["equity_series"]))
    print("start/end   :", r["start_equity"], "->", r["end_equity"])
    print("return %    :", r["total_return_pct"])
    print("max drawdown:", r["max_drawdown_pct"], "%")
    print("sharpe      :", r["sharpe"])
    print("win rate    :", r["win_rate"], "%")
    print("trades      :", r["trades"], "(W", r["wins"], "/ L", r["losses"], ")")
