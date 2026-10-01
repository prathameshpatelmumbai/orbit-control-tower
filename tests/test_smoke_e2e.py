"""
ORBIT Autonomous Data Operations Control Tower - End-to-End Smoke Test
Validates the full enterprise lifecycle across all modules:
1. Synthetic Data Generation & DuckDB Storage
2. Fault Injection & Quality Assertions
3. ML Telemetry (Anomaly, Drift, Forecasting)
4. Multi-Agent Autonomous Healing Crew (Sentinel -> Strategist)
5. FastAPI REST API Endpoints
"""

import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient

# Ensure root is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from data_gen.generator import EnterpriseDataGenerator
from data_gen.fault_injector import FaultInjector, FaultType
from data_gen.storage_manager import StorageManager

from pipelines.pipeline_runner import PipelineRunner
from pipelines.data_quality.expectations import DataQualitySuite
from ml.anomaly_detector import OrbitAnomalyDetector
from ml.drift_detector import DriftDetector
from ml.forecaster import SLAPredictiveForecaster
from agents.crew import OrbitAgentCrew
from agents.state import IncidentState
from services.api.app.main import app


def test_end_to_end_smoke_pipeline():
    """Runs a complete smoke test through all system layers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "smoke_orbit.duckdb")
        
        # 1. Data Generation & DuckDB Ingestion
        generator = EnterpriseDataGenerator(seed=42, persist_to_duckdb=False)
        banking_records = generator.generate_stream("banking", count=50)
        retail_records = generator.generate_stream("retail", count=50)
        supply_records = generator.generate_stream("supply_chain", count=50)
        customer_records = generator.generate_stream("customer", count=50)

        assert len(banking_records) == 50
        assert len(retail_records) == 50
        assert len(supply_records) == 50
        assert len(customer_records) == 50

        storage = StorageManager(db_path=test_db)
        storage.save_batch("bronze_banking_transactions", banking_records)
        assert storage.get_table_count("bronze_banking_transactions") == 50
        
        # 2. Fault Injection & Quality Check Failure Detection
        injector = FaultInjector(seed=42)
        corrupted_records, meta = injector.inject(
            banking_records, 
            FaultType.NULL_SPIKE, 
            severity="high",
            target_field="amount"
        )
        corrupted_df = pd.DataFrame(corrupted_records)
        assert corrupted_df["amount"].isna().sum() > 0

        # Validate Invariants detect failure
        suite = DataQualitySuite("test_banking_suite")
        eval_result = suite.evaluate(corrupted_df, domain="banking")
        assert eval_result["is_healthy"] is False
        assert len(eval_result["failed_expectations"]) > 0

        # 3. ML Telemetry
        # Anomaly Detector
        detector = OrbitAnomalyDetector()
        clean_df = pd.DataFrame(banking_records)
        detector.fit(clean_df, feature_cols=["amount"])
        anom_res = detector.predict(clean_df)
        assert "is_anomaly" in anom_res.columns
        assert "anomaly_score" in anom_res.columns

        # Drift Detector
        drift_det = DriftDetector()
        drift_res = drift_det.evaluate_feature_drift(clean_df, clean_df, feature_cols=["amount"])
        assert drift_res["overall_status"] == "healthy"

        # Forecaster & What-If
        forecaster = SLAPredictiveForecaster()
        forecast = forecaster.forecast_metric(historical_values=[120.0, 130.0, 140.0], horizon_steps=12)
        assert len(forecast) == 12
        sim_res = forecaster.simulate_what_if(data_volume_multiplier=1.8, fault_rate_pct=2.5, latency_budget_ms=250.0)
        assert sim_res["metrics"]["projected_mttr_min"] > 0
        assert sim_res["metrics"]["hourly_risk_cost_usd"] >= 0

        # 4. Multi-Agent Autonomous Healing Crew
        crew = OrbitAgentCrew(db_path=test_db)
        final_state = crew.run_incident_resolution(
            pipeline_id="banking_pipeline",
            node_id="bronze_banking_transactions",
            fault_type="null_spike",
            severity="critical",
            auto_approve_safe_fixes=True
        )
        assert final_state.fix_applied is True
        assert final_state.validation_passed is True
        assert len(final_state.trace_steps) >= 5
        assert final_state.incident_report is not None
        assert len(final_state.incident_report) > 50

        # 5. FastAPI REST API
        client = TestClient(app)
        
        # Health
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # Pipelines
        res = client.get("/api/v1/pipelines")
        assert res.status_code == 200
        assert len(res.json()) >= 3

        # Lineage
        res = client.get("/api/v1/lineage")
        assert res.status_code == 200
        lineage = res.json()
        assert len(lineage["nodes"]) >= 15
        assert len(lineage["edges"]) >= 15

        # Scenarios
        res = client.get("/api/v1/chaos/scenarios")
        assert res.status_code == 200
        assert len(res.json()) >= 6

        # Simulate
        res = client.post("/api/v1/simulate", json={"data_volume_multiplier": 1.5, "fault_rate_pct": 1.2, "latency_budget_ms": 250.0})
        assert res.status_code == 200
        assert "metrics" in res.json()

        # Ask
        res = client.post("/api/v1/ask", json={"query": "Show bronze banking transactions"})
        assert res.status_code == 200
        ask_data = res.json()
        assert "natural_language_answer" in ask_data
        assert "generated_sql" in ask_data

        print("\n[SMOKE TEST PASSED] All 5 core subsystem checks completed with 100% success.")


if __name__ == "__main__":
    test_end_to_end_smoke_pipeline()
