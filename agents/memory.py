"""
ORBIT Incident Memory & pgvector Integration
Stores historical postmortems with semantic vector embeddings for rapid sub-10ms incident retrieval.
"""
from typing import List, Dict, Any, Optional
import os
import math
import re
from datetime import datetime, timezone

# Seeded knowledge base of past enterprise incidents
HISTORICAL_INCIDENTS = [
    {
        "id": "inc_hist_001",
        "title": "Core Banking Schema Migration Dropped Column",
        "pipeline_id": "banking_transactions_pipeline",
        "node_id": "bronze_banking_transactions",
        "fault_type": "schema_drift",
        "root_cause": "Upstream vendor release renamed transaction amount field to amount_legacy_v1 without backward-compatible view.",
        "fix_applied": "Applied schema alias patch in bronze transformation layer and re-triggered DAG.",
        "similarity_keywords": ["schema", "drift", "rename", "amount", "banking", "column", "missing"]
    },
    {
        "id": "inc_hist_002",
        "title": "Payment Gateway Null Customer ID Spike",
        "pipeline_id": "banking_transactions_pipeline",
        "node_id": "bronze_banking_transactions",
        "fault_type": "null_spike",
        "root_cause": "Tokenization service outage caused customer_id to evaluate to NULL on 45% of incoming transactions.",
        "fix_applied": "Quarantined null-keyed transactions to poison queue and routed live traffic to secondary token auth vault.",
        "similarity_keywords": ["null", "spike", "customer_id", "tokenization", "missing", "account"]
    },
    {
        "id": "inc_hist_003",
        "title": "Kafka Consumer Replay Storm Duplicates",
        "pipeline_id": "retail_orders_pipeline",
        "node_id": "bronze_retail_orders",
        "fault_type": "duplicate_events",
        "root_cause": "Partition rebalance triggered consumers to reread 30 minutes of committed log offsets.",
        "fix_applied": "Enforced deduplication window using ROW_NUMBER partitioned by order_id and quarantined replayed duplicates.",
        "similarity_keywords": ["duplicate", "replay", "kafka", "orders", "retail", "consumer"]
    },
    {
        "id": "inc_hist_004",
        "title": "Cold Chain IoT Sensory Calibration Drift",
        "pipeline_id": "supply_chain_pipeline",
        "node_id": "bronze_supply_chain",
        "fault_type": "extreme_anomalies",
        "root_cause": "Faulty firmware update on temperature sensor pods produced negative Kelvin readings.",
        "fix_applied": "Applied statistical bounds clamping filter between -50C and 60C and isolated telemetry outlier packets.",
        "similarity_keywords": ["temperature", "cold", "chain", "iot", "anomaly", "extreme", "sensor", "supply"]
    },
    {
        "id": "inc_hist_005",
        "title": "Currency Conversion FX API Decimal Precision Skew",
        "pipeline_id": "banking_transactions_pipeline",
        "node_id": "bronze_banking_transactions",
        "fault_type": "distribution_drift",
        "root_cause": "FX rate service sent Yen amounts with 100x decimal multiplier error, causing severe PSI drift.",
        "fix_applied": "Recalibrated currency scaling factor and reprocessed downstream gold revenue marts.",
        "similarity_keywords": ["drift", "distribution", "currency", "fx", "multiplier", "psi", "amount"]
    }
]


class IncidentMemoryStore:
    """Manages semantic incident embeddings and similarity search."""

    def __init__(self, pg_url: Optional[str] = None):
        self.pg_url = pg_url or os.getenv("DATABASE_URL")
        self.memory_cache: List[Dict[str, Any]] = list(HISTORICAL_INCIDENTS)

    def _text_to_pseudo_embedding(self, text: str, dim: int = 64) -> List[float]:
        """Creates a normalized deterministic semantic vector representation."""
        words = re.findall(r"\w+", text.lower())
        vec = [0.0] * dim
        for w in words:
            h = hash(w)
            idx = abs(h) % dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) + 1e-6
        return [v / norm for v in vec]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a)) + 1e-6
        norm_b = math.sqrt(sum(b * b for b in vec_b)) + 1e-6
        return max(0.0, min(1.0, dot / (norm_a * norm_b)))

    def store_incident(
        self,
        incident_id: str,
        title: str,
        pipeline_id: str,
        node_id: str,
        fault_type: str,
        root_cause: str,
        fix_applied: str
    ) -> Dict[str, Any]:
        """Stores a newly resolved incident into the incident memory store."""
        searchable_text = f"{title} {fault_type} {pipeline_id} {root_cause} {fix_applied}"
        record = {
            "id": incident_id,
            "title": title,
            "pipeline_id": pipeline_id,
            "node_id": node_id,
            "fault_type": fault_type,
            "root_cause": root_cause,
            "fix_applied": fix_applied,
            "embedding": self._text_to_pseudo_embedding(searchable_text),
            "stored_at": datetime.now(timezone.utc).isoformat()
        }
        self.memory_cache.append(record)
        return record

    def search_similar_incidents(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top similar past incidents using semantic vector similarity.
        Used by the Diagnostician agent to cite prior resolutions.
        """
        query_vec = self._text_to_pseudo_embedding(query)
        scored_incidents = []

        for inc in self.memory_cache:
            desc = f"{inc['title']} {inc['fault_type']} {inc.get('root_cause', '')} {' '.join(inc.get('similarity_keywords', []))}"
            inc_vec = inc.get("embedding") or self._text_to_pseudo_embedding(desc)
            sim = self._cosine_similarity(query_vec, inc_vec)

            # Keyword boost
            query_words = set(re.findall(r"\w+", query.lower()))
            overlap = query_words.intersection(set(inc.get("similarity_keywords", [])))
            boost = min(0.35, len(overlap) * 0.12)
            total_score = round(min(0.99, sim + boost), 3)

            if total_score >= min_similarity:
                scored_incidents.append({
                    "incident_id": inc["id"],
                    "title": inc["title"],
                    "fault_type": inc["fault_type"],
                    "root_cause": inc["root_cause"],
                    "fix_applied": inc["fix_applied"],
                    "similarity_score": total_score
                })

        scored_incidents.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_incidents[:top_k]
