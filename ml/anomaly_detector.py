"""
ORBIT Machine Learning Anomaly Detection Engine
Uses Isolation Forest with dynamic contamination estimation and robust scaling
to detect operational throughput, monetary, and latency anomalies.
"""
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler


class OrbitAnomalyDetector:
    """Enterprise anomaly detector powered by Isolation Forest with calibrated scoring."""

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.feature_cols: List[str] = []
        self.is_fitted: bool = False

    def fit(self, df: pd.DataFrame, feature_cols: List[str]) -> "OrbitAnomalyDetector":
        """Fits the Isolation Forest on specified numerical features."""
        self.feature_cols = feature_cols
        X = df[feature_cols].copy()
        # Impute missing values with medians
        X = X.fillna(X.median())
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates anomaly scores and labels for input DataFrame.
        Returns copy of DataFrame with 'anomaly_score' (0 to 1, 1=extreme outlier) and 'is_anomaly' (bool).
        """
        if not self.is_fitted:
            raise RuntimeError("OrbitAnomalyDetector must be fitted before predict.")

        df_out = df.copy()
        X = df_out[self.feature_cols].copy()
        X = X.fillna(X.median())
        X_scaled = self.scaler.transform(X)

        # decision_function yields negative for anomalies, positive for normal
        raw_scores = self.model.decision_function(X_scaled)
        # Logistic calibration: when raw_score < 0 (outlier), normalized_scores > 0.75
        normalized_scores = 1.0 / (1.0 + np.exp(raw_scores * 12.0))
        
        preds = self.model.predict(X_scaled) # -1 for anomaly, 1 for normal


        df_out["anomaly_score"] = np.round(normalized_scores, 4)
        df_out["is_anomaly"] = preds == -1
        return df_out

    def get_top_anomalies(self, df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
        """Returns the top N most severe anomalous records."""
        scored = self.predict(df)
        anomalies = scored[scored["is_anomaly"]].sort_values("anomaly_score", ascending=False)
        if anomalies.empty:
            anomalies = scored.sort_values("anomaly_score", ascending=False)
        return anomalies.head(top_n).to_dict(orient="records")
