"""
ORBIT Lineage Router
Exposes 3D spatial lineage graph, node coordinates, health states, and flow edges.
"""
from fastapi import APIRouter
from pipelines.pipeline_runner import PipelineRunner

router = APIRouter(prefix="/lineage", tags=["Lineage"])
runner = PipelineRunner()


@router.get("")
async def get_lineage():
    """
    Returns full 3D spatial dependency lineage graph.
    Consumed directly by the React Three Fiber Data Galaxy and telemetry cards.
    """
    return runner.get_lineage_graph()
