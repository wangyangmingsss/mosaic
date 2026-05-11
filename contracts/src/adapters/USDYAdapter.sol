// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IProtocolAdapter} from "./IProtocolAdapter.sol";
import {IMoeLBRouter} from "../interfaces/external/IMoeLBRouter.sol";
import {IMoeLBQuoter} from "../interfaces/external/IMoeLBQuoter.sol";

interface IUSDY {
    function allowlist() external view returns (address);
}

interface IAllowlist {
    function isAllowed(address account) external view returns (bool);
}

interface IERC20Meta is IERC20 {
    function decimals() external view returns (uint8);
}

/**
 * @title USDYAdapter
 * @notice Ondo USDY adapter with allowlist/blocklist compliance checks.
 *         Routes through Merchant Moe LB v2.2 for USDY/USDC swaps.
 */
contract USDYAdapter is IProtocolAdapter, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public constant MOE_LB_ROUTER = 0x013e138EF6008ae5FDFDE29700e3f2Bc61d21E3a;
    address public constant MOE_LB_QUOTER = 0x501b8AFd35df20f531fF45F6f695793AC3316c85;
    address public constant USDC = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;
    address public constant USDY_TOKEN = 0x5bE26527e817998A7206475496fDE1E68957c5A6;

    uint16 public immutable BIN_STEP;

    event OnboardingRequired(address indexed account, string reason);
    event SwapExecuted(
        address indexed caller,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    constructor(uint16 binStep_) Ownable(msg.sender) {
        BIN_STEP = binStep_;
    }

    function targetAsset() external pure override returns (address) {
        return USDY_TOKEN;
    }

    function buy(uint256 amountInUSDC, uint256 minAmountOut, address recipient)
        external override nonReentrant returns (ExecutionReceipt memory)
    {
        require(_isOnAllowlist(recipient), "USDY: recipient not on allowlist");
        require(_isOnAllowlist(address(this)), "USDY: adapter not on allowlist");

        IERC20(USDC).safeTransferFrom(msg.sender, address(this), amountInUSDC);
        IERC20(USDC).forceApprove(MOE_LB_ROUTER, amountInUSDC);

        IMoeLBRouter.Path memory path = _buildPath(USDC, USDY_TOKEN);
        uint256 amountOut = IMoeLBRouter(MOE_LB_ROUTER).swapExactTokensForTokens(
            amountInUSDC, minAmountOut, path, recipient, block.timestamp + 300
        );

        emit SwapExecuted(msg.sender, USDC, USDY_TOKEN, amountInUSDC, amountOut);

        return ExecutionReceipt({
            protocol: MOE_LB_ROUTER,
            amountIn: amountInUSDC,
            amountOut: amountOut,
            gasUsed: 0,
            protocolTxId: bytes32(0)
        });
    }

    function sell(uint256 amountIn, uint256 minAmountOut, address recipient)
        external override nonReentrant returns (ExecutionReceipt memory)
    {
        IERC20(USDY_TOKEN).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(USDY_TOKEN).forceApprove(MOE_LB_ROUTER, amountIn);

        IMoeLBRouter.Path memory path = _buildPath(USDY_TOKEN, USDC);
        uint256 amountOut = IMoeLBRouter(MOE_LB_ROUTER).swapExactTokensForTokens(
            amountIn, minAmountOut, path, recipient, block.timestamp + 300
        );

        emit SwapExecuted(msg.sender, USDY_TOKEN, USDC, amountIn, amountOut);

        return ExecutionReceipt({
            protocol: MOE_LB_ROUTER,
            amountIn: amountIn,
            amountOut: amountOut,
            gasUsed: 0,
            protocolTxId: bytes32(0)
        });
    }

    function quoteBuy(uint256 amountInUSDC) external view override returns (uint256) {
        address[] memory route = new address[](2);
        route[0] = USDC;
        route[1] = USDY_TOKEN;
        IMoeLBQuoter.Quote memory q = IMoeLBQuoter(MOE_LB_QUOTER).findBestPathFromAmountIn(
            route, uint128(amountInUSDC)
        );
        return q.amounts.length > 1 ? q.amounts[1] : 0;
    }

    function priceUSDC() external view override returns (uint256) {
        uint256 oneUnit = 10 ** IERC20Meta(USDY_TOKEN).decimals();
        address[] memory route = new address[](2);
        route[0] = USDY_TOKEN;
        route[1] = USDC;
        IMoeLBQuoter.Quote memory q = IMoeLBQuoter(MOE_LB_QUOTER).findBestPathFromAmountIn(
            route, uint128(oneUnit)
        );
        return q.amounts.length > 1 ? q.amounts[1] : 0;
    }

    function _isOnAllowlist(address account) internal view returns (bool) {
        try IUSDY(USDY_TOKEN).allowlist() returns (address allowlistAddr) {
            try IAllowlist(allowlistAddr).isAllowed(account) returns (bool ok) {
                return ok;
            } catch {
                return false;
            }
        } catch {
            // If USDY doesn't expose allowlist getter, assume allowed
            return true;
        }
    }

    function _buildPath(address tokenIn, address tokenOut)
        internal view returns (IMoeLBRouter.Path memory)
    {
        address[] memory tokens = new address[](2);
        tokens[0] = tokenIn;
        tokens[1] = tokenOut;

        uint256[] memory pairBinSteps = new uint256[](1);
        pairBinSteps[0] = BIN_STEP;

        IMoeLBRouter.Version[] memory versions = new IMoeLBRouter.Version[](1);
        versions[0] = IMoeLBRouter.Version.V2_2;

        return IMoeLBRouter.Path({
            pairBinSteps: pairBinSteps,
            versions: versions,
            tokenPath: tokens
        });
    }
}
