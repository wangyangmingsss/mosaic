"""
Update README.md live stats section with on-chain data from Mantle Mainnet.
Runs via GitHub Actions every 15 minutes.
"""
import os
import re
import json
from web3 import Web3
from datetime import datetime, timezone

RPC = os.environ.get("MANTLE_RPC", "https://rpc.mantle.xyz")
w3 = Web3(Web3.HTTPProvider(RPC))

# V2 Contract addresses
DECISION_LOG = "0xB123cE88e8b1b8de606574BbA99b655D0D456994"
IDENTITY_REGISTRY = "0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95"

VAULTS = {
    "Conservative": "0xF3Df82262522307C6442137F24dA6710B182AE8b",
    "Balanced": "0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA",
    "Aggressive": "0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625",
}

# Minimal ABIs
DECISION_LOG_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"vault","type":"address"}],"name":"getTotalDecisions","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')

def get_total_decisions():
    contract = w3.eth.contract(address=Web3.to_checksum_address(DECISION_LOG), abi=DECISION_LOG_ABI)
    total = 0
    for name, addr in VAULTS.items():
        count = contract.functions.getTotalDecisions(Web3.to_checksum_address(addr)).call()
        total += count
    return total

def update_readme():
    total_decisions = get_total_decisions()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "r") as f:
        content = f.read()

    # Update total decisions count if there's a pattern to match
    pattern = r"(Total decisions on-chain \| )\*\*\d+\*\*"
    replacement = rf"\1**{total_decisions}**"
    content = re.sub(pattern, replacement, content)

    # Update last updated timestamp
    pattern2 = r"_Last updated: .*?_"
    replacement2 = f"_Last updated: {now}_"
    content = re.sub(pattern2, replacement2, content)

    with open(readme_path, "w") as f:
        f.write(content)

    print(f"Updated README: {total_decisions} total decisions, {now}")

if __name__ == "__main__":
    update_readme()
