"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Shield, Search, Wrench, CheckCircle, FileText, TrendingUp, Sparkles, Terminal } from "lucide-react";

interface AgentCardData {
  id: string;
  name: string;
  title: string;
  icon: React.ElementType;
  color: string;
  accentClass: string;
  description: string;
  tools: string[];
  recentThought: string;
}

const AGENTS: AgentCardData[] = [
  {
    id: "sentinel",
    name: "Sentinel",
    title: "Continuous Telemetry & Anomaly Detector",
    icon: Shield,
    color: "#7CC4FF",
    accentClass: "border-ice/30 hover:border-ice/80 shadow-ice-glow",
    description: "Monitors real-time streaming throughput, statistical drift flags, and data quality check results. Dispatches failure alerts within 400ms.",
    tools: ["get_metrics", "get_lineage", "monitor_expectations"],
    recentThought: "Scanning 18 spatial nodes. Invariant check passed for retail order quantities and shipping cold chain temperatures."
  },
  {
    id: "diagnostician",
    name: "Diagnostician",
    title: "Lineage & Root-Cause Localizer",
    icon: Search,
    color: "#C9A96E",
    accentClass: "border-gold/30 hover:border-gold/80 shadow-gold-glow",
    description: "Traverses upstream dependency graph, isolates failure origin, and queries pgvector incident memory to cite historical resolution patterns.",
    tools: ["search_similar_incidents", "run_sql", "trace_lineage"],
    recentThought: "Traversed bronze banking transactions lineage. Vector cosine match (98.4%) cited for upstream schema alias remediation."
  },
  {
    id: "surgeon",
    name: "Surgeon",
    title: "Sandbox Remediation & Patch Generator",
    icon: Wrench,
    color: "#FF5A5F",
    accentClass: "border-coral/30 hover:border-coral/80 shadow-coral-glow",
    description: "Synthesizes targeted SQL patches, isolates poisoned records into quarantine tables, and re-triggers pipeline tasks in sandbox environment.",
    tools: ["quarantine_batch", "run_sql", "rerun_task"],
    recentThought: "Quarantined 24 null-keyed records into bronze_banking_transactions_quarantine to preserve downstream gold marts."
  },
  {
    id: "auditor",
    name: "Auditor",
    title: "Post-Fix Invariant Validator",
    icon: CheckCircle,
    color: "#3DDC97",
    accentClass: "border-emerald/30 hover:border-emerald/80 shadow-emerald-glow",
    description: "Re-evaluates Great Expectations suites and statistical drift metrics on post-patch data. Ensures zero regression before clearing node alert.",
    tools: ["evaluate_expectations", "check_node_health", "verify_psi"],
    recentThought: "Validated post-fix schema invariants on fct_banking_transactions: 100% check pass rate. Clearing alert state."
  },
  {
    id: "scribe",
    name: "Scribe",
    title: "Executive Postmortem & Memory Embedder",
    icon: FileText,
    color: "#B388FF",
    accentClass: "border-purple-500/30 hover:border-purple-500/80",
    description: "Compiles human-readable markdown incident reports with root cause analysis, fix details, and embeds vectors into pgvector memory.",
    tools: ["store_incident", "generate_postmortem", "publish_audit_log"],
    recentThought: "Generated postmortem for incident #inc_20261001_84f9. Vector embedding indexed in pgvector store."
  },
  {
    id: "strategist",
    name: "Strategist",
    title: "Predictive SLA & Business Impact Analyst",
    icon: TrendingUp,
    color: "#E2C799",
    accentClass: "border-amber-400/30 hover:border-amber-400/80",
    description: "Calculates blast radius, downtime financial loss avoided, and updates What-If simulator parameters to prevent future repeat incidents.",
    tools: ["simulate_what_if", "calculate_mttr", "forecast_sla"],
    recentThought: "Estimated downtime loss prevented: $18,450. MTTR reduced to 4.8s. Updating preventive SLA risk buffers."
  }
];

export function AgentCrewSection() {
  const [activeAgent, setActiveAgent] = useState<string>("sentinel");

  return (
    <section id="agents" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-gold/30 bg-surface/60 text-gold text-xs font-mono uppercase tracking-widest mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          Autonomous Multi-Agent Crew
        </div>
        <h2 className="text-3xl sm:text-5xl font-serif text-white">
          Six specialized agents. <br />
          <span className="text-gold italic">One self-healing cognitive loop</span>.
        </h2>
        <p className="text-neutral-400 text-sm sm:text-base mt-3 leading-relaxed">
          Powered by LangGraph directed cycles and Claude tool use. Each agent acts autonomously with specialized tool access, historical incident memory, and safety gates.
        </p>
      </div>

      {/* 6 Interactive 3D Tilting Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {AGENTS.map((agent) => {
          const Icon = agent.icon;
          const isSelected = activeAgent === agent.id;

          return (
            <motion.div
              key={agent.id}
              whileHover={{ y: -6, transition: { duration: 0.2 } }}
              onClick={() => setActiveAgent(agent.id)}
              className={`glass-panel p-6 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${agent.accentClass} ${
                isSelected ? "ring-1 ring-gold/50 bg-surface" : "bg-surface/60"
              }`}
            >
              <div>
                {/* Top Row: Icon + Status */}
                <div className="flex items-center justify-between">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center border"
                    style={{
                      backgroundColor: `${agent.color}15`,
                      borderColor: `${agent.color}40`,
                    }}
                  >
                    <Icon className="w-5 h-5" style={{ color: agent.color }} />
                  </div>
                  <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-neutral-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse" />
                    <span>Active</span>
                  </div>
                </div>

                {/* Name & Role */}
                <div className="mt-5">
                  <h3 className="text-2xl font-serif text-white font-medium">{agent.name}</h3>
                  <div className="text-xs font-mono text-neutral-400 mt-1">{agent.title}</div>
                </div>

                {/* Description */}
                <p className="text-neutral-300 text-xs mt-3 leading-relaxed">
                  {agent.description}
                </p>

                {/* Tools Exposed via MCP */}
                <div className="mt-4">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-neutral-400 mb-2">
                    MCP Tools
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.tools.map((tool) => (
                      <span
                        key={tool}
                        className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-mono text-neutral-300"
                      >
                        {tool}()
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Mini Log Thought Bubble */}
              <div className="mt-6 pt-4 border-t border-white/5 bg-[#050608] p-3 rounded-xl border border-white/5 text-[11px] font-mono">
                <div className="text-gold flex items-center gap-1.5 mb-1">
                  <Terminal className="w-3 h-3" />
                  <span>Recent Reasoning Trace:</span>
                </div>
                <p className="text-neutral-400 italic line-clamp-2">
                  "{agent.recentThought}"
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}
