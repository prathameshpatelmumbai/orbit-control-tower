"""
ORBIT Pydantic API Schemas
Typed contracts for REST endpoints and WebSocket event streams.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# --- Pipelines & Runs ---
class PipelineRunSummary(BaseModel):
    run_id: str
    pipeline_id: str
    status: str
    started_at: str
    duration_sec: float
    records_processed: int
    quality_score: float


class PipelineSummary(BaseModel):
    id: str
    name: str
    domain: str
    status: str
    health_score: float
    nodes_count: int
    throughput_eps: int
    last_run_at: str


# --- Chaos Injection ---
class ChaosInjectRequest(BaseModel):
    domain: str = Field(default="banking", description="Target domain: banking, retail, supply_chain, customer")
    fault_type: str = Field(default="null_spike", description="Fault category")
    severity: str = Field(default="high", description="low, medium, high")
    target_field: Optional[str] = None
    scenario_id: Optional[str] = None


class ChaosInjectResponse(BaseModel):
    status: str
    incident_id: str
    fault_type: str
    domain: str
    severity: str
    impacted_node: str
    message: str
    timestamp: str


# --- Incidents & Trace ---
class IncidentSummary(BaseModel):
    incident_id: str
    title: str
    pipeline_id: str
    node_id: str
    fault_type: str
    severity: str
    status: str
    requires_approval: bool = False
    validation_passed: bool = False
    created_at: str
    resolved_at: Optional[str] = None


class IncidentApprovalRequest(BaseModel):
    approved_by: str = "operator"
    comment: Optional[str] = "Approved via ORBIT Control Tower"


class AgentStepSchema(BaseModel):
    agent_name: str
    thought: str
    tool_call: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    decision: Optional[str] = None
    timestamp: str


class IncidentTraceResponse(BaseModel):
    incident_id: str
    pipeline_id: str
    node_id: str
    fault_type: str
    severity: str
    root_cause: Optional[str] = None
    proposed_fix: Optional[Dict[str, Any]] = None
    fix_applied: bool = False
    validation_passed: bool = False
    incident_report: Optional[str] = None
    steps: List[AgentStepSchema]


# --- Ask ORBIT (NL Ops Console) ---
class AskOrbitRequest(BaseModel):
    query: str = Field(..., description="Natural language question, e.g. 'why did revenue data go stale at 3am?'")


class AskOrbitResponse(BaseModel):
    query: str
    natural_language_answer: str
    generated_sql: Optional[str] = None
    sql_result: Optional[List[Dict[str, Any]]] = None
    chart_config: Optional[Dict[str, Any]] = None
    highlighted_lineage_nodes: List[str] = Field(default_factory=list)
    confidence_score: float = 0.95


# --- What-If Simulator ---
class SimulatorRequest(BaseModel):
    data_volume_multiplier: float = Field(default=1.0, ge=0.2, le=10.0)
    fault_rate_pct: float = Field(default=2.0, ge=0.0, le=50.0)
    latency_budget_ms: float = Field(default=250.0, ge=50.0, le=2000.0)


class SimulatorResponse(BaseModel):
    inputs: Dict[str, Any]
    metrics: Dict[str, Any]
    comparative_curve: List[Dict[str, Any]]


# --- SLO & Metrics ---
class SLOMetricsResponse(BaseModel):
    overall_health: str
    system_availability_pct: float
    mean_time_to_remediation_sec: float
    total_incidents_24h: int
    auto_resolved_count: int
    data_quality_sla_pct: float
    pipelines: List[Dict[str, Any]]
