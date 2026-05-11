export const ADDRESSES = {
  IdentityRegistry: "0xD2074e8CDdB710a9E9C17c1B0a4c4fF694B6bf95",
  ReputationRegistry: "0xCf8AccC55a636131CaBa585Cf3B23e1c0f231fE9",
  ValidationRegistry: "0x09e402674c521f9293e7428A0FE8C3FCc8f93a0d",
  DecisionLog: "0xB123cE88e8b1b8de606574BbA99b655D0D456994",
  VaultFactory: "0x2CF55485f0B8371213DA74c90da8b3F9791e633A",
  ConservativeVault: "0xF3Df82262522307C6442137F24dA6710B182AE8b",
  BalancedVault: "0x424593f6E19d02B862a2cb2ec82Cf1A3de3d54bA",
  AggressiveVault: "0x542d2C1C1F7ca2fe54ec6A0F2139Fda069EC5625",
  USDYAdapter: "0x8978644428D4283fEb53ffe250a59F6a8CE5C9A0",
  METHAdapter: "0xcAae1dBf111aF26655A4f40eaC4792978d3249c8",
  CMETHAdapter: "0x66894e0ff472A1C7B36c5175EfE300Ca1cCC6643",
  FBTCAdapter: "0x3AF5c3D7E64Fc07C2affBA9a09D9DcFbF8a4650D",
} as const;

export const VAULTS = [
  { address: ADDRESSES.ConservativeVault, name: "Conservative", riskLevel: 1 },
  { address: ADDRESSES.BalancedVault, name: "Balanced", riskLevel: 2 },
  { address: ADDRESSES.AggressiveVault, name: "Aggressive", riskLevel: 3 },
] as const;

export const ASSET_COLORS: Record<string, string> = {
  USDY: "#22c55e",
  mETH: "#3b82f6",
  cmETH: "#a855f7",
  fBTC: "#f97316",
  USDC: "#6b7280",
};
