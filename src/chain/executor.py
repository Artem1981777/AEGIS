# src/chain/executor.py
# Real BSC-testnet transaction executor: builds, signs (local key), broadcasts.
# dry_run=True returns the unsigned plan; dry_run=False actually sends.
import os

from src.config import SETTINGS
from src.chain import wallet

try:
    from web3 import Web3
except Exception:
    Web3 = None

try:
    from eth_account import Account
except Exception:
    Account = None


def _w3():
    return wallet.w3()


def _ready():
    return Web3 is not None and Account is not None and wallet.PRIVATE_KEY != "" and _w3() is not None


def gas_price():
    c = _w3()
    if c is None:
        return None
    try:
        return c.eth.gas_price
    except Exception:
        return None


def build_native(to, amount_bnb):
    c = _w3()
    addr = wallet.address()
    if c is None or addr is None:
        return None
    value = c.to_wei(amount_bnb, "ether")
    tx = {"from": addr, "to": Web3.to_checksum_address(to), "value": value}
    tx["nonce"] = c.eth.get_transaction_count(addr)
    tx["chainId"] = SETTINGS.chain_id
    tx["gas"] = 21000
    tx["gasPrice"] = c.eth.gas_price
    return tx


def send_native(to, amount_bnb, dry_run=True):
    if not _ready():
        return {"ok": False, "error": "wallet/web3 not ready"}
    tx = build_native(to, amount_bnb)
    if tx is None:
        return {"ok": False, "error": "could not build tx"}
    plan = {"to": tx["to"], "value_bnb": amount_bnb, "nonce": tx["nonce"], "gasPrice_gwei": round(tx["gasPrice"] / 1e9, 3)}
    if dry_run:
        return {"ok": True, "dry_run": True, "plan": plan}
    c = _w3()
    signed = Account.sign_transaction(tx, wallet.PRIVATE_KEY)
    raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction", None)
    h = c.eth.send_raw_transaction(raw)
    return {"ok": True, "dry_run": False, "tx_hash": c.to_hex(h), "plan": plan}


if __name__ == "__main__":
    import sys
    print("ready:", _ready())
    addr = wallet.address()
    print("address:", addr)
    gp = gas_price()
    print("gas price gwei:", round(gp / 1e9, 3) if gp else None)
    live = "--live" in sys.argv
    res = send_native(addr, 0.001, dry_run=not live)
    print("result:", res)
    if res.get("tx_hash"):
        print("explorer:", SETTINGS.explorer + "/tx/" + res["tx_hash"])
