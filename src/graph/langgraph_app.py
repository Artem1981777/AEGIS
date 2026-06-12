# src/graph/langgraph_app.py
# LangGraph supervisor-veto graph for the AEGIS pipeline.
# perceive -> cognize -> (Risk Sentinel veto?) -> execute | halt
import os, sys
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from src.chain.portfolio import live_portfolio_state, baseline_equity


class AegisState(TypedDict, total=False):
    signals: Any
    token: str
    portfolio: Any
    live: bool
    decision: dict
    execution: dict


def perceive(state):
    print("[perceive] token:", state.get("token"))
    return {}


def cognize(state):
    from src.graph.graph import run_cycle
    decision = run_cycle(state["signals"], state["token"], state["portfolio"], publish=False)
    print("[cognize] verdict:", decision.get("verdict"), "size:", decision.get("final_size_pct"))
    return {"decision": decision}


def route(state):
    d = state.get("decision", {})
    verdict = str(d.get("verdict", "")).upper()
    size = d.get("final_size_pct", 0) or 0
    if size <= 0 or "VETO" in verdict or "KILL" in verdict:
        return "halt"
    return "execute"


def execute_node(state):
    from src.chain.trader import execute
    ex = execute(state["decision"], live=bool(state.get("live")))
    print("[execute]", ex)
    return {"execution": ex}


def halt_node(state):
    d = state.get("decision", {})
    ex = {"executed": False, "reason": "blocked by Risk Sentinel", "verdict": d.get("verdict")}
    print("[halt]", ex)
    return {"execution": ex}


def build_app():
    g = StateGraph(AegisState)
    g.add_node("perceive", perceive)
    g.add_node("cognize", cognize)
    g.add_node("execute", execute_node)
    g.add_node("halt", halt_node)
    g.set_entry_point("perceive")
    g.add_edge("perceive", "cognize")
    g.add_conditional_edges("cognize", route, {"execute": "execute", "halt": "halt"})
    g.add_edge("execute", END)
    g.add_edge("halt", END)
    return g.compile()


def main():
    try:
        from src.agents.regime import MarketSignals
    except Exception:
        from src.regime import MarketSignals
    try:
        from src.risk.sentinel import PortfolioState
    except Exception:
        from src.sentinel import PortfolioState
    signals = MarketSignals(62, 0.58, 0.47, 0.012)
    portfolio = live_portfolio_state()
    live = "--live" in sys.argv
    app = build_app()
    final = app.invoke({"signals": signals, "token": "CAKE", "portfolio": portfolio, "live": live})
    print("decision:", final.get("decision"))
    print("execution:", final.get("execution"))


if __name__ == "__main__":
    main()
