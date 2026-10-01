"use client";

import React, { useState, useEffect } from "react";
import { Sliders, TrendingUp, AlertCircle, DollarSign, Activity } from "lucide-react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ReferenceLine } from "recharts";
import { postSimulate } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";

export function WhatIfSimulator() {
  const [dataVolume, setDataVolume] = useState<number>(1.5);
  const [faultRate, setFaultRate] = useState<number>(3.0);
  const [latencyBudget, setLatencyBudget] = useState<number>(250);
  const [simResult, setSimResult] = useState<any>(null);

  useEffect(() => {
    postSimulate({
      data_volume_multiplier: dataVolume,
      fault_rate_pct: faultRate,
      latency_budget_ms: latencyBudget,
    }).then(setSimResult);
  }, [dataVolume, faultRate, latencyBudget]);

  return (
    <section id="simulator" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-gold/30 bg-surface/60 text-gold text-xs font-mono uppercase tracking-widest mb-4">
          <Sliders className="w-3.5 h-3.5" />
          Predictive Risk Modeling
        </div>
        <h2 className="text-3xl sm:text-5xl font-serif text-white">
          What-If Scenario Simulator
        </h2>
        <p className="text-neutral-400 text-sm sm:text-base mt-3 leading-relaxed">
          Stress-test pipeline resilience. Adjust data volume, fault rates, and latency budgets to project SLA breach risk and downtime cost curves.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Sliders Control Panel (5 cols) */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="text-xs font-mono uppercase tracking-wider text-neutral-300 border-b border-white/10 pb-4 mb-6">
              Parameter Stress Knobs
            </div>

            {/* Slider 1: Data Volume Multiplier */}
            <div className="mb-6">
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-white">Data Volume Multiplier</span>
                <span className="text-gold font-bold">{dataVolume}x</span>
              </div>
              <input
                type="range"
                min={0.5}
                max={5.0}
                step={0.1}
                value={dataVolume}
                onChange={(e) => setDataVolume(parseFloat(e.target.value))}
                className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-[#C9A96E]"
              />
              <div className="flex justify-between text-[10px] font-mono text-neutral-500 mt-1">
                <span>0.5x (Low)</span>
                <span>2.5x</span>
                <span>5.0x (Peak Surge)</span>
              </div>
            </div>

            {/* Slider 2: Injected Fault Rate */}
            <div className="mb-6">
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-white">Injected Fault Rate</span>
                <span className="text-coral font-bold">{faultRate}%</span>
              </div>
              <input
                type="range"
                min={0.0}
                max={20.0}
                step={0.5}
                value={faultRate}
                onChange={(e) => setFaultRate(parseFloat(e.target.value))}
                className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-[#FF5A5F]"
              />
              <div className="flex justify-between text-[10px] font-mono text-neutral-500 mt-1">
                <span>0% (Clean)</span>
                <span>10%</span>
                <span>20% (Heavy Chaos)</span>
              </div>
            </div>

            {/* Slider 3: Latency SLA Budget */}
            <div className="mb-6">
              <div className="flex justify-between text-xs font-mono mb-2">
                <span className="text-white">SLA Latency Budget</span>
                <span className="text-ice font-bold">{latencyBudget} ms</span>
              </div>
              <input
                type="range"
                min={100}
                max={600}
                step={25}
                value={latencyBudget}
                onChange={(e) => setLatencyBudget(parseInt(e.target.value))}
                className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-[#7CC4FF]"
              />
              <div className="flex justify-between text-[10px] font-mono text-neutral-500 mt-1">
                <span>100ms (Strict)</span>
                <span>350ms</span>
                <span>600ms (Relaxed)</span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Summary Cards */}
          {simResult && (
            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/10">
              <div className="bg-surface/60 p-3 rounded-xl border border-white/5">
                <div className="text-[10px] font-mono uppercase text-neutral-400">Throughput</div>
                <div className="text-lg font-serif text-white mt-0.5">
                  {formatNumber(simResult.metrics.throughput_eps)} EPS
                </div>
              </div>
              <div className="bg-surface/60 p-3 rounded-xl border border-white/5">
                <div className="text-[10px] font-mono uppercase text-neutral-400">Risk Cost / Hr</div>
                <div className="text-lg font-serif text-gold mt-0.5">
                  {formatCurrency(simResult.metrics.hourly_risk_cost_usd)}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Col: Comparative Before/After Chart (7 cols) */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
              <div>
                <h4 className="text-lg font-serif text-white font-medium">Comparative Latency Curve</h4>
                <div className="text-xs font-mono text-neutral-400 mt-0.5">Baseline vs Projected Stress Response</div>
              </div>
              {simResult && (
                <span
                  className={`px-2.5 py-0.5 rounded text-xs font-mono uppercase tracking-wider ${
                    simResult.metrics.sla_status === "EXCELLENT"
                      ? "bg-emerald/10 text-emerald border border-emerald/30"
                      : "bg-coral/10 text-coral border border-coral/30"
                  }`}
                >
                  SLA: {simResult.metrics.sla_status}
                </span>
              )}
            </div>

            {/* Recharts Comparative Line Chart */}
            <div className="h-[280px] w-full mt-4">
              {simResult && (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={simResult.comparative_curve}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1A1D26" />
                    <XAxis dataKey="time" stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                    <YAxis stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#12141A", borderColor: "#232733", borderRadius: 8, fontSize: 12 }}
                    />
                    <ReferenceLine
                      y={latencyBudget}
                      stroke="#FF5A5F"
                      strokeDasharray="4 4"
                      label={{ value: `SLA Budget (${latencyBudget}ms)`, fill: "#FF5A5F", fontSize: 10 }}
                    />
                    <Line
                      type="monotone"
                      name="Baseline (1.0x)"
                      dataKey="baseline_latency_ms"
                      stroke="#71717A"
                      strokeWidth={1.5}
                      strokeDasharray="3 3"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      name="Projected Curve"
                      dataKey="simulated_latency_ms"
                      stroke="#C9A96E"
                      strokeWidth={2.5}
                      dot={{ fill: "#C9A96E", r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Bottom Callout */}
          {simResult && (
            <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs font-mono text-neutral-400">
              <span>Projected MTTR: {simResult.metrics.projected_mttr_min} min</span>
              <span className="text-gold">SLA Breach Prob: {simResult.metrics.sla_breach_rate_pct}%</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
