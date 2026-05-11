"""
write_record.py — Reporting Scribe skill implementation
Uploads decision records to IPFS, writes keccak256 hash to MosaicVault contract.
"""
import asyncio
import hashlib
import json
import os
import time
from dataclasses import asdict
from typing import Optional

import httpx
from eth_account import Account
from eth_hash.auto import keccak
from web3 import Web3

MANTLE_RPC_URL = os.environ.get("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")
PINATA_JWT     = os.environ.get("PINATA_JWT", "")
PINATA_URL     = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

# MosaicVault ABI (minimal subset)
VAULT_ABI_RECORD = [
    {
        "name": "recordDecision",
        "type": "function",
        "inputs": [
            {"name": "recordHash",  "type": "bytes32"},
            {"name": "newAlloc",    "type": "tuple", "components": [
                {"name": "usdyBps",    "type": "uint16"},
                {"name": "xstocksBps", "type": "uint16"},
                {"name": "methBps",    "type": "uint16"},
                {"name": "fbtcBps",    "type": "uint16"},
                {"name": "usdcBps",    "type": "uint16"},
            ]},
            {"name": "pnlDeltaBps", "type": "int256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "updateMetadataURI",
        "type": "function",
        "inputs": [{"name": "uri", "type": "string"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "name": "agentIdentity",
        "type": "function",
        "inputs": [],
        "outputs": [
            {"name": "modelDeclaration",    "type": "string"},
            {"name": "createdAt",           "type": "uint256"},
            {"name": "totalDecisions",      "type": "uint256"},
            {"name": "successfulRebalances","type": "uint256"},
            {"name": "cumulativePnLBps",    "type": "int256"},
            {"name": "metadataURI",         "type": "string"},
        ],
        "stateMutability": "view",
    },
]


async def upload_to_ipfs(record: dict, name: str) -> str:
    """
    Upload DecisionRecord JSON to Pinata IPFS.
    Falls back to sha256 hash ID on failure (format: sha256:HEXHASH).
    """
    if not PINATA_JWT:
        print("[Scribe] PINATA_JWT not set. Using local hash fallback.")
        record_json = json.dumps(record, sort_keys=True)
        return "sha256:" + hashlib.sha256(record_json.encode()).hexdigest()

    payload = {
        "pinataContent":  record,
        "pinataMetadata": {"name": name},
        "pinataOptions":  {"cidVersion": 1},
    }
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type":  "application/json",
    }

    for attempt in range(2):  # retry once max
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.post(PINATA_URL, json=payload, headers=headers)
                resp.raise_for_status()
                cid = resp.json()["IpfsHash"]
                print(f"[Scribe] IPFS upload OK: {cid}")
                return cid
        except Exception as e:
            print(f"[Scribe] IPFS upload attempt {attempt+1} failed: {e}")
            if attempt == 0:
                await asyncio.sleep(3)

    # Both attempts failed, use sha256 fallback
    record_json = json.dumps(record, sort_keys=True)
    fallback = "sha256:" + hashlib.sha256(record_json.encode()).hexdigest()
    print(f"[Scribe] Using fallback: {fallback}")
    return fallback


def compute_record_hash(record: dict) -> bytes:
    """
    Compute keccak256 hash of DecisionRecord.
    Returns bytes32 for writing to DecisionLog contract.
    """
    record_json = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return keccak(record_json.encode("utf-8"))


async def write_record_onchain(
    vault_address:      str,
    record_hash_bytes:  bytes,
    target_allocation:  dict,
    pnl_delta_bps:      int,
    agent_private_key:  str,
) -> Optional[str]:
    """
    Call MosaicVault.recordDecision() to write hash on-chain.
    Returns tx_hash string on success, None on failure.
    """
    w3      = Web3(Web3.HTTPProvider(MANTLE_RPC_URL))
    account = Account.from_key(agent_private_key)
    vault   = w3.eth.contract(address=vault_address, abi=VAULT_ABI_RECORD)

    alloc_tuple = (
        target_allocation["usdy_bps"],
        target_allocation["xstocks_bps"],
        target_allocation["meth_bps"],
        target_allocation["fbtc_bps"],
        target_allocation["usdc_bps"],
    )

    for attempt in range(2):
        try:
            nonce = w3.eth.get_transaction_count(account.address)
            gas_price = w3.eth.gas_price

            tx = vault.functions.recordDecision(
                record_hash_bytes,
                alloc_tuple,
                pnl_delta_bps,
            ).build_transaction({
                "from":     account.address,
                "nonce":    nonce,
                "gas":      180_000,
                "gasPrice": int(gas_price * (1.2 if attempt > 0 else 1.0)),
                "chainId":  w3.eth.chain_id,
            })

            signed  = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)

            if receipt["status"] == 1:
                print(f"[Scribe] recordDecision OK: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                print(f"[Scribe] recordDecision reverted: {tx_hash.hex()}")

        except Exception as e:
            print(f"[Scribe] onchain write attempt {attempt+1} failed: {e}")
            if attempt == 0:
                await asyncio.sleep(5)

    return None


async def update_metadata_uri(
    vault_address:     str,
    metadata_uri:      str,
    agent_private_key: str,
) -> None:
    """Update ERC-8004 metadata URI (non-critical, failure does not affect main flow)"""
    try:
        w3      = Web3(Web3.HTTPProvider(MANTLE_RPC_URL))
        account = Account.from_key(agent_private_key)
        vault   = w3.eth.contract(address=vault_address, abi=VAULT_ABI_RECORD)

        nonce = w3.eth.get_transaction_count(account.address)
        tx = vault.functions.updateMetadataURI(metadata_uri).build_transaction({
            "from":    account.address,
            "nonce":   nonce,
            "gas":     80_000,
            "chainId": w3.eth.chain_id,
        })
        signed = account.sign_transaction(tx)
        w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"[Scribe] updateMetadataURI submitted: {metadata_uri}")
    except Exception as e:
        print(f"[Scribe] updateMetadataURI failed (non-critical): {e}")


async def write_record(
    vault_address:       str,
    decision_id:         int,
    macro_signal:        dict,
    previous_allocation: dict,
    target_allocation:   dict,
    reasoning:           str,
    tx_hashes:           list,
    risk_assessment:     dict,
    trigger:             str,
    pnl_delta_bps:       int,
) -> dict:
    """
    Reporting Scribe main function.
    1. Assemble DecisionRecord
    2. Upload to IPFS
    3. Write on-chain
    4. Update metadata URI
    """
    agent_private_key = os.environ["AGENT_PRIVATE_KEY"]

    # -- Step 1: Assemble DecisionRecord ---------------------------------------
    record = {
        "schema_version":      "1.0",
        "vault_address":       vault_address,
        "decision_id":         decision_id,
        "timestamp":           int(time.time()),
        "trigger":             trigger,
        "macro_snapshot":      macro_signal,
        "previous_allocation": previous_allocation,
        "target_allocation":   target_allocation,
        "reasoning_summary":   reasoning,
        "risk_assessment":     risk_assessment,
        "execution_txs":       tx_hashes,
        "pnl_delta_bps":       pnl_delta_bps,
        "agent_model":         "mulerun-mosaic-v1",
    }

    # -- Step 2: IPFS upload ---------------------------------------------------
    ipfs_name = f"mosaic-{vault_address[:8]}-decision-{decision_id}"
    ipfs_cid  = await upload_to_ipfs(record, ipfs_name)

    # -- Step 3: Compute keccak256 hash ----------------------------------------
    record_hash_bytes = compute_record_hash(record)
    record_hash_hex   = "0x" + record_hash_bytes.hex()

    # -- Step 4: Write on-chain ------------------------------------------------
    chain_tx = await write_record_onchain(
        vault_address,
        record_hash_bytes,
        target_allocation,
        pnl_delta_bps,
        agent_private_key,
    )

    # -- Step 5: Update ERC-8004 metadata URI ----------------------------------
    metadata_uri = f"ipfs://{ipfs_cid}"
    await update_metadata_uri(vault_address, metadata_uri, agent_private_key)

    return {
        "ipfs_cid":     ipfs_cid,
        "record_hash":  record_hash_hex,
        "tx_hash":      chain_tx,
        "decision_id":  decision_id,
        "metadata_uri": metadata_uri,
    }
