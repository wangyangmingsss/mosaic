"use client";

import { useAccount, useReadContract, useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { parseUnits, formatUnits } from "viem";
import { useState } from "react";
import { mosaicVaultAbi, erc20Abi } from "@/lib/abis";
import { VAULTS } from "@/lib/contracts";
import { AllocationPieChart } from "@/components/AllocationPieChart";

export default function DashboardPage() {
  const { address, isConnected } = useAccount();
  const [selectedVault, setSelectedVault] = useState<string>(VAULTS[0].address);
  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawShares, setWithdrawShares] = useState("");

  const { data: balance } = useReadContract({
    address: selectedVault as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "balanceOf",
    args: address ? [address] : undefined,
    query: { enabled: !!address },
  });

  const { data: totalAssets } = useReadContract({
    address: selectedVault as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "totalAssets",
  });

  const { data: allocation } = useReadContract({
    address: selectedVault as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "getAllocation",
  });

  const { data: assetAddress } = useReadContract({
    address: selectedVault as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "asset",
  });

  const { data: userAssetBalance } = useReadContract({
    address: assetAddress as `0x${string}` | undefined,
    abi: erc20Abi,
    functionName: "balanceOf",
    args: address ? [address] : undefined,
    query: { enabled: !!address && !!assetAddress },
  });

  const { writeContract: approve, data: approveTxHash } = useWriteContract();
  const { writeContract: deposit, data: depositTxHash } = useWriteContract();
  const { writeContract: redeem, data: redeemTxHash } = useWriteContract();

  const { isLoading: isApproving } = useWaitForTransactionReceipt({ hash: approveTxHash });
  const { isLoading: isDepositing } = useWaitForTransactionReceipt({ hash: depositTxHash });
  const { isLoading: isRedeeming } = useWaitForTransactionReceipt({ hash: redeemTxHash });

  const handleDeposit = () => {
    if (!depositAmount || !address || !assetAddress) return;
    const amount = parseUnits(depositAmount, 6);
    // First approve
    approve({
      address: assetAddress as `0x${string}`,
      abi: erc20Abi,
      functionName: "approve",
      args: [selectedVault as `0x${string}`, amount],
    });
  };

  const handleDepositAfterApproval = () => {
    if (!depositAmount || !address) return;
    const amount = parseUnits(depositAmount, 6);
    deposit({
      address: selectedVault as `0x${string}`,
      abi: mosaicVaultAbi,
      functionName: "deposit",
      args: [amount, address],
    });
  };

  const handleRedeem = () => {
    if (!withdrawShares || !address) return;
    const shares = parseUnits(withdrawShares, 18);
    redeem({
      address: selectedVault as `0x${string}`,
      abi: mosaicVaultAbi,
      functionName: "redeem",
      args: [shares, address, address],
    });
  };

  if (!isConnected) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">Dashboard</h1>
          <p className="text-slate-400 mb-8">Connect your wallet to manage your MOSAIC positions.</p>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 max-w-md mx-auto">
            <p className="text-slate-500">Please connect your wallet using the button above.</p>
          </div>
        </div>
      </div>
    );
  }

  const selectedVaultInfo = VAULTS.find((v) => v.address === selectedVault);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>

      {/* Vault selector */}
      <div className="mb-8">
        <label className="text-sm text-slate-400 block mb-2">Select Vault</label>
        <div className="flex gap-3">
          {VAULTS.map((v) => (
            <button
              key={v.address}
              onClick={() => setSelectedVault(v.address)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedVault === v.address
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              {v.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio stats */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Your Shares</p>
              <p className="text-xl font-semibold text-white mt-1">
                {balance ? Number(formatUnits(balance, 18)).toLocaleString(undefined, { maximumFractionDigits: 2 }) : "0"}
              </p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider">Vault TVL</p>
              <p className="text-xl font-semibold text-white mt-1">
                ${totalAssets ? Number(formatUnits(totalAssets, 6)).toLocaleString(undefined, { maximumFractionDigits: 0 }) : "0"}
              </p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <p className="text-xs text-slate-500 uppercase tracking-wider">USDC Balance</p>
              <p className="text-xl font-semibold text-white mt-1">
                ${userAssetBalance ? Number(formatUnits(userAssetBalance, 6)).toLocaleString(undefined, { maximumFractionDigits: 2 }) : "0"}
              </p>
            </div>
          </div>

          {/* Allocation */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
              {selectedVaultInfo?.name} Allocation
            </h3>
            <AllocationPieChart allocation={allocation as { usdyBps: number; xstocksBps: number; methBps: number; fbtcBps: number; usdcBps: number } | undefined} />
          </div>
        </div>

        {/* Deposit/Withdraw */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Deposit</h3>
            <input
              type="number"
              placeholder="Amount (USDC)"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 mb-3"
            />
            <div className="flex gap-2">
              <button
                onClick={handleDeposit}
                disabled={isApproving || !depositAmount}
                className="flex-1 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium transition-colors text-sm"
              >
                {isApproving ? "Approving..." : "Approve"}
              </button>
              <button
                onClick={handleDepositAfterApproval}
                disabled={isDepositing || !depositAmount}
                className="flex-1 px-4 py-2.5 rounded-lg bg-green-600 hover:bg-green-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium transition-colors text-sm"
              >
                {isDepositing ? "Depositing..." : "Deposit"}
              </button>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">Withdraw</h3>
            <input
              type="number"
              placeholder="Shares to redeem"
              value={withdrawShares}
              onChange={(e) => setWithdrawShares(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 mb-3"
            />
            <button
              onClick={handleRedeem}
              disabled={isRedeeming || !withdrawShares}
              className="w-full px-4 py-2.5 rounded-lg bg-orange-600 hover:bg-orange-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium transition-colors text-sm"
            >
              {isRedeeming ? "Redeeming..." : "Redeem"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
