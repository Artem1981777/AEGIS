---
name: aegis-momentum-regime
description: |
  AEGIS strategy skill: a regime-aware crypto momentum strategy for BNB Chain majors, driven by CoinMarketCap signals (price momentum, Fear and Greed, volatility). Outputs backtestable long or flat target allocations with a deterministic risk overlay (drawdown kill-switch, per-trade sizing caps).
  Use this skill when the user wants a backtestable trading strategy from CMC market data, a momentum or regime strategy on BSC tokens, or types /aegis-momentum-regime.
  Trigger: "aegis strategy", "momentum strategy", "regime strategy", "backtestable strategy", "/aegis-momentum-regime"
user-invocable: true
allowed-tools:
- Bash
- Read
---

# AEGIS Momentum-Regime Strategy

A backtestable, regime-aware momentum strategy for BNB Chain majors (BNB, ETH, BTCB, CAKE), authored as a CoinMarketCap Skill. It consumes CMC signals and outputs a target allocation per asset plus a risk verdict. The spec is fully backtestable on CMC historical quotes; no live execution is required.

## Data inputs (CoinMarketCap)
- Spot quotes and momentum from cryptocurrency quotes latest: price, percent_change_1h, percent_change_24h, percent_change_7d.
- Market sentiment from the Fear and Greed index latest, range 0 to 100.
- Optional CMC pre-computed indicators: RSI, MACD, EMA, ATR.
- Client reference: src/tools/cmc.py exposes quote(symbol) and fear_greed().

## Derived indicators
- Momentum M equals 0.4 times pct_24h plus 0.6 times pct_7d.
- Trend strength T equals fast EMA minus slow EMA (sign and magnitude).
- Volatility V equals ATR over 14 periods, used for inverse-volatility sizing.
- Sentiment S equals the Fear and Greed index.

## Regime classification
- RISK_ON: T greater than 0 and S between 25 and 80.
- RISK_OFF: T less than 0, or S below 20 (extreme fear). Allocation goes flat.
- EUPHORIA: S above 85. Exposure is halved as a mean-reversion guard.

## Entry and exit rules
- Enter long when M is positive and regime is RISK_ON.
- Exit to flat when regime is RISK_OFF or M turns negative.
- Position size equals base weight scaled by inverse volatility, capped at 3 percent of equity per trade.

## Risk overlay (deterministic sentinel)
Mirrors src/risk/sentinel.py. Every proposed order receives a verdict:
- APPROVE: within all limits.
- RESIZE: size above the 3 percent per-trade cap is scaled down.
- VETO: trades today at or above the daily limit of 2, new entries blocked.
- KILL: drawdown from peak equity above 10 percent forces the portfolio flat.

## Backtest specification
- Universe: CMC BSC majors allowlist (BNB, WBNB, ETH, BTCB, USDT, USDC).
- Cadence: daily rebalance on CMC daily close quotes.
- Costs modelled: 0.5 percent slippage plus fixed gas per trade.
- Metrics: total return, Sharpe ratio, maximum drawdown, win rate.
- Runner: scripts/backtest.py.

## Reference results
On the in-repo historical sample the strategy returned plus 1.61 percent with a Sharpe ratio of 3.19 and a maximum drawdown of 3.62 percent, well inside the 10 percent drawdown safeguard required by the competition.

## Files
- scripts/backtest.py: runnable backtester producing the metrics above.
- references: extended indicator and parameter notes.
