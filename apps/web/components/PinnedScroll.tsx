"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { AlertTriangle, CheckCircle2, Cpu, Wrench, ShieldCheck, Zap } from "lucide-react";

export function PinnedScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const card1Opacity = useTransform(scrollYProgress, [0, 0.25, 0.4], [1, 1, 0]);
  const card1Scale = useTransform(scrollYProgress, [0, 0.25, 0.4], [1, 1, 0.95]);

  const card2Opacity = useTransform(scrollYProgress, [0.35, 0.55, 0.7], [0, 1, 0]);
  const card2Scale = useTransform(scrollYProgress, [0.35, 0.55, 0.7], [0.95, 1, 0.95]);

  const card3Opacity = useTransform(scrollYProgress, [0.65, 0.85, 1], [0, 1, 1]);
  const card3Scale = useTransform(scrollYProgress, [0.65, 0.85, 1], [0.95, 1, 1]);

  return (
    <section ref={containerRef} className="relative h-[280vh] bg-background">
      <div className="sticky top-0 h-screen flex flex-col justify-center items-center px-4 overflow-hidden">
        {/* Section title */}
        <div className="text-center mb-8 max-w-xl">
          <div className="text-gold text-xs font-mono tracking-widest uppercase mb-2">
            Evolution of Operations
          </div>
          <h2 className="text-3xl sm:text-5xl font-serif text-white">
            From 3am on-call alerts to <span className="text-gold italic">autonomous self-healing</span>.
          </h2>
        </div>

        {/* Morphing Cards Stack */}
        <div className="relative w-full max-w-4xl h-[400px]">
          {/* Stage 1: The Legacy Fragile Pipeline */}
          <motion.div
            style={{ opacity: card1Opacity, scale: card1Scale }}
            className="absolute inset-0 glass-panel p-8 sm:p-10 rounded-2xl border border-coral/30 flex flex-col justify-between shadow-coral-glow pointer-events-none"
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 text-coral font-mono text-sm uppercase tracking-wider">
                  <AlertTriangle className="w-5 h-5 text-coral" />
                  <span>Legacy Pipeline Architecture</span>
                </div>
                <div className="px-2.5 py-1 rounded bg-coral/20 border border-coral/40 text-coral text-xs font-mono">
                  MTTR: 4.2 Hours
                </div>
              </div>
              <h3 className="text-2xl font-serif text-white mt-4">
                Silent drift and unhandled schema breaks.
              </h3>
              <p className="text-neutral-400 text-sm mt-2 leading-relaxed">
                A third-party API renames a critical payload column at 02:45 AM. Downstream DAGs fail silently until C-suite dashboards report missing revenue. Engineers wake to high-urgency PagerDuty alarms and spend hours running ad-hoc SQL hotfixes.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-6 border-t border-white/5 text-xs font-mono">
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Detection</div>
                <div className="text-coral mt-1 font-semibold">Manual / Pager</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Diagnosis</div>
                <div className="text-neutral-300 mt-1">Manual grep logs</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Blast Radius</div>
                <div className="text-coral mt-1">Full Downstream Halt</div>
              </div>
            </div>
          </motion.div>

          {/* Stage 2: The Multi-Agent Transition */}
          <motion.div
            style={{ opacity: card2Opacity, scale: card2Scale }}
            className="absolute inset-0 glass-panel p-8 sm:p-10 rounded-2xl border border-ice/30 flex flex-col justify-between shadow-ice-glow pointer-events-none"
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 text-ice font-mono text-sm uppercase tracking-wider">
                  <Cpu className="w-5 h-5 text-ice" />
                  <span>Cognitive Multi-Agent Crew Engagement</span>
                </div>
                <div className="px-2.5 py-1 rounded bg-ice/20 border border-ice/40 text-ice text-xs font-mono">
                  Autonomous Cycle
                </div>
              </div>
              <h3 className="text-2xl font-serif text-white mt-4">
                Sentinel detects. Diagnostician cites historical resolution.
              </h3>
              <p className="text-neutral-400 text-sm mt-2 leading-relaxed">
                Sentinel catches the schema divergence within 400 milliseconds. Diagnostician traverses upstream lineage and queries pgvector incident memory, identifying an identical failure resolved 3 months ago. Surgeon synthesizes an alias patch in sandbox isolation.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-6 border-t border-white/5 text-xs font-mono">
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Lineage Spotting</div>
                <div className="text-ice mt-1 font-semibold">Instant Sub-10ms</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Vector Memory</div>
                <div className="text-ice mt-1">98.4% Match Cited</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Safety Gate</div>
                <div className="text-gold mt-1">Sandbox Isolated</div>
              </div>
            </div>
          </motion.div>

          {/* Stage 3: The ORBIT Self-Healing Platform */}
          <motion.div
            style={{ opacity: card3Opacity, scale: card3Scale }}
            className="absolute inset-0 glass-panel-gold p-8 sm:p-10 rounded-2xl border border-gold/40 flex flex-col justify-between shadow-gold-glow pointer-events-none"
          >
            <div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 text-gold font-mono text-sm uppercase tracking-wider">
                  <ShieldCheck className="w-5 h-5 text-gold" />
                  <span>The ORBIT Autonomous Control Tower</span>
                </div>
                <div className="px-2.5 py-1 rounded bg-emerald/20 border border-emerald/40 text-emerald text-xs font-mono">
                  MTTR: 4.8 Seconds
                </div>
              </div>
              <h3 className="text-2xl font-serif text-white mt-4">
                Validated repair. Zero data loss. Automated postmortem.
              </h3>
              <p className="text-neutral-400 text-sm mt-2 leading-relaxed">
                Auditor validates that all schema invariants and null thresholds pass. Pipeline node turns healthy emerald. Scribe automatically files an executive incident report, and Strategist calculates $18,450 in business downtime loss prevented.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-6 border-t border-white/5 text-xs font-mono">
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Resolution</div>
                <div className="text-emerald mt-1 font-semibold">Self-Healed Live</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Human Touch</div>
                <div className="text-gold mt-1">Audit-Only / Zero Page</div>
              </div>
              <div className="bg-surface/50 p-3 rounded-lg border border-white/5">
                <div className="text-neutral-400">Data Integrity</div>
                <div className="text-emerald mt-1">100% Invariants Intact</div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
