// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

interface IProtocolAdapter {
    struct ExecutionReceipt {
        address protocol;
        uint256 amountIn;
        uint256 amountOut;
        uint256 gasUsed;
        bytes32 protocolTxId;
    }

    function buy(
        uint256 amountInUSDC,
        uint256 minAmountOut,
        address recipient
    ) external returns (ExecutionReceipt memory);

    function sell(
        uint256 amountIn,
        uint256 minAmountOut,
        address recipient
    ) external returns (ExecutionReceipt memory);

    function quoteBuy(uint256 amountInUSDC) external view returns (uint256);

    function priceUSDC() external view returns (uint256);

    function targetAsset() external view returns (address);
}
