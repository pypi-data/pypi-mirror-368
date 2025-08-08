"""
Additional tests for exceptions.py to achieve 95% coverage.
These tests target specific untested code paths and edge cases.
"""

import pytest
import pandas as pd
import numpy as np

from funputer.exceptions import (
    ConfigurationError,
    MetadataValidationError,
    ImputationException,
    check_skip_column,
    check_metadata_validation_failure,
    check_no_missing_values,
    check_unique_identifier,
    check_all_values_missing,
    check_mnar_without_business_rule,
    check_nullable_violation,
    check_allowed_values_violation,
    check_max_length_violation,
    apply_exception_handling,
    should_skip_column,
)
from funputer.models import (
    ColumnMetadata,
    AnalysisConfig,
    ImputationMethod,
    MissingnessAnalysis,
    MissingnessMechanism,
    OutlierAnalysis,
    OutlierHandling,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_configuration_error_creation(self):
        """Test ConfigurationError creation and usage."""
        error = ConfigurationError("Test configuration error")
        assert str(error) == "Test configuration error"
        assert isinstance(error, Exception)

    def test_metadata_validation_error_creation(self):
        """Test MetadataValidationError creation and usage."""
        error = MetadataValidationError("Test validation error")
        assert str(error) == "Test validation error"
        assert isinstance(error, Exception)

    def test_metadata_validation_error_in_context(self):
        """Test MetadataValidationError in exception handling context."""
        try:
            raise MetadataValidationError("Invalid metadata format")
        except MetadataValidationError as e:
            assert "Invalid metadata format" in str(e)


class TestImputationException:
    """Test ImputationException class."""

    def test_imputation_exception_creation_all_params(self):
        """Test ImputationException creation with all parameters."""
        exception = ImputationException(
            method=ImputationMethod.MEAN, rationale="Test rationale", confidence=0.75
        )
        assert exception.method == ImputationMethod.MEAN
        assert exception.rationale == "Test rationale"
        assert exception.confidence == 0.75

    def test_imputation_exception_creation_default_confidence(self):
        """Test ImputationException creation with default confidence."""
        exception = ImputationException(
            method=ImputationMethod.MEDIAN, rationale="Test with default confidence"
        )
        assert exception.method == ImputationMethod.MEDIAN
        assert exception.rationale == "Test with default confidence"
        assert exception.confidence == 0.0  # Default value

    def test_imputation_exception_to_proposal(self):
        """Test conversion to ImputationProposal."""
        exception = ImputationException(
            method=ImputationMethod.MODE,
            rationale="Mode imputation needed",
            confidence=0.8,
        )

        proposal = exception.to_proposal()
        assert proposal.method == ImputationMethod.MODE
        assert proposal.rationale == "Mode imputation needed"
        assert proposal.confidence_score == 0.8
        assert proposal.parameters == {"exception_handled": True}


class TestExceptionChecks:
    """Test individual exception check functions."""

    def test_check_skip_column_should_skip(self):
        """Test check_skip_column when column should be skipped."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        result = check_skip_column("col1", config)
        assert result is True

        result = check_skip_column("col2", config)
        assert result is True

    def test_check_skip_column_should_not_skip(self):
        """Test check_skip_column when column should not be skipped."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        result = check_skip_column("col3", config)
        assert result is None

        result = check_skip_column("different_col", config)
        assert result is None

    def test_check_skip_column_empty_skip_list(self):
        """Test check_skip_column with empty skip list."""
        config = AnalysisConfig(skip_columns=[])

        result = check_skip_column("any_col", config)
        assert result is None


class TestMetadataValidationFailure:
    """Test check_metadata_validation_failure function comprehensively."""

    def test_invalid_data_type(self):
        """Test metadata validation with invalid data type."""
        metadata = ColumnMetadata("col1", "invalid_type")
        data_series = pd.Series([1, 2, 3])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Invalid data type 'invalid_type'" in result.rationale
        assert result.confidence == 0.0

    def test_invalid_min_max_constraints(self):
        """Test metadata validation with invalid min/max constraints."""
        metadata = ColumnMetadata(
            "col1", "integer", min_value=10, max_value=5
        )  # min > max
        data_series = pd.Series([1, 2, 3])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "min_value (10) > max_value (5)" in result.rationale
        assert result.confidence == 0.0

    def test_missing_column_name(self):
        """Test metadata validation with missing column name."""
        metadata = ColumnMetadata("", "integer")  # Empty column name
        data_series = pd.Series([1, 2, 3])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Column name is missing or empty" in result.rationale
        assert result.confidence == 0.0

    def test_whitespace_only_column_name(self):
        """Test metadata validation with whitespace-only column name."""
        metadata = ColumnMetadata("   ", "integer")  # Whitespace only
        data_series = pd.Series([1, 2, 3])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Column name is missing or empty" in result.rationale

    def test_numeric_data_type_mismatch(self):
        """Test numeric data type mismatch."""
        metadata = ColumnMetadata("col1", "integer")
        data_series = pd.Series(["a", "b", "c"])  # String data but integer metadata

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Data type mismatch" in result.rationale
        assert "not numeric" in result.rationale

    def test_float_data_type_mismatch(self):
        """Test float data type mismatch."""
        metadata = ColumnMetadata("col1", "float")
        data_series = pd.Series(["text", "more text"])  # Non-numeric data

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "not numeric" in result.rationale

    def test_datetime_data_type_mismatch(self):
        """Test datetime data type mismatch."""
        metadata = ColumnMetadata("col1", "datetime")
        data_series = pd.Series(["not-a-date", "invalid-date"])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "cannot be parsed as datetime" in result.rationale

    def test_datetime_validation_with_valid_dates(self):
        """Test datetime validation with valid dates."""
        metadata = ColumnMetadata("col1", "datetime")
        data_series = pd.Series(["2023-01-01", "2023-12-31", None])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is None  # Should pass validation

    def test_validation_with_all_null_data(self):
        """Test validation when all data is null."""
        metadata = ColumnMetadata("col1", "integer")
        data_series = pd.Series([None, None, None])

        result = check_metadata_validation_failure(metadata, data_series)

        assert result is None  # Should not fail validation for all-null data

    def test_validation_success_cases(self):
        """Test successful validation cases."""
        # Valid integer data
        metadata = ColumnMetadata("col1", "integer")
        data_series = pd.Series([1, 2, 3, None])
        result = check_metadata_validation_failure(metadata, data_series)
        assert result is None

        # Valid string data
        metadata = ColumnMetadata("col2", "string")
        data_series = pd.Series(["a", "b", "c"])
        result = check_metadata_validation_failure(metadata, data_series)
        assert result is None

        # Valid constraints
        metadata = ColumnMetadata("col3", "float", min_value=0.0, max_value=10.0)
        data_series = pd.Series([1.0, 2.0, 3.0])
        result = check_metadata_validation_failure(metadata, data_series)
        assert result is None


def create_missingness_analysis(missing_count, missing_percentage, mechanism):
    """Helper to create MissingnessAnalysis with all required fields."""
    return MissingnessAnalysis(
        missing_count=missing_count,
        missing_percentage=missing_percentage,
        mechanism=mechanism,
        test_statistic=0.1 if mechanism != MissingnessMechanism.UNKNOWN else None,
        p_value=0.9 if mechanism != MissingnessMechanism.UNKNOWN else None,
        related_columns=[],
        rationale=f"{mechanism.value} mechanism detected",
    )


class TestNoMissingValues:
    """Test check_no_missing_values function."""

    def test_no_missing_values_detected(self):
        """Test when no missing values are detected."""
        missingness_analysis = create_missingness_analysis(
            0, 0.0, MissingnessMechanism.MCAR
        )

        result = check_no_missing_values(missingness_analysis)

        assert result is not None
        assert result.method == ImputationMethod.NO_ACTION_NEEDED
        assert "No missing values detected" in result.rationale
        assert result.confidence == 1.0

    def test_missing_values_present(self):
        """Test when missing values are present."""
        missingness_analysis = create_missingness_analysis(
            5, 0.25, MissingnessMechanism.MCAR
        )

        result = check_no_missing_values(missingness_analysis)
        assert result is None


class TestUniqueIdentifier:
    """Test check_unique_identifier function."""

    def test_unique_identifier_true(self):
        """Test when column is marked as unique identifier."""
        metadata = ColumnMetadata("id", "integer", unique_flag=True)

        result = check_unique_identifier(metadata)

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL
        assert "Unique IDs cannot be auto-imputed" in result.rationale
        assert result.confidence == 0.9

    def test_unique_identifier_false(self):
        """Test when column is not marked as unique identifier."""
        metadata = ColumnMetadata("age", "integer", unique_flag=False)

        result = check_unique_identifier(metadata)
        assert result is None

    def test_unique_identifier_none(self):
        """Test when unique_flag is None (default)."""
        metadata = ColumnMetadata(
            "age", "integer"
        )  # unique_flag defaults to None/False

        result = check_unique_identifier(metadata)
        assert result is None


class TestAllValuesMissing:
    """Test check_all_values_missing function."""

    def test_all_values_missing(self):
        """Test when all values in column are missing."""
        data_series = pd.Series([None, None, None, None])
        missingness_analysis = create_missingness_analysis(
            4, 1.0, MissingnessMechanism.UNKNOWN
        )

        result = check_all_values_missing(data_series, missingness_analysis)

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL
        assert "No observed values to base imputation" in result.rationale
        assert result.confidence == 0.8

    def test_partial_values_missing(self):
        """Test when only some values are missing."""
        data_series = pd.Series([1, None, 3, None])
        missingness_analysis = create_missingness_analysis(
            2, 0.5, MissingnessMechanism.MCAR
        )

        result = check_all_values_missing(data_series, missingness_analysis)
        assert result is None

    def test_empty_series_edge_case(self):
        """Test with empty series."""
        data_series = pd.Series([])
        missingness_analysis = create_missingness_analysis(
            0, 0.0, MissingnessMechanism.MCAR
        )

        result = check_all_values_missing(data_series, missingness_analysis)
        assert result is None  # Empty series should not trigger this check


class TestMNARWithoutBusinessRule:
    """Test check_mnar_without_business_rule function."""

    def test_mnar_without_business_rule(self):
        """Test MNAR mechanism without business rule."""
        missingness_analysis = create_missingness_analysis(
            5, 0.3, MissingnessMechanism.MNAR
        )
        metadata = ColumnMetadata("col1", "integer")  # No business rule

        result = check_mnar_without_business_rule(missingness_analysis, metadata)

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL
        assert "MNAR/Unknown mechanism detected with no domain rule" in result.rationale
        assert result.confidence == 0.7

    def test_unknown_without_business_rule(self):
        """Test UNKNOWN mechanism without business rule."""
        missingness_analysis = create_missingness_analysis(
            3, 0.2, MissingnessMechanism.UNKNOWN
        )
        metadata = ColumnMetadata("col1", "string")  # No business rule

        result = check_mnar_without_business_rule(missingness_analysis, metadata)

        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL
        assert "MNAR/Unknown mechanism detected with no domain rule" in result.rationale

    def test_mnar_with_business_rule(self):
        """Test MNAR mechanism with business rule."""
        missingness_analysis = create_missingness_analysis(
            5, 0.3, MissingnessMechanism.MNAR
        )
        metadata = ColumnMetadata("col1", "integer", business_rule="Some business rule")

        result = check_mnar_without_business_rule(missingness_analysis, metadata)
        assert result is None

    def test_other_mechanisms(self):
        """Test with other mechanisms (MCAR, MAR)."""
        missingness_analysis = create_missingness_analysis(
            3, 0.2, MissingnessMechanism.MCAR
        )
        metadata = ColumnMetadata("col1", "integer")

        result = check_mnar_without_business_rule(missingness_analysis, metadata)
        assert result is None


class TestNullableViolation:
    """Test check_nullable_violation function."""

    def test_nullable_false_with_missing_values(self):
        """Test nullable=False but has missing values."""
        missingness_analysis = create_missingness_analysis(
            3, 0.3, MissingnessMechanism.MCAR
        )
        metadata = ColumnMetadata("col1", "integer", nullable=False)

        result = check_nullable_violation(missingness_analysis, metadata)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "nullable=False but contains 3 missing values" in result.rationale
        assert result.confidence == 0.0

    def test_nullable_false_no_missing_values(self):
        """Test nullable=False with no missing values."""
        missingness_analysis = create_missingness_analysis(
            0, 0.0, MissingnessMechanism.MCAR
        )
        metadata = ColumnMetadata("col1", "integer", nullable=False)

        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is None

    def test_nullable_true(self):
        """Test nullable=True (should not trigger violation)."""
        missingness_analysis = create_missingness_analysis(
            3, 0.3, MissingnessMechanism.MCAR
        )
        metadata = ColumnMetadata("col1", "integer", nullable=True)

        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is None

    def test_nullable_none_default(self):
        """Test nullable=None (default, should not trigger violation)."""
        missingness_analysis = create_missingness_analysis(
            3, 0.3, MissingnessMechanism.MCAR
        )
        metadata = ColumnMetadata("col1", "integer")  # nullable defaults to None

        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is None


class TestAllowedValuesViolation:
    """Test check_allowed_values_violation function."""

    def test_allowed_values_violation(self):
        """Test values that violate allowed_values constraint."""
        data_series = pd.Series(["A", "B", "C", "X", "Y"])  # X, Y not allowed
        metadata = ColumnMetadata("col1", "string", allowed_values="A,B,C")

        result = check_allowed_values_violation(data_series, metadata)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "contains invalid values" in result.rationale
        assert "['X', 'Y']" in result.rationale
        assert "Allowed: ['A', 'B', 'C']" in result.rationale

    def test_allowed_values_violation_with_nulls(self):
        """Test allowed_values violation with null values present."""
        data_series = pd.Series(["A", "B", None, "X", None])  # X not allowed
        metadata = ColumnMetadata("col1", "string", allowed_values="A,B,C")

        result = check_allowed_values_violation(data_series, metadata)

        assert result is not None
        assert "invalid values: ['X']" in result.rationale

    def test_allowed_values_valid(self):
        """Test values that comply with allowed_values constraint."""
        data_series = pd.Series(["A", "B", "C", "A", "B"])
        metadata = ColumnMetadata("col1", "string", allowed_values="A,B,C")

        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

    def test_allowed_values_none(self):
        """Test when allowed_values is None."""
        data_series = pd.Series(["A", "B", "X", "Y"])
        metadata = ColumnMetadata("col1", "string", allowed_values=None)

        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

    def test_allowed_values_empty_string(self):
        """Test when allowed_values is empty string."""
        data_series = pd.Series(["A", "B"])
        metadata = ColumnMetadata("col1", "string", allowed_values="")

        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

    def test_allowed_values_whitespace_handling(self):
        """Test allowed_values with whitespace handling."""
        data_series = pd.Series(["A", "B", "C"])
        metadata = ColumnMetadata(
            "col1", "string", allowed_values="A, B , C,"
        )  # Extra spaces

        result = check_allowed_values_violation(data_series, metadata)
        assert result is None  # Should handle whitespace properly

    def test_allowed_values_many_invalid_values(self):
        """Test with many invalid values (should limit output)."""
        invalid_values = [f"invalid_{i}" for i in range(10)]
        data_series = pd.Series(["A"] + invalid_values)
        metadata = ColumnMetadata("col1", "string", allowed_values="A,B,C")

        result = check_allowed_values_violation(data_series, metadata)

        assert result is not None
        # Should limit to first 5 invalid values
        rationale_invalid_count = result.rationale.count("invalid_")
        assert rationale_invalid_count <= 5

    def test_allowed_values_all_null_data(self):
        """Test allowed_values check with all null data."""
        data_series = pd.Series([None, None, None])
        metadata = ColumnMetadata("col1", "string", allowed_values="A,B,C")

        result = check_allowed_values_violation(data_series, metadata)
        assert result is None  # No non-null data to validate


class TestMaxLengthViolation:
    """Test check_max_length_violation function."""

    def test_max_length_violation(self):
        """Test values that exceed max_length constraint."""
        data_series = pd.Series(
            ["short", "this_is_too_long", "ok"]
        )  # 'this_is_too_long' = 16 chars
        metadata = ColumnMetadata("col1", "string", max_length=10)

        result = check_max_length_violation(data_series, metadata)

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert (
            "max_length=10 but contains values up to 16 characters" in result.rationale
        )
        assert result.confidence == 0.0

    def test_max_length_violation_categorical(self):
        """Test max_length violation for categorical data."""
        data_series = pd.Series(["A", "very_long_category_name", "B"])
        metadata = ColumnMetadata("col1", "categorical", max_length=5)

        result = check_max_length_violation(data_series, metadata)

        assert result is not None
        assert "max_length=5" in result.rationale

    def test_max_length_valid(self):
        """Test values that comply with max_length constraint."""
        data_series = pd.Series(["short", "ok", "valid"])
        metadata = ColumnMetadata("col1", "string", max_length=10)

        result = check_max_length_violation(data_series, metadata)
        assert result is None

    def test_max_length_none(self):
        """Test when max_length is None."""
        data_series = pd.Series(["any_length_should_be_fine", "really_long_text"])
        metadata = ColumnMetadata("col1", "string", max_length=None)

        result = check_max_length_violation(data_series, metadata)
        assert result is None

    def test_max_length_non_string_type(self):
        """Test max_length check on non-string data type."""
        data_series = pd.Series([1, 2, 3, 100000])  # Numeric data
        metadata = ColumnMetadata(
            "col1", "integer", max_length=3
        )  # Should not apply to integers

        result = check_max_length_violation(data_series, metadata)
        assert result is None  # Should not check max_length for non-string types

    def test_max_length_with_nulls(self):
        """Test max_length check with null values."""
        data_series = pd.Series(["short", None, "this_is_too_long"])
        metadata = ColumnMetadata("col1", "string", max_length=10)

        result = check_max_length_violation(data_series, metadata)

        assert result is not None  # Should still detect the violation
        assert "max_length=10" in result.rationale

    def test_max_length_all_null_data(self):
        """Test max_length check with all null data."""
        data_series = pd.Series([None, None, None])
        metadata = ColumnMetadata("col1", "string", max_length=5)

        result = check_max_length_violation(data_series, metadata)
        assert result is None  # No non-null data to validate


class TestApplyExceptionHandling:
    """Test apply_exception_handling function."""

    def test_apply_exception_handling_priority_order(self):
        """Test that exceptions are applied in correct priority order."""
        # Create data that would trigger multiple exceptions
        data_series = pd.Series([None, None, None])  # All missing
        metadata = ColumnMetadata("col1", "integer", unique_flag=True, nullable=False)
        missingness_analysis = create_missingness_analysis(
            3, 1.0, MissingnessMechanism.UNKNOWN
        )
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers",
        )
        config = AnalysisConfig()

        result = apply_exception_handling(
            "col1",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Should return unique identifier exception (higher priority than nullable violation)
        assert result is not None
        assert result.method == ImputationMethod.MANUAL_BACKFILL
        assert "Unique IDs cannot be auto-imputed" in result.rationale

    def test_apply_exception_handling_skip_column(self):
        """Test apply_exception_handling when column should be skipped."""
        data_series = pd.Series([1, 2, None])
        metadata = ColumnMetadata("skip_me", "integer")
        missingness_analysis = create_missingness_analysis(
            1, 0.33, MissingnessMechanism.MCAR
        )
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers",
        )
        config = AnalysisConfig(skip_columns=["skip_me"])

        result = apply_exception_handling(
            "skip_me",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is None  # Should return None for skipped columns

    def test_apply_exception_handling_no_exceptions(self):
        """Test apply_exception_handling when no exceptions apply."""
        data_series = pd.Series([1, 2, None, 4, 5])
        metadata = ColumnMetadata("normal_col", "integer")
        missingness_analysis = create_missingness_analysis(
            1, 0.2, MissingnessMechanism.MCAR
        )
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers",
        )
        config = AnalysisConfig()

        result = apply_exception_handling(
            "normal_col",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is None  # No exceptions should apply

    def test_apply_exception_handling_metadata_validation_failure(self):
        """Test metadata validation failure takes priority."""
        data_series = pd.Series([1, 2, 3])
        metadata = ColumnMetadata("col1", "invalid_type")  # Invalid data type
        missingness_analysis = create_missingness_analysis(
            0, 0.0, MissingnessMechanism.MCAR
        )
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers",
        )
        config = AnalysisConfig()

        result = apply_exception_handling(
            "col1",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "Invalid data type" in result.rationale


class TestShouldSkipColumn:
    """Test should_skip_column function."""

    def test_should_skip_column_true(self):
        """Test should_skip_column returns True for skipped columns."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        assert should_skip_column("col1", config) is True
        assert should_skip_column("col2", config) is True

    def test_should_skip_column_false(self):
        """Test should_skip_column returns False for non-skipped columns."""
        config = AnalysisConfig(skip_columns=["col1", "col2"])

        assert should_skip_column("col3", config) is False
        assert should_skip_column("different_col", config) is False

    def test_should_skip_column_empty_list(self):
        """Test should_skip_column with empty skip list."""
        config = AnalysisConfig(skip_columns=[])

        assert should_skip_column("any_col", config) is False
        assert should_skip_column("another_col", config) is False
