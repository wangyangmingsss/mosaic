// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title  DecisionLog
/// @notice Immutable on-chain registry of every Mosaic agent decision.
///         Each entry stores the keccak256 hash of the full DecisionRecord JSON
///         (which lives on IPFS). This gives verifiable, low-cost auditability:
///         the chain proves *what was decided and when*; IPFS stores *why*.
contract DecisionLog {

    // ─────────────────────────────────────────────────────────────────────────
    // Structs
    // ─────────────────────────────────────────────────────────────────────────

    struct LogEntry {
        address vault;        // which MosaicVault made the decision
        uint256 decisionId;   // monotonically increasing per vault
        bytes32 recordHash;   // keccak256 of the IPFS-hosted JSON record
        uint256 timestamp;    // block.timestamp
        uint256 blockNumber;  // block.number for cross-referencing
    }

    // ─────────────────────────────────────────────────────────────────────────
    // State
    // ─────────────────────────────────────────────────────────────────────────

    /// @dev vault address  →  ordered list of log entries
    mapping(address => LogEntry[]) private _vaultLogs;

    /// @dev hash → true once recorded; prevents duplicates
    mapping(bytes32 => bool) public recordExists;

    /// @dev Set of vault addresses that are authorised to write (owner-managed)
    mapping(address => bool) public authorizedVaults;

    address public owner;

    // ─────────────────────────────────────────────────────────────────────────
    // Events
    // ─────────────────────────────────────────────────────────────────────────

    event DecisionRecorded(
        address indexed vault,
        uint256 indexed decisionId,
        bytes32         recordHash,
        uint256         timestamp
    );

    event VaultAuthorized(address indexed vault);
    event VaultRevoked(address indexed vault);

    // ─────────────────────────────────────────────────────────────────────────
    // Errors
    // ─────────────────────────────────────────────────────────────────────────

    error NotAuthorized();
    error DuplicateRecord();
    error ZeroHash();

    // ─────────────────────────────────────────────────────────────────────────
    // Constructor
    // ─────────────────────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Admin
    // ─────────────────────────────────────────────────────────────────────────

    /// @notice Allow a vault to write records.  Called by the factory after
    ///         deploying a new MosaicVault.
    function authorizeVault(address vault) external {
        if (msg.sender != owner) revert NotAuthorized();
        authorizedVaults[vault] = true;
        emit VaultAuthorized(vault);
    }

    function revokeVault(address vault) external {
        if (msg.sender != owner) revert NotAuthorized();
        authorizedVaults[vault] = false;
        emit VaultRevoked(vault);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Write
    // ─────────────────────────────────────────────────────────────────────────

    /// @notice Record a decision.  Called by MosaicVault.recordDecision().
    function writeRecord(
        address vault,
        uint256 decisionId,
        bytes32 recordHash
    ) external {
        if (!authorizedVaults[vault] && msg.sender != vault)
            revert NotAuthorized();
        if (recordHash == bytes32(0)) revert ZeroHash();
        if (recordExists[recordHash]) revert DuplicateRecord();

        recordExists[recordHash] = true;

        _vaultLogs[vault].push(LogEntry({
            vault:       vault,
            decisionId:  decisionId,
            recordHash:  recordHash,
            timestamp:   block.timestamp,
            blockNumber: block.number
        }));

        emit DecisionRecorded(vault, decisionId, recordHash, block.timestamp);
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Read
    // ─────────────────────────────────────────────────────────────────────────

    function getVaultHistory(address vault)
        external view returns (LogEntry[] memory)
    {
        return _vaultLogs[vault];
    }

    function getTotalDecisions(address vault)
        external view returns (uint256)
    {
        return _vaultLogs[vault].length;
    }

    function getEntry(address vault, uint256 index)
        external view returns (LogEntry memory)
    {
        return _vaultLogs[vault][index];
    }

    function getLatestEntry(address vault)
        external view returns (LogEntry memory)
    {
        uint256 len = _vaultLogs[vault].length;
        require(len > 0, "No entries");
        return _vaultLogs[vault][len - 1];
    }
}
