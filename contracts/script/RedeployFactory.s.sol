// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/DecisionLog.sol";
import "../src/VaultFactoryV2.sol";
import "../src/erc8004/IdentityRegistry.sol";
import "../src/erc8004/ReputationRegistry.sol";
import "../src/erc8004/ValidationRegistry.sol";

/// @notice Redeploys only VaultFactoryV2 (and a fresh DecisionLog) after fixing
///         MosaicVaultV2 to accept ERC721. Reuses existing registries and adapters.
contract RedeployFactory is Script {
    // Already deployed registries
    IdentityRegistry   constant identityReg   = IdentityRegistry(0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95);
    ReputationRegistry constant reputationReg = ReputationRegistry(0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9);
    ValidationRegistry constant validationReg = ValidationRegistry(0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d);

    // Already deployed adapters
    address constant usdyAdapter  = 0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0;
    address constant methAdapter  = 0xcAae1dBf111aF26655A4f40eaC4792978d3249c8;
    address constant cmethAdapter = 0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643;
    address constant fbtcAdapter  = 0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D;

    address constant USDC_MANTLE = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address agentEOA    = vm.envAddress("AGENT_EOA");
        vm.startBroadcast(deployerKey);

        // Fresh DecisionLog for V2
        DecisionLog dl2 = new DecisionLog();
        console.log("DecisionLog V2:", address(dl2));

        // Fresh VaultFactory
        VaultFactoryV2 factory = new VaultFactoryV2(
            address(dl2), agentEOA, USDC_MANTLE,
            identityReg, reputationReg, validationReg
        );
        console.log("VaultFactoryV2:", address(factory));

        factory.setDefaultAdapter("USDY",  usdyAdapter);
        factory.setDefaultAdapter("mETH",  methAdapter);
        factory.setDefaultAdapter("cmETH", cmethAdapter);
        factory.setDefaultAdapter("fBTC",  fbtcAdapter);

        dl2.authorizeVault(address(factory));

        vm.stopBroadcast();
    }
}
