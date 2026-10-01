"use client";

import React, { useRef, useMemo, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";
import { LineageNode, LineageEdge, useOrbitStore } from "@/lib/store";

interface GalaxySceneProps {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export function GalaxyScene({ nodes, edges }: GalaxySceneProps) {
  const { selectedNode, setSelectedNode, highlightedNodes, isChaosRunning } = useOrbitStore();
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Map node positions for quick lookup
  const nodeMap = useMemo(() => {
    const map = new Map<string, LineageNode>();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  return (
    <>
      <color attach="background" args={["#07080B"]} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 20, 15]} intensity={1.2} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#7CC4FF" />
      <pointLight position={[10, 10, 10]} intensity={0.8} color="#C9A96E" />
      <fog attach="fog" args={["#07080B", 20, 60]} />

      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        maxDistance={45}
        minDistance={8}
        maxPolarAngle={Math.PI / 1.7}
      />

      {/* Render Edges with dynamic data flows */}
      {edges.map((edge, idx) => {
        const sourceNode = nodeMap.get(edge.source);
        const targetNode = nodeMap.get(edge.target);
        if (!sourceNode || !targetNode) return null;

        const isHighlighted =
          highlightedNodes.includes(edge.source) ||
          highlightedNodes.includes(edge.target) ||
          hoveredNodeId === edge.source ||
          hoveredNodeId === edge.target;

        const isUnhealthy =
          sourceNode.status === "unhealthy" || targetNode.status === "unhealthy";

        return (
          <EdgeLine
            key={`${edge.source}-${edge.target}-${idx}`}
            start={sourceNode.position}
            end={targetNode.position}
            isHighlighted={isHighlighted}
            isUnhealthy={isUnhealthy}
          />
        );
      })}

      {/* Render Nodes */}
      {nodes.map((node) => {
        const isSelected = selectedNode?.id === node.id;
        const isHovered = hoveredNodeId === node.id;
        const isHighlighted = highlightedNodes.includes(node.id);

        return (
          <NodeMesh
            key={node.id}
            node={node}
            isSelected={isSelected}
            isHovered={isHovered}
            isHighlighted={isHighlighted}
            onSelect={() => setSelectedNode(node)}
            onHover={(h) => setHoveredNodeId(h ? node.id : null)}
          />
        );
      })}

      {/* Autonomous Agent Traveling Light Orbs */}
      <AgentLightOrbs isChaosRunning={isChaosRunning} nodes={nodes} />
    </>
  );
}

// Individual Node with glowing sphere and outer pulse ring
function NodeMesh({
  node,
  isSelected,
  isHovered,
  isHighlighted,
  onSelect,
  onHover,
}: {
  node: LineageNode;
  isSelected: boolean;
  isHovered: boolean;
  isHighlighted: boolean;
  onSelect: () => void;
  onHover: (hovered: boolean) => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  // Determine node color
  const color = useMemo(() => {
    if (node.status === "unhealthy") return "#FF5A5F"; // Coral
    if (node.status === "degraded") return "#C9A96E"; // Gold
    if (node.layer === "source") return "#7CC4FF"; // Ice Blue
    if (node.layer === "model") return "#B388FF"; // Purple
    if (node.layer === "dashboard") return "#E2C799"; // Champagne
    return "#3DDC97"; // Emerald for healthy pipeline stages
  }, [node.status, node.layer]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (meshRef.current) {
      if (node.status === "unhealthy") {
        // Red pulse
        const pulse = 1.0 + Math.sin(t * 8) * 0.25;
        meshRef.current.scale.set(pulse, pulse, pulse);
      } else if (isHovered || isSelected) {
        meshRef.current.scale.set(1.3, 1.3, 1.3);
      } else {
        meshRef.current.scale.set(1, 1, 1);
      }
    }

    if (ringRef.current && node.status === "unhealthy") {
      const ringScale = 1.2 + (t * 2 % 2) * 0.8;
      ringRef.current.scale.set(ringScale, ringScale, ringScale);
      (ringRef.current.material as THREE.MeshBasicMaterial).opacity = Math.max(0, 1.0 - (t * 2 % 2));
    }
  });

  return (
    <group position={node.position}>
      {/* Node Sphere */}
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onSelect();
        }}
        onPointerOver={(e) => {
          e.stopPropagation();
          onHover(true);
        }}
        onPointerOut={() => onHover(false)}
      >
        <sphereGeometry args={[0.6, 24, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={node.status === "unhealthy" ? 2.5 : (isSelected || isHovered ? 1.8 : 0.8)}
          roughness={0.2}
          metalness={0.7}
        />
      </mesh>

      {/* Unhealthy Warning Pulse Ring */}
      {node.status === "unhealthy" && (
        <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.8, 0.95, 32]} />
          <meshBasicMaterial color="#FF5A5F" transparent opacity={0.8} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Outer Selection Glow Ring */}
      {(isSelected || isHighlighted) && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.9, 1.05, 32]} />
          <meshBasicMaterial color="#C9A96E" transparent opacity={0.9} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Text Label */}
      <Html distanceFactor={18} center position={[0, -0.9, 0]} className="pointer-events-none select-none">
        <div
          className={`px-2 py-0.5 rounded text-[10px] font-mono whitespace-nowrap transition-all ${
            node.status === "unhealthy"
              ? "bg-coral/20 text-coral border border-coral/50 font-bold shadow-coral-glow"
              : isSelected || isHovered
              ? "bg-gold/20 text-gold border border-gold/50 shadow-gold-glow"
              : "bg-surface/70 text-neutral-300 border border-white/10"
          }`}
        >
          {node.name}
        </div>
      </Html>
    </group>
  );
}

// Glowing Edge Line connecting nodes with animated flow
function EdgeLine({
  start,
  end,
  isHighlighted,
  isUnhealthy,
}: {
  start: [number, number, number];
  end: [number, number, number];
  isHighlighted: boolean;
  isUnhealthy: boolean;
}) {
  const lineGeometry = useMemo(() => {
    const points = [new THREE.Vector3(...start), new THREE.Vector3(...end)];
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [start, end]);

  const color = isUnhealthy ? "#FF5A5F" : (isHighlighted ? "#C9A96E" : "#232733");
  const opacity = isUnhealthy ? 0.9 : (isHighlighted ? 0.8 : 0.25);

  const lineObject = useMemo(() => {
    const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity, linewidth: isHighlighted ? 2 : 1 });
    return new THREE.Line(lineGeometry, mat);
  }, [lineGeometry, color, opacity, isHighlighted]);

  return <primitive object={lineObject} />;
}

// Traveling Agent Light Orbs representing Sentinel and Surgeon healing nodes
function AgentLightOrbs({ isChaosRunning, nodes }: { isChaosRunning: boolean; nodes: LineageNode[] }) {
  const sentinelOrb = useRef<THREE.Mesh>(null);
  const surgeonOrb = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (sentinelOrb.current && nodes.length > 4) {
      // Sentinel orbs circulates around Bronze & Silver nodes
      const idx = Math.floor(t * 0.8) % nodes.length;
      const targetPos = nodes[idx].position;
      sentinelOrb.current.position.lerp(
        new THREE.Vector3(targetPos[0], targetPos[1] + Math.sin(t * 3) * 0.5, targetPos[2]),
        0.08
      );
    }

    if (surgeonOrb.current && isChaosRunning) {
      // Surgeon orb flies to unhealthy node
      const unhealthy = nodes.find((n) => n.status === "unhealthy");
      if (unhealthy) {
        surgeonOrb.current.position.lerp(
          new THREE.Vector3(unhealthy.position[0], unhealthy.position[1], unhealthy.position[2] + 0.8),
          0.1
        );
      }
    }
  });

  return (
    <>
      {/* Sentinel Monitoring Orb */}
      <mesh ref={sentinelOrb} position={[-7, 2, 0]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshBasicMaterial color="#7CC4FF" />
        <pointLight color="#7CC4FF" intensity={2.0} distance={4} />
      </mesh>

      {/* Surgeon Healing Orb */}
      {isChaosRunning && (
        <mesh ref={surgeonOrb} position={[0, 0, 0]}>
          <sphereGeometry args={[0.35, 16, 16]} />
          <meshBasicMaterial color="#C9A96E" />
          <pointLight color="#C9A96E" intensity={3.5} distance={6} />
        </mesh>
      )}
    </>
  );
}
