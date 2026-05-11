"use client";

import Link from "next/link";
import { ConnectButton } from "./ConnectButton";

export function Navbar() {
  return (
    <nav className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold text-white tracking-tight">
            MOSAIC
          </Link>
          <div className="hidden sm:flex items-center gap-6">
            <Link href="/dashboard" className="text-slate-400 hover:text-white transition-colors text-sm">
              Dashboard
            </Link>
            <Link href="/explorer" className="text-slate-400 hover:text-white transition-colors text-sm">
              Explorer
            </Link>
          </div>
        </div>
        <ConnectButton />
      </div>
    </nav>
  );
}
