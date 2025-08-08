"""
Adaptive threshold calculation based on data characteristics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from scipy import stats

from .models import ColumnMetadata, AnalysisConfig


class AdaptiveThresholds:
    """Calculate adaptive thresholds based on dataset characteristics."""

    def __init__(
        self,
        data: pd.DataFrame,
        metadata_dict: Dict[str, ColumnMetadata],
        config: AnalysisConfig,
    ):
        """
        Initialize adaptive threshold calculator.

        Args:
            data: Full dataset
            metadata_dict: Dictionary mapping column names to metadata
            config: Base configuration
        """
        self.data = data
        self.metadata_dict = metadata_dict
        self.config = config
        self.data_characteristics = self._analyze_dataset_characteristics()

    def _analyze_dataset_characteristics(self) -> Dict[str, float]:
        """
        Analyze overall dataset characteristics to inform threshold adaptation.

        Returns:
            Dictionary of dataset characteristics
        """
        characteristics = {}

        # Dataset size factors
        characteristics["n_rows"] = len(self.data)
        characteristics["n_columns"] = len(self.data.columns)
        characteristics["data_density"] = 1.0 - (
            self.data.isna().sum().sum() / (self.data.shape[0] * self.data.shape[1])
        )

        # Missing data patterns
        characteristics["avg_missing_rate"] = self.data.isna().mean().mean()
        characteristics["missing_columns_pct"] = (self.data.isna().any()).mean()

        # Data type distribution
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        characteristics["numeric_ratio"] = (
            len(numeric_cols) / len(self.data.columns)
            if len(self.data.columns) > 0
            else 0
        )

        # Data variability (for numeric columns)
        if len(numeric_cols) > 0:
            cv_values = []
            for col in numeric_cols:
                non_null_data = self.data[col].dropna()
                if len(non_null_data) > 1 and non_null_data.std() > 0:
                    cv = (
                        non_null_data.std() / abs(non_null_data.mean())
                        if non_null_data.mean() != 0
                        else 0
                    )
                    cv_values.append(cv)
            characteristics["avg_coefficient_variation"] = (
                np.mean(cv_values) if cv_values else 0
            )
        else:
            characteristics["avg_coefficient_variation"] = 0

        return characteristics

    def get_adaptive_missing_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive missing data threshold for confidence scoring.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive threshold for missing data percentage
        """
        base_threshold = 0.05  # 5% base threshold

        # Adjust based on dataset size
        if self.data_characteristics["n_rows"] < 100:
            # Small datasets - be more lenient
            size_adjustment = 0.02
        elif self.data_characteristics["n_rows"] > 10000:
            # Large datasets - can be more strict
            size_adjustment = -0.01
        else:
            size_adjustment = 0

        # Adjust based on overall data quality
        if self.data_characteristics["data_density"] < 0.8:
            # Low density data - be more lenient
            density_adjustment = 0.03
        elif self.data_characteristics["data_density"] > 0.95:
            # High density data - can be stricter
            density_adjustment = -0.01
        else:
            density_adjustment = 0

        # Adjust based on column importance (unique columns are more critical)
        metadata = self.metadata_dict.get(column_name)
        if metadata and metadata.unique_flag:
            importance_adjustment = -0.02  # Stricter for unique columns
        elif metadata and getattr(metadata, 'business_rule', None):
            importance_adjustment = -0.01  # Stricter for business rule columns
        else:
            importance_adjustment = 0

        adapted_threshold = (
            base_threshold
            + size_adjustment
            + density_adjustment
            + importance_adjustment
        )
        return max(0.01, min(0.15, adapted_threshold))  # Bound between 1% and 15%

    def get_adaptive_confidence_adjustment(
        self, column_name: str, missing_pct: float
    ) -> float:
        """
        Calculate adaptive confidence adjustment based on data characteristics.

        Args:
            column_name: Name of the column
            missing_pct: Missing percentage for the column

        Returns:
            Confidence adjustment factor (-0.3 to +0.3)
        """
        adjustment = 0.0

        # Adjust based on sample size adequacy
        non_missing_count = (
            len(self.data[column_name].dropna())
            if column_name in self.data.columns
            else 0
        )
        if non_missing_count > 1000:
            adjustment += 0.1  # Large sample, higher confidence
        elif non_missing_count < 50:
            adjustment -= 0.15  # Small sample, lower confidence
        elif non_missing_count < 20:
            adjustment -= 0.25  # Very small sample, much lower confidence

        # Adjust based on data variability
        if column_name in self.data.columns:
            metadata = self.metadata_dict.get(column_name)
            if metadata and metadata.data_type in ["integer", "float"]:
                non_null_data = self.data[column_name].dropna()
                if len(non_null_data) > 1:
                    # High variability reduces confidence in simple imputation methods
                    cv = (
                        non_null_data.std() / abs(non_null_data.mean())
                        if non_null_data.mean() != 0
                        else 0
                    )
                    if cv > 2.0:  # Very high variability
                        adjustment -= 0.1
                    elif cv < 0.2:  # Low variability
                        adjustment += 0.05

        # Adjust based on business context
        metadata = self.metadata_dict.get(column_name)
        if metadata:
            if metadata.unique_flag:
                adjustment -= 0.1  # Unique columns are inherently harder to impute
            elif getattr(metadata, 'business_rule', None) and metadata.dependent_column:
                adjustment += 0.1  # Business rules provide guidance

        # Adjust based on overall data quality context
        if self.data_characteristics["data_density"] > 0.95:
            adjustment += 0.05  # High quality dataset
        elif self.data_characteristics["data_density"] < 0.7:
            adjustment -= 0.1  # Low quality dataset

        return max(-0.3, min(0.3, adjustment))

    def get_adaptive_skewness_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive skewness threshold for mean vs median decision.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive skewness threshold
        """
        base_threshold = self.config.skewness_threshold  # Default 2.0

        # Adjust based on sample size
        if column_name in self.data.columns:
            non_null_count = len(self.data[column_name].dropna())
            if non_null_count < 30:
                # Small samples - be more conservative, use median more often
                return base_threshold * 0.7
            elif non_null_count > 1000:
                # Large samples - can be less conservative
                return base_threshold * 1.2

        return base_threshold

    def get_adaptive_outlier_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive outlier percentage threshold.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive outlier threshold
        """
        base_threshold = self.config.outlier_threshold  # Default 0.05

        # Adjust based on data type and business rules
        metadata = self.metadata_dict.get(column_name)
        if metadata:
            if metadata.min_value is not None or metadata.max_value is not None:
                # Columns with defined ranges - be more strict about outliers
                return base_threshold * 0.8
            elif metadata.unique_flag:
                # Unique columns - outliers are more problematic
                return base_threshold * 0.6

        # Adjust based on dataset characteristics
        if self.data_characteristics["avg_coefficient_variation"] > 1.5:
            # High variability dataset - be more lenient with outliers
            return base_threshold * 1.3
        elif self.data_characteristics["avg_coefficient_variation"] < 0.5:
            # Low variability dataset - be more strict
            return base_threshold * 0.8

        return base_threshold

    def get_adaptive_correlation_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive correlation threshold for relationship detection.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive correlation threshold
        """
        base_threshold = self.config.correlation_threshold  # Default 0.3

        # Adjust based on dataset size
        if self.data_characteristics["n_rows"] < 100:
            # Small datasets - need stronger correlations to be meaningful
            return base_threshold * 1.3
        elif self.data_characteristics["n_rows"] > 5000:
            # Large datasets - weaker correlations can be meaningful
            return base_threshold * 0.8

        # Adjust based on number of potential predictors
        if self.data_characteristics["n_columns"] > 20:
            # Many columns - be more selective
            return base_threshold * 1.1
        elif self.data_characteristics["n_columns"] < 5:
            # Few columns - be more inclusive
            return base_threshold * 0.9

        return base_threshold


def calculate_adaptive_confidence_score(
    column_name: str,
    missingness_analysis,
    outlier_analysis,
    metadata: ColumnMetadata,
    data_series: pd.Series,
    adaptive_thresholds: AdaptiveThresholds,
) -> float:
    """
    Calculate confidence score using adaptive thresholds.

    Args:
        column_name: Name of the column
        missingness_analysis: Results of missingness mechanism analysis
        outlier_analysis: Results of outlier analysis
        metadata: Column metadata
        data_series: The actual data series
        adaptive_thresholds: Adaptive threshold calculator

    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence

    # Get adaptive thresholds
    missing_threshold = adaptive_thresholds.get_adaptive_missing_threshold(column_name)
    missing_pct = missingness_analysis.missing_percentage

    # Adjust based on missing percentage using adaptive threshold
    if missing_pct < missing_threshold:
        confidence += 0.2
    elif missing_pct < missing_threshold * 2:
        confidence += 0.1
    elif missing_pct > 0.50:  # Still use absolute threshold for very high missingness
        confidence -= 0.2

    # Apply adaptive confidence adjustment
    adaptive_adjustment = adaptive_thresholds.get_adaptive_confidence_adjustment(
        column_name, missing_pct
    )
    confidence += adaptive_adjustment

    # Adjust based on mechanism certainty (unchanged)
    from .models import MissingnessMechanism

    if missingness_analysis.mechanism == MissingnessMechanism.MCAR:
        if missingness_analysis.p_value is None or missingness_analysis.p_value > 0.1:
            confidence += 0.1
    elif missingness_analysis.mechanism == MissingnessMechanism.MAR:
        if missingness_analysis.p_value and missingness_analysis.p_value < 0.01:
            confidence += 0.15

    # Adjust based on outlier percentage using adaptive threshold
    outlier_threshold = adaptive_thresholds.get_adaptive_outlier_threshold(column_name)
    if outlier_analysis.outlier_percentage < outlier_threshold:
        confidence += 0.05
    elif outlier_analysis.outlier_percentage > outlier_threshold * 4:
        confidence -= 0.1

    # Adjust based on metadata completeness (unchanged)
    if getattr(metadata, 'business_rule', None):
        confidence += 0.05
    if metadata.dependent_column:
        confidence += 0.05

    # Ensure confidence is within bounds
    return max(0.1, min(1.0, confidence))
