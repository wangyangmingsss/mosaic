// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

/**
 * @title IValidationRegistry (ERC-8004 Validation Registry)
 * @notice Generic hooks for posting validation results from independent validators.
 */
interface IValidationRegistry {
    enum ValidationKind { Stake, ZKML, TEE, Trusted }

    struct Validation {
        address validator;
        uint256 agentId;
        bytes32 taskHash;
        bool    success;
        ValidationKind kind;
        uint256 timestamp;
        string  proofURI;
    }

    event ValidationPosted(
        uint256 indexed agentId,
        bytes32 indexed taskHash,
        address indexed validator,
        bool success,
        ValidationKind kind,
        string proofURI
    );

    function postValidation(
        uint256 agentId,
        bytes32 taskHash,
        bool success,
        ValidationKind kind,
        string calldata proofURI
    ) external;

    function getValidations(uint256 agentId, bytes32 taskHash)
        external view returns (Validation[] memory);
}
