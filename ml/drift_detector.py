"""
ORBIT Statistical Distribution Drift Detection Engine
Computes Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests
to detect silent data drift between baseline training sets and live production windows.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


class DriftDetector:
    """Calculates PSI and KS statistics across numerical and categorical features."""

    def __init__(self, psi_threshold_warning: float = 0.1, psi_threshold_critical: float = 0.25):
        self.psi_threshold_warning = psi_threshold_warning
        self.psi_threshold_critical = psi_threshold_critical

    def calculate_psi(
        self,
        baseline: np.ndarray,
        target: np.ndarray,
        num_buckets: int = 10
    ) -> float:
        """
        Calculates Population Stability Index between baseline and target samples.
        PSI < 0.1: No change
        0.1 <= PSI < 0.25: Moderate drift
        PSI >= 0.25: Significant distribution shift
        """
        baseline = baseline[~np.isnan(baseline)]
        target = target[~np.isnan(target)]

        if len(baseline) == 0 or len(target) == 0:
            return 0.0

        # Create quantile-based bins using baseline
        quantiles = np.linspace(0, 100, num_buckets + 1)
        bins = np.percentile(baseline, quantiles)
        # Ensure bin edges are strictly monotonic and outer bins capture entire distribution
        for i in range(1, len(bins)):
            if bins[i] <= bins[i - 1]:
                bins[i] = bins[i - 1] + 1e-5
        bins[0] = -np.inf
        bins[-1] = np.inf


        # Count frequencies
        base_counts, _ = np.histogram(baseline, bins=bins)
        target_counts, _ = np.histogram(target, bins=bins)

        # Convert to percentages with epsilon smoothing to prevent div by zero
        eps = 1e-4
        base_pct = (base_counts / len(baseline)) + eps
        target_pct = (target_counts / len(target)) + eps

        # Re-normalize
        base_pct /= base_pct.sum()
        target_pct /= target_pct.sum()

        psi_value = np.sum((target_pct - base_pct) * np.log(target_pct / base_pct))
        return float(np.round(max(0.0, psi_value), 4))

    def calculate_ks_test(self, baseline: np.ndarray, target: np.ndarray) -> Dict[str, float]:
        """Performs two-sample Kolmogorov-Smirnov test."""
        baseline = baseline[~np.isnan(baseline)]
        target = target[~np.isnan(target)]
        if len(baseline) == 0 or len(target) == 0:
            return {"statistic": 0.0, "p_value": 1.0}

        res = stats.ks_2samp(baseline, target)
        return {
            "statistic": float(np.round(res.statistic, 4)),
            "p_value": float(np.round(res.pvalue, 6))
        }

    def evaluate_feature_drift(
        self,
        baseline_df: pd.DataFrame,
        current_df: pd.DataFrame,
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates drift metrics for a list of features.
        Returns a comprehensive drift report with per-feature PSI, KS, and overall drift alert.
        """
        feature_results = {}
        drift_detected_count = 0
        max_psi = 0.0

        for col in feature_cols:
            if col not in baseline_df.columns or col not in current_df.columns:
                continue

            base_vals = pd.to_numeric(baseline_df[col], errors='coerce').dropna().values
            curr_vals = pd.to_numeric(current_df[col], errors='coerce').dropna().values

            if len(base_vals) < 5 or len(curr_vals) < 5:
                continue

            psi = self.calculate_psi(base_vals, curr_vals)
            ks = self.calculate_ks_test(base_vals, curr_vals)

            is_drifting = psi >= self.psi_threshold_warning or ks["p_value"] < 0.01
            severity = "none"
            if psi >= self.psi_threshold_critical or ks["statistic"] > 0.4:
                severity = "critical"
            elif psi >= self.psi_threshold_warning:
                severity = "warning"

            if is_drifting:
                drift_detected_count += 1
            if psi > max_psi:
                max_psi = psi

            feature_results[col] = {
                "psi": psi,
                "ks_statistic": ks["statistic"],
                "ks_p_value": ks["p_value"],
                "is_drifting": is_drifting,
                "severity": severity,
                "baseline_mean": float(np.round(np.mean(base_vals), 2)),
                "current_mean": float(np.round(np.mean(curr_vals), 2)),
                "mean_shift_pct": float(np.round(((np.mean(curr_vals) - np.mean(base_vals)) / (np.mean(base_vals) + 1e-5)) * 100, 2))
            }

        overall_status = "healthy"
        if any(f["severity"] == "critical" for f in feature_results.values()):
            overall_status = "critical_drift"
        elif drift_detected_count > 0:
            overall_status = "warning_drift"

        return {
            "overall_status": overall_status,
            "features_evaluated": len(feature_results),
            "drifting_features_count": drift_detected_count,
            "max_psi": max_psi,
            "feature_metrics": feature_results
        }
