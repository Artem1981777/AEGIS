from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    APPROVE = "approve"
    RESIZE = "resize"
    VETO = "veto"
    KILL = "kill"


@dataclass
class RiskConfig:
    max_drawdown_pct: float = 25.0
    per_trade_max_pct: float = 15.0
    max_slippage_bps: int = 80
    daily_trade_limit: int = 20
    vol_target_annual: float = 0.40
    allowlist: frozenset = frozenset()


@dataclass
class TradeProposal:
    token: str
    side: str
    size_pct: float
    est_slippage_bps: int
    token_vol_annual: float


@dataclass
class PortfolioState:
    equity: float
    peak_equity: float
    trades_today: int

    @property
    def drawdown_pct(self) -> float:
        if self.peak_equity <= 0:
            return 0.0
        return (1 - self.equity / self.peak_equity) * 100


class RiskSentinel:
    def __init__(self, cfg: RiskConfig):
        self.cfg = cfg

    def review(self, p: TradeProposal, s: PortfolioState):
        if s.drawdown_pct >= self.cfg.max_drawdown_pct:
            return Verdict.KILL, 0.0, "drawdown cap hit -> exit to stable"
        if p.token not in self.cfg.allowlist:
            return Verdict.VETO, 0.0, "token not in allowlist"
        if p.est_slippage_bps > self.cfg.max_slippage_bps:
            return Verdict.VETO, 0.0, "slippage too high"
        if s.trades_today >= self.cfg.daily_trade_limit:
            return Verdict.VETO, 0.0, "daily trade limit reached"
        vol = max(p.token_vol_annual, 1e-6)
        size = min(p.size_pct * (self.cfg.vol_target_annual / vol), self.cfg.per_trade_max_pct)
        if size < p.size_pct:
            return Verdict.RESIZE, size, "vol-targeted resize"
        return Verdict.APPROVE, size, "within risk bounds"
