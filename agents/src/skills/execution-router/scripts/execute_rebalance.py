"""
execute_rebalance.py — Execution Router skill implementation
Note: Uses SIMULATION mode until protocol addresses are fully confirmed.
Set DRY_RUN=false and fill all addresses to switch to live execution.
"""
import asyncio
import os
import time
from dataclasses import dataclass, field
from typing import Optional

from eth_account import Account
from web3 import Web3

MANTLE_RPC_URL = os.environ.get("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")
DRY_RUN        = os.environ.get("DRY_RUN", "true").lower() == "true"

DUST_THRESHOLD_BPS = 50  # ignore deltas < 0.5%

# -- Contract addresses (must be filled after Module A completes) --------------
USDC_ADDRESS  = os.environ.get("USDC_ADDRESS",  "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9")
METH_ADDRESS  = os.environ.get("METH_ADDRESS",  "0xcDA86A272531e8640cD7F1a92c01839911B90bb0")
USDY_ADDRESS  = os.environ.get("USDY_ADDRESS",  "0x5bE26527e817998A7206475496fDE1E68957c5A6")
FBTC_ADDRESS  = os.environ.get("FBTC_ADDRESS",  "0xC96dE26018A54D51c097160568752c4E3BD6C364")
MANTLE_LSP    = os.environ.get("MANTLE_LSP",    "0xe3cBd06D7dadB3F4e6557bAb7EdD924CD1489E8f")
MERCHANT_MOE  = os.environ.get("MERCHANT_MOE_LB_ROUTER", "")  # TODO: Module A
FLUXION       = os.environ.get("FLUXION_ROUTER_ADDRESS",  "")  # TODO: Module A

# Mantle LSP ABI (stake/unstake)
LSP_ABI = [
    {
        "name": "stake",
        "type": "function",
        "inputs": [],
        "outputs": [],
        "stateMutability": "payable",
    },
    {
        "name": "unstake",
        "type": "function",
        "inputs": [{"name": "mETHAmount", "type": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]


@dataclass
class ExecutionResult:
    tx_hashes:       list = field(default_factory=list)
    trades_executed: int  = 0
    trades_skipped:  int  = 0
    skip_reasons:    list = field(default_factory=list)
    execution_ok:    bool = True


def compute_deltas(current: dict, target: dict) -> dict:
    return {
        "usdy":    target.get("usdy_bps", 0)    - current.get("usdy_bps", 0),
        "xstocks": target.get("xstocks_bps", 0) - current.get("xstocks_bps", 0),
        "meth":    target.get("meth_bps", 0)    - current.get("meth_bps", 0),
        "fbtc":    target.get("fbtc_bps", 0)    - current.get("fbtc_bps", 0),
        "usdc":    target.get("usdc_bps", 0)    - current.get("usdc_bps", 0),
    }


async def simulate_or_execute_trade(
    asset:       str,
    delta_bps:   int,
    vault_tvl:   float,
    w3:          Web3,
    account:     Account,
) -> Optional[str]:
    """
    Core routing function.
    DRY_RUN=true: returns simulated tx hash, no broadcast.
    DRY_RUN=false: executes real transaction (requires addresses + balance).
    """
    direction  = "buy" if delta_bps > 0 else "sell"
    amount_usd = abs(delta_bps) / 10_000 * vault_tvl

    if DRY_RUN:
        # Simulation mode: generate deterministic fake hash (for pipeline testing)
        import hashlib
        fake = "0x" + hashlib.sha256(
            f"{asset}-{direction}-{amount_usd}-{time.time()}".encode()
        ).hexdigest()
        print(f"[ExecRouter] [DRY_RUN] {direction} {asset} ${amount_usd:.2f} -> {fake[:18]}...")
        await asyncio.sleep(0.1)  # simulate network delay
        return fake

    # -- Real execution (DRY_RUN=false, protocol addresses must be filled) -----

    if asset == "meth":
        return await execute_meth_trade(direction, amount_usd, w3, account)

    elif asset == "usdy":
        if not MERCHANT_MOE:
            print(f"[ExecRouter] Merchant Moe address not set, skipping USDY trade")
            return None
        return await execute_usdy_trade(direction, amount_usd, w3, account)

    elif asset == "xstocks":
        if not FLUXION:
            print(f"[ExecRouter] Fluxion address not set, skipping xStocks trade")
            return None
        return await execute_xstocks_trade(direction, amount_usd, w3, account)

    # fBTC and usdc adjustments skipped (awaiting Function vault address)
    print(f"[ExecRouter] {asset} trade not yet implemented, skipping")
    return None


async def execute_meth_trade(
    direction: str, amount_usd: float, w3: Web3, account: Account
) -> Optional[str]:
    """Stake/unstake mETH via Mantle LSP"""
    try:
        lsp = w3.eth.contract(address=MANTLE_LSP, abi=LSP_ABI)
        # Rough conversion: $2850/ETH (should read from oracle in production)
        eth_price_approx = 2850.0
        eth_amount       = amount_usd / eth_price_approx
        wei_amount       = int(eth_amount * 1e18)

        nonce = w3.eth.get_transaction_count(account.address)

        if direction == "buy":  # stake ETH -> get mETH
            tx = lsp.functions.stake().build_transaction({
                "from":    account.address,
                "value":   wei_amount,
                "nonce":   nonce,
                "gas":     200_000,
                "chainId": w3.eth.chain_id,
            })
        else:  # unstake mETH -> get ETH
            tx = lsp.functions.unstake(wei_amount).build_transaction({
                "from":    account.address,
                "nonce":   nonce,
                "gas":     200_000,
                "chainId": w3.eth.chain_id,
            })

        # eth_call simulation (prevent failed txs from wasting gas)
        try:
            w3.eth.call(tx)
        except Exception as sim_err:
            print(f"[ExecRouter] mETH {direction} simulation failed: {sim_err}. Skipping.")
            return None

        signed  = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        if receipt["status"] == 1:
            return tx_hash.hex()
        return None

    except Exception as e:
        print(f"[ExecRouter] mETH trade error: {e}")
        return None


async def execute_usdy_trade(direction, amount_usd, w3, account):
    """
    Buy/sell USDY via Merchant Moe LBRouter.
    TODO: implement full logic after MERCHANT_MOE address is filled.
    """
    print(f"[ExecRouter] USDY {direction} ${amount_usd:.2f} -- implementation pending Merchant Moe address")
    return None


async def execute_xstocks_trade(direction, amount_usd, w3, account):
    """
    Buy/sell xStocks via Fluxion Atomic RFQ.
    TODO: implement full logic after FLUXION address is filled.
    """
    print(f"[ExecRouter] xStocks {direction} ${amount_usd:.2f} -- implementation pending Fluxion address")
    return None


async def execute_rebalance(
    vault_address:     str,
    current_alloc:     dict,
    target_alloc:      dict,
    vault_tvl_usd:     float,
) -> dict:
    """Execution Router main function"""
    w3      = Web3(Web3.HTTPProvider(MANTLE_RPC_URL))
    account = Account.from_key(os.environ["AGENT_PRIVATE_KEY"])

    deltas = compute_deltas(current_alloc, target_alloc)
    result = ExecutionResult()

    for asset, delta_bps in deltas.items():
        if abs(delta_bps) < DUST_THRESHOLD_BPS:
            result.trades_skipped += 1
            result.skip_reasons.append(f"{asset}: {delta_bps}bps < dust threshold {DUST_THRESHOLD_BPS}bps")
            continue

        tx_hash = await simulate_or_execute_trade(
            asset, delta_bps, vault_tvl_usd, w3, account
        )

        if tx_hash:
            result.tx_hashes.append(tx_hash)
            result.trades_executed += 1
        else:
            result.trades_skipped += 1
            result.skip_reasons.append(f"{asset}: execution failed or skipped")

    if result.trades_executed == 0 and any(abs(d) >= DUST_THRESHOLD_BPS for d in deltas.values()):
        result.execution_ok = False

    return {
        "tx_hashes":       result.tx_hashes,
        "trades_executed": result.trades_executed,
        "trades_skipped":  result.trades_skipped,
        "skip_reasons":    result.skip_reasons,
        "execution_ok":    result.execution_ok,
        "dry_run":         DRY_RUN,
    }
