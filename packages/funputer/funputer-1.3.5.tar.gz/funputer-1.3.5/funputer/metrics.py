"""
No-op metrics collection for compatibility.
This module provides stub implementations that maintain API compatibility
without any external dependencies or actual metrics collection.
"""

import time
from typing import Dict, Any


class MetricsCollector:
    """No-op metrics collector that maintains API compatibility."""

    def __init__(self, port: int = 8001):
        """Initialize no-op metrics collector."""
        self.port = port
        self._enabled = False

    def start_server(self) -> None:
        """No-op server start."""
        pass

    def record_column_processed(self, data_type: str, mechanism: str) -> None:
        """No-op column processing record."""
        pass

    def update_missing_values_total(self, count: int) -> None:
        """No-op missing values update."""
        pass

    def update_outliers_total(self, count: int) -> None:
        """No-op outliers update."""
        pass

    def record_analysis_duration(
        self, column_name: str, data_type: str, duration: float
    ) -> None:
        """No-op analysis duration record."""
        pass

    def update_total_analysis_duration(self, duration: float) -> None:
        """No-op total duration update."""
        pass

    def record_confidence_score(
        self, method: str, mechanism: str, score: float
    ) -> None:
        """No-op confidence score record."""
        pass

    def update_data_quality_score(self, dataset: str, score: float) -> None:
        """No-op data quality score update."""
        pass

    def calculate_data_quality_score(self, analysis_results: list) -> float:
        """Calculate data quality score without external dependencies."""
        if not analysis_results:
            return 0.0

        total_columns = len(analysis_results)
        quality_factors = []

        for result in analysis_results:
            # Missing data impact (0-1, where 1 is best)
            missing_pct = getattr(result, "missing_percentage", 0)
            missing_score = max(
                0, 1 - (missing_pct * 2)
            )  # Heavy penalty for missing data

            # Outlier impact (0-1, where 1 is best)
            outlier_pct = getattr(result, "outlier_percentage", 0)
            outlier_score = max(
                0, 1 - (outlier_pct * 1.5)
            )  # Moderate penalty for outliers

            # Confidence score (already 0-1)
            confidence = getattr(result, "confidence_score", 0.5)
            if hasattr(result, "imputation_proposal"):
                confidence = getattr(
                    result.imputation_proposal, "confidence_score", 0.5
                )

            # Weighted average
            column_quality = (
                missing_score * 0.4 + outlier_score * 0.3 + confidence * 0.3
            )
            quality_factors.append(column_quality)

        # Overall quality score
        overall_score = sum(quality_factors) / total_columns if quality_factors else 0.0
        return min(1.0, max(0.0, overall_score))


# Global no-op metrics instance
_metrics_collector = None


def get_metrics_collector(port: int = 8001) -> MetricsCollector:
    """Get or create the global no-op metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(port)
    return _metrics_collector


def start_metrics_server(port: int = 8001) -> None:
    """No-op metrics server start."""
    pass


class AnalysisTimer:
    """No-op context manager for timing analysis operations."""

    def __init__(self, column_name: str, data_type: str):
        """Initialize no-op timer."""
        self.column_name = column_name
        self.data_type = data_type
        self.start_time = None

    def __enter__(self):
        """Start timing (no-op)."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing (no-op)."""
        pass


# Alias for backward compatibility
MetricsContext = AnalysisTimer
