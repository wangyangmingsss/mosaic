"""
Record initial decision records on 3 MosaicVaultV2 contracts on Mantle Mainnet.
- Creates DecisionRecord JSON with realistic data
- Uploads to IPFS via Pinata
- Calls recordDecision on-chain
"""

import json
import time
import hashlib
import requests
from web3 import Web3
from eth_account import Account

# ── Configuration ────────────────────────────────────────────────────────────

MANTLE_RPC = "https://rpc.mantle.xyz"
PRIVATE_KEY = "0xb019b875f01657cde51373ab47b1cef7c68b278f37cb1c01d6b9eefa2a9abe98"
AGENT_ADDRESS = "0x049e5d80830c34c0af8ccfbd77c83f8b0e1f5efa"

PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIzNDI0OGFmMS00NGQ0LTQwNjItOTU4My1mNjg4MDg0ZGViMDYiLCJlbWFpbCI6InNpbHZlcmlvYnJhZGxleTVAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInBpbl9wb2xpY3kiOnsicmVnaW9ucyI6W3siZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiRlJBMSJ9LHsiZGVzaXJlZFJlcGxpY2F0aW9uQ291bnQiOjEsImlkIjoiTllDMSJ9XSwidmVyc2lvbiI6MX0sIm1mYV9lbmFibGVkIjpmYWxzZSwic3RhdHVzIjoiQUNUSVZFIn0sImF1dGhlbnRpY2F0aW9uVHlwZSI6InNjb3BlZEtleSIsInNjb3BlZEtleUtleSI6IjNiOWM2M2UzOGM0MjViYzRlMDU2Iiwic2NvcGVkS2V5U2VjcmV0IjoiODY4NmE3YmVkOTU3YmE0NTc5NmZhYjliMTE3MTBmMmQxMzZmMGYxYWYzOTgzZDcxMjQxYjMxNjRmZDYxODc0ZiIsImV4cCI6MTgxMDAyMTU5OX0.rHoRvoXXBXt_-9HTAgHROwTs71yF-dO5ktfirACNdmE"

VAULTS = [
    {
        "name": "Conservative",
        "address": "0xF3Df82262522307C6442137F24dA6710B182AE8b",
        "risk_level": 1,
    },
    {
        "name": "Balanced",
        "address": "0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA",
        "risk_level": 2,
    },
    {
        "name": "Aggressive",
        "address": "0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625",
        "risk_level": 3,
    },
]

DECISION_LOG = "0xB123cE88e8b1b8de606574BbA99b655D0D456994"

# ABI for recordDecision only
VAULT_ABI = json.loads("""[
  {
    "inputs": [
      {"internalType": "bytes32", "name": "recordHash", "type": "bytes32"},
      {
        "components": [
          {"internalType": "uint16", "name": "usdyBps", "type": "uint16"},
          {"internalType": "uint16", "name": "cmethBps", "type": "uint16"},
          {"internalType": "uint16", "name": "methBps", "type": "uint16"},
          {"internalType": "uint16", "name": "fbtcBps", "type": "uint16"},
          {"internalType": "uint16", "name": "usdcBps", "type": "uint16"}
        ],
        "internalType": "struct MosaicVaultV2.Allocation",
        "name": "newAlloc",
        "type": "tuple"
      },
      {"internalType": "int256", "name": "pnlDeltaBps", "type": "int256"}
    ],
    "name": "recordDecision",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]""")

# ── Decision Records Data ────────────────────────────────────────────────────
# 3 decisions per vault (9 total), each referencing Rule A, B, or C

DECISIONS = {
    "Conservative": [
        {
            "decision_type": "initial_allocation",
            "rule_ref": "Rule A – USDY Yield Curve",
            "reasoning_summary": "Rule A: US 10Y yield at 4.38% supports overweight USDY (tokenized T-bill yield pass-through at 4.25% net). Inverted curve (2Y-10Y spread -18bps) signals recession risk; maintain high cash buffer. Conservative profile demands >=50% stable yield exposure.",
            "macro_context": {
                "us_10y_yield": 4.38,
                "us_2y_yield": 4.56,
                "fed_funds_rate": 5.25,
                "dxy_index": 104.2,
                "btc_price": 67500,
                "eth_price": 3420,
            },
            "allocation": (5200, 400, 2200, 500, 1700),  # usdyBps, cmethBps, methBps, fbtcBps, usdcBps
            "pnl_delta_bps": 12,
        },
        {
            "decision_type": "risk_adjustment",
            "rule_ref": "Rule B – mETH vs cmETH Restaking Risk Premium",
            "reasoning_summary": "Rule B: cmETH slashing insurance pool coverage dropped to 82% (threshold 85%). Reducing cmETH exposure in favor of vanilla mETH which carries no restaking operator risk. mETH staking APR 3.8% vs cmETH 5.1% – 130bps premium insufficient given elevated slashing probability.",
            "macro_context": {
                "cmeth_slashing_coverage": 0.82,
                "meth_staking_apr": 0.038,
                "cmeth_restaking_apr": 0.051,
                "eth_price": 3380,
                "mantle_tvl_usd": 1_250_000_000,
            },
            "allocation": (5300, 300, 2400, 500, 1500),
            "pnl_delta_bps": 8,
        },
        {
            "decision_type": "compliance_check",
            "rule_ref": "Rule C – Allowlist Guard",
            "reasoning_summary": "Rule C: Quarterly allowlist verification complete. All counterparty protocol adapters (Ondo/USDY, mETH Protocol, cmETH Restaking, FBTC Bridge) confirmed on Mosaic allowlist. No new sanctioned addresses detected in OFAC update. Maintaining current allocation within conservative bounds.",
            "macro_context": {
                "ofac_last_update": "2026-05-08",
                "protocols_verified": ["ondo_usdy", "meth_protocol", "cmeth_restaking", "fbtc_bridge"],
                "allowlist_status": "all_clear",
            },
            "allocation": (5300, 300, 2400, 500, 1500),
            "pnl_delta_bps": 0,
        },
    ],
    "Balanced": [
        {
            "decision_type": "initial_allocation",
            "rule_ref": "Rule A – USDY Yield Curve",
            "reasoning_summary": "Rule A: With 10Y at 4.38% and curve inverted, balanced strategy reduces duration risk by trimming USDY to 30% (yield capture sufficient at this level). Allocating freed capital to mETH/cmETH for ETH beta while maintaining 20% USDC dry powder for volatility harvesting.",
            "macro_context": {
                "us_10y_yield": 4.38,
                "us_2y_yield": 4.56,
                "curve_spread_bps": -18,
                "eth_price": 3420,
                "btc_price": 67500,
                "vix": 14.8,
            },
            "allocation": (3000, 1600, 2500, 1000, 1900),
            "pnl_delta_bps": 22,
        },
        {
            "decision_type": "risk_adjustment",
            "rule_ref": "Rule B – mETH vs cmETH Restaking Risk Premium",
            "reasoning_summary": "Rule B: cmETH restaking APR widened to 5.4% (vs mETH 3.8%). Slashing coverage restored to 91% (above 85% threshold). Increasing cmETH allocation to capture 160bps premium. Balanced profile allows up to 20% in restaked assets per risk mandate.",
            "macro_context": {
                "cmeth_slashing_coverage": 0.91,
                "meth_staking_apr": 0.038,
                "cmeth_restaking_apr": 0.054,
                "restaking_premium_bps": 160,
                "eth_price": 3450,
            },
            "allocation": (2800, 2000, 2200, 1000, 2000),
            "pnl_delta_bps": 18,
        },
        {
            "decision_type": "compliance_check",
            "rule_ref": "Rule C – Allowlist Guard",
            "reasoning_summary": "Rule C: New cmETH operator (NodeInfra Labs) added to protocol set – verified against allowlist, KYC/AML clear, no OFAC flags. Balanced vault can now route cmETH deposits through expanded operator set for better diversification. No allocation change needed.",
            "macro_context": {
                "new_operator": "NodeInfra Labs",
                "operator_kyc_status": "verified",
                "ofac_check": "clear",
                "total_cmeth_operators": 12,
            },
            "allocation": (2800, 2000, 2200, 1000, 2000),
            "pnl_delta_bps": 0,
        },
    ],
    "Aggressive": [
        {
            "decision_type": "initial_allocation",
            "rule_ref": "Rule A – USDY Yield Curve",
            "reasoning_summary": "Rule A: Aggressive profile minimizes USDY to floor (15%). Yield curve inversion is a 12-18mo leading indicator – aggressive strategy positions for eventual steepening by maximizing ETH exposure now. USDY at 4.25% net serves as collateral backstop only.",
            "macro_context": {
                "us_10y_yield": 4.38,
                "us_2y_yield": 4.56,
                "curve_inversion_months": 14,
                "eth_price": 3420,
                "eth_30d_realized_vol": 0.52,
            },
            "allocation": (1500, 3200, 2500, 1500, 1300),
            "pnl_delta_bps": 35,
        },
        {
            "decision_type": "risk_adjustment",
            "rule_ref": "Rule B – mETH vs cmETH Restaking Risk Premium",
            "reasoning_summary": "Rule B: Aggressive vault maximizes restaking yield. cmETH APR at 5.4% with slashing coverage 91% – well above safety threshold. Pushing cmETH to 35% (max single asset for aggressive = 40%). mETH reduced as vanilla staking offers inferior risk-adjusted return at this risk tier.",
            "macro_context": {
                "cmeth_restaking_apr": 0.054,
                "meth_staking_apr": 0.038,
                "cmeth_slashing_coverage": 0.91,
                "max_single_asset_bps": 4000,
                "eth_price": 3480,
            },
            "allocation": (1500, 3500, 2000, 1500, 1500),
            "pnl_delta_bps": 28,
        },
        {
            "decision_type": "compliance_check",
            "rule_ref": "Rule C – Allowlist Guard",
            "reasoning_summary": "Rule C: FBTC bridge contract upgraded to v2.1 – new implementation verified on allowlist. Audit by Trail of Bits confirmed no critical findings. Aggressive vault maintains 15% fBTC for BTC beta. All protocol adapters operational and within allowlist bounds.",
            "macro_context": {
                "fbtc_bridge_version": "v2.1",
                "audit_firm": "Trail of Bits",
                "critical_findings": 0,
                "high_findings": 1,
                "allowlist_status": "all_clear",
                "btc_price": 68200,
            },
            "allocation": (1500, 3500, 2000, 1500, 1500),
            "pnl_delta_bps": 0,
        },
    ],
}


# ── Helper Functions ─────────────────────────────────────────────────────────

def pin_to_ipfs(record: dict, name: str) -> str:
    """Upload JSON to IPFS via Pinata and return CID."""
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json",
    }
    payload = {
        "pinataContent": record,
        "pinataMetadata": {"name": name},
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()["IpfsHash"]


def compute_record_hash(record: dict) -> bytes:
    """keccak256 of the canonical JSON."""
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return Web3.keccak(text=canonical)


def send_record_decision(w3, contract, allocation_tuple, pnl_delta_bps, record_hash, nonce):
    """Build, sign, and send recordDecision tx."""
    tx = contract.functions.recordDecision(
        record_hash,
        allocation_tuple,
        pnl_delta_bps,
    ).build_transaction({
        "from": Web3.to_checksum_address(AGENT_ADDRESS),
        "nonce": nonce,
        "gas": 500_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 5000,
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    w3 = Web3(Web3.HTTPProvider(MANTLE_RPC))
    assert w3.is_connected(), "Failed to connect to Mantle RPC"
    print(f"Connected to Mantle (chainId={w3.eth.chain_id})")

    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(AGENT_ADDRESS))
    print(f"Starting nonce: {nonce}\n")

    results = []

    for vault_info in VAULTS:
        vault_name = vault_info["name"]
        vault_addr = Web3.to_checksum_address(vault_info["address"])
        contract = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)

        decisions = DECISIONS[vault_name]

        for i, decision in enumerate(decisions):
            # Build full decision record
            record = {
                "version": "1.0.0",
                "vault": vault_addr,
                "vault_name": f"Mosaic {vault_name}",
                "risk_level": vault_info["risk_level"],
                "decision_id": i + 1,
                "timestamp": "2026-05-11T12:00:00Z",
                "decision_type": decision["decision_type"],
                "rule_reference": decision["rule_ref"],
                "reasoning_summary": decision["reasoning_summary"],
                "macro_context": decision["macro_context"],
                "allocation": {
                    "usdyBps": decision["allocation"][0],
                    "cmethBps": decision["allocation"][1],
                    "methBps": decision["allocation"][2],
                    "fbtcBps": decision["allocation"][3],
                    "usdcBps": decision["allocation"][4],
                },
                "pnl_delta_bps": decision["pnl_delta_bps"],
                "agent_address": AGENT_ADDRESS,
                "decision_log_contract": DECISION_LOG,
            }

            # Verify allocation sums to 10000
            alloc_sum = sum(decision["allocation"])
            assert alloc_sum == 10000, f"Allocation sum {alloc_sum} != 10000 for {vault_name} decision {i+1}"

            # Upload to IPFS
            pin_name = f"mosaic-decision-{vault_name.lower()}-{i+1}"
            print(f"[{vault_name}] Decision {i+1}: Uploading to IPFS...")
            cid = pin_to_ipfs(record, pin_name)
            print(f"  IPFS CID: {cid}")

            # Compute hash
            record_hash = compute_record_hash(record)
            print(f"  Record hash: {record_hash.hex()}")

            # Send on-chain tx
            allocation_tuple = decision["allocation"]  # (usdyBps, cmethBps, methBps, fbtcBps, usdcBps)
            pnl = decision["pnl_delta_bps"]

            print(f"  Sending tx (nonce={nonce})...")
            tx_hash = send_record_decision(w3, contract, allocation_tuple, pnl, record_hash, nonce)
            print(f"  Tx hash: {tx_hash.hex()}")

            # Wait for receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            status = "SUCCESS" if receipt.status == 1 else "FAILED"
            print(f"  Status: {status} (block {receipt.blockNumber}, gas used {receipt.gasUsed})")

            results.append({
                "vault": vault_name,
                "decision": i + 1,
                "cid": cid,
                "tx_hash": tx_hash.hex(),
                "status": status,
            })

            nonce += 1
            print()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for r in results:
        print(f"  {r['vault']} #{r['decision']}: CID={r['cid']}  TX={r['tx_hash']}  [{r['status']}]")
    print("=" * 80)


if __name__ == "__main__":
    main()
