// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IProtocolAdapter} from "./IProtocolAdapter.sol";
import {IMoeLBRouter} from "../interfaces/external/IMoeLBRouter.sol";
import {IMoeLBQuoter} from "../interfaces/external/IMoeLBQuoter.sol";

interface IERC20Decimals is IERC20 {
    function decimals() external view returns (uint8);
}

/**
 * @title MoeAdapter
 * @notice Generic Merchant Moe LB v2.2 swap adapter for MOSAIC.
 *         Each instance is configured at deploy time for a specific (USDC <-> target) pair.
 */
contract MoeAdapter is IProtocolAdapter, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Mantle Mainnet Constants
    address public constant MOE_LB_ROUTER = 0x013e138EF6008ae5FDFDE29700e3f2Bc61d21E3a;
    address public constant MOE_LB_QUOTER = 0x501b8AFd35df20f531fF45F6f695793AC3316c85;
    address public constant USDC = 0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9;

    address public immutable TARGET;
    uint16  public immutable BIN_STEP;
    uint16  public maxSlippageBps = 100; // 1% default

    event SwapExecuted(
        address indexed caller,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        bytes32 reason
    );

    constructor(address target_, uint16 binStep_) Ownable(msg.sender) {
        TARGET = target_;
        BIN_STEP = binStep_;
    }

    function targetAsset() external view override returns (address) {
        return TARGET;
    }

    function buy(uint256 amountInUSDC, uint256 minAmountOut, address recipient)
        external override nonReentrant returns (ExecutionReceipt memory)
    {
        IERC20(USDC).safeTransferFrom(msg.sender, address(this), amountInUSDC);
        IERC20(USDC).forceApprove(MOE_LB_ROUTER, amountInUSDC);

        IMoeLBRouter.Path memory path = _buildPath(USDC, TARGET);

        uint256 amountOut = IMoeLBRouter(MOE_LB_ROUTER).swapExactTokensForTokens(
            amountInUSDC, minAmountOut, path, recipient, block.timestamp + 300
        );

        emit SwapExecuted(msg.sender, USDC, TARGET, amountInUSDC, amountOut, "buy");

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
        IERC20(TARGET).safeTransferFrom(msg.sender, address(this), amountIn);
        IERC20(TARGET).forceApprove(MOE_LB_ROUTER, amountIn);

        IMoeLBRouter.Path memory path = _buildPath(TARGET, USDC);
        uint256 amountOut = IMoeLBRouter(MOE_LB_ROUTER).swapExactTokensForTokens(
            amountIn, minAmountOut, path, recipient, block.timestamp + 300
        );

        emit SwapExecuted(msg.sender, TARGET, USDC, amountIn, amountOut, "sell");

        return ExecutionReceipt({
            protocol: MOE_LB_ROUTER,
            amountIn: amountIn,
            amountOut: amountOut,
            gasUsed: 0,
            protocolTxId: bytes32(0)
        });
    }

    function quoteBuy(uint256 amountInUSDC) external view override returns (uint256) {
        address[] memory route = _toPath(USDC, TARGET);
        IMoeLBQuoter.Quote memory q = IMoeLBQuoter(MOE_LB_QUOTER).findBestPathFromAmountIn(
            route, uint128(amountInUSDC)
        );
        return q.amounts.length > 1 ? q.amounts[1] : 0;
    }

    function priceUSDC() external view override returns (uint256) {
        uint256 oneUnit = 10 ** IERC20Decimals(TARGET).decimals();
        address[] memory route = _toPath(TARGET, USDC);
        IMoeLBQuoter.Quote memory q = IMoeLBQuoter(MOE_LB_QUOTER).findBestPathFromAmountIn(
            route, uint128(oneUnit)
        );
        return q.amounts.length > 1 ? q.amounts[1] : 0;
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

    function _toPath(address tokenIn, address tokenOut)
        internal pure returns (address[] memory tokens)
    {
        tokens = new address[](2);
        tokens[0] = tokenIn;
        tokens[1] = tokenOut;
    }

    function setMaxSlippage(uint16 bps) external onlyOwner {
        require(bps <= 500, "max 5%");
        maxSlippageBps = bps;
    }
}
