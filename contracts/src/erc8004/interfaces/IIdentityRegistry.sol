// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

/**
 * @title IIdentityRegistry (ERC-8004 Identity Registry)
 * @notice Minimal on-chain handle (ERC-721 + URIStorage) for trustless agents.
 *         tokenURI MUST resolve to an agent registration file conforming to
 *         the ERC-8004 registration schema (off-chain JSON, typically on IPFS).
 */
interface IIdentityRegistry {
    event AgentRegistered(uint256 indexed tokenId, address indexed owner, string tokenURI);
    event AgentURIUpdated(uint256 indexed tokenId, string newURI);

    function register(address to, string calldata uri) external returns (uint256 tokenId);
    function updateURI(uint256 tokenId, string calldata uri) external;
    function tokenURI(uint256 tokenId) external view returns (string memory);
    function ownerOf(uint256 tokenId) external view returns (address);
}
