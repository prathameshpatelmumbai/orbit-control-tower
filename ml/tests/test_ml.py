"""
Unit tests for ORBIT Machine Learning & Explainability Engine
"""
import sys
import os
import pytest
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ml.anomaly_detector import OrbitAnomalyDetector
from ml.drift_detector import DriftDetector
from ml.explainability import AnomalyExplainer
from ml.forecaster import SLAPredictiveForecaster
from ml.registry import MLRegistry


@pytest.fixture
def sample_data():
    np.random.seed(42)
    n = 100
    return pd.DataFrame({
        "amount": np.random.normal(150.0, 30.0, n),
        "risk_score": np.random.uniform(5.0, 50.0, n),
        "client_latency_ms": np.random.normal(80.0, 15.0, n)
    })


def test_anomaly_detector(sample_data):
    detector = OrbitAnomalyDetector(contamination=0.08, random_state=42)
    detector.fit(sample_data, feature_cols=["amount", "risk_score", "client_latency_ms"])
    
    # Add an obvious outlier
    test_df = sample_data.copy()
    test_df.loc[0, "amount"] = 99999.0
    test_df.loc[0, "risk_score"] = 99.0

    scored = detector.predict(test_df)
    assert "anomaly_score" in scored.columns
    assert "is_anomaly" in scored.columns
    assert scored.loc[0, "anomaly_score"] > 0.7
    assert scored.loc[0, "is_anomaly"] == True

    top_anomalies = detector.get_top_anomalies(test_df, top_n=3)
    assert len(top_anomalies) >= 1
    assert top_anomalies[0]["amount"] == 99999.0


def test_drift_detector_stable(sample_data):
    detector = DriftDetector()
    base = sample_data["amount"].values
    target = base + np.random.normal(0, 1.0, len(base))
    psi = detector.calculate_psi(base, target)
    assert psi < 0.1 # Should be stable
    
    ks = detector.calculate_ks_test(base, target)
    assert ks["p_value"] > 0.05


def test_drift_detector_severe_drift(sample_data):
    detector = DriftDetector()
    base = sample_data["amount"].values
    target = base * 4.0 # 4x distribution drift
    psi = detector.calculate_psi(base, target)
    assert psi > 0.25 # Significant shift detected

    report = detector.evaluate_feature_drift(
        sample_data,
        pd.DataFrame({"amount": target, "risk_score": sample_data["risk_score"]}),
        feature_cols=["amount", "risk_score"]
    )
    assert report["overall_status"] in ["critical_drift", "warning_drift"]
    assert report["drifting_features_count"] >= 1
    assert "amount" in report["feature_metrics"]


def test_explainability(sample_data):
    explainer = AnomalyExplainer(sample_data, feature_cols=["amount", "risk_score", "client_latency_ms"])
    anomalous_instance = {
        "amount": 45000.0, # massive deviation
        "risk_score": 15.0, # normal
        "client_latency_ms": 78.0 # normal
    }
    attributions = explainer.explain_instance(anomalous_instance, top_k=3)
    assert len(attributions) == 3
    assert attributions[0]["feature"] == "amount"
    assert attributions[0]["direction"] == "elevated"
    assert attributions[0]["contribution_pct"] > 70.0


def test_sla_forecaster_and_simulator():
    forecaster = SLAPredictiveForecaster(base_sla_latency_ms=200.0)
    forecast = forecaster.forecast_metric([100.0, 110.0, 120.0, 115.0, 130.0], horizon_steps=6)
    assert len(forecast) == 6
    assert "upper_bound" in forecast[0]
    assert "lower_bound" in forecast[0]
    assert forecast[0]["upper_bound"] >= forecast[0]["predicted"]

    # Test What-If Simulator
    sim = forecaster.simulate_what_if(data_volume_multiplier=2.5, fault_rate_pct=8.0, latency_budget_ms=250.0)
    assert "metrics" in sim
    assert "comparative_curve" in sim
    assert sim["metrics"]["throughput_eps"] > 4500
    assert sim["metrics"]["projected_latency_ms"] > 150.0
    assert len(sim["comparative_curve"]) == 6


def test_ml_registry():
    registry = MLRegistry()
    run = registry.log_model_run(
        model_name="test_isolation_forest",
        version="v1.0.1",
        params={"contamination": 0.05, "n_estimators": 100},
        metrics={"f1_score": 0.942, "max_psi": 0.04}
    )
    assert run["model_name"] == "test_isolation_forest"
    assert "run_id" in run

    history = registry.get_latest_models()
    assert len(history) >= 1
    assert history[0]["model_name"] == "test_isolation_forest"
