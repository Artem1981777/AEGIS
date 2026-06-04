# src/backtest/publish.py
# Run the backtest and merge real metrics into dashboard/state.json
# (the dashboard shallow-merges these keys over its DEMO defaults).
import json
import os

from src.backtest.backtest import run_backtest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE = os.path.join(ROOT, "dashboard", "state.json")


def _downsample(series, k=24):
    if len(series) <= k:
        return [round(x, 2) for x in series]
    step = (len(series) - 1) / (k - 1)
    return [round(series[int(round(i * step))], 2) for i in range(k)]


def _recent_trades(log, token, n=6):
    return [{"time": "t" + str(t["i"]), "token": token, "side": str(t["side"]).upper(), "size": t["size"], "price": t["price"]} for t in log[-n:]]


def publish(token="CAKE"):
    r = run_backtest(token=token)
    eq = _downsample(r["equity_series"])
    patch = {
        "winRate": r["win_rate"],
        "sharpe": r["sharpe"],
        "drawdown": r["max_drawdown_pct"],
        "equitySeries": eq,
        "btSeries": eq,
        "backtest": {"ret": r["total_return_pct"], "maxDd": r["max_drawdown_pct"], "sharpe": r["sharpe"], "trades": r["trades"], "winRate": r["win_rate"]},
        "trades": _recent_trades(r["trade_log"], token),
    }
    state = {}
    if os.path.exists(STATE):
        try:
            with open(STATE) as f:
                state = json.load(f)
        except Exception:
            state = {}
    state.update(patch)
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2)
    print("merged backtest metrics into", STATE)
    print("ret", patch["backtest"]["ret"], "maxDd", patch["backtest"]["maxDd"], "sharpe", patch["backtest"]["sharpe"], "winRate", patch["winRate"])
    return patch


if __name__ == "__main__":
    publish()
