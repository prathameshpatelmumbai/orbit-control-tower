"""
Unit and Integration Tests for ORBIT Pipelines and Quality Engine
"""
import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from pipelines.pipeline_runner import PipelineRunner
from pipelines.data_quality.expectations import DataQualitySuite


@pytest.fixture
def runner():
    return PipelineRunner()


def test_pipeline_transformations_execution(runner):
    """Verifies complete medallion materialization in DuckDB."""
    result = runner.run_all_transformations()
    assert result["status"] == "success"
    assert "fct_banking_transactions" in result["materialized_tables"]
    assert "dm_enterprise_revenue" in result["materialized_tables"]
    assert "dm_supply_chain_sla" in result["materialized_tables"]


def test_quality_suite_healthy_data():
    """Verifies that healthy baseline records pass quality checks."""
    suite = DataQualitySuite("test_suite")
    healthy_data = [
        {"event_id": f"txn_{i}", "account_id": f"acc_{i}", "customer_id": f"cust_{i}", "amount": 100.0 + i, "currency": "USD"}
        for i in range(20)
    ]
    report = suite.evaluate(healthy_data, domain="banking")
    assert report["is_healthy"] is True
    assert report["failed_tests"] == 0
    assert report["health_score"] == 100.0


def test_quality_suite_null_spike_detection():
    """Verifies that null spikes trigger failed expectations and degraded health."""
    suite = DataQualitySuite("test_suite")
    corrupted_data = [
        {"event_id": f"txn_{i}", "account_id": f"acc_{i}", "customer_id": f"cust_{i}", "amount": None if i < 15 else 150.0, "currency": "USD"}
        for i in range(20)
    ]
    report = suite.evaluate(corrupted_data, domain="banking")
    assert report["is_healthy"] is False
    assert report["failed_tests"] >= 1
    failed_names = [f["expectation"] for f in report["failed_expectations"]]
    assert "expect_column_values_to_not_be_null" in failed_names


def test_quality_suite_schema_drift_detection():
    """Verifies that renamed/dropped columns trigger critical schema failure."""
    suite = DataQualitySuite("test_suite")
    corrupted_schema = [
        {"event_id": f"txn_{i}", "account_id": f"acc_{i}", "customer_id": f"cust_{i}", "amount_legacy_v1": 250.0, "currency": "USD"}
        for i in range(10)
    ]
    report = suite.evaluate(corrupted_schema, domain="banking")
    assert report["is_healthy"] is False
    failed_cols = [f["column"] for f in report["failed_expectations"]]
    assert "amount" in failed_cols


def test_lineage_graph_structure(runner):
    """Verifies 3D lineage graph topology, coordinates, and health properties."""
    graph = runner.get_lineage_graph()
    assert "nodes" in graph
    assert "edges" in graph
    assert "summary" in graph

    assert len(graph["nodes"]) >= 15
    assert len(graph["edges"]) >= 10

    # Ensure all nodes have 3D coordinates
    for node in graph["nodes"]:
        assert len(node["position"]) == 3
        assert "status" in node
        assert node["status"] in ["healthy", "degraded", "unhealthy"]

    # Verify edge connectivity
    node_ids = {n["id"] for n in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids
