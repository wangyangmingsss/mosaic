"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { ASSET_COLORS } from "@/lib/contracts";

interface Allocation {
  usdyBps: number;
  xstocksBps: number;
  methBps: number;
  fbtcBps: number;
  usdcBps: number;
}

export function AllocationPieChart({ allocation }: { allocation: Allocation | undefined }) {
  if (!allocation) {
    return (
      <div className="w-full h-48 flex items-center justify-center text-slate-500">
        Loading...
      </div>
    );
  }

  const data = [
    { name: "USDY", value: Number(allocation.usdyBps), color: ASSET_COLORS.USDY },
    { name: "mETH", value: Number(allocation.methBps), color: ASSET_COLORS.mETH },
    { name: "cmETH", value: Number(allocation.xstocksBps), color: ASSET_COLORS.cmETH },
    { name: "fBTC", value: Number(allocation.fbtcBps), color: ASSET_COLORS.fBTC },
    { name: "USDC", value: Number(allocation.usdcBps), color: ASSET_COLORS.USDC },
  ].filter((d) => d.value > 0);

  return (
    <div className="w-full h-48">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={70}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => `${(Number(value) / 100).toFixed(1)}%`}
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px" }}
            labelStyle={{ color: "#e2e8f0" }}
            itemStyle={{ color: "#e2e8f0" }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-3 justify-center mt-2">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-1 text-xs text-slate-400">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />
            {d.name} {(d.value / 100).toFixed(0)}%
          </div>
        ))}
      </div>
    </div>
  );
}
