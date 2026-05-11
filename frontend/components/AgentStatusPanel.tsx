"use client";

import { useReadContract } from "wagmi";
import { mosaicVaultAbi } from "@/lib/abis";

export function AgentStatusPanel({ vaultAddress }: { vaultAddress: string }) {
  const { data: identity, isLoading } = useReadContract({
    address: vaultAddress as `0x${string}`,
    abi: mosaicVaultAbi,
    functionName: "getAgentIdentity",
  });

  if (isLoading) {
    return <div className="text-slate-500 text-sm">Loading agent info...</div>;
  }

  if (!identity) {
    return <div className="text-slate-500 text-sm">Unable to load agent identity.</div>;
  }

  const { modelDeclaration, createdAt, totalDecisions, successfulRebalances, cumulativePnLBps, metadataURI } = identity as unknown as {
    modelDeclaration: string;
    createdAt: bigint;
    totalDecisions: bigint;
    successfulRebalances: bigint;
    cumulativePnLBps: bigint;
    metadataURI: string;
  };

  const createdDate = new Date(Number(createdAt) * 1000);
  const successRate = Number(totalDecisions) > 0
    ? ((Number(successfulRebalances) / Number(totalDecisions)) * 100).toFixed(1)
    : "N/A";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-4">
        ERC-8004 Agent Identity
      </h3>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Model</span>
          <span className="text-sm text-white font-mono">{modelDeclaration}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Created</span>
          <span className="text-sm text-white">{createdDate.toLocaleDateString()}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Total Decisions</span>
          <span className="text-sm text-white">{Number(totalDecisions)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Success Rate</span>
          <span className="text-sm text-green-400">{successRate}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-slate-500">Cumulative PnL</span>
          <span className={`text-sm ${Number(cumulativePnLBps) >= 0 ? "text-green-400" : "text-red-400"}`}>
            {Number(cumulativePnLBps) >= 0 ? "+" : ""}{(Number(cumulativePnLBps) / 100).toFixed(2)}%
          </span>
        </div>
        {metadataURI && (
          <div className="flex justify-between">
            <span className="text-sm text-slate-500">Metadata</span>
            <a
              href={metadataURI.startsWith("ipfs://") ? `https://gateway.pinata.cloud/ipfs/${metadataURI.slice(7)}` : metadataURI}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-400 hover:text-blue-300 truncate max-w-[200px]"
            >
              View on IPFS
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
