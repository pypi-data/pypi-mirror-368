#!/usr/bin/env python3
"""
Comprehensive tests for models.py to increase coverage.
"""

import pytest
from pydantic import ValidationError

from funputer.models import (
    DataType,
    MissingnessType,
    ImputationMethod,
    OutlierHandling,
    ExceptionRule,
    ColumnMetadata,
    AnalysisConfig,
    OutlierAnalysis,
    MissingnessAnalysis,
    ImputationProposal,
    ColumnAnalysis,
    ImputationSuggestion,
    DataQualityMetrics,
    MissingnessMechanism,
)


class TestEnums:
    """Test all enum classes."""

    def test_data_type_enum(self):
        """Test DataType enum values."""
        assert DataType.INTEGER.value == "integer"
        assert DataType.FLOAT.value == "float"
        assert DataType.STRING.value == "string"
        assert DataType.CATEGORICAL.value == "categorical"
        assert DataType.BOOLEAN.value == "boolean"
        assert DataType.DATETIME.value == "datetime"

        # Test enum can be used in comparisons
        assert DataType.INTEGER == DataType.INTEGER
        assert DataType.INTEGER != DataType.FLOAT

    def test_missingness_type_enum(self):
        """Test MissingnessType enum values."""
        assert MissingnessType.MCAR.value == "MCAR"
        assert MissingnessType.MAR.value == "MAR"
        assert MissingnessType.MNAR.value == "MNAR"
        assert MissingnessType.UNKNOWN.value == "Unknown"

        # Test legacy alias
        assert MissingnessMechanism == MissingnessType

    def test_imputation_method_enum(self):
        """Test ImputationMethod enum values."""
        assert ImputationMethod.MEDIAN.value == "Median"
        assert ImputationMethod.MEAN.value == "Mean"
        assert ImputationMethod.MODE.value == "Mode"
        assert ImputationMethod.REGRESSION.value == "Regression"
        assert ImputationMethod.KNN.value == "kNN"
        assert ImputationMethod.CONSTANT_MISSING.value == "Constant 'Missing'"
        assert ImputationMethod.MANUAL_BACKFILL.value == "Manual Backfill"
        assert ImputationMethod.BUSINESS_RULE.value == "Business Rule"
        assert ImputationMethod.FORWARD_FILL.value == "Forward Fill"
        assert ImputationMethod.BACKWARD_FILL.value == "Backward Fill"
        assert ImputationMethod.NO_ACTION_NEEDED.value == "No action needed"
        assert (
            ImputationMethod.ERROR_INVALID_METADATA.value == "Error: Invalid metadata"
        )

    def test_outlier_handling_enum(self):
        """Test OutlierHandling enum values."""
        assert OutlierHandling.CAP_TO_BOUNDS.value == "Cap to bounds"
        assert OutlierHandling.CONVERT_TO_NAN.value == "Convert to NaN"
        assert OutlierHandling.LEAVE_AS_IS.value == "Leave as is"
        assert OutlierHandling.REMOVE_ROWS.value == "Remove rows"

    def test_exception_rule_enum(self):
        """Test ExceptionRule enum values."""
        assert ExceptionRule.NO_MISSING_VALUES.value == "no_missing_values"
        assert ExceptionRule.UNIQUE_IDENTIFIER.value == "unique_identifier"
        assert ExceptionRule.ALL_VALUES_MISSING.value == "all_values_missing"
        assert ExceptionRule.MNAR_NO_BUSINESS_RULE.value == "mnar_no_business_rule"
        assert ExceptionRule.SKIP_COLUMN.value == "skip_column"
        assert (
            ExceptionRule.METADATA_VALIDATION_FAILURE.value
            == "metadata_validation_failure"
        )


class TestColumnMetadata:
    """Test ColumnMetadata dataclass."""

    def test_column_metadata_basic_creation(self):
        """Test basic ColumnMetadata creation."""
        metadata = ColumnMetadata(column_name="test_col", data_type="integer")

        assert metadata.column_name == "test_col"
        assert metadata.data_type == "integer"

        # Test defaults
        assert metadata.min_value is None
        assert metadata.max_value is None
        assert metadata.max_length is None
        assert metadata.unique_flag == False
        assert metadata.nullable == True
        assert metadata.description == ""
        assert metadata.dependent_column is None
        assert metadata.business_rule is None
        assert metadata.dependency_rule is None
        assert metadata.allowed_values is None

    def test_column_metadata_enhanced_fields_defaults(self):
        """Test enhanced metadata fields have correct defaults."""
        metadata = ColumnMetadata(column_name="test_col", data_type="string")

        # Enhanced fields
        assert metadata.role == "feature"
        assert metadata.do_not_impute == False
        assert metadata.sentinel_values is None
        assert metadata.meaning_of_missing is None
        assert metadata.time_index == False
        assert metadata.group_by == False
        assert metadata.order_by is None
        assert metadata.fallback_method is None
        assert metadata.policy_version == "v1.0"

    def test_column_metadata_full_creation(self):
        """Test ColumnMetadata creation with all fields."""
        metadata = ColumnMetadata(
            column_name="customer_id",
            data_type="string",
            min_value=1.0,
            max_value=1000.0,
            max_length=50,
            unique_flag=True,
            nullable=False,
            description="Unique customer identifier",
            dependent_column="user_profile",
            business_rule="Must be positive integer",
            dependency_rule="customer_id = user_profile.id",
            allowed_values="1,2,3,4,5",
            role="identifier",
            do_not_impute=True,
            sentinel_values="-999,NULL",
            meaning_of_missing="not_applicable",
            time_index=False,
            group_by=False,
            order_by="timestamp",
            fallback_method="manual",
            policy_version="v2.0",
        )

        assert metadata.column_name == "customer_id"
        assert metadata.data_type == "string"
        assert metadata.min_value == 1.0
        assert metadata.max_value == 1000.0
        assert metadata.max_length == 50
        assert metadata.unique_flag == True
        assert metadata.nullable == False
        assert metadata.description == "Unique customer identifier"
        assert metadata.dependent_column == "user_profile"
        assert metadata.business_rule == "Must be positive integer"
        assert metadata.dependency_rule == "customer_id = user_profile.id"
        assert metadata.allowed_values == "1,2,3,4,5"
        assert metadata.role == "identifier"
        assert metadata.do_not_impute == True
        assert metadata.sentinel_values == "-999,NULL"
        assert metadata.meaning_of_missing == "not_applicable"
        assert metadata.time_index == False
        assert metadata.group_by == False
        assert metadata.order_by == "timestamp"
        assert metadata.fallback_method == "manual"
        assert metadata.policy_version == "v2.0"

    def test_column_metadata_role_variations(self):
        """Test different role values."""
        roles = ["identifier", "feature", "target", "time_index", "group_by", "ignore"]

        for role in roles:
            metadata = ColumnMetadata(
                column_name=f"col_{role}", data_type="string", role=role
            )
            assert metadata.role == role

    def test_column_metadata_time_index_flag(self):
        """Test time_index flag variations."""
        metadata_time = ColumnMetadata(
            column_name="timestamp_col", data_type="datetime", time_index=True
        )
        assert metadata_time.time_index == True

        metadata_no_time = ColumnMetadata(
            column_name="regular_col", data_type="string", time_index=False
        )
        assert metadata_no_time.time_index == False

    def test_column_metadata_group_by_flag(self):
        """Test group_by flag variations."""
        metadata_group = ColumnMetadata(
            column_name="segment_col", data_type="categorical", group_by=True
        )
        assert metadata_group.group_by == True


class TestAnalysisConfig:
    """Test AnalysisConfig Pydantic model."""

    def test_analysis_config_defaults(self):
        """Test AnalysisConfig with default values."""
        config = AnalysisConfig()

        assert config.iqr_multiplier == 1.5
        assert config.outlier_threshold == 0.05
        assert config.correlation_threshold == 0.3
        assert config.chi_square_alpha == 0.05
        assert config.point_biserial_threshold == 0.2
        assert config.skewness_threshold == 2.0
        assert config.missing_threshold == 0.8
        assert config.skip_columns == []
        assert config.metadata_path is None
        assert config.data_path is None
        assert config.output_path == "imputation_suggestions.csv"
        assert config.audit_log_path == "audit_logs.jsonl"
        assert config.metrics_port == 8001

    def test_analysis_config_custom_values(self):
        """Test AnalysisConfig with custom values."""
        config = AnalysisConfig(
            iqr_multiplier=2.0,
            outlier_threshold=0.1,
            correlation_threshold=0.5,
            chi_square_alpha=0.01,
            point_biserial_threshold=0.3,
            skewness_threshold=3.0,
            missing_threshold=0.9,
            skip_columns=["id", "timestamp"],
            metadata_path="/path/to/metadata.csv",
            data_path="/path/to/data.csv",
            output_path="custom_output.csv",
            audit_log_path="custom_audit.jsonl",
            metrics_port=9001,
        )

        assert config.iqr_multiplier == 2.0
        assert config.outlier_threshold == 0.1
        assert config.correlation_threshold == 0.5
        assert config.chi_square_alpha == 0.01
        assert config.point_biserial_threshold == 0.3
        assert config.skewness_threshold == 3.0
        assert config.missing_threshold == 0.9
        assert config.skip_columns == ["id", "timestamp"]
        assert config.metadata_path == "/path/to/metadata.csv"
        assert config.data_path == "/path/to/data.csv"
        assert config.output_path == "custom_output.csv"
        assert config.audit_log_path == "custom_audit.jsonl"
        assert config.metrics_port == 9001

    def test_analysis_config_validation_iqr_multiplier(self):
        """Test AnalysisConfig IQR multiplier validation."""
        # Valid values
        config = AnalysisConfig(iqr_multiplier=1.0)
        assert config.iqr_multiplier == 1.0

        config = AnalysisConfig(iqr_multiplier=5.0)
        assert config.iqr_multiplier == 5.0

        # Invalid values should raise validation error
        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=0.05)  # Too small

        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=6.0)  # Too large

        with pytest.raises(ValidationError):
            AnalysisConfig(iqr_multiplier=-1.0)  # Negative

    def test_analysis_config_validation_outlier_threshold(self):
        """Test AnalysisConfig outlier threshold validation."""
        # Valid values
        config = AnalysisConfig(outlier_threshold=0.001)
        assert config.outlier_threshold == 0.001

        config = AnalysisConfig(outlier_threshold=0.5)
        assert config.outlier_threshold == 0.5

        # Invalid values
        with pytest.raises(ValidationError):
            AnalysisConfig(outlier_threshold=0.0005)  # Too small

        with pytest.raises(ValidationError):
            AnalysisConfig(outlier_threshold=0.6)  # Too large

    def test_analysis_config_validation_metrics_port(self):
        """Test AnalysisConfig metrics port validation."""
        # Valid values
        config = AnalysisConfig(metrics_port=8080)
        assert config.metrics_port == 8080

        config = AnalysisConfig(metrics_port=65535)
        assert config.metrics_port == 65535

        # Invalid values
        with pytest.raises(ValidationError):
            AnalysisConfig(metrics_port=80)  # Too small

        with pytest.raises(ValidationError):
            AnalysisConfig(metrics_port=70000)  # Too large

    def test_analysis_config_alias_fields(self):
        """Test AnalysisConfig field aliases."""
        # Test using alias names
        config = AnalysisConfig(
            outlier_percentage_threshold=0.1, missing_percentage_threshold=0.7
        )

        assert config.outlier_threshold == 0.1
        assert config.missing_threshold == 0.7


class TestOutlierAnalysis:
    """Test OutlierAnalysis Pydantic model."""

    def test_outlier_analysis_creation(self):
        """Test OutlierAnalysis model creation."""
        analysis = OutlierAnalysis(
            outlier_count=5,
            outlier_percentage=10.5,
            lower_bound=0.0,
            upper_bound=100.0,
            outlier_values=[150.0, 200.0, -10.0],
            handling_strategy=OutlierHandling.CAP_TO_BOUNDS,
            rationale="Values beyond IQR bounds detected",
        )

        assert analysis.outlier_count == 5
        assert analysis.outlier_percentage == 10.5
        assert analysis.lower_bound == 0.0
        assert analysis.upper_bound == 100.0
        assert analysis.outlier_values == [150.0, 200.0, -10.0]
        assert analysis.handling_strategy == OutlierHandling.CAP_TO_BOUNDS
        assert analysis.rationale == "Values beyond IQR bounds detected"

    def test_outlier_analysis_optional_fields(self):
        """Test OutlierAnalysis with optional fields."""
        analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers detected",
        )

        assert analysis.outlier_count == 0
        assert analysis.lower_bound is None
        assert analysis.upper_bound is None
        assert analysis.outlier_values == []  # Default empty list


class TestMissingnessAnalysis:
    """Test MissingnessAnalysis Pydantic model."""

    def test_missingness_analysis_creation(self):
        """Test MissingnessAnalysis model creation."""
        analysis = MissingnessAnalysis(
            missing_count=15,
            missing_percentage=25.0,
            mechanism=MissingnessType.MCAR,
            test_statistic=2.45,
            p_value=0.02,
            related_columns=["age", "income"],
            rationale="Chi-square test suggests MCAR mechanism",
        )

        assert analysis.missing_count == 15
        assert analysis.missing_percentage == 25.0
        assert analysis.mechanism == MissingnessType.MCAR
        assert analysis.test_statistic == 2.45
        assert analysis.p_value == 0.02
        assert analysis.related_columns == ["age", "income"]
        assert analysis.rationale == "Chi-square test suggests MCAR mechanism"

    def test_missingness_analysis_optional_fields(self):
        """Test MissingnessAnalysis with optional fields."""
        analysis = MissingnessAnalysis(
            missing_count=10,
            missing_percentage=20.0,
            mechanism=MissingnessType.UNKNOWN,
            related_columns=[],
            rationale="Insufficient data for mechanism determination",
        )

        assert analysis.test_statistic is None
        assert analysis.p_value is None
        assert analysis.related_columns == []


class TestImputationProposal:
    """Test ImputationProposal Pydantic model."""

    def test_imputation_proposal_creation(self):
        """Test ImputationProposal model creation."""
        proposal = ImputationProposal(
            method=ImputationMethod.MEDIAN,
            rationale="Robust against outliers",
            parameters={"value": 50.0, "strategy": "robust"},
            confidence_score=0.85,
        )

        assert proposal.method == ImputationMethod.MEDIAN
        assert proposal.rationale == "Robust against outliers"
        assert proposal.parameters == {"value": 50.0, "strategy": "robust"}
        assert proposal.confidence_score == 0.85

    def test_imputation_proposal_different_methods(self):
        """Test ImputationProposal with different methods."""
        methods = [
            ImputationMethod.MEAN,
            ImputationMethod.MODE,
            ImputationMethod.KNN,
            ImputationMethod.REGRESSION,
        ]

        for method in methods:
            proposal = ImputationProposal(
                method=method,
                rationale=f"Using {method.value} for imputation",
                parameters={},
                confidence_score=0.7,
            )
            assert proposal.method == method


class TestImputationSuggestion:
    """Test ImputationSuggestion Pydantic model."""

    def test_imputation_suggestion_creation(self):
        """Test ImputationSuggestion model creation."""
        suggestion = ImputationSuggestion(
            column_name="age",
            missing_count=10,
            missing_percentage=20.0,
            mechanism="MCAR",
            proposed_method="Median",
            rationale="Robust imputation method",
            outlier_count=2,
            outlier_percentage=4.0,
            outlier_handling="Cap to bounds",
            outlier_rationale="IQR method detected outliers",
            confidence_score=0.85,
        )

        assert suggestion.column_name == "age"
        assert suggestion.missing_count == 10
        assert suggestion.missing_percentage == 20.0
        assert suggestion.mechanism == "MCAR"
        assert suggestion.proposed_method == "Median"
        assert suggestion.rationale == "Robust imputation method"
        assert suggestion.outlier_count == 2
        assert suggestion.outlier_percentage == 4.0
        assert suggestion.outlier_handling == "Cap to bounds"
        assert suggestion.outlier_rationale == "IQR method detected outliers"
        assert suggestion.confidence_score == 0.85

    def test_imputation_suggestion_defaults(self):
        """Test ImputationSuggestion with default values."""
        suggestion = ImputationSuggestion(
            column_name="score",
            proposed_method="Mean",
            rationale="Simple average imputation",
        )

        assert suggestion.missing_count == 0
        assert suggestion.missing_percentage == 0.0
        assert suggestion.mechanism == "UNKNOWN"
        assert suggestion.outlier_count == 0
        assert suggestion.outlier_percentage == 0.0
        assert suggestion.outlier_handling == "Leave as is"
        assert suggestion.outlier_rationale == ""
        assert suggestion.confidence_score == 0.0

    def test_imputation_suggestion_to_dict(self):
        """Test ImputationSuggestion to_dict method."""
        suggestion = ImputationSuggestion(
            column_name="test_col",
            missing_count=5,
            missing_percentage=10.5,
            mechanism="MAR",
            proposed_method="Mode",
            rationale="Categorical data",
            outlier_count=1,
            outlier_percentage=2.0,
            outlier_handling="Remove rows",
            outlier_rationale="Single extreme value",
            confidence_score=0.92,
        )

        result_dict = suggestion.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["Column"] == "test_col"
        assert result_dict["Missing_Count"] == 5
        assert result_dict["Missing_Percentage"] == "10.5%"
        assert result_dict["Missingness_Mechanism"] == "MAR"
        assert result_dict["Proposed_Method"] == "Mode"
        assert result_dict["Rationale"] == "Categorical data"
        assert result_dict["Outlier_Count"] == 1
        assert result_dict["Outlier_Percentage"] == "2.0%"
        assert result_dict["Outlier_Handling"] == "Remove rows"
        assert result_dict["Outlier_Rationale"] == "Single extreme value"
        assert result_dict["Confidence_Score"] == "0.920"


class TestColumnAnalysis:
    """Test ColumnAnalysis Pydantic model."""

    def test_column_analysis_creation(self):
        """Test ColumnAnalysis model creation."""
        metadata = ColumnMetadata(column_name="test_col", data_type="float")

        outlier_analysis = OutlierAnalysis(
            outlier_count=3,
            outlier_percentage=5.0,
            handling_strategy=OutlierHandling.CAP_TO_BOUNDS,
            rationale="IQR outliers detected",
        )

        missingness_analysis = MissingnessAnalysis(
            missing_count=8,
            missing_percentage=13.3,
            mechanism=MissingnessType.MCAR,
            related_columns=[],
            rationale="Random missingness pattern",
        )

        imputation_proposal = ImputationProposal(
            method=ImputationMethod.MEDIAN,
            rationale="Robust to outliers",
            parameters={},
            confidence_score=0.88,
        )

        analysis = ColumnAnalysis(
            column_name="test_col",
            data_type="float",
            outlier_analysis=outlier_analysis,
            missingness_analysis=missingness_analysis,
            imputation_proposal=imputation_proposal,
            metadata=metadata,
            analysis_timestamp="2024-01-01T12:00:00",
            processing_duration_seconds=0.125,
        )

        assert analysis.column_name == "test_col"
        assert analysis.data_type == "float"
        assert analysis.outlier_analysis == outlier_analysis
        assert analysis.missingness_analysis == missingness_analysis
        assert analysis.imputation_proposal == imputation_proposal
        assert analysis.metadata == metadata
        assert analysis.analysis_timestamp == "2024-01-01T12:00:00"
        assert analysis.processing_duration_seconds == 0.125


class TestDataQualityMetrics:
    """Test DataQualityMetrics Pydantic model."""

    def test_data_quality_metrics_creation(self):
        """Test DataQualityMetrics model creation."""
        metrics = DataQualityMetrics(
            total_missing_values=150,
            total_outliers=25,
            data_quality_score=0.78,
            average_confidence=0.82,
            columns_analyzed=12,
            analysis_duration=45.5,
        )

        assert metrics.total_missing_values == 150
        assert metrics.total_outliers == 25
        assert metrics.data_quality_score == 0.78
        assert metrics.average_confidence == 0.82
        assert metrics.columns_analyzed == 12
        assert metrics.analysis_duration == 45.5

    def test_data_quality_metrics_defaults(self):
        """Test DataQualityMetrics with default values."""
        metrics = DataQualityMetrics(
            total_missing_values=100,
            total_outliers=10,
            data_quality_score=0.85,
            average_confidence=0.90,
        )

        assert metrics.columns_analyzed == 0
        assert metrics.analysis_duration == 0.0


class TestModelIntegration:
    """Test integration between different models."""

    def test_enum_usage_in_models(self):
        """Test that enums work properly within models."""
        # Test using enums as values
        proposal = ImputationProposal(
            method=ImputationMethod.KNN,
            rationale="K-nearest neighbors",
            parameters={"k": 5},
            confidence_score=0.75,
        )

        assert proposal.method == ImputationMethod.KNN
        assert proposal.method.value == "kNN"

    def test_nested_model_structure(self):
        """Test nested model relationships."""
        metadata = ColumnMetadata(
            column_name="complex_col",
            data_type="float",
            role="feature",
            do_not_impute=False,
        )

        # Create nested analysis
        outlier_analysis = OutlierAnalysis(
            outlier_count=0,
            outlier_percentage=0.0,
            handling_strategy=OutlierHandling.LEAVE_AS_IS,
            rationale="No outliers detected",
        )

        missingness_analysis = MissingnessAnalysis(
            missing_count=5,
            missing_percentage=10.0,
            mechanism=MissingnessType.MCAR,
            related_columns=[],
            rationale="Missing completely at random",
        )

        imputation_proposal = ImputationProposal(
            method=ImputationMethod.MEAN,
            rationale="Simple mean imputation",
            parameters={"value": 42.5},
            confidence_score=0.70,
        )

        # Combine into full analysis
        full_analysis = ColumnAnalysis(
            column_name="complex_col",
            data_type="float",
            outlier_analysis=outlier_analysis,
            missingness_analysis=missingness_analysis,
            imputation_proposal=imputation_proposal,
            metadata=metadata,
            analysis_timestamp="2024-01-01T10:00:00",
            processing_duration_seconds=0.5,
        )

        # Test that nested structure works
        assert full_analysis.metadata.role == "feature"
        assert full_analysis.imputation_proposal.method == ImputationMethod.MEAN
        assert (
            full_analysis.outlier_analysis.handling_strategy
            == OutlierHandling.LEAVE_AS_IS
        )
        assert full_analysis.missingness_analysis.mechanism == MissingnessType.MCAR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
