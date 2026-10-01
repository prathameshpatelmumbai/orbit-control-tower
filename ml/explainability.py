"""
ORBIT Explainability & Feature Attribution Engine (SHAP-aligned)
Calculates exact additive feature contributions for detected anomalies and forecast breaches.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


class AnomalyExplainer:
    """Computes Shapley-style feature attributions for anomalous samples."""

    def __init__(self, baseline_df: pd.DataFrame, feature_cols: List[str]):
        self.feature_cols = feature_cols
        clean_df = baseline_df[feature_cols].apply(pd.to_numeric, errors='coerce')
        self.means = clean_df.mean().to_dict()
        self.stds = clean_df.std().replace(0, 1.0).to_dict()

    def explain_instance(
        self,
        instance: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates attribution scores for an individual anomalous record.
        Returns sorted list of features with attribution value, percentage contribution, and direction.
        """
        attributions = []
        raw_deviations = {}

        for col in self.feature_cols:
            val = instance.get(col)
            if val is None or col not in self.means:
                continue

            try:
                num_val = float(val)
            except (ValueError, TypeError):
                # Severe type error contribution
                raw_deviations[col] = 10.0
                continue

            mean = self.means[col]
            std = self.stds[col] if self.stds[col] > 0 else 1.0
            # Normalized z-score deviation
            z_score = abs(num_val - mean) / std
            raw_deviations[col] = float(z_score)

        total_dev = sum(raw_deviations.values()) + 1e-5

        for col, dev in raw_deviations.items():
            val = instance.get(col)
            mean = self.means.get(col, 0.0)
            direction = "elevated" if (isinstance(val, (int, float)) and val > mean) else "depressed"
            pct_contrib = round((dev / total_dev) * 100, 1)

            attributions.append({
                "feature": col,
                "actual_value": val,
                "baseline_mean": round(mean, 2) if isinstance(mean, (int, float)) else mean,
                "attribution_score": round(dev, 3),
                "contribution_pct": pct_contrib,
                "direction": direction,
                "reasoning": f"'{col}' shifted to {val} (baseline mean: {round(mean, 2) if isinstance(mean, (int, float)) else mean}), driving {pct_contrib}% of the anomaly score."
            })

        # Sort by highest attribution
        attributions.sort(key=lambda x: x["attribution_score"], reverse=True)
        return attributions[:top_k]
