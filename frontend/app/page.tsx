"use client";

import Link from "next/link";
import { VaultCard } from "@/components/VaultCard";
import { VAULTS } from "@/lib/contracts";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-950/20 to-transparent" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-6xl font-bold text-white tracking-tight">
              Autonomous RWA
              <span className="text-blue-400"> Yield Management</span>
            </h1>
            <p className="mt-6 text-lg text-slate-400 leading-relaxed">
              MOSAIC uses AI agents with on-chain identity (ERC-8004) to manage
              diversified Real World Asset portfolios on Mantle. Transparent,
              verifiable, and fully autonomous.
            </p>
            <div className="mt-8 flex items-center justify-center gap-4">
              <Link
                href="/dashboard"
                className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors"
              >
                Launch App
              </Link>
              <Link
                href="/explorer"
                className="px-6 py-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors border border-slate-700"
              >
                Explore Vaults
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Feature cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-white font-semibold mb-2">ERC-8004 Identity</h3>
            <p className="text-sm text-slate-400">
              Every agent has verifiable on-chain identity with reputation scores,
              decision history, and performance metrics.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <h3 className="text-white font-semibold mb-2">Multi-Asset Yield</h3>
            <p className="text-sm text-slate-400">
              Diversified across USDY, mETH, cmETH, and fBTC with AI-optimized
              allocations rebalanced autonomously.
            </p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
              <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-white font-semibold mb-2">Full Auditability</h3>
            <p className="text-sm text-slate-400">
              Every decision is logged on-chain with IPFS-backed reasoning.
              Verify exactly what the agent decided and why.
            </p>
          </div>
        </div>
      </section>

      {/* Vault overview */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-2xl font-bold text-white mb-8">Active Vaults</h2>
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
      </section>
    </div>
  );
}
