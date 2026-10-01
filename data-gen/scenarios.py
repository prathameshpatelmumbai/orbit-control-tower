from typing import Dict, Any, List

try:
    from .fault_injector import FaultType
except (ImportError, ValueError):
    from fault_injector import FaultType




SCENARIO_LIBRARY: Dict[str, Dict[str, Any]] = {
    "black_friday_overload": {
        "id": "black_friday_overload",
        "name": "Black Friday Traffic Surge & Inventory Race",
        "domain": "retail",
        "description": "Massive concurrency creates duplicate event replay and inventory count desynchronization.",
        "seed": 101,
        "pipeline_target": "retail_orders_pipeline",
        "node_target": "node_retail_orders_clean",
        "faults": [
            {"fault_type": FaultType.DUPLICATE_EVENTS, "severity": "high"},
            {"fault_type": FaultType.LATE_ARRIVALS, "severity": "medium", "target_field": "timestamp"}
        ]
    },
    "core_banking_migration_fail": {
        "id": "core_banking_migration_fail",
        "name": "Legacy Core Banking Schema Break",
        "domain": "banking",
        "description": "Upstream partner database migration dropped backward-compatible schema mappings and caused null spikes.",
        "seed": 202,
        "pipeline_target": "banking_transactions_pipeline",
        "node_target": "node_banking_txns_raw",
        "faults": [
            {"fault_type": FaultType.SCHEMA_DRIFT, "severity": "high", "target_field": "amount"},
            {"fault_type": FaultType.NULL_SPIKE, "severity": "high", "target_field": "account_id"}
        ]
    },
    "global_shipping_hub_freeze": {
        "id": "global_shipping_hub_freeze",
        "name": "Logistics Cold Chain & Telemetry Anomaly",
        "domain": "supply_chain",
        "description": "IoT sensory disruption injects impossible extreme temperatures and delayed arrivals.",
        "seed": 303,
        "pipeline_target": "supply_chain_pipeline",
        "node_target": "node_supply_chain_silver",
        "faults": [
            {"fault_type": FaultType.EXTREME_ANOMALIES, "severity": "high", "target_field": "cargo_temp_celsius"},
            {"fault_type": FaultType.LATE_ARRIVALS, "severity": "high", "target_field": "timestamp"}
        ]
    },
    "upstream_payment_gateway_down": {
        "id": "upstream_payment_gateway_down",
        "name": "Payment Gateway Circuit Breaker Trip",
        "domain": "banking",
        "description": "Sudden 90% throughput drop combined with type-mismatched error payloads.",
        "seed": 404,
        "pipeline_target": "banking_transactions_pipeline",
        "node_target": "node_banking_settlement_gold",
        "faults": [
            {"fault_type": FaultType.VOLUME_DROP, "severity": "high"},
            {"fault_type": FaultType.TYPE_MISMATCH, "severity": "medium", "target_field": "amount"}
        ]
    },
    "clickstream_botnet_replay": {
        "id": "clickstream_botnet_replay",
        "name": "Clickstream Replay & Payload Corruption",
        "domain": "customer",
        "description": "Rogue web scraper causes massive duplicates and corrupted byte payloads in telemetry stream.",
        "seed": 505,
        "pipeline_target": "customer_analytics_pipeline",
        "node_target": "node_customer_events_raw",
        "faults": [
            {"fault_type": FaultType.DUPLICATE_EVENTS, "severity": "high"},
            {"fault_type": FaultType.CORRUPTED_PAYLOAD, "severity": "medium"}
        ]
    },
    "currency_arbitrage_drift": {
        "id": "currency_arbitrage_drift",
        "name": "Market Shock Distribution Drift",
        "domain": "banking",
        "description": "Macroeconomic shift causes 10x distribution drift in average transaction size.",
        "seed": 606,
        "pipeline_target": "banking_transactions_pipeline",
        "node_target": "node_banking_features",
        "faults": [
            {"fault_type": FaultType.DISTRIBUTION_DRIFT, "severity": "high", "target_field": "amount"}
        ]
    }
}


def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Retrieves scenario definition by ID."""
    return SCENARIO_LIBRARY.get(scenario_id)


def list_scenarios() -> List[Dict[str, Any]]:
    """Returns summary of all available seedable scenarios."""
    return list(SCENARIO_LIBRARY.values())
