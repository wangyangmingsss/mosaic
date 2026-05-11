// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "./MosaicVaultV2.sol";
import "./DecisionLog.sol";
import "./erc8004/IdentityRegistry.sol";
import "./erc8004/ReputationRegistry.sol";
import "./erc8004/ValidationRegistry.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

/// @title  VaultFactoryV2
/// @notice Deploys MosaicVaultV2 with ERC-8004 agent identity registration
///         and protocol adapter injection.
contract VaultFactoryV2 is IERC721Receiver {

    address public immutable decisionLog;
    address public immutable authorizedAgent;
    address public immutable usdc;

    IdentityRegistry   public immutable identityRegistry;
    ReputationRegistry public immutable reputationRegistry;
    ValidationRegistry public immutable validationRegistry;

    address public owner;
    address[] public allVaults;

    /// @dev symbol hash => default adapter address
    mapping(bytes32 => address) public defaultAdapters;

    event VaultCreated(
        address indexed vault,
        uint256 indexed agentTokenId,
        address indexed creator,
        uint8   riskLevel,
        uint256 timestamp
    );

    error ZeroAddress();
    error NotOwner();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor(
        address _decisionLog,
        address _agent,
        address _usdc,
        IdentityRegistry   _identityRegistry,
        ReputationRegistry _reputationRegistry,
        ValidationRegistry _validationRegistry
    ) {
        if (_decisionLog == address(0) || _agent == address(0) || _usdc == address(0))
            revert ZeroAddress();
        decisionLog        = _decisionLog;
        authorizedAgent    = _agent;
        usdc               = _usdc;
        identityRegistry   = _identityRegistry;
        reputationRegistry = _reputationRegistry;
        validationRegistry = _validationRegistry;
        owner = msg.sender;
    }

    function createVault(
        uint8  riskLevel,
        uint8  rebalanceFrequency,
        uint16 maxDrawdownBps,
        uint16 maxSingleAssetBps,
        string calldata agentRegistrationURI
    ) external returns (address vault) {
        // 1. Register agent identity in ERC-8004 IdentityRegistry
        uint256 tokenId = identityRegistry.register(address(this), agentRegistrationURI);

        MosaicVaultV2.RiskProfile memory profile = MosaicVaultV2.RiskProfile({
            riskLevel:          riskLevel,
            rebalanceFrequency: rebalanceFrequency,
            maxDrawdownBps:     maxDrawdownBps,
            maxSingleAssetBps:  maxSingleAssetBps
        });

        string memory name   = string.concat("Mosaic V2 Vault #", _toString(allVaults.length + 1));
        string memory symbol = string.concat("msV2-", _toString(allVaults.length + 1));

        // 2. Deploy vault
        MosaicVaultV2 v = new MosaicVaultV2(
            IERC20(usdc),
            name,
            symbol,
            profile,
            authorizedAgent,
            decisionLog,
            identityRegistry,
            reputationRegistry,
            validationRegistry,
            tokenId
        );

        vault = address(v);

        // 3. Transfer agent identity NFT to vault
        identityRegistry.safeTransferFrom(address(this), vault, tokenId);

        // 4. Vault self-authorizes in DecisionLog via msg.sender check

        // 5. Set default adapters
        bytes32[5] memory symbols = [
            keccak256("USDY"),
            keccak256("mETH"),
            keccak256("cmETH"),
            keccak256("fBTC"),
            keccak256("USDC")
        ];
        for (uint256 i = 0; i < symbols.length; i++) {
            if (defaultAdapters[symbols[i]] != address(0)) {
                v.setAdapter(symbols[i], defaultAdapters[symbols[i]]);
            }
        }

        // 6. Transfer vault ownership to creator
        v.transferOwnership(msg.sender);

        allVaults.push(vault);
        emit VaultCreated(vault, tokenId, msg.sender, riskLevel, block.timestamp);
    }

    function setDefaultAdapter(string calldata symbol, address adapter) external onlyOwner {
        defaultAdapters[keccak256(bytes(symbol))] = adapter;
    }

    function totalVaults() external view returns (uint256) {
        return allVaults.length;
    }

    function onERC721Received(address, address, uint256, bytes calldata)
        external pure override returns (bytes4)
    {
        return IERC721Receiver.onERC721Received.selector;
    }

    function _toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";
        uint256 temp = value;
        uint256 digits;
        while (temp != 0) { digits++; temp /= 10; }
        bytes memory buf = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buf[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }
        return string(buf);
    }
}
