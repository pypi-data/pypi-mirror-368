"""
Simplified missingness mechanism analysis with MCAR-focused defaults.
"""

import pandas as pd
from typing import Dict

from .models import (
    MissingnessAnalysis,
    MissingnessMechanism,
    ColumnMetadata,
    AnalysisConfig,
)


def analyze_missingness_mechanism(
    target_column: str,
    data: pd.DataFrame,
    metadata_dict: Dict[str, ColumnMetadata],
    config: AnalysisConfig,
) -> MissingnessAnalysis:
    """
    Simplified missingness mechanism analysis that defaults to MCAR.
    
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

    # If no missing values
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

    # Check if metadata explicitly indicates MAR through dependent_column
    target_metadata = metadata_dict.get(target_column)
    if target_metadata and target_metadata.dependent_column:
        dependent_col = target_metadata.dependent_column
        if dependent_col in data.columns and not data[dependent_col].isna().all():
            return MissingnessAnalysis(
                missing_count=missing_count,
                missing_percentage=missing_percentage,
                mechanism=MissingnessMechanism.MAR,
                test_statistic=None,
                p_value=None,
                related_columns=[dependent_col],
                rationale=f"Metadata indicates dependency on '{dependent_col}' - classified as MAR",
            )

    # Default to MCAR for all other cases (simplified approach)
    return MissingnessAnalysis(
        missing_count=missing_count,
        missing_percentage=missing_percentage,
        mechanism=MissingnessMechanism.MCAR,
        test_statistic=None,
        p_value=None,
        related_columns=[],
        rationale="Simplified analysis defaults to MCAR unless explicit dependency specified",
    )
