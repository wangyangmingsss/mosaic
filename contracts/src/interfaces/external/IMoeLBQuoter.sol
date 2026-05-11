// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IMoeLBQuoter {
    struct Quote {
        address[] route;
        address[] pairs;
        uint256[] binSteps;
        uint256[] versions;
        uint128[] amounts;
        uint128[] virtualAmountsWithoutSlippage;
        uint128[] fees;
    }

    function findBestPathFromAmountIn(
        address[] calldata route,
        uint128 amountIn
    ) external view returns (Quote memory quote);

    function findBestPathFromAmountOut(
        address[] calldata route,
        uint128 amountOut
    ) external view returns (Quote memory quote);
}
