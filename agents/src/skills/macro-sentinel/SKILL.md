# macro-sentinel

## Description
Fetches multi-source macro data for Mantle RWA portfolio management and computes a risk score. Use when you need to assess current market conditions before making portfolio allocation decisions. Triggers on: "get macro signal", "fetch market data", "check risk score", "market conditions".

## What This Skill Does
Aggregates four data streams — Pyth Network equity prices, Chainlink yield oracles, Mantle on-chain mETH APY, and Bybit BTC funding rate — into a single MacroSignal JSON object with a 0–100 risk score (higher = more risk-on).

## Inputs
```
vault_address: string      # Which vault to query (for Mantle LSP APY)
previous_risk_score: int   # Previous cycle's risk score (for delta calculation)
```

## Output (MacroSignal)
```json
{
  "risk_score": 58,
  "equity_momentum": "neutral",
  "meth_apy": 4.2,
  "usdy_yield": 4.85,
  "btc_funding_rate": 0.0003,
  "equity_prices": {
    "TSLAx": 248.50, "NVDAx": 118.30,
    "AAPLx": 195.20, "SPYx": 542.80, "QQQx": 465.10
  },
  "timestamp": 1747012800,
  "data_freshness_ok": true
}
```

## Step-by-Step Instructions

### Step 1 — Fetch equity prices from Pyth Network
```python
import httpx, time

PYTH_ENDPOINT = "https://hermes.pyth.network/v2/updates/price/latest"
PRICE_IDS = {
    "TSLAx": "0x...",  # See references/pyth_price_ids.json for Mantle-specific IDs
    "NVDAx": "0x...",
    "AAPLx": "0x...",
    "SPYx":  "0x...",
    "QQQx":  "0x..."
}

resp = httpx.get(PYTH_ENDPOINT, params={"ids[]": list(PRICE_IDS.values())})
prices = {sym: parse_pyth_price(resp.json(), pid) for sym, pid in PRICE_IDS.items()}
```

### Step 2 — Fetch mETH APY from Mantle LSP
```python
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(os.environ["MANTLE_RPC_URL"]))
lsp = w3.eth.contract(address=MANTLE_LSP_ADDRESS, abi=LSP_ABI)
meth_apy = lsp.functions.getStakingAPY().call() / 1e18 * 100  # in percent
```

### Step 3 — Fetch USDY yield from Ondo oracle
```python
usdy_contract = w3.eth.contract(address=USDY_ORACLE_ADDRESS, abi=USDY_ABI)
usdy_yield = usdy_contract.functions.getCurrentYield().call() / 1e18 * 100
```

### Step 4 — Fetch BTC funding rate from Bybit
```python
import hmac, hashlib, time, base64

timestamp = str(int(time.time() * 1000))
sign_str  = timestamp + "GET" + "/v5/market/funding/history?category=linear&symbol=BTCUSDT&limit=1"
signature = base64.b64encode(hmac.new(os.environ["BYBIT_SECRET"].encode(), sign_str.encode(), hashlib.sha256).digest()).decode()

headers = {
    "X-BAPI-API-KEY":   os.environ["BYBIT_API_KEY"],
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-SIGN":      signature,
}
resp = httpx.get("https://api.bybit.com/v5/market/funding/history", params=..., headers=headers)
btc_funding = float(resp.json()["result"]["list"][0]["fundingRate"])
```

### Step 5 — Compute risk score
```python
def compute_risk_score(equity_prices, meth_apy, btc_funding) -> int:
    # Compute 24h equity momentum
    avg_change = mean([p["change_24h_pct"] for p in equity_prices.values()])
    equity_momentum = "bullish" if avg_change > 1.0 else "bearish" if avg_change < -1.0 else "neutral"

    score = 50  # neutral baseline
    if equity_momentum == "bullish":  score += 20
    if equity_momentum == "bearish":  score -= 20
    if meth_apy > 5.0:               score += 10
    if btc_funding >  0.02:          score += 10   # market overheating
    if btc_funding < -0.01:          score -= 15   # fear signal
    return max(0, min(100, score))
```

### Step 6 — Check data freshness
If any price timestamp is more than 60 seconds old, set `data_freshness_ok = false` and fall back to cached values from the previous cycle.

### Step 7 — Return MacroSignal
Assemble and return the MacroSignal JSON object.

## Error Handling
- If Pyth returns 4xx/5xx: use last known equity prices, mark `data_freshness_ok = false`
- If Mantle RPC times out: use last known mETH APY from in-memory cache
- If Bybit API key missing: set btc_funding_rate = 0.0 (neutral signal)
- Never throw — always return a MacroSignal, even with stale data

## References
- `references/pyth_price_ids.json` — Pyth price feed IDs for Mantle xStocks
- `references/contract_addresses.json` — Mantle LSP, USDY oracle addresses
- `references/bybit_api.md` — Bybit v5 API authentication guide
