"""
ORBIT Enterprise Synthetic Data Generator
Orchestrates streams across BFSI, Retail, Supply Chain, and Customer domains.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import random

try:
    from .streams.banking import generate_banking_batch
    from .streams.retail import generate_retail_batch
    from .streams.supply_chain import generate_supply_chain_batch
    from .streams.customer import generate_customer_batch
    from .fault_injector import FaultInjector, FaultType
    from .scenarios import get_scenario, SCENARIO_LIBRARY
    from .storage_manager import StorageManager
except (ImportError, ValueError):
    from streams.banking import generate_banking_batch
    from streams.retail import generate_retail_batch
    from streams.supply_chain import generate_supply_chain_batch
    from streams.customer import generate_customer_batch
    from fault_injector import FaultInjector, FaultType
    from scenarios import get_scenario, SCENARIO_LIBRARY
    from storage_manager import StorageManager



class EnterpriseDataGenerator:
    """Master generator for synthetic enterprise datasets and chaos scenarios."""

    def __init__(self, seed: int = 42, persist_to_duckdb: bool = True):
        self.seed = seed
        self.fault_injector = FaultInjector(seed=seed)
        self.storage = StorageManager() if persist_to_duckdb else None

    def generate_stream(
        self,
        domain: str,
        count: int = 100,
        base_time: Optional[datetime] = None,
        seed: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Generates a batch of healthy enterprise records for the specified domain."""
        current_seed = seed or self.seed
        if domain == "banking":
            return generate_banking_batch(count=count, base_time=base_time, seed=current_seed)
        elif domain == "retail":
            return generate_retail_batch(count=count, base_time=base_time, seed=current_seed)
        elif domain == "supply_chain":
            return generate_supply_chain_batch(count=count, base_time=base_time, seed=current_seed)
        elif domain == "customer":
            return generate_customer_batch(count=count, base_time=base_time, seed=current_seed)
        else:
            raise ValueError(f"Unknown enterprise domain: {domain}. Expected banking, retail, supply_chain, or customer.")

    def generate_all_streams(
        self,
        count_per_stream: int = 250,
        persist: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generates healthy baseline records for all four enterprise domains."""
        now = datetime.now(timezone.utc)
        streams = {
            "banking": self.generate_stream("banking", count=count_per_stream, base_time=now, seed=self.seed + 1),
            "retail": self.generate_stream("retail", count=count_per_stream, base_time=now, seed=self.seed + 2),
            "supply_chain": self.generate_stream("supply_chain", count=count_per_stream, base_time=now, seed=self.seed + 3),
            "customer": self.generate_stream("customer", count=count_per_stream, base_time=now, seed=self.seed + 4),
        }

        if persist and self.storage:
            self.storage.save_batch("bronze_banking_transactions", streams["banking"], mode="overwrite")
            self.storage.save_batch("bronze_retail_orders", streams["retail"], mode="overwrite")
            self.storage.save_batch("bronze_supply_chain", streams["supply_chain"], mode="overwrite")
            self.storage.save_batch("bronze_customer_events", streams["customer"], mode="overwrite")

        return streams

    def inject_chaos(
        self,
        domain: str,
        fault_type: FaultType,
        severity: str = "high",
        target_field: Optional[str] = None,
        count: int = 150,
        persist: bool = True
    ) -> Dict[str, Any]:
        """Generates stream data and injects the specified chaos fault."""
        healthy_batch = self.generate_stream(domain=domain, count=count)
        corrupted_batch, metadata = self.fault_injector.inject(
            data=healthy_batch,
            fault_type=fault_type,
            severity=severity,
            target_field=target_field
        )

        metadata["domain"] = domain
        table_map = {
            "banking": "bronze_banking_transactions",
            "retail": "bronze_retail_orders",
            "supply_chain": "bronze_supply_chain",
            "customer": "bronze_customer_events"
        }

        if persist and self.storage:
            table_name = table_map.get(domain)
            if table_name:
                self.storage.save_batch(table_name, corrupted_batch, mode="overwrite")

        return {
            "metadata": metadata,
            "corrupted_records": corrupted_batch,
            "sample_row": corrupted_batch[0] if corrupted_batch else None
        }

    def execute_scenario(self, scenario_id: str, count: int = 200, persist: bool = True) -> Dict[str, Any]:
        """Executes a pre-defined seedable enterprise scenario."""
        scenario = get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario '{scenario_id}' not found in library.")

        self.fault_injector.set_seed(scenario["seed"])
        domain = scenario["domain"]
        records = self.generate_stream(domain=domain, count=count, seed=scenario["seed"])

        injected_fault_summaries = []
        for fault_spec in scenario["faults"]:
            records, meta = self.fault_injector.inject(
                data=records,
                fault_type=fault_spec["fault_type"],
                severity=fault_spec.get("severity", "high"),
                target_field=fault_spec.get("target_field")
            )
            injected_fault_summaries.append(meta)

        table_map = {
            "banking": "bronze_banking_transactions",
            "retail": "bronze_retail_orders",
            "supply_chain": "bronze_supply_chain",
            "customer": "bronze_customer_events"
        }

        if persist and self.storage:
            table_name = table_map.get(domain)
            if table_name:
                self.storage.save_batch(table_name, records, mode="overwrite")

        return {
            "scenario": scenario,
            "fault_summaries": injected_fault_summaries,
            "record_count": len(records),
            "sample_row": records[0] if records else None
        }


if __name__ == "__main__":
    print("Generating baseline enterprise data streams...")
    generator = EnterpriseDataGenerator(seed=42)
    streams = generator.generate_all_streams(count_per_stream=300)
    for domain, rows in streams.items():
        print(f" -> Generated {len(rows)} records for {domain}")
    print("Baseline streams successfully generated and persisted to DuckDB.")
