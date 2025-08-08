"""
Tests for the simple analyzer functionality.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from funputer.simple_analyzer import (
    SimpleImputationAnalyzer,
    analyze_imputation_requirements,
    analyze_dataframe,
)
from funputer.models import (
    ColumnMetadata,
    AnalysisConfig,
    ImputationSuggestion,
    ImputationMethod,
    MissingnessType,
)


class TestSimpleImputationAnalyzer:
    """Test SimpleImputationAnalyzer class."""

    def test_analyzer_initialization_default(self):
        """Test analyzer initialization with default config."""
        analyzer = SimpleImputationAnalyzer()
        assert analyzer.config is not None
        assert isinstance(analyzer.config, AnalysisConfig)
        assert analyzer.config.iqr_multiplier == 1.5

    def test_analyzer_initialization_custom_config(self, analysis_config):
        """Test analyzer initialization with custom config."""
        analyzer = SimpleImputationAnalyzer(analysis_config)
        assert analyzer.config == analysis_config
        assert analyzer.config.iqr_multiplier == 1.5

    def test_analyze_dataframe_basic(self, sample_data, sample_metadata):
        """Test basic DataFrame analysis."""
        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(sample_data, sample_metadata)

        # Should return suggestions for all columns in metadata
        assert len(suggestions) == len(sample_metadata)
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

        # Check that column names match
        suggestion_columns = {s.column_name for s in suggestions}
        metadata_columns = {m.column_name for m in sample_metadata}
        assert suggestion_columns == metadata_columns

    def test_analyze_dataframe_with_dict_metadata(self, sample_data, sample_metadata):
        """Test DataFrame analysis with dictionary metadata."""
        metadata_dict = {meta.column_name: meta for meta in sample_metadata}
        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(sample_data, metadata_dict)

        assert len(suggestions) == len(sample_metadata)
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

    def test_analyze_dataframe_no_missing_values(self):
        """Test analysis with data that has no missing values."""
        data = pd.DataFrame({"id": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})
        metadata = [ColumnMetadata("id", "integer"), ColumnMetadata("value", "integer")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        # All suggestions should be "No action needed"
        for suggestion in suggestions:
            assert suggestion.proposed_method == "No action needed"
            assert suggestion.missing_count == 0
            assert suggestion.confidence_score == 1.0

    def test_analyze_dataframe_all_missing_values(self):
        """Test analysis with column that has all missing values."""
        data = pd.DataFrame({"id": [1, 2, 3], "all_missing": [None, None, None]})
        metadata = [
            ColumnMetadata("id", "integer"),
            ColumnMetadata("all_missing", "float"),
        ]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        # Check all_missing column suggestion
        all_missing_suggestion = next(
            s for s in suggestions if s.column_name == "all_missing"
        )
        assert all_missing_suggestion.proposed_method == "Manual Backfill"
        assert all_missing_suggestion.missing_count == 3
        assert "No observed values" in all_missing_suggestion.rationale

    def test_analyze_dataframe_unique_identifier(self):
        """Test analysis with unique identifier column."""
        data = pd.DataFrame(
            {"id": [1, None, 3, 4, None], "value": [10, 20, 30, 40, 50]}
        )
        metadata = [
            ColumnMetadata("id", "integer", unique_flag=True),
            ColumnMetadata("value", "integer"),
        ]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        # Unique ID column should suggest manual backfill
        id_suggestion = next(s for s in suggestions if s.column_name == "id")
        assert id_suggestion.proposed_method == "Manual Backfill"
        assert "Unique IDs cannot be auto-imputed" in id_suggestion.rationale

    def test_analyze_dataframe_business_rule(self):
        """Test analysis with business rule dependency."""
        data = pd.DataFrame(
            {"age": [25, 30, 35, 40, 45], "income": [50000, None, 70000, None, 90000]}
        )
        income_metadata = ColumnMetadata(
            "income",
            "float", 
            dependent_column="age",
        )
        # Add business rule dynamically
        income_metadata.business_rule = "Higher with age"
        
        metadata = [
            ColumnMetadata("age", "integer"),
            income_metadata,
        ]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        # Income should use business rule
        income_suggestion = next(s for s in suggestions if s.column_name == "income")
        assert income_suggestion.proposed_method == "Business Rule"
        assert "business rule" in income_suggestion.rationale.lower()

    def test_analyze_dataframe_skipped_columns(self, sample_data, sample_metadata):
        """Test analysis with skipped columns."""
        config = AnalysisConfig(skip_columns=["age", "income"])
        analyzer = SimpleImputationAnalyzer(config)
        suggestions = analyzer.analyze_dataframe(sample_data, sample_metadata)

        # Skipped columns should not appear in suggestions
        suggestion_columns = {s.column_name for s in suggestions}
        assert "age" not in suggestion_columns
        assert "income" not in suggestion_columns
        assert len(suggestions) == len(sample_metadata) - 2

    def test_analyze_dataframe_missing_column_in_data(self, sample_metadata):
        """Test analysis when metadata column is missing from data."""
        data = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "age": [25, 30, 35],
                # 'income' column is missing
            }
        )

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, sample_metadata)

        # Should only analyze columns present in data
        suggestion_columns = {s.column_name for s in suggestions}
        data_columns = set(data.columns)
        metadata_columns = {m.column_name for m in sample_metadata}

        # Suggestions should only include columns present in both data and metadata
        expected_columns = data_columns.intersection(metadata_columns)
        assert suggestion_columns == expected_columns

    def test_analyze_with_file_paths(self, temp_csv_files):
        """Test analyze method with file paths."""
        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze(
            temp_csv_files["metadata_path"], temp_csv_files["data_path"]
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

    def test_analyze_dataframe_empty_data(self, empty_data):
        """Test analysis with empty DataFrame."""
        metadata = [ColumnMetadata("col1", "integer")]
        analyzer = SimpleImputationAnalyzer()

        # Should handle empty data gracefully
        suggestions = analyzer.analyze_dataframe(empty_data, metadata)
        assert len(suggestions) == 0  # No columns to analyze

    def test_analyze_dataframe_single_row(self, single_row_data):
        """Test analysis with single row of data."""
        metadata = [
            ColumnMetadata("id", "integer"),
            ColumnMetadata("value", "float"),
            ColumnMetadata("category", "categorical"),
        ]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(single_row_data, metadata)

        # Should handle single row gracefully
        assert len(suggestions) == len(metadata)
        for suggestion in suggestions:
            assert suggestion.proposed_method == "No action needed"
            assert suggestion.missing_count == 0


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_analyze_imputation_requirements(self, temp_csv_files):
        """Test analyze_imputation_requirements function."""
        suggestions = analyze_imputation_requirements(
            temp_csv_files["data_path"], temp_csv_files["metadata_path"]
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

    def test_analyze_imputation_requirements_with_config(self, temp_csv_files):
        """Test analyze_imputation_requirements with custom config."""
        config = AnalysisConfig(iqr_multiplier=2.0, skewness_threshold=1.0)

        suggestions = analyze_imputation_requirements(
            temp_csv_files["data_path"], temp_csv_files["metadata_path"], config=config
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

    def test_analyze_dataframe_function(self, sample_data, sample_metadata):
        """Test analyze_dataframe convenience function."""
        suggestions = analyze_dataframe(sample_data, sample_metadata)

        assert len(suggestions) == len(sample_metadata)
        assert all(isinstance(s, ImputationSuggestion) for s in suggestions)

    def test_analyze_dataframe_function_with_config(self, sample_data, sample_metadata):
        """Test analyze_dataframe function with custom config."""
        config = AnalysisConfig(skip_columns=["date"])
        suggestions = analyze_dataframe(sample_data, sample_metadata, config=config)

        # Should skip the 'date' column
        suggestion_columns = {s.column_name for s in suggestions}
        assert "date" not in suggestion_columns
        assert len(suggestions) == len(sample_metadata) - 1


class TestAnalysisResults:
    """Test analysis results and their properties."""

    def test_categorical_data_analysis(self):
        """Test analysis of categorical data."""
        data = pd.DataFrame({"category": ["A", "B", None, "A", "C", None, "B", "A"]})
        metadata = [ColumnMetadata("category", "categorical")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        suggestion = suggestions[0]
        assert suggestion.column_name == "category"
        assert suggestion.proposed_method == "Mode"
        assert suggestion.missing_count == 2
        assert suggestion.missing_percentage == 0.25

    def test_numeric_data_analysis_normal_distribution(self):
        """Test analysis of normally distributed numeric data."""
        np.random.seed(42)
        normal_data = np.random.normal(50, 10, 100).tolist()
        normal_data[10:15] = [None] * 5  # Add some missing values

        data = pd.DataFrame({"values": normal_data})
        metadata = [ColumnMetadata("values", "float")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        suggestion = suggestions[0]
        assert suggestion.column_name == "values"
        assert (
            suggestion.proposed_method == "Mean"
        )  # Should choose mean for normal data
        assert suggestion.missing_count == 5

    def test_numeric_data_analysis_skewed_distribution(self):
        """Test analysis of highly skewed numeric data."""
        # Create highly skewed data
        skewed_data = [1] * 50 + [2] * 30 + [3] * 15 + [100, 200, 300, 400, 500]
        skewed_data[0:5] = [None] * 5  # Add missing values

        data = pd.DataFrame({"values": skewed_data})
        metadata = [ColumnMetadata("values", "float")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        suggestion = suggestions[0]
        assert suggestion.column_name == "values"
        assert (
            suggestion.proposed_method == "Median"
        )  # Should choose median for skewed data
        assert suggestion.missing_count == 5

    def test_boolean_data_analysis(self):
        """Test analysis of boolean data."""
        data = pd.DataFrame({"is_active": [True, False, None, True, None, False, True]})
        metadata = [ColumnMetadata("is_active", "boolean")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        suggestion = suggestions[0]
        assert suggestion.column_name == "is_active"
        assert suggestion.proposed_method == "Mode"
        assert suggestion.missing_count == 2

    def test_datetime_data_analysis(self):
        """Test analysis of datetime data."""
        dates = pd.date_range("2023-01-01", periods=10, freq="D").tolist()
        dates[2] = None
        dates[5] = None

        data = pd.DataFrame({"date": dates})
        metadata = [ColumnMetadata("date", "datetime")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        suggestion = suggestions[0]
        assert suggestion.column_name == "date"
        assert suggestion.proposed_method == "Forward Fill"
        assert suggestion.missing_count == 2

    def test_high_missing_percentage_analysis(self, high_missing_data):
        """Test analysis of data with very high missing percentage."""
        metadata = [
            ColumnMetadata("mostly_missing", "float"),
            ColumnMetadata("some_values", "integer"),
        ]

        config = AnalysisConfig(missing_percentage_threshold=0.5)  # 50% threshold
        analyzer = SimpleImputationAnalyzer(config)
        suggestions = analyzer.analyze_dataframe(high_missing_data, metadata)

        # Column with 80% missing should get special treatment
        mostly_missing_suggestion = next(
            s for s in suggestions if s.column_name == "mostly_missing"
        )
        assert mostly_missing_suggestion.missing_percentage == 0.8
        # Should suggest constant 'Missing' for very high missing percentage
        assert mostly_missing_suggestion.proposed_method == "Constant 'Missing'"

    def test_confidence_scores(self, sample_data, sample_metadata):
        """Test that confidence scores are reasonable."""
        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(sample_data, sample_metadata)

        for suggestion in suggestions:
            # Confidence scores should be between 0 and 1
            assert 0.0 <= suggestion.confidence_score <= 1.0

            # "No action needed" should have perfect confidence
            if suggestion.proposed_method == "No action needed":
                assert suggestion.confidence_score == 1.0

    def test_outlier_detection_integration(self, outlier_data):
        """Test that outlier detection is integrated properly."""
        metadata = [ColumnMetadata("values", "float"), ColumnMetadata("id", "integer")]

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(outlier_data, metadata)

        values_suggestion = next(s for s in suggestions if s.column_name == "values")

        # Should detect outliers
        assert values_suggestion.outlier_count > 0
        assert values_suggestion.outlier_percentage > 0
        assert values_suggestion.outlier_handling in [
            "Cap to bounds",
            "Leave as is",
            "Convert to NaN",
        ]
