"""
create_vaults.py — Deploy three demo vaults with different risk levels
Usage: python scripts/create_vaults.py
"""
import os
from web3 import Web3
from eth_account import Account

RPC_URL = os.environ["MANTLE_RPC_TESTNET"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]
FACTORY_ADDRESS = os.environ["VAULT_FACTORY_ADDRESS"]

FACTORY_ABI = [
    {
        "name": "createVault",
        "type": "function",
        "inputs": [
            {"name": "riskLevel",          "type": "uint8"},
            {"name": "rebalanceFrequency", "type": "uint8"},
            {"name": "maxDrawdownBps",     "type": "uint16"},
            {"name": "maxSingleAssetBps",  "type": "uint16"},
        ],
        "outputs": [{"name": "vault", "type": "address"}],
        "stateMutability": "nonpayable",
    }
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)
factory = w3.eth.contract(address=FACTORY_ADDRESS, abi=FACTORY_ABI)

VAULT_CONFIGS = [
    # (risk_level, rebalance_freq, max_drawdown_bps, max_single_asset_bps, label)
    (1, 2, 1000, 6000, "Conservative"),  # 10% max drawdown, 60% single asset cap
    (2, 2, 1500, 6000, "Balanced"),      # 15% max drawdown
    (3, 1, 2500, 7000, "Aggressive"),    # 25% max drawdown, 70% single asset cap
]

deployed_vaults = {}

for risk_level, freq, drawdown, single_asset, label in VAULT_CONFIGS:
    nonce = w3.eth.get_transaction_count(account.address)
    tx = factory.functions.createVault(
        risk_level, freq, drawdown, single_asset
    ).build_transaction({
        "from":   account.address,
        "nonce":  nonce,
        "gas":    500_000,
        "chainId": w3.eth.chain_id,
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Parse vault address from event logs
    vault_address = receipt["logs"][0]["address"]
    deployed_vaults[label] = vault_address
    print(f"  {label} Vault: {vault_address} (tx: {tx_hash.hex()})")

# Write to .env
with open("../.env", "a") as f:
    f.write(f"\nVAULT_CONSERVATIVE={deployed_vaults['Conservative']}")
    f.write(f"\nVAULT_BALANCED={deployed_vaults['Balanced']}")
    f.write(f"\nVAULT_AGGRESSIVE={deployed_vaults['Aggressive']}")

print("\n  Three vault addresses written to .env")
print("Next step: run python src/mosaic_pipeline.py --vault <address>")
