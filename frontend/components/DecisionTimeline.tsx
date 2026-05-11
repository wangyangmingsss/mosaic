"use client";

import { useReadContract } from "wagmi";
import { decisionLogAbi } from "@/lib/abis";
import { ADDRESSES } from "@/lib/contracts";

export function DecisionTimeline({ vaultAddress }: { vaultAddress: string }) {
  const { data: history, isLoading } = useReadContract({
    address: ADDRESSES.DecisionLog as `0x${string}`,
    abi: decisionLogAbi,
    functionName: "getVaultHistory",
    args: [vaultAddress as `0x${string}`],
  });

  if (isLoading) {
    return (
      <div className="text-slate-500 text-sm py-4">Loading decision history...</div>
    );
  }

  const entries = history as Array<{
    vault: string;
    decisionId: bigint;
    recordHash: string;
    timestamp: bigint;
    blockNumber: bigint;
  }> | undefined;

  if (!entries || entries.length === 0) {
    return (
      <div className="text-slate-500 text-sm py-4">No decisions recorded yet.</div>
    );
  }

  const sorted = [...entries].reverse().slice(0, 20);

  return (
    <div className="space-y-3">
      {sorted.map((entry, i) => {
        const date = new Date(Number(entry.timestamp) * 1000);
        return (
          <div key={i} className="flex gap-4 items-start group">
            <div className="flex flex-col items-center">
              <div className="w-3 h-3 rounded-full bg-blue-500 group-hover:bg-blue-400 transition-colors" />
              {i < sorted.length - 1 && <div className="w-px h-8 bg-slate-700" />}
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-white">
                  Decision #{Number(entry.decisionId)}
                </span>
                <span className="text-xs text-slate-500">
                  Block {Number(entry.blockNumber).toLocaleString()}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {date.toLocaleDateString()} {date.toLocaleTimeString()}
              </p>
              <p className="text-xs text-slate-500 mt-1 font-mono truncate">
                Hash: {entry.recordHash}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
