// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IDecisionLog {
    function writeRecord(address vault, uint256 decisionId, bytes32 recordHash) external;
    function getTotalDecisions(address vault) external view returns (uint256);
    function recordExists(bytes32 hash) external view returns (bool);
}
