"use client";

import React, { useState, useEffect } from "react";
import { Zap, Play, CheckCircle2, AlertOctagon, Terminal, Flame, ShieldAlert, Cpu } from "lucide-react";
import { useOrbitStore } from "@/lib/store";
import { injectChaos, fetchScenarios } from "@/lib/api";

export function ChaosConsole() {
  const { isChaosRunning, setIsChaosRunning, recentSteps, addAgentStep } = useOrbitStore();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>("black_friday_overload");
  const [isTriggering, setIsTriggering] = useState(false);
  const [activeTab, setActiveTab] = useState<"scenario" | "manual">("scenario");
  const [manualDomain, setManualDomain] = useState("banking");
  const [manualFault, setManualFault] = useState("null_spike");

  useEffect(() => {
    fetchScenarios().then(setScenarios);
  }, []);

  const handleInject = async () => {
    if (isTriggering || isChaosRunning) return;
    setIsTriggering(true);
    setIsChaosRunning(true);

    try {
      if (activeTab === "scenario") {
        await injectChaos({ scenario_id: selectedScenario });
      } else {
        await injectChaos({
          domain: manualDomain,
          fault_type: manualFault,
          severity: "high"
        });
      }
    } catch (e) {
      console.error("Chaos error", e);
    } finally {
      setIsTriggering(false);
      setTimeout(() => setIsChaosRunning(false), 2000);
    }
  };

  return (
    <section id="chaos" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between mb-12">
        <div>
          <div className="text-coral text-xs font-mono uppercase tracking-widest flex items-center gap-1.5 mb-2">
            <Flame className="w-4 h-4 fill-coral" />
            <span>Chaos Engineering & Self-Healing Loop</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-serif text-white">
            Inject a fault. Watch it <span className="text-gold italic">heal</span>.
          </h2>
          <p className="text-neutral-400 text-sm sm:text-base mt-2 max-w-2xl">
            Simulate realistic enterprise pipeline breakdowns. The autonomous agent crew detects anomalies, locates root cause via historical incident memory, generates a sandbox patch, and validates recovery.
          </p>
        </div>

        {/* Big Trigger Button */}
        <div className="mt-6 md:mt-0">
          <button
            onClick={handleInject}
            disabled={isTriggering || isChaosRunning}
            className="flex items-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-coral via-red-600 to-amber-600 hover:from-coral hover:to-amber-500 text-white font-mono uppercase text-sm font-semibold tracking-wider transition-all hover:scale-105 hover:shadow-coral-glow disabled:opacity-50"
          >
            <Zap className={`w-5 h-5 fill-white ${isTriggering || isChaosRunning ? "animate-bounce" : ""}`} />
            <span>
              {isTriggering || isChaosRunning ? "Self-Healing In Progress..." : "Inject Chaos Fault"}
            </span>
          </button>
        </div>
      </div>

      {/* Main Grid: Controls + Live Animated Remediation Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Scenario Selector (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-neutral-300">
                Failure Scenarios
              </span>
              <div className="flex gap-2 text-xs font-mono">
                <button
                  onClick={() => setActiveTab("scenario")}
                  className={`px-2.5 py-1 rounded ${activeTab === "scenario" ? "bg-white/10 text-white" : "text-neutral-500"}`}
                >
                  Curated
                </button>
                <button
                  onClick={() => setActiveTab("manual")}
                  className={`px-2.5 py-1 rounded ${activeTab === "manual" ? "bg-white/10 text-white" : "text-neutral-500"}`}
                >
                  Custom
                </button>
              </div>
            </div>

            {activeTab === "scenario" ? (
              <div className="space-y-3">
                {scenarios.map((sc) => {
                  const isSelected = selectedScenario === sc.id;
                  return (
                    <div
                      key={sc.id}
                      onClick={() => setSelectedScenario(sc.id)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer ${
                        isSelected
                          ? "bg-surface border-coral/60 shadow-coral-glow"
                          : "bg-surface/50 border-white/5 hover:border-white/20"
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-white font-medium">{sc.name}</span>
                        <span className="px-2 py-0.5 rounded bg-white/5 text-neutral-400 uppercase">
                          {sc.domain}
                        </span>
                      </div>
                      <p className="text-neutral-400 text-xs mt-1.5 leading-relaxed">
                        {sc.description || "Injected schema drift and late-arriving event replays."}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-4 pt-2">
                <div>
                  <label className="text-xs font-mono text-neutral-400 block mb-1.5">Target Pipeline Domain</label>
                  <select
                    value={manualDomain}
                    onChange={(e) => setManualDomain(e.target.value)}
                    className="w-full bg-surface border border-white/10 rounded-lg p-2.5 text-xs font-mono text-white focus:outline-none focus:border-gold"
                  >
                    <option value="banking">Banking (BFSI)</option>
                    <option value="retail">Retail Orders & Inventory</option>
                    <option value="supply_chain">Supply Chain Logistics</option>
                    <option value="customer">Customer Clickstream</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-mono text-neutral-400 block mb-1.5">Fault Type (8+ Available)</label>
                  <select
                    value={manualFault}
                    onChange={(e) => setManualFault(e.target.value)}
                    className="w-full bg-surface border border-white/10 rounded-lg p-2.5 text-xs font-mono text-white focus:outline-none focus:border-gold"
                  >
                    <option value="null_spike">Null Spike (Foreign Keys)</option>
                    <option value="schema_drift">Schema Drift (Dropped/Renamed Column)</option>
                    <option value="duplicate_events">Duplicate Events (Kafka Offset Replay)</option>
                    <option value="late_arrivals">Late Arrivals (Watermark Breach)</option>
                    <option value="distribution_drift">Distribution Drift (PSI Drift)</option>
                    <option value="extreme_anomalies">Extreme Outliers (Impossible Values)</option>
                    <option value="type_mismatch">Type Mismatch (Corrupted Strings)</option>
                    <option value="volume_drop">Volume Drop (Throughput Collapse)</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 flex items-center justify-between text-xs font-mono text-neutral-400">
            <span>Automated validation: Enabled</span>
            <span className="text-emerald">Human Gate: Active</span>
          </div>
        </div>

        {/* Right Col: Live Remediation Timeline (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-gold" />
                <span className="text-xs font-mono uppercase tracking-wider text-white font-medium">
                  Live Agent Cognitive Timeline
                </span>
              </div>
              <span className="text-[11px] font-mono text-emerald flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald animate-pulse" /> Live Stream
              </span>
            </div>

            {/* Step Progression Visualizer */}
            <div className="grid grid-cols-5 gap-2 text-center text-xs font-mono mb-6">
              {["Detect", "Diagnose", "Fix", "Validate", "Report"].map((label, idx) => {
                const isActive = recentSteps.length > idx;
                return (
                  <div
                    key={label}
                    className={`py-2 px-1 rounded-lg border transition-all ${
                      isActive
                        ? "bg-gold/15 border-gold text-gold font-medium shadow-gold-glow"
                        : "bg-surface/50 border-white/5 text-neutral-500"
                    }`}
                  >
                    <div className="text-[10px] text-neutral-400">0{idx + 1}</div>
                    <div className="mt-0.5">{label}</div>
                  </div>
                );
              })}
            </div>

            {/* Live Terminal Logs */}
            <div className="bg-[#040507] border border-white/5 rounded-xl p-4 h-[240px] overflow-y-auto space-y-3 font-mono text-xs">
              {recentSteps.length === 0 ? (
                <div className="h-full flex items-center justify-center text-neutral-500">
                  Click 'Inject Chaos Fault' to trigger autonomous multi-agent reasoning stream.
                </div>
              ) : (
                recentSteps.map((step, idx) => (
                  <div key={idx} className="border-l-2 border-gold/40 pl-3 py-1 animate-in fade-in">
                    <div className="flex items-center gap-2 text-neutral-400 text-[11px]">
                      <span className="text-gold font-semibold">[{step.agent_name}]</span>
                      <span>{step.timestamp.split("T")[1]?.slice(0, 8)}</span>
                      {step.tool_call && (
                        <span className="px-1.5 py-0.2 rounded bg-white/10 text-ice text-[10px]">
                          Tool: {step.tool_call}
                        </span>
                      )}
                    </div>
                    <p className="text-neutral-200 mt-1 leading-relaxed">{step.thought}</p>
                    {step.decision && (
                      <div className="text-emerald text-[11px] mt-1 font-semibold">
                        &rarr; Decision: {step.decision}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs font-mono text-neutral-400">
            <span>Memory search latency: 3.2ms</span>
            <span className="text-ice">Zero human paging required</span>
          </div>
        </div>
      </div>
    </section>
  );
}
