"""
ORBIT Incidents Router
Manages incident lifecycles, agent reasoning traces, and human approvals.
"""
from typing import List
from fastapi import APIRouter, HTTPException
from ..schemas import IncidentSummary, IncidentTraceResponse, IncidentApprovalRequest
from ..services.incident_service import incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentSummary])
async def list_incidents():
    """Returns all active and resolved pipeline incidents."""
    return incident_service.list_incidents()


@router.get("/{incident_id}/trace", response_model=IncidentTraceResponse)
async def get_incident_trace(incident_id: str):
    """
    Returns step-by-step agent reasoning trace for scrubber replay:
    Sentinel -> Diagnostician -> Surgeon -> Auditor -> Scribe -> Strategist.
    """
    trace = incident_service.get_incident_trace(incident_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return trace


@router.post("/{incident_id}/approve")
async def approve_incident(incident_id: str, req: IncidentApprovalRequest):
    """
    Human-in-the-loop approval gate.
    Authorizes a pending remediation action and executes remaining agent steps.
    """
    res = await incident_service.approve_incident(incident_id, approved_by=req.approved_by)
    if res.get("status") == "error":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res
