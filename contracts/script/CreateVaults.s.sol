// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/MosaicVault.sol";
import "../src/DecisionLog.sol";

contract CreateVaults is Script {
    address constant USDC_MANTLE = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;
    address constant DECISION_LOG = 0x035a459893EC171615B2Fd747d3EDd1eB0A5526D;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address agentEOA = vm.envAddress("AGENT_EOA");

        vm.startBroadcast(deployerKey);

        DecisionLog dlog = DecisionLog(DECISION_LOG);

        // Vault 1: Conservative
        MosaicVault v1 = new MosaicVault(
            IERC20(USDC_MANTLE),
            "Mosaic Vault #1 Conservative",
            "msV1",
            MosaicVault.RiskProfile({
                riskLevel: 1,
                rebalanceFrequency: 2,
                maxDrawdownBps: 1000,
                maxSingleAssetBps: 6000
            }),
            agentEOA,
            DECISION_LOG
        );
        dlog.authorizeVault(address(v1));
        console.log("Conservative Vault:", address(v1));

        // Vault 2: Balanced
        MosaicVault v2 = new MosaicVault(
            IERC20(USDC_MANTLE),
            "Mosaic Vault #2 Balanced",
            "msV2",
            MosaicVault.RiskProfile({
                riskLevel: 2,
                rebalanceFrequency: 2,
                maxDrawdownBps: 1500,
                maxSingleAssetBps: 6000
            }),
            agentEOA,
            DECISION_LOG
        );
        dlog.authorizeVault(address(v2));
        console.log("Balanced Vault:", address(v2));

        // Vault 3: Aggressive
        MosaicVault v3 = new MosaicVault(
            IERC20(USDC_MANTLE),
            "Mosaic Vault #3 Aggressive",
            "msV3",
            MosaicVault.RiskProfile({
                riskLevel: 3,
                rebalanceFrequency: 1,
                maxDrawdownBps: 2500,
                maxSingleAssetBps: 7000
            }),
            agentEOA,
            DECISION_LOG
        );
        dlog.authorizeVault(address(v3));
        console.log("Aggressive Vault:", address(v3));

        vm.stopBroadcast();

        console.log("===== VAULT SUMMARY =====");
        console.log("Conservative:", address(v1));
        console.log("Balanced:    ", address(v2));
        console.log("Aggressive:  ", address(v3));
    }
}
