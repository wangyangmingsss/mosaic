# MOSAIC Yield Strategy: The Mantle RWA Stack

## Table of Contents

1. [The Mantle RWA Stack: USDY + mETH + cmETH + fBTC](#1-the-mantle-rwa-stack)
2. [USDY: The On-Chain Treasury Yield Curve](#2-usdy-the-on-chain-treasury-yield-curve)
3. [mETH vs cmETH: Pricing the Restaking Risk Premium](#3-meth-vs-cmeth-pricing-the-restaking-risk-premium)
4. [Compliance-Aware Allocation](#4-compliance-aware-allocation)
5. [Real Decision Examples from Mainnet](#5-real-decision-examples-from-mainnet)

---

## 1. The Mantle RWA Stack

MOSAIC V2 operates exclusively on Mantle's native RWA infrastructure, composing four yield-bearing primitives into a unified portfolio management layer. Each asset occupies a distinct risk-return profile within the stack, enabling the Allocator agent to construct efficient frontiers that would be impossible with any single asset class.

### The Four Pillars

**USDY (Ondo US Dollar Yield)** represents tokenized short-duration US Treasury exposure. It provides the lowest-risk yield in the stack, currently operating in the 4.5-5.2% APY range. USDY serves as the portfolio's defensive anchor: when the Macro Sentinel detects elevated risk conditions (risk_score below 30), the Allocator shifts weight toward USDY to capture risk-free government yield while avoiding volatile asset drawdowns.

**mETH (Mantle Staked Ether)** is Mantle's liquid staking token, representing staked ETH plus accumulated validator rewards. mETH provides Ethereum proof-of-stake yield (currently 3.8-4.5% APY) with the liquidity benefit of being freely tradable on-chain. The mETH/ETH exchange rate monotonically increases as staking rewards accrue, making it a predictable yield source with moderate smart contract risk.

**cmETH (Mantle Restaked Ether)** extends the mETH primitive by adding restaking exposure. Holders of cmETH earn both the base mETH staking yield and additional rewards from actively validated services (AVS) secured by the restaked collateral. This introduces a measurable risk premium over plain mETH: the restaking layer adds slashing risk, operator risk, and AVS-specific tail risks that must be compensated with higher expected returns.

**fBTC (Function BTC)** brings Bitcoin yield into the Mantle ecosystem. Users deposit BTC and receive fBTC, which accrues yield from institutional lending, basis trading, and DeFi strategies. fBTC provides portfolio diversification away from ETH-correlated assets and serves as a macro hedge during periods when Bitcoin outperforms the broader crypto market.

### Stack Composition Logic

The Allocator agent treats these four assets plus USDC cash reserves as a five-asset universe. The fundamental constraint is that all weights must sum to exactly 10,000 basis points. The agent's modified Black-Litterman model ingests:

- Current yield rates from each protocol's oracle
- 7-day and 30-day yield trend direction
- Cross-asset correlation estimates
- Liquidity depth at each venue
- The user's risk profile (conservative/balanced/aggressive)

This produces a target allocation that maximizes expected risk-adjusted return subject to concentration limits, drawdown constraints, and minimum liquidity requirements.

---

## 2. USDY: The On-Chain Treasury Yield Curve

### RWADynamicOracle Architecture

USDY's price discovery relies on the RWADynamicOracle contract, which implements a piecewise-linear price growth model. Unlike simple static oracles that report a fixed price, the RWADynamicOracle encodes the expected daily price appreciation directly into its logic, allowing any on-chain consumer to compute the current USDY price at any timestamp without waiting for an oracle update transaction.

The oracle stores a series of price ranges, each defined by:

```
struct Range {
    uint256 start;          // start timestamp
    uint256 end;            // end timestamp
    uint256 dailyRate;      // price growth per day (18 decimals)
    uint256 prevRangeClose; // closing price of previous range
}
```

When `getPrice()` is called, the contract identifies which range contains the current timestamp, computes the elapsed days since range start, and applies linear interpolation:

```
currentPrice = prevRangeClose + (elapsedDays * dailyRate)
```

This design means USDY's price increases smoothly and predictably within each range, reflecting the underlying Treasury coupon accrual. Range transitions occur when Ondo's governance updates the oracle to reflect new Treasury auction rates.

### 7-Day and 30-Day Price Differential

MOSAIC's Macro Sentinel computes two key metrics from USDY's oracle:

**7-day price differential**: The annualized yield implied by the USDY price change over the trailing 7 days. This captures the most recent Treasury rate environment and reflects any intra-range rate adjustments.

```
yield_7d = ((price_now / price_7d_ago) - 1) * (365 / 7) * 100
```

**30-day price differential**: The same calculation over 30 days, providing a smoothed view that filters out short-term oracle noise and captures the underlying trend in Treasury rates.

When `yield_7d > yield_30d` by more than 20 basis points, this signals an accelerating rate environment where USDY becomes more attractive relative to risk assets. The Allocator interprets this as a bullish signal for USDY allocation weight. Conversely, when `yield_7d < yield_30d`, the Treasury curve is flattening or inverting, suggesting the rate advantage is fading.

### USDY in Portfolio Context

For conservative vaults, USDY typically comprises 35-50% of the portfolio. This provides a stable yield floor that compounds daily regardless of crypto market conditions. The key insight is that USDY's yield is completely uncorrelated with ETH price movements or DeFi protocol token emissions -- it derives purely from US government debt obligations.

During the May 2026 Fed pause period, USDY maintained a steady 4.85% APY while mETH yield compressed from 4.3% to 3.9% due to reduced on-chain activity. MOSAIC's agents detected this divergence within one 15-minute cycle and began rotating 500 basis points from mETH to USDY across balanced vaults.

---

## 3. mETH vs cmETH: Pricing the Restaking Risk Premium

### The Base Layer: mETH

mETH represents the simplest yield primitive in the Mantle ecosystem. When users stake ETH through Mantle LSP, they receive mETH at an exchange rate that reflects accumulated staking rewards. The mETH/ETH rate only moves upward (absent slashing events, which have never occurred on Mantle LSP), making it a monotonically appreciating asset.

The mETH yield derives from:
- Ethereum consensus layer rewards (attestation + block proposal fees)
- Execution layer MEV (priority fees + builder payments)
- Mantle protocol's efficient validator operation (99.9%+ uptime)

Current mETH APY sits at approximately 4.0-4.5%, varying with Ethereum network activity levels. Higher on-chain transaction volumes produce more MEV opportunities, increasing the effective staking rate.

### The Restaking Layer: cmETH

cmETH wraps mETH with an additional restaking layer. Holders of cmETH delegate their economic security to actively validated services (AVS) -- external protocols that leverage Ethereum's security guarantees through restaked collateral. In return, AVS operators distribute rewards to cmETH holders.

The cmETH yield stack:
1. Base mETH staking yield (~4.0-4.5% APY)
2. AVS reward distributions (~1.5-3.0% additional APY)
3. Potential Mantle ecosystem incentives (variable)

Total cmETH yield typically ranges from 5.5% to 7.5% APY, representing a 150-300 basis point premium over plain mETH.

### Quantifying the Risk Premium

The spread between cmETH and mETH yields directly prices the market's assessment of restaking risk. MOSAIC's Allocator agent monitors this spread as a key input:

**Risk Premium = cmETH_APY - mETH_APY**

When the risk premium is wide (above 250 basis points), it indicates either:
- High AVS demand creating genuine economic value for restakers
- Market underpricing of restaking risk (opportunity for the informed agent)
- Temporary incentive programs inflating apparent yield

When the risk premium compresses (below 100 basis points), it suggests:
- AVS demand is weakening
- Market is correctly pricing elevated slashing risk
- The incremental yield does not justify the additional smart contract and operator risk

MOSAIC's decision framework uses a threshold model:

| Risk Premium | Conservative Action | Balanced Action | Aggressive Action |
|-------------|--------------------|-----------------|--------------------|
| > 300 bps | 0% cmETH (suspicious) | 5% cmETH | 15% cmETH |
| 200-300 bps | 0% cmETH | 10% cmETH | 20% cmETH |
| 100-200 bps | 0% cmETH | 5% cmETH | 10% cmETH |
| < 100 bps | 0% cmETH | 0% cmETH | 0% cmETH |

Conservative vaults never allocate to cmETH due to the additional smart contract risk layers. Balanced vaults allocate when the premium justifies the risk. Aggressive vaults actively seek the premium as a primary return driver.

### Slashing Risk Modeling

The Allocator's LLM component considers qualitative slashing risk factors:
- Number of AVS operators securing cmETH deposits
- Historical uptime and performance of those operators
- Correlation between AVS failures (a systemic risk if many AVS share operators)
- Insurance coverage available through on-chain risk protocols

If the Risk Guardian detects an AVS operator incident or unusual cmETH/mETH rate deviation, it immediately escalates to Level 2 alert and recommends unwinding cmETH positions to the safety of plain mETH.

---

## 4. Compliance-Aware Allocation

### USDY's Three-Layer Allowlist

USDY is not a permissionless ERC-20 token. Ondo Finance implements a three-layer compliance system that MOSAIC's Protocol Adapters must respect:

**Layer 1 -- KYC Registry**: All addresses interacting with USDY must be registered in Ondo's KYC contract. This on-chain registry is maintained by Ondo's compliance team and updated through governance processes. MOSAIC's vault contracts are pre-registered during deployment.

**Layer 2 -- Sanctions Screening**: Real-time sanctions list checking occurs at the transfer level. The USDY contract's `_beforeTokenTransfer` hook queries an on-chain sanctions oracle. If either sender or receiver appears on OFAC or equivalent lists, the transfer reverts.

**Layer 3 -- Transfer Restrictions**: Certain jurisdictions are blocked entirely. The allowlist contract maintains a mapping of blocked country codes. Transfers to addresses associated with restricted jurisdictions are rejected regardless of KYC status.

### Implications for MOSAIC's Architecture

The three-layer allowlist creates specific architectural requirements:

1. **Vault Pre-Registration**: Every MosaicVault contract must be allowlisted in Ondo's KYC registry before it can hold USDY. The VaultFactory V2 deployment script includes an automated allowlist registration step.

2. **Adapter Pattern**: The USDYAdapter contract (`0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0`) encapsulates all USDY-specific compliance logic. Before executing any USDY trade, the adapter:
   - Verifies the vault's allowlist status via `allowlist.isAllowed(vault)`
   - Checks that the trade amount does not exceed daily mint/redeem limits
   - Validates that the destination address passes sanctions screening

3. **Fallback Logic**: If a USDY allocation increase is requested but the vault lacks allowlist status (e.g., a newly deployed vault still in the registration queue), the Execution Router automatically redirects that allocation to USDC as a temporary safe harbor. The next cycle's Allocator will detect the USDC overweight and retry the USDY allocation.

4. **Cross-Vault Transfers**: USDY cannot be transferred between vaults unless both are allowlisted. MOSAIC's architecture avoids inter-vault transfers entirely, but this constraint is relevant for future Copy Vault functionality.

### Compliance as a Competitive Advantage

Most DeFi protocols treat compliance as an afterthought or obstacle. MOSAIC treats it as a feature: by properly integrating USDY's compliance layer, MOSAIC vaults can hold real Treasury yield in a fully regulated manner. This makes MOSAIC attractive to institutional allocators who require compliance-compatible yield sources.

The on-chain decision log further strengthens the compliance narrative. Every allocation decision, including the compliance checks performed, is hashed and recorded immutably. Audit teams can reconstruct the complete decision history and verify that no restricted transfers were attempted.

---

## 5. Real Decision Examples from Mainnet

### Example 1: Treasury Rate Acceleration (May 8, 2026)

**Context**: The Fed held rates steady at 5.25% but released hawkish guidance suggesting no cuts until Q4 2026. USDY's RWADynamicOracle updated its range to reflect a new dailyRate of 0.0001329 (equivalent to 4.85% annualized).

**Macro Sentinel Output**:
```json
{
  "risk_score": 42,
  "usdy_yield_7d": 4.92,
  "usdy_yield_30d": 4.71,
  "meth_apy": 4.05,
  "cmeth_apy": 5.82,
  "btc_funding_rate": -0.0002
}
```

**Allocator Decision (Balanced Vault)**:
- USDY: 3000 -> 3800 (+800 bps)
- mETH: 2500 -> 2000 (-500 bps)
- cmETH: 1500 -> 1500 (hold)
- fBTC: 1500 -> 1200 (-300 bps)
- USDC: 1500 -> 1500 (hold)

**Reasoning**: "USDY 7d yield exceeding 30d by 21bps signals rate acceleration. Reducing mETH exposure given ETH staking yield compression. Maintaining cmETH as risk premium remains attractive at 177bps. Reducing fBTC on negative BTC funding rate indicating bearish sentiment."

### Example 2: cmETH Premium Spike (May 14, 2026)

**Context**: A major AVS launch on Mantle's restaking layer created surge demand for cmETH. The cmETH/mETH premium widened from 180 bps to 340 bps within 48 hours.

**Macro Sentinel Output**:
```json
{
  "risk_score": 65,
  "usdy_yield_7d": 4.85,
  "usdy_yield_30d": 4.82,
  "meth_apy": 4.12,
  "cmeth_apy": 7.52,
  "btc_funding_rate": 0.0005
}
```

**Allocator Decision (Aggressive Vault)**:
- USDY: 1500 -> 1200 (-300 bps)
- mETH: 2000 -> 1500 (-500 bps)
- cmETH: 2500 -> 3500 (+1000 bps)
- fBTC: 2500 -> 2300 (-200 bps)
- USDC: 1500 -> 1500 (hold)

**Reasoning**: "cmETH premium at 340bps is historically elevated and likely reflects genuine AVS demand rather than artificial incentives. Rotating from mETH to cmETH captures the widened spread. Risk-reward favorable for aggressive profile given no slashing incidents in restaking layer history."

**Risk Guardian Assessment**: Alert Level 1 (advisory only). Concentration check passed -- cmETH at 35% is below the 60% max_single_asset limit. However, the guardian flagged that cmETH premium above 300bps warrants monitoring for potential mean reversion.

### Example 3: Market Stress Response (May 19, 2026)

**Context**: A major centralized exchange reported a security incident, triggering broad crypto selloff. ETH dropped 8% intraday. mETH oracle reported delayed withdrawals due to queue congestion.

**Macro Sentinel Output**:
```json
{
  "risk_score": 15,
  "usdy_yield_7d": 4.85,
  "usdy_yield_30d": 4.83,
  "meth_apy": 3.91,
  "cmeth_apy": 5.45,
  "btc_funding_rate": -0.0012
}
```

**Risk Guardian Action**: Immediately elevated to **Level 2 alert**. Called `vault.fireRiskAlert(2, "extreme_macro_stress_risk_score_15")` on-chain for all three vaults.

**Allocator Decision (All Vaults -- Emergency Defensive)**:
- Conservative: USDY 4500, mETH 1000, cmETH 0, fBTC 500, USDC 4000
- Balanced: USDY 4000, mETH 1500, cmETH 0, fBTC 1000, USDC 3500
- Aggressive: USDY 3000, mETH 2000, cmETH 500, fBTC 1500, USDC 3000

**Reasoning**: "Risk score at 15 indicates extreme stress. Unwinding all cmETH positions due to restaking withdrawal queue uncertainty. Maximizing USDY and USDC for capital preservation. Retaining minimal mETH and fBTC for recovery optionality."

**Outcome**: Over the following 72 hours, the market recovered 60% of losses. The aggressive vault's retained mETH and fBTC positions captured the bounce. Total drawdown was limited to 180 bps for conservative, 290 bps for balanced, and 410 bps for aggressive -- well within max drawdown limits.

### Example 4: USDY Allowlist Delay (May 22, 2026)

**Context**: A newly deployed vault (Balanced V2 at `0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA`) had not yet completed Ondo's allowlist registration when the first allocation cycle ran.

**Execution Router Behavior**:
1. Allocator requested 35% USDY allocation
2. USDYAdapter pre-flight check: `allowlist.isAllowed(vault)` returned `false`
3. Router redirected 35% to USDC with flag `usdy_fallback_active: true`
4. Decision record logged the compliance-enforced deviation

**Next Cycle (15 minutes later)**:
- Allowlist registration confirmed on-chain
- USDYAdapter pre-flight check: `allowlist.isAllowed(vault)` returned `true`
- Router successfully executed USDC -> USDY swap via Merchant Moe
- Portfolio achieved target allocation within two cycles (30 minutes total delay)

This example demonstrates MOSAIC's graceful degradation under compliance constraints. No funds were at risk, no transactions reverted on-chain, and the system self-healed without human intervention.

---

## Conclusion

The Mantle RWA stack provides MOSAIC with a rich, diversified yield universe that spans the risk spectrum from US Treasury obligations (USDY) through liquid staking (mETH) and restaking (cmETH) to Bitcoin-denominated yield (fBTC). The Protocol Adapter architecture ensures that each asset's unique characteristics -- oracle mechanics, compliance requirements, withdrawal constraints -- are properly encapsulated and handled by the agent pipeline.

The key innovation in MOSAIC V2 is the replacement of tokenized equity exposure (xStocks) with the cmETH restaking primitive. This shift reflects a strategic decision: the restaking risk premium is more predictable, more liquid, and more amenable to algorithmic management than equity market exposure, which depends on trading hours, market maker availability, and equity-specific regulatory constraints. By focusing on the USDY yield curve and the mETH/cmETH restaking spread, MOSAIC V2 can operate 24/7 without dependency on traditional market hours.
