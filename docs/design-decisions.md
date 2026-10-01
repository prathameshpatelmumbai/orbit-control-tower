# ORBIT: Architectural Design Decisions

## 1. System Vision & Paradigm
ORBIT is designed as an **Autonomous Data Operations Control Tower**, transforming passive data engineering operations into a proactive, self-healing system. Rather than relying on static dashboard alerts and manual on-call paging, ORBIT introduces autonomous multi-agent cognitive loops to monitor, isolate, fix, and audit data pipeline disruptions.

---

## 2. Core Architectural Decisions

### 2.1 Multi-Agent Orchestration via LangGraph
- **Decision**: Adopt a stateful directed graph architecture using **LangGraph** with a specialized crew of 6 agents (Sentinel, Diagnostician, Surgeon, Auditor, Scribe, Strategist).
- **Rationale**: Linear chains (ReAct / sequential agents) fail when a diagnostic hypothesis is disproven or when a fix fails validation. LangGraph allows cyclical branching: if the *Auditor* detects residual schema errors after the *Surgeon* applies a fix, execution can route back to the *Diagnostician* with updated sandbox metrics.
- **Human-in-the-Loop (HITL)**: Fixes categorized as destructive (e.g., dropping partitions or altering primary keys) pause execution with a pending token awaiting human approval via the REST API or UI.

### 2.2 Storage & Vector Memory Architecture
- **PostgreSQL + pgvector**: Stores pipeline configurations, incident metadata, and vector embeddings of past incident postmortems. When a new fault emerges, semantic similarity search retrieves historical resolutions in sub-10ms.
- **DuckDB**: Embedded columnar engine for in-memory and local file-based analytics. Enables sub-second analytical aggregations and simulated What-If queries without heavy cluster overhead.
- **Redis Streams**: Acts as the real-time event bus connecting Python telemetry emitters, multi-agent status transitions, and FastAPI WebSocket handlers.

### 2.3 Medallion Pipeline Architecture (Dagster + dbt)
- **Bronze Layer**: Raw synthetic streaming data from banking transactions, retail orders/inventory, supply chain shipments, and customer telemetry.
- **Silver Layer**: Cleansed, typed, deduplicated, and enriched tables with automated schema conformance tests.
- **Gold Layer**: Dimensionally modeled business aggregations (Daily Revenue, SLA metrics, Inventory turnover).
- **Dagster**: Software-defined assets orchestrating dependencies, data quality checks, and lineage tracking.

### 2.4 Machine Learning & Statistical Drift Detection
- **Anomaly Detection**: Isolation Forests coupled with trend-adjusted sliding windows for time-series throughput anomalies.
- **Drift Detection**: Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests comparing 7-day baseline distributions against live hourly windows.
- **Explainability**: SHAP (SHapley Additive exPlanations) values computed for flagged anomalies to highlight exact feature contributions to the *Diagnostician* agent.

### 2.5 Luxury Cinematic Frontend Design
- **Visual Aesthetic**: Obsidian black (`#07080B`) backdrop, graphite glass surfaces, champagne gold accents (`#C9A96E`), electric ice-blue glows (`#7CC4FF`), and alert coral (`#FF5A5F`).
- **3D Data Galaxy**: WebGL scene built using Three.js and React Three Fiber. Data nodes are represented as glowing celestial bodies with dynamic particle streams representing data flow. Red pulsing indicators highlight degraded nodes, and agent light orbs travel graph edges during active remediation.
- **Perceptual Performance**: DPR capped at 2.0, instanced geometry for node meshes, Bloom and Chromatic Aberration selectively enabled via post-processing, and fallback to 2D canvas on low-power devices.
