# AEGIS - Autonomous Execution and Guarded Intelligence System

Risk-gated AI trading agent on BNB Chain. Built for BNB Hack: AI Trading Agent Edition (Track 1).

## Thesis
The edge is not the model - it is the guardrail. A drawdown breach disqualifies an agent, so AEGIS treats risk as a deterministic, first-class citizen with veto/kill power over every trade.

## Architecture
Dual-loop design:
- Slow loop (cognition): perception -> regime -> strategy proposal.
- Fast loop (guardrail): Risk Sentinel enforces the Risk Constitution and can RESIZE / VETO / KILL.

Pipeline: CMC data -> perception -> regime -> strategy -> Risk Sentinel -> executor/DEX -> BNB Chain.
Orchestrated as a LangGraph supervisor-veto graph (src/graph/langgraph_app.py).

## On-chain (BNB testnet, chain 97)
- ERC-8004 identity: agentId 1282 (gas-free via MegaFuel)
- Wallet: 0xaFe4Ea6E832F68c353237EBa2B03E1dDA0992297
- Proven txs: native transfer, WBNB wrap/unwrap, Risk-Sentinel-gated execution

## Layout
- src/agents - perception, regime, strategy, execution
- src/risk/sentinel.py - Risk Sentinel (veto/kill)
- src/graph - run_cycle + LangGraph app
- src/chain - wallet, executor, dex, trader, register (ERC-8004)
- src/tools - cmc, twak
- src/backtest - backtest + publish
- dashboard - Vercel dashboard + wallet connect
- tests - unit tests

## Setup
    pip install -r requirements.txt
    cp .env.example .env
    python -m src.graph.langgraph_app

## Run
- Graph cycle: python -m src.graph.langgraph_app [--live]
- Trader: python -m src.chain.trader [--live]
- DEX: python -m src.chain.dex [--unwrap] [--live]
- Register: python -m src.chain.register [--dry]
- Backtest: python -m src.backtest.backtest
- Tests: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

## Risk Constitution
max_drawdown 25% (stricter than the ~30% disqualification line), per-trade max 15%, daily limit 20, min 1 trade/day, slippage cap 80 bps, vol target 40%.

## Dashboard
https://aegis-delta-nine.vercel.app

## License
MIT
