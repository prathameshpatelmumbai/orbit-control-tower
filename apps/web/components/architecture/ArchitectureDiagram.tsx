"use client";

import React, { useState } from "react";
import { Database, Cpu, Layers, GitBranch, Shield, Activity, Terminal, ArrowRight } from "lucide-react";

interface LayerInfo {
  id: string;
  name: string;
  role: string;
  tech: string[];
  description: string;
  color: string;
}

const ARCH_LAYERS: LayerInfo[] = [
  {
    id: "data_plane",
    name: "1. Synthetic Enterprise Data Plane",
    role: "Ingestion & Fault Injection",
    tech: ["Python", "Faker", "NumPy", "DuckDB"],
    description: "Generates high-velocity synthetic streams for BFSI payments, retail orders, supply chain IoT, and web clickstream. Features a controlled 8+ fault injection chaos engine.",
    color: "#7CC4FF"
  },
  {
    id: "pipeline_plane",
    name: "2. Medallion Pipeline Architecture",
    role: "Orchestration & Data Quality",
    tech: ["Dagster", "dbt-core", "DuckDB", "Great Expectations"],
    description: "Orchestrates Bronze (raw), Silver (cleansed & deduplicated), and Gold (analytics marts). Enforces automated schema tests and null threshold invariants.",
    color: "#3DDC97"
  },
  {
    id: "ml_plane",
    name: "3. ML Telemetry & Explainability",
    role: "Anomalies, Drift & Forecasting",
    tech: ["Isolation Forest", "Evidently AI", "SHAP", "MLflow"],
    description: "Evaluates multi-dimensional outlier scores, calculates Population Stability Index (PSI) drift, produces SHAP feature attributions, and models SLA forecasts with confidence bands.",
    color: "#B388FF"
  },
  {
    id: "agent_plane",
    name: "4. Autonomous Multi-Agent Crew",
    role: "LangGraph Cognitive Remediation",
    tech: ["LangGraph", "Claude API", "MCP Server", "HITL Gate"],
    description: "Six specialized agents (Sentinel, Diagnostician, Surgeon, Auditor, Scribe, Strategist) run cyclical self-healing loops with human-in-the-loop approval gates for risky operations.",
    color: "#C9A96E"
  },
  {
    id: "storage_plane",
    name: "5. Vector Memory & State Bus",
    role: "Semantic Memory & Event Streaming",
    tech: ["PostgreSQL 16", "pgvector", "Redis Streams", "DuckDB"],
    description: "Stores historical postmortems in pgvector for sub-10ms similarity retrieval by Diagnostician. Redis Streams broadcasts real-time telemetry events to WebSockets.",
    color: "#FF5A5F"
  }
];

export function ArchitectureDiagram() {
  const [selectedLayer, setSelectedLayer] = useState<string>("agent_plane");
  const active = ARCH_LAYERS.find((l) => l.id === selectedLayer) || ARCH_LAYERS[3];

  return (
    <section id="architecture" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-gold/30 bg-surface/60 text-gold text-xs font-mono uppercase tracking-widest mb-4">
          <Layers className="w-3.5 h-3.5" />
          System Blueprints
        </div>
        <h2 className="text-3xl sm:text-5xl font-serif text-white">
          Architectural Blueprint
        </h2>
        <p className="text-neutral-400 text-sm sm:text-base mt-3 leading-relaxed">
          Decoupled, event-driven data plane orchestrated through software-defined assets, stateful multi-agent directed graphs, and sub-10ms semantic incident memory.
        </p>
      </div>

      {/* Interactive Layer Flow */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Layer Blocks Stack (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          {ARCH_LAYERS.map((layer, idx) => {
            const isSelected = selectedLayer === layer.id;
            return (
              <div
                key={layer.id}
                onClick={() => setSelectedLayer(layer.id)}
                className={`p-5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? "glass-panel-gold border-gold/60 shadow-gold-glow"
                    : "glass-panel border-white/5 hover:border-white/20 hover:bg-surface/50"
                }`}
              >
                <div>
                  <div className="flex items-center gap-2 text-xs font-mono uppercase">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: layer.color }}
                    />
                    <span className="text-neutral-400">{layer.role}</span>
                  </div>
                  <h4 className="text-lg font-serif text-white mt-1 font-medium">{layer.name}</h4>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {layer.tech.map((t) => (
                      <span
                        key={t}
                        className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[10px] font-mono text-neutral-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all ${
                    isSelected ? "bg-gold text-background border-gold" : "bg-white/5 text-neutral-500 border-white/10"
                  }`}
                >
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed Inspector Card (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-8 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-gold mb-2">
              <span
                className="w-2.5 h-2.5 rounded-full animate-pulse"
                style={{ backgroundColor: active.color }}
              />
              <span>{active.role}</span>
            </div>

            <h3 className="text-2xl font-serif text-white font-medium">{active.name}</h3>

            <p className="text-neutral-300 text-sm mt-4 leading-relaxed font-sans">
              {active.description}
            </p>

            <div className="mt-8">
              <div className="text-xs font-mono uppercase tracking-wider text-neutral-400 mb-3">
                Core Technologies & Standards
              </div>
              <div className="flex flex-wrap gap-2">
                {active.tech.map((t) => (
                  <span
                    key={t}
                    className="px-3 py-1.5 rounded-lg bg-surface border border-white/10 text-xs font-mono text-white"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-8 pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-neutral-400">
            <span>Decoupled Control Plane</span>
            <span className="text-emerald">SAIF & Zero-Trust Compliant</span>
          </div>
        </div>
      </div>
    </section>
  );
}
