import os
from dotenv import load_dotenv
from src.risk.sentinel import RiskConfig

load_dotenv()


def _f(k, d):
    return float(os.getenv(k, d))


def _i(k, d):
    return int(os.getenv(k, d))


RISK = RiskConfig(
    max_drawdown_pct=_f("MAX_DRAWDOWN_PCT", 25),
    per_trade_max_pct=_f("PER_TRADE_MAX_PCT", 15),
    max_slippage_bps=_i("MAX_SLIPPAGE_BPS", 80),
    daily_trade_limit=_i("DAILY_TRADE_LIMIT", 20),
    vol_target_annual=_f("VOL_TARGET_ANNUAL", 0.40),
)

BSC_RPC_URL = os.getenv("BSC_RPC_URL")
COMPETITION_CONTRACT = os.getenv("COMPETITION_CONTRACT")
