"""
ORBIT Ask Console Router
Natural language query assistant translating operator questions into SQL, charts, and lineage spotlights.
"""
from fastapi import APIRouter
from ..schemas import AskOrbitRequest, AskOrbitResponse
from ..services.ask_service import ask_service

router = APIRouter(prefix="/ask", tags=["Ask ORBIT"])


@router.post("", response_model=AskOrbitResponse)
async def ask_orbit(req: AskOrbitRequest):
    """
    Analyzes natural language question, generates & runs SQL against DuckDB,
    and returns visualization chart configuration and highlighted lineage nodes.
    """
    return ask_service.process_query(req.query)
