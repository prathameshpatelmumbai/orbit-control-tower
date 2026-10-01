"use client";

import React from "react";
import { motion } from "framer-motion";
import { ArrowDown, Zap, Shield, Sparkles, Activity } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-24 pb-16 px-4 text-center overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-gold/10 via-ice/10 to-transparent blur-[140px] pointer-events-none rounded-full" />
      <div className="absolute bottom-10 left-1/4 w-[400px] h-[250px] bg-emerald/5 blur-[120px] pointer-events-none rounded-full" />

      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-gold/30 bg-surface/80 backdrop-blur-md text-gold text-xs font-mono uppercase tracking-widest mb-8 shadow-gold-glow"
      >
        <span className="w-2 h-2 rounded-full bg-emerald animate-pulse" />
        Autonomous Control Tower Active
      </motion.div>

      {/* Main Headline */}
      <motion.h1
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.1 }}
        className="text-6xl sm:text-7xl md:text-8xl lg:text-9xl font-serif tracking-tight text-white max-w-5xl leading-[1.05]"
      >
        Data that <br />
        <span className="italic bg-gradient-to-r from-gold via-gold-light to-amber-200 bg-clip-text text-transparent">
          heals
        </span>{" "}
        itself.
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.25 }}
        className="mt-6 max-w-2xl text-lg sm:text-xl text-neutral-400 font-sans leading-relaxed"
      >
        Autonomous operations for modern enterprise pipelines. Synthetic data streams, real-time 3D spatial lineage, and an AI agent crew that isolates faults, generates patches, and validates recovery live.
      </motion.p>

      {/* Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.4 }}
        className="mt-10 flex flex-wrap items-center justify-center gap-4"
      >
        <a
          href="#galaxy"
          className="group relative inline-flex items-center gap-2.5 px-6 py-3.5 rounded-lg bg-gold text-background font-medium text-sm transition-all hover:bg-gold-light hover:shadow-gold-glow hover:scale-[1.02]"
        >
          <Sparkles className="w-4 h-4 fill-background" />
          <span>Launch 3D Data Galaxy</span>
        </a>

        <a
          href="#chaos"
          className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-lg bg-surface hover:bg-surface-hover border border-white/10 text-white font-medium text-sm transition-all hover:border-coral/50 hover:shadow-coral-glow"
        >
          <Zap className="w-4 h-4 text-coral" />
          <span>Explore Chaos Mode</span>
        </a>
      </motion.div>

      {/* Telemetry pill row */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.55 }}
        className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl w-full text-left"
      >
        <div className="glass-panel p-4 rounded-xl border-hairline">
          <div className="text-neutral-400 text-xs font-mono uppercase tracking-wider">Spatial Lineage</div>
          <div className="text-2xl font-serif text-white mt-1">18 Nodes</div>
          <div className="text-[11px] text-emerald mt-1 flex items-center gap-1 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald" /> 100% Monitored
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border-hairline">
          <div className="text-neutral-400 text-xs font-mono uppercase tracking-wider">Mean Time to Heal</div>
          <div className="text-2xl font-serif text-gold mt-1">4.8 sec</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">
            Down from 4.2h manual MTTR
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border-hairline">
          <div className="text-neutral-400 text-xs font-mono uppercase tracking-wider">System Availability</div>
          <div className="text-2xl font-serif text-white mt-1">99.98%</div>
          <div className="text-[11px] text-ice mt-1 font-mono">
            Zero data loss SLA
          </div>
        </div>

        <div className="glass-panel p-4 rounded-xl border-hairline">
          <div className="text-neutral-400 text-xs font-mono uppercase tracking-wider">Agent Crew</div>
          <div className="text-2xl font-serif text-emerald mt-1">6 Active</div>
          <div className="text-[11px] text-neutral-400 mt-1 font-mono">
            LangGraph cognitive loop
          </div>
        </div>
      </motion.div>

      {/* Scroll down prompt */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
        className="mt-16 flex flex-col items-center gap-2 text-neutral-500 text-xs font-mono"
      >
        <span>SCROLL TO EXPLORE ARCHITECTURE</span>
        <ArrowDown className="w-4 h-4 animate-bounce text-neutral-400" />
      </motion.div>
    </section>
  );
}
