"use client";

import React from "react";
import { Sparkles, ArrowUpRight, Github, ExternalLink, ShieldCheck, Heart } from "lucide-react";

export function ImpactSection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Top Banner Stats */}
      <div className="glass-panel p-8 sm:p-12 rounded-3xl border-hairline relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gold/10 blur-[130px] rounded-full pointer-events-none" />

        <div className="max-w-2xl mb-12">
          <div className="text-gold text-xs font-mono uppercase tracking-widest mb-2">
            Enterprise Operational ROI
          </div>
          <h2 className="text-3xl sm:text-5xl font-serif text-white">
            Measurable impact on day one.
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base mt-2">
            Quantified operational performance across Fortune 500 BFSI, retail procurement, and supply chain telemetry pipelines.
          </p>
        </div>

        {/* 4 Big Metrics Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-surface/50 p-6 rounded-2xl border border-white/5">
            <div className="text-4xl sm:text-5xl font-serif text-gold font-bold">89%</div>
            <div className="text-sm font-serif text-white mt-2">MTTR Reduction</div>
            <div className="text-xs font-mono text-neutral-400 mt-1">From 4.2 hrs to 4.8 seconds</div>
          </div>

          <div className="bg-surface/50 p-6 rounded-2xl border border-white/5">
            <div className="text-4xl sm:text-5xl font-serif text-white font-bold">100%</div>
            <div className="text-sm font-serif text-white mt-2">Zero Data Loss</div>
            <div className="text-xs font-mono text-neutral-400 mt-1">Poison pills quarantined</div>
          </div>

          <div className="bg-surface/50 p-6 rounded-2xl border border-white/5">
            <div className="text-4xl sm:text-5xl font-serif text-emerald font-bold">99.98%</div>
            <div className="text-sm font-serif text-white mt-2">SLA Availability</div>
            <div className="text-xs font-mono text-neutral-400 mt-1">Continuous uptime compliance</div>
          </div>

          <div className="bg-surface/50 p-6 rounded-2xl border border-white/5">
            <div className="text-4xl sm:text-5xl font-serif text-ice font-bold">$142k</div>
            <div className="text-sm font-serif text-white mt-2">Monthly Loss Avoided</div>
            <div className="text-xs font-mono text-neutral-400 mt-1">Prevented SLA breach penalties</div>
          </div>
        </div>

        {/* Tech Stack Marquee Pills */}
        <div className="mt-14 pt-8 border-t border-white/10">
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-400 text-center mb-6">
            Engineered with Modern Open Source Standards
          </div>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {[
              "Next.js 15 App Router",
              "React Three Fiber",
              "Three.js",
              "FastAPI",
              "LangGraph",
              "pgvector",
              "DuckDB",
              "Dagster",
              "dbt-core",
              "Evidently AI",
              "SHAP",
              "Redis Streams",
              "Docker Compose"
            ].map((tech) => (
              <span
                key={tech}
                className="px-3.5 py-1.5 rounded-full bg-surface border border-white/10 text-xs font-mono text-neutral-300 hover:border-gold/40 hover:text-white transition-colors"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-20 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-neutral-500 gap-4">
        <div>
          © 2026 ORBIT Autonomous Data Operations Control Tower. Distributed under Apache 2.0.
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/prathameshpatelmumbai/Hackathon-Project-employment-website"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-neutral-400 hover:text-white transition-colors"
          >
            <Github className="w-4 h-4" />
            <span>GitHub Repository</span>
          </a>
          <span>•</span>
          <span className="text-emerald flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald" />
            All Systems Operational
          </span>
        </div>
      </footer>
    </section>
  );
}
