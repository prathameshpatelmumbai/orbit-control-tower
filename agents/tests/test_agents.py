"""
Unit and Integration Tests for ORBIT Multi-Agent Crew & MCP Tools
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

from agents.tools import OrbitTools
from agents.mcp_server import OrbitMCPServer
from agents.memory import IncidentMemoryStore
from agents.crew import OrbitAgentCrew


@pytest.fixture
def tools():
    return OrbitTools()


@pytest.fixture
def mcp_server():
    return OrbitMCPServer()


@pytest.fixture
def memory_store():
    return IncidentMemoryStore()


@pytest.fixture
def crew():
    return OrbitAgentCrew()


def test_mcp_tool_definitions(mcp_server):
    defs = mcp_server.get_tool_definitions()
    assert len(defs) == 5
    names = [d["name"] for d in defs]
    assert "run_sql" in names
    assert "get_lineage" in names
    assert "rerun_task" in names
    assert "quarantine_batch" in names
    assert "get_metrics" in names


def test_mcp_run_sql(mcp_server):
    res = mcp_server.call_tool("run_sql", {"query": "SELECT 1 as test_val"})
    assert res["status"] == "success"
    assert res["rows"][0]["test_val"] == 1


def test_mcp_get_lineage(mcp_server):
    res = mcp_server.call_tool("get_lineage", {})
    assert res["status"] == "success"
    assert "lineage" in res
    assert len(res["lineage"]["nodes"]) >= 15


def test_incident_memory_search(memory_store):
    query = "schema migration renamed column amount in banking"
    matches = memory_store.search_similar_incidents(query, top_k=2)
    assert len(matches) >= 1
    assert matches[0]["similarity_score"] > 0.2
    assert "schema" in matches[0]["title"].lower() or "banking" in matches[0]["title"].lower()


def test_agent_crew_end_to_end_resolution(crew):
    state = crew.run_incident_resolution(
        pipeline_id="banking_transactions_pipeline",
        node_id="bronze_banking_transactions",
        fault_type="null_spike",
        severity="high",
        auto_approve_safe_fixes=True
    )

    assert state.incident_id.startswith("inc_")
    assert state.fix_applied is True
    assert state.validation_passed is True
    assert state.incident_report is not None

    # Check that all 6 agents took actions
    agent_names = [s.agent_name for s in state.trace_steps]
    assert "Sentinel" in agent_names
    assert "Diagnostician" in agent_names
    assert "Surgeon" in agent_names
    assert "Auditor" in agent_names
    assert "Scribe" in agent_names
    assert "Strategist" in agent_names


def test_human_in_the_loop_gate(crew):
    # Without auto-approval, risky fault stops at gate
    state = crew.run_incident_resolution(
        pipeline_id="banking_transactions_pipeline",
        node_id="bronze_banking_transactions",
        fault_type="schema_drift",
        severity="high",
        auto_approve_safe_fixes=False
    )

    agent_names = [s.agent_name for s in state.trace_steps]
    assert "ApprovalGate" in agent_names
    assert "Surgeon" not in agent_names # Did not proceed past gate
