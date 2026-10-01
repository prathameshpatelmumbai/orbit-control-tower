"use client";

import React, { useState, useEffect } from "react";
import { Play, Pause, RotateCcw, FastForward, Rewind, Terminal, Cpu, CheckCircle } from "lucide-react";
import { useOrbitStore, AgentStep } from "@/lib/store";

const DEFAULT_DEMO_STEPS: AgentStep[] = [
  {
    agent_name: "Sentinel",
    thought: "Alert triggered on node 'bronze_banking_transactions'. Quality invariant breached: detected 'null_spike' with severity 'high'. Null rate exceeded 45% on mandatory field 'account_id'.",
    tool_call: "get_lineage",
    decision: "DISPATCH_INCIDENT_TO_DIAGNOSTICIAN",
    timestamp: "13:24:02 UTC"
  },
  {
    agent_name: "Diagnostician",
    thought: "Traversed upstream lineage to 'src_core_banking'. Retrieved 2 similar historical incidents from pgvector memory. Citing root cause: Tokenization gateway timeout caused customer_id and account_id to evaluate to NULL on 48% of incoming transactions.",
    tool_call: "search_similar_incidents",
    decision: "ROOT_CAUSE_ISOLATED_HANDOFF_TO_SURGEON",
    timestamp: "13:24:03 UTC"
  },
  {
    agent_name: "Surgeon",
    thought: "Formulated sandbox fix for 'null_spike'. Executing quarantine_batch('bronze_banking_transactions', 'customer_id IS NULL OR account_id IS NULL') to isolate 38 corrupted records into quarantine table.",
    tool_call: "quarantine_batch",
    decision: "FIX_APPLIED_DISPATCH_TO_AUDITOR",
    timestamp: "13:24:04 UTC"
  },
  {
    agent_name: "Auditor",
    thought: "Executed post-remediation validation suite on bronze_banking_transactions. 100% of non-null expectations passed. Data health score restored from 38% to 99.8%.",
    tool_call: "evaluate_expectations",
    decision: "VALIDATION_SUCCESSFUL_PASS_TO_SCRIBE",
    timestamp: "13:24:05 UTC"
  },
  {
    agent_name: "Scribe",
    thought: "Compiled executive postmortem for incident #inc_20261001_84f9. Synthesized root cause, patch details, and embedded vector representation into pgvector memory for future sub-10ms citation.",
    tool_call: "store_incident",
    decision: "POSTMORTEM_PUBLISHED",
    timestamp: "13:24:06 UTC"
  },
  {
    agent_name: "Strategist",
    thought: "Calculated blast radius: Downstream Gold Enterprise Revenue Mart protected from poison pill records. Estimated Mean Time to Remediation (MTTR): 4.8s. Business downtime loss prevented: $18,450.00.",
    tool_call: "get_metrics",
    decision: "INCIDENT_CLOSED_METRICS_LOGGED",
    timestamp: "13:24:07 UTC"
  }
];

export function AgentReplayScrubber() {
  const { recentSteps } = useOrbitStore();
  const steps = recentSteps.length >= 3 ? recentSteps : DEFAULT_DEMO_STEPS;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= steps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [isPlaying, steps.length]);

  const activeStep = steps[currentIndex] || steps[0];

  return (
    <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="glass-panel p-8 rounded-2xl border-hairline">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-white/10 gap-4">
          <div>
            <div className="text-gold text-xs font-mono uppercase tracking-widest flex items-center gap-1.5 mb-1">
              <Cpu className="w-3.5 h-3.5" />
              <span>Agent Reasoning Replay</span>
            </div>
            <h3 className="text-2xl font-serif text-white">
              Step-by-step cognitive decision replay scrubber.
            </h3>
          </div>

          {/* Scrubber Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
              disabled={currentIndex === 0}
              className="p-2 rounded-lg bg-surface hover:bg-surface-hover text-neutral-400 hover:text-white border border-white/5 disabled:opacity-40"
            >
              <Rewind className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-4 py-2 rounded-lg bg-gold hover:bg-gold-light text-background font-mono text-xs uppercase tracking-wider font-semibold flex items-center gap-1.5 shadow-gold-glow"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span>{isPlaying ? "Pause" : "Play"}</span>
            </button>
            <button
              onClick={() => setCurrentIndex(Math.min(steps.length - 1, currentIndex + 1))}
              disabled={currentIndex === steps.length - 1}
              className="p-2 rounded-lg bg-surface hover:bg-surface-hover text-neutral-400 hover:text-white border border-white/5 disabled:opacity-40"
            >
              <FastForward className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentIndex(0)}
              className="p-2 rounded-lg bg-surface hover:bg-surface-hover text-neutral-400 hover:text-white border border-white/5"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Timeline Slider Track */}
        <div className="mt-8">
          <div className="flex justify-between text-xs font-mono text-neutral-400 mb-2">
            <span>Step {currentIndex + 1} of {steps.length}: [{activeStep.agent_name}]</span>
            <span>{activeStep.timestamp}</span>
          </div>

          <input
            type="range"
            min={0}
            max={steps.length - 1}
            value={currentIndex}
            onChange={(e) => setCurrentIndex(Number(e.target.value))}
            className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-[#C9A96E]"
          />

          <div className="grid grid-cols-6 gap-2 mt-4">
            {steps.map((s, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentIndex(idx)}
                className={`py-1.5 px-2 rounded text-[11px] font-mono border text-center transition-all ${
                  idx === currentIndex
                    ? "bg-gold/20 border-gold text-gold font-semibold shadow-gold-glow"
                    : idx < currentIndex
                    ? "bg-surface/80 border-emerald/40 text-emerald"
                    : "bg-surface/30 border-white/5 text-neutral-500"
                }`}
              >
                {s.agent_name}
              </button>
            ))}
          </div>
        </div>

        {/* Active Step Reasoning Terminal Card */}
        <div className="mt-8 bg-[#040507] p-6 rounded-xl border border-white/10 font-mono text-xs">
          <div className="flex items-center justify-between border-b border-white/5 pb-3 mb-3">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-gold" />
              <span className="text-white font-medium text-sm">Agent: {activeStep.agent_name}</span>
            </div>
            {activeStep.tool_call && (
              <span className="px-2 py-0.5 rounded bg-ice/15 border border-ice/30 text-ice text-[11px]">
                Invoked Tool: {activeStep.tool_call}()
              </span>
            )}
          </div>

          <div className="text-neutral-300 leading-relaxed text-sm py-2">
            {activeStep.thought}
          </div>

          {activeStep.decision && (
            <div className="mt-3 pt-3 border-t border-white/5 flex items-center gap-2 text-emerald font-semibold text-xs">
              <CheckCircle className="w-4 h-4" />
              <span>Decision: {activeStep.decision}</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
