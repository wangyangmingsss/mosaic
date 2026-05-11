// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IMoeLBRouter {
    enum Version { V1, V2, V2_1, V2_2 }

    struct Path {
        uint256[] pairBinSteps;
        Version[] versions;
        address[] tokenPath;
    }

    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        Path memory path,
        address to,
        uint256 deadline
    ) external returns (uint256 amountOut);

    function swapTokensForExactTokens(
        uint256 amountOut,
        uint256 amountInMax,
        Path memory path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amountsIn);
}
