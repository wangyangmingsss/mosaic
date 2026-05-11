// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";
import "../src/BenchmarkTracker.sol";

contract BenchmarkTrackerTest is Test {

    BenchmarkTracker tracker;
    address vault   = address(0x1234);
    address writer  = address(0x5678);
    address owner;

    function setUp() public {
        owner = address(this);
        tracker = new BenchmarkTracker();
        tracker.setWriter(vault, writer);
    }

    function test_recordSnapshot_basic() public {
        vm.prank(writer);
        tracker.recordSnapshot(vault, 10250, 10180);

        BenchmarkTracker.BenchmarkSnapshot[] memory snaps = tracker.getSnapshots(vault);
        assertEq(snaps.length, 1);
        assertEq(snaps[0].vaultNAVBps, 10250);
        assertEq(snaps[0].benchmarkNAVBps, 10180);
        assertEq(snaps[0].alphaBps, 70);  // +0.70%
    }

    function test_getLatestAlpha() public {
        vm.startPrank(writer);
        tracker.recordSnapshot(vault, 10100, 10050);
        tracker.recordSnapshot(vault, 10300, 10150);
        vm.stopPrank();

        int256 alpha = tracker.getLatestAlpha(vault);
        assertEq(alpha, 150);  // 10300 - 10150
    }

    function test_getCumulativeAlpha() public {
        vm.startPrank(writer);
        tracker.recordSnapshot(vault, 10100, 10050);  // alpha = 50
        tracker.recordSnapshot(vault, 10300, 10150);  // alpha = 150
        vm.stopPrank();

        int256 cumAlpha = tracker.getCumulativeAlpha(vault);
        assertEq(cumAlpha, 100);  // 150 - 50
    }

    function test_unauthorized_reverts() public {
        address rando = address(0x9999);
        vm.prank(rando);
        vm.expectRevert("Not authorized");
        tracker.recordSnapshot(vault, 10000, 10000);
    }

    function test_owner_can_write() public {
        // Owner should be able to write without being set as writer
        tracker.recordSnapshot(vault, 10500, 10200);

        BenchmarkTracker.BenchmarkSnapshot[] memory snaps = tracker.getSnapshots(vault);
        assertEq(snaps.length, 1);
        assertEq(snaps[0].alphaBps, 300);
    }

    function test_setWriter_only_owner() public {
        address rando = address(0x9999);
        vm.prank(rando);
        vm.expectRevert("Not owner");
        tracker.setWriter(vault, rando);
    }

    function test_empty_vault_returns_zero_alpha() public view {
        address emptyVault = address(0xAAAA);
        int256 alpha = tracker.getLatestAlpha(emptyVault);
        assertEq(alpha, 0);

        int256 cumAlpha = tracker.getCumulativeAlpha(emptyVault);
        assertEq(cumAlpha, 0);
    }

    function test_negative_alpha() public {
        // Agent underperforms benchmark
        vm.prank(writer);
        tracker.recordSnapshot(vault, 9800, 10100);

        int256 alpha = tracker.getLatestAlpha(vault);
        assertEq(alpha, -300);  // -3.00%
    }
}
