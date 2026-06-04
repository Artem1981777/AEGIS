from src.agents.regime import MarketSignals, classify_regime


def test_risk_off_fear():
    assert classify_regime(MarketSignals(fear_greed=15, trend_strength=0.1, volatility=0.4)) == "risk_off"


def test_trend_up():
    assert classify_regime(MarketSignals(fear_greed=60, trend_strength=0.6, volatility=0.4)) == "trend"


def test_range():
    assert classify_regime(MarketSignals(fear_greed=50, trend_strength=0.1, volatility=0.4)) == "range"


def test_risk_off_vol():
    assert classify_regime(MarketSignals(fear_greed=60, trend_strength=0.1, volatility=1.2)) == "risk_off"
