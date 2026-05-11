// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./MosaicVault.sol";
import "./DecisionLog.sol";

/// @title  VaultFactory
/// @notice One-stop shop for deploying a new MosaicVault.
///         Deploys the vault, authorises it in DecisionLog, and emits an event
///         that the Web Explorer indexes.
contract VaultFactory {

    address public immutable decisionLog;
    address public immutable authorizedAgent; // global mulerun executor
    address public immutable usdc;            // deposit token on Mantle

    address[] public allVaults;

    event VaultCreated(
        address indexed vault,
        address indexed owner,
        uint8   riskLevel,
        uint256 timestamp
    );

    error ZeroAddress();

    constructor(address _decisionLog, address _agent, address _usdc) {
        if (_decisionLog == address(0) || _agent == address(0) || _usdc == address(0))
            revert ZeroAddress();
        decisionLog     = _decisionLog;
        authorizedAgent = _agent;
        usdc            = _usdc;
    }

    /// @notice Deploy a new MosaicVault for the caller.
    /// @param  riskLevel          1 = conservative, 2 = balanced, 3 = aggressive
    /// @param  rebalanceFrequency 1 = daily, 2 = weekly, 3 = monthly
    /// @param  maxDrawdownBps     e.g. 1500 = 15%
    /// @param  maxSingleAssetBps  e.g. 6000 = 60%
    function createVault(
        uint8  riskLevel,
        uint8  rebalanceFrequency,
        uint16 maxDrawdownBps,
        uint16 maxSingleAssetBps
    ) external returns (address vault) {
        MosaicVault.RiskProfile memory profile = MosaicVault.RiskProfile({
            riskLevel:          riskLevel,
            rebalanceFrequency: rebalanceFrequency,
            maxDrawdownBps:     maxDrawdownBps,
            maxSingleAssetBps:  maxSingleAssetBps
        });

        string memory name   = string.concat("Mosaic Vault #", _toString(allVaults.length + 1));
        string memory symbol = string.concat("msV", _toString(allVaults.length + 1));

        MosaicVault v = new MosaicVault(
            IERC20(usdc),
            name,
            symbol,
            profile,
            authorizedAgent,
            decisionLog
        );

        // Transfer vault ownership to the creator
        v.transferOwnership(msg.sender);

        // Authorise vault to write to DecisionLog
        DecisionLog(decisionLog).authorizeVault(address(v));

        allVaults.push(address(v));

        emit VaultCreated(address(v), msg.sender, riskLevel, block.timestamp);
        return address(v);
    }

    function totalVaults() external view returns (uint256) {
        return allVaults.length;
    }

    // ─── util ────────────────────────────────────────────────────────────────

    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) { digits++; temp /= 10; }
        bytes memory buf = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buf[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buf);
    }
}
