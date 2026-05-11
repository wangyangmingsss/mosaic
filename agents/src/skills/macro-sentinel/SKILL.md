# macro-sentinel

## Description
Fetches multi-source macro data for Mantle RWA portfolio management and computes a risk score. Use when you need to assess current market conditions before making portfolio allocation decisions. Triggers on: "get macro signal", "fetch market data", "check risk score", "market conditions".

## What This Skill Does
Aggregates data streams — USDY oracle pricing and yield data, Mantle on-chain mETH/cmETH APY, and Bybit BTC funding rate — into a single MacroSignal JSON object with a 0-100 risk score (higher = more risk-on). Computes the restaking risk premium between cmETH and mETH and checks vault USDY allowlist status.

## Inputs
```
vault_address: string      # Which vault to query (for Mantle LSP APY and allowlist check)
previous_risk_score: int   # Previous cycle's risk score (for delta calculation)
```

## Output (MacroSignal)
```json
{
  "risk_score": 58,
  "meth_apy_7d": 4.20,
  "cmeth_apy_7d": 5.85,
  "restaking_premium_bps": 165,
  "usdy_oracle_price": 1.0512,
  "usdy_apy_30d": 4.85,
  "usdy_apy_7d": 4.72,
  "btc_funding_rate": 0.0003,
  "vault_on_usdy_allowlist": true,
  "timestamp": 1747012800,
  "data_freshness_ok": true
}
```

## Step-by-Step Instructions

### Step 1 — Fetch mETH APY from Mantle LSP
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.environ["MANTLE_RPC_URL"]))
lsp = w3.eth.contract(address=MANTLE_LSP_ADDRESS, abi=LSP_ABI)
meth_apy_7d = lsp.functions.getStakingAPY().call() / 1e18 * 100  # in percent
```

### Step 2 — Fetch cmETH APY from Mantle restaking contract
```python
cmeth_contract = w3.eth.contract(address=CMETH_ADDRESS, abi=CMETH_ABI)
cmeth_apy_7d = cmeth_contract.functions.getRestakingAPY().call() / 1e18 * 100  # in percent
```

### Step 3 — Compute restaking risk premium
```python
restaking_premium_bps = int((cmeth_apy_7d - meth_apy_7d) * 100)  # APY difference in bps
```

### Step 4 — Fetch USDY oracle price and yield data
```python
usdy_oracle = w3.eth.contract(address=USDY_ORACLE_ADDRESS, abi=USDY_ABI)
usdy_oracle_price = usdy_oracle.functions.getPrice().call() / 1e18
usdy_apy_30d = usdy_oracle.functions.getTrailingAPY(30).call() / 1e18 * 100
usdy_apy_7d  = usdy_oracle.functions.getTrailingAPY(7).call() / 1e18 * 100
```

### Step 5 — Check vault USDY allowlist status
```python
usdy_token = w3.eth.contract(address=USDY_TOKEN_ADDRESS, abi=USDY_TOKEN_ABI)
vault_on_usdy_allowlist = usdy_token.functions.isAllowed(vault_address).call()
```

### Step 6 — Fetch BTC funding rate from Bybit
```python
import hmac, hashlib, time

BYBIT_API_KEY = "SxjEUjNshid1ccJsbi"
BYBIT_SECRET  = "DNxladcKZ4E5N4K0zMj1ofVWQV4Iirtew4r7"

timestamp = str(int(time.time() * 1000))
recv_window = "5000"
params = "category=linear&symbol=BTCUSDT&limit=1"
sign_str = timestamp + BYBIT_API_KEY + recv_window + params
signature = hmac.new(BYBIT_SECRET.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

headers = {
    "X-BAPI-API-KEY":     BYBIT_API_KEY,
    "X-BAPI-TIMESTAMP":   timestamp,
    "X-BAPI-RECV-WINDOW": recv_window,
    "X-BAPI-SIGN":        signature,
}
resp = httpx.get(
    "https://api.bybit.com/v5/market/funding/history",
    params={"category": "linear", "symbol": "BTCUSDT", "limit": "1"},
    headers=headers
)
btc_funding = float(resp.json()["result"]["list"][0]["fundingRate"])
```

### Step 7 — Compute risk score
```python
def compute_risk_score(meth_apy_7d, cmeth_apy_7d, restaking_premium_bps, btc_funding) -> int:
    score = 50  # neutral baseline

    # Staking yield signal
    if meth_apy_7d > 5.0:               score += 10
    if cmeth_apy_7d > 7.0:              score += 5

    # Restaking premium health
    if restaking_premium_bps > 150:      score += 5   # healthy premium
    if restaking_premium_bps < 50:       score -= 10  # risk not compensated

    # BTC funding rate signal
    if btc_funding > 0.02:               score += 10  # market overheating
    if btc_funding < -0.01:              score -= 15  # fear signal

    return max(0, min(100, score))
```

### Step 8 — Check data freshness
If any on-chain call timestamp is more than 60 seconds old, set `data_freshness_ok = false` and fall back to cached values from the previous cycle.

### Step 9 — Return MacroSignal
Assemble and return the MacroSignal JSON object.

## Error Handling
- If Mantle RPC times out: use last known mETH/cmETH APY from in-memory cache
- If USDY oracle returns stale price: use last known values, mark `data_freshness_ok = false`
- If Bybit API key fails: set btc_funding_rate = 0.0 (neutral signal)
- Never throw — always return a MacroSignal, even with stale data

## References
- `references/contract_addresses.json` — Mantle LSP, cmETH, USDY oracle, USDY token addresses
- `references/bybit_api.md` — Bybit v5 API authentication guide
- `references/cmeth_abi.json` — cmETH restaking contract ABI
