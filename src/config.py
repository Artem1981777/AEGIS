# src/config.py
# Central configuration for AEGIS. Loads .env if present; targets BSC testnet.
import os
from dataclasses import dataclass, field

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.risk.sentinel import RiskConfig


DEFAULT_ALLOWLIST = "BNB,WBNB,USDT,USDC,BUSD,CAKE,ETH,BTCB,XRP,ADA,DOGE,LINK"


def _f(name, default):
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return float(default)


def _i(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return int(default)


def _allowlist():
    raw = os.getenv("TOKEN_ALLOWLIST", DEFAULT_ALLOWLIST)
    return frozenset(t.strip().upper() for t in raw.split(",") if t.strip())


@dataclass
class Settings:
    network: str = os.getenv("NETWORK", "bsc-testnet")
    chain_id: int = _i("CHAIN_ID", 97)
    rpc_url: str = os.getenv("RPC_URL", "https://data-seed-prebsc-1-s1.binance.org:8545/")
    explorer: str = os.getenv("EXPLORER", "https://testnet.bscscan.com")
    competition_contract: str = os.getenv("COMPETITION_CONTRACT", "0x212c61b9b72c95d95bf29cf032f5e5635629aed5")
    cmc_mcp_url: str = os.getenv("CMC_MCP_URL", "")
    max_drawdown_pct: float = _f("MAX_DRAWDOWN_PCT", 25.0)
    per_trade_max_pct: float = _f("PER_TRADE_MAX_PCT", 15.0)
    max_slippage_bps: int = _i("MAX_SLIPPAGE_BPS", 80)
    daily_trade_limit: int = _i("DAILY_TRADE_LIMIT", 20)
    min_trades_per_day: int = _i("MIN_TRADES_PER_DAY", 1)
    vol_target_annual: float = _f("VOL_TARGET_ANNUAL", 0.40)
    allowlist: frozenset = field(default_factory=_allowlist)

    def risk_config(self):
        return RiskConfig(
            max_drawdown_pct=self.max_drawdown_pct,
            per_trade_max_pct=self.per_trade_max_pct,
            max_slippage_bps=self.max_slippage_bps,
            daily_trade_limit=self.daily_trade_limit,
            vol_target_annual=self.vol_target_annual,
            allowlist=self.allowlist,
        )


SETTINGS = Settings()
