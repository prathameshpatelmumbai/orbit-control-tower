"""
ORBIT Predictive SLA Forecaster & What-If Simulator
Forecasts latency, throughput, and SLA breach probabilities with confidence bands.
Simulates What-If operational scenarios under varying data volumes, fault rates, and latency budgets.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd


class SLAPredictiveForecaster:
    """Predicts future operational metrics and evaluates What-If risk simulations."""

    def __init__(self, base_sla_latency_ms: float = 250.0):
        self.base_sla_latency_ms = base_sla_latency_ms

    def forecast_metric(
        self,
        historical_values: List[float],
        horizon_steps: int = 12,
        noise_std: float = 5.0
    ) -> List[Dict[str, Any]]:
        """
        Generates forward-looking forecast with 95% confidence bands.
        """
        if not historical_values:
            historical_values = [120.0, 125.0, 130.0, 128.0, 135.0, 140.0]

        series = np.array(historical_values)
        trend = (series[-1] - series[0]) / len(series) if len(series) > 1 else 1.0
        last_val = series[-1]

        forecast = []
        for i in range(1, horizon_steps + 1):
            # Diurnal/seasonal curve + linear trend
            seasonal = np.sin(i * np.pi / 6.0) * 12.0
            predicted_mean = float(round(last_val + (trend * i) + seasonal, 2))
            uncertainty = float(round(noise_std * np.sqrt(i) * 1.96, 2))

            upper_bound = float(round(predicted_mean + uncertainty, 2))
            lower_bound = float(round(max(0.0, predicted_mean - uncertainty), 2))
            breach_prob = float(round(min(1.0, max(0.0, (upper_bound - self.base_sla_latency_ms) / 100.0)), 3)) if upper_bound > self.base_sla_latency_ms else 0.0

            forecast.append({
                "step": f"T+{i}h",
                "predicted": predicted_mean,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "sla_target": self.base_sla_latency_ms,
                "breach_probability": breach_prob
            })

        return forecast

    def simulate_what_if(
        self,
        data_volume_multiplier: float = 1.0,
        fault_rate_pct: float = 2.0,
        latency_budget_ms: float = 250.0
    ) -> Dict[str, Any]:
        """
        Simulates What-If operational outcomes based on interactive parameters:
        - data_volume_multiplier: 0.5x to 5.0x
        - fault_rate_pct: 0% to 25%
        - latency_budget_ms: 100ms to 1000ms
        """
        # Baseline calculations
        base_eps = 4500
        simulated_eps = int(base_eps * data_volume_multiplier)

        # Baseline latency responds non-linearly to throughput and fault retries
        queue_factor = max(1.0, (data_volume_multiplier ** 1.6))
        fault_overhead_ms = fault_rate_pct * 14.5
        projected_latency_ms = round(85.0 * queue_factor + fault_overhead_ms, 1)

        # SLA breach percentage
        if projected_latency_ms <= latency_budget_ms:
            sla_breach_rate = round(max(0.1, (projected_latency_ms / latency_budget_ms) * 3.5), 2)
        else:
            excess = projected_latency_ms - latency_budget_ms
            sla_breach_rate = round(min(99.9, 15.0 + (excess / 10.0)), 2)

        # Projected hourly downtime cost ($2,400/hr baseline * breach percentage)
        hourly_risk_cost_usd = round((sla_breach_rate / 100.0) * 12500.0 * data_volume_multiplier, 2)

        # MTTR projection (minutes)
        projected_mttr_min = round(4.2 + (fault_rate_pct * 0.6) + (data_volume_multiplier * 0.8), 1)

        # Generate comparative curves (baseline vs simulated)
        steps = ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"]
        comparative_curve = []
        for idx, t in enumerate(steps):
            hour_factor = [0.6, 0.7, 1.2, 1.4, 1.3, 0.9][idx]
            base_curve_val = round(110.0 * hour_factor, 1)
            sim_curve_val = round(projected_latency_ms * hour_factor, 1)
            comparative_curve.append({
                "time": t,
                "baseline_latency_ms": base_curve_val,
                "simulated_latency_ms": sim_curve_val,
                "budget_limit": latency_budget_ms,
                "is_breach": sim_curve_val > latency_budget_ms
            })

        return {
            "inputs": {
                "data_volume_multiplier": data_volume_multiplier,
                "fault_rate_pct": fault_rate_pct,
                "latency_budget_ms": latency_budget_ms
            },
            "metrics": {
                "throughput_eps": simulated_eps,
                "projected_latency_ms": projected_latency_ms,
                "sla_breach_rate_pct": sla_breach_rate,
                "sla_status": "EXCELLENT" if sla_breach_rate < 2.0 else ("AT_RISK" if sla_breach_rate < 15.0 else "BREACHED"),
                "hourly_risk_cost_usd": hourly_risk_cost_usd,
                "projected_mttr_min": projected_mttr_min
            },
            "comparative_curve": comparative_curve
        }
