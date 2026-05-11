"use client";

import Link from "next/link";
import { useReadContract } from "wagmi";
import { formatUnits } from "viem";
import { mosaicVaultAbi } from "@/lib/abis";
import { AllocationPieChart } from "./AllocationPieChart";

const RISK_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "Conservative", color: "text-green-400" },
  2: { label: "Balanced", color: "text-blue-400" },
  3: { label: "Aggressive", color: "text-orange-400" },
};

export function VaultCard({ address, name, riskLevel }: { address: string; name: string; riskLevel: number }) {
  const { data: totalAssets } = useReadContract({
    address: address as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "totalAssets",
  });

  const { data: allocation } = useReadContract({
    address: address as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "getAllocation",
  });

  const { data: identity } = useReadContract({
    address: address as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "getAgentIdentity",
  });

  const risk = RISK_LABELS[riskLevel] || RISK_LABELS[2];
  const tvl = totalAssets ? formatUnits(totalAssets, 6) : "0";
  const identityData = identity as unknown as { totalDecisions: bigint; cumulativePnLBps: bigint } | undefined;
  const decisions = identityData ? Number(identityData.totalDecisions) : 0;
  const pnlBps = identityData ? Number(identityData.cumulativePnLBps) : 0;

  return (
    <Link href={`/explorer/vault/${address}`}>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-600 transition-all cursor-pointer group">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">
            {name}
          </h3>
          <span className={`text-xs font-medium px-2 py-1 rounded-full bg-slate-800 ${risk.color}`}>
            {risk.label}
          </span>
        </div>

        <AllocationPieChart allocation={allocation as { usdyBps: number; xstocksBps: number; methBps: number; fbtcBps: number; usdcBps: number } | undefined} />

        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-800">
          <div>
            <p className="text-xs text-slate-500">TVL</p>
            <p className="text-sm font-medium text-white">
              ${Number(tvl).toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Decisions</p>
            <p className="text-sm font-medium text-white">{decisions}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">PnL</p>
            <p className={`text-sm font-medium ${pnlBps >= 0 ? "text-green-400" : "text-red-400"}`}>
              {pnlBps >= 0 ? "+" : ""}{(pnlBps / 100).toFixed(2)}%
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}
