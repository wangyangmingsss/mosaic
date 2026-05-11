// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/VaultFactoryV2.sol";

/// @notice Creates 3 V2 vaults (Conservative, Balanced, Aggressive) on Mantle Mainnet.
contract CreateVaultsV2 is Script {
    address constant FACTORY_V2 = 0x47Fd2d17a8536770b469Bece132Eb0e250CA22C7;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerKey);

        VaultFactoryV2 factory = VaultFactoryV2(FACTORY_V2);

        // Conservative vault
        address v1 = factory.createVault(
            1,    // riskLevel
            1,    // rebalanceFrequency (daily)
            1500, // maxDrawdownBps (15%)
            6000, // maxSingleAssetBps (60%)
            "ipfs://QmNiMzNu6E1RvzrTxHeZ6Uf59w17BBYiaNLjRVLxotnFjw"
        );
        console.log("Conservative V2:", v1);

        // Balanced vault
        address v2 = factory.createVault(
            2,
            2,
            2000,
            5000,
            "ipfs://QmduWJpWea1LSR12KGrmMj99Pum534FhfMmQ7bbuKqzUag"
        );
        console.log("Balanced V2    :", v2);

        // Aggressive vault
        address v3 = factory.createVault(
            3,
            1,
            3000,
            5000,
            "ipfs://QmRhMMnzEyKLy8ciXgLELAQzVrSntLk4ZpDcHw1oMBbrWp"
        );
        console.log("Aggressive V2  :", v3);

        vm.stopBroadcast();
    }
}
