from typing import List, Dict, Any
from fastapi import APIRouter
from ..schemas import ChaosInjectRequest, ChaosInjectResponse
from ..services.incident_service import incident_service


try:
    from data_gen.scenarios import list_scenarios
except (ImportError, ModuleNotFoundError):
    import sys
    data_gen_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "data-gen")
    if data_gen_path not in sys.path:
        sys.path.insert(0, data_gen_path)
    from scenarios import list_scenarios



router = APIRouter(prefix="/chaos", tags=["Chaos Engineering"])


@router.post("/inject", response_model=ChaosInjectResponse)
async def inject_chaos(req: ChaosInjectRequest):
    """
    Triggers a live chaos fault into the enterprise stream and launches
    the autonomous multi-agent crew live resolution cycle.
    """
    result = await incident_service.inject_chaos_and_resolve(
        domain=req.domain,
        fault_type=req.fault_type,
        severity=req.severity,
        target_field=req.target_field,
        scenario_id=req.scenario_id
    )
    return result


@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def get_scenarios():
    """Returns curated seedable scenario library for the Chaos Mode UI."""
    return list_scenarios()
