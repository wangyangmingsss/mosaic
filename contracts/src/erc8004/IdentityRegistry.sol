// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.26;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {IERC721} from "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {IIdentityRegistry} from "./interfaces/IIdentityRegistry.sol";

/**
 * @title IdentityRegistry
 * @notice Reference ERC-8004 Identity Registry deployment on Mantle Mainnet.
 *         Minimal & singleton-friendly: anyone can register an agent NFT here.
 *         Aligned with the ERC-8004 spec (DRAFT, August 2025).
 */
contract IdentityRegistry is ERC721URIStorage, IIdentityRegistry {
    uint256 private _nextTokenId = 1;

    constructor() ERC721("ERC-8004 Agent Identity", "AGENT") {}

    function register(address to, string calldata uri)
        external override returns (uint256 tokenId)
    {
        tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        emit AgentRegistered(tokenId, to, uri);
    }

    function updateURI(uint256 tokenId, string calldata uri) external override {
        require(_ownerOf(tokenId) == msg.sender, "ERC8004: not owner");
        _setTokenURI(tokenId, uri);
        emit AgentURIUpdated(tokenId, uri);
    }

    function tokenURI(uint256 tokenId)
        public view override(ERC721URIStorage, IIdentityRegistry)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function ownerOf(uint256 tokenId)
        public view override(ERC721, IERC721, IIdentityRegistry)
        returns (address)
    {
        return super.ownerOf(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
