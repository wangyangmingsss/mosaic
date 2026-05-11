"""
assess_risk.py — Risk Guardian skill implementation
Four-dimensional risk check: concentration, drawdown, liquidity, macro stress
"""
import os
from dataclasses import dataclass, asdict
from typing import Optional

from web3 import Web3
from eth_account import Account

MANTLE_RPC_URL = os.environ.get("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")

VAULT_ALERT_ABI = [
    {
        "name": "fireRiskAlert",
        "type": "function",
        "inputs": [
            {"name": "level",  "type": "uint8"},
            {"name": "reason", "type": "string"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    }
]


@dataclass
class RiskCheck:
    ok:    bool
    level: int      # 0-3
    detail: dict


def check_concentration(alloc: dict, max_single_asset_bps: int) -> RiskCheck:
    """Concentration check: no single asset may exceed maxSingleAssetBps"""
    max_w = max(
        alloc.get("usdy_bps", 0),
        alloc.get("xstocks_bps", 0),
        alloc.get("meth_bps", 0),
        alloc.get("fbtc_bps", 0),
    )
    ok = max_w <= max_single_asset_bps

    if max_w > max_single_asset_bps * 1.1:
        level = 2
    elif max_w > max_single_asset_bps:
        level = 1
    else:
        level = 0

    return RiskCheck(ok=ok, level=level, detail={
        "max_weight_bps": max_w,
        "limit_bps":      max_single_asset_bps,
    })


def check_drawdown(nav_history: list, max_drawdown_bps: int) -> RiskCheck:
    """30-day max drawdown check"""
    if len(nav_history) < 2:
        return RiskCheck(ok=True, level=0, detail={"current_dd_bps": 0})

    recent = nav_history[-30:] if len(nav_history) >= 30 else nav_history
    peak   = max(h.get("nav_usd", 0) for h in recent)
    curr   = nav_history[-1].get("nav_usd", peak)

    dd_bps = int((1 - curr / peak) * 10_000) if peak > 0 else 0

    if dd_bps > max_drawdown_bps * 1.5:
        level = 3
    elif dd_bps > max_drawdown_bps:
        level = 2
    elif dd_bps > max_drawdown_bps * 0.7:
        level = 1
    else:
        level = 0

    return RiskCheck(ok=(dd_bps <= max_drawdown_bps), level=level, detail={
        "current_dd_bps": dd_bps,
        "limit_bps":      max_drawdown_bps,
        "peak_nav":       peak,
        "current_nav":    curr,
    })


def check_liquidity(alloc: dict) -> RiskCheck:
    """
    Liquidity check.
    USDC + USDY are instantly liquid; xStocks ~90% liquid during market hours;
    mETH has 7-day unstaking delay; fBTC has 2-day delay.
    Requirement: instantly liquid assets >= 25%.
    """
    liquid_bps = (
        alloc.get("usdc_bps", 0) +
        alloc.get("usdy_bps", 0) +
        alloc.get("xstocks_bps", 0) * 0.9  # 90% instantly liquidatable
    )
    liquid_pct = liquid_bps / 100  # convert to percentage

    if liquid_pct < 15:
        level = 3
    elif liquid_pct < 25:
        level = 2
    elif liquid_pct < 35:
        level = 1
    else:
        level = 0

    return RiskCheck(ok=(liquid_pct >= 25), level=level, detail={
        "liquid_pct":   round(liquid_pct, 1),
        "threshold_pct": 25,
    })


def check_macro_stress(macro_signal: dict) -> RiskCheck:
    """Macro stress check"""
    risk_score = macro_signal.get("risk_score", 50)

    if risk_score < 10:
        level = 3
    elif risk_score < 20:
        level = 2
    elif risk_score < 30:
        level = 1
    else:
        level = 0

    return RiskCheck(ok=(risk_score >= 20), level=level, detail={
        "risk_score": risk_score,
        "threshold":  20,
    })


async def fire_onchain_alert(
    vault_address:     str,
    alert_level:       int,
    reason:            str,
    agent_private_key: str,
) -> Optional[str]:
    """Call vault.fireRiskAlert() to write on-chain event"""
    try:
        w3      = Web3(Web3.HTTPProvider(MANTLE_RPC_URL))
        account = Account.from_key(agent_private_key)
        vault   = w3.eth.contract(address=vault_address, abi=VAULT_ALERT_ABI)

        # reason max 200 chars (contract limit)
        truncated_reason = reason[:200]

        nonce = w3.eth.get_transaction_count(account.address)
        tx = vault.functions.fireRiskAlert(
            alert_level, truncated_reason
        ).build_transaction({
            "from":    account.address,
            "nonce":   nonce,
            "gas":     100_000,
            "chainId": w3.eth.chain_id,
        })
        signed  = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"[RiskGuardian] fireRiskAlert level={alert_level} tx={tx_hash.hex()}")
        return tx_hash.hex()

    except Exception as e:
        print(f"[RiskGuardian] fireRiskAlert failed: {e}")
        return None


async def assess_risk(
    vault_address:    str,
    current_alloc:    dict,
    macro_signal:     dict,
    vault_tvl_usd:    float,
    nav_history:      list,
    risk_profile:     dict,
) -> dict:
    """
    Risk Guardian main function.
    Returns standard RiskAssessment dict.
    """
    max_single = risk_profile.get("max_single_asset_bps", 6000)
    max_dd     = risk_profile.get("max_drawdown_bps", 1500)

    # Four-dimensional check
    concentration_check = check_concentration(current_alloc, max_single)
    drawdown_check      = check_drawdown(nav_history, max_dd)
    liquidity_check     = check_liquidity(current_alloc)
    macro_check         = check_macro_stress(macro_signal)

    # Take highest alert level
    final_level = max(
        concentration_check.level,
        drawdown_check.level,
        liquidity_check.level,
        macro_check.level,
    )

    # Collect alert reasons
    reasons = []
    if not concentration_check.ok:
        reasons.append(
            f"Concentration {concentration_check.detail['max_weight_bps']}bps "
            f"> limit {concentration_check.detail['limit_bps']}bps"
        )
    if not drawdown_check.ok:
        reasons.append(
            f"Drawdown {drawdown_check.detail['current_dd_bps']}bps "
            f"> limit {drawdown_check.detail['limit_bps']}bps"
        )
    if not liquidity_check.ok:
        reasons.append(
            f"Liquidity {liquidity_check.detail['liquid_pct']}% "
            f"< threshold {liquidity_check.detail['threshold_pct']}%"
        )
    if not macro_check.ok:
        reasons.append(
            f"Macro risk_score {macro_check.detail['risk_score']} "
            f"< threshold {macro_check.detail['threshold']}"
        )

    # Fire on-chain alert (level >= 2)
    action_taken = "none"
    if final_level >= 2:
        agent_key = os.environ.get("AGENT_PRIVATE_KEY", "")
        if agent_key:
            reason_str = "; ".join(reasons) if reasons else "Automatic risk check"
            await fire_onchain_alert(vault_address, final_level, reason_str, agent_key)
            action_taken = f"fired_alert_level_{final_level}"

    return {
        "alert_level":  final_level,
        "checks": {
            "concentration": asdict(concentration_check),
            "drawdown":      asdict(drawdown_check),
            "liquidity":     asdict(liquidity_check),
            "macro_stress":  asdict(macro_check),
        },
        "reasons":      reasons,
        "action_taken": action_taken,
    }
