// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

/// @title  BenchmarkTracker
/// @notice Records each vault's hypothetical performance under a fixed benchmark strategy.
///         Benchmark strategy: fixed weights per riskLevel, no rebalancing.
///         Alpha = agent actual performance - benchmark performance.
contract BenchmarkTracker {

    struct BenchmarkSnapshot {
        uint256 timestamp;
        uint256 vaultNAVBps;      // vault real NAV change vs initial, in bps
        uint256 benchmarkNAVBps;  // benchmark strategy hypothetical NAV, in bps
        int256  alphaBps;         // vaultNAVBps - benchmarkNAVBps (positive = agent outperforms)
    }

    // vault address -> ordered snapshots
    mapping(address => BenchmarkSnapshot[]) public snapshots;

    // vault address -> authorized writer (the agent)
    mapping(address => address) public authorizedWriter;

    address public owner;

    event SnapshotRecorded(
        address indexed vault,
        uint256 vaultNAVBps,
        uint256 benchmarkNAVBps,
        int256  alphaBps
    );

    modifier onlyWriter(address vault) {
        require(
            msg.sender == authorizedWriter[vault] || msg.sender == owner,
            "Not authorized"
        );
        _;
    }

    constructor() { owner = msg.sender; }

    function setWriter(address vault, address writer) external {
        require(msg.sender == owner, "Not owner");
        authorizedWriter[vault] = writer;
    }

    /// @notice Agent calls after each rebalance to record NAV comparison
    function recordSnapshot(
        address vault,
        uint256 vaultNAVBps,      // e.g. 10250 = +2.50% vs initial
        uint256 benchmarkNAVBps   // e.g. 10180 = +1.80% vs initial
    ) external onlyWriter(vault) {
        int256 alpha = int256(vaultNAVBps) - int256(benchmarkNAVBps);

        snapshots[vault].push(BenchmarkSnapshot({
            timestamp:        block.timestamp,
            vaultNAVBps:      vaultNAVBps,
            benchmarkNAVBps:  benchmarkNAVBps,
            alphaBps:         alpha
        }));

        emit SnapshotRecorded(vault, vaultNAVBps, benchmarkNAVBps, alpha);
    }

    function getSnapshots(address vault) external view returns (BenchmarkSnapshot[] memory) {
        return snapshots[vault];
    }

    function getLatestAlpha(address vault) external view returns (int256) {
        uint256 len = snapshots[vault].length;
        if (len == 0) return 0;
        return snapshots[vault][len - 1].alphaBps;
    }

    /// @notice Returns cumulative alpha (last snapshot - first snapshot)
    function getCumulativeAlpha(address vault) external view returns (int256) {
        uint256 len = snapshots[vault].length;
        if (len < 2) return 0;
        return snapshots[vault][len-1].alphaBps - snapshots[vault][0].alphaBps;
    }
}
