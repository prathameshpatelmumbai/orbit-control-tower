"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Zap, ShieldCheck, Activity, Terminal, Layers, Sparkles } from "lucide-react";
import { useOrbitStore } from "@/lib/store";
import { injectChaos } from "@/lib/api";

export function Navbar() {
  const { systemHealth, systemScore, isChaosRunning, setIsChaosRunning } = useOrbitStore();
  const [isInjecting, setIsInjecting] = useState(false);

  const handleQuickChaos = async () => {
    if (isInjecting || isChaosRunning) return;
    setIsInjecting(true);
    setIsChaosRunning(true);
    try {
      await injectChaos({
        domain: "banking",
        fault_type: "null_spike",
        severity: "high"
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsInjecting(false);
      setTimeout(() => setIsChaosRunning(false), 3000);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-white/5 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-gold/10 border border-gold/40 flex items-center justify-center transition-all group-hover:scale-105 group-hover:shadow-gold-glow">
            <Sparkles className="w-4 h-4 text-gold" />
          </div>
          <div>
            <div className="font-serif tracking-wider font-semibold text-lg text-white group-hover:text-gold transition-colors">
              ORBIT
            </div>
            <div className="text-[10px] text-neutral-400 font-mono tracking-widest uppercase">
              Control Tower
            </div>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden md:flex items-center gap-6 text-sm text-neutral-300">
          <a href="#galaxy" className="hover:text-gold transition-colors">3D Galaxy</a>
          <a href="#chaos" className="hover:text-gold transition-colors">Chaos Mode</a>
          <a href="#agents" className="hover:text-gold transition-colors">Agent Crew</a>
          <a href="#insights" className="hover:text-gold transition-colors">Insights Lab</a>
          <a href="#simulator" className="hover:text-gold transition-colors">What-If</a>
          <a href="#ask" className="hover:text-gold transition-colors">Ask Console</a>
          <a href="#architecture" className="hover:text-gold transition-colors">Architecture</a>
        </nav>

        {/* Right Status & Trigger */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-surface border border-white/10 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                systemHealth === "healthy"
                  ? "bg-emerald animate-pulse"
                  : "bg-coral animate-ping"
              }`}
            />
            <span className="text-neutral-400">SLO:</span>
            <span className="text-white font-medium">{systemScore}%</span>
          </div>

          <button
            onClick={handleQuickChaos}
            disabled={isInjecting || isChaosRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-gradient-to-r from-coral/20 to-coral/10 hover:from-coral/30 hover:to-coral/20 border border-coral/40 text-coral text-xs font-mono uppercase tracking-wider transition-all hover:shadow-coral-glow disabled:opacity-50"
          >
            <Zap className="w-3.5 h-3.5 fill-coral" />
            <span>{isInjecting ? "Injecting..." : "Chaos Trigger"}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
