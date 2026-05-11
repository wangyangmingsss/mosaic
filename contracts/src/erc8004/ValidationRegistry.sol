// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

import {IValidationRegistry} from "./interfaces/IValidationRegistry.sol";

/**
 * @title ValidationRegistry
 * @notice ERC-8004 Validation Registry — stores validation results from independent
 *         validators (stakers, zkML verifiers, TEE oracles, trusted judges).
 */
contract ValidationRegistry is IValidationRegistry {
    /// @dev agentId => taskHash => list of validations
    mapping(uint256 => mapping(bytes32 => Validation[])) private _validations;

    function postValidation(
        uint256 agentId,
        bytes32 taskHash,
        bool success,
        ValidationKind kind,
        string calldata proofURI
    ) external override {
        _validations[agentId][taskHash].push(Validation({
            validator: msg.sender,
            agentId: agentId,
            taskHash: taskHash,
            success: success,
            kind: kind,
            timestamp: block.timestamp,
            proofURI: proofURI
        }));

        emit ValidationPosted(agentId, taskHash, msg.sender, success, kind, proofURI);
    }

    function getValidations(uint256 agentId, bytes32 taskHash)
        external view override returns (Validation[] memory)
    {
        return _validations[agentId][taskHash];
    }
}
