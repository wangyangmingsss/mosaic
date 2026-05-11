"""
mosaic_pipeline.py — Main mulerun agent orchestration loop

This is the entry point for the Mosaic AI agent pipeline.
Run with:
    python mosaic_pipeline.py --vault 0xYourVaultAddress

The pipeline runs indefinitely on a 15-minute cycle, coordinating
all five sub-agents through MuleRun's skill invocation system.
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Optional

# ── Logging setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mosaic_pipeline.log"),
    ],
)
log = logging.getLogger("Mosaic")

# ── Configuration ─────────────────────────────────────────────────────────────

CYCLE_INTERVAL_SECONDS = 900          # 15 minutes
SIGNAL_SHIFT_THRESHOLD  = 10          # Trigger rebalance if risk score shifts >10
MIN_TRADE_SIZE_BPS      = 50          # Ignore deltas smaller than 0.5%

REQUIRED_ENV_VARS = [
    "MANTLE_RPC_URL",
    "AGENT_PRIVATE_KEY",
    "AGENT_EOA",
    "PYTH_ENDPOINT",
    "BYBIT_API_KEY",
    "BYBIT_SECRET",
    "PINATA_JWT",
    "VAULT_FACTORY_ADDRESS",
    "DECISION_LOG_ADDRESS",
]

# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class MacroSignal:
    risk_score:       int
    equity_momentum:  str
    meth_apy:         float
    usdy_yield:       float
    btc_funding_rate: float
    equity_prices:    dict
    timestamp:        int
    data_freshness_ok: bool

@dataclass
class Allocation:
    usdy_bps:    int
    xstocks_bps: int
    meth_bps:    int
    fbtc_bps:    int
    usdc_bps:    int

    def validate(self):
        total = self.usdy_bps + self.xstocks_bps + self.meth_bps + self.fbtc_bps + self.usdc_bps
        if total != 10_000:
            raise ValueError(f"Allocation must sum to 10000 bps, got {total}")

    def to_tuple(self):
        return (self.usdy_bps, self.xstocks_bps, self.meth_bps, self.fbtc_bps, self.usdc_bps)

@dataclass
class RiskProfile:
    risk_level:          int
    rebalance_frequency: int   # 1=daily, 2=weekly, 3=monthly
    max_drawdown_bps:    int
    max_single_asset_bps: int

@dataclass
class RiskAssessment:
    alert_level: int
    checks:      dict
    reasons:     list
    action_taken: str

@dataclass
class ExecutionResult:
    tx_hashes:        list
    trades_executed:  int
    trades_skipped:   int
    skip_reasons:     list
    execution_ok:     bool

@dataclass
class ScribeResult:
    ipfs_cid:     str
    record_hash:  str
    tx_hash:      Optional[str]
    decision_id:  int
    metadata_uri: str

# ── Skill invokers ────────────────────────────────────────────────────────────
# Each function below corresponds to one MuleRun skill ZIP installed in the
# agents/src/skills/ directory.  In the MuleRun runtime, skills are invoked
# by the agent automatically when their SKILL.md trigger conditions match.
# For local/CI use, we implement them as direct Python function calls.

async def invoke_macro_sentinel(vault_address: str, prev_score: int) -> MacroSignal:
    """Invoke macro-sentinel skill."""
    from skills.macro_sentinel import fetch_macro_signal
    return await fetch_macro_signal(vault_address, prev_score)

async def invoke_allocator(
    macro: MacroSignal,
    profile: RiskProfile,
    current: Allocation
) -> tuple[Allocation, str, float]:
    """Invoke allocator skill. Returns (allocation, reasoning, confidence)."""
    from skills.allocator import compute_allocation
    return await compute_allocation(macro, profile, current)

async def invoke_execution_router(
    vault_address: str,
    current: Allocation,
    target: Allocation,
    vault_tvl_usd: float
) -> ExecutionResult:
    """Invoke execution-router skill."""
    from skills.execution_router import execute_rebalance
    return await execute_rebalance(vault_address, current, target, vault_tvl_usd)

async def invoke_risk_guardian(
    vault_address: str,
    current: Allocation,
    macro: MacroSignal,
    vault_tvl_usd: float,
    history: list,
    profile: RiskProfile
) -> RiskAssessment:
    """Invoke risk-guardian skill."""
    from skills.risk_guardian import assess_risk
    return await assess_risk(vault_address, current, macro, vault_tvl_usd, history, profile)

async def invoke_reporting_scribe(
    vault_address: str,
    decision_id: int,
    macro: MacroSignal,
    previous: Allocation,
    target: Allocation,
    reasoning: str,
    tx_hashes: list,
    risk_assessment: RiskAssessment,
    trigger: str,
    pnl_delta_bps: int
) -> ScribeResult:
    """Invoke reporting-scribe skill."""
    from skills.reporting_scribe import write_record
    return await write_record(
        vault_address, decision_id, macro, previous, target,
        reasoning, tx_hashes, risk_assessment, trigger, pnl_delta_bps
    )

# ── Vault state helpers ───────────────────────────────────────────────────────

async def fetch_vault_state(vault_address: str) -> tuple[Allocation, RiskProfile, float, list]:
    """
    Read current allocation, risk profile, TVL, and 30-day NAV history
    from the MosaicVault contract and local state cache.
    """
    from web3 import Web3
    from config import VAULT_ABI

    w3    = Web3(Web3.HTTPProvider(os.environ["MANTLE_RPC_URL"]))
    vault = w3.eth.contract(address=vault_address, abi=VAULT_ABI)

    # Read on-chain allocation
    alloc_raw  = vault.functions.getAllocation().call()
    allocation = Allocation(*alloc_raw)

    # Read on-chain risk profile
    profile_raw = vault.functions.riskProfile().call()
    profile     = RiskProfile(*profile_raw)

    # Read TVL (totalAssets in USDC, 6 decimals)
    tvl_raw = vault.functions.totalAssets().call()
    tvl_usd = tvl_raw / 1e6

    # NAV history: in production, read from DecisionLog + subgraph
    # For now, return empty list (risk-guardian handles missing history)
    nav_history = []

    return allocation, profile, tvl_usd, nav_history

def needs_rebalance(
    current_score: int,
    previous_score: Optional[int],
    profile: RiskProfile,
    last_rebalance_ts: Optional[int]
) -> tuple[bool, str]:
    """Determine if a rebalance should be triggered this cycle."""
    now = int(time.time())

    # Signal shift trigger
    if previous_score is not None:
        if abs(current_score - previous_score) > SIGNAL_SHIFT_THRESHOLD:
            return True, "macro_signal_shift"

    # Time trigger
    if last_rebalance_ts is not None:
        freq_seconds = {1: 86400, 2: 604800, 3: 2592000}
        if now - last_rebalance_ts >= freq_seconds.get(profile.rebalance_frequency, 604800):
            return True, "time_trigger"

    # First cycle always triggers
    if previous_score is None:
        return True, "initial"

    return False, "none"

# ── Main pipeline loop ────────────────────────────────────────────────────────

async def run_pipeline(vault_address: str):
    """
    Main agent loop. Runs indefinitely, executing one cycle every CYCLE_INTERVAL_SECONDS.
    """
    log.info(f"Mosaic Pipeline starting for vault {vault_address}")
    log.info(f"Cycle interval: {CYCLE_INTERVAL_SECONDS}s ({CYCLE_INTERVAL_SECONDS // 60}m)")

    # ── Persistent state ──────────────────────────────────────────────────────
    previous_macro:    Optional[MacroSignal]  = None
    last_rebalance_ts: Optional[int]          = None
    decision_counter:  int                    = 0

    while True:
        cycle_start = time.time()
        log.info(f"─── Cycle {decision_counter + 1} ─────────────────────────────────────────")

        try:
            # ── Step 1: Fetch vault state ─────────────────────────────────────
            current_alloc, profile, tvl_usd, nav_history = await fetch_vault_state(vault_address)
            log.info(f"Vault TVL: ${tvl_usd:,.2f} | Risk level: {profile.risk_level}")

            # ── Step 2: Macro Sentinel ────────────────────────────────────────
            prev_score = previous_macro.risk_score if previous_macro else None
            macro      = await invoke_macro_sentinel(vault_address, prev_score or 50)
            log.info(
                f"MacroSignal: risk_score={macro.risk_score} | "
                f"equity={macro.equity_momentum} | mETH={macro.meth_apy:.2f}% | "
                f"fresh={macro.data_freshness_ok}"
            )

            # ── Step 3: Decide whether to rebalance ───────────────────────────
            do_rebalance, trigger = needs_rebalance(
                macro.risk_score, prev_score, profile, last_rebalance_ts
            )

            if not do_rebalance:
                log.info("No rebalance trigger. Sleeping until next cycle.")
                previous_macro = macro
                await asyncio.sleep(max(0, CYCLE_INTERVAL_SECONDS - (time.time() - cycle_start)))
                continue

            log.info(f"Rebalance triggered: {trigger}")

            # ── Step 4: Risk Guardian pre-check ──────────────────────────────
            risk = await invoke_risk_guardian(
                vault_address, current_alloc, macro, tvl_usd, nav_history, profile
            )
            log.info(f"RiskAssessment: alert_level={risk.alert_level} | {risk.reasons}")

            if risk.alert_level >= 3:
                log.warning(f"LEVEL-3 ALERT — skipping execution this cycle. Reasons: {risk.reasons}")
                previous_macro = macro
                await asyncio.sleep(max(0, CYCLE_INTERVAL_SECONDS - (time.time() - cycle_start)))
                continue

            # ── Step 5: Allocator ─────────────────────────────────────────────
            target_alloc, reasoning, confidence = await invoke_allocator(
                macro, profile, current_alloc
            )
            target_alloc.validate()
            log.info(
                f"Allocator: {reasoning} | confidence={confidence:.2f} | "
                f"alloc={asdict(target_alloc)}"
            )

            # ── Step 6: Execution Router ──────────────────────────────────────
            exec_result = await invoke_execution_router(
                vault_address, current_alloc, target_alloc, tvl_usd
            )
            log.info(
                f"Execution: {exec_result.trades_executed} trades | "
                f"ok={exec_result.execution_ok} | "
                f"txs={exec_result.tx_hashes}"
            )

            # ── Step 7: Reporting Scribe ──────────────────────────────────────
            decision_counter += 1
            scribe = await invoke_reporting_scribe(
                vault_address  = vault_address,
                decision_id    = decision_counter,
                macro          = macro,
                previous       = current_alloc,
                target         = target_alloc,
                reasoning      = reasoning,
                tx_hashes      = exec_result.tx_hashes,
                risk_assessment = risk,
                trigger        = trigger,
                pnl_delta_bps  = 0,  # calculated by performance tracker
            )
            log.info(
                f"Scribe: IPFS={scribe.ipfs_cid} | "
                f"hash={scribe.record_hash[:18]}... | "
                f"chain_tx={scribe.tx_hash}"
            )

            # ── Update state ──────────────────────────────────────────────────
            previous_macro    = macro
            last_rebalance_ts = int(time.time())

            log.info(
                f"✓ Cycle {decision_counter} complete. "
                f"Vault: {vault_address[:10]}... | "
                f"Record #{decision_counter}"
            )

        except Exception as e:
            # A crashed cycle should NEVER stop the pipeline
            log.error(f"Cycle error (will retry next cycle): {e}", exc_info=True)

        # ── Sleep until next cycle ────────────────────────────────────────────
        elapsed = time.time() - cycle_start
        sleep_for = max(0, CYCLE_INTERVAL_SECONDS - elapsed)
        log.info(f"Sleeping {sleep_for:.0f}s until next cycle.")
        await asyncio.sleep(sleep_for)

# ── Environment validation ────────────────────────────────────────────────────

def validate_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        log.error(f"Missing environment variables: {missing}")
        log.error("Copy .env.example to .env and fill in all values.")
        sys.exit(1)
    log.info("Environment variables validated.")

# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mosaic RWA Portfolio Agent Pipeline")
    parser.add_argument("--vault",   required=True,  help="MosaicVault contract address")
    parser.add_argument("--dry-run", action="store_true", help="Simulate but don't broadcast txs")
    args = parser.parse_args()

    validate_env()

    if args.dry_run:
        os.environ["DRY_RUN"] = "1"
        log.info("DRY RUN MODE — no transactions will be broadcast")

    asyncio.run(run_pipeline(args.vault))
