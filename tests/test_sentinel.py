from src.risk.sentinel import RiskSentinel, RiskConfig, TradeProposal, PortfolioState, Verdict

CFG = RiskConfig(allowlist=frozenset({"CAKE", "TWT"}))
SENT = RiskSentinel(CFG)


def test_kill():
    s = PortfolioState(equity=70, peak_equity=100, trades_today=0)
    p = TradeProposal("CAKE", "buy", 10, 20, 0.4)
    assert SENT.review(p, s)[0] is Verdict.KILL


def test_resize():
    s = PortfolioState(equity=100, peak_equity=100, trades_today=0)
    p = TradeProposal("CAKE", "buy", 10, 20, 0.8)
    v, size, _ = SENT.review(p, s)
    assert v is Verdict.RESIZE and size < 10


def test_veto():
    s = PortfolioState(equity=100, peak_equity=100, trades_today=0)
    p = TradeProposal("SCAM", "buy", 5, 10, 0.3)
    assert SENT.review(p, s)[0] is Verdict.VETO
