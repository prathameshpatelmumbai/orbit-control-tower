import React from "react";
import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { PinnedScroll } from "@/components/PinnedScroll";
import { DataGalaxy3D } from "@/components/galaxy/DataGalaxy3D";
import { ChaosConsole } from "@/components/chaos/ChaosConsole";
import { AgentCrewSection } from "@/components/crew/AgentCrewSection";
import { AgentReplayScrubber } from "@/components/replay/AgentReplayScrubber";
import { InsightsLab } from "@/components/insights/InsightsLab";
import { WhatIfSimulator } from "@/components/simulator/WhatIfSimulator";
import { AskOrbitConsole } from "@/components/ask/AskOrbitConsole";
import { ArchitectureDiagram } from "@/components/architecture/ArchitectureDiagram";
import { ImpactSection } from "@/components/impact/ImpactSection";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col selection:bg-gold/30 selection:text-white">
      {/* 1. Fixed Luxury Navbar */}
      <Navbar />

      {/* 2. Cinematic Hero Section */}
      <Hero />

      {/* 3. Problem to Solution Pinned Scroll Section */}
      <PinnedScroll />

      {/* 4. Live Control Tower: 3D Data Galaxy */}
      <DataGalaxy3D />

      {/* 5. Chaos Mode Live Injection & Animated Incident Timeline */}
      <ChaosConsole />

      {/* 6. Agent Crew 3D Tilt Cards */}
      <AgentCrewSection />

      {/* 7. Agent Reasoning Replay Scrubber */}
      <AgentReplayScrubber />

      {/* 8. Insights Lab: ML Drift, SHAP, and SLA Forecaster */}
      <InsightsLab />

      {/* 9. What-If Predictive Scenario Simulator */}
      <WhatIfSimulator />

      {/* 10. Ask ORBIT Natural Language Console */}
      <AskOrbitConsole />

      {/* 11. Interactive Platform Architecture */}
      <ArchitectureDiagram />

      {/* 12. Quantified Impact & Tech Stack Marquee */}
      <ImpactSection />
    </div>
  );
}
