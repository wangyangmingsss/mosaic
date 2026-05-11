// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/DecisionLog.sol";
import "../src/VaultFactory.sol";

/// @notice Deploys DecisionLog → VaultFactory to Mantle testnet / mainnet.
///         Run:
///           forge script script/Deploy.s.sol:Deploy \
///             --rpc-url $MANTLE_RPC \
///             --broadcast \
///             --verify \
///             --verifier-url https://explorer.mantle.xyz/api \
///             --etherscan-api-key $MANTLE_EXPLORER_KEY
contract Deploy is Script {

    // ── Mantle mainnet addresses ──────────────────────────────────────────────
    // Update these if Mantle deploys new canonical addresses.
    address constant USDC_MANTLE   = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;
    address constant METH_MANTLE   = 0xcDA86A272531e8640cD7F1a92c01839911B90bb0;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address deployer    = vm.addr(deployerKey);
        address agentEOA    = vm.envAddress("AGENT_EOA"); // mulerun executor wallet

        console.log("Deployer :", deployer);
        console.log("Agent EOA:", agentEOA);

        vm.startBroadcast(deployerKey);

        // 1. DecisionLog
        DecisionLog log = new DecisionLog();
        console.log("DecisionLog deployed at:", address(log));

        // 2. VaultFactory  (USDC as deposit asset)
        VaultFactory factory = new VaultFactory(
            address(log),
            agentEOA,
            USDC_MANTLE
        );
        console.log("VaultFactory deployed at:", address(factory));

        // 3. Transfer DecisionLog ownership to factory so it can authorise vaults
        log.authorizeVault(address(factory)); // factory itself can grant sub-vaults
        // Note: ownership remains with deployer for emergency revocations

        vm.stopBroadcast();

        // ── Summary ────────────────────────────────────────────────────────
        console.log("===== DEPLOYMENT SUMMARY =====");
        console.log("DecisionLog :", address(log));
        console.log("VaultFactory:", address(factory));
        console.log("Network     : Mantle");
    }
}
