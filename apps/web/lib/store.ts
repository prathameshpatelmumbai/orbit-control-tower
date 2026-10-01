import { create } from "zustand";

export interface LineageNode {
  id: string;
  name: string;
  type: string;
  domain: string;
  layer: string;
  status: "healthy" | "degraded" | "unhealthy";
  health_score?: number;
  position: [number, number, number];
  throughput_eps?: number;
  records?: number;
  failed_expectations?: Array<{ expectation: string; details: any }>;
}

export interface LineageEdge {
  source: string;
  target: string;
}

export interface AgentStep {
  agent_name: string;
  thought: string;
  tool_call?: string;
  tool_args?: any;
  tool_result?: any;
  decision?: string;
  timestamp: string;
}

export interface IncidentState {
  incident_id: string;
  pipeline_id: string;
  node_id: string;
  fault_type: string;
  severity: string;
  root_cause?: string;
  proposed_fix?: any;
  fix_applied: boolean;
  validation_passed: boolean;
  incident_report?: string;
  steps: AgentStep[];
}

interface OrbitState {
  // Lineage & 3D Galaxy
  nodes: LineageNode[];
  edges: LineageEdge[];
  selectedNode: LineageNode | null;
  highlightedNodes: string[];
  systemHealth: "healthy" | "degraded" | "unhealthy";
  systemScore: number;
  setSelectedNode: (node: LineageNode | null) => void;
  setHighlightedNodes: (nodeIds: string[]) => void;
  setNodes: (nodes: LineageNode[]) => void;
  updateNodeStatus: (nodeId: string, status: "healthy" | "degraded" | "unhealthy", healthScore?: number) => void;

  // Chaos & Incidents
  isChaosRunning: boolean;
  currentIncident: IncidentState | null;
  recentSteps: AgentStep[];
  setIsChaosRunning: (running: boolean) => void;
  setCurrentIncident: (incident: IncidentState | null) => void;
  addAgentStep: (step: AgentStep) => void;

  // Replay scrubber
  replayIndex: number;
  setReplayIndex: (index: number) => void;
}

export const useOrbitStore = create<OrbitState>((set) => ({
  nodes: [],
  edges: [],
  selectedNode: null,
  highlightedNodes: [],
  systemHealth: "healthy",
  systemScore: 99.8,
  setSelectedNode: (node) => set({ selectedNode: node }),
  setHighlightedNodes: (nodeIds) => set({ highlightedNodes: nodeIds }),
  setNodes: (nodes) => set({ nodes }),
  updateNodeStatus: (nodeId, status, healthScore) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId
          ? { ...n, status, health_score: healthScore ?? (status === "healthy" ? 99.5 : 35.0) }
          : n
      ),
      systemHealth: status === "unhealthy" ? "degraded" : state.systemHealth,
    })),

  isChaosRunning: false,
  currentIncident: null,
  recentSteps: [],
  setIsChaosRunning: (running) => set({ isChaosRunning: running }),
  setCurrentIncident: (incident) =>
    set({
      currentIncident: incident,
      recentSteps: incident ? incident.steps : [],
      replayIndex: incident ? incident.steps.length - 1 : 0,
    }),
  addAgentStep: (step) =>
    set((state) => ({
      recentSteps: [...state.recentSteps, step],
      replayIndex: state.recentSteps.length,
    })),

  replayIndex: 0,
  setReplayIndex: (index) => set({ replayIndex: index }),
}));
