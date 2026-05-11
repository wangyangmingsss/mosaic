"use client";

import { useParams } from "next/navigation";
import { useReadContract } from "wagmi";
import { formatUnits } from "viem";
import { mosaicVaultAbi } from "@/lib/abis";
import { VAULTS } from "@/lib/contracts";
import { AllocationPieChart } from "@/components/AllocationPieChart";
import { DecisionTimeline } from "@/components/DecisionTimeline";
import { AgentStatusPanel } from "@/components/AgentStatusPanel";

export default function VaultDetailPage() {
  const params = useParams();
  const vaultAddress = params.address as string;

  const vaultInfo = VAULTS.find(
    (v) => v.address.toLowerCase() === vaultAddress?.toLowerCase()
  );

  const { data: vaultName } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "name",
  });

  const { data: totalAssets } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "totalAssets",
  });

  const { data: totalSupply } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "totalSupply",
  });

  const { data: allocation } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "getAllocation",
  });

  const { data: isPaused } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "paused",
  });

  const { data: riskProfile } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "riskProfile",
  });

  const displayName = vaultInfo?.name || (vaultName as string) || "Vault";
  const tvl = totalAssets ? formatUnits(totalAssets, 6) : "0";
  const supply = totalSupply ? formatUnits(totalSupply, 18) : "0";

  const frequencyLabels: Record<number, string> = { 1: "Daily", 2: "Weekly", 3: "Monthly" };
  const riskLabels: Record<number, string> = { 1: "Conservative", 2: "Balanced", 3: "Aggressive" };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">{displayName}</h1>
          <p className="text-sm text-slate-500 font-mono mt-1">{vaultAddress}</p>
        </div>
        {isPaused && (
          <span className="px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs font-medium">
            PAUSED
          </span>
        )}
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider">TVL</p>
          <p className="text-xl font-semibold text-white mt-1">
            ${Number(tvl).toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider">Total Supply</p>
          <p className="text-xl font-semibold text-white mt-1">
            {Number(supply).toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider">Risk Level</p>
          <p className="text-xl font-semibold text-white mt-1">
            {riskProfile ? riskLabels[Number(riskProfile[0])] || "Unknown" : "-"}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wider">Rebalance Freq</p>
          <p className="text-xl font-semibold text-white mt-1">
            {riskProfile ? frequencyLabels[Number(riskProfile[1])] || "Unknown" : "-"}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Allocation */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
              Current Allocation
            </h2>
            <AllocationPieChart allocation={allocation as { usdyBps: number; xstocksBps: number; methBps: number; fbtcBps: number; usdcBps: number } | undefined} />
          </div>

          {/* Decision timeline */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
              Decision History
            </h2>
            <DecisionTimeline vaultAddress={vaultAddress} />
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-6">
          <AgentStatusPanel vaultAddress={vaultAddress} />

          {/* Risk parameters */}
          {riskProfile && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
                Risk Parameters
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-500">Max Drawdown</span>
                  <span className="text-sm text-white">
                    {(Number(riskProfile[2]) / 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-500">Max Single Asset</span>
                  <span className="text-sm text-white">
                    {(Number(riskProfile[3]) / 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
