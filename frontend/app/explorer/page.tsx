"use client";

import { VaultCard } from "@/components/VaultCard";
import { VAULTS } from "@/lib/contracts";

export default function ExplorerPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Vault Explorer</h1>
        <p className="text-slate-400 mt-2">
          Browse all MOSAIC vaults and their real-time allocations on Mantle.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {VAULTS.map((vault) => (
          <VaultCard
            key={vault.address}
            address={vault.address}
            name={vault.name}
            riskLevel={vault.riskLevel}
          />
        ))}
      </div>
    </div>
  );
}
