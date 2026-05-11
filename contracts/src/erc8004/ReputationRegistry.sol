// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

import {IReputationRegistry} from "./interfaces/IReputationRegistry.sol";

/**
 * @title ReputationRegistry
 * @notice ERC-8004 Reputation Registry — stores on-chain feedback signals for agents.
 *         Aggregate score uses exponentially weighted moving average (EWMA).
 */
contract ReputationRegistry is IReputationRegistry {
    /// @dev agentId => list of feedbacks
    mapping(uint256 => Feedback[]) private _feedbacks;

    /// @dev agentId => EWMA aggregate score (scaled by 1e4 internally)
    mapping(uint256 => int256) private _aggregateScore;

    /// @dev EWMA alpha = 20% for new feedback weighting
    int256 private constant ALPHA_NUM = 20;
    int256 private constant ALPHA_DEN = 100;

    function postFeedback(
        uint256 agentId,
        int256 score,
        string calldata feedbackURI
    ) external override {
        require(score >= -100 && score <= 100, "score out of range [-100,100]");

        _feedbacks[agentId].push(Feedback({
            client: msg.sender,
            agentId: agentId,
            score: score,
            timestamp: block.timestamp,
            feedbackURI: feedbackURI
        }));

        // Update EWMA: new_agg = alpha * score + (1 - alpha) * old_agg
        if (_feedbacks[agentId].length == 1) {
            _aggregateScore[agentId] = score;
        } else {
            int256 old = _aggregateScore[agentId];
            _aggregateScore[agentId] = (ALPHA_NUM * score + (ALPHA_DEN - ALPHA_NUM) * old) / ALPHA_DEN;
        }

        emit FeedbackPosted(agentId, msg.sender, score, feedbackURI);
    }

    function getFeedback(uint256 agentId, uint256 index)
        external view override returns (Feedback memory)
    {
        return _feedbacks[agentId][index];
    }

    function getFeedbackCount(uint256 agentId)
        external view override returns (uint256)
    {
        return _feedbacks[agentId].length;
    }

    function getAggregateScore(uint256 agentId)
        external view override returns (int256)
    {
        return _aggregateScore[agentId];
    }
}
