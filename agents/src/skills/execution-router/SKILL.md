# execution-router

## Description
Executes portfolio rebalancing trades on Mantle by routing each asset delta to the optimal protocol. Use after the allocator has produced a target allocation. Triggers on: "execute rebalance", "route trades", "execute allocation", "swap assets on Mantle".

## What This Skill Does
Computes the delta between current and target allocations, then routes each non-dust trade to the best available liquidity source on Mantle:
- xStocks → Fluxion Atomic RFQ (during market hours) or Fluxion AMM (after hours)
- USDY → Merchant Moe USDY/USDC pool
- mETH → Mantle LSP stake/unstake
- fBTC → Function fBTC vault deposit/withdraw
- USDC → held in vault

## Inputs
```
vault_address: string          # MosaicVault contract address
current_allocation: Allocation # Live allocation in basis points
target_allocation: Allocation  # Output from allocator skill
vault_tvl_usd: float           # Total vault value in USD (for size calculation)
```

## Output (ExecutionResult)
```json
{
  "tx_hashes": ["0xabc...", "0xdef..."],
  "trades_executed": 3,
  "trades_skipped": 1,
  "skip_reasons": ["usdc delta 30bps < 50bps dust threshold"],
  "total_gas_used": 284000,
  "execution_ok": true
}
```

## Step-by-Step Instructions

### Step 1 — Compute deltas
```python
DUST_THRESHOLD_BPS = 50  # Skip trades smaller than 0.5% of TVL

def compute_deltas(current: dict, target: dict) -> dict:
    return {
        "usdy":    target["usdy_bps"]    - current["usdy_bps"],
        "xstocks": target["xstocks_bps"] - current["xstocks_bps"],
        "meth":    target["meth_bps"]    - current["meth_bps"],
        "fbtc":    target["fbtc_bps"]    - current["fbtc_bps"],
        "usdc":    target["usdc_bps"]    - current["usdc_bps"],
    }
```

### Step 2 — Filter dust trades
```python
executable = {k: v for k, v in deltas.items() if abs(v) >= DUST_THRESHOLD_BPS}
skipped    = {k: v for k, v in deltas.items() if abs(v) < DUST_THRESHOLD_BPS}
```

### Step 3 — Pre-execution simulation (CRITICAL)
Before broadcasting any transaction, simulate with eth_call:
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider(os.environ["MANTLE_RPC_URL"]))

def simulate_tx(tx: dict) -> bool:
    try:
        w3.eth.call(tx)
        return True
    except Exception as e:
        print(f"[ExecutionRouter] Simulation failed: {e}")
        return False
```
Skip any trade whose simulation fails.

### Step 4a — Route xStocks trades via Fluxion
```python
import httpx, time

FLUXION_RFQ_URL = "https://api.fluxion.io/v1/rfq/quote"

def execute_xstocks(direction: str, amount_usd: float) -> str:
    """direction: 'buy' or 'sell'. Returns tx hash."""
    # Try Atomic RFQ first (lower slippage)
    quote_resp = httpx.post(FLUXION_RFQ_URL, json={
        "tokenIn":    "USDC" if direction == "buy" else "SPYx",
        "tokenOut":   "SPYx" if direction == "buy" else "USDC",
        "amountIn":   str(int(amount_usd * 1e6)),  # USDC has 6 decimals
        "slippage":   "30",   # 30 bps = 0.3%
        "chainId":    "5000"  # Mantle mainnet
    })
    quote = quote_resp.json()

    if quote["source"] == "rfq" and float(quote["priceImpact"]) < 0.005:
        # Execute via RFQ
        tx_hash = send_signed_tx(quote["calldata"], quote["to"])
        return tx_hash
    else:
        # Fallback to AMM
        return execute_xstocks_amm(direction, amount_usd)
```

### Step 4b — Route USDY trades via Merchant Moe
```python
MERCHANT_MOE_ROUTER = "0x..."  # Mantle mainnet address — see references/contract_addresses.json

def execute_usdy(direction: str, amount_usdc: float) -> str:
    """direction: 'buy' (USDC→USDY) or 'sell' (USDY→USDC)"""
    # Use MerchantMoe's LBRouter for USDY/USDC pair
    # ABI and address in references/merchant_moe_abi.json
    router = w3.eth.contract(address=MERCHANT_MOE_ROUTER, abi=LB_ROUTER_ABI)

    if direction == "buy":
        tx = router.functions.swapExactTokensForTokens(
            int(amount_usdc * 1e6),
            int(amount_usdc * 1e6 * 0.997),  # 0.3% slippage
            [[USDC_ADDRESS, USDY_ADDRESS, False, MERCHANT_MOE_FACTORY]],
            vault_address,
            int(time.time()) + 300
        ).build_transaction({"from": agent_address, "gas": 150_000})
    else:
        # reverse path
        ...

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 4c — Route mETH trades via Mantle LSP
```python
MANTLE_LSP = "0xe3cBd06D7dadB3F4e6557bAb7EdD924CD1489E8f"  # Mantle LSP

def execute_meth(direction: str, amount_eth: float) -> str:
    lsp = w3.eth.contract(address=MANTLE_LSP, abi=LSP_ABI)
    if direction == "stake":
        tx = lsp.functions.stake(int(amount_eth * 1e18)).build_transaction({
            "from": agent_address,
            "value": int(amount_eth * 1e18),
            "gas": 200_000
        })
    else:
        tx = lsp.functions.unstake(int(amount_eth * 1e18)).build_transaction({
            "from": agent_address, "gas": 200_000
        })
    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 4d — Route fBTC trades via Function vault
```python
FUNCTION_FBTC_VAULT = "0x..."  # see references/contract_addresses.json

def execute_fbtc(direction: str, amount_btc: float) -> str:
    vault_contract = w3.eth.contract(address=FUNCTION_FBTC_VAULT, abi=FBTC_VAULT_ABI)
    if direction == "deposit":
        tx = vault_contract.functions.deposit(int(amount_btc * 1e8)).build_transaction(...)
    else:
        tx = vault_contract.functions.withdraw(int(amount_btc * 1e8)).build_transaction(...)
    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 5 — Collect results
Wait for receipt confirmation (1 block) for each tx. Record gas used. Return ExecutionResult.

## Error Handling
- If simulation fails: skip trade, add to `skip_reasons`, continue with others
- If tx broadcast fails (nonce error, gas): retry once with bumped gas (+20%)
- If Fluxion RFQ returns empty: fallback to AMM immediately, do not retry RFQ
- Partial execution (some trades fail): set `execution_ok = false`, still return hashes for successful ones
- Never retry a failed tx more than once — risk of double execution

## References
- `references/contract_addresses.json` — all Mantle protocol addresses
- `references/merchant_moe_abi.json` — Merchant Moe LBRouter ABI
- `references/fluxion_api.md` — Fluxion RFQ and AMM API documentation
- `references/mantle_lsp_abi.json` — Mantle LSP stake/unstake ABI
