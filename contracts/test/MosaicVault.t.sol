// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";
import "../src/MosaicVault.sol";
import "../src/DecisionLog.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @dev Minimal ERC-20 stub for tests
contract MockUSDC is ERC20 {
    constructor() ERC20("USD Coin", "USDC") {}
    function mint(address to, uint256 amount) external { _mint(to, amount); }
}

contract MosaicVaultTest is Test {
    MockUSDC     usdc;
    DecisionLog  log;
    MosaicVault  vault;

    address owner = address(0xA11CE);
    address agent = address(0xB0B);
    address user  = address(0xC0FFEE);

    MosaicVault.RiskProfile profile = MosaicVault.RiskProfile({
        riskLevel:          2,
        rebalanceFrequency: 2,
        maxDrawdownBps:     1500,
        maxSingleAssetBps:  6000
    });

    function setUp() public {
        vm.startPrank(owner);
        usdc  = new MockUSDC();
        log   = new DecisionLog();
        vault = new MosaicVault(
            IERC20(address(usdc)),
            "Mosaic Vault #1",
            "msV1",
            profile,
            agent,
            address(log)
        );
        log.authorizeVault(address(vault));
        vm.stopPrank();

        // Fund user
        usdc.mint(user, 10_000e6);
        vm.prank(user);
        usdc.approve(address(vault), type(uint256).max);
    }

    // ── Deposit / Withdraw ────────────────────────────────────────────────────

    function test_deposit_and_withdraw() public {
        vm.prank(user);
        uint256 shares = vault.deposit(1000e6, user);
        assertGt(shares, 0, "No shares minted");
        assertEq(vault.totalAssets(), 1000e6);

        vm.prank(user);
        uint256 assets = vault.redeem(shares, user, user);
        assertEq(assets, 1000e6);
    }

    // ── recordDecision ────────────────────────────────────────────────────────

    function test_record_decision_updates_state() public {
        MosaicVault.Allocation memory newAlloc = MosaicVault.Allocation({
            usdyBps:    4000,
            xstocksBps: 2500,
            methBps:    2000,
            fbtcBps:    1000,
            usdcBps:     500
        });

        bytes32 hash = keccak256("ipfs://test");

        vm.prank(agent);
        vault.recordDecision(hash, newAlloc, 50);

        assertEq(vault.agentIdentity().totalDecisions, 1);
        assertEq(vault.agentIdentity().successfulRebalances, 1);
        assertEq(vault.agentIdentity().cumulativePnLBps, 50);
        assertEq(vault.currentAllocation().usdyBps, 4000);
        assertEq(log.getTotalDecisions(address(vault)), 1);
    }

    function test_record_decision_rejects_invalid_allocation() public {
        MosaicVault.Allocation memory bad = MosaicVault.Allocation({
            usdyBps: 9999, xstocksBps: 0, methBps: 0, fbtcBps: 0, usdcBps: 0
        });
        vm.prank(agent);
        vm.expectRevert(MosaicVault.InvalidAllocation.selector);
        vault.recordDecision(keccak256("x"), bad, 0);
    }

    function test_record_decision_only_agent() public {
        MosaicVault.Allocation memory alloc = MosaicVault.Allocation({
            usdyBps: 5000, xstocksBps: 1500, methBps: 2000, fbtcBps: 500, usdcBps: 1000
        });
        vm.prank(user);
        vm.expectRevert(MosaicVault.NotAuthorizedAgent.selector);
        vault.recordDecision(keccak256("y"), alloc, 0);
    }

    // ── Risk Guardian pause ───────────────────────────────────────────────────

    function test_fire_risk_alert_level3_pauses_vault() public {
        vm.prank(agent);
        vault.fireRiskAlert(3, "Extreme market stress");

        assertTrue(vault.paused());

        // Deposit should revert while paused
        vm.prank(user);
        vm.expectRevert(MosaicVault.VaultIsPaused.selector);
        vault.deposit(100e6, user);
    }

    function test_resume_vault_by_owner() public {
        vm.prank(agent);
        vault.fireRiskAlert(3, "test");

        vm.prank(owner);
        vault.resumeVault();
        assertFalse(vault.paused());
    }

    // ── updateMetadataURI ────────────────────────────────────────────────────

    function test_update_metadata_uri() public {
        string memory uri = "ipfs://QmTest123";
        vm.prank(agent);
        vault.updateMetadataURI(uri);
        assertEq(vault.agentIdentity().metadataURI, uri);
    }

    // ── Duplicate record hash ────────────────────────────────────────────────

    function test_duplicate_record_hash_reverts() public {
        MosaicVault.Allocation memory alloc = MosaicVault.Allocation({
            usdyBps: 5000, xstocksBps: 1500, methBps: 2000, fbtcBps: 500, usdcBps: 1000
        });
        bytes32 hash = keccak256("same");

        vm.prank(agent);
        vault.recordDecision(hash, alloc, 0);

        vm.prank(agent);
        vm.expectRevert(DecisionLog.DuplicateRecord.selector);
        vault.recordDecision(hash, alloc, 0);
    }
}
