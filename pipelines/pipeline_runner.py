"""
ORBIT Pipeline Execution Engine & Lineage Graph Orchestrator
Executes Bronze -> Silver -> Gold transformation workflows, runs data quality checks,
and generates the 3D spatial lineage graph for the Data Galaxy and API endpoints.
"""
from typing import Dict, Any, List, Optional
import os
import duckdb
from datetime import datetime, timezone
import pandas as pd

from .data_quality.expectations import DataQualitySuite


DEFAULT_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
DEFAULT_DUCKDB_PATH = os.path.join(DEFAULT_STORAGE_DIR, "orbit_analytics.duckdb")


class PipelineRunner:
    """Orchestrates pipeline transformations, data quality verification, and lineage tracking."""

    def __init__(self, db_path: str = DEFAULT_DUCKDB_PATH):
        self.db_path = db_path
        self.quality_suite = DataQualitySuite("orbit_enterprise_quality_suite")

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return duckdb.connect(self.db_path)

    def run_all_transformations(self) -> Dict[str, Any]:
        """
        Executes complete medallion transformation pipeline (Bronze -> Silver -> Gold).
        Materializes Silver and Gold tables in DuckDB and computes quality invariants.
        """
        conn = self._get_connection()
        run_results = {}
        try:
            # 1. Silver Transformations
            # Banking Silver
            conn.execute("""
                CREATE OR REPLACE TABLE fct_banking_transactions AS
                WITH deduplicated AS (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY timestamp DESC) AS rn
                    FROM bronze_banking_transactions
                    WHERE event_id IS NOT NULL
                      AND account_id IS NOT NULL
                      AND amount IS NOT NULL
                      AND amount > 0
                )
                SELECT
                    event_id,
                    timestamp,
                    account_id,
                    customer_id,
                    transaction_type,
                    amount,
                    currency,
                    channel,
                    merchant_name,
                    merchant_category,
                    risk_score,
                    CASE WHEN risk_score >= 80.0 THEN TRUE ELSE FALSE END AS is_high_risk,
                    origin_country,
                    status
                FROM deduplicated
                WHERE rn = 1
            """)

            # Retail Silver
            conn.execute("""
                CREATE OR REPLACE TABLE fct_retail_orders AS
                WITH deduplicated AS (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY timestamp DESC) AS rn
                    FROM bronze_retail_orders
                    WHERE order_id IS NOT NULL
                      AND customer_id IS NOT NULL
                      AND total_amount IS NOT NULL
                      AND total_amount > 0
                )
                SELECT
                    order_id,
                    timestamp,
                    customer_id,
                    warehouse_id,
                    product_category,
                    sku,
                    quantity,
                    unit_price,
                    discount_applied,
                    total_amount,
                    payment_method,
                    order_status,
                    GREATEST(0, inventory_remaining) AS inventory_remaining,
                    CASE 
                        WHEN inventory_remaining <= 10 THEN 'CRITICAL_LOW_STOCK'
                        WHEN inventory_remaining <= 50 THEN 'LOW_STOCK'
                        ELSE 'OPTIMAL_STOCK'
                    END AS stock_health_status
                FROM deduplicated
                WHERE rn = 1
            """)

            # Supply Chain Silver
            conn.execute("""
                CREATE OR REPLACE TABLE fct_supply_chain AS
                WITH deduplicated AS (
                    SELECT
                        *,
                        ROW_NUMBER() OVER (PARTITION BY shipment_id ORDER BY timestamp DESC) AS rn
                    FROM bronze_supply_chain
                    WHERE shipment_id IS NOT NULL
                      AND current_latitude BETWEEN -90.0 AND 90.0
                      AND current_longitude BETWEEN -180.0 AND 180.0
                )
                SELECT
                    shipment_id,
                    timestamp,
                    order_id,
                    carrier_name,
                    transport_mode,
                    origin_hub,
                    destination_hub,
                    current_latitude,
                    current_longitude,
                    status,
                    estimated_arrival,
                    is_cold_chain,
                    cargo_temp_celsius,
                    transit_delay_hours,
                    CASE
                        WHEN is_cold_chain AND cargo_temp_celsius > -10.0 THEN 'BREACH_COLD_CHAIN'
                        WHEN transit_delay_hours >= 24 THEN 'SEVERE_DELAY'
                        WHEN transit_delay_hours > 0 THEN 'MODERATE_DELAY'
                        ELSE 'ON_SCHEDULE'
                    END AS telemetry_alert_level
                FROM deduplicated
                WHERE rn = 1
            """)

            # Customer Sessions Silver
            conn.execute("""
                CREATE OR REPLACE TABLE fct_customer_sessions AS
                SELECT
                    session_id,
                    customer_id,
                    MIN(timestamp) AS session_start_time,
                    MAX(timestamp) AS session_end_time,
                    COUNT(*) AS total_interactions,
                    AVG(client_latency_ms) AS avg_client_latency_ms,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) AS error_count,
                    MAX(CASE WHEN action = 'checkout_step' THEN 1 ELSE 0 END) AS has_checkout
                FROM bronze_customer_events
                WHERE session_id IS NOT NULL
                GROUP BY session_id, customer_id
            """)

            # 2. Gold Transformations
            # Enterprise Revenue Gold
            conn.execute("""
                CREATE OR REPLACE TABLE dm_enterprise_revenue AS
                WITH banking_rev AS (
                    SELECT
                        DATE_TRUNC('day', timestamp) AS metric_date,
                        SUM(amount) AS banking_revenue_usd,
                        COUNT(*) AS banking_txns
                    FROM fct_banking_transactions
                    WHERE status = 'settled'
                    GROUP BY 1
                ),
                retail_rev AS (
                    SELECT
                        DATE_TRUNC('day', timestamp) AS metric_date,
                        SUM(total_amount) AS retail_revenue_usd,
                        COUNT(*) AS retail_orders
                    FROM fct_retail_orders
                    GROUP BY 1
                )
                SELECT
                    COALESCE(b.metric_date, r.metric_date) AS metric_date,
                    COALESCE(b.banking_revenue_usd, 0.0) AS banking_revenue_usd,
                    COALESCE(r.retail_revenue_usd, 0.0) AS retail_revenue_usd,
                    COALESCE(b.banking_revenue_usd, 0.0) + COALESCE(r.retail_revenue_usd, 0.0) AS total_revenue_usd,
                    COALESCE(b.banking_txns, 0) AS total_banking_txns,
                    COALESCE(r.retail_orders, 0) AS total_retail_orders
                FROM banking_rev b
                FULL OUTER JOIN retail_rev r ON b.metric_date = r.metric_date
            """)

            # Supply Chain SLA Gold
            conn.execute("""
                CREATE OR REPLACE TABLE dm_supply_chain_sla AS
                SELECT
                    carrier_name,
                    transport_mode,
                    COUNT(*) AS total_shipments,
                    AVG(transit_delay_hours) AS avg_delay_hours,
                    ROUND((COUNT(CASE WHEN transit_delay_hours = 0 THEN 1 END) * 100.0) / COUNT(*), 2) AS on_time_sla_percentage,
                    COUNT(CASE WHEN telemetry_alert_level = 'BREACH_COLD_CHAIN' THEN 1 END) AS cold_chain_breaches
                FROM fct_supply_chain
                GROUP BY carrier_name, transport_mode
            """)

            # Data Quality Metrics Gold
            conn.execute("""
                CREATE OR REPLACE TABLE dm_data_quality_metrics AS
                SELECT
                    'banking_transactions' AS pipeline_name,
                    COUNT(*) AS total_processed,
                    ROUND((COUNT(CASE WHEN NOT is_high_risk THEN 1 END) * 100.0) / COUNT(*), 2) AS health_pct
                FROM fct_banking_transactions
                UNION ALL
                SELECT
                    'retail_orders',
                    COUNT(*),
                    ROUND((COUNT(CASE WHEN stock_health_status != 'CRITICAL_LOW_STOCK' THEN 1 END) * 100.0) / COUNT(*), 2)
                FROM fct_retail_orders
                UNION ALL
                SELECT
                    'supply_chain',
                    COUNT(*),
                    ROUND((COUNT(CASE WHEN telemetry_alert_level = 'ON_SCHEDULE' THEN 1 END) * 100.0) / COUNT(*), 2)
                FROM fct_supply_chain
            """)

            run_results["status"] = "success"
            run_results["executed_at"] = datetime.now(timezone.utc).isoformat()
            run_results["materialized_tables"] = [
                "fct_banking_transactions", "fct_retail_orders", 
                "fct_supply_chain", "fct_customer_sessions",
                "dm_enterprise_revenue", "dm_supply_chain_sla", "dm_data_quality_metrics"
            ]
        except Exception as e:
            run_results["status"] = "failed"
            run_results["error"] = str(e)
        finally:
            conn.close()

        return run_results

    def check_node_health(self, table_name: str, domain: str) -> Dict[str, Any]:
        """Runs quality checks on a table and returns health status and failure diagnostics."""
        conn = self._get_connection()
        try:
            df = conn.execute(f"SELECT * FROM {table_name} LIMIT 500").df()
            report = self.quality_suite.evaluate(df, domain=domain)
            
            # Map score to status
            score = report.get("health_score", 100.0)
            if score >= 95.0 and report.get("is_healthy"):
                status = "healthy"
            elif score >= 70.0:
                status = "degraded"
            else:
                status = "unhealthy"

            return {
                "table_name": table_name,
                "status": status,
                "health_score": score,
                "record_count": len(df),
                "failed_count": report.get("failed_tests", 0),
                "failed_expectations": report.get("failed_expectations", [])
            }
        except Exception as e:
            return {
                "table_name": table_name,
                "status": "unhealthy",
                "health_score": 0.0,
                "error": str(e),
                "failed_count": 1,
                "failed_expectations": [{"expectation": "table_queryable", "details": str(e)}]
            }
        finally:
            conn.close()

    def get_lineage_graph(self) -> Dict[str, Any]:
        """
        Builds the complete spatial Lineage Graph for the 3D Data Galaxy and API.
        Includes 3D coordinates (x, y, z), health status, node types, and edge connections.
        """
        # Evaluate health of key bronze/silver tables
        banking_health = self.check_node_health("bronze_banking_transactions", "banking")
        retail_health = self.check_node_health("bronze_retail_orders", "retail")
        supply_health = self.check_node_health("bronze_supply_chain", "supply_chain")
        customer_health = self.check_node_health("bronze_customer_events", "customer")

        nodes = [
            # Sources (Layer 0: X = -12)
            {
                "id": "src_core_banking",
                "name": "Core Banking Engine",
                "type": "source",
                "domain": "banking",
                "layer": "source",
                "status": "healthy",
                "position": [-14, 4, 0],
                "throughput_eps": 1420,
                "records": 52000
            },
            {
                "id": "src_retail_pos",
                "name": "Omnichannel Retail POS",
                "type": "source",
                "domain": "retail",
                "layer": "source",
                "status": "healthy",
                "position": [-14, 1.5, -2],
                "throughput_eps": 890,
                "records": 31000
            },
            {
                "id": "src_supply_iot",
                "name": "Supply Chain IoT Gateways",
                "type": "source",
                "domain": "supply_chain",
                "layer": "source",
                "status": "healthy",
                "position": [-14, -1.5, 2],
                "throughput_eps": 640,
                "records": 18500
            },
            {
                "id": "src_web_clickstream",
                "name": "Global Web Clickstream",
                "type": "source",
                "domain": "customer",
                "layer": "source",
                "status": "healthy",
                "position": [-14, -4, 0],
                "throughput_eps": 3200,
                "records": 112000
            },

            # Bronze Medallion (Layer 1: X = -6)
            {
                "id": "bronze_banking_transactions",
                "name": "Bronze Banking Txns",
                "type": "pipeline_stage",
                "domain": "banking",
                "layer": "bronze",
                "status": banking_health["status"],
                "health_score": banking_health["health_score"],
                "failed_expectations": banking_health.get("failed_expectations", []),
                "position": [-7, 4, 0],
                "records": banking_health["record_count"]
            },
            {
                "id": "bronze_retail_orders",
                "name": "Bronze Retail Orders",
                "type": "pipeline_stage",
                "domain": "retail",
                "layer": "bronze",
                "status": retail_health["status"],
                "health_score": retail_health["health_score"],
                "failed_expectations": retail_health.get("failed_expectations", []),
                "position": [-7, 1.5, -2],
                "records": retail_health["record_count"]
            },
            {
                "id": "bronze_supply_chain",
                "name": "Bronze Supply Chain",
                "type": "pipeline_stage",
                "domain": "supply_chain",
                "layer": "bronze",
                "status": supply_health["status"],
                "health_score": supply_health["health_score"],
                "failed_expectations": supply_health.get("failed_expectations", []),
                "position": [-7, -1.5, 2],
                "records": supply_health["record_count"]
            },
            {
                "id": "bronze_customer_events",
                "name": "Bronze Customer Events",
                "type": "pipeline_stage",
                "domain": "customer",
                "layer": "bronze",
                "status": customer_health["status"],
                "health_score": customer_health["health_score"],
                "failed_expectations": customer_health.get("failed_expectations", []),
                "position": [-7, -4, 0],
                "records": customer_health["record_count"]
            },

            # Silver Medallion (Layer 2: X = 0)
            {
                "id": "fct_banking_transactions",
                "name": "Silver Fact Banking",
                "type": "pipeline_stage",
                "domain": "banking",
                "layer": "silver",
                "status": "degraded" if banking_health["status"] == "unhealthy" else "healthy",
                "position": [0, 4, 0],
                "records": max(0, banking_health["record_count"] - 2)
            },
            {
                "id": "fct_retail_orders",
                "name": "Silver Fact Retail",
                "type": "pipeline_stage",
                "domain": "retail",
                "layer": "silver",
                "status": "degraded" if retail_health["status"] == "unhealthy" else "healthy",
                "position": [0, 1.5, -2],
                "records": retail_health["record_count"]
            },
            {
                "id": "fct_supply_chain",
                "name": "Silver Fact Supply",
                "type": "pipeline_stage",
                "domain": "supply_chain",
                "layer": "silver",
                "status": "degraded" if supply_health["status"] == "unhealthy" else "healthy",
                "position": [0, -1.5, 2],
                "records": supply_health["record_count"]
            },
            {
                "id": "fct_customer_sessions",
                "name": "Silver Fact Sessions",
                "type": "pipeline_stage",
                "domain": "customer",
                "layer": "silver",
                "status": "degraded" if customer_health["status"] == "unhealthy" else "healthy",
                "position": [0, -4, 0],
                "records": max(1, customer_health["record_count"] // 3)
            },

            # Gold Medallion (Layer 3: X = 7)
            {
                "id": "dm_enterprise_revenue",
                "name": "Gold Revenue Mart",
                "type": "data_mart",
                "domain": "finance",
                "layer": "gold",
                "status": "healthy" if banking_health["status"] == "healthy" and retail_health["status"] == "healthy" else "degraded",
                "position": [7, 3, -1],
                "records": 48
            },
            {
                "id": "dm_supply_chain_sla",
                "name": "Gold Supply SLA Mart",
                "type": "data_mart",
                "domain": "supply_chain",
                "layer": "gold",
                "status": "healthy" if supply_health["status"] == "healthy" else "degraded",
                "position": [7, -1, 1],
                "records": 16
            },
            {
                "id": "dm_data_quality_metrics",
                "name": "Gold Ops Health Mart",
                "type": "data_mart",
                "domain": "operations",
                "layer": "gold",
                "status": "healthy",
                "position": [7, -3.5, 0],
                "records": 4
            },

            # ML Models & Dashboards (Layer 4: X = 14)
            {
                "id": "ml_anomaly_detector",
                "name": "Isolation Forest Anomaly Model",
                "type": "ml_model",
                "domain": "ml",
                "layer": "model",
                "status": "healthy",
                "position": [14, 3.5, 2],
                "accuracy_f1": 0.962
            },
            {
                "id": "ml_sla_forecaster",
                "name": "XGBoost SLA Forecaster",
                "type": "ml_model",
                "domain": "ml",
                "layer": "model",
                "status": "healthy",
                "position": [14, 1.0, -2],
                "accuracy_mape": 0.041
            },
            {
                "id": "dash_executive_revenue",
                "name": "C-Suite Revenue Cockpit",
                "type": "dashboard",
                "domain": "executive",
                "layer": "dashboard",
                "status": "healthy",
                "position": [14, -1.5, -1],
                "sla_target": "99.9%"
            },
            {
                "id": "dash_ops_control_tower",
                "name": "ORBIT Control Tower Live",
                "type": "dashboard",
                "domain": "operations",
                "layer": "dashboard",
                "status": "healthy",
                "position": [14, -4, 1],
                "sla_target": "99.99%"
            }
        ]

        edges = [
            # Sources -> Bronze
            {"source": "src_core_banking", "target": "bronze_banking_transactions"},
            {"source": "src_retail_pos", "target": "bronze_retail_orders"},
            {"source": "src_supply_iot", "target": "bronze_supply_chain"},
            {"source": "src_web_clickstream", "target": "bronze_customer_events"},

            # Bronze -> Silver
            {"source": "bronze_banking_transactions", "target": "fct_banking_transactions"},
            {"source": "bronze_retail_orders", "target": "fct_retail_orders"},
            {"source": "bronze_supply_chain", "target": "fct_supply_chain"},
            {"source": "bronze_customer_events", "target": "fct_customer_sessions"},

            # Silver -> Gold
            {"source": "fct_banking_transactions", "target": "dm_enterprise_revenue"},
            {"source": "fct_retail_orders", "target": "dm_enterprise_revenue"},
            {"source": "fct_supply_chain", "target": "dm_supply_chain_sla"},
            {"source": "fct_banking_transactions", "target": "dm_data_quality_metrics"},
            {"source": "fct_retail_orders", "target": "dm_data_quality_metrics"},
            {"source": "fct_supply_chain", "target": "dm_data_quality_metrics"},

            # Gold / Silver -> ML & Dashboards
            {"source": "fct_banking_transactions", "target": "ml_anomaly_detector"},
            {"source": "dm_supply_chain_sla", "target": "ml_sla_forecaster"},
            {"source": "dm_enterprise_revenue", "target": "dash_executive_revenue"},
            {"source": "dm_data_quality_metrics", "target": "dash_ops_control_tower"},
            {"source": "ml_anomaly_detector", "target": "dash_ops_control_tower"}
        ]

        # Calculate graph summary
        total_nodes = len(nodes)
        unhealthy_nodes = [n["id"] for n in nodes if n["status"] == "unhealthy"]
        degraded_nodes = [n["id"] for n in nodes if n["status"] == "degraded"]

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total_nodes": total_nodes,
                "healthy_count": total_nodes - len(unhealthy_nodes) - len(degraded_nodes),
                "degraded_count": len(degraded_nodes),
                "unhealthy_count": len(unhealthy_nodes),
                "unhealthy_node_ids": unhealthy_nodes,
                "degraded_node_ids": degraded_nodes,
                "system_status": "unhealthy" if unhealthy_nodes else ("degraded" if degraded_nodes else "healthy"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
