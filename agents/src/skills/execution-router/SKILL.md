# execution-router

## Description
Executes portfolio rebalancing trades on Mantle by routing each asset delta to the optimal protocol. Use after the allocator has produced a target allocation. Triggers on: "execute rebalance", "route trades", "execute allocation", "swap assets on Mantle".

## What This Skill Does
Computes the delta between current and target allocations, then routes each non-dust trade through Merchant Moe LB v2.2 adapters on L2:
- USDY  -> Merchant Moe LB v2.2 USDY/USDC pool
- mETH  -> Merchant Moe LB v2.2 mETH/USDC pool (DEX, NOT Mantle LSP stake/unstake on L1)
- cmETH -> Merchant Moe LB v2.2 cmETH/mETH pool (DEX, NOT Mantle LSP stake/unstake on L1)
- fBTC  -> Merchant Moe LB v2.2 fBTC/USDC pool
- USDC  -> held in vault

All swaps stay on Mantle L2 and route through Merchant Moe Liquidity Book v2.2 adapters. mETH and cmETH are traded on the DEX — we do NOT use Mantle LSP stake/unstake operations on L1.

## Adapter Contracts (Mantle Mainnet)
| Asset Pair     | Merchant Moe LB v2.2 Pool | Adapter |
|----------------|---------------------------|---------|
| USDY/USDC      | `0x...` (see references)  | LBRouter v2.2 |
| mETH/USDC      | `0x...` (see references)  | LBRouter v2.2 |
| cmETH/mETH     | `0x...` (see references)  | LBRouter v2.2 |
| fBTC/USDC      | `0x...` (see references)  | LBRouter v2.2 |

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
        "usdy":  target["usdy_bps"]  - current["usdy_bps"],
        "meth":  target["meth_bps"]  - current["meth_bps"],
        "cmeth": target["cmeth_bps"] - current["cmeth_bps"],
        "fbtc":  target["fbtc_bps"]  - current["fbtc_bps"],
        "usdc":  target["usdc_bps"]  - current["usdc_bps"],
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

### Step 4a — Route USDY trades via Merchant Moe LB v2.2
```python
MERCHANT_MOE_LB_ROUTER = "0x..."  # LBRouter v2.2 — see references/contract_addresses.json

def execute_usdy(direction: str, amount_usdc: float) -> str:
    """direction: 'buy' (USDC->USDY) or 'sell' (USDY->USDC)"""
    router = w3.eth.contract(address=MERCHANT_MOE_LB_ROUTER, abi=LB_ROUTER_V22_ABI)

    if direction == "buy":
        path = build_lb_path(USDC_ADDRESS, USDY_ADDRESS, bin_step=1)
        tx = router.functions.swapExactTokensForTokens(
            int(amount_usdc * 1e6),
            int(amount_usdc * 1e6 * 0.997),  # 0.3% slippage
            path,
            vault_address,
            int(time.time()) + 300
        ).build_transaction({"from": agent_address, "gas": 200_000})
    else:
        path = build_lb_path(USDY_ADDRESS, USDC_ADDRESS, bin_step=1)
        tx = router.functions.swapExactTokensForTokens(
            int(amount_usdc * 1e18),
            int(amount_usdc * 1e6 * 0.997),
            path,
            vault_address,
            int(time.time()) + 300
        ).build_transaction({"from": agent_address, "gas": 200_000})

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 4b — Route mETH trades via Merchant Moe LB v2.2 (DEX only)
```python
def execute_meth(direction: str, amount_usd: float) -> str:
    """Trade mETH on DEX via Merchant Moe LB v2.2 pool. NOT via Mantle LSP stake/unstake."""
    router = w3.eth.contract(address=MERCHANT_MOE_LB_ROUTER, abi=LB_ROUTER_V22_ABI)

    if direction == "buy":
        path = build_lb_path(USDC_ADDRESS, METH_ADDRESS, bin_step=15)
        amount_in = int(amount_usd * 1e6)
    else:
        path = build_lb_path(METH_ADDRESS, USDC_ADDRESS, bin_step=15)
        amount_in = int(amount_usd / meth_price * 1e18)

    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        0,  # min out computed off-chain with 0.5% slippage
        path,
        vault_address,
        int(time.time()) + 300
    ).build_transaction({"from": agent_address, "gas": 250_000})

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 4c — Route cmETH trades via Merchant Moe LB v2.2 (DEX only)
```python
def execute_cmeth(direction: str, amount_usd: float) -> str:
    """Trade cmETH on DEX via cmETH/mETH pool. NOT via Mantle LSP stake/unstake."""
    router = w3.eth.contract(address=MERCHANT_MOE_LB_ROUTER, abi=LB_ROUTER_V22_ABI)

    if direction == "buy":
        # Route: USDC -> mETH -> cmETH (two-hop via LB)
        path = build_lb_multi_path([USDC_ADDRESS, METH_ADDRESS, CMETH_ADDRESS], bin_steps=[15, 5])
        amount_in = int(amount_usd * 1e6)
    else:
        # Route: cmETH -> mETH -> USDC
        path = build_lb_multi_path([CMETH_ADDRESS, METH_ADDRESS, USDC_ADDRESS], bin_steps=[5, 15])
        amount_in = int(amount_usd / cmeth_price * 1e18)

    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        0,  # min out computed off-chain with 0.5% slippage
        path,
        vault_address,
        int(time.time()) + 300
    ).build_transaction({"from": agent_address, "gas": 350_000})

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 4d — Route fBTC trades via Merchant Moe LB v2.2
```python
def execute_fbtc(direction: str, amount_usd: float) -> str:
    """Trade fBTC on DEX via Merchant Moe LB v2.2 fBTC/USDC pool."""
    router = w3.eth.contract(address=MERCHANT_MOE_LB_ROUTER, abi=LB_ROUTER_V22_ABI)

    if direction == "buy":
        path = build_lb_path(USDC_ADDRESS, FBTC_ADDRESS, bin_step=25)
        amount_in = int(amount_usd * 1e6)
    else:
        path = build_lb_path(FBTC_ADDRESS, USDC_ADDRESS, bin_step=25)
        amount_in = int(amount_usd / btc_price * 1e8)

    tx = router.functions.swapExactTokensForTokens(
        amount_in,
        0,  # min out computed off-chain with 0.5% slippage
        path,
        vault_address,
        int(time.time()) + 300
    ).build_transaction({"from": agent_address, "gas": 250_000})

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    return w3.eth.send_raw_transaction(signed.raw_transaction).hex()
```

### Step 5 — Collect results
Wait for receipt confirmation (1 block) for each tx. Record gas used. Return ExecutionResult.

## Error Handling
- If simulation fails: skip trade, add to `skip_reasons`, continue with others
- If tx broadcast fails (nonce error, gas): retry once with bumped gas (+20%)
- If LB pool has insufficient liquidity: skip trade, log reason, set `execution_ok = false`
- Partial execution (some trades fail): set `execution_ok = false`, still return hashes for successful ones
- Never retry a failed tx more than once — risk of double execution

## References
- `references/contract_addresses.json` — all Mantle protocol addresses and LB pool addresses
- `references/merchant_moe_lb_v22_abi.json` — Merchant Moe LBRouter v2.2 ABI
- `references/lb_path_helper.md` — LB path encoding and bin step configuration
