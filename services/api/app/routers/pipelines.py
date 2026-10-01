"""
ORBIT Pipelines Router
Provides listing of enterprise pipelines and execution run histories.
"""
from typing import List
from fastapi import APIRouter, HTTPException
from ..schemas import PipelineSummary, PipelineRunSummary
from datetime import datetime, timezone

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])

PIPELINES_DATA = [
    {
        "id": "banking",
        "name": "BFSI Core Banking Pipeline",
        "domain": "banking",
        "status": "healthy",
        "health_score": 99.8,
        "nodes_count": 4,
        "throughput_eps": 1420,
        "last_run_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "retail",
        "name": "Omnichannel Retail Orders Pipeline",
        "domain": "retail",
        "status": "healthy",
        "health_score": 99.2,
        "nodes_count": 4,
        "throughput_eps": 890,
        "last_run_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "supply_chain",
        "name": "Global Supply Chain Logistics",
        "domain": "supply_chain",
        "status": "healthy",
        "health_score": 98.7,
        "nodes_count": 4,
        "throughput_eps": 640,
        "last_run_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "customer",
        "name": "Customer Telemetry & Sessions",
        "domain": "customer",
        "status": "healthy",
        "health_score": 99.9,
        "nodes_count": 3,
        "throughput_eps": 3200,
        "last_run_at": datetime.now(timezone.utc).isoformat()
    }
]


@router.get("", response_model=List[PipelineSummary])
async def list_pipelines():
    """Returns active enterprise pipelines with health and throughput metrics."""
    return PIPELINES_DATA


@router.get("/{pipeline_id}/runs", response_model=List[PipelineRunSummary])
async def get_pipeline_runs(pipeline_id: str):
    """Returns historical run metadata and durations for a pipeline."""
    runs = [
        {
            "run_id": f"run_{pipeline_id}_01",
            "pipeline_id": pipeline_id,
            "status": "success",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_sec": 4.2,
            "records_processed": 12500,
            "quality_score": 99.8
        },
        {
            "run_id": f"run_{pipeline_id}_02",
            "pipeline_id": pipeline_id,
            "status": "success",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_sec": 3.9,
            "records_processed": 12480,
            "quality_score": 99.4
        }
    ]
    return runs
