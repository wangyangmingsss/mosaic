"""
benchmark_calculator.py — Compute benchmark strategy (fixed allocation) hypothetical NAV

Benchmark strategy definitions:
- Conservative (riskLevel=1): 50% USDY + 20% mETH + 30% USDC (no xStocks, fBTC)
- Balanced (riskLevel=2): 40% USDY + 30% xStocks + 20% mETH + 10% USDC (no rebalancing)
- Aggressive (riskLevel=3): 20% USDY + 50% xStocks + 25% mETH + 5% USDC (no rebalancing)

NAV tracking: initial value set to 10000 bps (100%), updated each cycle by current prices.
"""

from typing import Optional

BENCHMARK_ALLOCATIONS = {
    1: {"usdy": 0.50, "xstocks": 0.00, "meth": 0.20, "fbtc": 0.00, "usdc": 0.30},
    2: {"usdy": 0.40, "xstocks": 0.30, "meth": 0.20, "fbtc": 0.00, "usdc": 0.10},
    3: {"usdy": 0.20, "xstocks": 0.50, "meth": 0.25, "fbtc": 0.00, "usdc": 0.05},
}


class BenchmarkCalculator:
    """
    Track benchmark strategy hypothetical NAV.

    Usage:
    1. Initialize with risk_level and initial asset prices
    2. Call update() after each agent rebalance with current prices
    3. Read benchmark_nav_bps and vault_nav_bps to compute alpha
    """

    def __init__(self, risk_level: int, initial_prices: dict):
        self.risk_level       = risk_level
        self.weights          = BENCHMARK_ALLOCATIONS.get(risk_level, BENCHMARK_ALLOCATIONS[2])
        self.initial_prices   = initial_prices.copy()
        self.initial_nav_bps  = 10_000  # 100%

    def compute_nav_bps(self, current_prices: dict) -> int:
        """
        Compute benchmark strategy NAV at current prices (relative to initial).

        NAV_bps = 10000 * sum(weight_i * current_price_i / initial_price_i)

        Price key mapping:
        - "usdy"    -> current_prices["usdy_nav"] (USDY net value, initial ~1.0)
        - "xstocks" -> current_prices["spy_price"] (SPY as xStocks proxy)
        - "meth"    -> current_prices["meth_eth_ratio"] (1 mETH = X ETH)
        - "usdc"    -> 1.0 (stablecoin)
        """
        usdy_ratio = (
            current_prices.get("usdy_nav", 1.0) /
            self.initial_prices.get("usdy_nav", 1.0)
        )
        xstocks_ratio = (
            current_prices.get("spy_price", 542.0) /
            self.initial_prices.get("spy_price", 542.0)
        ) if self.initial_prices.get("spy_price", 0) > 0 else 1.0

        meth_ratio = (
            current_prices.get("meth_eth_ratio", 1.042) /
            self.initial_prices.get("meth_eth_ratio", 1.042)
        ) if self.initial_prices.get("meth_eth_ratio", 0) > 0 else 1.0

        nav = (
            self.weights["usdy"]    * usdy_ratio    +
            self.weights["xstocks"] * xstocks_ratio +
            self.weights["meth"]    * meth_ratio    +
            self.weights["usdc"]    * 1.0           # stablecoin
        )

        return int(10_000 * nav)

    def compute_vault_nav_bps(
        self,
        initial_deposit_usd: float,
        current_vault_assets_usd: float
    ) -> int:
        """
        Compute vault actual NAV (relative to initial deposit).
        Requires reading vault.totalAssets() from chain.
        """
        if initial_deposit_usd <= 0:
            return 10_000
        return int(10_000 * current_vault_assets_usd / initial_deposit_usd)
