# AEGIS - Autonomous Execution and Guarded Intelligence System

Risk-gated, CMC-aware AI trading agent on BNB Chain. Built for BNB Hack: AI Trading Agent Edition (CoinMarketCap x Trust Wallet). Submitted to Track 1 (Autonomous Trading Agents); also ships a CMC Strategy Skill (Track 2 spec). Targets the CMC Agent Hub, Trust Wallet Agent Kit, and BNB AI Agent SDK special prizes.

## Why AEGIS is different
Most agents chase alpha and blow the drawdown gate, and a drawdown breach is an automatic disqualification. AEGIS inverts the problem:
- Survival-first: a deterministic Risk Sentinel can RESIZE, VETO, or KILL any trade before it reaches the chain. The guardrail is the edge.
- Verifiable autonomy: an ERC-8004 on-chain identity (agentId 1282) plus a full decision log of regime, CMC Fear and Greed, momentum, and the Sentinel verdict behind every decision in the live trading loop, so judges can audit each trade on bscscan.
- Full partner stack in one architecture: live CoinMarketCap signals, Trust Wallet Agent Kit self-custody execution, and BNB AI Agent SDK identity, eligible for all three special prizes.
- Live and transparent: a public dashboard streams equity, drawdown, and the exact signal behind each decision in real time.

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

## Native x402 payments (live on-chain proof)

AEGIS pays for CoinMarketCap data per request via x402 (HTTP 402) over the Trust Wallet Agent Kit, settling real USDC on BNB Smart Chain. No API key. The paid call runs inside run_cycle (the autonomous loop), with graceful fallback and skip-reason logging.

- Client src/tools/x402.py wired into src/graph/graph.py run_cycle.
- Asset USDC on BSC 0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d, permit2-exact, 0.01 USDC per call.
- Permit2 approval tx 0xd9b118a05cab52f60ce65c0878e994c20b4a8b8bc7f71cdb858616ef0d1aa096
- Funding swap USDT to USDC tx 0xaaa27d5525e3e5872119576eec6d5572e10f58ed46da4f9b7ae52ed5abce82e5
- Live proof: run_cycle wrote x402BtcUsd = 62828.15 to dashboard/state.json from a paid response.

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

## Demo video
https://youtube.com/shorts/eom-HqzNHc8

## Dashboard
https://aegis-artem7.vercel.app

## License
MIT

## 🛡️ Dual-Guard Treasury (live on BNB Chain mainnet)

AEGIS is autonomous but **cannot drain its treasury**:
- **Sentinel** — software risk veto (APPROVE / RESIZE / VETO / KILL).
- **Safe Allowance Module** — on-chain hard cap; agent is a delegate with a **5 USDT/day** limit; governor key held by the human only.

| Component | Address |
|---|---|
| Safe (treasury) | `0x9BEa0C7b2266F6d7989D27F55d411001736E8949` |
| Allowance Module | `0xCFbFaC74C26F8647cBDb8c5caf80BB5b32E43134` |
| Delegate (agent) | `0xBeaF9e2B5a63C338FD79cEd8bB2C2d58dA0deAe3` |

Live guarded transfer proof: `0x9dcff0bf…c671` (BscScan). Full details in `SUBMISSION.md`.

## 🟢 Live Autonomous Run Log

Verified scheduler-triggered trades on BNB Chain mainnet (no manual action):

| Date | Trigger | Side | Swap | Fallback | Tx | Status |
|---|---|---|---|---|---|---|
| 2026-06-22 | schedule (auto) | SELL | 0.00532 BNB → 3.153961076926417368 USDT | True | [0x58745616…](https://bscscan.com/tx/0x58745616e7a5641b120c9fb5d769f7a9355d6dfa0ba08205d2a249b595f44de9) | success |
