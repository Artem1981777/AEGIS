import os
from decimal import Decimal

try:
    from web3 import Web3
except Exception:
    Web3 = None

try:
    from eth_account import Account
except Exception:
    Account = None

RPC_URL = os.getenv("BSC_MAINNET_RPC", os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org"))
CHAIN_ID = int(os.getenv("SAFE_CHAIN_ID", "56"))
SAFE_ADDRESS = os.getenv("SAFE_ADDRESS", "0x9BEa0C7b2266F6d7989D27F55d411001736E8949")
ALLOWANCE_MODULE = os.getenv("ALLOWANCE_MODULE", "0xCFbFaC74C26F8647cBDb8c5caf80BB5b32E43134")
TREASURY_TOKEN = os.getenv("TREASURY_TOKEN", "0x55d398326f99059fF775485246999027B3197955")
TOKEN_DECIMALS = int(os.getenv("TREASURY_TOKEN_DECIMALS", "18"))
ZERO = "0x0000000000000000000000000000000000000000"

ALLOWANCE_ABI = [
    {
        "name": "getTokenAllowance", "type": "function", "stateMutability": "view",
        "inputs": [
            {"name": "safe", "type": "address"},
            {"name": "delegate", "type": "address"},
            {"name": "token", "type": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256[5]"}],
    },
    {
        "name": "executeAllowanceTransfer", "type": "function", "stateMutability": "nonpayable",
        "inputs": [
            {"name": "safe", "type": "address"},
            {"name": "token", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "amount", "type": "uint96"},
            {"name": "paymentToken", "type": "address"},
            {"name": "payment", "type": "uint96"},
            {"name": "delegate", "type": "address"},
            {"name": "signature", "type": "bytes"},
        ],
        "outputs": [],
    },
]
