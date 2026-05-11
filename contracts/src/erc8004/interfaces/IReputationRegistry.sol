// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

/**
 * @title IReputationRegistry (ERC-8004 Reputation Registry)
 * @notice Standard interface for posting and reading feedback signals on agents.
 */
interface IReputationRegistry {
    struct Feedback {
        address client;
        uint256 agentId;
        int256  score;
        uint256 timestamp;
        string  feedbackURI;
    }

    event FeedbackPosted(
        uint256 indexed agentId,
        address indexed client,
        int256 score,
        string feedbackURI
    );

    function postFeedback(
        uint256 agentId,
        int256 score,
        string calldata feedbackURI
    ) external;

    function getFeedback(uint256 agentId, uint256 index)
        external view returns (Feedback memory);

    function getFeedbackCount(uint256 agentId) external view returns (uint256);

    function getAggregateScore(uint256 agentId) external view returns (int256);
}
