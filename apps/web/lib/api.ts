const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/events";

export async function fetchLineage() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/lineage`);
    if (!res.ok) throw new Error("Failed to fetch lineage");
    return await res.json();
  } catch (err) {
    console.warn("Using offline fallback lineage data", err);
    return getOfflineLineage();
  }
}

export async function fetchSLOMetrics() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/metrics/slo`);
    if (!res.ok) throw new Error("Failed to fetch SLO metrics");
    return await res.json();
  } catch (err) {
    return {
      overall_health: "OPTIMAL",
      system_availability_pct: 99.98,
      mean_time_to_remediation_sec: 4.8,
      total_incidents_24h: 14,
      auto_resolved_count: 14,
      data_quality_sla_pct: 99.4,
      pipelines: [
        { id: "banking", name: "Banking BFSI", sla_pct: 99.95, p95_ms: 118, status: "healthy" },
        { id: "retail", name: "Retail Orders", sla_pct: 99.88, p95_ms: 94, status: "healthy" },
        { id: "supply_chain", name: "Supply Chain", sla_pct: 99.72, p95_ms: 142, status: "healthy" },
        { id: "customer", name: "Customer Telemetry", sla_pct: 99.99, p95_ms: 48, status: "healthy" }
      ]
    };
  }
}

export async function fetchInsightsLab() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/metrics/lab`);
    if (!res.ok) throw new Error("Failed to fetch lab metrics");
    return await res.json();
  } catch (err) {
    return getOfflineLabData();
  }
}

export async function fetchScenarios() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/chaos/scenarios`);
    if (!res.ok) throw new Error("Failed to fetch scenarios");
    return await res.json();
  } catch (err) {
    return [
      { id: "black_friday_overload", name: "Black Friday Traffic Surge", domain: "retail" },
      { id: "core_banking_migration_fail", name: "Core Banking Schema Break", domain: "banking" },
      { id: "global_shipping_hub_freeze", name: "Cold Chain Telemetry Anomaly", domain: "supply_chain" }
    ];
  }
}

export async function injectChaos(payload: { domain?: string; fault_type?: string; severity?: string; scenario_id?: string }) {
  const res = await fetch(`${API_BASE}/api/v1/chaos/inject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to trigger chaos");
  return await res.json();
}

export async function postAskOrbit(query: string) {
  const res = await fetch(`${API_BASE}/api/v1/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Ask ORBIT request failed");
  return await res.json();
}

export async function postSimulate(inputs: { data_volume_multiplier: number; fault_rate_pct: number; latency_budget_ms: number }) {
  const res = await fetch(`${API_BASE}/api/v1/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(inputs),
  });
  if (!res.ok) throw new Error("Simulator request failed");
  return await res.json();
}

export function connectWebSocket(onMessage: (data: any) => void): WebSocket | null {
  try {
    const ws = new WebSocket(WS_BASE);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (e) {}
    };
    return ws;
  } catch (e) {
    return null;
  }
}

function getOfflineLineage() {
  return {
    nodes: [
      { id: "src_core_banking", name: "Core Banking Engine", type: "source", domain: "banking", layer: "source", status: "healthy", position: [-14, 4, 0], throughput_eps: 1420 },
      { id: "src_retail_pos", name: "Omnichannel Retail POS", type: "source", domain: "retail", layer: "source", status: "healthy", position: [-14, 1.5, -2], throughput_eps: 890 },
      { id: "src_supply_iot", name: "Supply Chain IoT Gateways", type: "source", domain: "supply_chain", layer: "source", status: "healthy", position: [-14, -1.5, 2], throughput_eps: 640 },
      { id: "src_web_clickstream", name: "Global Web Clickstream", type: "source", domain: "customer", layer: "source", status: "healthy", position: [-14, -4, 0], throughput_eps: 3200 },
      { id: "bronze_banking_transactions", name: "Bronze Banking Txns", type: "pipeline_stage", domain: "banking", layer: "bronze", status: "healthy", health_score: 99.8, position: [-7, 4, 0] },
      { id: "bronze_retail_orders", name: "Bronze Retail Orders", type: "pipeline_stage", domain: "retail", layer: "bronze", status: "healthy", health_score: 99.4, position: [-7, 1.5, -2] },
      { id: "bronze_supply_chain", name: "Bronze Supply Chain", type: "pipeline_stage", domain: "supply_chain", layer: "bronze", status: "healthy", health_score: 98.9, position: [-7, -1.5, 2] },
      { id: "bronze_customer_events", name: "Bronze Customer Events", type: "pipeline_stage", domain: "customer", layer: "bronze", status: "healthy", health_score: 100.0, position: [-7, -4, 0] },
      { id: "fct_banking_transactions", name: "Silver Fact Banking", type: "pipeline_stage", domain: "banking", layer: "silver", status: "healthy", position: [0, 4, 0] },
      { id: "fct_retail_orders", name: "Silver Fact Retail", type: "pipeline_stage", domain: "retail", layer: "silver", status: "healthy", position: [0, 1.5, -2] },
      { id: "fct_supply_chain", name: "Silver Fact Supply", type: "pipeline_stage", domain: "supply_chain", layer: "silver", status: "healthy", position: [0, -1.5, 2] },
      { id: "fct_customer_sessions", name: "Silver Fact Sessions", type: "pipeline_stage", domain: "customer", layer: "silver", status: "healthy", position: [0, -4, 0] },
      { id: "dm_enterprise_revenue", name: "Gold Revenue Mart", type: "data_mart", domain: "finance", layer: "gold", status: "healthy", position: [7, 3, -1] },
      { id: "dm_supply_chain_sla", name: "Gold Supply SLA Mart", type: "data_mart", domain: "supply_chain", layer: "gold", status: "healthy", position: [7, -1, 1] },
      { id: "dm_data_quality_metrics", name: "Gold Ops Health Mart", type: "data_mart", domain: "operations", layer: "gold", status: "healthy", position: [7, -3.5, 0] },
      { id: "ml_anomaly_detector", name: "Isolation Forest Model", type: "ml_model", domain: "ml", layer: "model", status: "healthy", position: [14, 3.5, 2] },
      { id: "ml_sla_forecaster", name: "XGBoost SLA Forecaster", type: "ml_model", domain: "ml", layer: "model", status: "healthy", position: [14, 1.0, -2] },
      { id: "dash_ops_control_tower", name: "ORBIT Control Tower", type: "dashboard", domain: "operations", layer: "dashboard", status: "healthy", position: [14, -4, 1] }
    ],
    edges: [
      { source: "src_core_banking", target: "bronze_banking_transactions" },
      { source: "src_retail_pos", target: "bronze_retail_orders" },
      { source: "src_supply_iot", target: "bronze_supply_chain" },
      { source: "src_web_clickstream", target: "bronze_customer_events" },
      { source: "bronze_banking_transactions", target: "fct_banking_transactions" },
      { source: "bronze_retail_orders", target: "fct_retail_orders" },
      { source: "bronze_supply_chain", target: "fct_supply_chain" },
      { source: "bronze_customer_events", target: "fct_customer_sessions" },
      { source: "fct_banking_transactions", target: "dm_enterprise_revenue" },
      { source: "fct_retail_orders", target: "dm_enterprise_revenue" },
      { source: "fct_supply_chain", target: "dm_supply_chain_sla" },
      { source: "fct_banking_transactions", target: "dm_data_quality_metrics" },
      { source: "fct_retail_orders", target: "dm_data_quality_metrics" },
      { source: "fct_supply_chain", target: "dm_data_quality_metrics" },
      { source: "fct_banking_transactions", target: "ml_anomaly_detector" },
      { source: "dm_supply_chain_sla", target: "ml_sla_forecaster" },
      { source: "dm_data_quality_metrics", target: "dash_ops_control_tower" },
      { source: "ml_anomaly_detector", target: "dash_ops_control_tower" }
    ],
    summary: {
      total_nodes: 18,
      healthy_count: 18,
      degraded_count: 0,
      unhealthy_count: 0,
      system_status: "healthy"
    }
  };
}

function getOfflineLabData() {
  const hours = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"];
  const scores = [0.08, 0.12, 0.22, 0.88, 0.24, 0.09];
  return {
    anomaly_timeline: hours.map((h, i) => ({ time: h, score: scores[i], threshold: 0.65 })),
    drift_metrics: [
      { feature: "transaction_amount", psi: 0.042, status: "stable", threshold: 0.25 },
      { feature: "risk_score", psi: 0.085, status: "stable", threshold: 0.25 },
      { feature: "client_latency_ms", psi: 0.148, status: "moderate_drift", threshold: 0.25 },
      { feature: "quantity_per_order", psi: 0.029, status: "stable", threshold: 0.25 },
      { feature: "cargo_temp_celsius", psi: 0.056, status: "stable", threshold: 0.25 }
    ],
    shap_attributions: [
      { feature: "amount", importance: 0.42, direction: "+420%", reason: "Amount surged above $45k" },
      { feature: "risk_score", importance: 0.28, direction: "+180%", reason: "Risk score elevated to 92.4" },
      { feature: "client_latency", importance: 0.18, direction: "+95%", reason: "Edge network buffer lag" },
      { feature: "account_age", importance: 0.08, direction: "-15%", reason: "Newly created account" },
      { feature: "channel", importance: 0.04, direction: "0%", reason: "Mobile app traffic" }
    ],
    forecast_bands: [
      { hour: "T+1h", predicted: 110, upper: 125, lower: 95, sla: 250 },
      { hour: "T+2h", predicted: 118, upper: 138, lower: 98, sla: 250 },
      { hour: "T+3h", predicted: 135, upper: 162, lower: 108, sla: 250 },
      { hour: "T+4h", predicted: 142, upper: 178, lower: 112, sla: 250 },
      { hour: "T+5h", predicted: 130, upper: 165, lower: 105, sla: 250 },
      { hour: "T+6h", predicted: 115, upper: 145, lower: 92, sla: 250 }
    ],
    system_sla_gauge: {
      current_pct: 99.98,
      target_pct: 99.90,
      status: "EXCELLENT",
      mttr_sec: 4.8
    }
  };
}
