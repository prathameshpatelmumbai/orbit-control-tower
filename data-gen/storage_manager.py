"""
ORBIT Storage & Analytical Engine Manager
Integrates DuckDB for zero-latency local analytics, Parquet partitions, and schema isolation.
"""
import os
import duckdb
import pandas as pd
from typing import List, Dict, Any, Optional

DEFAULT_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
DEFAULT_DUCKDB_PATH = os.path.join(DEFAULT_STORAGE_DIR, "orbit_analytics.duckdb")


class StorageManager:
    """Manages analytical persistence in DuckDB and Parquet."""

    def __init__(self, db_path: str = DEFAULT_DUCKDB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)

    def _init_db(self):
        """Initializes tables for all 4 enterprise streams."""
        conn = self._get_connection()
        try:
            # Banking Transactions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bronze_banking_transactions (
                    event_id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    account_id VARCHAR,
                    customer_id VARCHAR,
                    transaction_type VARCHAR,
                    amount DOUBLE,
                    currency VARCHAR,
                    channel VARCHAR,
                    merchant_name VARCHAR,
                    merchant_category VARCHAR,
                    risk_score DOUBLE,
                    is_flagged BOOLEAN,
                    origin_country VARCHAR,
                    status VARCHAR
                )
            """)

            # Retail Orders
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bronze_retail_orders (
                    order_id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    customer_id VARCHAR,
                    warehouse_id VARCHAR,
                    product_category VARCHAR,
                    sku VARCHAR,
                    quantity INTEGER,
                    unit_price DOUBLE,
                    discount_applied DOUBLE,
                    total_amount DOUBLE,
                    payment_method VARCHAR,
                    order_status VARCHAR,
                    inventory_remaining INTEGER
                )
            """)

            # Supply Chain Shipments
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bronze_supply_chain (
                    shipment_id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    order_id VARCHAR,
                    carrier_name VARCHAR,
                    transport_mode VARCHAR,
                    origin_hub VARCHAR,
                    destination_hub VARCHAR,
                    current_latitude DOUBLE,
                    current_longitude DOUBLE,
                    status VARCHAR,
                    estimated_arrival TIMESTAMP,
                    is_cold_chain BOOLEAN,
                    cargo_temp_celsius DOUBLE,
                    transit_delay_hours INTEGER
                )
            """)

            # Customer Events
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bronze_customer_events (
                    event_id VARCHAR PRIMARY KEY,
                    timestamp TIMESTAMP,
                    session_id VARCHAR,
                    customer_id VARCHAR,
                    action VARCHAR,
                    page_url VARCHAR,
                    device_type VARCHAR,
                    ip_address VARCHAR,
                    client_latency_ms INTEGER,
                    status_code INTEGER,
                    payload_bytes INTEGER
                )
            """)
        finally:
            conn.close()

    def save_batch(self, table_name: str, records: List[Dict[str, Any]], mode: str = "append"):
        """Saves a batch of records into DuckDB."""
        if not records:
            return
        df = pd.DataFrame(records)
        conn = self._get_connection()
        try:
            if mode == "overwrite":
                conn.execute(f"DELETE FROM {table_name}")
            conn.register("batch_df", df)
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM batch_df")
        except Exception as e:
            # Fallback for dynamic/corrupted schema during fault injection
            conn.register("corrupted_df", df)
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM corrupted_df")
        finally:
            conn.close()

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Executes analytical SQL query and returns records as list of dictionaries."""
        conn = self._get_connection()
        try:
            if params:
                cursor = conn.execute(sql, params)
            else:
                cursor = conn.execute(sql)
            df = cursor.df()
            return df.to_dict(orient="records")
        finally:
            conn.close()

    def get_table_count(self, table_name: str) -> int:
        """Returns total row count for table."""
        res = self.query(f"SELECT COUNT(*) as cnt FROM {table_name}")
        return res[0]["cnt"] if res else 0
