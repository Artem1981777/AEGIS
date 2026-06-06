# src/chain/register.py ERC-8004 on-chain agent registration (BNB testnet, gas-free via MegaFuel)
import os, sys
from dotenv import load_dotenv

load_dotenv()

NAME = os.getenv("AGENT_NAME", "AEGIS")
DESC = os.getenv("AGENT_DESC", "Autonomous Execution and Guarded Intelligence System - risk-gated AI trading agent on BNB Chain")
ENDPOINT = os.getenv("AGENT_ENDPOINT", "https://aegis-delta-nine.vercel.app")
REGISTRY = "0x8004A818BFB912233c491871b3d84c89A494BD9e"

def register():
    from bnbagent import ERC8004Agent, AgentEndpoint, EVMWalletProvider
    wallet = EVMWalletProvider(
        password=os.getenv("WALLET_PASSWORD"),
        private_key=os.getenv("PRIVATE_KEY"),
    )
    sdk = ERC8004Agent(network="bsc-testnet", wallet_provider=wallet)
    agent_uri = sdk.generate_agent_uri(
        name=NAME,
        description=DESC,
        endpoints=[AgentEndpoint(name="dashboard", endpoint=ENDPOINT, version="0.1.0")],
    )
    print("agent_uri:", agent_uri)
    result = sdk.register_agent(agent_uri=agent_uri)
    print("registered agentId:", result.get("agentId"))
    print("tx:", result.get("transactionHash"))
    return result


if __name__ == "__main__":
    if "--dry" in sys.argv:
        print("name:", NAME)
        print("endpoint:", ENDPOINT)
        print("registry:", REGISTRY, "(BSC testnet, chain 97)")
        print("gas: sponsored by MegaFuel paymaster (gas-free)")
        print("dry run - no tx. Re-run without --dry to register.")
    else:
        register()
