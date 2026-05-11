# allocator

## Description
Computes optimal RWA portfolio allocation given a MacroSignal and user RiskProfile. Use when you have fresh macro data and need to determine target asset weights. Triggers on: "compute allocation", "rebalance portfolio", "calculate target weights", "portfolio optimisation".

## What This Skill Does
Implements a simplified Black-Litterman framework where the LLM provides the "views" (subjective market outlook) that modify the equilibrium allocation defined by the user's RiskProfile. Returns a validated Allocation (5 weights summing to exactly 10000 bps) and a one-sentence reasoning summary.

## Inputs
```
macro_signal: MacroSignal     # Output from macro-sentinel skill
risk_profile: RiskProfile     # User's vault configuration
current_allocation: Allocation # Current live allocation
```

## Output (AllocationDecision)
```json
{
  "allocation": {
    "usdy_bps":    4000,
    "xstocks_bps": 2500,
    "meth_bps":    2000,
    "fbtc_bps":    1000,
    "usdc_bps":     500
  },
  "reasoning": "Equity momentum weakening; rotating 10pp from xStocks to USDY for defensive yield.",
  "confidence": 0.78,
  "triggered_by": "macro_signal_shift"
}
```

## Step-by-Step Instructions

### Step 1 — Load base allocation for risk level
```python
BASE_ALLOCATIONS = {
    1: {"usdy_bps": 5000, "xstocks_bps": 1500, "meth_bps": 2000, "fbtc_bps":  500, "usdc_bps": 1000},
    2: {"usdy_bps": 3000, "xstocks_bps": 3000, "meth_bps": 2500, "fbtc_bps": 1000, "usdc_bps":  500},
    3: {"usdy_bps": 1500, "xstocks_bps": 4500, "meth_bps": 2500, "fbtc_bps": 1500, "usdc_bps":    0},
}
base = BASE_ALLOCATIONS[risk_profile.risk_level]
```

### Step 2 — Build the LLM prompt
```python
prompt = f"""You are a quantitative portfolio manager for a RWA portfolio on Mantle blockchain.

Current macro environment:
- Risk score: {macro.risk_score}/100 (higher = more risk-on)
- Equity momentum: {macro.equity_momentum}
- mETH staking APY: {macro.meth_apy:.2f}%
- USDY yield: {macro.usdy_yield:.2f}%
- BTC funding rate: {macro.btc_funding_rate:.4f}

Current allocation (basis points):
{json.dumps(current_allocation, indent=2)}

Base allocation for risk_level={risk_profile.risk_level}:
{json.dumps(base, indent=2)}

User constraints:
- max single asset: {risk_profile.max_single_asset_bps} bps
- max drawdown: {risk_profile.max_drawdown_bps} bps

Available assets and their characteristics:
- USDY: tokenised US Treasury yield (~{macro.usdy_yield:.2f}% APY), very low volatility, defensive
- xStocks: tokenised equities (TSLAx, NVDAx, AAPLx, SPYx), growth-oriented, correlated to US equity markets
- mETH: ETH liquid staking ({macro.meth_apy:.2f}% APY), moderate volatility, crypto-native yield
- fBTC: BTC restaking via Babylon, highest risk/return, Bitcoin-correlated
- USDC: cash reserve, 0 yield but immediate liquidity for rebalancing

Your task: Determine the optimal target allocation for the NEXT cycle.

Rules:
1. Weights must sum to EXACTLY 10000 basis points
2. No single asset may exceed {risk_profile.max_single_asset_bps} bps
3. Conservative portfolio (risk_level=1): xstocks_bps ≤ 2500
4. Changes from current allocation should be proportional to signal strength

Respond with ONLY valid JSON (no markdown, no explanation outside the JSON):
{{
  "usdy_bps": <int>,
  "xstocks_bps": <int>,
  "meth_bps": <int>,
  "fbtc_bps": <int>,
  "usdc_bps": <int>,
  "reasoning": "<one sentence explaining the key change and why>",
  "confidence": <float 0.0-1.0>
}}"""
```

### Step 3 — Call LLM and parse response
```python
response = await llm_client.complete(
    model="claude-sonnet-4-20250514",
    prompt=prompt,
    max_tokens=300,
    temperature=0.1   # low temperature for consistent numerical output
)

# Strip any accidental markdown fences
clean = response.strip().removeprefix("```json").removesuffix("```").strip()
parsed = json.loads(clean)
```

### Step 4 — Validate allocation
```python
def validate(parsed: dict, risk_profile: RiskProfile) -> Allocation:
    total = sum([parsed["usdy_bps"], parsed["xstocks_bps"],
                 parsed["meth_bps"], parsed["fbtc_bps"], parsed["usdc_bps"]])
    if total != 10_000:
        raise ValueError(f"Allocation sums to {total}, expected 10000")

    max_weight = max(parsed["usdy_bps"], parsed["xstocks_bps"],
                     parsed["meth_bps"], parsed["fbtc_bps"])
    if max_weight > risk_profile.max_single_asset_bps:
        raise ValueError(f"Single asset exceeds limit: {max_weight}")

    return Allocation(**{k: parsed[k] for k in ["usdy_bps","xstocks_bps","meth_bps","fbtc_bps","usdc_bps"]})
```

### Step 5 — Retry on validation failure (max 3 attempts)
If validation fails, re-invoke the LLM with the error appended to the prompt. After 3 failed attempts, fall back to the base allocation for the user's risk level.

### Step 6 — Return AllocationDecision
Return the validated Allocation plus reasoning and confidence.

## Error Handling
- If LLM returns invalid JSON: strip response and retry (max 3 times)
- If validation fails after 3 retries: use base allocation, set confidence = 0.0, reasoning = "fallback to base allocation due to LLM error"
- Always return an AllocationDecision; never throw

## References
- `references/risk_profiles.json` — base allocations and constraint tables
- `references/asset_metadata.json` — asset descriptions and typical APY ranges
