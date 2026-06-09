# AEGIS — Autonomous Execution & Guarded Intelligence System

Survival-first autonomous trading agent on BNB Chain. The edge is the guardrail.

## One-liner
AEGIS is a fully autonomous trading agent for BNB Chain that pairs an LLM cognition loop with a deterministic Risk Sentinel holding veto and kill power over every trade — purpose-built for a competition where the largest drawdown gets you disqualified.

## The problem
Autonomous trading competitions do not reward the boldest agent. They eliminate the one that breaches a drawdown limit. Most agents optimize purely for upside and ignore the gate that actually decides who survives. Autonomy without hard, verifiable risk control is a liability, not an edge.

## The solution
AEGIS runs two loops in tandem:

1. Cognition loop (LLM + LangGraph). Reads live market structure from CoinMarketCap — Fear and Greed, momentum, volatility, regime — classifies the regime and proposes a single trade.
2. Risk Sentinel loop (deterministic, non-negotiable). Every proposal passes through a pure-Python guardrail before it can touch the chain:
   - Drawdown breach -> KILL (exit to stable, no new exposure)
   - Token not in allowlist -> VETO
   - Slippage above cap -> VETO
   - Daily trade limit reached -> VETO
   - Position too large for current volatility -> RESIZE (volatility-targeted)
   - Within bounds -> APPROVE

The intelligence proposes; the guardrail disposes. The Sentinel can always override or shut down the AI.

## Why AEGIS stands out
1. Survival-first by design. The guardrail is executable code, not a paragraph in a README. It is proven by scripts/sentinel_demo.py (5 of 5 scenarios) and surfaced live on the public dashboard as a verdict panel.
2. Verifiable autonomy. The agent carries an on-chain identity via the BNB AI Agent SDK and ERC-8004 (agentId 1282). Every decision — regime, signals, Sentinel verdict, transaction — is logged and auditable on bscscan.
3. Full BNB partner stack. CoinMarketCap signals, Trust Wallet TWAK execution, and BNB AI Agent SDK identity — qualifying across Track 1, Track 2, and all three special prizes.
4. Live and transparent. The agent runs daily on GitHub Actions and publishes a public dashboard with an explainable decision log.

## Architecture
~~~
[CoinMarketCap signals] --> [Cognition loop: regime + momentum] --> trade proposal
                                                                       |
                                                                       v
                                    [Risk Sentinel: APPROVE / RESIZE / VETO / KILL]
                                                                       |
                                                          APPROVE or RESIZE only
                                                                       v
                            [Trust Wallet TWAK] --> [BNB Chain mainnet swap] --> [bscscan]
                                                                       |
                                                                       v
                              [Public dashboard + decision log + proof artifacts]
~~~

## Tracks and prizes targeted
- Track 1 — Autonomous Trading Agents: live mainnet agent, daily cadence, drawdown-gated.
- Track 2 — Strategy Skills: the aegis-momentum-regime skill (regime classifier plus backtest).
- Special — Trust Wallet TWAK: mainnet execution through the TWAK CLI.
- Special — CoinMarketCap Agent Hub: CMC-driven regime and Fear and Greed signals.
- Special — BNB AI Agent SDK: ERC-8004 verifiable agent identity (agentId 1282).

## Tech stack
BNB Chain mainnet (chain 56), Trust Wallet TWAK CLI, CoinMarketCap API, ERC-8004 identity, LangGraph dual-loop, GitHub Actions as the autonomous host, Vercel dashboard.

## Proof and links
- Repository: github.com/Artem1981777/AEGIS
- Live dashboard: aegis-delta-nine.vercel.app
- Sample mainnet swap: 0x353002534fef60e1a1272aafdb79b6601fb3164329133ebdb0591cbd8bc9f4cd (0.003 BNB to 1.8163 USDT)
- Risk Sentinel demo: scripts/sentinel_demo.py with proof artifact dashboard/sentinel_demo.json

## Verify it yourself
~~~
PYTHONPATH=. python3 scripts/sentinel_demo.py
~~~
Expected output: 5 of 5 verdicts match — APPROVE, RESIZE, VETO, VETO, KILL — and a proof artifact is written to dashboard/sentinel_demo.json.

## Roadmap
- Deeper TWAK x402 metered execution and twak automate scheduling.
- Expanded strategy-skill library on the CoinMarketCap Agent Hub.
- Multi-asset regime rotation within the allowlist.

## Native x402 payments (live on-chain proof)

AEGIS pays for CoinMarketCap market data per request via the x402 protocol (HTTP 402) over Trust Wallet Agent Kit (TWAK), settling real USDC micropayments on BNB Smart Chain. No API key, no subscription.

- Client: `src/tools/x402.py` (`btc()` and `price_usd()` call `twak x402 request` and parse the paid response).
- Asset: USDC on BSC `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`, method permit2-exact, $0.01 per call.
- Permit2 one-time approval tx: `0xd9b118a05cab52f60ce65c0878e994c20b4a8b8bc7f71cdb858616ef0d1aa096`
- Funding swap (USDT to USDC) tx: `0xcdb4c38d368bff0d628435e690794681336f100dc2a59afedc02df6bcadba252`
- Verified live: a paid x402 request through our own code returned BTC = $62,640.52.
- Wired into the autonomous loop: the paid x402 call runs inside run_cycle (src/graph/graph.py) with graceful fallback and skip-reason logging, not a side script.
- Live in-loop proof: a run_cycle run wrote x402BtcUsd = 62828.15 to dashboard/state.json from a paid response; funding swap tx 0xaaa27d5525e3e5872119576eec6d5572e10f58ed46da4f9b7ae52ed5abce82e5.
