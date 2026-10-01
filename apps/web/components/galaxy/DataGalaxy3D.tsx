"use client";

import React, { useEffect, useState, Suspense } from "react";
import dynamic from "next/dynamic";
import { Canvas } from "@react-three/fiber";
import { useOrbitStore } from "@/lib/store";
import { fetchLineage, connectWebSocket } from "@/lib/api";
import { GalaxyScene } from "./GalaxyScene";
import { NodeInspectorSheet } from "./NodeInspectorSheet";
import { Layers, RotateCcw, Shield, Activity, Eye, Sparkles } from "lucide-react";

export function DataGalaxy3D() {
  const {
    nodes,
    edges,
    setNodes,
    selectedNode,
    setSelectedNode,
    updateNodeStatus,
    addAgentStep,
    setIsChaosRunning
  } = useOrbitStore();

  const [isLoading, setIsLoading] = useState(true);

  // Fetch initial lineage graph and connect WebSocket
  useEffect(() => {
    let ws: WebSocket | null = null;

    async function loadData() {
      setIsLoading(true);
      const data = await fetchLineage();
      if (data && data.nodes) {
        setNodes(data.nodes);
        useOrbitStore.setState({ edges: data.edges });
      }
      setIsLoading(false);

      // Connect WebSocket for live events
      ws = connectWebSocket((event) => {
        if (event.type === "node_health_update") {
          updateNodeStatus(event.node_id, event.status, event.health_score);
          if (event.status === "unhealthy") {
            setIsChaosRunning(true);
          } else if (event.status === "healthy") {
            setIsChaosRunning(false);
          }
        } else if (event.type === "agent_thought") {
          addAgentStep({
            agent_name: event.agent_name,
            thought: event.thought,
            tool_call: event.tool_call,
            decision: event.decision,
            timestamp: event.timestamp
          });
        }
      });
    }

    loadData();

    return () => {
      if (ws) ws.close();
    };
  }, []);

  return (
    <section id="galaxy" className="relative w-full h-[90vh] min-h-[650px] bg-background border-y border-white/5 flex flex-col overflow-hidden">
      {/* Top Floating Control Bar */}
      <div className="absolute top-6 left-6 z-20 flex flex-wrap items-center gap-3">
        <div className="glass-panel px-4 py-2 rounded-xl flex items-center gap-3 border-hairline">
          <div className="w-2 h-2 rounded-full bg-gold animate-pulse" />
          <span className="text-xs font-mono uppercase tracking-widest text-white font-medium">
            3D Data Galaxy
          </span>
          <span className="text-neutral-500 font-mono text-xs">|</span>
          <span className="text-neutral-400 font-mono text-xs">
            {nodes.length} Spatial Lineage Nodes
          </span>
        </div>

        {/* Legend */}
        <div className="hidden lg:flex items-center gap-4 glass-panel px-4 py-2 rounded-xl text-[11px] font-mono border-hairline text-neutral-300">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-ice" />
            <span>Sources</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald" />
            <span>Medallion</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#B388FF]" />
            <span>ML Models</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-gold" />
            <span>Dashboards</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-coral animate-ping" />
            <span>Fault Alert</span>
          </div>
        </div>
      </div>

      {/* Floating Instructions Bottom Left */}
      <div className="absolute bottom-6 left-6 z-20 glass-panel px-4 py-2 rounded-lg border-hairline text-xs font-mono text-neutral-400 hidden sm:block">
        Left Click + Drag: Rotate • Right Click: Pan • Scroll: Zoom • Click Node: Inspect
      </div>

      {/* 3D Canvas */}
      <div className="w-full h-full relative cursor-grab active:cursor-grabbing">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center text-gold font-mono text-sm">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-gold animate-ping" />
              Initializing 3D Lineage Mesh...
            </div>
          </div>
        ) : (
          <Canvas
            camera={{ position: [0, 2, 28], fov: 45 }}
            dpr={[1, 2]} // Cap DPR at 2 for optimal performance
            gl={{ antialias: true, alpha: false }}
          >
            <Suspense fallback={null}>
              <GalaxyScene nodes={nodes} edges={edges} />
            </Suspense>
          </Canvas>
        )}
      </div>

      {/* Side Panel Inspector Sheet */}
      <NodeInspectorSheet
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </section>
  );
}
