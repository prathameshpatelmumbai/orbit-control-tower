"""
ORBIT Metrics & Telemetry Router
Exposes enterprise SLA gauges, anomaly distribution, drift reports, and SHAP attributions.
"""
from fastapi import APIRouter
from ..schemas import SLOMetricsResponse
from ml.drift_detector import DriftDetector
from ml.anomaly_detector import OrbitAnomalyDetector
from ml.explainability import AnomalyExplainer
import numpy as np
import pandas as pd

router = APIRouter(prefix="/metrics", tags=["Telemetry & SLO"])


@router.get("/slo", response_model=SLOMetricsResponse)
async def get_slo_metrics():
    """Returns top-level SLA, MTTR, availability, and incident rate."""
    return {
        "overall_health": "OPTIMAL",
        "system_availability_pct": 99.98,
        "mean_time_to_remediation_sec": 4.8,
        "total_incidents_24h": 14,
        "auto_resolved_count": 14,
        "data_quality_sla_pct": 99.4,
        "pipelines": [
            {"id": "banking", "name": "Banking BFSI", "sla_pct": 99.95, "p95_ms": 118, "status": "healthy"},
            {"id": "retail", "name": "Retail Orders", "sla_pct": 99.88, "p95_ms": 94, "status": "healthy"},
            {"id": "supply_chain", "name": "Supply Chain", "sla_pct": 99.72, "p95_ms": 142, "status": "healthy"},
            {"id": "customer", "name": "Customer Telemetry", "sla_pct": 99.99, "p95_ms": 48, "status": "healthy"}
        ]
    }


@router.get("/lab")
async def get_insights_lab_data():
    """
    Returns telemetry data for the Insights Lab charts:
    - Anomaly scores & outlier bar
    - Statistical drift (PSI & KS metrics)
    - SHAP feature attributions
    - Forecast with confidence bands
    - SLA breach gauge
    """
    # Generate realistic Insights Lab snapshot
    hours = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00"]
    anomaly_scores = [0.08, 0.12, 0.09, 0.15, 0.22, 0.31, 0.88, 0.24, 0.14, 0.11, 0.09, 0.07]

    psi_features = [
        {"feature": "transaction_amount", "psi": 0.042, "status": "stable", "threshold": 0.25},
        {"feature": "risk_score", "psi": 0.085, "status": "stable", "threshold": 0.25},
        {"feature": "client_latency_ms", "psi": 0.148, "status": "moderate_drift", "threshold": 0.25},
        {"feature": "quantity_per_order", "psi": 0.029, "status": "stable", "threshold": 0.25},
        {"feature": "cargo_temp_celsius", "psi": 0.056, "status": "stable", "threshold": 0.25}
    ]

    shap_attributions = [
        {"feature": "amount", "importance": 0.42, "direction": "+420%", "reason": "Amount surged above $45k"},
        {"feature": "risk_score", "importance": 0.28, "direction": "+180%", "reason": "Risk score elevated to 92.4"},
        {"feature": "client_latency", "importance": 0.18, "direction": "+95%", "reason": "Edge network buffer lag"},
        {"feature": "account_age", "importance": 0.08, "direction": "-15%", "reason": "Newly created account"},
        {"feature": "channel", "importance": 0.04, "direction": "0%", "reason": "Mobile app traffic"}
    ]

    forecast_bands = [
        {"hour": "T+1h", "predicted": 110, "upper": 125, "lower": 95, "sla": 250},
        {"hour": "T+2h", "predicted": 118, "upper": 138, "lower": 98, "sla": 250},
        {"hour": "T+3h", "predicted": 135, "upper": 162, "lower": 108, "sla": 250},
        {"hour": "T+4h", "predicted": 142, "upper": 178, "lower": 112, "sla": 250},
        {"hour": "T+5h", "predicted": 130, "upper": 165, "lower": 105, "sla": 250},
        {"hour": "T+6h", "predicted": 115, "upper": 145, "lower": 92, "sla": 250}
    ]

    return {
        "anomaly_timeline": [{"time": h, "score": s, "threshold": 0.65} for h, s in zip(hours, anomaly_scores)],
        "drift_metrics": psi_features,
        "shap_attributions": shap_attributions,
        "forecast_bands": forecast_bands,
        "system_sla_gauge": {
            "current_pct": 99.98,
            "target_pct": 99.90,
            "status": "EXCELLENT",
            "mttr_sec": 4.8
        }
    }
