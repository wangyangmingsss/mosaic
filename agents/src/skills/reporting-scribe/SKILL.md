# reporting-scribe

## Description
Assembles a structured DecisionRecord from all agent outputs, uploads it to IPFS, writes its keccak256 hash to the MosaicVault smart contract, and posts to the ValidationRegistry. Use at the end of every rebalance cycle. Triggers on: "write decision record", "upload to IPFS", "archive decision", "record rebalance on chain".

## What This Skill Does
Takes all outputs from a completed rebalance cycle, builds a canonical DecisionRecord JSON, stores it on IPFS via Pinata, calls MosaicVault.recordDecision() to write the hash on-chain, then posts to the ValidationRegistry for downstream consumers. Also updates the vault's ERC-8004 metadata URI.

## Inputs
```
vault_address: string
macro_signal: MacroSignal         # from macro-sentinel
previous_allocation: Allocation   # before this rebalance
target_allocation: Allocation     # after this rebalance
reasoning: str                    # from allocator
tx_hashes: list[str]              # from execution-router
risk_assessment: RiskAssessment   # from risk-guardian
trigger: str                      # "macro_signal_shift" | "time_trigger" | "manual"
pnl_delta_bps: int                # incremental PnL since last cycle
```

## Output (ScribeResult)
```json
{
  "ipfs_cid": "QmXyz...",
  "record_hash": "0xabc...",
  "tx_hash": "0xdef...",
  "validation_registry_tx": "0x123...",
  "decision_id": 47,
  "metadata_uri": "ipfs://QmXyz..."
}
```

## DecisionRecord JSON Schema
```json
{
  "schema_version": "2.0",
  "vault_address":  "0x...",
  "decision_id":    47,
  "timestamp":      1747012800,
  "trigger":        "macro_signal_shift",
  "macro_snapshot": {
    "risk_score": 58,
    "meth_apy_7d": 4.20,
    "cmeth_apy_7d": 5.85,
    "restaking_premium_bps": 165,
    "usdy_oracle_price": 1.0512,
    "usdy_apy_30d": 4.85,
    "usdy_apy_7d": 4.72,
    "btc_funding_rate": 0.0003,
    "vault_on_usdy_allowlist": true
  },
  "previous_allocation": {"usdy_bps": 3000, "meth_bps": 2500, "cmeth_bps": 1500, ...},
  "target_allocation":   {"usdy_bps": 4000, "meth_bps": 2500, "cmeth_bps": 1500, ...},
  "reasoning_summary":   "Restaking premium healthy; maintaining cmETH exposure.",
  "risk_assessment": {
    "alert_level": 0,
    "checks": {...}
  },
  "execution_txs": ["0xabc...", "0xdef..."],
  "pnl_delta_bps": 12,
  "agent_model":   "mulerun-mosaic-v2"
}
```

## Step-by-Step Instructions

### Step 1 — Assemble DecisionRecord
```python
import json, hashlib, time

record = {
    "schema_version":      "2.0",
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
    "agent_model":         "mulerun-mosaic-v2"
}
record_json = json.dumps(record, indent=2, sort_keys=True)
```

### Step 2 — Upload to IPFS via Pinata
```python
import httpx

PINATA_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

resp = httpx.post(
    PINATA_URL,
    json={
        "pinataContent": record,
        "pinataMetadata": {
            "name": f"mosaic-decision-{vault_address[:8]}-{decision_id}"
        }
    },
    headers={
        "Authorization": f"Bearer {os.environ['PINATA_JWT']}",
        "Content-Type": "application/json"
    },
    timeout=15
)

if resp.status_code == 200:
    ipfs_cid = resp.json()["IpfsHash"]
else:
    # Fallback: use SHA-256 hash of the JSON string as a deterministic CID substitute
    ipfs_cid = "sha256:" + hashlib.sha256(record_json.encode()).hexdigest()
```

### Step 3 — Compute record hash (keccak256)
```python
from eth_hash.auto import keccak

record_hash_bytes = keccak(record_json.encode())
record_hash_hex   = "0x" + record_hash_bytes.hex()
```

### Step 4 — Call MosaicVault.recordDecision()
```python
from web3 import Web3

w3     = Web3(Web3.HTTPProvider(os.environ["MANTLE_RPC_URL"]))
vault  = w3.eth.contract(address=vault_address, abi=VAULT_ABI)

alloc_tuple = (
    target_allocation["usdy_bps"],
    target_allocation["meth_bps"],
    target_allocation["cmeth_bps"],
    target_allocation["fbtc_bps"],
    target_allocation["usdc_bps"],
)

tx = vault.functions.recordDecision(
    record_hash_bytes,
    alloc_tuple,
    pnl_delta_bps
).build_transaction({
    "from":  agent_address,
    "gas":   150_000,
    "nonce": w3.eth.get_transaction_count(agent_address)
})

signed  = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction).hex()

# Wait for confirmation
receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
if receipt["status"] != 1:
    raise RuntimeError(f"recordDecision tx failed: {tx_hash}")
```

### Step 5 — Post to ValidationRegistry
```python
VALIDATION_REGISTRY = "0x..."  # see references/contract_addresses.json

registry = w3.eth.contract(address=VALIDATION_REGISTRY, abi=VALIDATION_REGISTRY_ABI)

tx_reg = registry.functions.postDecision(
    vault_address,
    decision_id,
    record_hash_bytes,
    ipfs_cid
).build_transaction({
    "from":  agent_address,
    "gas":   100_000,
    "nonce": w3.eth.get_transaction_count(agent_address)
})

signed_reg = w3.eth.account.sign_transaction(tx_reg, os.environ["AGENT_PRIVATE_KEY"])
validation_registry_tx = w3.eth.send_raw_transaction(signed_reg.raw_transaction).hex()

# Wait for confirmation
receipt_reg = w3.eth.wait_for_transaction_receipt(validation_registry_tx, timeout=60)
if receipt_reg["status"] != 1:
    print(f"[Scribe] WARNING: ValidationRegistry post failed: {validation_registry_tx}")
```

### Step 6 — Update metadata URI
```python
metadata_uri = f"ipfs://{ipfs_cid}"

tx2 = vault.functions.updateMetadataURI(metadata_uri).build_transaction({
    "from":  agent_address,
    "gas":   60_000,
    "nonce": w3.eth.get_transaction_count(agent_address)
})
signed2 = w3.eth.account.sign_transaction(tx2, os.environ["AGENT_PRIVATE_KEY"])
w3.eth.send_raw_transaction(signed2.raw_transaction)
```

### Step 7 — Return ScribeResult
Return CID, hash, tx hash, validation registry tx, decision ID, and metadata URI.

## Error Handling
- If Pinata upload fails: use fallback hash (sha256 of JSON), log warning, continue with on-chain write
- If recordDecision tx fails: retry once with +20% gas; if still fails, log error and return with `tx_hash = null`
- If ValidationRegistry post fails: log warning, continue — this is non-blocking but should be investigated
- If nonce collision: fetch fresh nonce and retry once
- Never skip the on-chain write — it is the core product promise

## References
- `references/vault_abi.json` — MosaicVault ABI
- `references/validation_registry_abi.json` — ValidationRegistry ABI
- `references/contract_addresses.json` — ValidationRegistry address
- `references/pinata_guide.md` — Pinata JWT authentication
