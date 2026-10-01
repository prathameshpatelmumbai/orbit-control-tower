"""
Unit tests for ORBIT Fault Injection Engine
Validates all 8+ failure categories against strict statistical and schema invariants.
"""
import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fault_injector import FaultInjector, FaultType
from streams.banking import generate_banking_batch
from streams.retail import generate_retail_batch


@pytest.fixture
def banking_sample():
    return generate_banking_batch(count=100, seed=42)


@pytest.fixture
def injector():
    return FaultInjector(seed=42)


def test_schema_drift(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.SCHEMA_DRIFT, target_field="amount")
    assert meta["fault_type"] == "schema_drift"
    assert "amount" not in corrupted[0]
    assert "amount_legacy_v1" in corrupted[0]


def test_null_spike(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.NULL_SPIKE, severity="high", target_field="customer_id")
    assert meta["fault_type"] == "null_spike"
    assert meta["null_count"] > 25
    null_rows = [r for r in corrupted if r["customer_id"] is None]
    assert len(null_rows) == meta["null_count"]


def test_late_arrivals(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.LATE_ARRIVALS, severity="high")
    assert meta["fault_type"] == "late_arrivals"
    late_events = [r for r in corrupted if r.get("_is_late_arriving") is True]
    assert len(late_events) > 10


def test_duplicate_events(banking_sample, injector):
    orig_len = len(banking_sample)
    corrupted, meta = injector.inject(banking_sample, FaultType.DUPLICATE_EVENTS, severity="medium")
    assert meta["fault_type"] == "duplicate_events"
    assert len(corrupted) > orig_len
    assert meta["duplicates_injected"] == len(corrupted) - orig_len


def test_distribution_drift(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.DISTRIBUTION_DRIFT, severity="high", target_field="amount")
    assert meta["fault_type"] == "distribution_drift"
    orig_avg = sum(r["amount"] for r in banking_sample) / len(banking_sample)
    drifted_avg = sum(r["amount"] for r in corrupted) / len(corrupted)
    assert drifted_avg > orig_avg * 5.0


def test_extreme_anomalies(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.EXTREME_ANOMALIES, target_field="amount")
    assert meta["fault_type"] == "extreme_anomalies"
    anomalies = [r for r in corrupted if r.get("_injected_anomaly") is True]
    assert len(anomalies) >= 2


def test_type_mismatch(banking_sample, injector):
    corrupted, meta = injector.inject(banking_sample, FaultType.TYPE_MISMATCH, severity="high", target_field="amount")
    assert meta["fault_type"] == "type_mismatch"
    string_amounts = [r for r in corrupted if isinstance(r["amount"], str)]
    assert len(string_amounts) > 15


def test_volume_drop(banking_sample, injector):
    orig_len = len(banking_sample)
    corrupted, meta = injector.inject(banking_sample, FaultType.VOLUME_DROP, severity="high")
    assert meta["fault_type"] == "volume_drop"
    assert len(corrupted) < orig_len * 0.5
