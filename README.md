[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/wangyangmingsss/mosaic/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Mantle](https://img.shields.io/badge/Mantle-Chain_5000-8B5CF6)](https://mantle.xyz)
[![AI x RWA](https://img.shields.io/badge/Track-AI_x_RWA-10B981)](https://dorahacks.io/hackathon/mantleturingtesthackathon2026)
[![MuleRun](https://img.shields.io/badge/Agent-MuleRun-F59E0B)](https://mulerun.com)

# MOSAIC

**Five autonomous AI agents managing your real-world asset portfolio on Mantle. Every decision, permanently on-chain.**

MOSAIC deploys USDY Treasury yield and mETH liquid staking as its primary allocation targets, composing them with cmETH restaking derivatives and fBTC Bitcoin yield into a fully automated, compliance-aware portfolio managed by collaborative AI agents on Mantle. The protocol's V2 upgrade introduces protocol adapters, ERC-8004 agent identity registries, and the cmETH restaking risk premium as a core alpha source.

> Demo site: https://mosaic-mantle.mule.page  
> Web Explorer: https://mosaic-explorer.mule.page  
> DoraHacks: https://dorahacks.io/hackathon/mantleturingtesthackathon2026

---

## Live on Mantle Mainnet

Contracts deployed to **Mantle Mainnet (Chain ID 5000)**.

### V2 Contracts

| Contract | Address | Explorer |
|----------|---------|----------|
| **IdentityRegistry** | `0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95` | [View](https://explorer.mantle.xyz/address/0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95) |
| **ReputationRegistry** | `0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9` | [View](https://explorer.mantle.xyz/address/0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9) |
| **ValidationRegistry** | `0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d` | [View](https://explorer.mantle.xyz/address/0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d) |
| **DecisionLog V2** | `0xB123cE88e8b1b8de606574BbA99b655D0D456994` | [View](https://explorer.mantle.xyz/address/0xB123cE88e8b1b8de606574BbA99b655D0D456994) |
| **VaultFactory V2** | `0x2CF55485f0B8371213DA74c90da8b3F9791e633A` | [View](https://explorer.mantle.xyz/address/0x2CF55485f0B8371213DA74c90da8b3F9791e633A) |
| **USDYAdapter** | `0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0` | [View](https://explorer.mantle.xyz/address/0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0) |
| **METHAdapter** | `0xcAae1dBf111aF26655A4f40eaC4792978d3249c8` | [View](https://explorer.mantle.xyz/address/0xcAae1dBf111aF26655A4f40eaC4792978d3249c8) |
| **CMETHAdapter** | `0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643` | [View](https://explorer.mantle.xyz/address/0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643) |
| **FBTCAdapter** | `0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D` | [View](https://explorer.mantle.xyz/address/0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D) |
| **Conservative V2** | `0xF3Df82262522307C6442137F24dA6710B182AE8b` | [View](https://explorer.mantle.xyz/address/0xF3Df82262522307C6442137F24dA6710B182AE8b) |
| **Balanced V2** | `0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA` | [View](https://explorer.mantle.xyz/address/0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA) |
| **Aggressive V2** | `0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625` | [View](https://explorer.mantle.xyz/address/0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625) |

### V1 Contracts (Legacy)

| Contract | Address | Explorer |
|----------|---------|----------|
| **DecisionLog** | `0x035a459893EC171615B2Fd747d3EDd1eB0A5526D` | [View](https://explorer.mantle.xyz/address/0x035a459893EC171615B2Fd747d3EDd1eB0A5526D) |
| **VaultFactory** | `0xCc0c3F76A8eF1E31B8e7BE83BB4EFcF60Ea1C79A` | [View](https://explorer.mantle.xyz/address/0xCc0c3F76A8eF1E31B8e7BE83BB4EFcF60Ea1C79A) |
| **BenchmarkTracker** | `0xa7E9bF736af06E6E6eFe5E0cA86e7c67BD6A7d57` | [View](https://explorer.mantle.xyz/address/0xa7E9bF736af06E6E6eFe5E0cA86e7c67BD6A7d57) |
| **MosaicVault #1 (Conservative)** | `0x075849a9Ce4b977B14462068774526f890EF56C4` | [View](https://explorer.mantle.xyz/address/0x075849a9Ce4b977B14462068774526f890EF56C4) |
| **MosaicVault #2 (Balanced)** | `0x51774634376596957Ef63F4560F05e08c7fc4779` | [View](https://explorer.mantle.xyz/address/0x51774634376596957Ef63F4560F05e08c7fc4779) |
| **MosaicVault #3 (Aggressive)** | `0xF0b19b1577E614CCB813F5800AA49Eb9b763B234` | [View](https://explorer.mantle.xyz/address/0xF0b19b1577E614CCB813F5800AA49Eb9b763B234) |

> Block Explorer: https://explorer.mantle.xyz

---

## Project Overview

MOSAIC is the first truly AI agent-driven RWA asset management protocol on Mantle.

Users deposit funds into an ERC-4626 vault, and MOSAIC's five collaborative agents -- orchestrated by the MuleRun AI agent framework -- immediately begin working 24/7: monitoring macro signals, computing optimal RWA allocations across the USDY yield curve and mETH/cmETH restaking spread, executing trades via Merchant Moe and Mantle LSP, and staking/unstaking through protocol adapters. Every rebalancing decision's complete reasoning chain (trigger conditions, macro data snapshot, LLM reasoning summary, execution records) is hashed with keccak256 and written to Mantle, with content stored on IPFS for anyone to verify.

**Why this matters:**  
Mantle has built the world's best on-chain RWA infrastructure -- USDY (Treasury yield), mETH (ETH staking), cmETH (restaking), fBTC (BTC yield) are all live. But today's users must manually judge the macro environment, manually switch allocations, and manually monitor risk. MOSAIC fully automates this complex workflow while maintaining institutional-grade auditability.

**Core differentiators:**

- **USDY yield curve + mETH/cmETH restaking arbitrage**: MOSAIC is the first project to build AI agent strategies that actively price the restaking risk premium and exploit Treasury yield curve dynamics on Mantle
- **True cross-asset management**: Treasuries + ETH staking + ETH restaking + BTC yield, not a single-asset yield aggregator
- **Institutional decision audit trail**: Every rebalance fully recorded on-chain, compliance departments can actually audit
- **ERC-8004 agent reputation**: Each vault's agent instance accumulates traceable on-chain performance; reputation itself is a verifiable asset

---

## ERC-8004 Registry

MOSAIC is the first production deployment of ERC-8004 agent identity on Mantle. The registry system provides three composable contracts that together establish a verifiable, on-chain identity and reputation layer for autonomous agents.

**IdentityRegistry** (`0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95`): Mints a soulbound NFT for each agent instance. The token metadata URI points to IPFS, containing the agent's model declaration, capability set, and deployment configuration. Identity tokens are non-transferable and can only be revoked by the registry owner.

**ReputationRegistry** (`0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9`): Accumulates on-chain performance metrics for each registered agent. After every successful rebalance cycle, the Reporting Scribe calls `updateReputation(agentId, pnlDeltaBps, decisionCount)` to update the agent's track record. External protocols can query an agent's cumulative PnL, decision count, and success rate before trusting its outputs.

**ValidationRegistry** (`0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d`): Stores validation attestations from third-party auditors. Validators can attest that a given agent's decision-making process meets specific criteria (e.g., "never exceeds 60% concentration", "always runs pre-flight simulation"). These attestations are queryable on-chain by any consumer.

See `docs/examples/agent-registration.json` for a complete ERC-8004 registration payload example.

---

## Protocol Adapter Architecture

V2 introduces a modular adapter pattern that isolates protocol-specific logic from the core vault and agent pipeline. Each supported asset has a dedicated adapter contract responsible for:

1. **Oracle integration** -- reading the protocol's native price oracle and converting to a standardized format
2. **Compliance checks** -- verifying allowlist status, sanctions screening, and transfer restrictions before execution
3. **Trade routing** -- executing deposits, withdrawals, swaps, and stakes through the protocol's optimal entry point
4. **Error handling** -- graceful fallback when a protocol is temporarily unavailable (e.g., withdrawal queue congestion)

| Adapter | Address | Protocol | Asset | Key Method |
|---------|---------|----------|-------|-----------|
| **USDYAdapter** | `0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0` | Ondo / Merchant Moe | USDY | `allocate(vault, amount)` |
| **METHAdapter** | `0xcAae1dBf111aF26655A4f40eaC4792978d3249c8` | Mantle LSP | mETH | `stake(vault, ethAmount)` |
| **CMETHAdapter** | `0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643` | Mantle Restaking | cmETH | `restake(vault, methAmount)` |
| **FBTCAdapter** | `0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D` | Function | fBTC | `deposit(vault, btcAmount)` |

The Execution Router agent calls adapters through a unified interface (`IProtocolAdapter`), allowing new assets to be added without modifying the core pipeline. Each adapter implements:

```solidity
interface IProtocolAdapter {
    function allocate(address vault, uint256 amount) external returns (bool);
    function deallocate(address vault, uint256 amount) external returns (bool);
    function getPrice() external view returns (uint256);
    function getYield() external view returns (uint256);
    function preflightCheck(address vault) external view returns (bool, string memory);
}
```

---

## System Architecture

```
+---------------------------------------------------------------------------+
|                           MOSAIC V2 Architecture                          |
|                            Mantle Chain 5000                              |
+---------------------------------------------------------------------------+
|                                                                           |
|   USER LAYER                                                              |
|   Web dApp -- Connect Wallet -- Select Risk Profile -- Deposit USDC      |
|                                                                           |
+---------------------------------------------------------------------------+
|                                                                           |
|   SMART CONTRACT LAYER                                                    |
|   +------------------+  +------------------+  +------------------+       |
|   |   MosaicVault     |  |   DecisionLog V2  |  |   VaultFactory V2|       |
|   | ERC-4626 +       |  | Immutable on-    |  | One-click vault  |       |
|   | ERC-8004 agent   |  | chain decision   |  | deployment +     |       |
|   | identity NFT     |  | hash registry    |  | auth wiring      |       |
|   +------------------+  +------------------+  +------------------+       |
|   +------------------+  +------------------+  +------------------+       |
|   | IdentityRegistry  |  |ReputationRegistry|  |ValidationRegistry|       |
|   | ERC-8004 agent   |  | On-chain perf    |  | Third-party      |       |
|   | soulbound NFT    |  | accumulator      |  | attestations     |       |
|   +------------------+  +------------------+  +------------------+       |
|                                                                           |
|   PROTOCOL ADAPTERS                                                       |
|   +------------+  +------------+  +------------+  +------------+         |
|   |USDYAdapter  |  |METHAdapter  |  |CMETHAdapter |  |FBTCAdapter  |         |
|   |Ondo oracle  |  |Mantle LSP   |  |Restaking    |  |Function     |         |
|   |3-layer KYC  |  |stake/unstake|  |AVS rewards  |  |BTC yield    |         |
|   +------------+  +------------+  +------------+  +------------+         |
|                                                                           |
+---------------------------------------------------------------------------+
|                                                                           |
|   MULERUN AGENT PIPELINE  (15-minute cycle, off-chain orchestration)      |
|   +----------------+ +---------------+ +----------------+                |
|   | Macro Sentinel  | |  Allocator    | |Execution Router|                |
|   | Pyth + Chainlink| |Black-Litterman| |Protocol Adapters|               |
|   | Bybit + mETH   | |+ LLM views   | |Merchant Moe    |                |
|   | APY oracle     | |Validates 10k | |Mantle LSP      |                |
|   | risk_score 0-100| |bps constraint| |slip protection |                |
|   +----------------+ +---------------+ +----------------+                |
|   +----------------+ +---------------+                                    |
|   |  Risk Guardian  | |Reporting Scribe|                                   |
|   | VaR + liquidity | |JSON -> IPFS   |                                   |
|   | concentration  | |keccak256 hash|                                   |
|   | 3-level alerts  | |-> chain write |                                   |
|   +----------------+ +---------------+                                    |
|                                                                           |
+---------------------------------------------------------------------------+
|                                                                           |
|   PROTOCOL INTEGRATIONS                                                   |
|   Ondo (USDY) . Mantle LSP (mETH) . Mantle Restaking (cmETH)            |
|   Function (fBTC) . Merchant Moe . Agni Finance . Pyth . Chainlink       |
|                                                                           |
+---------------------------------------------------------------------------+
|                                                                           |
|   FRONTEND                                                                |
|   User dApp (deposit / dashboard)  .  Web Explorer (public audit trail)  |
|                                                                           |
+---------------------------------------------------------------------------+
```

---

## Smart Contract Architecture

All contracts written in Solidity ^0.8.26, deployed to Mantle via Foundry.

| Contract | Source | Description | Key Functions |
|----------|--------|-------------|---------------|
| **MosaicVault** | `contracts/src/MosaicVault.sol` | ERC-4626 vault + ERC-8004 agent identity extension. Holds user funds, records agent decisions, executes risk pauses. | `recordDecision()`, `fireRiskAlert()`, `resumeVault()`, `updateMetadataURI()` |
| **DecisionLog V2** | `contracts/src/DecisionLog.sol` | Immutable on-chain decision hash registry. Each record contains vault address, decision ID, recordHash (keccak256 of IPFS JSON), timestamp, block number. | `writeRecord()`, `getVaultHistory()`, `getTotalDecisions()` |
| **VaultFactory V2** | `contracts/src/VaultFactory.sol` | One-click new MosaicVault deployment: deploy, authorize in DecisionLog, register in IdentityRegistry, transfer ownership to user. | `createVault()`, `totalVaults()` |
| **IdentityRegistry** | `contracts/src/IdentityRegistry.sol` | ERC-8004 soulbound agent identity NFTs. | `register()`, `revoke()`, `getIdentity()` |
| **ReputationRegistry** | `contracts/src/ReputationRegistry.sol` | Cumulative on-chain performance tracking per agent. | `updateReputation()`, `getReputation()` |
| **ValidationRegistry** | `contracts/src/ValidationRegistry.sol` | Third-party attestation storage for agent validation. | `attest()`, `getAttestations()` |

**MosaicVault Core Structs:**

```solidity
struct AgentIdentity {
    string  modelDeclaration;      // "mulerun-mosaic-v2"
    uint256 createdAt;
    uint256 totalDecisions;
    uint256 successfulRebalances;
    int256  cumulativePnLBps;      // vs benchmark
    string  metadataURI;           // IPFS link to full stats
}

struct Allocation {
    uint16 usdyBps;    // USDY weight in basis points
    uint16 cmethBps;   // cmETH restaking weight
    uint16 methBps;    // mETH weight
    uint16 fbtcBps;    // fBTC weight
    uint16 usdcBps;    // USDC cash reserve
    // sum must always == 10000
}
```

**Deployment order (see `contracts/script/Deploy.s.sol`):**

```
IdentityRegistry → ReputationRegistry → ValidationRegistry
DecisionLog V2 → VaultFactory V2
VaultFactory.createVault() → MosaicVault (per user)
DecisionLog.authorizeVault(MosaicVault)
IdentityRegistry.register(MosaicVault.agentId)
Protocol Adapters (USDY, mETH, cmETH, fBTC)
```

---

## Live Performance (as of June 16, 2026)

> Three vaults have been running continuously since May 25, 2026.

| Metric | Conservative | Balanced | Aggressive |
|--------|-------------|---------|-----------|
| Days running | 22 | 22 | 22 |
| Total decisions | -- | -- | -- |
| vs Fixed benchmark (alpha) | +--% | +--% | +--% |
| On-chain records | [View](https://explorer.mantle.xyz/address/0xF3Df82262522307C6442137F24dA6710B182AE8b) | [View](https://explorer.mantle.xyz/address/0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA) | [View](https://explorer.mantle.xyz/address/0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625) |

> All decision records are publicly verifiable on Mantle Explorer and IPFS.

---

## MuleRun Agent Pipeline

Five agents orchestrated by MuleRun Agent Builder, each corresponding to an independent Skill ZIP.

### Agent 1 -- Macro Sentinel
**Cycle**: Every 15 minutes | **Skill file**: `agents/src/skills/macro-sentinel/SKILL.md`

Pulls macro data from multiple sources and computes risk_score (0-100):
- **Pyth Network**: Real-time asset prices and 24h change
- **Mantle LSP**: mETH current staking APY
- **Mantle Restaking**: cmETH yield and risk premium vs mETH
- **Ondo oracle**: USDY current yield (7d and 30d price differential)
- **Bybit v5 API**: BTC funding rate (market sentiment indicator)

Output: `MacroSignal` JSON (risk_score, restaking_premium, meth_apy, usdy_yield_7d, usdy_yield_30d, btc_funding_rate)

### Agent 2 -- Allocator
**Trigger**: After Macro Sentinel completes | **Skill file**: `agents/src/skills/allocator/SKILL.md`

Modified Black-Litterman model with LLM providing subjective market views:
1. Load base allocation for user's risk level
2. Build LLM prompt (includes MacroSignal + RiskProfile + current allocation + constraints)
3. LLM outputs target allocation + reasoning (strict validation: 5 weights must sum to 10000)
4. Retry up to 3 times on failure; fall back to base allocation after 3 failures

### Agent 3 -- Execution Router
**Trigger**: After Allocator completes | **Skill file**: `agents/src/skills/execution-router/SKILL.md`

Computes deltas, filters dust (< 50 bps), routes to optimal protocol adapter:
- **USDY delta** -> USDYAdapter (Merchant Moe USDY/USDC pool, compliance pre-flight)
- **mETH delta** -> METHAdapter (Mantle LSP `stake()` / `unstake()`)
- **cmETH delta** -> CMETHAdapter (Mantle Restaking `restake()` / `unrestake()`)
- **fBTC delta** -> FBTCAdapter (Function fBTC vault `deposit()` / `withdraw()`)

All trades undergo mandatory `eth_call` simulation before execution; failed simulations are skipped.

### Agent 4 -- Risk Guardian
**Trigger**: Every Macro Sentinel cycle | **Skill file**: `agents/src/skills/risk-guardian/SKILL.md`

Four-dimensional risk check, returns alert_level 0-3:

| Dimension | Level 2 Trigger | Level 3 Trigger |
|-----------|----------------|----------------|
| Concentration | Single asset > maxSingleAssetBps | Single asset > maxSingleAssetBps x 1.1 |
| Max Drawdown | 30-day drawdown > maxDrawdownBps | 30-day drawdown > maxDrawdownBps x 1.5 |
| Liquidity | Instantly liquidatable assets < 25% | Instantly liquidatable assets < 15% |
| Macro Stress | risk_score < 20 | risk_score < 10 |

Level >= 2: Calls `vault.fireRiskAlert(level, reason)` to write on-chain event  
Level 3: Pauses all new vault deposits until owner manually calls `resumeVault()`

### Agent 5 -- Reporting Scribe
**Trigger**: After execution completes | **Skill file**: `agents/src/skills/reporting-scribe/SKILL.md`

1. Assembles `DecisionRecord` JSON (includes MacroSignal, before/after allocations, reasoning, txs, risk assessment)
2. Uploads to IPFS (Pinata), obtains CID
3. Computes keccak256 hash of the JSON
4. Calls `MosaicVault.recordDecision(recordHash, newAlloc, pnlDeltaBps)` to write to Mantle
5. Calls `vault.updateMetadataURI("ipfs://CID")` to update ERC-8004 metadata
6. Calls `ReputationRegistry.updateReputation(agentId, pnlDeltaBps, 1)` to update reputation

**DecisionRecord JSON Example:**
```json
{
  "schema_version": "2.0",
  "vault_address": "0x...",
  "decision_id": 47,
  "timestamp": 1747012800,
  "trigger": "macro_signal_shift",
  "macro_snapshot": {
    "risk_score": 58,
    "restaking_premium_bps": 185,
    "meth_apy": 4.2,
    "usdy_yield_7d": 4.92,
    "usdy_yield_30d": 4.85,
    "btc_funding_rate": 0.0003
  },
  "previous_allocation": {"usdy_bps": 3000, "cmeth_bps": 1500, "meth_bps": 2500, "fbtc_bps": 1000, "usdc_bps": 2000},
  "target_allocation":   {"usdy_bps": 3800, "cmeth_bps": 1500, "meth_bps": 2000, "fbtc_bps": 1200, "usdc_bps": 1500},
  "reasoning_summary": "USDY 7d yield exceeding 30d by 21bps signals rate acceleration; rotating from mETH to USDY for defensive yield.",
  "execution_txs": ["0xabc...", "0xdef..."],
  "pnl_delta_bps": 12,
  "agent_model": "mulerun-mosaic-v2",
  "adapter_calls": [
    {"adapter": "USDYAdapter", "action": "allocate", "amount": "800", "success": true},
    {"adapter": "METHAdapter", "action": "deallocate", "amount": "500", "success": true}
  ]
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
+-- macro-sentinel/
    +-- SKILL.md                        <- Required: skill instructions
    +-- scripts/
    |   +-- fetch_macro.py              <- Actual execution script
    +-- references/
        +-- pyth_price_ids.json         <- Pyth price feed IDs
        +-- contract_addresses.json     <- Mantle protocol addresses
        +-- bybit_api.md                <- Bybit v5 authentication guide
```

### MCP Configuration (Advanced Settings)

In MuleRun Agent Builder -> Settings -> MCP, add:
- **Mantle RPC MCP**: Connects to Mantle node, agent can call contracts directly
- **Pinata MCP**: IPFS upload (requires Pinata JWT)
- **Bybit MCP**: Market data + trade execution

---

## Contribution to the Mantle Ecosystem

| Mantle Metric | MOSAIC's Impact | On-chain proof |
|---------------|-----------------|----------------|
| USDY TVL | Conservative vaults hold up to 50% USDY, continuously contributing USDY liquidity | USDYAdapter allocation txs on Explorer |
| mETH Staking | Every vault holds at least 20% mETH, increasing Mantle LSP staking volume | METHAdapter stake() calls |
| cmETH Restaking | Balanced/aggressive vaults actively restake when premium is favorable | CMETHAdapter restake() calls |
| fBTC TVL | BTC yield allocation diversifies portfolio and contributes Function protocol TVL | FBTCAdapter deposit() calls |
| Merchant Moe Liquidity | USDY/USDC rebalances route through Merchant Moe, increasing pool utilization | Swap txs via USDYAdapter |
| ERC-8004 Usage | MOSAIC is the first production deployment of ERC-8004 agent identity on Mantle | IdentityRegistry NFT mints |

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
# 3. Click "Initialize Agent" -> "Launch Agent"

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
+-- .env.example                          # Environment variable template
+-- .gitignore
+-- README.md                             # Updated with V2 addresses + live data
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml                        # Foundry tests + Python lint + tests
|
+-- contracts/                            # Solidity smart contracts (Foundry)
|   +-- foundry.toml
|   +-- script/
|   |   +-- Deploy.s.sol                  # Full deployment script
|   +-- src/
|   |   +-- MosaicVault.sol               # ERC-4626 + ERC-8004 vault
|   |   +-- DecisionLog.sol               # On-chain decision hash registry
|   |   +-- VaultFactory.sol              # One-click vault deployment
|   |   +-- BenchmarkTracker.sol          # Human vs AI benchmark comparison
|   |   +-- IdentityRegistry.sol          # ERC-8004 agent identity
|   |   +-- ReputationRegistry.sol        # On-chain reputation accumulator
|   |   +-- ValidationRegistry.sol        # Third-party attestations
|   |   +-- adapters/
|   |   |   +-- USDYAdapter.sol           # USDY protocol adapter
|   |   |   +-- METHAdapter.sol           # mETH protocol adapter
|   |   |   +-- CMETHAdapter.sol          # cmETH protocol adapter
|   |   |   +-- FBTCAdapter.sol           # fBTC protocol adapter
|   |   +-- interfaces/
|   |       +-- IDecisionLog.sol
|   |       +-- IProtocolAdapter.sol      # Unified adapter interface
|   +-- test/
|       +-- MosaicVault.t.sol             # Foundry test suite
|       +-- BenchmarkTracker.t.sol        # Benchmark tracker tests
|
+-- agents/                               # MuleRun agent pipeline (Python)
|   +-- AGENTS.md                         # MuleRun agent instruction file
|   +-- requirements.txt
|   +-- dist/                             # Packaged Skill ZIPs
|   |   +-- macro-sentinel.zip
|   |   +-- allocator.zip
|   |   +-- execution-router.zip
|   |   +-- risk-guardian.zip
|   |   +-- reporting-scribe.zip
|   +-- src/
|       +-- mosaic_pipeline.py            # Main orchestration loop + benchmark integration
|       +-- config.py                     # Contract addresses + ABI + network config
|       +-- core/
|       |   +-- benchmark_calculator.py   # Fixed-allocation benchmark NAV calculator
|       +-- skills/
|       |   +-- macro-sentinel/
|       |   |   +-- SKILL.md
|       |   |   +-- scripts/fetch_macro.py
|       |   +-- allocator/
|       |   |   +-- SKILL.md
|       |   |   +-- scripts/compute_allocation.py
|       |   +-- execution-router/
|       |   |   +-- SKILL.md
|       |   |   +-- scripts/execute_rebalance.py
|       |   +-- risk-guardian/
|       |   |   +-- SKILL.md
|       |   |   +-- scripts/assess_risk.py
|       |   +-- reporting-scribe/
|       |       +-- SKILL.md
|       |       +-- scripts/write_record.py
|       +-- scripts/
|           +-- create_vaults.py          # Deploy 3 demo vaults
|           +-- pack_skills.py            # Package skills as ZIPs
|
+-- docs/                                 # Documentation
|   +-- yield-strategy.md                 # USDY + mETH + cmETH yield strategy deep-dive
|   +-- examples/
|       +-- agent-registration.json       # ERC-8004 registration payload example
|
+-- frontend/                             # React dApp
    +-- src/
    |   +-- components/
    |   |   +-- VaultCard.tsx
    |   |   +-- AllocationPieChart.tsx
    |   |   +-- DecisionHistory.tsx
    |   |   +-- AgentStatusPanel.tsx
    |   +-- hooks/
    |   |   +-- useVault.ts
    |   |   +-- useDecisionLog.ts
    |   +-- lib/
    |       +-- mantle.ts                 # wagmi/viem Mantle config
    +-- public/
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MANTLE_RPC_URL` | Yes | Mantle mainnet RPC (`https://rpc.mantle.xyz`) |
| `AGENT_PRIVATE_KEY` | Yes | Agent EOA private key for signing on-chain transactions |
| `AGENT_EOA` | Yes | Agent wallet address (public) |
| `DECISION_LOG_ADDRESS` | Yes | DecisionLog V2 contract address |
| `VAULT_FACTORY_ADDRESS` | Yes | VaultFactory V2 contract address |
| `IDENTITY_REGISTRY_ADDRESS` | Yes | IdentityRegistry contract address |
| `REPUTATION_REGISTRY_ADDRESS` | Yes | ReputationRegistry contract address |
| `BYBIT_API_KEY` | Yes | Bybit v5 API key (BTC funding rate + data) |
| `BYBIT_SECRET` | Yes | Bybit API secret |
| `PINATA_JWT` | Yes | Pinata JWT token (IPFS upload) |
| `DEEPSEEK_API_KEY` | Yes | DeepSeek API key (Allocator LLM) |
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
2026-05-11T10:00:02 [Mosaic] INFO MacroSignal: risk_score=62 | restaking_premium=185bps | mETH=4.25% | fresh=True
2026-05-11T10:00:02 [Mosaic] INFO Rebalance triggered: initial
2026-05-11T10:00:02 [Mosaic] INFO RiskAssessment: alert_level=0 | []
2026-05-11T10:00:03 [Mosaic] INFO Allocator: USDY yield accelerating; increasing USDY 8pp from mETH. | confidence=0.82
2026-05-11T10:00:04 [Mosaic] INFO Adapter pre-flight: USDY=ok | mETH=ok | cmETH=ok | fBTC=ok
2026-05-11T10:00:05 [Mosaic] INFO Execution: 3 trades | ok=True | txs=['0xabc...', '0xdef...', '0x123...']
2026-05-11T10:00:06 [Mosaic] INFO Scribe: IPFS=QmXyz... | hash=0x4a2f8c1b9e... | chain_tx=0x789...
2026-05-11T10:00:06 [Mosaic] INFO Reputation updated: agent#1 pnl=+12bps decisions=48
2026-05-11T10:00:06 [Mosaic] INFO Cycle 1 complete. Vault: 0x1234... | Record #48
```

### Three-Vault Parallel Demo (recommended for hackathon)

```bash
# Launch three vaults with different risk levels for diversified data
python src/mosaic_pipeline.py --vault $VAULT_CONSERVATIVE &
python src/mosaic_pipeline.py --vault $VAULT_BALANCED &
python src/mosaic_pipeline.py --vault $VAULT_AGGRESSIVE &
```

Three vaults start running from `Week 3 (May 25)`, accumulating **18-21 days of real on-chain decision data** by Demo Day.

---

## Economic Loop

```
+------------------------------------------------------------------------------+
|                         MOSAIC V2 Value Loop                                 |
|                                                                              |
|  User deposits USDC                                                          |
|       |                                                                      |
|       v                                                                      |
|  +-------------+   MacroSignal   +-------------+   target alloc             |
|  |Macro Sentinel| -------------> |  Allocator   | -------------+            |
|  |15min cycle   |                |LLM + BL model|              |            |
|  +-------------+                +-------------+              v            |
|                                                        +-------------+     |
|                                                        |  Execution   |     |
|  +-------------+ risk check     +-------------+       |  Router      |     |
|  |Risk Guardian | -------------> |  MosaicVault | <---- | Adapters:   |     |
|  |VaR monitor   |                |  ERC-4626   |       | USDY/mETH/  |     |
|  |3-level alert |                |  ERC-8004   |       | cmETH/fBTC  |     |
|  +-------------+                +------+------+       +-------------+     |
|                                        |                                    |
|                                        | recordDecision()                   |
|                                        v                                    |
|                               +-------------+  IPFS JSON  +-------------+  |
|                               | DecisionLog  | <---------- |  Reporting  |  |
|                               | on-chain     |             |  Scribe     |  |
|                               | hash registry|             |  Pinata     |  |
|                               +-------------+             +------+------+  |
|                                                                   |         |
|                                                                   v         |
|                                                          +-------------+   |
|                                                          | Reputation  |   |
|                                                          | Registry    |   |
|                                                          +-------------+   |
|                                        |                                    |
|                                        v                                    |
|                               Web Explorer (public audit trail)             |
+------------------------------------------------------------------------------+
```

**Asset Flow:**
- User funds -> MosaicVault (held via ERC-4626)
- Execution Router calls protocol adapters to complete asset allocation
- USDY Treasury yield, mETH staking yield, cmETH restaking rewards, and fBTC yield auto-compound within the vault
- Every rebalance record permanently stored on Mantle + IPFS
- Agent reputation accumulates in ReputationRegistry with each successful cycle

---

## Security Model

### Pre-Execution Simulation
Execution Router simulates every transaction via `eth_call` before broadcast; failed simulations are skipped -- no broadcast, no gas consumed.

### Adapter Pre-Flight Checks
Each protocol adapter implements a `preflightCheck()` function that validates compliance requirements, liquidity availability, and protocol health before any trade is attempted.

### Risk Pause Mechanism
After Risk Guardian triggers Level 3, MosaicVault automatically rejects all new `deposit()` and `mint()` calls (ReentrancyGuard protected) until the vault owner calls `resumeVault()`.

### Agent Error Isolation
The main pipeline loop wraps every cycle in try/catch. A single skill invocation failure never stops the pipeline; failed skill outputs are replaced by fallback values, and the on-chain decision record logs `error_flag: true`.

### Private Key Protection
`AGENT_PRIVATE_KEY` only exists in `.env` and MuleRun's encrypted environment variables -- never appears in logs or on-chain data. All logs only record the EOA address.

### Anti-Replay
The DecisionLog contract enforces uniqueness checks per recordHash (`mapping(bytes32 => bool) public recordExists`); the same hash cannot be written twice.

---

## Roadmap

**v1 (Legacy)**
- All five agents fully implemented, running 24/7
- Supports USDY, mETH, fBTC, USDC
- On-chain decision records + Web Explorer

**v2 (Current)**
- Protocol Adapter architecture for modular asset integration
- ERC-8004 agent identity with IdentityRegistry, ReputationRegistry, ValidationRegistry
- cmETH restaking integration with risk premium monitoring
- USDY yield curve analysis (7d/30d differential)
- Compliance-aware allocation with three-layer allowlist support
- Upgraded DecisionLog and VaultFactory contracts

**v3 (Post-Hackathon)**
- Copy Vault: One-click copy of high-reputation agent's historically optimal strategy
- Cross-chain restaking: Support additional restaking protocols via new adapters
- Institutional white-label: Family offices deploy private MOSAIC instances with custom strategy templates

**v4 (Long-term)**
- Cross-chain expansion: Support Solana-side assets via Mantle Super Portal
- Community strategy marketplace: Developers publish custom allocator strategies
- Agent-to-agent delegation: High-reputation agents can delegate sub-tasks to specialized agents

---

## Team

| Role | Account |
|------|---------|
| Solo Developer | **wangyangmingssssss** |

Built for the Mantle Turing Test Hackathon 2026.  
Five agents. Twelve contracts. One truly autonomous on-chain RWA asset management protocol.

---

## License

MIT License. SPDX declarations in each source file.

```
SPDX-License-Identifier: MIT
```
