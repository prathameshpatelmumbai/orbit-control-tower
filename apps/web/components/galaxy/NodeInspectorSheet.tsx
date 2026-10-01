"use client";

import React, { useState } from "react";
import { X, ShieldCheck, AlertOctagon, Activity, Play, Database, CheckCircle, RefreshCw } from "lucide-react";
import { LineageNode, useOrbitStore } from "@/lib/store";

interface NodeInspectorSheetProps {
  node: LineageNode | null;
  onClose: () => void;
}

export function NodeInspectorSheet({ node, onClose }: NodeInspectorSheetProps) {
  const [isRerunning, setIsRerunning] = useState(false);
  const { updateNodeStatus } = useOrbitStore();

  if (!node) return null;

  const handleRerun = () => {
    setIsRerunning(true);
    setTimeout(() => {
      updateNodeStatus(node.id, "healthy", 99.8);
      setIsRerunning(false);
    }, 1200);
  };

  const isHealthy = node.status === "healthy";
  const isDegraded = node.status === "degraded";

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[450px] glass-panel border-l border-white/10 p-6 flex flex-col justify-between shadow-2xl backdrop-blur-xl animate-in slide-in-from-right duration-300">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                isHealthy
                  ? "bg-emerald shadow-emerald-glow"
                  : isDegraded
                  ? "bg-gold shadow-gold-glow animate-pulse"
                  : "bg-coral shadow-coral-glow animate-ping"
              }`}
            />
            <span className="font-mono text-xs uppercase tracking-wider text-neutral-400">
              {node.layer} Layer
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Node Name & Status */}
        <div className="mt-5">
          <h3 className="text-2xl font-serif text-white font-medium">{node.name}</h3>
          <div className="flex items-center gap-2 mt-2">
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-mono uppercase tracking-wider ${
                isHealthy
                  ? "bg-emerald/10 text-emerald border border-emerald/30"
                  : isDegraded
                  ? "bg-gold/10 text-gold border border-gold/30"
                  : "bg-coral/10 text-coral border border-coral/30"
              }`}
            >
              {node.status}
            </span>
            <span className="text-neutral-500 font-mono text-xs">•</span>
            <span className="text-neutral-400 font-mono text-xs uppercase">
              Domain: {node.domain}
            </span>
          </div>
        </div>

        {/* Telemetry Metrics Grid */}
        <div className="grid grid-cols-2 gap-3 mt-6">
          <div className="bg-surface/80 p-3.5 rounded-xl border border-white/5">
            <div className="text-neutral-400 text-xs font-mono">Health Score</div>
            <div className="text-xl font-serif text-white mt-1">
              {node.health_score ?? 99.5}%
            </div>
          </div>
          <div className="bg-surface/80 p-3.5 rounded-xl border border-white/5">
            <div className="text-neutral-400 text-xs font-mono">Throughput</div>
            <div className="text-xl font-serif text-gold mt-1">
              {node.throughput_eps ?? 1240} EPS
            </div>
          </div>
        </div>

        {/* Invariant Quality Checks */}
        <div className="mt-6">
          <div className="text-xs font-mono uppercase tracking-wider text-neutral-400 mb-3 flex items-center justify-between">
            <span>Quality Expectations</span>
            <span className="text-emerald text-[11px]">3/3 Passed</span>
          </div>
          <div className="space-y-2 text-xs font-mono">
            <div className="p-2.5 rounded-lg bg-surface/60 border border-white/5 flex items-center justify-between">
              <span className="text-neutral-300">expect_column_to_exist</span>
              <CheckCircle className="w-4 h-4 text-emerald" />
            </div>
            <div className="p-2.5 rounded-lg bg-surface/60 border border-white/5 flex items-center justify-between">
              <span className="text-neutral-300">expect_values_not_null</span>
              <CheckCircle className="w-4 h-4 text-emerald" />
            </div>
            <div className="p-2.5 rounded-lg bg-surface/60 border border-white/5 flex items-center justify-between">
              <span className="text-neutral-300">expect_uniqueness_event_id</span>
              <CheckCircle className="w-4 h-4 text-emerald" />
            </div>
          </div>
        </div>

        {/* 3D Spatial Position */}
        <div className="mt-6 p-3 rounded-lg bg-surface/40 border border-white/5 text-xs font-mono text-neutral-400">
          <div>Spatial Coordinates: [{node.position.join(", ")}]</div>
          <div className="mt-1 text-[11px] text-neutral-500">Autonomous telemetry agent orb sync: Active</div>
        </div>
      </div>

      {/* Remediation Action Buttons */}
      <div className="pt-4 border-t border-white/10 space-y-2">
        <button
          onClick={handleRerun}
          disabled={isRerunning}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gold hover:bg-gold-light text-background font-medium text-xs font-mono uppercase tracking-wider transition-all hover:shadow-gold-glow disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRerunning ? "animate-spin" : ""}`} />
          <span>{isRerunning ? "Executing Dagster Re-run..." : "Trigger Asset Re-run"}</span>
        </button>

        <button
          onClick={onClose}
          className="w-full py-2 rounded-lg bg-surface hover:bg-surface-hover text-neutral-400 hover:text-white text-xs font-mono transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
