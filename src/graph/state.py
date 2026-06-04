from typing import TypedDict, Literal, Optional


class AgentState(TypedDict):
    regime: Literal["trend", "range", "risk_off"]
    features: dict
    proposal: Optional[dict]
    verdict: Optional[str]
    final_size_pct: float
    rationale: str
    equity: float
    peak_equity: float
    trades_today: int
