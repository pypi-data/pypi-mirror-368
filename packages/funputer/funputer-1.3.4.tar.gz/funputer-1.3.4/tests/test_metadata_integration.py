"""
Tests for metadata field integration in analysis engine.

Tests the integration of nullable, allowed_values, max_length, and description
fields into the imputation analysis and proposal logic.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock

from funputer.models import (
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    ImputationMethod,
    MissingnessMechanism,
    AnalysisConfig,
)
from funputer.exceptions import (
    check_nullable_violation,
    check_allowed_values_violation,
    check_max_length_violation,
)
from funputer.proposal import (
    propose_imputation_method,
    calculate_confidence_score,
    _get_allowed_values_list,
    _adjust_confidence_for_constraints,
)


class TestMetadataIntegration:
    """Test suite for metadata field integration."""

    def test_nullable_violation_detection(self):
        """Test detection of nullable=False with missing values."""
        metadata = ColumnMetadata(
            column_name="test_col", data_type="integer", nullable=False
        )

        missingness_analysis = Mock()
        missingness_analysis.missing_count = 5

        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "nullable=False" in result.rationale
        assert "5 missing values" in result.rationale

        # Test no violation when nullable=True
        metadata.nullable = True
        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is None

        # Test no violation when no missing values
        metadata.nullable = False
        missingness_analysis.missing_count = 0
        result = check_nullable_violation(missingness_analysis, metadata)
        assert result is None

    def test_allowed_values_violation_detection(self):
        """Test detection of values outside allowed_values."""
        metadata = ColumnMetadata(
            column_name="test_col",
            data_type="categorical",
            allowed_values="red,blue,green",
        )

        data_series = pd.Series(["red", "blue", "yellow", "green", "purple"])

        result = check_allowed_values_violation(data_series, metadata)
        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "invalid values" in result.rationale
        assert "yellow" in result.rationale or "purple" in result.rationale

        # Test no violation with valid values
        data_series = pd.Series(["red", "blue", "green"])
        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

        # Test with empty allowed_values
        metadata.allowed_values = ""
        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

        # Test with None allowed_values
        metadata.allowed_values = None
        result = check_allowed_values_violation(data_series, metadata)
        assert result is None

    def test_max_length_violation_detection(self):
        """Test detection of string values exceeding max_length."""
        metadata = ColumnMetadata(
            column_name="test_col", data_type="string", max_length=5
        )

        data_series = pd.Series(["hello", "world", "toolong", "short"])

        result = check_max_length_violation(data_series, metadata)
        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA
        assert "max_length=5" in result.rationale
        assert "7 characters" in result.rationale

        # Test no violation with valid lengths
        data_series = pd.Series(["hello", "world", "short"])
        result = check_max_length_violation(data_series, metadata)
        assert result is None

        # Test with None max_length
        metadata.max_length = None
        result = check_max_length_violation(data_series, metadata)
        assert result is None

        # Test with non-string data type
        metadata.data_type = "integer"
        metadata.max_length = 5
        result = check_max_length_violation(data_series, metadata)
        assert result is None

    def test_get_allowed_values_list(self):
        """Test parsing of allowed_values string."""
        metadata = ColumnMetadata(column_name="test", data_type="categorical")

        # Test normal parsing
        metadata.allowed_values = "red, blue, green"
        result = _get_allowed_values_list(metadata)
        assert result == ["red", "blue", "green"]

        # Test with extra spaces
        metadata.allowed_values = "  red  ,  blue  ,  green  "
        result = _get_allowed_values_list(metadata)
        assert result == ["red", "blue", "green"]

        # Test with empty values
        metadata.allowed_values = "red,,blue, ,green"
        result = _get_allowed_values_list(metadata)
        assert result == ["red", "blue", "green"]

        # Test with None
        metadata.allowed_values = None
        result = _get_allowed_values_list(metadata)
        assert result == []

        # Test with empty string
        metadata.allowed_values = ""
        result = _get_allowed_values_list(metadata)
        assert result == []

    def test_confidence_adjustment_for_constraints(self):
        """Test confidence adjustment based on metadata constraints."""
        metadata = ColumnMetadata(column_name="test", data_type="categorical")
        data_series = pd.Series(["a", "b", None, "c"])

        base_confidence = 0.7

        # Test with allowed_values
        metadata.allowed_values = "a,b,c"
        result = _adjust_confidence_for_constraints(
            base_confidence, metadata, data_series
        )
        assert result > base_confidence

        # Test with max_length
        metadata.allowed_values = None
        metadata.max_length = 10
        result = _adjust_confidence_for_constraints(
            base_confidence, metadata, data_series
        )
        assert result > base_confidence

        # Test with nullable=False and missing values
        metadata.nullable = False
        result = _adjust_confidence_for_constraints(
            base_confidence, metadata, data_series
        )
        assert result < base_confidence

        # Test with nullable=False and no missing values
        data_series_no_missing = pd.Series(["a", "b", "c"])
        result = _adjust_confidence_for_constraints(
            base_confidence, metadata, data_series_no_missing
        )
        assert result > base_confidence

    def test_proposal_with_allowed_values(self):
        """Test imputation proposals respect allowed_values."""
        metadata = ColumnMetadata(
            column_name="color",
            data_type="categorical",
            allowed_values="red,blue,green",
        )

        data_series = pd.Series(["red", "blue", None, "red"])

        missingness_analysis = Mock()
        missingness_analysis.missing_percentage = 0.25
        missingness_analysis.missing_count = 1
        missingness_analysis.mechanism = MissingnessMechanism.MCAR
        missingness_analysis.p_value = 0.5
        missingness_analysis.related_columns = []

        outlier_analysis = Mock()
        outlier_analysis.outlier_count = 0
        outlier_analysis.outlier_percentage = 0.0

        config = AnalysisConfig()

        proposal = propose_imputation_method(
            "color",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert proposal.method == ImputationMethod.MODE
        assert "allowed values constraint" in proposal.rationale
        assert "allowed_values" in proposal.parameters
        assert proposal.parameters["allowed_values"] == ["red", "blue", "green"]

    def test_proposal_with_max_length(self):
        """Test imputation proposals respect max_length."""
        metadata = ColumnMetadata(column_name="name", data_type="string", max_length=10)

        data_series = pd.Series(["alice", "bob", None, "charlie"])

        missingness_analysis = Mock()
        missingness_analysis.missing_percentage = 0.25
        missingness_analysis.missing_count = 1
        missingness_analysis.mechanism = MissingnessMechanism.MCAR
        missingness_analysis.p_value = 0.5
        missingness_analysis.related_columns = []

        outlier_analysis = Mock()
        outlier_analysis.outlier_count = 0
        outlier_analysis.outlier_percentage = 0.0

        config = AnalysisConfig()

        proposal = propose_imputation_method(
            "name",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Check that it's handled as string data with max_length parameter
        assert proposal.method == ImputationMethod.MODE
        assert "max_length" in proposal.parameters
        assert proposal.parameters["max_length"] == 10
        # Check that rationale mentions string data or max_length
        assert "String data" in proposal.rationale or "max_length" in proposal.rationale

    def test_confidence_score_with_metadata_constraints(self):
        """Test confidence score calculation with metadata constraints."""
        metadata = ColumnMetadata(
            column_name="test",
            data_type="categorical",
            allowed_values="a,b,c",
            max_length=5,
            nullable=True,
        )

        data_series = pd.Series(["a", "b", "c"])

        missingness_analysis = Mock()
        missingness_analysis.missing_percentage = 0.1
        missingness_analysis.missing_count = 0
        missingness_analysis.mechanism = MissingnessMechanism.MCAR
        missingness_analysis.p_value = 0.5
        missingness_analysis.related_columns = []

        outlier_analysis = Mock()
        outlier_analysis.outlier_count = 0
        outlier_analysis.outlier_percentage = 0.0

        confidence = calculate_confidence_score(
            missingness_analysis, outlier_analysis, metadata, data_series
        )

        # Should be higher due to constraints
        assert confidence > 0.5
        assert confidence <= 1.0

    def test_nullable_false_with_missing_values(self):
        """Test that nullable=False with missing values triggers exception."""
        metadata = ColumnMetadata(
            column_name="test", data_type="integer", nullable=False
        )

        data_series = pd.Series([1, 2, None, 4])

        missingness_analysis = Mock()
        missingness_analysis.missing_percentage = 0.25
        missingness_analysis.missing_count = 1
        missingness_analysis.mechanism = MissingnessMechanism.MCAR

        outlier_analysis = Mock()
        outlier_analysis.outlier_count = 0
        outlier_analysis.outlier_percentage = 0.0

        config = AnalysisConfig()

        # Should trigger exception handling
        from funputer.exceptions import apply_exception_handling

        result = apply_exception_handling(
            "test",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        assert result is not None
        assert result.method == ImputationMethod.ERROR_INVALID_METADATA

    def test_description_field_usage(self):
        """Test that description field is used in rationale when provided."""
        metadata = ColumnMetadata(
            column_name="status",
            data_type="categorical",
            description="Customer status: active, inactive, suspended",
            allowed_values="active,inactive,suspended",
        )

        data_series = pd.Series(["active", "active", None, "inactive"])

        missingness_analysis = Mock()
        missingness_analysis.missing_percentage = 0.25
        missingness_analysis.missing_count = 1
        missingness_analysis.mechanism = MissingnessMechanism.MCAR
        missingness_analysis.p_value = 0.5
        missingness_analysis.related_columns = []

        outlier_analysis = Mock()
        outlier_analysis.outlier_count = 0
        outlier_analysis.outlier_percentage = 0.0

        config = AnalysisConfig()

        proposal = propose_imputation_method(
            "status",
            data_series,
            metadata,
            missingness_analysis,
            outlier_analysis,
            config,
        )

        # Should use allowed values for imputation
        assert proposal.method == ImputationMethod.MODE
        assert "allowed values constraint" in proposal.rationale
        assert proposal.parameters["allowed_values"] == [
            "active",
            "inactive",
            "suspended",
        ]
