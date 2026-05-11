"""
fetch_macro.py — Macro Sentinel skill implementation
Pulls macro data from Pyth, Mantle LSP, Bybit, outputs MacroSignal JSON
"""
import asyncio
import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Optional

import httpx
from web3 import Web3

# -- Config --------------------------------------------------------------------

PYTH_HERMES_URL = "https://hermes.pyth.network/v2/updates/price/latest"
MANTLE_RPC_URL  = os.environ.get("MANTLE_RPC_URL", "https://rpc.sepolia.mantle.xyz")
BYBIT_BASE_URL  = "https://api.bybit.com"

# Pyth price feed IDs (verified on Mantle)
# Full list: https://pyth.network/developers/price-feed-ids
PYTH_IDS = {
    "ETH":  "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "BTC":  "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    # xStocks price feeds — use equity market index proxies for demo
    "SPY":  "0x19e09bb805456ada3979a7d1cbb4b6d63babc3a0f8e8a9509f68afa5c1c76c4a",
    "QQQ":  "0x28ce9e26b83c33e77f7e98615c6e4e9a4ea0ec38dc4e1fbb8de4c432ee36b3fd",
}

MANTLE_LSP_ADDRESS = "0xe3cBd06D7dadB3F4e6557bAb7EdD924CD1489E8f"
MANTLE_LSP_ABI = [
    {
        "name": "mETHToETH",
        "type": "function",
        "inputs": [{"name": "mETHAmount", "type": "uint256"}],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
    },
    {
        "name": "totalControlled",
        "type": "function",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
    },
]

# -- Data model ----------------------------------------------------------------

@dataclass
class MacroSignal:
    risk_score:        int
    equity_momentum:   str   # "bullish" | "neutral" | "bearish"
    meth_apy:          float
    usdy_yield:        float
    btc_funding_rate:  float
    equity_prices:     dict
    timestamp:         int
    data_freshness_ok: bool

# -- Data fetchers -------------------------------------------------------------

async def fetch_pyth_prices() -> dict:
    """Fetch latest prices from Pyth Hermes."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            params = {"ids[]": list(PYTH_IDS.values())}
            resp = await client.get(PYTH_HERMES_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            prices = {}
            for item in data.get("parsed", []):
                feed_id = "0x" + item["id"]
                for sym, pid in PYTH_IDS.items():
                    if pid == feed_id:
                        price_raw = item["price"]["price"]
                        expo      = item["price"]["expo"]
                        prices[sym] = float(price_raw) * (10 ** expo)
                        break
            return prices

        except Exception as e:
            print(f"[MacroSentinel] Pyth fetch failed: {e}. Using fallback.")
            return {
                "ETH": 2850.0,
                "BTC": 95000.0,
                "SPY": 542.0,
                "QQQ": 465.0,
            }


async def fetch_meth_apy() -> float:
    """
    Estimate mETH APY from Mantle LSP contract.
    Calculates how much ETH 1 mETH is worth, then annualizes.
    """
    try:
        w3  = Web3(Web3.HTTPProvider(MANTLE_RPC_URL))
        lsp = w3.eth.contract(address=MANTLE_LSP_ADDRESS, abi=MANTLE_LSP_ABI)
        one_meth_in_wei = 10 ** 18
        eth_amount = lsp.functions.mETHToETH(one_meth_in_wei).call()
        ratio = eth_amount / 1e18  # e.g. 1.042 means 4.2% cumulative
        # Simplified: assume protocol running ~18 months, extrapolate annual
        estimated_apy = (ratio - 1.0) * 12 / 18 * 100
        return round(max(0, min(estimated_apy, 20.0)), 2)
    except Exception as e:
        print(f"[MacroSentinel] mETH APY fetch failed: {e}. Using default 4.2%.")
        return 4.2


async def fetch_usdy_yield() -> float:
    """
    USDY current annualized yield.
    Tries Ondo API first, falls back to Treasury rate proxy.
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                "https://api.ondo.finance/v1/products/usdy/yield",
                timeout=5
            )
            if resp.status_code == 200:
                return float(resp.json().get("apy", 4.85))
    except Exception:
        pass
    # Fallback: USDY pegs to US Treasury rate, currently ~4.5-5.2%
    return 4.85


async def fetch_btc_funding_rate() -> float:
    """Fetch BTC-USDT perpetual funding rate from Bybit."""
    api_key    = os.environ.get("BYBIT_API_KEY", "")
    api_secret = os.environ.get("BYBIT_SECRET", "")

    if not api_key or not api_secret:
        print("[MacroSentinel] Bybit API key missing. Using neutral funding rate.")
        return 0.0001

    try:
        timestamp  = str(int(time.time() * 1000))
        recv_window = "5000"
        query_str  = "category=linear&symbol=BTCUSDT&limit=1"
        sign_str   = timestamp + api_key + recv_window + query_str
        signature  = hmac.new(
            api_secret.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "X-BAPI-API-KEY":    api_key,
            "X-BAPI-TIMESTAMP":  timestamp,
            "X-BAPI-SIGN":       signature,
            "X-BAPI-RECV-WINDOW": recv_window,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BYBIT_BASE_URL}/v5/market/funding/history",
                params={"category": "linear", "symbol": "BTCUSDT", "limit": "1"},
                headers=headers
            )
            data = resp.json()
            entries = data.get("result", {}).get("list", [])
            if entries:
                return float(entries[0]["fundingRate"])
    except Exception as e:
        print(f"[MacroSentinel] Bybit funding rate failed: {e}.")

    return 0.0001  # neutral fallback


# -- Risk score computation ----------------------------------------------------

def compute_equity_momentum(prices: dict, prev_prices: Optional[dict]) -> str:
    """
    Compute equity momentum.
    If previous prices available, compute change; otherwise neutral.
    """
    if not prev_prices:
        return "neutral"

    changes = []
    for sym in ["SPY", "QQQ"]:
        if sym in prices and sym in prev_prices and prev_prices[sym] > 0:
            pct = (prices[sym] - prev_prices[sym]) / prev_prices[sym] * 100
            changes.append(pct)

    if not changes:
        return "neutral"

    avg_change = sum(changes) / len(changes)
    if avg_change > 1.0:
        return "bullish"
    elif avg_change < -1.0:
        return "bearish"
    return "neutral"


def compute_risk_score(
    equity_momentum: str,
    meth_apy: float,
    btc_funding_rate: float
) -> int:
    """
    Compute composite risk score (0-100, higher = more risk-on).

    Rules:
    - Baseline 50 (neutral)
    - Equity momentum bullish  -> +20
    - Equity momentum bearish  -> -20
    - mETH APY > 5%           -> +10 (strong ETH demand)
    - BTC funding rate > 0.02  -> +10 (overheated market)
    - BTC funding rate < -0.01 -> -15 (panic sentiment)
    """
    score = 50

    if equity_momentum == "bullish":
        score += 20
    elif equity_momentum == "bearish":
        score -= 20

    if meth_apy > 5.0:
        score += 10

    if btc_funding_rate > 0.02:
        score += 10
    elif btc_funding_rate < -0.01:
        score -= 15

    return max(0, min(100, score))


# -- Main function -------------------------------------------------------------

async def fetch_macro_signal(
    vault_address: str,
    previous_risk_score: int = 50,
    prev_prices: Optional[dict] = None
) -> MacroSignal:
    """
    Macro Sentinel main function.
    Concurrently fetches all data sources, assembles MacroSignal.
    """
    prices_task        = asyncio.create_task(fetch_pyth_prices())
    meth_apy_task      = asyncio.create_task(fetch_meth_apy())
    usdy_yield_task    = asyncio.create_task(fetch_usdy_yield())
    btc_funding_task   = asyncio.create_task(fetch_btc_funding_rate())

    prices, meth_apy, usdy_yield, btc_funding = await asyncio.gather(
        prices_task, meth_apy_task, usdy_yield_task, btc_funding_task
    )

    data_freshness_ok = bool(prices)

    equity_momentum = compute_equity_momentum(prices, prev_prices)
    risk_score      = compute_risk_score(equity_momentum, meth_apy, btc_funding)

    return MacroSignal(
        risk_score        = risk_score,
        equity_momentum   = equity_momentum,
        meth_apy          = meth_apy,
        usdy_yield        = usdy_yield,
        btc_funding_rate  = btc_funding,
        equity_prices     = prices,
        timestamp         = int(time.time()),
        data_freshness_ok = data_freshness_ok,
    )


# -- Standalone test -----------------------------------------------------------

if __name__ == "__main__":
    import json
    from dataclasses import asdict

    signal = asyncio.run(fetch_macro_signal("0xtest"))
    print(json.dumps(asdict(signal), indent=2))
