"""
Integration Tests for ORBIT FastAPI REST & WebSocket Endpoints
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(parent_dir))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from services.api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_system_metrics(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "uptime_seconds" in res.json()


def test_pipelines_endpoints(client):
    res = client.get("/api/v1/pipelines")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    assert data[0]["domain"] in ["banking", "retail", "supply_chain", "customer"]

    runs_res = client.get("/api/v1/pipelines/banking/runs")
    assert runs_res.status_code == 200
    assert len(runs_res.json()) >= 1


def test_lineage_endpoint(client):
    res = client.get("/api/v1/lineage")
    assert res.status_code == 200
    graph = res.json()
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) >= 15


def test_incidents_and_trace(client):
    res = client.get("/api/v1/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert len(incidents) >= 1

    first_id = incidents[0]["incident_id"]
    trace_res = client.get(f"/api/v1/incidents/{first_id}/trace")
    assert trace_res.status_code == 200
    trace = trace_res.json()
    assert trace["incident_id"] == first_id
    assert len(trace["steps"]) >= 4


def test_ask_orbit_console(client):
    payload = {"query": "why did revenue data go stale at 3am?"}
    res = client.post("/api/v1/ask", json=payload)
    assert res.status_code == 200
    ans = res.json()
    assert "revenue" in ans["natural_language_answer"].lower()
    assert ans["generated_sql"] is not None
    assert len(ans["highlighted_lineage_nodes"]) >= 1
    assert "chart_config" in ans


def test_simulator_endpoint(client):
    payload = {
        "data_volume_multiplier": 2.0,
        "fault_rate_pct": 5.0,
        "latency_budget_ms": 300.0
    }
    res = client.post("/api/v1/simulate", json=payload)
    assert res.status_code == 200
    sim = res.json()
    assert "metrics" in sim
    assert "comparative_curve" in sim
    assert sim["metrics"]["throughput_eps"] > 4500


def test_metrics_slo_and_lab(client):
    slo_res = client.get("/api/v1/metrics/slo")
    assert slo_res.status_code == 200
    assert slo_res.json()["overall_health"] == "OPTIMAL"

    lab_res = client.get("/api/v1/metrics/lab")
    assert lab_res.status_code == 200
    lab = lab_res.json()
    assert "anomaly_timeline" in lab
    assert "drift_metrics" in lab
    assert "shap_attributions" in lab
    assert "forecast_bands" in lab


def test_chaos_inject_endpoint(client):
    payload = {
        "domain": "banking",
        "fault_type": "null_spike",
        "severity": "high"
    }
    res = client.post("/api/v1/chaos/inject", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "resolved"
    assert data["impacted_node"] == "bronze_banking_transactions"


def test_websocket_endpoint(client):
    with client.websocket_connect("/ws/events") as websocket:
        init_data = websocket.receive_json()
        assert init_data["type"] == "connection_established"
        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert resp == "pong"
