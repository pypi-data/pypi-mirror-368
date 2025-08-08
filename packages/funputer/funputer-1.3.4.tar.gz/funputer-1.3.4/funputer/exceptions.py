"""
Exception handling for imputation suggestions to prevent inappropriate recommendations.
"""

import pandas as pd
from typing import Optional, Tuple
from .models import (
    ImputationProposal,
    ImputationMethod,
    MissingnessMechanism,
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    AnalysisConfig,
)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""

    pass


class MetadataValidationError(Exception):
    """Exception raised for metadata validation errors."""

    pass


class ImputationException:
    """Base class for imputation exceptions with standardized handling."""

    def __init__(
        self, method: ImputationMethod, rationale: str, confidence: float = 0.0
    ):
        self.method = method
        self.rationale = rationale
        self.confidence = confidence

    def to_proposal(self) -> ImputationProposal:
        """Convert exception to ImputationProposal."""
        return ImputationProposal(
            method=self.method,
            rationale=self.rationale,
            parameters={"exception_handled": True},
            confidence_score=self.confidence,
        )


def check_skip_column(column_name: str, config: AnalysisConfig) -> Optional[bool]:
    """
    Check if column should be skipped entirely from analysis.

    Args:
        column_name: Name of the column to check
        config: Analysis configuration

    Returns:
        True if column should be skipped, None otherwise
    """
    if column_name in config.skip_columns:
        return True
    return None


def check_metadata_validation_failure(
    metadata: ColumnMetadata, data_series: pd.Series
) -> Optional[ImputationException]:
    """
    Check for metadata validation failures that would prevent proper analysis.

    Args:
        metadata: Column metadata
        data_series: The data series

    Returns:
        ImputationException if validation fails, None otherwise
    """
    # Check for invalid data type
    valid_data_types = {
        "integer",
        "float",
        "string",
        "categorical",
        "datetime",
        "boolean",
    }
    if metadata.data_type not in valid_data_types:
        return ImputationException(
            method=ImputationMethod.ERROR_INVALID_METADATA,
            rationale=f"Invalid data type '{metadata.data_type}'. Valid types: {valid_data_types}",
            confidence=0.0,
        )

    # Check for invalid min/max constraints
    if (
        metadata.min_value is not None
        and metadata.max_value is not None
        and metadata.min_value > metadata.max_value
    ):
        return ImputationException(
            method=ImputationMethod.ERROR_INVALID_METADATA,
            rationale=f"Invalid constraints: min_value ({metadata.min_value}) > max_value ({metadata.max_value})",
            confidence=0.0,
        )

    # Check for missing column name
    if not metadata.column_name or metadata.column_name.strip() == "":
        return ImputationException(
            method=ImputationMethod.ERROR_INVALID_METADATA,
            rationale="Column name is missing or empty",
            confidence=0.0,
        )

    # Check for data type mismatch with actual data
    if len(data_series.dropna()) > 0:
        non_null_data = data_series.dropna()

        if metadata.data_type in ["integer", "float"]:
            if not pd.api.types.is_numeric_dtype(non_null_data):
                return ImputationException(
                    method=ImputationMethod.ERROR_INVALID_METADATA,
                    rationale=f"Data type mismatch: metadata says '{metadata.data_type}' but data is not numeric",
                    confidence=0.0,
                )

        elif metadata.data_type == "datetime":
            try:
                pd.to_datetime(non_null_data.head(5))
            except (ValueError, TypeError):
                return ImputationException(
                    method=ImputationMethod.ERROR_INVALID_METADATA,
                    rationale="Data type mismatch: metadata says 'datetime' but data cannot be parsed as datetime",
                    confidence=0.0,
                )

    return None


def check_no_missing_values(
    missingness_analysis: MissingnessAnalysis,
) -> Optional[ImputationException]:
    """
    Check if column has no missing values.

    Args:
        missingness_analysis: Results of missingness analysis

    Returns:
        ImputationException if no missing values, None otherwise
    """
    if missingness_analysis.missing_count == 0:
        return ImputationException(
            method=ImputationMethod.NO_ACTION_NEEDED,
            rationale="No missing values detected - no imputation required",
            confidence=1.0,
        )
    return None


def check_unique_identifier(metadata: ColumnMetadata) -> Optional[ImputationException]:
    """
    Check if column is a unique identifier.

    Args:
        metadata: Column metadata

    Returns:
        ImputationException if unique identifier, None otherwise
    """
    if metadata.unique_flag:
        return ImputationException(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Unique IDs cannot be auto-imputed - requires manual backfill to maintain data integrity",
            confidence=0.9,
        )
    return None


def check_all_values_missing(
    data_series: pd.Series, missingness_analysis: MissingnessAnalysis
) -> Optional[ImputationException]:
    """
    Check if all values in the column are missing.

    Args:
        data_series: The data series
        missingness_analysis: Results of missingness analysis

    Returns:
        ImputationException if all values missing, None otherwise
    """
    total_rows = len(data_series)
    if missingness_analysis.missing_count == total_rows and total_rows > 0:
        return ImputationException(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="No observed values to base imputation on - requires manual data collection",
            confidence=0.8,
        )
    return None


def check_mnar_without_business_rule(
    missingness_analysis: MissingnessAnalysis, metadata: ColumnMetadata
) -> Optional[ImputationException]:
    """
    Check if mechanism is MNAR/UNKNOWN without business rule.

    Args:
        missingness_analysis: Results of missingness analysis
        metadata: Column metadata

    Returns:
        ImputationException if MNAR/UNKNOWN without business rule, None otherwise
    """
    if (
        missingness_analysis.mechanism
        in [MissingnessMechanism.MNAR, MissingnessMechanism.UNKNOWN]
        and not metadata.business_rule
    ):
        return ImputationException(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale=f"MNAR/Unknown mechanism detected with no domain rule - requires manual investigation",
            confidence=0.7,
        )
    return None


def check_nullable_violation(
    missingness_analysis: MissingnessAnalysis, metadata: ColumnMetadata
) -> Optional[ImputationException]:
    """
    Check if column has missing values when nullable=False.

    Args:
        missingness_analysis: Results of missingness analysis
        metadata: Column metadata

    Returns:
        ImputationException if nullable=False but has missing values, None otherwise
    """
    if metadata.nullable is False and missingness_analysis.missing_count > 0:
        return ImputationException(
            method=ImputationMethod.ERROR_INVALID_METADATA,
            rationale=f"Column '{metadata.column_name}' has nullable=False but contains {missingness_analysis.missing_count} missing values",
            confidence=0.0,
        )
    return None


def check_allowed_values_violation(
    data_series: pd.Series, metadata: ColumnMetadata
) -> Optional[ImputationException]:
    """
    Check if column contains values outside allowed_values.

    Args:
        data_series: The data series
        metadata: Column metadata

    Returns:
        ImputationException if values violate allowed_values constraint, None otherwise
    """
    if metadata.allowed_values is not None and len(data_series.dropna()) > 0:
        # Parse allowed values from comma-separated string
        allowed_values = [v.strip() for v in str(metadata.allowed_values).split(",")]
        allowed_values = [v for v in allowed_values if v]  # Remove empty strings

        if allowed_values:
            non_null_data = data_series.dropna()
            invalid_values = non_null_data[
                ~non_null_data.astype(str).isin(allowed_values)
            ]

            if len(invalid_values) > 0:
                unique_invalid = invalid_values.unique()[
                    :5
                ]  # Limit to first 5 for readability
                return ImputationException(
                    method=ImputationMethod.ERROR_INVALID_METADATA,
                    rationale=f"Column '{metadata.column_name}' contains invalid values: {list(unique_invalid)}. Allowed: {allowed_values}",
                    confidence=0.0,
                )
    return None


def check_max_length_violation(
    data_series: pd.Series, metadata: ColumnMetadata
) -> Optional[ImputationException]:
    """
    Check if string values exceed max_length constraint.

    Args:
        data_series: The data series
        metadata: Column metadata

    Returns:
        ImputationException if values exceed max_length, None otherwise
    """
    if metadata.max_length is not None and metadata.data_type in [
        "string",
        "categorical",
    ]:
        non_null_data = data_series.dropna().astype(str)
        if len(non_null_data) > 0:
            max_actual_length = non_null_data.str.len().max()
            if max_actual_length > metadata.max_length:
                return ImputationException(
                    method=ImputationMethod.ERROR_INVALID_METADATA,
                    rationale=f"Column '{metadata.column_name}' has max_length={metadata.max_length} but contains values up to {max_actual_length} characters",
                    confidence=0.0,
                )
    return None


def apply_exception_handling(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
) -> Optional[ImputationProposal]:
    """
    Apply all exception handling rules in priority order.

    Args:
        column_name: Name of the column
        data_series: The data series
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration

    Returns:
        ImputationProposal if exception applies, None if normal processing should continue
    """
    # Priority 1: Check if column should be skipped entirely
    if check_skip_column(column_name, config):
        return None  # This will be handled at a higher level by omitting from output

    # Priority 2: Metadata validation failure
    metadata_exception = check_metadata_validation_failure(metadata, data_series)
    if metadata_exception:
        return metadata_exception.to_proposal()

    # Priority 3: No missing values (highest priority for actual analysis)
    no_missing_exception = check_no_missing_values(missingness_analysis)
    if no_missing_exception:
        return no_missing_exception.to_proposal()

    # Priority 4: Unique identifier
    unique_id_exception = check_unique_identifier(metadata)
    if unique_id_exception:
        return unique_id_exception.to_proposal()

    # Priority 5: All values missing
    all_missing_exception = check_all_values_missing(data_series, missingness_analysis)
    if all_missing_exception:
        return all_missing_exception.to_proposal()

    # Priority 6: MNAR/UNKNOWN without business rule
    mnar_exception = check_mnar_without_business_rule(missingness_analysis, metadata)
    if mnar_exception:
        return mnar_exception.to_proposal()

    # Priority 7: Nullable violation
    nullable_exception = check_nullable_violation(missingness_analysis, metadata)
    if nullable_exception:
        return nullable_exception.to_proposal()

    # Priority 8: Allowed values violation
    allowed_values_exception = check_allowed_values_violation(data_series, metadata)
    if allowed_values_exception:
        return allowed_values_exception.to_proposal()

    # Priority 9: Max length violation
    max_length_exception = check_max_length_violation(data_series, metadata)
    if max_length_exception:
        return max_length_exception.to_proposal()

    # No exceptions apply - proceed with normal imputation proposal logic
    return None


def should_skip_column(column_name: str, config: AnalysisConfig) -> bool:
    """
    Determine if a column should be completely omitted from analysis output.

    Args:
        column_name: Name of the column
        config: Analysis configuration

    Returns:
        True if column should be skipped, False otherwise
    """
    return column_name in config.skip_columns
