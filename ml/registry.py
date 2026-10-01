"""
ORBIT MLflow Tracking & Model Registry Integration
Logs model hyperparameters, drift metrics, and registered models.
"""
from typing import Dict, Any, Optional, List
import os
import json
from datetime import datetime, timezone

DEFAULT_REGISTRY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage_registry")


class MLRegistry:
    """Enterprise model registry with MLflow support and fallback local metadata store."""

    def __init__(self, tracking_uri: Optional[str] = None):
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        self.local_registry_path = os.path.join(DEFAULT_REGISTRY_DIR, "models_metadata.json")
        os.makedirs(DEFAULT_REGISTRY_DIR, exist_ok=True)
        if not os.path.exists(self.local_registry_path):
            with open(self.local_registry_path, "w") as f:
                json.dump([], f)

    def log_model_run(
        self,
        model_name: str,
        version: str,
        params: Dict[str, Any],
        metrics: Dict[str, Any],
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Logs experiment run metadata and registers model version."""
        run_record = {
            "run_id": f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "model_name": model_name,
            "version": version,
            "params": params,
            "metrics": metrics,
            "tags": tags or {"stage": "production", "framework": "scikit-learn"},
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "tracking_uri": self.tracking_uri
        }

        # Try logging to MLflow if accessible
        try:
            import mlflow
            mlflow.set_tracking_uri(self.tracking_uri)
            with mlflow.start_run(run_name=f"{model_name}_{version}"):
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                if tags:
                    mlflow.set_tags(tags)
            run_record["mlflow_logged"] = True
        except Exception:
            run_record["mlflow_logged"] = False

        # Always persist to local registry
        try:
            with open(self.local_registry_path, "r") as f:
                runs = json.load(f)
            runs.insert(0, run_record)
            with open(self.local_registry_path, "w") as f:
                json.dump(runs[:50], f, indent=2)
        except Exception:
            pass

        return run_record

    def get_latest_models(self) -> List[Dict[str, Any]]:
        """Retrieves registered production models and metrics."""
        try:
            with open(self.local_registry_path, "r") as f:
                runs = json.load(f)
            return runs
        except Exception:
            return []
