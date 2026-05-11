# risk-guardian

## Description
Monitors active RWA portfolio positions for risk breaches and fires on-chain alerts. Use before executing any rebalance and in every cycle to scan for emerging risks. Triggers on: "check risk", "monitor portfolio", "risk assessment", "portfolio health check".

## What This Skill Does
Evaluates five risk dimensions — concentration, drawdown, liquidity, macro stress, and restaking risk — and returns an alert level 0-3. Level 3 calls vault.fireRiskAlert() which pauses all deposits.

## Inputs
```
vault_address: string
current_allocation: Allocation
macro_signal: MacroSignal
vault_tvl_usd: float
portfolio_history: list[dict]   # Last 30 days of daily NAV snapshots
risk_profile: RiskProfile
```

## Output (RiskAssessment)
```json
{
  "alert_level": 1,
  "checks": {
    "concentration":   {"ok": true,  "max_weight_bps": 4200, "limit_bps": 6000},
    "drawdown":        {"ok": true,  "current_dd_bps": 320,  "limit_bps": 1500},
    "liquidity":       {"ok": true,  "liquid_pct": 87.5},
    "macro_stress":    {"ok": false, "risk_score": 18, "threshold": 20},
    "restaking_risk":  {"ok": true,  "restaking_premium_bps": 165, "min_threshold_bps": 50}
  },
  "reasons": ["Macro risk score critically low (18 < threshold 20)"],
  "action_taken": "none"
}
```

## Alert Levels
| Level | Meaning | Action |
|-------|---------|--------|
| 0 | All clear | None |
| 1 | Watch — minor concern | Log warning; no trade change |
| 2 | Adjust — rebalance toward safe assets | Force allocator to run with conservative_mode=True |
| 3 | Pause — extreme stress | Call vault.fireRiskAlert(3, reason); halt execution |

## Step-by-Step Instructions

### Step 1 — Concentration check
```python
def check_concentration(alloc: dict, limit_bps: int) -> dict:
    max_weight = max(alloc["usdy_bps"], alloc["meth_bps"],
                     alloc["cmeth_bps"], alloc["fbtc_bps"])
    ok = max_weight <= limit_bps
    level = 0 if ok else (2 if max_weight > limit_bps * 1.1 else 1)
    return {"ok": ok, "max_weight_bps": max_weight, "limit_bps": limit_bps, "alert": level}
```

### Step 2 — Drawdown check
```python
def check_drawdown(history: list, limit_bps: int) -> dict:
    if len(history) < 2:
        return {"ok": True, "current_dd_bps": 0, "limit_bps": limit_bps, "alert": 0}
    peak    = max(h["nav_usd"] for h in history[-30:])
    current = history[-1]["nav_usd"]
    dd_bps  = int((1 - current / peak) * 10_000) if peak > 0 else 0
    ok      = dd_bps <= limit_bps
    level   = 0 if ok else (3 if dd_bps > limit_bps * 1.5 else 2)
    return {"ok": ok, "current_dd_bps": dd_bps, "limit_bps": limit_bps, "alert": level}
```

### Step 3 — Liquidity check
```python
def check_liquidity(alloc: dict, tvl: float) -> dict:
    # USDC and USDY are fully liquid; mETH/cmETH have DEX liquidity constraints; fBTC has 2-day
    liquid_bps = alloc["usdc_bps"] + alloc["usdy_bps"] + alloc["meth_bps"] * 0.8 + alloc["cmeth_bps"] * 0.7
    liquid_pct = liquid_bps / 100
    ok = liquid_pct >= 25.0  # at least 25% liquid at all times
    level = 0 if ok else (2 if liquid_pct >= 15.0 else 3)
    return {"ok": ok, "liquid_pct": liquid_pct, "alert": level}
```

### Step 4 — Macro stress check
```python
def check_macro_stress(macro: dict) -> dict:
    risk_score = macro["risk_score"]
    ok         = risk_score >= 20
    level      = 0 if risk_score >= 30 else (1 if risk_score >= 20 else (2 if risk_score >= 10 else 3))
    return {"ok": ok, "risk_score": risk_score, "threshold": 20, "alert": level}
```

### Step 5 — Restaking risk check
```python
def check_restaking_risk(macro: dict, alloc: dict) -> dict:
    """
    Validates that cmETH exposure is justified by sufficient restaking premium.
    If premium is too low but cmETH weight is non-zero, flag a risk alert.
    """
    restaking_premium = macro["restaking_premium_bps"]
    cmeth_weight = alloc["cmeth_bps"]
    min_threshold_bps = 50  # minimum acceptable premium

    # Risk only applies if we hold cmETH
    if cmeth_weight == 0:
        return {"ok": True, "restaking_premium_bps": restaking_premium,
                "min_threshold_bps": min_threshold_bps, "alert": 0}

    ok = restaking_premium >= min_threshold_bps
    if not ok:
        # Premium too low for the risk we are taking
        level = 2 if restaking_premium >= 25 else 3
    else:
        level = 0

    return {"ok": ok, "restaking_premium_bps": restaking_premium,
            "min_threshold_bps": min_threshold_bps, "alert": level}
```

### Step 6 — Aggregate to final alert level
```python
final_level = max(
    concentration_result["alert"],
    drawdown_result["alert"],
    liquidity_result["alert"],
    macro_result["alert"],
    restaking_result["alert"]
)
```

### Step 7 — Fire on-chain alert if level >= 2
```python
if final_level >= 2:
    reasons = [r for r in all_reason_strings if r]
    reason_str = "; ".join(reasons)

    vault_contract = w3.eth.contract(address=vault_address, abi=VAULT_ABI)
    tx = vault_contract.functions.fireRiskAlert(
        final_level,
        reason_str[:200]  # contract has 200 char limit
    ).build_transaction({"from": agent_address, "gas": 80_000})

    signed = w3.eth.account.sign_transaction(tx, os.environ["AGENT_PRIVATE_KEY"])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction).hex()
    print(f"[RiskGuardian] Level-{final_level} alert fired. TX: {tx_hash}")
```

## Error Handling
- If history data is missing: skip drawdown check, log warning, continue
- If restaking premium data is unavailable: assume premium = 0, flag level-2 alert for cmETH holders
- If on-chain alert tx fails: log error, still return the RiskAssessment — caller must handle
- Never block the pipeline — if this skill itself throws, return level=0 with error flag

## References
- `references/risk_thresholds.json` — configurable thresholds per risk level
- `references/vault_abi.json` — MosaicVault ABI for fireRiskAlert
