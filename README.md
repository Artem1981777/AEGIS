# AEGIS - Autonomous Execution and Guarded Intelligence System

Risk-gated, CMC-aware AI trading agent on BNB Chain. Built for BNB Hack: AI Trading Agent Edition (CoinMarketCap x Trust Wallet). Competes in Track 1 (Autonomous Trading Agents) and Track 2 (CMC Strategy Skills), and targets the CMC Agent Hub, Trust Wallet Agent Kit, and BNB AI Agent SDK special prizes.

## Thesis
The edge is not the model - it is the guardrail. A drawdown breach disqualifies an agent, so AEGIS treats risk as a deterministic, first-class citizen with veto and kill power over every trade.

## Architecture
Dual-loop design:
- Slow loop (cognition): perception, regime classification, strategy proposal.
- Fast loop (guardrail): the Risk Sentinel enforces the Risk Constitution and can RESIZE, VETO, or KILL any trade.

Pipeline: CoinMarketCap data, perception, regime, strategy, Risk Sentinel, executor and DEX, BNB Chain. Orchestrated as a LangGraph supervisor-veto graph (src/graph/langgraph_app.py).

## Live CMC integration
AEGIS reads live CoinMarketCap signals every cycle:
- Spot quote and momentum (1h, 24h, 7d) from the quotes endpoint.
- Market regime from the Fear and Greed index.
These feed regime classification and position sizing, and drive the autonomous executor.

## Track 1 - Autonomous Trading Agent (live on BNB mainnet, chain 56)
- Runs unattended via GitHub Actions every day at 12:00 MSK, and on demand.
- Each run pulls CMC Fear and Greed plus BNB 24h momentum, classifies the regime, and executes exactly one micro-trade through the Trust Wallet Agent Kit (TWAK) on BNB mainnet.
- Self-custody signing via TWAK. No private keys in code. All secrets injected at runtime.
- ERC-8004 on-chain identity: agentId 1282.
- Competition wallet: 0xA7a448F0093c3e5cC1930031cAe4184E5BdDB67E

Proven live transactions (BNB mainnet, bscscan.com):
- Regime-driven swap 0.003 BNB to 1.8163 USDT: 0x353002534fef60e1a1272aafdb79b6601fb3164329133ebdb0591cbd8bc9f4cd
- First autonomous trade: 0xd18e83d44c94820f5e4471f4a44986bbf59c9f51523fdba874e060fdac47634e

## Track 2 - CMC Strategy Skill
A backtestable, execution-free strategy specification packaged as an official CoinMarketCap skill:
- skills/aegis-momentum-regime/SKILL.md - regime-aware momentum strategy on CMC signals.
- skills/aegis-momentum-regime/references/indicators.md - indicator definitions.
- skills/aegis-momentum-regime/scripts/backtest.py - reference backtest.

## Special prizes
- CMC Agent Hub: live CMC quotes and Fear and Greed drive every decision.
- Trust Wallet Agent Kit: self-custody execution on BNB mainnet via TWAK CLI.
- BNB AI Agent SDK: ERC-8004 identity (agentId 1282) for verifiable agent provenance.

## Layout
- src/agents - perception, regime, strategy, execution
- src/risk/sentinel.py - Risk Sentinel (veto and kill)
- src/graph - run_cycle and LangGraph app
- src/chain - wallet, executor, dex, trader, register (ERC-8004)
- src/tools - cmc, twak
- src/backtest - backtest and publish
- skills/aegis-momentum-regime - Track 2 CMC strategy skill
- dashboard - Vercel dashboard and wallet connect
- tests - unit tests
- .github/workflows/trade.yml - autonomous CMC-aware daily executor

## Setup
~~~
pip install -r requirements.txt
cp .env.example .env
python -m src.graph.langgraph_app
~~~

## Run
- Graph cycle: python -m src.graph.langgraph_app [--live]
- Trader: python -m src.chain.trader [--live]
- DEX: python -m src.chain.dex [--unwrap] [--live]
- Register: python -m src.chain.register [--dry]
- Backtest: python -m src.backtest.backtest
- Tests: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

## Risk Constitution
Max drawdown 10 percent (well inside the disqualification line), per-trade max 3 percent, daily limit 2, min 1 trade per day, slippage cap 50 bps.

## Dashboard
https://aegis-delta-nine.vercel.app

## License
MIT
