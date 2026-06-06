# src/chain/dex.py
# BSC-testnet DEX layer: WBNB wrap/unwrap (guaranteed) + PancakeSwap V2 swap.
import os
import time

from src.config import SETTINGS
from src.chain import wallet, executor

try:
    from web3 import Web3
except Exception:
    Web3 = None

ROUTER = os.getenv("PANCAKE_ROUTER", "0x9aC64Cc6e4415144C455BD8E4837Fea55603e5c3")
WBNB = os.getenv("WBNB_ADDRESS", "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd")

WBNB_ABI = [{"name": "deposit", "type": "function", "stateMutability": "payable", "inputs": [], "outputs": []}, {"name": "withdraw", "type": "function", "stateMutability": "nonpayable", "inputs": [{"name": "wad", "type": "uint256"}], "outputs": []}, {"name": "balanceOf", "type": "function", "stateMutability": "view", "inputs": [{"name": "a", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}]}]

ROUTER_ABI = [{"name": "getAmountsOut", "type": "function", "stateMutability": "view", "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "path", "type": "address[]"}], "outputs": [{"name": "", "type": "uint256[]"}]},
{"name": "swapExactETHForTokens", "type": "function", "stateMutability": "payable", "inputs": [{"name": "amountOutMin", "type": "uint256"}, {"name": "path", "type": "address[]"}, {"name": "to", "type": "address"}, {"name": "deadline", "type": "uint256"}], "outputs": [{"name": "", "type": "uint256[]"}]}]

def _c():
    return executor._w3()


def _wbnb():
    c = _c()
    if c is None or Web3 is None:
        return None
    return c.eth.contract(address=Web3.to_checksum_address(WBNB), abi=WBNB_ABI)


def _router():
    c = _c()
    if c is None or Web3 is None:
        return None
    return c.eth.contract(address=Web3.to_checksum_address(ROUTER), abi=ROUTER_ABI)


def wbnb_balance():
    w = _wbnb()
    c = _c()
    addr = wallet.address()
    if w is None or addr is None:
        return None
    return float(c.from_wei(w.functions.balanceOf(addr).call(), "ether"))


def _send(func, value=0, gas=200000, dry_run=True):
    if not executor._ready():
        return {"ok": False, "error": "wallet/web3 not ready"}
    c = _c()
    addr = wallet.address()
    tx = func.build_transaction({"from": addr, "value": value, "nonce": c.eth.get_transaction_count(addr), "chainId": SETTINGS.chain_id, "gas": gas, "gasPrice": c.eth.gas_price})
    if dry_run:
        return {"ok": True, "dry_run": True, "to": tx["to"], "value_bnb": float(c.from_wei(value, "ether")), "gas": gas}
    signed = executor.Account.sign_transaction(tx, wallet.PRIVATE_KEY)
    raw = getattr(signed, "raw_transaction", None) or getattr(signed, "rawTransaction", None)
    h = c.eth.send_raw_transaction(raw)
    return {"ok": True, "dry_run": False, "tx_hash": c.to_hex(h)}


def wrap(amount_bnb, dry_run=True):
    w = _wbnb()
    c = _c()
    if w is None:
        return {"ok": False, "error": "no web3"}
    value = c.to_wei(amount_bnb, "ether")
    res = _send(w.functions.deposit(), value=value, gas=120000, dry_run=dry_run)
    res["action"] = "wrap"
    res["amount_bnb"] = amount_bnb
    return res


def unwrap(amount_bnb, dry_run=True):
    w = _wbnb()
    c = _c()
    if w is None:
        return {"ok": False, "error": "no web3"}
    wad = c.to_wei(amount_bnb, "ether")
    res = _send(w.functions.withdraw(wad), value=0, gas=120000, dry_run=dry_run)
    res["action"] = "unwrap"
    res["amount_bnb"] = amount_bnb
    return res


def quote_out(amount_bnb, token_out):
    r = _router()
    c = _c()
    if r is None:
        return None
    amt = c.to_wei(amount_bnb, "ether")
    path = [Web3.to_checksum_address(WBNB), Web3.to_checksum_address(token_out)]
    try:
        outs = r.functions.getAmountsOut(amt, path).call()
        return int(outs[-1])
    except Exception as e:
        return {"error": str(e)[:140]}


def swap_bnb_for_token(token_out, amount_bnb, slippage_bps=80, dry_run=True):
    r = _router()
    c = _c()
    addr = wallet.address()
    if r is None or addr is None:
        return {"ok": False, "error": "no web3"}
    amt = c.to_wei(amount_bnb, "ether")
    path = [Web3.to_checksum_address(WBNB), Web3.to_checksum_address(token_out)]
    q = quote_out(amount_bnb, token_out)
    if not isinstance(q, int):
        return {"ok": False, "error": "no quote/liquidity", "detail": q}
    min_out = int(q * (10000 - slippage_bps) / 10000)
    deadline = int(time.time()) + 600
    func = r.functions.swapExactETHForTokens(min_out, path, addr, deadline)
    res = _send(func, value=amt, gas=300000, dry_run=dry_run)
    res["action"] = "swap"
    res["min_out"] = min_out
    return res


if __name__ == "__main__":
    import sys
    print("router:", ROUTER)
    print("wbnb:", WBNB)
    print("wbnb balance:", wbnb_balance())
    live = "--live" in sys.argv
    if "--unwrap" in sys.argv:
        print(unwrap(0.01, dry_run=not live))
    else:
        print(wrap(0.01, dry_run=not live))
    print("wbnb balance after:", wbnb_balance())
