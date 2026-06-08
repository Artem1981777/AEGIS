"""TWAK CLI swap executor for AEGIS live trading.

Competition wallet is TWAK-managed (no exportable private key), so trades
execute by shelling out to the twak CLI, which signs internally.
"""
import json
import os
import subprocess

CHAIN = os.getenv("TWAK_CHAIN", "bsc")
SLIPPAGE_PCT = float(os.getenv("MAX_SLIPPAGE_BPS", "80")) / 100.0
TIMEOUT_S = 180


def _run(args):
    proc = subprocess.run(["twak"] + args, capture_output=True, text=True, timeout=TIMEOUT_S)
    out = (proc.stdout or "").strip()
    err = (proc.stderr or "").strip()
    data = None
    if out:
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            data = None
    return {"ok": proc.returncode == 0, "code": proc.returncode, "stdout": out, "stderr": err, "data": data}


def _base(amount, src, dst, slippage_pct, chain):
    slip = SLIPPAGE_PCT if slippage_pct is None else slippage_pct
    return ["swap", str(amount), src, dst, "--chain", chain, "--slippage", str(slip), "--json"]


def quote(amount, src, dst, slippage_pct=None, chain=CHAIN):
    return _run(_base(amount, src, dst, slippage_pct, chain) + ["--quote-only"])


def execute(amount, src, dst, slippage_pct=None, chain=CHAIN, password=None):
    pw = password or os.getenv("TWAK_WALLET_PASSWORD", "")
    if not pw:
        return {"ok": False, "code": -1, "stdout": "", "stderr": "TWAK_WALLET_PASSWORD not set", "data": None}
    return _run(_base(amount, src, dst, slippage_pct, chain) + ["--password", pw])
