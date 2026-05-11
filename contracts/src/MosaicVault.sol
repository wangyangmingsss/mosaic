// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./interfaces/IDecisionLog.sol";

/// @title  MosaicVault
/// @notice ERC-4626 compliant vault extended with ERC-8004 agent identity.
///         Each vault instance represents one autonomous RWA portfolio managed
///         by the Mosaic mulerun agent pipeline.
contract MosaicVault is ERC4626, Ownable, ReentrancyGuard {

    // ─────────────────────────────────────────────────────────────────────────
    // Structs
    // ─────────────────────────────────────────────────────────────────────────

    /// @notice ERC-8004 agent identity metadata stored on-chain.
    struct AgentIdentity {
        string  modelDeclaration;      // e.g. "mulerun-mosaic-v1"
        uint256 createdAt;             // unix timestamp
        uint256 totalDecisions;        // total rebalance count
        uint256 successfulRebalances;  // decisions executed without error
        int256  cumulativePnLBps;      // cumulative PnL vs benchmark, in basis points
        string  metadataURI;           // IPFS link to full performance JSON
    }

    /// @notice User-defined risk and rebalancing constraints.
    struct RiskProfile {
        uint8  riskLevel;          // 1 = conservative, 2 = balanced, 3 = aggressive
        uint8  rebalanceFrequency; // 1 = daily, 2 = weekly, 3 = monthly
        uint16 maxDrawdownBps;     // e.g. 1500 = 15% max drawdown
        uint16 maxSingleAssetBps;  // e.g. 6000 = 60% single-asset cap
    }

    /// @notice Current target allocation across RWA asset classes (sum = 10000 bps).
    struct Allocation {
        uint16 usdyBps;    // USDY – tokenised US Treasury yield
        uint16 xstocksBps; // xStocks aggregate (TSLAx, NVDAx, AAPLx, …)
        uint16 methBps;    // mETH – Mantle ETH liquid staking
        uint16 fbtcBps;    // fBTC – BTC restaking via Babylon
        uint16 usdcBps;    // USDC – cash reserve / dry powder
    }

    // ─────────────────────────────────────────────────────────────────────────
    // State
    // ─────────────────────────────────────────────────────────────────────────

    AgentIdentity  public agentIdentity;
    RiskProfile    public riskProfile;
    Allocation     public currentAllocation;

    address public authorizedAgent;  // mulerun executor EOA
    address public decisionLog;      // DecisionLog contract address

    bool public paused;              // set by Risk Guardian (alert level 3)

    // ─────────────────────────────────────────────────────────────────────────
    // Events
    // ─────────────────────────────────────────────────────────────────────────

    event AgentRebalanced(uint256 indexed decisionId, bytes32 recordHash);
    event AllocationUpdated(Allocation newAlloc);
    event RiskAlertFired(uint8 alertLevel, string reason);
    event VaultPaused(string reason);
    event VaultResumed();
    event MetadataURIUpdated(string uri);

    // ─────────────────────────────────────────────────────────────────────────
    // Errors
    // ─────────────────────────────────────────────────────────────────────────

    error NotAuthorizedAgent();
    error VaultIsPaused();
    error InvalidAllocation();
    error ZeroAddress();

    // ─────────────────────────────────────────────────────────────────────────
    // Modifiers
    // ─────────────────────────────────────────────────────────────────────────

    modifier onlyAgent() {
        if (msg.sender != authorizedAgent) revert NotAuthorizedAgent();
        _;
    }

    modifier whenNotPaused() {
        if (paused) revert VaultIsPaused();
        _;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Constructor
    // ─────────────────────────────────────────────────────────────────────────

    constructor(
        IERC20        _asset,
        string memory _name,
        string memory _symbol,
        RiskProfile memory _profile,
        address       _agent,
        address       _decisionLog
    )
        ERC4626(_asset)
        ERC20(_name, _symbol)
        Ownable(msg.sender)
    {
        if (_agent       == address(0)) revert ZeroAddress();
        if (_decisionLog == address(0)) revert ZeroAddress();

        riskProfile     = _profile;
        authorizedAgent = _agent;
        decisionLog     = _decisionLog;

        agentIdentity = AgentIdentity({
            modelDeclaration:    "mulerun-mosaic-v1",
            createdAt:           block.timestamp,
            totalDecisions:      0,
            successfulRebalances: 0,
            cumulativePnLBps:    0,
            metadataURI:         ""
        });

        // Default allocation depends on risk level
        currentAllocation = _defaultAllocation(_profile.riskLevel);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Agent-callable functions (called by mulerun pipeline)
    // ─────────────────────────────────────────────────────────────────────────

    /// @notice Record a completed rebalance decision on-chain.
    /// @param  recordHash  keccak256 of the full DecisionRecord JSON (stored on IPFS).
    /// @param  newAlloc    Target allocation after this rebalance.
    /// @param  pnlDeltaBps Incremental PnL change in basis points.
    function recordDecision(
        bytes32          recordHash,
        Allocation calldata newAlloc,
        int256           pnlDeltaBps
    )
        external
        onlyAgent
        nonReentrant
    {
        _validateAllocation(newAlloc);

        currentAllocation = newAlloc;
        agentIdentity.totalDecisions++;
        agentIdentity.successfulRebalances++;
        agentIdentity.cumulativePnLBps += pnlDeltaBps;

        // Write the record hash to the DecisionLog contract
        IDecisionLog(decisionLog).writeRecord(
            address(this),
            agentIdentity.totalDecisions,
            recordHash
        );

        emit AgentRebalanced(agentIdentity.totalDecisions, recordHash);
        emit AllocationUpdated(newAlloc);
    }

    /// @notice Risk Guardian fires an alert; level 3 pauses the vault.
    function fireRiskAlert(uint8 level, string calldata reason)
        external
        onlyAgent
    {
        emit RiskAlertFired(level, reason);
        if (level >= 3) {
            paused = true;
            emit VaultPaused(reason);
        }
    }

    /// @notice Resume the vault after a level-3 pause (owner only).
    function resumeVault() external onlyOwner {
        paused = false;
        emit VaultResumed();
    }

    /// @notice Update the IPFS metadata URI after Scribe uploads new stats.
    function updateMetadataURI(string calldata uri) external onlyAgent {
        agentIdentity.metadataURI = uri;
        emit MetadataURIUpdated(uri);
    }

    /// @notice Change the authorized agent address (owner only).
    function setAuthorizedAgent(address newAgent) external onlyOwner {
        if (newAgent == address(0)) revert ZeroAddress();
        authorizedAgent = newAgent;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // ERC-4626 overrides – enforce pause
    // ─────────────────────────────────────────────────────────────────────────

    function deposit(uint256 assets, address receiver)
        public
        override
        whenNotPaused
        returns (uint256)
    {
        return super.deposit(assets, receiver);
    }

    function mint(uint256 shares, address receiver)
        public
        override
        whenNotPaused
        returns (uint256)
    {
        return super.mint(shares, receiver);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // View helpers
    // ─────────────────────────────────────────────────────────────────────────

    /// @notice Return all agent identity data in one call (for Explorer).
    function getAgentIdentity() external view returns (AgentIdentity memory) {
        return agentIdentity;
    }

    /// @notice Return current allocation snapshot.
    function getAllocation() external view returns (Allocation memory) {
        return currentAllocation;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Internal helpers
    // ─────────────────────────────────────────────────────────────────────────

    function _validateAllocation(Allocation calldata a) internal pure {
        uint256 total = uint256(a.usdyBps) + a.xstocksBps + a.methBps + a.fbtcBps + a.usdcBps;
        if (total != 10_000) revert InvalidAllocation();
    }

    function _defaultAllocation(uint8 riskLevel) internal pure returns (Allocation memory) {
        if (riskLevel == 1) {
            return Allocation({ usdyBps: 5000, xstocksBps: 1500, methBps: 2000, fbtcBps:  500, usdcBps: 1000 });
        } else if (riskLevel == 2) {
            return Allocation({ usdyBps: 3000, xstocksBps: 3000, methBps: 2500, fbtcBps: 1000, usdcBps:  500 });
        } else {
            return Allocation({ usdyBps: 1500, xstocksBps: 4500, methBps: 2500, fbtcBps: 1500, usdcBps:    0 });
        }
    }
}
