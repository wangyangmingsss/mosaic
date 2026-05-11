[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/wangyangmingsss/mosaic/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Mantle](https://img.shields.io/badge/Mantle-Chain_5000-8B5CF6)](https://mantle.xyz)
[![AI x RWA](https://img.shields.io/badge/Track-AI_x_RWA-10B981)](https://dorahacks.io/hackathon/mantleturingtesthackathon2026)
[![MuleRun](https://img.shields.io/badge/Agent-MuleRun-F59E0B)](https://mulerun.com)

# MOSAIC

**Five autonomous AI agents managing your real-world asset portfolio on Mantle. Every decision, permanently on-chain.**

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

---

## MuleRun Agent Pipeline

Five agents orchestrated by MuleRun Agent Builder, each corresponding to an independent Skill ZIP.

### Agent 1 — Macro Sentinel
**Cycle**: Every 15 minutes | **Skill file**: `agents/src/skills/macro-sentinel/SKILL.md`

### Agent 2 — Allocator
**Trigger**: After Macro Sentinel completes | **Skill file**: `agents/src/skills/allocator/SKILL.md`

### Agent 3 — Execution Router
**Trigger**: After Allocator completes | **Skill file**: `agents/src/skills/execution-router/SKILL.md`

### Agent 4 — Risk Guardian
**Trigger**: Every Macro Sentinel cycle | **Skill file**: `agents/src/skills/risk-guardian/SKILL.md`

### Agent 5 — Reporting Scribe
**Trigger**: After execution completes | **Skill file**: `agents/src/skills/reporting-scribe/SKILL.md`

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
# Fill in all required variables
```

### 3. Compile and test contracts

```bash
cd contracts
forge install OpenZeppelin/openzeppelin-contracts --no-commit
forge install foundry-rs/forge-std --no-commit
forge build
forge test -vvv --gas-report
```

### 4. Deploy to Mantle Testnet

```bash
source .env
forge script script/Deploy.s.sol:Deploy \
  --rpc-url $MANTLE_RPC_TESTNET \
  --broadcast \
  --legacy
```

### 5. Install agent dependencies

```bash
cd ../agents
pip install -r requirements.txt
```

### 6. Start agent pipeline

```bash
python src/mosaic_pipeline.py --vault 0xYourVaultAddress
```

---

## Project Structure

```
mosaic/
├── .env.example
├── .gitignore
├── README.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── contracts/
│   ├── foundry.toml
│   ├── script/
│   │   └── Deploy.s.sol
│   ├── src/
│   │   ├── MosaicVault.sol
│   │   ├── DecisionLog.sol
│   │   ├── VaultFactory.sol
│   │   └── interfaces/
│   │       └── IDecisionLog.sol
│   └── test/
│       └── MosaicVault.t.sol
├── agents/
│   ├── AGENTS.md
│   ├── requirements.txt
│   └── src/
│       ├── mosaic_pipeline.py
│       ├── config.py
│       └── skills/
│           ├── macro-sentinel/
│           │   └── SKILL.md
│           ├── allocator/
│           │   └── SKILL.md
│           ├── execution-router/
│           │   └── SKILL.md
│           ├── risk-guardian/
│           │   └── SKILL.md
│           └── reporting-scribe/
│               └── SKILL.md
```

---

## Security Model

- **Pre-execution simulation**: Every transaction simulated via `eth_call` before broadcast
- **Risk pause mechanism**: Level 3 alert auto-rejects all `deposit()` and `mint()` calls
- **Agent error isolation**: Each cycle wrapped in try/catch; one skill failure never stops the pipeline
- **Private key protection**: `AGENT_PRIVATE_KEY` only exists in `.env` and MuleRun encrypted env vars
- **Anti-replay**: DecisionLog enforces uniqueness per recordHash

---

## License

MIT License. SPDX declarations in each source file.
