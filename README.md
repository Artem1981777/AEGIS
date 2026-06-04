# 🛡️ AEGIS — Autonomous Execution & Guarded Intelligence System

Non-custodial AI trading agent on BNB Chain that thinks like a quant,
executes like a machine, and survives like a guardian.

Built for **BNB Hack: AI Trading Agent Edition** (CoinMarketCap × Trust Wallet × BNB Chain).

## TL;DR
An LLM strategist proposes trades; a deterministic Risk Sentinel can veto them.
The agent earns without blowing up — surviving the drawdown gate that
disqualifies greedy momentum bots.

## Dual-loop design
- Slow loop (15–60 min): LLM reads market, classifies regime, proposes a plan.
- Fast loop (every block): deterministic Risk Sentinel enforces risk, veto, kill-switch.

Plus: on-chain verifiable reasoning, and metered cognition via x402.

## Stack
LangGraph · CoinMarketCap AI Agent Hub (MCP+x402) · Trust Wallet Agent Kit · BNB AI Agent SDK · pgvector/Chroma · React dashboard

## Quickstart
    cp .env.example .env
    pip install -r requirements.txt
    python -m src.main --mode paper

## Risk Constitution
Drawdown circuit breaker · vol-targeted sizing · per-trade & daily limits · 149-token allowlist · self-custody (keys never leave TWAK).

## License
MIT
