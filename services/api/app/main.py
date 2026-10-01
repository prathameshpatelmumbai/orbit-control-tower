"""
ORBIT FastAPI Main Application Entrypoint
Exposes OpenAPI documented REST endpoints under /api/v1 and WebSocket telemetry on /ws/events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.api.app.config import settings

# Import routers
from services.api.app.routers.pipelines import router as pipelines_router
from services.api.app.routers.lineage import router as lineage_router
from services.api.app.routers.incidents import router as incidents_router
from services.api.app.routers.chaos import router as chaos_router
from services.api.app.routers.ask import router as ask_router
from services.api.app.routers.simulator import router as simulator_router
from services.api.app.routers.metrics import router as metrics_router
from services.api.app.routers.websocket import router as ws_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ORBIT Autonomous Data Operations Control Tower API. Powers 3D Data Galaxy, multi-agent remediation, chaos engineering, and telemetry.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST endpoints under /api/v1
app.include_router(pipelines_router, prefix=settings.API_V1_STR)
app.include_router(lineage_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(chaos_router, prefix=settings.API_V1_STR)
app.include_router(ask_router, prefix=settings.API_V1_STR)
app.include_router(simulator_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router, prefix=settings.API_V1_STR)

# Mount WebSocket endpoint
app.include_router(ws_router)


@app.get("/health", tags=["System"])
async def health_check():
    """System health verification."""
    return {
        "status": "healthy",
        "service": "orbit-api",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/metrics", tags=["System"])
async def system_metrics():
    """System operations telemetry metrics."""
    return {
        "uptime_seconds": 14280,
        "pipelines_active": 4,
        "nodes_healthy": 18,
        "nodes_degraded": 0,
        "nodes_unhealthy": 0,
        "incidents_auto_resolved": 42,
        "mean_time_to_remediation_sec": 4.8
    }
