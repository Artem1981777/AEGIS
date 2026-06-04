from dataclasses import dataclass


@dataclass
class MarketSignals:
    fear_greed: float
    trend_strength: float
    volatility: float
    funding_rate: float = 0.0


def classify_regime(s: MarketSignals) -> str:
    """Deterministic market-regime classifier.

    Returns one of: "risk_off", "trend", "range".
    """
    if s.fear_greed <= 25 or s.trend_strength <= -0.4 or s.volatility >= 1.0:
        return "risk_off"
    if abs(s.trend_strength) >= 0.4 and s.fear_greed >= 40:
        return "trend"
    return "range"
