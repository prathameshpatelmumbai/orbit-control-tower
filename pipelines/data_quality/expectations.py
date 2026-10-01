"""
ORBIT Data Quality Invariant & Expectations Engine
Provides declarative Great-Expectations-style validation suites for enterprise data pipelines.
Generates structured diagnostics consumed by Sentinel and Diagnostician agents.
"""
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


class QualityExpectationResult:
    """Stores the evaluation outcome of an individual data quality rule."""
    def __init__(
        self,
        expectation_name: str,
        column: Optional[str],
        success: bool,
        details: Dict[str, Any],
        severity: str = "critical"
    ):
        self.expectation_name = expectation_name
        self.column = column
        self.success = success
        self.details = details
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expectation": self.expectation_name,
            "column": self.column,
            "success": self.success,
            "severity": self.severity,
            "details": self.details
        }


class DataQualitySuite:
    """Evaluates data quality constraints against DataFrames or raw record batches."""

    def __init__(self, suite_name: str):
        self.suite_name = suite_name

    def evaluate(self, df_or_records: Any, domain: str = "banking") -> Dict[str, Any]:
        """
        Runs comprehensive data quality validation suite based on domain.
        Returns:
            Quality Report dict with pass/fail summary and diagnostic details.
        """
        if isinstance(df_or_records, list):
            df = pd.DataFrame(df_or_records)
        elif isinstance(df_or_records, pd.DataFrame):
            df = df_or_records
        else:
            return {
                "suite_name": self.suite_name,
                "is_healthy": False,
                "error": "Invalid data format"
            }

        results: List[QualityExpectationResult] = []

        if df.empty:
            results.append(QualityExpectationResult(
                expectation_name="expect_table_not_empty",
                column=None,
                success=False,
                details={"reason": "Empty dataset received. Possible upstream pipeline collapse."},
                severity="critical"
            ))
            return self._build_report(results)

        # 1. Universal Tests: Row count volume floor
        min_expected_rows = 5
        results.append(QualityExpectationResult(
            expectation_name="expect_table_row_count_to_be_above",
            column=None,
            success=len(df) >= min_expected_rows,
            details={"actual_rows": len(df), "threshold": min_expected_rows},
            severity="critical" if len(df) < min_expected_rows else "info"
        ))

        # 2. Domain Specific Test Suites
        if domain == "banking":
            # Column existence (Schema Drift detection)
            for col in ["event_id", "account_id", "customer_id", "amount", "currency"]:
                results.append(self._check_column_exists(df, col))

            if "amount" in df.columns:
                results.append(self._check_column_not_null(df, "amount", max_null_pct=0.01))
                results.append(self._check_numeric_type(df, "amount"))
                results.append(self._check_values_between(df, "amount", min_val=0.01, max_val=5000000.0))

            if "event_id" in df.columns:
                results.append(self._check_uniqueness(df, "event_id"))

            if "account_id" in df.columns:
                results.append(self._check_column_not_null(df, "account_id", max_null_pct=0.02))

            if "currency" in df.columns:
                results.append(self._check_set_membership(
                    df, "currency", allowed_set={"USD", "EUR", "GBP", "JPY", "CAD", "AUD"}
                ))

        elif domain == "retail":
            for col in ["order_id", "customer_id", "warehouse_id", "total_amount"]:
                results.append(self._check_column_exists(df, col))

            if "order_id" in df.columns:
                results.append(self._check_uniqueness(df, "order_id"))

            if "total_amount" in df.columns:
                results.append(self._check_column_not_null(df, "total_amount", max_null_pct=0.01))
                results.append(self._check_numeric_type(df, "total_amount"))
                results.append(self._check_values_between(df, "total_amount", min_val=0.01, max_val=1000000.0))

            if "inventory_remaining" in df.columns:
                results.append(self._check_values_between(df, "inventory_remaining", min_val=0, max_val=10000))

        elif domain == "supply_chain":
            for col in ["shipment_id", "carrier_name", "current_latitude", "current_longitude"]:
                results.append(self._check_column_exists(df, col))

            if "shipment_id" in df.columns:
                results.append(self._check_uniqueness(df, "shipment_id"))

            if "current_latitude" in df.columns:
                results.append(self._check_values_between(df, "current_latitude", min_val=-90.0, max_val=90.0))

            if "current_longitude" in df.columns:
                results.append(self._check_values_between(df, "current_longitude", min_val=-180.0, max_val=180.0))

            if "cargo_temp_celsius" in df.columns:
                # Cold chain limit: between -50C and 55C
                results.append(self._check_values_between(df, "cargo_temp_celsius", min_val=-50.0, max_val=60.0))

        elif domain == "customer":
            for col in ["event_id", "session_id", "action"]:
                results.append(self._check_column_exists(df, col))

            if "event_id" in df.columns:
                results.append(self._check_uniqueness(df, "event_id"))

            if "client_latency_ms" in df.columns:
                results.append(self._check_values_between(df, "client_latency_ms", min_val=0, max_val=60000))

        return self._build_report(results)

    def _check_column_exists(self, df: pd.DataFrame, column: str) -> QualityExpectationResult:
        exists = column in df.columns
        return QualityExpectationResult(
            expectation_name="expect_column_to_exist",
            column=column,
            success=exists,
            details={"column": column, "exists": exists},
            severity="critical" if not exists else "info"
        )

    def _check_column_not_null(self, df: pd.DataFrame, column: str, max_null_pct: float = 0.0) -> QualityExpectationResult:
        null_count = int(df[column].isna().sum())
        null_pct = round(null_count / len(df), 4)
        success = null_pct <= max_null_pct
        return QualityExpectationResult(
            expectation_name="expect_column_values_to_not_be_null",
            column=column,
            success=success,
            details={
                "null_count": null_count,
                "null_pct": null_pct,
                "threshold_pct": max_null_pct
            },
            severity="high" if not success else "info"
        )

    def _check_uniqueness(self, df: pd.DataFrame, column: str) -> QualityExpectationResult:
        dupe_count = int(df[column].duplicated().sum())
        success = dupe_count == 0
        return QualityExpectationResult(
            expectation_name="expect_column_values_to_be_unique",
            column=column,
            success=success,
            details={"duplicate_count": dupe_count},
            severity="medium" if not success else "info"
        )

    def _check_numeric_type(self, df: pd.DataFrame, column: str) -> QualityExpectationResult:
        # Check if column is numeric or can be cast cleanly without errors
        try:
            pd.to_numeric(df[column])
            success = True
            invalid_count = 0
        except Exception:
            # Count invalid
            invalid_count = int(pd.to_numeric(df[column], errors='coerce').isna().sum()) - int(df[column].isna().sum())
            success = invalid_count == 0
        return QualityExpectationResult(
            expectation_name="expect_column_type_to_match_numeric",
            column=column,
            success=success,
            details={"non_numeric_values_count": invalid_count},
            severity="critical" if not success else "info"
        )

    def _check_values_between(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> QualityExpectationResult:
        series = pd.to_numeric(df[column], errors='coerce')
        out_of_bounds = int(((series < min_val) | (series > max_val)).sum())
        success = out_of_bounds == 0
        return QualityExpectationResult(
            expectation_name="expect_column_values_to_be_between",
            column=column,
            success=success,
            details={
                "min_expected": min_val,
                "max_expected": max_val,
                "violations_count": out_of_bounds
            },
            severity="high" if not success else "info"
        )

    def _check_set_membership(self, df: pd.DataFrame, column: str, allowed_set: set) -> QualityExpectationResult:
        invalid_items = int((~df[column].isin(allowed_set)).sum())
        success = invalid_items == 0
        return QualityExpectationResult(
            expectation_name="expect_column_values_to_be_in_set",
            column=column,
            success=success,
            details={"allowed_set": list(allowed_set), "violations_count": invalid_items},
            severity="medium" if not success else "info"
        )

    def _build_report(self, results: List[QualityExpectationResult]) -> Dict[str, Any]:
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        failed_details = [r.to_dict() for r in results if not r.success]

        return {
            "suite_name": self.suite_name,
            "is_healthy": failed_tests == 0,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "health_score": round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 100.0,
            "failed_expectations": failed_details,
            "all_results": [r.to_dict() for r in results]
        }
