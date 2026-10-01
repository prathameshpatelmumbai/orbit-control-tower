"""
ORBIT Simulator Router
Simulates What-If operational projections under varying volume, fault rate, and latency constraints.
"""
from fastapi import APIRouter
from ..schemas import SimulatorRequest, SimulatorResponse
from ml.forecaster import SLAPredictiveForecaster

router = APIRouter(prefix="/simulate", tags=["Simulator"])
forecaster = SLAPredictiveForecaster()


@router.post("", response_model=SimulatorResponse)
async def simulate_what_if(req: SimulatorRequest):
    """
    Computes comparative before/after curves, SLA breach percentages,
    hourly downtime cost, and projected MTTR.
    """
    res = forecaster.simulate_what_if(
        data_volume_multiplier=req.data_volume_multiplier,
        fault_rate_pct=req.fault_rate_pct,
        latency_budget_ms=req.latency_budget_ms
    )
    return res
