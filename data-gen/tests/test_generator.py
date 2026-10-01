"""
Unit tests for ORBIT Enterprise Data Generator
"""
import sys
import os
import pytest

# Ensure data-gen is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from generator import EnterpriseDataGenerator
from scenarios import list_scenarios, get_scenario


def test_banking_stream_generation():
    generator = EnterpriseDataGenerator(seed=123, persist_to_duckdb=False)
    batch = generator.generate_stream("banking", count=25)
    assert len(batch) == 25
    first = batch[0]
    assert "event_id" in first
    assert "amount" in first
    assert "account_id" in first
    assert "currency" in first
    assert first["amount"] > 0


def test_retail_stream_generation():
    generator = EnterpriseDataGenerator(seed=123, persist_to_duckdb=False)
    batch = generator.generate_stream("retail", count=30)
    assert len(batch) == 30
    first = batch[0]
    assert "order_id" in first
    assert "sku" in first
    assert "warehouse_id" in first
    assert "total_amount" in first
    assert first["quantity"] >= 1


def test_supply_chain_stream_generation():
    generator = EnterpriseDataGenerator(seed=123, persist_to_duckdb=False)
    batch = generator.generate_stream("supply_chain", count=20)
    assert len(batch) == 20
    first = batch[0]
    assert "shipment_id" in first
    assert "carrier_name" in first
    assert "cargo_temp_celsius" in first
    assert "status" in first


def test_customer_stream_generation():
    generator = EnterpriseDataGenerator(seed=123, persist_to_duckdb=False)
    batch = generator.generate_stream("customer", count=40)
    assert len(batch) == 40
    first = batch[0]
    assert "event_id" in first
    assert "session_id" in first
    assert "action" in first
    assert "status_code" in first


def test_scenario_library():
    scenarios = list_scenarios()
    assert len(scenarios) >= 5
    first_id = scenarios[0]["id"]
    scenario = get_scenario(first_id)
    assert scenario is not None
    assert "faults" in scenario
    assert len(scenario["faults"]) >= 1
