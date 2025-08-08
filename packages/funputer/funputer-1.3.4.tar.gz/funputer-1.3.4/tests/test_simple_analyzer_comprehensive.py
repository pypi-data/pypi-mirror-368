#!/usr/bin/env python3
"""
Comprehensive tests for simple_analyzer.py to increase coverage.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

from funputer.simple_analyzer import (
    SimpleImputationAnalyzer,
    analyze_imputation_requirements,
)
from funputer.models import (
    ColumnMetadata,
    AnalysisConfig,
    ImputationSuggestion,
    ImputationMethod,
    MissingnessType,
)


class TestSimpleImputationAnalyzer:
    """Comprehensive tests for SimpleImputationAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = AnalysisConfig()
        self.analyzer = SimpleImputationAnalyzer(self.config)

        # Create sample data
        self.sample_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "age": [25, None, 35, 45, 30],
                "name": ["Alice", "Bob", None, "David", "Eve"],
                "score": [85.5, 92.0, None, 78.5, 88.0],
                "category": ["A", "B", "A", None, "B"],
                "all_missing": [None, None, None, None, None],
                "no_missing": [1, 2, 3, 4, 5],
            }
        )

        self.sample_metadata = [
            ColumnMetadata(column_name="id", data_type="integer", unique_flag=True),
            ColumnMetadata(column_name="age", data_type="integer"),
            ColumnMetadata(column_name="name", data_type="string"),
            ColumnMetadata(column_name="score", data_type="float"),
            ColumnMetadata(column_name="category", data_type="categorical"),
            ColumnMetadata(column_name="all_missing", data_type="string"),
            ColumnMetadata(column_name="no_missing", data_type="integer"),
        ]

    def test_init_with_config(self):
        """Test analyzer initialization with config."""
        config = AnalysisConfig(iqr_multiplier=2.0, outlier_percentage_threshold=0.1)
        analyzer = SimpleImputationAnalyzer(config)
        assert analyzer.config.iqr_multiplier == 2.0
        assert analyzer.config.outlier_threshold == 0.1

    def test_init_without_config(self):
        """Test analyzer initialization without config."""
        analyzer = SimpleImputationAnalyzer()
        assert analyzer.config is not None
        assert analyzer.config.iqr_multiplier == 1.5  # Default

    def test_analyze_dataframe_basic(self):
        """Test basic dataframe analysis."""
        suggestions = self.analyzer.analyze_dataframe(
            self.sample_data, self.sample_metadata
        )

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Check that we get suggestions for columns with missing data
        suggestion_columns = [s.column_name for s in suggestions]
        assert "age" in suggestion_columns
        assert "name" in suggestion_columns
        assert "score" in suggestion_columns
        assert "category" in suggestion_columns

    def test_analyze_dataframe_no_metadata(self):
        """Test dataframe analysis without explicit metadata (uses auto-inference)."""
        # analyze_dataframe now requires metadata, but we can auto-infer it
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(
            self.sample_data, warn_user=False
        )

        suggestions = self.analyzer.analyze_dataframe(
            self.sample_data, inferred_metadata
        )

        assert isinstance(suggestions, list)
        # Should still work with inferred metadata
        assert len(suggestions) > 0

    def test_analyze_column_numeric_with_missing(self):
        """Test analysis of numeric column with missing values."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"test_col": [1, 2, None, 4, 5]})
        metadata = [ColumnMetadata(column_name="test_col", data_type="integer")]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert isinstance(suggestion, ImputationSuggestion)
        assert suggestion.column_name == "test_col"
        assert suggestion.missing_count == 1
        assert suggestion.missing_percentage == 0.2  # 20% as decimal
        assert suggestion.proposed_method in ["Median", "Mean"]

    def test_analyze_column_categorical_with_missing(self):
        """Test analysis of categorical column with missing values."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"cat_col": ["A", "B", None, "A", "B"]})
        metadata = [ColumnMetadata(column_name="cat_col", data_type="categorical")]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert isinstance(suggestion, ImputationSuggestion)
        assert suggestion.column_name == "cat_col"
        assert suggestion.missing_count == 1
        assert suggestion.proposed_method == "Mode"

    def test_analyze_column_no_missing_values(self):
        """Test analysis of column with no missing values."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"complete_col": [1, 2, 3, 4, 5]})
        metadata = [ColumnMetadata(column_name="complete_col", data_type="integer")]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == "complete_col"
        assert suggestion.missing_count == 0
        assert suggestion.proposed_method == "No action needed"

    def test_analyze_column_all_missing(self):
        """Test analysis of column with all missing values."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"empty_col": [None, None, None]})
        metadata = [ColumnMetadata(column_name="empty_col", data_type="string")]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == "empty_col"
        assert suggestion.missing_count == 3
        assert suggestion.missing_percentage == 1.0  # 100% as decimal
        assert (
            "all values missing" in suggestion.rationale.lower()
            or "Manual" in suggestion.proposed_method
        )

    def test_analyze_column_unique_identifier(self):
        """Test analysis of unique identifier column."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"id_col": [1, 2, None, 4, 5]})
        metadata = [
            ColumnMetadata(column_name="id_col", data_type="integer", unique_flag=True)
        ]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == "id_col"
        assert (
            "unique" in suggestion.rationale.lower()
            or "identifier" in suggestion.rationale.lower()
        )

    def test_analyze_column_with_outliers(self):
        """Test analysis of column with outliers."""
        # Create data with clear outliers
        df = pd.DataFrame({"outlier_col": [1, 2, 3, 100, 5, None]})
        metadata = [ColumnMetadata(column_name="outlier_col", data_type="integer")]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == "outlier_col"
        assert suggestion.outlier_count >= 1
        assert suggestion.outlier_percentage > 0

    def test_analyze_with_enhanced_metadata_fields(self):
        """Test analysis with enhanced metadata fields."""
        # Convert series to dataframe for analysis
        df = pd.DataFrame({"enhanced_col": [1, 2, None, 4, 5]})
        metadata = [
            ColumnMetadata(
                column_name="enhanced_col",
                data_type="integer",
                role="target",
                do_not_impute=True,
                sentinel_values="-999",
                meaning_of_missing="refused_to_answer",
            )
        ]

        suggestions = self.analyzer.analyze_dataframe(df, metadata)

        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.column_name == "enhanced_col"
        # Test verifies enhanced metadata fields are processed successfully
        # The fact that we get a suggestion shows the enhanced metadata was accepted
        assert suggestion.confidence_score >= 0.0
        assert suggestion.proposed_method in [
            "Mean",
            "Mode",
            "Median",
            "Business Rule",
            "Manual Backfill",
        ]

    @patch("funputer.simple_analyzer.logger")
    def test_analyze_with_logging(self, mock_logger):
        """Test that analysis generates appropriate log messages."""
        suggestions = self.analyzer.analyze_dataframe(
            self.sample_data, self.sample_metadata
        )

        # Verify logging was called
        assert mock_logger.info.called or mock_logger.debug.called

    def test_analyze_empty_dataframe(self):
        """Test analysis of empty dataframe."""
        empty_df = pd.DataFrame()

        # Empty dataframe should return empty suggestions list, not raise exception
        suggestions = self.analyzer.analyze_dataframe(empty_df, [])
        assert isinstance(suggestions, list)
        assert len(suggestions) == 0

    def test_analyze_dataframe_with_skip_columns(self):
        """Test analysis with skip_columns configuration."""
        config = AnalysisConfig(skip_columns=["age", "name"])
        analyzer = SimpleImputationAnalyzer(config)

        suggestions = analyzer.analyze_dataframe(self.sample_data, self.sample_metadata)
        suggestion_columns = [s.column_name for s in suggestions]

        # Should not include skipped columns
        assert "age" not in suggestion_columns
        assert "name" not in suggestion_columns
        assert "score" in suggestion_columns  # Not skipped

    def test_analyze_with_high_missing_threshold(self):
        """Test analysis with high missing threshold."""
        config = AnalysisConfig(missing_threshold=0.5)  # 50% threshold
        analyzer = SimpleImputationAnalyzer(config)

        # Create data with 60% missing
        high_missing_data = pd.DataFrame(
            {"col1": [1, None, None, None, None, 6]}  # 66% missing
        )
        metadata = [ColumnMetadata(column_name="col1", data_type="integer")]

        suggestions = analyzer.analyze_dataframe(high_missing_data, metadata)

        # Should handle high missing percentage appropriately
        assert len(suggestions) > 0
        suggestion = suggestions[0]
        # missing_percentage is a decimal (0-1), not percentage (0-100)
        assert suggestion.missing_percentage > 0.5  # 50%


class TestAnalyzeImputationRequirements:
    """Test the main analyze_imputation_requirements function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create test CSV file
        self.test_csv = os.path.join(self.temp_dir, "test_data.csv")
        test_data = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "age": [25, None, 35, 45, 30],
                "name": ["Alice", "Bob", None, "David", "Eve"],
                "score": [85.5, 92.0, None, 78.5, 88.0],
            }
        )
        test_data.to_csv(self.test_csv, index=False)

        # Create test metadata file
        self.test_metadata = os.path.join(self.temp_dir, "metadata.csv")
        metadata_data = pd.DataFrame(
            {
                "column_name": ["id", "age", "name", "score"],
                "data_type": ["integer", "integer", "string", "float"],
                "nullable": [False, True, True, True],
                "unique_flag": [True, False, False, False],
            }
        )
        metadata_data.to_csv(self.test_metadata, index=False)

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_with_data_path_only(self):
        """Test analysis with only data path (auto-inference)."""
        suggestions = analyze_imputation_requirements(data_path=self.test_csv)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Should have suggestions for columns with missing data
        suggestion_columns = [s.column_name for s in suggestions]
        assert "age" in suggestion_columns
        assert "name" in suggestion_columns
        assert "score" in suggestion_columns

    def test_analyze_with_data_and_metadata_paths(self):
        """Test analysis with both data and metadata paths."""
        suggestions = analyze_imputation_requirements(
            data_path=self.test_csv, metadata_path=self.test_metadata
        )

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Verify suggestions use provided metadata
        for suggestion in suggestions:
            assert suggestion.column_name in ["id", "age", "name", "score"]

    def test_analyze_with_config_path(self):
        """Test analysis with config object (simple analyzer version)."""
        # Create config object instead of file path
        config = AnalysisConfig(
            iqr_multiplier=2.0,
            outlier_percentage_threshold=0.1,  # Use alias for outlier_threshold
            missing_percentage_threshold=0.9,  # Use alias for missing_threshold
        )

        suggestions = analyze_imputation_requirements(
            data_path=self.test_csv, config=config
        )

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_analyze_file_not_found(self):
        """Test analysis with non-existent file."""
        with pytest.raises(Exception):
            analyze_imputation_requirements(data_path="/nonexistent/file.csv")

    def test_analyze_invalid_metadata_path(self):
        """Test analysis with invalid metadata path."""
        with pytest.raises(Exception):
            analyze_imputation_requirements(
                data_path=self.test_csv, metadata_path="/nonexistent/metadata.csv"
            )

    @patch("funputer.simple_analyzer.logger")
    def test_analyze_with_verbose_logging(self, mock_logger):
        """Test analysis generates verbose logging."""
        suggestions = analyze_imputation_requirements(data_path=self.test_csv)

        # Should generate log messages
        assert mock_logger.info.called or mock_logger.debug.called

    def test_analyze_returns_correct_format(self):
        """Test that analysis returns correctly formatted suggestions."""
        suggestions = analyze_imputation_requirements(data_path=self.test_csv)

        for suggestion in suggestions:
            assert isinstance(suggestion, ImputationSuggestion)
            assert hasattr(suggestion, "column_name")
            assert hasattr(suggestion, "proposed_method")
            assert hasattr(suggestion, "confidence_score")
            assert hasattr(suggestion, "rationale")
            assert hasattr(suggestion, "missing_count")
            assert hasattr(suggestion, "missing_percentage")

    def test_analyze_dataframe_through_analyzer(self):
        """Test dataframe analysis through analyzer class."""
        df = pd.read_csv(self.test_csv)
        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(df, warn_user=False)

        suggestions = analyzer.analyze_dataframe(df, inferred_metadata)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        suggestion_columns = [s.column_name for s in suggestions]
        assert "age" in suggestion_columns
        assert "name" in suggestion_columns
        assert "score" in suggestion_columns


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_analyze_with_special_characters(self):
        """Test analysis with special characters in data."""
        data = pd.DataFrame({"special_col": ["café", "naïve", None, "résumé", "中文"]})

        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(data, warn_user=False)

        suggestions = analyzer.analyze_dataframe(data, inferred_metadata)

        assert len(suggestions) == 1
        assert suggestions[0].column_name == "special_col"

    def test_analyze_with_very_large_values(self):
        """Test analysis with very large numeric values."""
        data = pd.DataFrame({"large_col": [1e10, 1e11, None, 1e12, 1e13]})

        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(data, warn_user=False)

        suggestions = analyzer.analyze_dataframe(data, inferred_metadata)

        assert len(suggestions) == 1
        assert suggestions[0].column_name == "large_col"

    def test_analyze_with_datetime_data(self):
        """Test analysis with datetime data."""
        data = pd.DataFrame(
            {
                "date_col": pd.to_datetime(
                    ["2023-01-01", "2023-01-02", None, "2023-01-04", "2023-01-05"]
                )
            }
        )

        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(data, warn_user=False)

        suggestions = analyzer.analyze_dataframe(data, inferred_metadata)

        assert len(suggestions) == 1
        assert suggestions[0].column_name == "date_col"

    def test_analyze_with_mixed_types_column(self):
        """Test analysis with mixed data types in column."""
        data = pd.DataFrame({"mixed_col": [1, "text", None, 3.14, True]})

        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(data, warn_user=False)

        # Should handle mixed types gracefully
        suggestions = analyzer.analyze_dataframe(data, inferred_metadata)

        assert len(suggestions) == 1
        assert suggestions[0].column_name == "mixed_col"

    def test_analyze_single_row_dataframe(self):
        """Test analysis with single row dataframe."""
        data = pd.DataFrame({"single_col": [None]})

        analyzer = SimpleImputationAnalyzer()

        # Auto-infer metadata for the analysis
        from funputer.metadata_inference import infer_metadata_from_dataframe

        inferred_metadata = infer_metadata_from_dataframe(data, warn_user=False)

        suggestions = analyzer.analyze_dataframe(data, inferred_metadata)

        assert len(suggestions) == 1
        assert suggestions[0].missing_percentage == 1.0  # 100% as decimal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
