from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    agent_name: str
    thought: str
    tool_call: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_result: Optional[Any] = None
    decision: Optional[str] = None
    timestamp: str


class IncidentState(BaseModel):
    incident_id: str
    pipeline_id: str
    node_id: str
    fault_type: str
    severity: str
    detected_metric: Dict[str, Any] = Field(default_factory=dict)
    similar_incidents: List[Dict[str, Any]] = Field(default_factory=list)
    root_cause: Optional[str] = None
    proposed_fix: Optional[Dict[str, Any]] = None
    human_approved: bool = False
    fix_applied: bool = False
    validation_passed: bool = False
    incident_report: Optional[str] = None
    trace_steps: List[AgentStep] = Field(default_factory=list)
