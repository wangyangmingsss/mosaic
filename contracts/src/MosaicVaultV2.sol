// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./interfaces/IDecisionLog.sol";
import "./erc8004/interfaces/IIdentityRegistry.sol";
import "./erc8004/interfaces/IReputationRegistry.sol";
import "./erc8004/interfaces/IValidationRegistry.sol";
import "./adapters/IProtocolAdapter.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

/// @title  MosaicVaultV2
/// @notice ERC-4626 vault with ERC-8004 agent identity via Registry pattern.
///         Upgraded: xstocksBps replaced by cmethBps for USDY/mETH/cmETH strategy.
contract MosaicVaultV2 is ERC4626, Ownable, ReentrancyGuard, IERC721Receiver {

    // ── Structs ──────────────────────────────────────────────────────────────

    struct RiskProfile {
        uint8  riskLevel;
        uint8  rebalanceFrequency;
        uint16 maxDrawdownBps;
        uint16 maxSingleAssetBps;
    }

    /// @notice v2 Allocation: cmethBps replaces xstocksBps
    struct Allocation {
        uint16 usdyBps;    // USDY – tokenized US Treasury yield
        uint16 cmethBps;   // cmETH – restaked mETH
        uint16 methBps;    // mETH – Mantle ETH liquid staking
        uint16 fbtcBps;    // fBTC – BTC restaking
        uint16 usdcBps;    // USDC – cash reserve
    }

    // ── ERC-8004 Registry References ─────────────────────────────────────────

    IIdentityRegistry   public immutable identityRegistry;
    IReputationRegistry public immutable reputationRegistry;
    IValidationRegistry public immutable validationRegistry;
    uint256 public immutable agentTokenId;

    // ── State ────────────────────────────────────────────────────────────────

    RiskProfile public riskProfile;
    Allocation  public currentAllocation;

    address public authorizedAgent;
    address public decisionLog;
    bool    public paused;

    /// @dev adapter routing: keccak256(symbol) => adapter address
    mapping(bytes32 => address) public adapters;

    uint256 public totalDecisions;
    uint256 public successfulRebalances;
    int256  public cumulativePnLBps;

    // ── Events ───────────────────────────────────────────────────────────────

    event AgentRebalanced(uint256 indexed decisionId, bytes32 recordHash);
    event AllocationUpdated(Allocation newAlloc);
    event RiskAlertFired(uint8 alertLevel, string reason);
    event VaultPaused(string reason);
    event VaultResumed();
    event AdapterSet(bytes32 indexed symbol, address adapter);

    // ── Errors ───────────────────────────────────────────────────────────────

    error NotAuthorizedAgent();
    error VaultIsPaused();
    error InvalidAllocation();
    error ZeroAddress();

    // ── Modifiers ────────────────────────────────────────────────────────────

    modifier onlyAgent() {
        if (msg.sender != authorizedAgent) revert NotAuthorizedAgent();
        _;
    }

    modifier whenNotPaused() {
        if (paused) revert VaultIsPaused();
        _;
    }

    // ── Constructor ──────────────────────────────────────────────────────────

    constructor(
        IERC20        _asset,
        string memory _name,
        string memory _symbol,
        RiskProfile memory _profile,
        address       _agent,
        address       _decisionLog,
        IIdentityRegistry   _identityRegistry,
        IReputationRegistry _reputationRegistry,
        IValidationRegistry _validationRegistry,
        uint256             _agentTokenId
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

        identityRegistry   = _identityRegistry;
        reputationRegistry = _reputationRegistry;
        validationRegistry = _validationRegistry;
        agentTokenId       = _agentTokenId;

        currentAllocation = _defaultAllocation(_profile.riskLevel);
    }

    // ── Agent-callable ───────────────────────────────────────────────────────

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
        totalDecisions++;
        successfulRebalances++;
        cumulativePnLBps += pnlDeltaBps;

        IDecisionLog(decisionLog).writeRecord(
            address(this),
            totalDecisions,
            recordHash
        );

        // Post to ERC-8004 ValidationRegistry as initial trust signal
        validationRegistry.postValidation(
            agentTokenId,
            recordHash,
            true,
            IValidationRegistry.ValidationKind.Trusted,
            ""
        );

        emit AgentRebalanced(totalDecisions, recordHash);
        emit AllocationUpdated(newAlloc);
    }

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

    function resumeVault() external onlyOwner {
        paused = false;
        emit VaultResumed();
    }

    function updateAgentURI(string calldata newURI) external onlyAgent {
        identityRegistry.updateURI(agentTokenId, newURI);
    }

    function setAuthorizedAgent(address newAgent) external onlyOwner {
        if (newAgent == address(0)) revert ZeroAddress();
        authorizedAgent = newAgent;
    }

    function setAdapter(bytes32 symbol, address adapter) external onlyOwner {
        adapters[symbol] = adapter;
        emit AdapterSet(symbol, adapter);
    }

    // ── ERC-4626 overrides ───────────────────────────────────────────────────

    function deposit(uint256 assets, address receiver)
        public override whenNotPaused returns (uint256)
    {
        return super.deposit(assets, receiver);
    }

    function mint(uint256 shares, address receiver)
        public override whenNotPaused returns (uint256)
    {
        return super.mint(shares, receiver);
    }

    // ── View helpers ─────────────────────────────────────────────────────────

    function getAllocation() external view returns (Allocation memory) {
        return currentAllocation;
    }

    function getReputationScore() external view returns (int256) {
        return reputationRegistry.getAggregateScore(agentTokenId);
    }

    // ── ERC-721 Receiver ───────────────────────────────────────────────────

    function onERC721Received(address, address, uint256, bytes calldata)
        external pure override returns (bytes4)
    {
        return IERC721Receiver.onERC721Received.selector;
    }

    // ── Internal ─────────────────────────────────────────────────────────────

    function _validateAllocation(Allocation calldata a) internal pure {
        uint256 total = uint256(a.usdyBps) + a.cmethBps + a.methBps + a.fbtcBps + a.usdcBps;
        if (total != 10_000) revert InvalidAllocation();
    }

    function _defaultAllocation(uint8 riskLevel) internal pure returns (Allocation memory) {
        if (riskLevel == 1) {
            // Conservative: heavy USDY, moderate mETH, low cmETH
            return Allocation({
                usdyBps: 5000, cmethBps: 500, methBps: 2500, fbtcBps: 500, usdcBps: 1500
            });
        } else if (riskLevel == 2) {
            // Balanced
            return Allocation({
                usdyBps: 3000, cmethBps: 1500, methBps: 2500, fbtcBps: 1000, usdcBps: 2000
            });
        } else {
            // Aggressive: heavy mETH/cmETH
            return Allocation({
                usdyBps: 1500, cmethBps: 3000, methBps: 2500, fbtcBps: 1500, usdcBps: 1500
            });
        }
    }
}
