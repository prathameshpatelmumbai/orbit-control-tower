"use client";

import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { Activity, BarChart3, TrendingUp, AlertTriangle, ShieldCheck } from "lucide-react";
import { fetchInsightsLab } from "@/lib/api";

export function InsightsLab() {
  const [labData, setLabData] = useState<any>(null);

  useEffect(() => {
    fetchInsightsLab().then(setLabData);
  }, []);

  if (!labData) return null;

  return (
    <section id="insights" className="py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-gold/30 bg-surface/60 text-gold text-xs font-mono uppercase tracking-widest mb-4">
          <Activity className="w-3.5 h-3.5" />
          ML Telemetry & Explainability
        </div>
        <h2 className="text-3xl sm:text-5xl font-serif text-white">
          The Insights Lab
        </h2>
        <p className="text-neutral-400 text-sm sm:text-base mt-3 leading-relaxed">
          Isolation Forest anomaly scores, Population Stability Index (PSI) drift monitoring, and additive SHAP feature attributions in real time.
        </p>
      </div>

      {/* Grid of 4 Core Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Anomaly Scores Timeline */}
        <div className="glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-lg font-serif text-white font-medium">Anomaly Scoring Timeline</h4>
                <div className="text-xs font-mono text-neutral-400 mt-0.5">Isolation Forest dynamic contamination threshold (0.65)</div>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-coral/10 text-coral border border-coral/30 text-[10px] font-mono uppercase">
                1 Outlier Flagged
              </span>
            </div>

            <div className="h-[220px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={labData.anomaly_timeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1A1D26" />
                  <XAxis dataKey="time" stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <YAxis domain={[0, 1]} stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#12141A", borderColor: "#232733", borderRadius: 8, fontSize: 12 }}
                  />
                  <ReferenceLine y={0.65} stroke="#FF5A5F" strokeDasharray="4 4" label={{ value: "Threshold", fill: "#FF5A5F", fontSize: 10 }} />
                  <Line type="monotone" dataKey="score" stroke="#C9A96E" strokeWidth={2} dot={{ fill: "#C9A96E", r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-neutral-400 flex justify-between">
            <span>Peak anomaly: 0.88 at 12:00 UTC</span>
            <span className="text-emerald">Remediated in 4.8s</span>
          </div>
        </div>

        {/* Chart 2: Statistical Drift (PSI) */}
        <div className="glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-lg font-serif text-white font-medium">Population Stability Index (PSI)</h4>
                <div className="text-xs font-mono text-neutral-400 mt-0.5">Continuous distribution divergence tracking</div>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-emerald/10 text-emerald border border-emerald/30 text-[10px] font-mono uppercase">
                All &lt; 0.25 Threshold
              </span>
            </div>

            <div className="h-[220px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={labData.drift_metrics} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1A1D26" />
                  <XAxis type="number" domain={[0, 0.3]} stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <YAxis dataKey="feature" type="category" width={110} stroke="#71717A" tick={{ fontSize: 10, fill: "#A1A1AA" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#12141A", borderColor: "#232733", borderRadius: 8, fontSize: 12 }}
                  />
                  <ReferenceLine x={0.25} stroke="#FF5A5F" strokeDasharray="4 4" label={{ value: "Critical (0.25)", fill: "#FF5A5F", fontSize: 10 }} />
                  <Bar dataKey="psi" fill="#7CC4FF" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-neutral-400 flex justify-between">
            <span>Max PSI: 0.148 (client_latency_ms)</span>
            <span className="text-ice">KS Test p-val &gt; 0.05</span>
          </div>
        </div>

        {/* Chart 3: SHAP Feature Attribution */}
        <div className="glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-lg font-serif text-white font-medium">SHAP Feature Attribution</h4>
                <div className="text-xs font-mono text-neutral-400 mt-0.5">Additive contribution breakdown for flagged incident</div>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-gold/10 text-gold border border-gold/30 text-[10px] font-mono uppercase">
                Explainability
              </span>
            </div>

            <div className="h-[220px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={labData.shap_attributions}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1A1D26" />
                  <XAxis dataKey="feature" stroke="#71717A" tick={{ fontSize: 10, fill: "#71717A" }} />
                  <YAxis stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#12141A", borderColor: "#232733", borderRadius: 8, fontSize: 12 }}
                  />
                  <Bar dataKey="importance" fill="#C9A96E" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-neutral-400 flex justify-between">
            <span>Top driver: 'amount' (+42% impact)</span>
            <span className="text-neutral-500 font-mono">Additive Shapley Values</span>
          </div>
        </div>

        {/* Chart 4: SLA Forecast & Confidence Bands */}
        <div className="glass-panel p-6 rounded-2xl border-hairline flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-lg font-serif text-white font-medium">SLA Latency Forecast (T+6h)</h4>
                <div className="text-xs font-mono text-neutral-400 mt-0.5">XGBoost prediction with 95% confidence bands</div>
              </div>
              <span className="px-2.5 py-0.5 rounded bg-emerald/10 text-emerald border border-emerald/30 text-[10px] font-mono uppercase">
                Zero SLA Breach Risk
              </span>
            </div>

            <div className="h-[220px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={labData.forecast_bands}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1A1D26" />
                  <XAxis dataKey="hour" stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <YAxis domain={[50, 300]} stroke="#71717A" tick={{ fontSize: 11, fill: "#71717A" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#12141A", borderColor: "#232733", borderRadius: 8, fontSize: 12 }}
                  />
                  <ReferenceLine y={250} stroke="#FF5A5F" strokeDasharray="4 4" label={{ value: "SLA Limit (250ms)", fill: "#FF5A5F", fontSize: 10 }} />
                  <Area type="monotone" dataKey="upper" stroke="none" fill="#7CC4FF" fillOpacity={0.15} />
                  <Area type="monotone" dataKey="lower" stroke="none" fill="#07080B" fillOpacity={1} />
                  <Line type="monotone" dataKey="predicted" stroke="#7CC4FF" strokeWidth={2} dot={{ fill: "#7CC4FF", r: 3 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/5 text-[11px] font-mono text-neutral-400 flex justify-between">
            <span>Projected max: 178ms at T+4h</span>
            <span className="text-emerald">Budget buffer: 72ms</span>
          </div>
        </div>
      </div>
    </section>
  );
}
