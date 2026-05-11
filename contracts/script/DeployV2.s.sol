// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/DecisionLog.sol";
import "../src/VaultFactoryV2.sol";
import "../src/erc8004/IdentityRegistry.sol";
import "../src/erc8004/ReputationRegistry.sol";
import "../src/erc8004/ValidationRegistry.sol";
import "../src/adapters/USDYAdapter.sol";
import "../src/adapters/METHAdapter.sol";
import "../src/adapters/FBTCAdapter.sol";

/// @notice Deploys MOSAIC V2 on Mantle Mainnet (Chain ID 5000).
///         Includes ERC-8004 Registries + Protocol Adapters + VaultFactory.
contract DeployV2 is Script {
    // Mantle Mainnet addresses
    address constant USDC_MANTLE  = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;
    address constant USDY_MANTLE  = 0x5bE26527e817998A7206475496fDE1E68957c5A6;
    address constant METH_MANTLE  = 0xcDA86A272531e8640cD7F1a92c01839911B90bb0;
    address constant CMETH_MANTLE = 0xE6829d9a7eE3040e1276Fa75293Bde931859e8fA;
    address constant WMNT_MANTLE  = 0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8;
    // fBTC — using WMNT as placeholder (fBTC address TBD)
    address constant FBTC_MANTLE  = 0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8;

    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address deployer    = vm.addr(deployerKey);
        address agentEOA    = vm.envAddress("AGENT_EOA");

        console.log("Deployer :", deployer);
        console.log("Agent EOA:", agentEOA);

        vm.startBroadcast(deployerKey);

        // ═══ Layer 1: ERC-8004 Registry singletons ═══
        IdentityRegistry   identityReg   = new IdentityRegistry();
        ReputationRegistry reputationReg = new ReputationRegistry();
        ValidationRegistry validationReg = new ValidationRegistry();

        console.log("IdentityRegistry  :", address(identityReg));
        console.log("ReputationRegistry:", address(reputationReg));
        console.log("ValidationRegistry:", address(validationReg));

        // ═══ Layer 2: DecisionLog ═══
        DecisionLog decisionLogV2 = new DecisionLog();
        console.log("DecisionLog V2    :", address(decisionLogV2));

        // ═══ Layer 3: Protocol Adapters ═══
        USDYAdapter usdyAdapter   = new USDYAdapter(25);
        METHAdapter methAdapter   = new METHAdapter(METH_MANTLE, 10);
        METHAdapter cmethAdapter  = new METHAdapter(CMETH_MANTLE, 10);
        FBTCAdapter fbtcAdapter   = new FBTCAdapter(FBTC_MANTLE, 10);

        console.log("USDYAdapter       :", address(usdyAdapter));
        console.log("METHAdapter       :", address(methAdapter));
        console.log("CMETHAdapter      :", address(cmethAdapter));
        console.log("FBTCAdapter       :", address(fbtcAdapter));

        // ═══ Layer 4: VaultFactory V2 ═══
        VaultFactoryV2 factory = new VaultFactoryV2(
            address(decisionLogV2),
            agentEOA,
            USDC_MANTLE,
            identityReg,
            reputationReg,
            validationReg
        );
        console.log("VaultFactoryV2    :", address(factory));

        // Configure default adapters
        factory.setDefaultAdapter("USDY",  address(usdyAdapter));
        factory.setDefaultAdapter("mETH",  address(methAdapter));
        factory.setDefaultAdapter("cmETH", address(cmethAdapter));
        factory.setDefaultAdapter("fBTC",  address(fbtcAdapter));

        // Transfer DecisionLog ownership to factory for vault authorization
        // Factory calls decisionLog.authorizeVault() in createVault()
        // Keep deployer as owner for emergency control
        // Grant factory authorization to act on behalf
        decisionLogV2.authorizeVault(address(factory));

        vm.stopBroadcast();

        // ═══ Summary ═══
        console.log("========== MOSAIC V2 DEPLOYMENT SUMMARY ==========");
        console.log("Network           : Mantle Mainnet (5000)");
        console.log("IdentityRegistry  :", address(identityReg));
        console.log("ReputationRegistry:", address(reputationReg));
        console.log("ValidationRegistry:", address(validationReg));
        console.log("DecisionLog V2    :", address(decisionLogV2));
        console.log("USDYAdapter       :", address(usdyAdapter));
        console.log("METHAdapter       :", address(methAdapter));
        console.log("CMETHAdapter      :", address(cmethAdapter));
        console.log("FBTCAdapter       :", address(fbtcAdapter));
        console.log("VaultFactoryV2    :", address(factory));
        console.log("==================================================");
    }
}
