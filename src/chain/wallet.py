# src/chain/wallet.py
# BSC testnet wallet helper. PRIVATE_KEY comes ONLY from env and is never
# logged or committed. Can generate a fresh testnet wallet on demand.
import os

from src.config import SETTINGS

try:
    from web3 import Web3
except Exception:
    Web3 = None

try:
    from eth_account import Account
except Exception:
    Account = None

PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")


def w3():
    if Web3 is None:
        return None
    return Web3(Web3.HTTPProvider(SETTINGS.rpc_url))


def address():
    if not PRIVATE_KEY or Account is None:
        return None
    return Account.from_key(PRIVATE_KEY).address


def balance_tbnb():
    c = w3()
    addr = address()
    if c is None or addr is None:
        return None
    try:
        wei = c.eth.get_balance(addr)
        return float(c.from_wei(wei, "ether"))
    except Exception:
        return None


def generate():
    if Account is None:
        return None
    acct = Account.create()
    return {"address": acct.address, "private_key": acct.key.hex()}


def status():
    print("web3 installed:", Web3 is not None)
    print("eth_account installed:", Account is not None)
    print("rpc:", SETTINGS.rpc_url, "chain_id:", SETTINGS.chain_id)
    addr = address()
    if addr is None:
        print("no PRIVATE_KEY in env -> generate one (step below)")
        return
    print("address:", addr)
    bal = balance_tbnb()
    if bal is None:
        print("balance: unavailable (web3 missing or RPC offline)")
    else:
        print("balance tBNB:", bal)
        if bal == 0:
            print("fund it: https://testnet.bnbchain.org/faucet-smart")


if __name__ == "__main__":
    status()
