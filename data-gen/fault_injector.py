"""
ORBIT Fault Injection Engine
Simulates realistic enterprise pipeline disruptions across 8+ fault categories.
Provides reproducible scenarios, fault metadata, and baseline comparisons.
"""
from typing import List, Dict, Any, Tuple
from enum import Enum
import random
import copy
from datetime import datetime, timedelta, timezone


class FaultType(str, Enum):
    SCHEMA_DRIFT = "schema_drift"
    NULL_SPIKE = "null_spike"
    LATE_ARRIVALS = "late_arrivals"
    DUPLICATE_EVENTS = "duplicate_events"
    DISTRIBUTION_DRIFT = "distribution_drift"
    EXTREME_ANOMALIES = "extreme_anomalies"
    TYPE_MISMATCH = "type_mismatch"
    VOLUME_DROP = "volume_drop"
    CORRUPTED_PAYLOAD = "corrupted_payload"


class FaultInjector:
    """Applies controlled chaos fault injections to enterprise data batches."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def set_seed(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)

    def inject(
        self,
        data: List[Dict[str, Any]],
        fault_type: FaultType,
        severity: str = "high",
        target_field: str = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Injects the requested fault into a copy of the dataset.
        Returns:
            (corrupted_data, fault_metadata)
        """
        if not data:
            return [], {"status": "empty_input"}

        records = [copy.deepcopy(row) for row in data]
        metadata = {
            "fault_type": fault_type.value if isinstance(fault_type, FaultType) else fault_type,
            "severity": severity,
            "original_count": len(data),
            "target_field": target_field,
            "injected_at": datetime.now(timezone.utc).isoformat()
        }

        intensity = 0.6 if severity == "high" else (0.3 if severity == "medium" else 0.15)

        if fault_type == FaultType.SCHEMA_DRIFT:
            # Drops a critical column or renames it across rows
            field_to_rename = target_field or ("amount" if "amount" in records[0] else list(records[0].keys())[2])
            new_field_name = f"{field_to_rename}_legacy_v1"
            for row in records:
                if field_to_rename in row:
                    row[new_field_name] = row.pop(field_to_rename)
            metadata["renamed_field"] = field_to_rename
            metadata["new_field"] = new_field_name
            metadata["description"] = f"Upstream ETL renamed schema field '{field_to_rename}' to '{new_field_name}'"

        elif fault_type == FaultType.NULL_SPIKE:
            # Surge of null values in critical field
            field_to_null = target_field or ("customer_id" if "customer_id" in records[0] else list(records[0].keys())[3])
            affected_count = 0
            for row in records:
                if self.rng.random() < intensity:
                    row[field_to_null] = None
                    affected_count += 1
            metadata["nullified_field"] = field_to_null
            metadata["null_count"] = affected_count
            metadata["null_percentage"] = round((affected_count / len(records)) * 100, 2)
            metadata["description"] = f"Null spike injected: {metadata['null_percentage']}% nulls in mandatory field '{field_to_null}'"

        elif fault_type == FaultType.LATE_ARRIVALS:
            # Shift event timestamps backward by 12 to 72 hours
            time_field = target_field or "timestamp"
            affected_count = 0
            for row in records:
                if self.rng.random() < intensity and time_field in row:
                    try:
                        orig_dt = datetime.fromisoformat(row[time_field])
                    except Exception:
                        orig_dt = datetime.now(timezone.utc)
                    hours_back = self.rng.randint(12, 72)
                    row[time_field] = (orig_dt - timedelta(hours=hours_back)).isoformat()
                    row["_is_late_arriving"] = True
                    affected_count += 1
            metadata["affected_records"] = affected_count
            metadata["lag_hours_range"] = [12, 72]
            metadata["description"] = f"Late arrivals: {affected_count} records delayed by 12-72 hours, breaching watermark SLA"

        elif fault_type == FaultType.DUPLICATE_EVENTS:
            # Duplicate a portion of events
            dupe_candidates = self.rng.sample(records, k=max(1, int(len(records) * intensity)))
            records.extend([copy.deepcopy(cand) for cand in dupe_candidates])
            metadata["duplicates_injected"] = len(dupe_candidates)
            metadata["new_total_count"] = len(records)
            metadata["description"] = f"Duplicate event replay: {len(dupe_candidates)} duplicate events injected"

        elif fault_type == FaultType.DISTRIBUTION_DRIFT:
            # Multiply numerical field by 8x - 15x or skew categorical values
            drift_field = target_field or ("amount" if "amount" in records[0] else "quantity")
            affected_count = 0
            for row in records:
                if drift_field in row and row[drift_field] is not None:
                    multiplier = self.rng.uniform(8.5, 14.0)
                    row[drift_field] = round(float(row[drift_field]) * multiplier, 2)
                    affected_count += 1
            metadata["drift_field"] = drift_field
            metadata["multiplier_range"] = [8.5, 14.0]
            metadata["description"] = f"Distribution drift: '{drift_field}' values shifted upward by 8.5x-14.0x"

        elif fault_type == FaultType.EXTREME_ANOMALIES:
            # Inject extreme outliers / invalid negative or astronomical numbers
            anomaly_field = target_field or ("amount" if "amount" in records[0] else "unit_price")
            affected_indices = self.rng.sample(range(len(records)), k=max(2, int(len(records) * 0.08)))
            for idx in affected_indices:
                extreme_val = self.rng.choice([-99999.00, 48500000.00, -1.00, 99999999.99])
                records[idx][anomaly_field] = extreme_val
                records[idx]["_injected_anomaly"] = True
            metadata["anomaly_field"] = anomaly_field
            metadata["anomaly_count"] = len(affected_indices)
            metadata["description"] = f"Extreme outliers injected: {len(affected_indices)} records with impossible values in '{anomaly_field}'"

        elif fault_type == FaultType.TYPE_MISMATCH:
            # Change numbers to strings with garbage text
            corrupt_field = target_field or ("amount" if "amount" in records[0] else "risk_score")
            affected_count = 0
            for row in records:
                if self.rng.random() < intensity:
                    row[corrupt_field] = self.rng.choice(["NAN_ERR", "NULL_STR", "--", "ERR_DIV_ZERO"])
                    affected_count += 1
            metadata["corrupted_field"] = corrupt_field
            metadata["corrupted_count"] = affected_count
            metadata["description"] = f"Type mismatch: string literals injected into numeric field '{corrupt_field}'"

        elif fault_type == FaultType.VOLUME_DROP:
            # Sudden 80-95% drop in records
            keep_count = max(1, int(len(records) * (1.0 - intensity)))
            records = records[:keep_count]
            metadata["kept_count"] = keep_count
            metadata["drop_percentage"] = round(((metadata["original_count"] - keep_count) / metadata["original_count"]) * 100, 2)
            metadata["description"] = f"Throughput plummet: volume dropped by {metadata['drop_percentage']}%"

        elif fault_type == FaultType.CORRUPTED_PAYLOAD:
            # Truncates or replaces payload
            affected_count = 0
            for row in records:
                if self.rng.random() < intensity:
                    row["corrupted_raw_bytes"] = "0xFF\x00\x1A\xFE[MALFORMED_CHUNK]"
                    affected_count += 1
            metadata["corrupted_count"] = affected_count
            metadata["description"] = f"Corrupted payload: unparseable raw bytes injected into {affected_count} records"

        metadata["result_count"] = len(records)
        return records, metadata
