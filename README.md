[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](https://github.com/wangyangmingsss/mosaic/actions)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Mantle](https://img.shields.io/badge/Mantle-Chain_5000-8B5CF6)](https://mantle.xyz)
[![AI x RWA](https://img.shields.io/badge/Track-AI_x_RWA-10B981)](https://dorahacks.io/hackathon/mantleturingtesthackathon2026)
[![MuleRun](https://img.shields.io/badge/Agent-MuleRun-F59E0B)](https://mulerun.com)

# MOSAIC

**五个自主 AI 代理在 Mantle 上管理你的真实资产投资组合。每一个决策，永久上链。**

> 演示站点: https://mosaic-mantle.mule.page  
> Web Explorer: https://mosaic-explorer.mule.page  
> DoraHacks: https://dorahacks.io/hackathon/mantleturingtesthackathon2026

---

## 项目概述

MOSAIC 是 Mantle 上第一个真正的 AI agent 驱动的 RWA 资产管理协议。

用户将资金存入一个 ERC-4626 金库，MOSAIC 的五个协作 agent——由 MuleRun AI agent 框架编排——立即开始 7×24 持续工作：监控宏观信号、计算最优 RWA 配置、通过 Fluxion Atomic RFQ 执行代币化美股交易、通过 Merchant Moe 买卖 USDY、在 Mantle LSP 质押/取质押 mETH。每次调仓决策的完整推理链路（触发条件、宏观数据快照、LLM 推理摘要、执行记录）都经 keccak256 哈希后写入 Mantle，内容存储在 IPFS，任何人可验证。

**为什么这很重要：**  
Mantle 已经建成了全球最好的链上 RWA 基础设施——xStocks（代币化美股）、USDY（国债收益）、mETH（ETH staking）、fBTC（BTC restaking）全部上线。但今天的用户需要自己手动判断宏观环境、手动切换配置、手动监控风险。MOSAIC 把这个复杂流程完全自动化，同时保持机构级的可审计性。

**核心差异化：**

- **xStocks 优先集成**：MOSAIC 是第一个把 AI agent 策略建立在 Fluxion Atomic RFQ + xStocks 代币化美股上的项目，直接服务 Mantle 最新的战略业务线
- **真正的跨资产类别管理**：美股 + 国债 + ETH staking + BTC yield，不是单一资产 yield aggregator
- **机构级决策审计链**：每次调仓完整记录上链，合规部门可实际审计
- **ERC-8004 agent 声誉**：每个金库的 agent 实例积累可追溯的链上业绩，声誉本身是可验证的资产

---

## 系统架构

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

## 智能合约架构

所有合约使用 Solidity ^0.8.26 编写，通过 Foundry 部署到 Mantle。

| 合约 | 源文件 | 说明 | 关键函数 |
|------|--------|------|---------|
| **MosaicVault** | `contracts/src/MosaicVault.sol` | ERC-4626 金库 + ERC-8004 agent 身份扩展。持有用户资金，记录 agent 决策，执行风险暂停。 | `recordDecision()`, `fireRiskAlert()`, `resumeVault()`, `updateMetadataURI()` |
| **DecisionLog** | `contracts/src/DecisionLog.sol` | 不可篡改的链上决策哈希注册表。每条记录含 vault 地址、决策 ID、recordHash（keccak256 of IPFS JSON）、时间戳、区块号。 | `writeRecord()`, `getVaultHistory()`, `getTotalDecisions()` |
| **VaultFactory** | `contracts/src/VaultFactory.sol` | 一键部署新 MosaicVault：deploy → authorize in DecisionLog → transfer ownership to user。 | `createVault()`, `totalVaults()` |

**MosaicVault 核心结构体：**

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

**部署顺序（参见 `contracts/script/Deploy.s.sol`）：**

```
DecisionLog → VaultFactory
VaultFactory.createVault() → MosaicVault (per user)
DecisionLog.authorizeVault(MosaicVault)
```

---

## 链上部署

合约已部署至 **Mantle Testnet（Sepolia, Chain ID 5003）** 进行黑客松演示。

| 合约 | 地址 |
|------|------|
| **DecisionLog** | `待更新 — 部署后填入` |
| **VaultFactory** | `待更新 — 部署后填入` |
| **MosaicVault #1 (Conservative)** | `待更新` |
| **MosaicVault #2 (Balanced)** | `待更新` |
| **MosaicVault #3 (Aggressive)** | `待更新` |

> 区块浏览器: https://explorer.testnet.mantle.xyz

---

## MuleRun Agent Pipeline

五个 agent 由 MuleRun Agent Builder 编排，每个 agent 对应一个独立的 Skill ZIP。

### Agent 1 — Macro Sentinel
**周期**：每 15 分钟 | **技能文件**：`agents/src/skills/macro-sentinel/SKILL.md`

从四个数据源拉取宏观数据并计算 risk_score（0–100）：
- **Pyth Network**：TSLAx、NVDAx、AAPLx、SPYx、QQQx 实时价格及 24h 涨跌幅
- **Mantle LSP**：mETH 当前质押 APY
- **Ondo oracle**：USDY 当前收益率
- **Bybit v5 API**：BTC 资金费率（市场情绪指标）

输出：`MacroSignal` JSON（risk_score, equity_momentum, meth_apy, usdy_yield, btc_funding_rate）

### Agent 2 — Allocator
**触发**：Macro Sentinel 完成后 | **技能文件**：`agents/src/skills/allocator/SKILL.md`

改良版 Black-Litterman 模型，LLM（claude-sonnet-4-20250514）提供主观市场观点：
1. 加载用户风险等级对应的基准配置
2. 构建 LLM prompt（包含 MacroSignal + RiskProfile + 当前配置 + 约束条件）
3. LLM 输出目标配置 + reasoning（严格验证：5 个权重之和必须 == 10000）
4. 失败重试最多 3 次；3 次失败后回退基准配置

### Agent 3 — Execution Router
**触发**：Allocator 完成后 | **技能文件**：`agents/src/skills/execution-router/SKILL.md`

计算 delta，过滤 dust（< 50 bps），路由到最优协议：
- **xStocks delta** → Fluxion Atomic RFQ（交易时段）/ Fluxion AMM（收市后）
- **USDY delta** → Merchant Moe USDY/USDC 流动性池
- **mETH delta** → Mantle LSP `stake()` / `unstake()`
- **fBTC delta** → Function fBTC vault `deposit()` / `withdraw()`

所有交易执行前强制 `eth_call` 模拟；模拟失败的交易跳过不执行。

### Agent 4 — Risk Guardian
**触发**：每个 Macro Sentinel 周期 | **技能文件**：`agents/src/skills/risk-guardian/SKILL.md`

四维风险检查，返回 alert_level 0–3：

| 维度 | Level 2 触发 | Level 3 触发 |
|------|-------------|-------------|
| 集中度 | 单资产 > maxSingleAssetBps | 单资产 > maxSingleAssetBps × 1.1 |
| 最大回撤 | 30日回撤 > maxDrawdownBps | 30日回撤 > maxDrawdownBps × 1.5 |
| 流动性 | 可即时变现资产 < 25% | 可即时变现资产 < 15% |
| 宏观压力 | risk_score < 20 | risk_score < 10 |

Level ≥ 2：调用 `vault.fireRiskAlert(level, reason)` 写入链上事件  
Level 3：暂停金库所有新存款直到 owner 手动恢复

### Agent 5 — Reporting Scribe
**触发**：执行完成后 | **技能文件**：`agents/src/skills/reporting-scribe/SKILL.md`

1. 组装 `DecisionRecord` JSON（含 MacroSignal、前后配置、reasoning、txs、风险评估）
2. 上传至 IPFS（Pinata），获取 CID
3. 计算 JSON 的 keccak256 哈希
4. 调用 `MosaicVault.recordDecision(recordHash, newAlloc, pnlDeltaBps)` 写入 Mantle
5. 调用 `vault.updateMetadataURI("ipfs://CID")` 更新 ERC-8004 元数据

**DecisionRecord JSON 示例：**
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

## MuleRun Agent Builder 配置

MOSAIC 使用 MuleRun Agent Builder 部署五个协作 agent。

### Agent 设置

**AGENTS.md 位置**: `agents/AGENTS.md`

| 字段 | 值 |
|------|-----|
| Agent Name | Mosaic RWA Portfolio Agent |
| 主要 Skill | macro-sentinel, allocator, execution-router, risk-guardian, reporting-scribe |
| 运行模式 | Scheduled (15-minute interval) |
| 环境变量 | 见 `.env.example` 中 MuleRun 配置部分 |

### Skills ZIP 结构

每个 skill 打包为 ZIP 上传至 MuleRun Agent Builder：

```
macro-sentinel.zip
└── macro-sentinel/
    ├── SKILL.md                        ← 必须：skill 指令
    ├── scripts/
    │   └── fetch_macro.py              ← 实际执行脚本
    └── references/
        ├── pyth_price_ids.json         ← Pyth 价格 feed IDs
        ├── contract_addresses.json     ← Mantle 协议地址
        └── bybit_api.md                ← Bybit v5 认证指南
```

### MCP 配置 (Advanced Settings)

在 MuleRun Agent Builder → Settings → MCP 中添加：
- **Mantle RPC MCP**: 连接 Mantle 节点，agent 可直接调用合约
- **Pinata MCP**: IPFS 上传（需 Pinata JWT）
- **Bybit MCP**: 市场数据 + 交易执行

---

## 快速开始

### 环境要求

- [Foundry](https://book.getfoundry.sh/) (Solidity 编译与测试)
- Python >= 3.11 (agent 运行时)
- [MuleRun 账号](https://mulerun.com) (agent 部署)

### 1. 克隆仓库

```bash
git clone https://github.com/wangyangmingsss/mosaic.git
cd mosaic
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 填入所有必需变量（见下方环境变量说明）
```

### 3. 编译与测试合约

```bash
cd contracts

# 安装 OpenZeppelin 依赖
forge install OpenZeppelin/openzeppelin-contracts --no-commit
forge install foundry-rs/forge-std --no-commit

# 编译
forge build

# 运行测试（含 gas report）
forge test -vvv --gas-report
```

### 4. 部署到 Mantle Testnet

```bash
source .env

forge script script/Deploy.s.sol:Deploy \
  --rpc-url $MANTLE_RPC_TESTNET \
  --broadcast \
  --legacy

# 将输出的合约地址填入 .env：
# DECISION_LOG_ADDRESS=0x...
# VAULT_FACTORY_ADDRESS=0x...
```

### 5. 安装 agent 依赖

```bash
cd ../agents
pip install -r requirements.txt
```

### 6. 创建测试金库

```bash
cd agents
python scripts/create_vault.py \
  --risk-level 2 \
  --rebalance-frequency 2 \
  --max-drawdown 1500 \
  --max-single-asset 6000
# 输出: Vault deployed at 0x...
```

### 7. 启动 agent pipeline

```bash
# 使用 MuleRun 平台（推荐）
# 1. 打包 skills: python scripts/pack_skills.py
# 2. 在 MuleRun Agent Builder 上传 agents/AGENTS.md + 5 个 skill ZIPs
# 3. 点击 "Initialize Agent" → "Launch Agent"

# 或本地运行（用于开发）
python src/mosaic_pipeline.py --vault 0xYourVaultAddress
```

### 8. 查看 Dashboard

```bash
# Web Explorer (公开，无需登录)
open https://mosaic-explorer.mule.page

# 或本地前端
cd frontend && npm install && npm run dev
```

---

## 项目结构

```
mosaic/
├── .env.example                          # 环境变量模板
├── .gitignore
├── README.md
│
├── .github/
│   └── workflows/
│       └── ci.yml                        # Foundry 测试 + Python lint + tests
│
├── contracts/                            # Solidity 智能合约 (Foundry)
│   ├── foundry.toml
│   ├── script/
│   │   └── Deploy.s.sol                  # 完整部署脚本
│   ├── src/
│   │   ├── MosaicVault.sol               # ERC-4626 + ERC-8004 金库
│   │   ├── DecisionLog.sol               # 链上决策哈希注册表
│   │   ├── VaultFactory.sol              # 一键部署金库
│   │   └── interfaces/
│   │       └── IDecisionLog.sol
│   └── test/
│       └── MosaicVault.t.sol             # Foundry 测试套件
│
├── agents/                               # MuleRun agent pipeline (Python)
│   ├── AGENTS.md                         # MuleRun agent 指令文件
│   ├── requirements.txt
│   └── src/
│       ├── mosaic_pipeline.py            # 主编排循环
│       ├── config.py                     # 合约地址 + ABI + 网络配置
│       └── skills/
│           ├── macro-sentinel/
│           │   └── SKILL.md              # 宏观数据采集 skill
│           ├── allocator/
│           │   └── SKILL.md              # Black-Litterman + LLM 配置优化 skill
│           ├── execution-router/
│           │   └── SKILL.md              # 链上交易执行 skill
│           ├── risk-guardian/
│           │   └── SKILL.md              # 风险监控 + 链上告警 skill
│           └── reporting-scribe/
│               └── SKILL.md              # IPFS 归档 + 链上记录 skill
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
    │       └── mantle.ts                 # wagmi/viem Mantle 配置
    └── public/
```

---

## 环境变量说明

| 变量 | 必须 | 说明 |
|------|------|------|
| `MANTLE_RPC_URL` | ✅ | Mantle 主网 RPC（`https://rpc.mantle.xyz`）|
| `AGENT_PRIVATE_KEY` | ✅ | agent EOA 私钥，用于签名链上交易 |
| `AGENT_EOA` | ✅ | agent 钱包地址（public） |
| `DECISION_LOG_ADDRESS` | ✅ | 部署后填入 DecisionLog 合约地址 |
| `VAULT_FACTORY_ADDRESS` | ✅ | 部署后填入 VaultFactory 合约地址 |
| `BYBIT_API_KEY` | ✅ | Bybit v5 API key（BTC 资金费率 + 数据） |
| `BYBIT_SECRET` | ✅ | Bybit API secret |
| `PINATA_JWT` | ✅ | Pinata JWT token（IPFS 上传） |
| `ANTHROPIC_API_KEY` | ✅ | Claude API key（Allocator LLM） |
| `FLUXION_API_KEY` | ⚠️ | Fluxion Atomic RFQ API（可选，有 fallback） |
| `MANTLE_EXPLORER_KEY` | ⚠️ | Mantle Explorer API（合约 verify 用） |
| `DRY_RUN` | ⚠️ | `true` 时模拟但不广播交易（测试用） |

---

## 运行演示

### 本地 Demo（无链上交易）

```bash
cd agents
python src/mosaic_pipeline.py --vault 0xMockAddress --dry-run
```

观察控制台输出：

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

### 三个金库并行演示（黑客松推荐）

```bash
# 启动三个不同风险等级的金库，产生多样化数据
python src/mosaic_pipeline.py --vault $VAULT_CONSERVATIVE &
python src/mosaic_pipeline.py --vault $VAULT_BALANCED &
python src/mosaic_pipeline.py --vault $VAULT_AGGRESSIVE &
```

三个金库从 `Week 3（5月25日）` 开始运行，到 Demo Day 时将积累 **18-21 天的真实链上决策数据**。

---

## 经济循环

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

**资产流向：**
- 用户资金 → MosaicVault（ERC-4626 持有）
- Execution Router 调用各协议合约完成资产配置
- USDY 的国债收益、mETH 的质押收益、xStocks 的价格敞口在金库内自动复利
- 每次调仓的完整记录永久存储在 Mantle + IPFS

---

## 安全模型

### 执行前模拟
Execution Router 对每笔交易先执行 `eth_call` 模拟；模拟失败的交易直接跳过，不广播，不消耗 gas。

### 风险暂停机制
Risk Guardian 触发 Level 3 后，MosaicVault 自动拒绝所有新的 `deposit()` 和 `mint()` 调用（ReentrancyGuard 保护），直到 vault owner 调用 `resumeVault()`。

### Agent 错误隔离
主 pipeline 循环每个周期都有 try/catch 包裹。一次 skill 调用异常不会停止 pipeline；失败的 skill 输出会被 fallback 值替代，并在链上 decision record 中记录 `error_flag: true`。

### 私钥保护
`AGENT_PRIVATE_KEY` 只存在于 `.env` 和 MuleRun 的加密环境变量中，从不出现在日志或链上数据里。所有日志只记录 EOA 地址。

### 防重放
DecisionLog 合约对每个 recordHash 执行唯一性检查（`mapping(bytes32 => bool) public recordExists`），同一哈希不可二次写入。

---

## 对 Mantle 生态的贡献

| Mantle 指标 | MOSAIC 的影响 |
|------------|--------------|
| xStocks TVL | 每个 balanced/aggressive vault 持续购买 xStocks，直接增加 Fluxion xStocks 交易量和 TVL |
| USDY TVL | conservative vault 最高持有 50% USDY，持续贡献 USDY 流动性 |
| mETH staking | 每个 vault 至少 20% mETH，增加 Mantle LSP 质押量 |
| Fluxion 交易量 | Execution Router 优先走 Fluxion Atomic RFQ，每次 xStocks 调仓贡献交易量 |
| Merchant Moe 流动性 | USDY/USDC 调仓通过 Merchant Moe，增加其池子利用率 |
| ERC-8004 使用 | MOSAIC 是 ERC-8004 agent identity 的首个有实际业务意义的扩展应用 |

---

## 路线图

**v1（当前 — 黑客松版本）**
- 五个 agent 全部实现，7×24 运行
- 支持 USDY、xStocks（SPYx、NVDAx）、mETH、fBTC、USDC
- 链上决策记录 + Web Explorer

**v2（黑客松后）**
- Copy Vault 功能：一键复制高声誉 agent 的历史最优策略
- xPoints 积分整合：Mantle xStocks 生态激励直接流向 MOSAIC 用户
- 更多 xStocks 品种接入（TSLAx、AAPLx、METAx、GOOGLx）

**v3（长期）**
- 机构白标版本：family office 可部署私有 MOSAIC 实例，使用自定义策略模板
- 跨链扩展：通过 Mantle Super Portal 支持 Solana 侧资产
- 社区策略市场：开发者可发布自定义 allocator 策略

---

## 团队

| 角色 | 账号 |
|------|------|
| 独立开发者 | **wangyangmingssssss** |

为 Mantle Turing Test Hackathon 2026 打造。  
五个 agent。三种合约。一个真正自主的链上 RWA 资产管理协议。

---

## 许可证

MIT License。各源文件中有 SPDX 声明。

```
SPDX-License-Identifier: MIT
```
