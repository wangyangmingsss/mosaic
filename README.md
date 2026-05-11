[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/wangyangmingsss/mosaic/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Mantle](https://img.shields.io/badge/Mantle-Chain_5000-8B5CF6)](https://mantle.xyz)
[![AI x RWA](https://img.shields.io/badge/Track-AI_x_RWA-10B981)](https://dorahacks.io/hackathon/mantleturingtesthackathon2026)
[![MuleRun](https://img.shields.io/badge/Agent-MuleRun-F59E0B)](https://mulerun.com)

# MOSAIC

**Five autonomous AI agents managing your real-world asset portfolio on Mantle. Every decision, permanently on-chain.**

> Demo site: https://mosaic-mantle.mule.page  
> Web Explorer: https://mosaic-explorer.mule.page  
> DoraHacks: https://dorahacks.io/hackathon/mantleturingtesthackathon2026

---

## Project Overview

MOSAIC is the first truly AI agent-driven RWA asset management protocol on Mantle.

Users deposit funds into an ERC-4626 vault, and MOSAIC's five collaborative agents — orchestrated by the MuleRun AI agent framework — immediately begin working 24/7: monitoring macro signals, computing optimal RWA allocations, executing tokenized equity trades via Fluxion Atomic RFQ, buying/selling USDY via Merchant Moe, and staking/unstaking mETH via Mantle LSP. Every rebalancing decision's complete reasoning chain (trigger conditions, macro data snapshot, LLM reasoning summary, execution records) is hashed with keccak256 and written to Mantle, with content stored on IPFS for anyone to verify.

**Why this matters:**  
Mantle has built the world's best on-chain RWA infrastructure — xStocks (tokenized equities), USDY (Treasury yield), mETH (ETH staking), fBTC (BTC restaking) are all live. But today's users must manually judge the macro environment, manually switch allocations, and manually monitor risk. MOSAIC fully automates this complex workflow while maintaining institutional-grade auditability.

**Core differentiators:**

- **xStocks-first integration**: MOSAIC is the first project to build AI agent strategies on Fluxion Atomic RFQ + xStocks tokenized equities, directly serving Mantle's newest strategic business line
- **True cross-asset management**: Equities + Treasuries + ETH staking + BTC yield, not a single-asset yield aggregator
- **Institutional decision audit trail**: Every rebalance fully recorded on-chain, compliance departments can actually audit
- **ERC-8004 agent reputation**: Each vault's agent instance accumulates traceable on-chain performance; reputation itself is a verifiable asset

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MOSAIC Architecture                               │
│                            Mantle Chain 5000                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   USER LAYER                                                                │
│   Web dApp ── Connect Wallet ── Select Risk Profile ── Deposit USDC        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SMART CONTRACT LAYER                                                      │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│   │   MosaicVault     │  │   DecisionLog     │  │   VaultFactory   │        │
│   │ ERC-4626 +       │  │ Immutable on-    │  │ One-click vault  │        │
│   │ ERC-8004 agent   │  │ chain decision   │  │ deployment +     │        │
│   │ identity NFT     │  │ hash registry    │  │ auth wiring      │        │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MULERUN AGENT PIPELINE  (15-minute cycle, off-chain orchestration)        │
│   ┌────────────────┐ ┌───────────────┐ ┌────────────────┐                 │
│   │ Macro Sentinel  │ │  Allocator    │ │Execution Router│                 │
│   │ Pyth + Chainlink│ │Black-Litterman│ │Fluxion RFQ     │                 │
│   │ Bybit + mETH   │ │+ LLM views   │ │Merchant Moe    │                 │
│   │ APY oracle     │ │Validates 10k │ │Mantle LSP      │                 │
│   │ risk_score 0-100│ │bps constraint│ │slip protection │                 │
│   └────────────────┘ └───────────────┘ └────────────────┘                 │
│   ┌────────────────┐ ┌───────────────┐                                     │
│   │  Risk Guardian  │ │Reporting Scribe│                                    │
│   │ VaR + liquidity │ │JSON → IPFS   │                                     │
│   │ concentration  │ │keccak256 hash│                                     │
│   │ 3-level alerts  │ │→ chain write │                                     │
│   └────────────────┘ └───────────────┘                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   PROTOCOL INTEGRATIONS                                                     │
│   Fluxion (xStocks Atomic RFQ) · Merchant Moe (USDY) · Mantle LSP (mETH)  │
│   Function (fBTC) · Agni Finance (liquidity) · Pyth · Chainlink · Bybit    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTEND                                                                  │
│   User dApp (deposit / dashboard)  ·  Web Explorer (public audit trail)    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---
## Smart Contract Architecture

All contracts written in Solidity ^0.8.26, deployed to Mantle via Foundry.

| Contract | Source | Description | Key Functions |
|----------|--------|-------------|---------------|
| **MosaicVault** | `contracts/src/MosaicVault.sol` | ERC-4626 vault + ERC-8004 agent identity extension. Holds user funds, records agent decisions, executes risk pauses. | `recordDecision()`, `fireRiskAlert()`, `resumeVault()`, `updateMetadataURI()` |
| **DecisionLog** | `contracts/src/DecisionLog.sol` | Immutable on-chain decision hash registry. Each record contains vault address, decision ID, recordHash (keccak256 of IPFS JSON), timestamp, block number. | `writeRecord()`, `getVaultHistory()`, `getTotalDecisions()` |
| **VaultFactory** | `contracts/src/VaultFactory.sol` | One-click new MosaicVault deployment: deploy → authorize in DecisionLog → transfer ownership to user. | `createVault()`, `totalVaults()` |

**MosaicVault Core Structs:**

```solidity
struct AgentIdentity {
    string  modelDeclaration;      // "mulerun-mosaic-v1"
    uint256 createdAt;
    uint256 totalDecisions;
    uint256 successfulRebalances;
    int256  cumulativePnLBps;      // vs benchmark
    string  metadataURI;           // IPFS link to full stats
}

struct Allocation {
    uint16 usdyBps;    // USDY weight in basis points
    uint16 xstocksBps; // xStocks aggregate weight
    uint16 methBps;    // mETH weight
    uint16 fbtcBps;    // fBTC weight
    uint16 usdcBps;    // USDC cash reserve
    // sum must always == 10000
}
```

**Deployment order (see `contracts/script/Deploy.s.sol`):**

```
DecisionLog → VaultFactory
VaultFactory.createVault() → MosaicVault (per user)
DecisionLog.authorizeVault(MosaicVault)
```

---
## On-Chain Deployment

Contracts deployed to **Mantle Testnet (Sepolia, Chain ID 5003)** for hackathon demo.

| Contract | Address |
|----------|---------|
| **DecisionLog** | `TBD — fill after deployment` |
| **VaultFactory** | `TBD — fill after deployment` |
| **MosaicVault #1 (Conservative)** | `TBD` |
| **MosaicVault #2 (Balanced)** | `TBD` |
| **MosaicVault #3 (Aggressive)** | `TBD` |

> Block Explorer: https://explorer.testnet.mantle.xyz

---
## MuleRun Agent Pipeline

Five agents orchestrated by MuleRun Agent Builder, each corresponding to an independent Skill ZIP.

### Agent 1 — Macro Sentinel
**Cycle**: Every 15 minutes | **Skill file**: `agents/src/skills/macro-sentinel/SKILL.md`

Pulls macro data from four sources and computes risk_score (0–100):
- **Pyth Network**: TSLAx, NVDAx, AAPLx, SPYx, QQQx real-time prices and 24h change
- **Mantle LSP**: mETH current staking APY
- **Ondo oracle**: USDY current yield
- **Bybit v5 API**: BTC funding rate (market sentiment indicator)

Output: `MacroSignal` JSON (risk_score, equity_momentum, meth_apy, usdy_yield, btc_funding_rate)

### Agent 2 — Allocator
**Trigger**: After Macro Sentinel completes | **Skill file**: `agents/src/skills/allocator/SKILL.md`

Modified Black-Litterman model with LLM (claude-sonnet-4-20250514) providing subjective market views:
1. Load base allocation for user's risk level
2. Build LLM prompt (includes MacroSignal + RiskProfile + current allocation + constraints)
3. LLM outputs target allocation + reasoning (strict validation: 5 weights must sum to 10000)
4. Retry up to 3 times on failure; fall back to base allocation after 3 failures

### Agent 3 — Execution Router
**Trigger**: After Allocator completes | **Skill file**: `agents/src/skills/execution-router/SKILL.md`

Computes deltas, filters dust (< 50 bps), routes to optimal protocol:
- **xStocks delta** → Fluxion Atomic RFQ (market hours) / Fluxion AMM (after hours)
- **USDY delta** → Merchant Moe USDY/USDC liquidity pool
- **mETH delta** → Mantle LSP `stake()` / `unstake()`
- **fBTC delta** → Function fBTC vault `deposit()` / `withdraw()`

All trades undergo mandatory `eth_call` simulation before execution; failed simulations are skipped.

### Agent 4 — Risk Guardian
**Trigger**: Every Macro Sentinel cycle | **Skill file**: `agents/src/skills/risk-guardian/SKILL.md`

Four-dimensional risk check, returns alert_level 0–3:

| Dimension | Level 2 Trigger | Level 3 Trigger |
|-----------|----------------|----------------|
| Concentration | Single asset > maxSingleAssetBps | Single asset > maxSingleAssetBps × 1.1 |
| Max Drawdown | 30-day drawdown > maxDrawdownBps | 30-day drawdown > maxDrawdownBps × 1.5 |
| Liquidity | Instantly liquidatable assets < 25% | Instantly liquidatable assets < 15% |
| Macro Stress | risk_score < 20 | risk_score < 10 |

Level >= 2: Calls `vault.fireRiskAlert(level, reason)` to write on-chain event  
Level 3: Pauses all new vault deposits until owner manually calls `resumeVault()`

### Agent 5 — Reporting Scribe
**Trigger**: After execution completes | **Skill file**: `agents/src/skills/reporting-scribe/SKILL.md`

1. Assembles `DecisionRecord` JSON (includes MacroSignal, before/after allocations, reasoning, txs, risk assessment)
2. Uploads to IPFS (Pinata), obtains CID
3. Computes keccak256 hash of the JSON
4. Calls `MosaicVault.recordDecision(recordHash, newAlloc, pnlDeltaBps)` to write to Mantle
5. Calls `vault.updateMetadataURI("ipfs://CID")` to update ERC-8004 metadata

**DecisionRecord JSON Example:**
```json
{
  "schema_version": "1.0",
  "vault_address": "0x...",
  "decision_id": 47,
  "timestamp": 1747012800,
  "trigger": "macro_signal_shift",
  "macro_snapshot": {
    "risk_score": 58,
    "equity_momentum": "neutral",
    "meth_apy": 4.2,
    "usdy_yield": 4.85,
    "btc_funding_rate": 0.0003
  },
  "previous_allocation": {"usdy_bps": 3000, "xstocks_bps": 3000, "meth_bps": 2500, "fbtc_bps": 1000, "usdc_bps": 500},
  "target_allocation":   {"usdy_bps": 4000, "xstocks_bps": 2500, "meth_bps": 2500, "fbtc_bps": 500,  "usdc_bps": 500},
  "reasoning_summary": "Equity momentum weakening; rotating 10pp from xStocks to USDY for defensive yield.",
  "execution_txs": ["0xabc...", "0xdef..."],
  "pnl_delta_bps": 12,
  "agent_model": "mulerun-mosaic-v1"
}
```

---
## MuleRun Agent Builder Configuration

MOSAIC uses MuleRun Agent Builder to deploy five collaborative agents.

### Agent Settings

**AGENTS.md location**: `agents/AGENTS.md`

| Field | Value |
|-------|-------|
| Agent Name | Mosaic RWA Portfolio Agent |
| Primary Skills | macro-sentinel, allocator, execution-router, risk-guardian, reporting-scribe |
| Run Mode | Scheduled (15-minute interval) |
| Environment Variables | See `.env.example` |

### Skills ZIP Structure

Each skill is packaged as a ZIP and uploaded to MuleRun Agent Builder:

```
macro-sentinel.zip
└── macro-sentinel/
    ├── SKILL.md                        ← Required: skill instructions
    ├── scripts/
    │   └── fetch_macro.py              ← Actual execution script
    └── references/
        ├── pyth_price_ids.json         ← Pyth price feed IDs
        ├── contract_addresses.json     ← Mantle protocol addresses
        └── bybit_api.md                ← Bybit v5 authentication guide
```

### MCP Configuration (Advanced Settings)

In MuleRun Agent Builder → Settings → MCP, add:
- **Mantle RPC MCP**: Connects to Mantle node, agent can call contracts directly
- **Pinata MCP**: IPFS upload (requires Pinata JWT)
- **Bybit MCP**: Market data + trade execution

---
## Quick Start

### Prerequisites

- [Foundry](https://book.getfoundry.sh/) (Solidity compilation and testing)
- Python >= 3.11 (agent runtime)
- [MuleRun account](https://mulerun.com) (agent deployment)

### 1. Clone the repository

```bash
git clone https://github.com/wangyangmingsss/mosaic.git
cd mosaic
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in all required variables (see Environment Variables section below)
```

### 3. Compile and test contracts

```bash
cd contracts

# Install OpenZeppelin dependencies
forge install OpenZeppelin/openzeppelin-contracts --no-commit
forge install foundry-rs/forge-std --no-commit

# Compile
forge build

# Run tests (with gas report)
forge test -vvv --gas-report
```

### 4. Deploy to Mantle Testnet

```bash
source .env

forge script script/Deploy.s.sol:Deploy \
  --rpc-url $MANTLE_RPC_TESTNET \
  --broadcast \
  --legacy

# Fill the output contract addresses into .env:
# DECISION_LOG_ADDRESS=0x...
# VAULT_FACTORY_ADDRESS=0x...
```

### 5. Install agent dependencies

```bash
cd ../agents
pip install -r requirements.txt
```

### 6. Create a test vault

```bash
cd agents
python scripts/create_vault.py \
  --risk-level 2 \
  --rebalance-frequency 2 \
  --max-drawdown 1500 \
  --max-single-asset 6000
# Output: Vault deployed at 0x...
```

### 7. Start the agent pipeline

```bash
# Using MuleRun platform (recommended)
# 1. Package skills: python scripts/pack_skills.py
# 2. Upload agents/AGENTS.md + 5 skill ZIPs in MuleRun Agent Builder
# 3. Click "Initialize Agent" → "Launch Agent"

# Or run locally (for development)
python src/mosaic_pipeline.py --vault 0xYourVaultAddress
```

### 8. View Dashboard

```bash
# Web Explorer (public, no login required)
open https://mosaic-explorer.mule.page

# Or local frontend
cd frontend && npm install && npm run dev
```

---
## Project Structure

```
mosaic/
├── .env.example                          # Environment variable template
├── .gitignore
├── README.md
│
├── .github/
│   └── workflows/
│       └── ci.yml                        # Foundry tests + Python lint + tests
│
├── contracts/                            # Solidity smart contracts (Foundry)
│   ├── foundry.toml
│   ├── script/
│   │   └── Deploy.s.sol                  # Full deployment script
│   ├── src/
│   │   ├── MosaicVault.sol               # ERC-4626 + ERC-8004 vault
│   │   ├── DecisionLog.sol               # On-chain decision hash registry
│   │   ├── VaultFactory.sol              # One-click vault deployment
│   │   └── interfaces/
│   │       └── IDecisionLog.sol
│   └── test/
│       └── MosaicVault.t.sol             # Foundry test suite
│
├── agents/                               # MuleRun agent pipeline (Python)
│   ├── AGENTS.md                         # MuleRun agent instruction file
│   ├── requirements.txt
│   └── src/
│       ├── mosaic_pipeline.py            # Main orchestration loop
│       ├── config.py                     # Contract addresses + ABI + network config
│       └── skills/
│           ├── macro-sentinel/
│           │   └── SKILL.md              # Macro data collection skill
│           ├── allocator/
│           │   └── SKILL.md              # Black-Litterman + LLM allocation skill
│           ├── execution-router/
│           │   └── SKILL.md              # On-chain trade execution skill
│           ├── risk-guardian/
│           │   └── SKILL.md              # Risk monitoring + on-chain alert skill
│           └── reporting-scribe/
│               └── SKILL.md              # IPFS archival + on-chain record skill
│
└── frontend/                             # React dApp
    ├── src/
    │   ├── components/
    │   │   ├── VaultCard.tsx
    │   │   ├── AllocationPieChart.tsx
    │   │   ├── DecisionHistory.tsx
    │   │   └── AgentStatusPanel.tsx
    │   ├── hooks/
    │   │   ├── useVault.ts
    │   │   └── useDecisionLog.ts
    │   └── lib/
    │       └── mantle.ts                 # wagmi/viem Mantle config
    └── public/
```

---
## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MANTLE_RPC_URL` | Yes | Mantle mainnet RPC (`https://rpc.mantle.xyz`) |
| `AGENT_PRIVATE_KEY` | Yes | Agent EOA private key for signing on-chain transactions |
| `AGENT_EOA` | Yes | Agent wallet address (public) |
| `DECISION_LOG_ADDRESS` | Yes | DecisionLog contract address (fill after deployment) |
| `VAULT_FACTORY_ADDRESS` | Yes | VaultFactory contract address (fill after deployment) |
| `BYBIT_API_KEY` | Yes | Bybit v5 API key (BTC funding rate + data) |
| `BYBIT_SECRET` | Yes | Bybit API secret |
| `PINATA_JWT` | Yes | Pinata JWT token (IPFS upload) |
| `ANTHROPIC_API_KEY` | Yes | Claude API key (Allocator LLM) |
| `FLUXION_API_KEY` | Optional | Fluxion Atomic RFQ API (has fallback) |
| `MANTLE_EXPLORER_KEY` | Optional | Mantle Explorer API (for contract verification) |
| `DRY_RUN` | Optional | `true` to simulate without broadcasting transactions (for testing) |

---
## Running the Demo

### Local Demo (no on-chain transactions)

```bash
cd agents
python src/mosaic_pipeline.py --vault 0xMockAddress --dry-run
```

Observe console output:

```
2026-05-11T10:00:00 [Mosaic] INFO Mosaic Pipeline starting for vault 0x1234...
2026-05-11T10:00:01 [Mosaic] INFO Vault TVL: $10,000.00 | Risk level: 2
2026-05-11T10:00:02 [Mosaic] INFO MacroSignal: risk_score=62 | equity=bullish | mETH=4.25% | fresh=True
2026-05-11T10:00:02 [Mosaic] INFO Rebalance triggered: initial
2026-05-11T10:00:02 [Mosaic] INFO RiskAssessment: alert_level=0 | []
2026-05-11T10:00:03 [Mosaic] INFO Allocator: Equity momentum strong; increasing xStocks 5pp. | confidence=0.82
2026-05-11T10:00:05 [Mosaic] INFO Execution: 3 trades | ok=True | txs=['0xabc...', '0xdef...', '0x123...']
2026-05-11T10:00:06 [Mosaic] INFO Scribe: IPFS=QmXyz... | hash=0x4a2f8c1b9e... | chain_tx=0x789...
2026-05-11T10:00:06 [Mosaic] INFO ✓ Cycle 1 complete. Vault: 0x1234... | Record #1
```

### Three-Vault Parallel Demo (recommended for hackathon)

```bash
# Launch three vaults with different risk levels for diversified data
python src/mosaic_pipeline.py --vault $VAULT_CONSERVATIVE &
python src/mosaic_pipeline.py --vault $VAULT_BALANCED &
python src/mosaic_pipeline.py --vault $VAULT_AGGRESSIVE &
```

Three vaults start running from `Week 3 (May 25)`, accumulating **18–21 days of real on-chain decision data** by Demo Day.

---
## Economic Loop

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MOSAIC Value Loop                                    │
│                                                                              │
│  User deposits USDC                                                          │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────┐   MacroSignal   ┌─────────────┐   target alloc             │
│  │Macro Sentinel│ ──────────────> │  Allocator   │ ─────────────┐           │
│  │15min cycle   │                 │LLM + BL model│              │           │
│  └─────────────┘                 └─────────────┘              ▼           │
│                                                        ┌─────────────┐     │
│                                                        │  Execution   │     │
│  ┌─────────────┐ risk check     ┌─────────────┐       │  Router      │     │
│  │Risk Guardian │ ─────────────> │  MosaicVault │ <──── │  Fluxion RFQ│     │
│  │VaR monitor   │                │  ERC-4626   │       │  MerchantMoe│     │
│  │3-level alert │                │  ERC-8004   │       │  Mantle LSP │     │
│  └─────────────┘                └──────┬──────┘       └─────────────┘     │
│                                        │                                    │
│                                        │ recordDecision()                   │
│                                        ▼                                    │
│                               ┌─────────────┐  IPFS JSON  ┌─────────────┐ │
│                               │ DecisionLog  │ <────────── │  Reporting  │ │
│                               │ on-chain     │             │  Scribe     │ │
│                               │ hash registry│             │  Pinata     │ │
│                               └─────────────┘             └─────────────┘ │
│                                        │                                    │
│                                        ▼                                    │
│                               Web Explorer (public audit trail)             │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Asset Flow:**
- User funds → MosaicVault (held via ERC-4626)
- Execution Router calls protocol contracts to complete asset allocation
- USDY Treasury yield, mETH staking yield, and xStocks price exposure auto-compound within the vault
- Every rebalance record permanently stored on Mantle + IPFS

---
## Security Model

### Pre-Execution Simulation
Execution Router simulates every transaction via `eth_call` before broadcast; failed simulations are skipped — no broadcast, no gas consumed.

### Risk Pause Mechanism
After Risk Guardian triggers Level 3, MosaicVault automatically rejects all new `deposit()` and `mint()` calls (ReentrancyGuard protected) until the vault owner calls `resumeVault()`.

### Agent Error Isolation
The main pipeline loop wraps every cycle in try/catch. A single skill invocation failure never stops the pipeline; failed skill outputs are replaced by fallback values, and the on-chain decision record logs `error_flag: true`.

### Private Key Protection
`AGENT_PRIVATE_KEY` only exists in `.env` and MuleRun's encrypted environment variables — never appears in logs or on-chain data. All logs only record the EOA address.

### Anti-Replay
The DecisionLog contract enforces uniqueness checks per recordHash (`mapping(bytes32 => bool) public recordExists`); the same hash cannot be written twice.

---
## Contribution to the Mantle Ecosystem

| Mantle Metric | MOSAIC's Impact |
|---------------|-----------------|
| xStocks TVL | Every balanced/aggressive vault continuously buys xStocks, directly increasing Fluxion xStocks trading volume and TVL |
| USDY TVL | Conservative vaults hold up to 50% USDY, continuously contributing USDY liquidity |
| mETH Staking | Every vault holds at least 20% mETH, increasing Mantle LSP staking volume |
| Fluxion Volume | Execution Router prioritizes Fluxion Atomic RFQ, contributing volume on every xStocks rebalance |
| Merchant Moe Liquidity | USDY/USDC rebalances route through Merchant Moe, increasing pool utilization |
| ERC-8004 Usage | MOSAIC is the first practically meaningful extension application of ERC-8004 agent identity |

---
## Roadmap

**v1 (Current — Hackathon Version)**
- All five agents fully implemented, running 24/7
- Supports USDY, xStocks (SPYx, NVDAx), mETH, fBTC, USDC
- On-chain decision records + Web Explorer

**v2 (Post-Hackathon)**
- Copy Vault: One-click copy of high-reputation agent's historically optimal strategy
- xPoints integration: Mantle xStocks ecosystem incentives flow directly to MOSAIC users
- More xStocks instruments (TSLAx, AAPLx, METAx, GOOGLx)

**v3 (Long-term)**
- Institutional white-label: Family offices can deploy private MOSAIC instances with custom strategy templates
- Cross-chain expansion: Support Solana-side assets via Mantle Super Portal
- Community strategy marketplace: Developers can publish custom allocator strategies

---
## Team

| Role | Account |
|------|---------|
| Solo Developer | **wangyangmingssssss** |

Built for the Mantle Turing Test Hackathon 2026.  
Five agents. Three contracts. One truly autonomous on-chain RWA asset management protocol.

---
## License

MIT License. SPDX declarations in each source file.

```
SPDX-License-Identifier: MIT
```
