"""
compute_allocation.py — Allocator skill implementation
Black-Litterman framework + LLM views, outputs validated target allocation.
"""
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

# DeepSeek V4 API (OpenAI-compatible)
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com",
)

BASE_ALLOCATIONS = {
    1: {"usdy_bps": 5000, "xstocks_bps": 1500, "meth_bps": 2000, "fbtc_bps":  500, "usdc_bps": 1000},
    2: {"usdy_bps": 3000, "xstocks_bps": 3000, "meth_bps": 2500, "fbtc_bps": 1000, "usdc_bps":  500},
    3: {"usdy_bps": 1500, "xstocks_bps": 4500, "meth_bps": 2500, "fbtc_bps": 1500, "usdc_bps":    0},
}


def validate_allocation(parsed: dict, risk_profile: dict) -> Optional[str]:
    """
    Validate LLM output allocation against constraints.
    Returns error message string, None if valid.
    """
    keys = ["usdy_bps", "xstocks_bps", "meth_bps", "fbtc_bps", "usdc_bps"]

    # Check all keys exist
    for k in keys:
        if k not in parsed:
            return f"Missing key: {k}"
        if not isinstance(parsed[k], int):
            return f"Key {k} must be int, got {type(parsed[k])}"

    # Check total
    total = sum(parsed[k] for k in keys)
    if total != 10_000:
        return f"Allocation sums to {total}, must be 10000"

    # Check non-negative
    for k in keys:
        if parsed[k] < 0:
            return f"Key {k} is negative: {parsed[k]}"

    # Check single asset limit
    max_single = risk_profile.get("max_single_asset_bps", 6000)
    for k in ["xstocks_bps", "meth_bps", "fbtc_bps"]:
        if parsed[k] > max_single:
            return f"{k}={parsed[k]} exceeds max_single_asset_bps={max_single}"

    return None  # validation passed


def build_prompt(macro_signal: dict, risk_profile: dict, current_alloc: dict) -> str:
    risk_level = risk_profile.get("risk_level", 2)
    base = BASE_ALLOCATIONS.get(risk_level, BASE_ALLOCATIONS[2])

    return f"""You are a quantitative portfolio manager for a Real World Asset (RWA) portfolio on Mantle blockchain.

## Current Macro Environment
- Risk score: {macro_signal.get('risk_score', 50)}/100 (0=extreme fear, 100=extreme greed)
- Equity momentum: {macro_signal.get('equity_momentum', 'neutral')}
- mETH staking APY: {macro_signal.get('meth_apy', 4.2):.2f}%
- USDY Treasury yield: {macro_signal.get('usdy_yield', 4.85):.2f}%
- BTC funding rate: {macro_signal.get('btc_funding_rate', 0.0001):.5f}

## Current Allocation (basis points, sum = 10000)
{json.dumps(current_alloc, indent=2)}

## Base Allocation for Risk Level {risk_level}
{json.dumps(base, indent=2)}

## User Constraints
- max_single_asset_bps: {risk_profile.get('max_single_asset_bps', 6000)}
- max_drawdown_bps: {risk_profile.get('max_drawdown_bps', 1500)}

## Asset Characteristics
- USDY (~{macro_signal.get('usdy_yield', 4.85):.2f}% APY): US Treasury yield, very low volatility, defensive safe-haven
- xStocks: Tokenized equities (TSLAx, NVDAx, SPYx), growth-oriented, correlated to US equity markets
- mETH ({macro_signal.get('meth_apy', 4.2):.2f}% APY): ETH liquid staking, moderate volatility, crypto-native yield
- fBTC: BTC restaking via Babylon, highest risk/return, Bitcoin-correlated
- USDC: Cash reserve, 0 yield, maximum liquidity for rebalancing

## Your Task
Determine the optimal target allocation for the next 15-minute cycle.

STRICT RULES:
1. All 5 weights MUST sum to exactly 10000 basis points
2. No single asset may exceed {risk_profile.get('max_single_asset_bps', 6000)} basis points
3. For risk_level=1 (conservative): xstocks_bps <= 2500
4. Changes from current should be proportional to signal strength (avoid excessive turnover)
5. If risk_score < 30, increase USDY and USDC defensively

Respond with ONLY valid JSON, no markdown, no explanation outside the JSON:
{{
  "usdy_bps": <integer>,
  "xstocks_bps": <integer>,
  "meth_bps": <integer>,
  "fbtc_bps": <integer>,
  "usdc_bps": <integer>,
  "reasoning": "<one concise sentence explaining the main change and why>",
  "confidence": <float 0.0-1.0>
}}"""


async def compute_allocation(
    macro_signal:    dict,
    risk_profile:    dict,
    current_alloc:   dict,
) -> tuple:
    """
    Allocator main function.
    Returns (target_allocation: dict, reasoning: str, confidence: float).
    """
    risk_level = risk_profile.get("risk_level", 2)
    base       = BASE_ALLOCATIONS.get(risk_level, BASE_ALLOCATIONS[2])
    prompt     = build_prompt(macro_signal, risk_profile, current_alloc)

    last_error = ""
    for attempt in range(3):
        try:
            # Append error info on retry
            full_prompt = prompt
            if last_error and attempt > 0:
                full_prompt += f"\n\nPREVIOUS ATTEMPT FAILED WITH: {last_error}\nPlease fix and ensure all weights sum to exactly 10000."

            response = client.chat.completions.create(
                model       = "deepseek-chat",
                max_tokens  = 400,
                temperature = 0.1,
                messages    = [{"role": "user", "content": full_prompt}],
            )

            raw = response.choices[0].message.content.strip()

            # Clean markdown fences (just in case)
            raw = re.sub(r"```(?:json)?", "", raw).strip()

            parsed = json.loads(raw)

            # Validate
            error = validate_allocation(parsed, risk_profile)
            if error:
                last_error = error
                print(f"[Allocator] Attempt {attempt+1} validation failed: {error}")
                continue

            return (
                {k: parsed[k] for k in ["usdy_bps", "xstocks_bps", "meth_bps", "fbtc_bps", "usdc_bps"]},
                parsed.get("reasoning", "No reasoning provided"),
                float(parsed.get("confidence", 0.5)),
            )

        except json.JSONDecodeError as e:
            last_error = f"JSON parse error: {e}. Raw output: {raw[:200]}"
            print(f"[Allocator] Attempt {attempt+1} JSON parse failed: {e}")
        except Exception as e:
            last_error = str(e)
            print(f"[Allocator] Attempt {attempt+1} error: {e}")

    # All 3 attempts failed, return base allocation
    print(f"[Allocator] All 3 attempts failed. Using base allocation for risk_level={risk_level}.")
    return (
        base,
        f"Fallback to base allocation (risk_level={risk_level}) due to LLM error: {last_error[:100]}",
        0.0,
    )
