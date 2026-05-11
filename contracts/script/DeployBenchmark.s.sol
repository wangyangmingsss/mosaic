// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Script.sol";
import "../src/BenchmarkTracker.sol";

contract DeployBenchmark is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        address agentEOA    = vm.envAddress("AGENT_EOA");

        vm.startBroadcast(deployerKey);

        BenchmarkTracker tracker = new BenchmarkTracker();
        console.log("BenchmarkTracker deployed at:", address(tracker));

        vm.stopBroadcast();
    }
}
