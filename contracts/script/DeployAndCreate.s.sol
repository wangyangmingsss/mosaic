// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/DecisionLog.sol";
import "../src/VaultFactoryV2.sol";
import "../src/erc8004/IdentityRegistry.sol";
import "../src/erc8004/ReputationRegistry.sol";
import "../src/erc8004/ValidationRegistry.sol";

contract DeployAndCreate is Script {
    // Existing registries
    IdentityRegistry   constant identityReg   = IdentityRegistry(0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95);
    ReputationRegistry constant reputationReg = ReputationRegistry(0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9);
    ValidationRegistry constant validationReg = ValidationRegistry(0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d);

    // Existing adapters
    address constant usdyAdapter  = 0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0;
    address constant methAdapter  = 0xcAae1dBf111aF26655A4f40eaC4792978d3249c8;
    address constant cmethAdapter = 0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643;
    address constant fbtcAdapter  = 0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D;

    address constant USDC_MANTLE = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address agentEOA    = vm.envAddress("AGENT_EOA");
        vm.startBroadcast(deployerKey);

        // Fresh DecisionLog
        DecisionLog dl = new DecisionLog();
        console.log("DecisionLog  :", address(dl));

        // Fresh VaultFactory
        VaultFactoryV2 factory = new VaultFactoryV2(
            address(dl), agentEOA, USDC_MANTLE,
            identityReg, reputationReg, validationReg
        );
        console.log("VaultFactory :", address(factory));

        factory.setDefaultAdapter("USDY",  usdyAdapter);
        factory.setDefaultAdapter("mETH",  methAdapter);
        factory.setDefaultAdapter("cmETH", cmethAdapter);
        factory.setDefaultAdapter("fBTC",  fbtcAdapter);

        // Create 3 vaults
        address v1 = factory.createVault(
            1, 1, 1500, 6000,
            "ipfs://QmNiMzNu6E1RvzrTxHeZ6Uf59w17BBYiaNLjRVLxotnFjw"
        );
        console.log("Conservative :", v1);

        address v2 = factory.createVault(
            2, 2, 2000, 5000,
            "ipfs://QmduWJpWea1LSR12KGrmMj99Pum534FhfMmQ7bbuKqzUag"
        );
        console.log("Balanced     :", v2);

        address v3 = factory.createVault(
            3, 1, 3000, 5000,
            "ipfs://QmRhMMnzEyKLy8ciXgLELAQzVrSntLk4ZpDcHw1oMBbrWp"
        );
        console.log("Aggressive   :", v3);

        vm.stopBroadcast();
    }
}
