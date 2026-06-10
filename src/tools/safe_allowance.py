import os
from decimal import Decimal
from web3 import Web3
from eth_account import Account

RPC = os.getenv("BSC_MAINNET_RPC", "https://bsc-dataseed.binance.org")
SAFE = os.getenv("SAFE_ADDRESS", "0x9BEa0C7b2266F6d7989D27F55d411001736E8949")
MODULE = os.getenv("ALLOWANCE_MODULE", "0xCFbFaC74C26F8647cBDb8c5caf80BB5b32E43134")
TOKEN = os.getenv("TREASURY_TOKEN", "0x55d398326f99059fF775485246999027B3197955")
ABI = [{"name":"getTokenAllowance","type":"function","stateMutability":"view","inputs":[{"name":"s","type":"address"},{"name":"d","type":"address"},{"name":"t","type":"address"}],"outputs":[{"name":"","type":"uint256[5]"}]}]

def _key():
    k = os.getenv("DELEGATE_PRIVATE_KEY","").strip() or open(os.path.expanduser("~/AEGIS/.delegate_key")).read().strip()
    return k if k.startswith("0x") else "0x"+k

def get_allowance():
    da = Account.from_key(_key()).address
    w3 = Web3(Web3.HTTPProvider(RPC))
    c = w3.eth.contract(address=Web3.to_checksum_address(MODULE), abi=ABI)
    v = c.functions.getTokenAllowance(Web3.to_checksum_address(SAFE), da, Web3.to_checksum_address(TOKEN)).call()
    u = Decimal(10)**18
    cap, spent = Decimal(v[0])/u, Decimal(v[1])/u
    return {"ok": True, "safe": SAFE, "module": MODULE, "delegate": da, "cap_usdt": float(cap), "spent_usdt": float(spent), "remaining_usdt": float(max(cap-spent,0)), "reset_min": int(v[2]), "nonce": int(v[4])}

def treasury_gate(amount_usdt):
    try:
        a = get_allowance()
    except Exception as e:
        fc = os.getenv("TREASURY_GATE_FAIL_CLOSED","0") in ("1","true")
        return (not fc, "treasury unavailable: "+str(e), {"ok": False})
    if not amount_usdt or amount_usdt <= 0:
        return (True, "no notional (advisory)", a)
    if amount_usdt <= a["remaining_usdt"] + 1e-9:
        return (True, "within on-chain allowance", a)
    return (False, "exceeds daily allowance", a)

if __name__ == "__main__":
    import json
    print(json.dumps(get_allowance(), indent=2))
