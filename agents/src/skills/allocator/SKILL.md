# allocator

## Description
Computes optimal RWA portfolio allocation given a MacroSignal and user RiskProfile. Use when you have fresh macro data and need to determine target asset weights. Triggers on: "compute allocation", "rebalance portfolio", "calculate target weights", "portfolio optimisation".

## What This Skill Does
Implements a rule-based allocation framework augmented by LLM reasoning (DeepSeek V4) where three deterministic rules constrain the output before the model provides fine-grained weight adjustments. Returns a validated Allocation (5 weights summing to exactly 10000 bps) and a one-sentence reasoning summary.

## Asset Buckets (v2)
| # | Asset  | Ticker | Description |
|---|--------|--------|-------------|
| 1 | USDY   | USDY   | Tokenised US Treasury yield, defensive, low vol |
| 2 | mETH   | mETH   | ETH liquid staking token on Mantle |
| 3 | cmETH  | cmETH  | mETH restaked into Eigenlayer via Mantle, higher yield + restaking risk |
| 4 | fBTC   | fBTC   | BTC restaking via Function/Babylon, Bitcoin-correlated |
| 5 | USDC   | USDC   | Cash reserve, 0 yield, immediate liquidity |

## Allocation Rules

### Rule A — USDY Yield Curve
When USDY 30-day trailing APY drops below the 7-day APY by more than 15 bps, the yield curve is inverting. Action: cap USDY weight at 3000 bps and redistribute excess equally to mETH and cmETH.

| Condition | Threshold | Action |
|-----------|-----------|--------|
| `usdy_apy_30d - usdy_apy_7d < -15 bps` | -15 bps | Cap USDY at 3000 bps |
| `usdy_apy_30d - usdy_apy_7d >= -15 bps` | N/A | No cap applied |

### Rule B — mETH vs cmETH Restaking Risk Premium
The restaking premium is defined as `cmeth_apy_7d - meth_apy_7d`. When the premium is too narrow, the additional smart-contract risk of cmETH is not compensated.

| Condition | Threshold | Action |
|-----------|-----------|--------|
| `restaking_premium < 50 bps` | 50 bps | Set cmETH weight to 0; reallocate to mETH |
| `restaking_premium >= 50 bps AND < 150 bps` | 50–150 bps | cmETH capped at mETH weight (1:1 max) |
| `restaking_premium >= 150 bps` | 150 bps | No constraint (LLM decides freely) |

### Rule C — Allowlist Guard
If `vault_on_usdy_allowlist == false`, USDY weight MUST be 0 and its share is redistributed to USDC.

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
    "usdy_bps":   4000,
    "meth_bps":   2500,
    "cmeth_bps":  1500,
    "fbtc_bps":   1000,
    "usdc_bps":   1000
  },
  "reasoning": "Restaking premium healthy at 180bps; shifting weight from USDC to cmETH for yield pickup.",
  "confidence": 0.82,
  "triggered_by": "macro_signal_shift"
}
```

## Step-by-Step Instructions

### Step 1 — Load base allocation for risk level
```python
BASE_ALLOCATIONS = {
    1: {"usdy_bps": 5000, "meth_bps": 2000, "cmeth_bps": 1000, "fbtc_bps":  500, "usdc_bps": 1500},
    2: {"usdy_bps": 3500, "meth_bps": 2500, "cmeth_bps": 1500, "fbtc_bps": 1000, "usdc_bps": 1500},
    3: {"usdy_bps": 2000, "meth_bps": 3000, "cmeth_bps": 2500, "fbtc_bps": 1500, "usdc_bps": 1000},
}
base = BASE_ALLOCATIONS[risk_profile.risk_level]
```

### Step 2 — Apply deterministic rules (A, B, C)
```python
def apply_rules(base: dict, macro: MacroSignal) -> dict:
    alloc = dict(base)

    # Rule C — Allowlist Guard (apply first, highest priority)
    if not macro.vault_on_usdy_allowlist:
        alloc["usdc_bps"] += alloc["usdy_bps"]
        alloc["usdy_bps"] = 0

    # Rule A — USDY Yield Curve inversion
    yield_spread = macro.usdy_apy_30d - macro.usdy_apy_7d  # in bps
    if yield_spread < -15 and alloc["usdy_bps"] > 3000:
        excess = alloc["usdy_bps"] - 3000
        alloc["usdy_bps"] = 3000
        alloc["meth_bps"]  += excess // 2
        alloc["cmeth_bps"] += excess - excess // 2

    # Rule B — Restaking Risk Premium
    restaking_premium = macro.restaking_premium_bps
    if restaking_premium < 50:
        alloc["meth_bps"] += alloc["cmeth_bps"]
        alloc["cmeth_bps"] = 0
    elif restaking_premium < 150:
        if alloc["cmeth_bps"] > alloc["meth_bps"]:
            overflow = alloc["cmeth_bps"] - alloc["meth_bps"]
            alloc["cmeth_bps"] = alloc["meth_bps"]
            alloc["meth_bps"] += overflow

    return alloc
```

### Step 3 — Build the LLM prompt
```python
prompt = f"""You are a quantitative portfolio manager for a RWA portfolio on Mantle blockchain.

Current macro environment:
- Risk score: {macro.risk_score}/100 (higher = more risk-on)
- mETH staking APY (7d): {macro.meth_apy_7d:.2f}%
- cmETH restaking APY (7d): {macro.cmeth_apy_7d:.2f}%
- Restaking premium: {macro.restaking_premium_bps} bps
- USDY yield (30d): {macro.usdy_apy_30d:.2f}%
- USDY yield (7d): {macro.usdy_apy_7d:.2f}%
- USDY oracle price: ${macro.usdy_oracle_price:.4f}
- BTC funding rate: {macro.btc_funding_rate:.4f}
- Vault on USDY allowlist: {macro.vault_on_usdy_allowlist}

Rule-constrained base allocation (after Rules A/B/C):
{json.dumps(rule_adjusted, indent=2)}

Current live allocation:
{json.dumps(current_allocation, indent=2)}

User constraints:
- max single asset: {risk_profile.max_single_asset_bps} bps
- max drawdown: {risk_profile.max_drawdown_bps} bps

Available assets:
- USDY: tokenised US Treasury yield (~{macro.usdy_apy_7d:.2f}% APY), very low volatility, defensive
- mETH: ETH liquid staking ({macro.meth_apy_7d:.2f}% APY), moderate volatility, crypto-native yield
- cmETH: mETH restaked via Eigenlayer ({macro.cmeth_apy_7d:.2f}% APY), higher yield but added restaking/slashing risk
- fBTC: BTC restaking via Babylon, highest risk/return, Bitcoin-correlated
- USDC: cash reserve, 0 yield but immediate liquidity for rebalancing

Your task: Fine-tune the rule-constrained allocation for the NEXT cycle.

Rules:
1. Weights must sum to EXACTLY 10000 basis points
2. No single asset may exceed {risk_profile.max_single_asset_bps} bps
3. Do NOT violate the rule constraints already applied (USDY cap, cmETH cap, allowlist)
4. Changes from current allocation should be proportional to signal strength

Respond with ONLY valid JSON (no markdown, no explanation outside the JSON):
{{
  "usdy_bps": <int>,
  "meth_bps": <int>,
  "cmeth_bps": <int>,
  "fbtc_bps": <int>,
  "usdc_bps": <int>,
  "reasoning": "<one sentence explaining the key change and why>",
  "confidence": <float 0.0-1.0>
}}"""
```

### Step 4 — Call DeepSeek V4 LLM and parse response
```python
import openai

client = openai.AsyncOpenAI(
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"],
)

response = await client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300,
    temperature=0.1   # low temperature for consistent numerical output
)

raw = response.choices[0].message.content
# Strip any accidental markdown fences
clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
parsed = json.loads(clean)
```

### Step 5 — Validate allocation
```python
def validate(parsed: dict, risk_profile: RiskProfile, macro: MacroSignal) -> Allocation:
    total = sum([parsed["usdy_bps"], parsed["meth_bps"],
                 parsed["cmeth_bps"], parsed["fbtc_bps"], parsed["usdc_bps"]])
    if total != 10_000:
        raise ValueError(f"Allocation sums to {total}, expected 10000")

    max_weight = max(parsed["usdy_bps"], parsed["meth_bps"],
                     parsed["cmeth_bps"], parsed["fbtc_bps"])
    if max_weight > risk_profile.max_single_asset_bps:
        raise ValueError(f"Single asset exceeds limit: {max_weight}")

    # Rule C enforcement
    if not macro.vault_on_usdy_allowlist and parsed["usdy_bps"] != 0:
        raise ValueError("USDY must be 0 when vault not on allowlist")

    # Rule B enforcement
    if macro.restaking_premium_bps < 50 and parsed["cmeth_bps"] != 0:
        raise ValueError("cmETH must be 0 when restaking premium < 50 bps")

    return Allocation(**{k: parsed[k] for k in ["usdy_bps","meth_bps","cmeth_bps","fbtc_bps","usdc_bps"]})
```

### Step 6 — Retry on validation failure (max 3 attempts)
If validation fails, re-invoke the LLM with the error appended to the prompt. After 3 failed attempts, fall back to the rule-adjusted base allocation for the user's risk level.

### Step 7 — Return AllocationDecision
Return the validated Allocation plus reasoning and confidence.

## Error Handling
- If LLM returns invalid JSON: strip response and retry (max 3 times)
- If validation fails after 3 retries: use rule-adjusted base allocation, set confidence = 0.0, reasoning = "fallback to base allocation due to LLM error"
- If DeepSeek API is unreachable: use rule-adjusted base allocation, log connectivity error
- Always return an AllocationDecision; never throw

## References
- `references/risk_profiles.json` — base allocations and constraint tables
- `references/asset_metadata.json` — asset descriptions and typical APY ranges
- `references/rule_thresholds.json` — Rule A/B/C threshold configuration
