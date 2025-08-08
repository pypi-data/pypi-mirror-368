"""
Imputation method proposal logic based on analysis results.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
from scipy import stats

from .models import (
    ImputationProposal,
    ImputationMethod,
    MissingnessMechanism,
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    AnalysisConfig,
)
from .exceptions import apply_exception_handling
from .adaptive_thresholds import AdaptiveThresholds, calculate_adaptive_confidence_score


def calculate_confidence_score(
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    metadata: ColumnMetadata,
    data_series: pd.Series,
) -> float:
    """
    Calculate confidence score for the imputation proposal (0-1 scale).

    Args:
        missingness_analysis: Results of missingness mechanism analysis
        outlier_analysis: Results of outlier analysis
        metadata: Column metadata
        data_series: The actual data series

    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence

    # Adjust based on missing percentage
    missing_pct = missingness_analysis.missing_percentage
    if missing_pct < 0.05:  # Less than 5% missing
        confidence += 0.2
    elif missing_pct < 0.20:  # Less than 20% missing
        confidence += 0.1
    elif missing_pct > 0.50:  # More than 50% missing
        confidence -= 0.2

    # Adjust based on mechanism certainty
    if missingness_analysis.mechanism == MissingnessMechanism.MCAR:
        if missingness_analysis.p_value is None or missingness_analysis.p_value > 0.1:
            confidence += 0.1  # High certainty of MCAR
    elif missingness_analysis.mechanism == MissingnessMechanism.MAR:
        if len(missingness_analysis.related_columns) > 0:
            confidence += 0.05  # Some evidence for MAR
    else:  # MNAR or UNKNOWN
        confidence -= 0.1

    # Adjust based on outlier impact
    outlier_pct = outlier_analysis.outlier_percentage
    if outlier_pct < 0.05:  # Low outlier percentage
        confidence += 0.05
    elif outlier_pct > 0.20:  # High outlier percentage
        confidence -= 0.1

    # NEW: Adjust based on metadata constraints
    if metadata.allowed_values is not None and str(metadata.allowed_values).strip():
        # Having allowed values increases confidence for categorical data
        if metadata.data_type in ["categorical", "string"]:
            confidence += 0.1

    if metadata.max_length is not None and metadata.max_length > 0:
        # Having max_length constraint increases confidence for string data
        if metadata.data_type in ["string", "categorical"]:
            confidence += 0.05

    if metadata.nullable is False:
        # Non-nullable columns with missing values reduce confidence
        if missingness_analysis.missing_count > 0:
            confidence -= 0.15
        else:
            # Non-nullable with no missing values increases confidence
            confidence += 0.05

    # NEW: Adjust based on data quality indicators
    non_null_data = data_series.dropna()
    if len(non_null_data) > 0:
        # Check if string data respects max_length
        if (
            metadata.data_type in ["string", "categorical"]
            and metadata.max_length is not None
        ):
            max_actual_length = non_null_data.astype(str).str.len().max()
            if max_actual_length <= metadata.max_length:
                confidence += 0.05

        # Check if categorical data respects allowed_values
        if metadata.data_type in ["categorical", "string"] and metadata.allowed_values:
            allowed_values = [
                v.strip() for v in str(metadata.allowed_values).split(",") if v.strip()
            ]
            if allowed_values:
                valid_ratio = non_null_data.astype(str).isin(allowed_values).mean()
                confidence += valid_ratio * 0.1

    return max(0.1, min(1.0, confidence))


def _get_allowed_values_list(metadata: ColumnMetadata) -> list:
    """Parse allowed_values string into a list of valid values."""
    if not metadata.allowed_values:
        return []

    # Split by comma and clean up
    values = [v.strip() for v in str(metadata.allowed_values).split(",")]
    return [v for v in values if v]


def _adjust_confidence_for_constraints(
    base_confidence: float, metadata: ColumnMetadata, data_series: pd.Series
) -> float:
    """Adjust confidence score based on metadata constraints."""
    confidence = base_confidence

    # Increase confidence when constraints are provided
    if metadata.allowed_values:
        confidence += 0.1

    if metadata.max_length is not None:
        confidence += 0.05

    # Decrease confidence if constraints might be violated
    if metadata.nullable is False and data_series.isnull().any():
        confidence -= 0.2

    return max(0.0, min(1.0, confidence))


def propose_imputation_method(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
    full_data: pd.DataFrame = None,
    metadata_dict: Dict[str, ColumnMetadata] = None,
) -> ImputationProposal:
    """
    Propose the best imputation method based on comprehensive analysis.

    Args:
        column_name: Name of the column
        data_series: The data series to analyze
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration
        full_data: Full dataset for adaptive threshold calculation
        metadata_dict: Dictionary of all column metadata for adaptive thresholds

    Returns:
        ImputationProposal with method, rationale, and parameters
    """
    # FIRST: Apply exception handling rules
    exception_proposal = apply_exception_handling(
        column_name,
        data_series,
        metadata,
        missingness_analysis,
        outlier_analysis,
        config,
    )

    if exception_proposal is not None:
        return exception_proposal

    # Initialize adaptive thresholds if data is available
    adaptive_thresholds = None
    if full_data is not None and metadata_dict is not None:
        adaptive_thresholds = AdaptiveThresholds(full_data, metadata_dict, config)

    # Helper function to calculate confidence score
    def get_confidence_score():
        if adaptive_thresholds is not None:
            return calculate_adaptive_confidence_score(
                column_name,
                missingness_analysis,
                outlier_analysis,
                metadata,
                data_series,
                adaptive_thresholds,
            )
        else:
            return calculate_confidence_score(
                missingness_analysis, outlier_analysis, metadata, data_series
            )

    # If no exceptions apply, proceed with normal imputation logic
    missing_pct = missingness_analysis.missing_percentage
    mechanism = missingness_analysis.mechanism

    # Handle unique identifier columns (backup check)
    if metadata.unique_flag:
        return ImputationProposal(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Unique identifier column requires manual backfill to maintain data integrity",
            parameters={"strategy": "manual_review"},
            confidence_score=get_confidence_score(),
        )

    # Handle dependency rule columns (specific calculations)
    if metadata.dependency_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has dependency rule on {metadata.dependent_column}: {metadata.dependency_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": metadata.dependency_rule,
                "rule_type": "dependency",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle business rule columns (general constraints)
    if metadata.business_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has business rule dependency on {metadata.dependent_column}: {metadata.business_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": metadata.business_rule,
                "rule_type": "business",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle high missing percentage (>80%)
    if missing_pct > config.missing_threshold:
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Very high missing percentage ({missing_pct:.1%}) suggests systematic absence - use constant 'Missing'",
            parameters={"fill_value": "Missing"},
            confidence_score=get_confidence_score(),
        )

    # Method selection based on data type and mechanism
    if metadata.data_type == "categorical":
        allowed_values = _get_allowed_values_list(metadata)

        if allowed_values and len(allowed_values) > 0:
            # Use allowed values for imputation when available
            if mechanism == MissingnessMechanism.MCAR:
                # Count frequency of allowed values only
                valid_data = data_series.dropna()
                if len(valid_data) > 0:
                    valid_data = valid_data[valid_data.astype(str).isin(allowed_values)]
                    if len(valid_data) > 0:
                        most_frequent = (
                            valid_data.mode().iloc[0]
                            if len(valid_data.mode()) > 0
                            else allowed_values[0]
                        )
                    else:
                        most_frequent = allowed_values[0]
                else:
                    most_frequent = allowed_values[0]

                confidence = get_confidence_score()
                confidence = _adjust_confidence_for_constraints(
                    confidence, metadata, data_series
                )

                return ImputationProposal(
                    method=ImputationMethod.MODE,
                    rationale=f"Categorical data with MCAR mechanism and allowed values constraint - use most frequent from {len(allowed_values)} allowed values",
                    parameters={
                        "strategy": "most_frequent",
                        "allowed_values": allowed_values,
                        "fill_value": most_frequent,
                    },
                    confidence_score=confidence,
                )
            else:  # MAR
                confidence = get_confidence_score()
                confidence = _adjust_confidence_for_constraints(
                    confidence, metadata, data_series
                )

                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"Categorical data with MAR mechanism and allowed values constraint - use kNN restricted to {len(allowed_values)} allowed values",
                    parameters={
                        "n_neighbors": min(5, max(3, data_series.count() // 20)),
                        "weights": "distance",
                        "allowed_values": allowed_values,
                    },
                    confidence_score=confidence,
                )
        else:
            # Original logic when no allowed_values specified
            if mechanism == MissingnessMechanism.MCAR:
                return ImputationProposal(
                    method=ImputationMethod.MODE,
                    rationale="Categorical data with MCAR mechanism - use most frequent category",
                    parameters={"strategy": "most_frequent"},
                    confidence_score=get_confidence_score(),
                )
            else:  # MAR
                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"Categorical data with MAR mechanism (related to {', '.join(missingness_analysis.related_columns[:2])}) - use kNN",
                    parameters={
                        "n_neighbors": min(5, max(3, data_series.count() // 20)),
                        "weights": "distance",
                    },
                    confidence_score=get_confidence_score(),
                )

    elif metadata.data_type == "string":
        if metadata.max_length is not None:
            confidence = get_confidence_score()
            confidence = _adjust_confidence_for_constraints(
                confidence, metadata, data_series
            )

            if mechanism == MissingnessMechanism.MCAR:
                return ImputationProposal(
                    method=ImputationMethod.MODE,
                    rationale=f"String data with MCAR mechanism and max_length={metadata.max_length} constraint - use most frequent string",
                    parameters={
                        "strategy": "most_frequent",
                        "max_length": metadata.max_length,
                    },
                    confidence_score=confidence,
                )
            else:  # MAR
                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"String data with MAR mechanism and max_length={metadata.max_length} constraint - use kNN",
                    parameters={
                        "n_neighbors": min(5, max(3, data_series.count() // 20)),
                        "weights": "distance",
                        "max_length": metadata.max_length,
                    },
                    confidence_score=confidence,
                )
        else:
            # Original string handling logic
            if mechanism == MissingnessMechanism.MCAR:
                return ImputationProposal(
                    method=ImputationMethod.MODE,
                    rationale="String data with MCAR mechanism - use most frequent string",
                    parameters={"strategy": "most_frequent"},
                    confidence_score=get_confidence_score(),
                )
            else:  # MAR
                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"String data with MAR mechanism - use kNN",
                    parameters={
                        "n_neighbors": min(5, max(3, data_series.count() // 20)),
                        "weights": "distance",
                    },
                    confidence_score=get_confidence_score(),
                )

    elif metadata.data_type in ["integer", "float"]:
        # Check for skewness to decide between mean and median
        non_null_data = data_series.dropna()
        if len(non_null_data) > 3:
            skewness = abs(stats.skew(non_null_data))
        else:
            skewness = 0

        # Get adaptive skewness threshold
        skewness_threshold = (
            adaptive_thresholds.get_adaptive_skewness_threshold(column_name)
            if adaptive_thresholds
            else config.skewness_threshold
        )

        if mechanism == MissingnessMechanism.MCAR:
            if skewness > skewness_threshold:
                return ImputationProposal(
                    method=ImputationMethod.MEDIAN,
                    rationale=f"Numeric data with MCAR mechanism and high skewness ({skewness:.2f}) - use median",
                    parameters={"strategy": "median"},
                    confidence_score=get_confidence_score(),
                )
            else:
                return ImputationProposal(
                    method=ImputationMethod.MEAN,
                    rationale=f"Numeric data with MCAR mechanism and low skewness ({skewness:.2f}) - use mean",
                    parameters={"strategy": "mean"},
                    confidence_score=get_confidence_score(),
                )
        else:  # MAR
            # Choose between regression and kNN based on data size and relationships
            if (
                len(non_null_data) > 50
                and len(missingness_analysis.related_columns) > 0
            ):
                return ImputationProposal(
                    method=ImputationMethod.REGRESSION,
                    rationale=f"Numeric data with MAR mechanism - use regression with predictors: {', '.join(missingness_analysis.related_columns[:2])}",
                    parameters={
                        "predictors": missingness_analysis.related_columns[:3],
                        "estimator": "BayesianRidge",
                    },
                    confidence_score=get_confidence_score(),
                )
            else:
                return ImputationProposal(
                    method=ImputationMethod.KNN,
                    rationale=f"Numeric data with MAR mechanism - use kNN (insufficient data for regression)",
                    parameters={
                        "n_neighbors": min(5, max(3, len(non_null_data) // 10)),
                        "weights": "distance",
                    },
                    confidence_score=get_confidence_score(),
                )

    elif metadata.data_type == "datetime":
        if mechanism == MissingnessMechanism.MCAR:
            return ImputationProposal(
                method=ImputationMethod.FORWARD_FILL,
                rationale="Datetime data with MCAR mechanism - use forward fill to maintain temporal continuity",
                parameters={"method": "ffill", "limit": 3},
                confidence_score=get_confidence_score(),
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.BUSINESS_RULE,
                rationale="Datetime data with MAR mechanism - requires business logic for temporal imputation",
                parameters={"strategy": "business_logic_required"},
                confidence_score=get_confidence_score(),
            )

    elif metadata.data_type == "boolean":
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Boolean data - use most frequent value",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score(),
        )

    # Default fallback
    return ImputationProposal(
        method=ImputationMethod.CONSTANT_MISSING,
        rationale=f"Unknown data type ({metadata.data_type}) - use constant 'Missing' as safe fallback",
        parameters={"fill_value": "Missing"},
        confidence_score=0.3,
    )
