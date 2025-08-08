"""
Missingness mechanism analysis using statistical tests.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
from scipy import stats
from scipy.stats import chi2_contingency, pointbiserialr
import warnings

from .models import (
    MissingnessAnalysis,
    MissingnessMechanism,
    ColumnMetadata,
    AnalysisConfig,
)


def point_biserial_test(
    target_missing: pd.Series, predictor: pd.Series, threshold: float = 0.2
) -> Tuple[float, float, bool]:
    """
    Perform point-biserial correlation test for MAR detection.

    Args:
        target_missing: Binary series indicating missingness (1=missing, 0=present)
        predictor: Continuous predictor variable
        threshold: Correlation threshold for significance

    Returns:
        Tuple of (correlation, p_value, is_significant)
    """
    # Remove rows where predictor is also missing
    valid_mask = ~predictor.isna()
    target_clean = target_missing[valid_mask]
    predictor_clean = predictor[valid_mask]

    if len(target_clean) < 10 or target_clean.sum() < 5:
        return 0.0, 1.0, False

    try:
        correlation, p_value = pointbiserialr(target_clean, predictor_clean)
        is_significant = abs(correlation) > threshold and p_value < 0.05
        return correlation, p_value, is_significant
    except Exception:
        return 0.0, 1.0, False


def chi_square_test(
    target_missing: pd.Series, predictor: pd.Series, alpha: float = 0.05
) -> Tuple[float, float, bool]:
    """
    Perform chi-square test for independence between missingness and categorical predictor.

    Args:
        target_missing: Binary series indicating missingness
        predictor: Categorical predictor variable
        alpha: Significance level

    Returns:
        Tuple of (chi2_statistic, p_value, is_significant)
    """
    # Remove rows where predictor is missing
    valid_mask = ~predictor.isna()
    target_clean = target_missing[valid_mask]
    predictor_clean = predictor[valid_mask]

    if len(target_clean) < 10 or target_clean.sum() < 5:
        return 0.0, 1.0, False

    try:
        # Create contingency table
        contingency_table = pd.crosstab(target_clean, predictor_clean)

        # Ensure minimum expected frequency
        if (contingency_table < 5).any().any():
            return 0.0, 1.0, False

        chi2, p_value, dof, expected = chi2_contingency(contingency_table)
        is_significant = p_value < alpha

        return chi2, p_value, is_significant
    except Exception:
        return 0.0, 1.0, False


def find_related_columns(
    target_column: str,
    data: pd.DataFrame,
    metadata_dict: Dict[str, ColumnMetadata],
    max_columns: int = 2,
) -> List[str]:
    """
    Find columns most likely to be related to the target column for MAR analysis.

    Args:
        target_column: Name of the target column
        data: Full dataset
        metadata_dict: Dictionary mapping column names to metadata
        max_columns: Maximum number of related columns to return

    Returns:
        List of related column names
    """
    related_columns = []
    target_metadata = metadata_dict.get(target_column)

    # First priority: explicitly defined dependent column
    if target_metadata and target_metadata.dependent_column:
        if target_metadata.dependent_column in data.columns:
            related_columns.append(target_metadata.dependent_column)

    # Second priority: columns that depend on this column
    for col_name, metadata in metadata_dict.items():
        if (
            col_name != target_column
            and metadata.dependent_column == target_column
            and col_name in data.columns
        ):
            related_columns.append(col_name)
            if len(related_columns) >= max_columns:
                break

    # Third priority: high correlation with numeric columns
    if len(related_columns) < max_columns:
        target_series = data[target_column]

        # Only calculate correlations for numeric target columns
        if target_metadata and target_metadata.data_type in ["integer", "float"]:
            correlations = []

            for col_name in data.columns:
                if (
                    col_name != target_column
                    and col_name not in related_columns
                    and metadata_dict.get(col_name, ColumnMetadata("", "")).data_type
                    in ["integer", "float"]
                ):

                    try:
                        corr = target_series.corr(data[col_name])
                        if not np.isnan(corr):
                            correlations.append((col_name, abs(corr)))
                    except Exception:
                        continue

            # Sort by correlation strength and add top candidates
            correlations.sort(key=lambda x: x[1], reverse=True)
            for col_name, corr in correlations[: max_columns - len(related_columns)]:
                if corr > 0.3:  # Minimum correlation threshold
                    related_columns.append(col_name)

    return related_columns[:max_columns]


def analyze_missingness_mechanism(
    target_column: str,
    data: pd.DataFrame,
    metadata_dict: Dict[str, ColumnMetadata],
    config: AnalysisConfig,
) -> MissingnessAnalysis:
    """
    Analyze missingness mechanism for a target column.

    Args:
        target_column: Name of the column to analyze
        data: Full dataset
        metadata_dict: Dictionary mapping column names to metadata
        config: Analysis configuration

    Returns:
        MissingnessAnalysis object with results
    """
    target_series = data[target_column]
    missing_count = target_series.isna().sum()
    total_count = len(target_series)
    missing_percentage = missing_count / total_count if total_count > 0 else 0.0

    # If no missing values, return MCAR
    if missing_count == 0:
        return MissingnessAnalysis(
            missing_count=0,
            missing_percentage=0.0,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="No missing values detected",
        )

    # If too few missing values for statistical testing
    if missing_count < 5:
        return MissingnessAnalysis(
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="Too few missing values for reliable statistical testing - assuming MCAR",
        )

    # Create binary missingness indicator
    missing_indicator = target_series.isna().astype(int)

    # Find related columns for testing
    related_columns = find_related_columns(target_column, data, metadata_dict)

    if not related_columns:
        return MissingnessAnalysis(
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            mechanism=MissingnessMechanism.MCAR,
            test_statistic=None,
            p_value=None,
            related_columns=[],
            rationale="No suitable predictor columns found for MAR testing - assuming MCAR",
        )

    # Test for MAR using related columns
    significant_relationships = []
    best_test_stat = 0.0
    best_p_value = 1.0

    for related_col in related_columns:
        related_series = data[related_col]
        related_metadata = metadata_dict.get(related_col)

        if related_metadata is None:
            continue

        # Choose appropriate test based on data type
        if related_metadata.data_type in ["integer", "float"]:
            # Point-biserial correlation for continuous predictors
            correlation, p_value, is_significant = point_biserial_test(
                missing_indicator, related_series, config.point_biserial_threshold
            )

            if is_significant:
                significant_relationships.append(related_col)
                if abs(correlation) > abs(best_test_stat):
                    best_test_stat = correlation
                    best_p_value = p_value

        elif related_metadata.data_type in ["categorical", "string"]:
            # Chi-square test for categorical predictors
            chi2_stat, p_value, is_significant = chi_square_test(
                missing_indicator, related_series, config.chi_square_alpha
            )

            if is_significant:
                significant_relationships.append(related_col)
                if chi2_stat > best_test_stat:
                    best_test_stat = chi2_stat
                    best_p_value = p_value

    # Determine mechanism based on test results
    if significant_relationships:
        mechanism = MissingnessMechanism.MAR
        rationale = (
            f"Significant relationship found with {len(significant_relationships)} "
            f"predictor(s): {', '.join(significant_relationships[:2])} "
            f"(p-value: {best_p_value:.4f})"
        )
    else:
        mechanism = MissingnessMechanism.MCAR
        rationale = (
            f"No significant relationships found with tested predictors "
            f"({', '.join(related_columns[:2])}) - assuming MCAR"
        )

    return MissingnessAnalysis(
        missing_count=missing_count,
        missing_percentage=missing_percentage,
        mechanism=mechanism,
        test_statistic=best_test_stat,
        p_value=best_p_value,
        related_columns=significant_relationships,
        rationale=rationale,
    )
