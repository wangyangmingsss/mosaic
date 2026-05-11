"""
config.py — Mantle network configuration and contract addresses for Mosaic.
All addresses are Mantle mainnet (chain ID 5000) unless otherwise noted.
"""

import os

# ── Network ───────────────────────────────────────────────────────────────────

MANTLE_CHAIN_ID        = 5000
MANTLE_RPC_MAINNET     = "https://rpc.mantle.xyz"
MANTLE_RPC_TESTNET     = "https://rpc.sepolia.mantle.xyz"
MANTLE_EXPLORER        = "https://explorer.mantle.xyz"

MANTLE_RPC_URL = os.environ.get("MANTLE_RPC_URL", MANTLE_RPC_MAINNET)

# ── Deployed Mosaic contracts (filled in after Deploy.s.sol runs) ─────────────

DECISION_LOG_ADDRESS   = os.environ.get("DECISION_LOG_ADDRESS",   "0x035a459893EC171615B2Fd747d3EDd1eB0A5526D")
VAULT_FACTORY_ADDRESS  = os.environ.get("VAULT_FACTORY_ADDRESS",  "0xCc0c3F76A8eF1E31B8e7BE83BB4EFcF60Ea1C79A")
BENCHMARK_TRACKER_ADDRESS = os.environ.get("BENCHMARK_TRACKER_ADDRESS", "0xa7E9bF736af06E6E6eFe5E0cA86e7c67BD6A7d57")

# ── 代币地址（Mantle Mainnet, Chain ID 5000）────────────────────────────────

USDC_ADDRESS  = "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9"  # Bridged USDC
METH_ADDRESS  = "0xcDA86A272531e8640cD7F1a92c01839911B90bb0"  # mETH
WETH_ADDRESS  = "0xdEAddEaDdeadDEadDEADDEAddEADDEAddead1111"  # WETH
MNT_ADDRESS   = "0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8"  # MNT
USDY_ADDRESS  = "0x5bE26527e817998A7206475496fDE1E68957c5A6"  # USDY (Ondo)
FBTC_ADDRESS  = "0xC96dE26018A54D51c097160568752c4E3BD6C364"  # fBTC (Function)
USDT_ADDRESS  = "0x201EBa5CC46D216Ce6DC03F6a759e8E766e956aE"  # USDT

# xStocks tokens (via BackedFi + xStocks)
# TODO: fill from xStocks official page https://xstocks.com/tokens
# or search Mantle Explorer https://explorer.mantle.xyz/tokens-erc20
XSTOCKS_TOKENS = {
    "TSLAx": "0x...",   # TODO: search Mantle Explorer for TSLAx
    "NVDAx": "0x...",   # TODO: search Mantle Explorer for NVDAx
    "AAPLx": "0x...",   # TODO: search Mantle Explorer for AAPLx
    "SPYx":  "0x...",   # TODO: search Mantle Explorer for SPYx
    "QQQx":  "0x...",   # TODO: search Mantle Explorer for QQQx
}

# Legacy aliases for backward compatibility
TSLA_X_ADDRESS = XSTOCKS_TOKENS["TSLAx"]
NVDA_X_ADDRESS = XSTOCKS_TOKENS["NVDAx"]
AAPL_X_ADDRESS = XSTOCKS_TOKENS["AAPLx"]
SPY_X_ADDRESS  = XSTOCKS_TOKENS["SPYx"]
QQQ_X_ADDRESS  = XSTOCKS_TOKENS["QQQx"]

# ── Mantle LSP（mETH 质押协议）────────────────────────────────────────────────

MANTLE_LSP_ADDRESS = "0xe3cBd06D7dadB3F4e6557bAb7EdD924CD1489E8f"

# ── Protocol contracts ───────────────────────────────────────────────────────

# Merchant Moe LBRouter v2.2 (Mantle Mainnet, verified)
MERCHANT_MOE_LB_ROUTER      = "0x013e138EF6008ae5FDFDE29700e3f2Bc61d21E3a"
MERCHANT_MOE_ROUTER_ADDRESS = MERCHANT_MOE_LB_ROUTER

# Fluxion Router (Mantle Mainnet, verified)
FLUXION_ROUTER_ADDRESS = "0x5628a59dF0ECAC3f3171f877A94bEb26BA6DFAa0"
FLUXION_RFQ_ADDRESS    = "0x5628a59dF0ECAC3f3171f877A94bEb26BA6DFAa0"  # Atomic RFQ

# Function fBTC Factory Contract / Vault (Mantle Mainnet, verified)
FUNCTION_FBTC_VAULT_ADDRESS = "0x4697F9b54Bf24776b81f42A5E2Da81FBA3763bA4"

# Agni Finance SwapRouter (Mantle Mainnet, verified)
AGNI_ROUTER_ADDRESS = "0x319B69888b0d11cEC22caA5034e25FfFBDc88421"

# ── Pyth Network Oracle（Mantle 主网）─────────────────────────────────────────

PYTH_MANTLE_ADDRESS = "0xA2aa501b19aff244D90cc15a4Cf739D2725B5729"
USDY_ORACLE_ADDRESS = "0x..."   # TODO: Ondo yield oracle

# ── ABIs (minimal — full ABIs in agents/src/abis/) ──────────────────────────

VAULT_ABI = [
    {"name": "recordDecision",   "type": "function", "inputs": [
        {"name": "recordHash",  "type": "bytes32"},
        {"name": "newAlloc",    "type": "tuple",
         "components": [
             {"name": "usdyBps",    "type": "uint16"},
             {"name": "xstocksBps", "type": "uint16"},
             {"name": "methBps",    "type": "uint16"},
             {"name": "fbtcBps",    "type": "uint16"},
             {"name": "usdcBps",    "type": "uint16"},
         ]},
        {"name": "pnlDeltaBps", "type": "int256"}
    ], "outputs": [], "stateMutability": "nonpayable"},

    {"name": "fireRiskAlert", "type": "function", "inputs": [
        {"name": "level",  "type": "uint8"},
        {"name": "reason", "type": "string"}
    ], "outputs": [], "stateMutability": "nonpayable"},

    {"name": "updateMetadataURI", "type": "function", "inputs": [
        {"name": "uri", "type": "string"}
    ], "outputs": [], "stateMutability": "nonpayable"},

    {"name": "getAllocation", "type": "function", "inputs": [], "outputs": [
        {"name": "", "type": "tuple",
         "components": [
             {"name": "usdyBps",    "type": "uint16"},
             {"name": "xstocksBps", "type": "uint16"},
             {"name": "methBps",    "type": "uint16"},
             {"name": "fbtcBps",    "type": "uint16"},
             {"name": "usdcBps",    "type": "uint16"},
         ]}
    ], "stateMutability": "view"},

    {"name": "riskProfile", "type": "function", "inputs": [], "outputs": [
        {"name": "riskLevel",          "type": "uint8"},
        {"name": "rebalanceFrequency", "type": "uint8"},
        {"name": "maxDrawdownBps",     "type": "uint16"},
        {"name": "maxSingleAssetBps",  "type": "uint16"},
    ], "stateMutability": "view"},

    {"name": "totalAssets", "type": "function", "inputs": [], "outputs": [
        {"name": "", "type": "uint256"}
    ], "stateMutability": "view"},

    {"name": "agentIdentity", "type": "function", "inputs": [], "outputs": [
        {"name": "modelDeclaration",   "type": "string"},
        {"name": "createdAt",          "type": "uint256"},
        {"name": "totalDecisions",     "type": "uint256"},
        {"name": "successfulRebalances","type": "uint256"},
        {"name": "cumulativePnLBps",   "type": "int256"},
        {"name": "metadataURI",        "type": "string"},
    ], "stateMutability": "view"},

    # Events
    {"name": "AgentRebalanced", "type": "event", "inputs": [
        {"name": "decisionId", "type": "uint256", "indexed": True},
        {"name": "recordHash", "type": "bytes32",  "indexed": False},
    ]},
    {"name": "RiskAlertFired", "type": "event", "inputs": [
        {"name": "alertLevel", "type": "uint8",   "indexed": False},
        {"name": "reason",     "type": "string",  "indexed": False},
    ]},
]

# ── Pyth price feed IDs for Mantle xStocks ────────────────────────────────────
# Source: https://pyth.network/developers/price-feed-ids

PYTH_PRICE_IDS = {
    "TSLAx": "0x16dad506d7db8da01c87581c87ca897a012a153557d4d578c3b9c9e1bc0632f1",
    "NVDAx": "0x16dad506d7db8da01c87581c87ca897a012a153557d4d578c3b9c9e1bc0632f1",  # TODO verify
    "AAPLx": "0x49f6b65cb1de6b10468b27191e46d58d72c03f7be5a573c47e3a2ac7e2e9d28a",
    "SPYx":  "0x19e09bb805456ada3979a7d1cbb4b6d63babc3a0f8e8a9509f68afa5c1c76c4a",
    "QQQx":  "0x28ce9e26b83c33e77f7e98615c6e4e9a4ea0ec38dc4e1fbb8de4c432ee36b3fd",
    "ETH":   "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "BTC":   "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
}
