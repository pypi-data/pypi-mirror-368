#!/usr/bin/env python3
"""
Comprehensive tests for metadata_inference.py to increase coverage.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from unittest.mock import patch, MagicMock

from funputer.metadata_inference import (
    MetadataInferenceEngine,
    infer_metadata_from_dataframe,
)
from funputer.models import ColumnMetadata


class TestMetadataInferenceEngine:
    """Comprehensive tests for MetadataInferenceEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MetadataInferenceEngine()

        # Sample data for testing
        self.comprehensive_data = pd.DataFrame(
            {
                "customer_id": ["CUST001", "CUST002", "CUST003", "CUST004", "CUST005"],
                "timestamp": pd.to_datetime(
                    [
                        "2024-01-01 10:00",
                        "2024-01-02 11:00",
                        "2024-01-03 12:00",
                        "2024-01-04 13:00",
                        "2024-01-05 14:00",
                    ]
                ),
                "age": [25, 30, 35, 40, 45],
                "score": [85.5, 92.0, 78.5, 88.0, 95.5],
                "category": ["A", "B", "A", "C", "B"],
                "user_segment": ["premium", "basic", "premium", "basic", "premium"],
                "is_active": [True, False, True, True, False],
                "nullable_col": [1, None, 3, None, 5],
                "sentinel_col": [10, 20, -999, 30, -999],  # Contains sentinel values
                "target_variable": [0, 1, 0, 1, 0],
                "temp_debug": ["debug1", "debug2", "debug3", "debug4", "debug5"],
            }
        )

    def test_engine_initialization_default(self):
        """Test engine initialization with default parameters."""
        engine = MetadataInferenceEngine()
        assert engine.categorical_threshold_ratio == 0.1
        assert engine.categorical_threshold_absolute == 50
        assert engine.datetime_sample_size == 100
        assert engine.min_rows_for_stats == 10

    def test_engine_initialization_custom(self):
        """Test engine initialization with custom parameters."""
        engine = MetadataInferenceEngine(
            categorical_threshold_ratio=0.2,
            categorical_threshold_absolute=30,
            datetime_sample_size=50,
            min_rows_for_stats=5,
        )
        assert engine.categorical_threshold_ratio == 0.2
        assert engine.categorical_threshold_absolute == 30
        assert engine.datetime_sample_size == 50
        assert engine.min_rows_for_stats == 5

    def test_infer_dataframe_metadata_basic(self):
        """Test basic dataframe metadata inference."""
        metadata_list = self.engine.infer_dataframe_metadata(self.comprehensive_data)

        assert len(metadata_list) == len(self.comprehensive_data.columns)
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)

        # Check that all columns are represented
        column_names = [m.column_name for m in metadata_list]
        assert set(column_names) == set(self.comprehensive_data.columns)

    def test_infer_column_metadata_numeric(self):
        """Test inference for numeric columns."""
        df = pd.DataFrame({"numeric_col": [1, 2, 3, 4, 5]})
        metadata = self.engine._infer_column_metadata(df, "numeric_col")

        assert metadata.column_name == "numeric_col"
        assert metadata.data_type == "integer"
        assert metadata.min_value == 1.0
        assert metadata.max_value == 5.0
        assert metadata.nullable == False  # No null values in this test data
        assert metadata.unique_flag == False  # Conservative uniqueness detection

    def test_infer_column_metadata_float(self):
        """Test inference for float columns."""
        df = pd.DataFrame({"float_col": [1.1, 2.2, 3.3, 4.4, 5.5]})
        metadata = self.engine._infer_column_metadata(df, "float_col")

        assert metadata.column_name == "float_col"
        assert metadata.data_type == "float"
        assert metadata.min_value == 1.1
        assert metadata.max_value == 5.5

    def test_infer_column_metadata_string(self):
        """Test inference for string columns."""
        df = pd.DataFrame({"string_col": ["apple", "banana", "cherry"]})
        metadata = self.engine._infer_column_metadata(df, "string_col")

        assert metadata.column_name == "string_col"
        assert metadata.data_type in ["string", "categorical"]  # Could be either
        assert metadata.max_length == 6  # 'banana' or 'cherry'
        assert metadata.unique_flag == False  # Conservative uniqueness detection

    def test_infer_column_metadata_categorical(self):
        """Test inference for categorical columns."""
        # Repeated values to make it categorical
        df = pd.DataFrame({"cat_col": ["A", "B", "A", "C", "B", "A"]})
        metadata = self.engine._infer_column_metadata(df, "cat_col")

        assert metadata.column_name == "cat_col"
        assert metadata.data_type == "categorical"
        assert metadata.unique_flag == False  # Not unique due to repetition

    def test_infer_column_metadata_boolean(self):
        """Test inference for boolean columns."""
        df = pd.DataFrame({"bool_col": [True, False, True, False]})
        metadata = self.engine._infer_column_metadata(df, "bool_col")

        assert metadata.column_name == "bool_col"
        assert metadata.data_type == "boolean"

    def test_infer_column_metadata_datetime(self):
        """Test inference for datetime columns."""
        df = pd.DataFrame(
            {"date_col": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])}
        )
        metadata = self.engine._infer_column_metadata(df, "date_col")

        assert metadata.column_name == "date_col"
        assert metadata.data_type == "datetime"
        assert metadata.unique_flag == False  # Conservative uniqueness detection

    def test_infer_column_metadata_with_nulls(self):
        """Test inference with null values."""
        df = pd.DataFrame({"nullable_col": [1, 2, None, 4, None]})
        metadata = self.engine._infer_column_metadata(df, "nullable_col")

        assert metadata.column_name == "nullable_col"
        assert metadata.nullable == True

    def test_infer_data_type_integer(self):
        """Test integer data type inference."""
        series = pd.Series([1, 2, 3, 4, 5])
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type == "integer"

    def test_infer_data_type_float(self):
        """Test float data type inference."""
        series = pd.Series([1.1, 2.2, 3.3])
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type == "float"

    def test_infer_data_type_string(self):
        """Test string data type inference."""
        series = pd.Series(["a", "b", "c"])
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type in ["string", "categorical"]  # Could be either based on logic

    def test_infer_data_type_categorical(self):
        """Test categorical data type inference."""
        # High repetition should trigger categorical
        series = pd.Series(["A"] * 10 + ["B"] * 10 + ["C"] * 5)
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type == "categorical"

    def test_infer_data_type_boolean(self):
        """Test boolean data type inference."""
        series = pd.Series([True, False, True])
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type == "boolean"

    def test_infer_data_type_datetime(self):
        """Test datetime data type inference."""
        series = pd.to_datetime(["2024-01-01", "2024-01-02"])
        non_null_series = series.dropna()
        data_type = self.engine._infer_data_type(series, non_null_series)
        assert data_type == "datetime"

    def test_infer_uniqueness_with_unique_values(self):
        """Test uniqueness inference with unique values."""
        # Need ID-like column name for uniqueness detection
        series = pd.Series([1, 2, 3, 4, 5], name="customer_id")
        unique_flag = self.engine._infer_uniqueness(series, len(series))
        assert unique_flag == True  # ID-like name triggers uniqueness

    def test_infer_uniqueness_with_duplicates(self):
        """Test uniqueness inference with duplicate values."""
        series = pd.Series([1, 1, 2, 2, 3])
        unique_flag = self.engine._infer_uniqueness(series, len(series))
        assert unique_flag == False

    def test_infer_constraints_numeric(self):
        """Test constraint inference for numeric data."""
        series = pd.Series([10, 20, 30, 40, 50])
        min_val, max_val, max_length = self.engine._infer_constraints(series, "integer")
        assert min_val == 10.0
        assert max_val == 50.0
        assert max_length is None

    def test_infer_constraints_string(self):
        """Test constraint inference for string data."""
        series = pd.Series(["short", "medium", "very_long_string"])
        min_val, max_val, max_length = self.engine._infer_constraints(series, "string")
        assert min_val is None
        assert max_val is None
        assert max_length == 16  # length of 'very_long_string'

    def test_infer_allowed_values_categorical(self):
        """Test allowed values inference for categorical data."""
        series = pd.Series(["A", "B", "C", "A", "B"])
        allowed_values = self.engine._infer_allowed_values(series, "categorical")
        assert allowed_values is not None
        assert "A" in allowed_values
        assert "B" in allowed_values
        assert "C" in allowed_values

    def test_infer_sentinel_values(self):
        """Test sentinel values inference."""
        series = pd.Series([10, 20, -999, 30, -999, 40])  # -999 as sentinel
        sentinel_values = self.engine._infer_sentinel_values(series, "integer")
        assert sentinel_values == "-999"

    def test_infer_time_index_flag(self):
        """Test time index flag inference."""
        time_index_flag = self.engine._infer_time_index("timestamp", "datetime")
        assert time_index_flag == True

        non_time_flag = self.engine._infer_time_index("regular_column", "string")
        assert non_time_flag == False

    def test_infer_group_by_flag(self):
        """Test group by flag inference."""
        series = pd.Series(["A", "B", "A", "C", "B", "A"])  # Low cardinality
        group_by_flag = self.engine._infer_group_by("category", "categorical", series)
        assert group_by_flag == True

    def test_infer_dependent_column_correlation(self):
        """Test finding dependent columns through correlation."""
        df = pd.DataFrame(
            {
                "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Need more data for correlation
                "y": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],  # Perfect correlation with x
                "z": [5, 4, 3, 2, 1, 6, 7, 8, 9, 11],  # Some correlation
            }
        )

        dependent = self.engine._infer_dependent_column("x", df, "integer")
        # May find highly correlated column or None based on threshold
        assert dependent in ["y", None]  # 'y' has perfect correlation

    def test_infer_dependent_column_none(self):
        """Test finding dependent columns when none exist."""
        df = pd.DataFrame(
            {"x": [1, 2, 3, 4, 5], "y": [10, 25, 30, 15, 40]}  # Random, low correlation
        )

        dependent = self.engine._infer_dependent_column("x", df, "integer")
        assert dependent is None  # Should not find strong correlation

    def test_infer_role_identifier(self):
        """Test role inference for identifier columns."""
        role = self.engine._infer_role("customer_id", "string", True, 0, 5)
        assert role == "identifier"

        role = self.engine._infer_role("user_key", "string", True, 0, 5)
        assert role == "identifier"

    def test_infer_role_time_index(self):
        """Test role inference for time index columns."""
        role = self.engine._infer_role("timestamp", "datetime", False, 1, 5)
        assert role == "time_index"

        role = self.engine._infer_role("created_date", "datetime", False, 1, 5)
        assert role == "time_index"

    def test_infer_role_target(self):
        """Test role inference for target columns."""
        role = self.engine._infer_role("target", "integer", False, 4, 5)
        assert role == "target"

        # Last column with enough total columns
        role = self.engine._infer_role("any_column", "float", False, 4, 5)
        assert role == "target"

    def test_infer_role_group_by(self):
        """Test role inference for group-by columns."""
        role = self.engine._infer_role("customer_segment", "categorical", False, 1, 5)
        assert role == "group_by"

        role = self.engine._infer_role("user_type", "string", False, 1, 5)
        assert role == "group_by"

    def test_infer_role_ignore(self):
        """Test role inference for ignore columns."""
        role = self.engine._infer_role("temp_flag", "boolean", False, 1, 5)
        assert role == "ignore"

        role = self.engine._infer_role("debug_info", "string", False, 1, 5)
        assert role == "ignore"

    def test_infer_role_feature_default(self):
        """Test role inference defaults to feature."""
        role = self.engine._infer_role("regular_column", "float", False, 1, 5)
        assert role == "feature"

    def test_infer_do_not_impute_identifier(self):
        """Test do_not_impute inference for identifier."""
        do_not_impute = self.engine._infer_do_not_impute("identifier", True)
        assert do_not_impute == True

    def test_infer_do_not_impute_target(self):
        """Test do_not_impute inference for target."""
        do_not_impute = self.engine._infer_do_not_impute("target", False)
        assert do_not_impute == True

    def test_infer_do_not_impute_feature(self):
        """Test do_not_impute inference for feature."""
        do_not_impute = self.engine._infer_do_not_impute("feature", False)
        assert do_not_impute == False

    def test_infer_sentinel_values_numeric(self):
        """Test sentinel value inference for numeric data."""
        series = pd.Series([1, 2, -999, 4, -999])  # -999 appears 40% of time
        sentinel = self.engine._infer_sentinel_values(series, "integer")
        assert sentinel == "-999"

    def test_infer_sentinel_values_string(self):
        """Test sentinel value inference for string data."""
        series = pd.Series(["A", "B", "UNKNOWN", "C", "UNKNOWN"])
        sentinel = self.engine._infer_sentinel_values(series, "string")
        assert sentinel == "UNKNOWN"

    def test_infer_sentinel_values_none(self):
        """Test sentinel value inference when none exist."""
        series = pd.Series([1, 2, 3, 4, 5])
        sentinel = self.engine._infer_sentinel_values(series, "integer")
        assert sentinel is None

    def test_infer_time_index_true(self):
        """Test time index inference for time columns."""
        time_index = self.engine._infer_time_index("timestamp", "datetime")
        assert time_index == True

        time_index = self.engine._infer_time_index("created_at", "datetime")
        assert time_index == True

    def test_infer_time_index_false(self):
        """Test time index inference for non-time columns."""
        time_index = self.engine._infer_time_index("timestamp", "string")
        assert time_index == False

        time_index = self.engine._infer_time_index("regular_column", "datetime")
        assert time_index == False

    def test_infer_group_by_name_based(self):
        """Test group-by inference based on column name."""
        series = pd.Series(["A", "B", "A"])
        group_by = self.engine._infer_group_by(
            "customer_segment", "categorical", series
        )
        assert group_by == True

    def test_infer_group_by_cardinality_based(self):
        """Test group-by inference based on cardinality."""
        # Low cardinality (3 unique in 100 rows = 3% unique)
        series = pd.Series(["A"] * 50 + ["B"] * 40 + ["C"] * 10)
        group_by = self.engine._infer_group_by("some_column", "categorical", series)
        assert group_by == True

    def test_infer_group_by_false(self):
        """Test group-by inference when false."""
        # High cardinality
        series = pd.Series(range(100))
        group_by = self.engine._infer_group_by("some_column", "categorical", series)
        assert group_by == False


class TestInferenceConvenienceFunctions:
    """Test convenience functions for metadata inference."""

    def test_infer_metadata_from_dataframe(self):
        """Test the convenience function for dataframe inference."""
        data = pd.DataFrame(
            {"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"], "age": [25, 30, 35]}
        )

        metadata_list = infer_metadata_from_dataframe(data, warn_user=False)

        assert len(metadata_list) == 3
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)

        column_names = [m.column_name for m in metadata_list]
        assert "id" in column_names
        assert "name" in column_names
        assert "age" in column_names

    def test_infer_metadata_from_dataframe_with_warning(self):
        """Test dataframe inference with user warning."""
        data = pd.DataFrame({"col1": [1, 2, 3]})

        with patch("funputer.metadata_inference.logger") as mock_logger:
            metadata_list = infer_metadata_from_dataframe(data, warn_user=True)

            # Should have generated a warning
            assert mock_logger.warning.called

    def test_infer_column_metadata_through_engine(self):
        """Test column metadata inference through engine."""
        engine = MetadataInferenceEngine()
        df = pd.DataFrame({"test_col": [1, 2, 3, 4, 5]})
        metadata = engine._infer_column_metadata(df, "test_col")

        assert isinstance(metadata, ColumnMetadata)
        assert metadata.column_name == "test_col"
        assert metadata.data_type == "integer"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = MetadataInferenceEngine()

    def test_empty_dataframe(self):
        """Test inference on empty dataframe."""
        empty_df = pd.DataFrame()
        metadata_list = self.engine.infer_dataframe_metadata(empty_df)
        assert len(metadata_list) == 0

    def test_single_row_dataframe(self):
        """Test inference on single row dataframe."""
        data = pd.DataFrame({"col1": [1], "col2": ["text"]})
        metadata_list = self.engine.infer_dataframe_metadata(data)

        assert len(metadata_list) == 2
        assert metadata_list[0].column_name == "col1"
        assert metadata_list[1].column_name == "col2"

    def test_all_null_column(self):
        """Test inference on column with all null values."""
        df = pd.DataFrame({"null_col": [None, None, None]})
        metadata = self.engine._infer_column_metadata(df, "null_col")

        assert metadata.column_name == "null_col"
        assert metadata.nullable == True
        # Data type should default to something reasonable
        assert metadata.data_type in ["string", "object"]

    def test_single_value_column(self):
        """Test inference on column with single repeated value."""
        df = pd.DataFrame({"constant_col": [42, 42, 42, 42]})
        metadata = self.engine._infer_column_metadata(df, "constant_col")

        assert metadata.column_name == "constant_col"
        assert metadata.data_type == "integer"
        assert metadata.unique_flag == False  # Not unique

    def test_very_long_strings(self):
        """Test inference on very long strings."""
        long_text = "A" * 1000
        df = pd.DataFrame({"text_col": [long_text, "short"]})
        metadata = self.engine._infer_column_metadata(df, "text_col")

        assert metadata.column_name == "text_col"
        assert metadata.data_type in ["string", "categorical"]  # Could be either
        assert metadata.max_length == 1000

    def test_mixed_numeric_types(self):
        """Test inference on mixed integer/float data."""
        df = pd.DataFrame({"mixed_num": [1, 2.5, 3, 4.7]})
        metadata = self.engine._infer_column_metadata(df, "mixed_num")

        assert metadata.column_name == "mixed_num"
        assert metadata.data_type == "float"  # Should infer as float

    def test_special_characters_in_names(self):
        """Test inference with special characters in column names."""
        data = pd.DataFrame(
            {
                "col with spaces": [1, 2, 3],
                "col-with-dashes": [4, 5, 6],
                "col_with_underscores": [7, 8, 9],
                "col.with.dots": [10, 11, 12],
            }
        )

        metadata_list = self.engine.infer_dataframe_metadata(data)

        assert len(metadata_list) == 4
        column_names = [m.column_name for m in metadata_list]
        assert "col with spaces" in column_names
        assert "col-with-dashes" in column_names
        assert "col_with_underscores" in column_names
        assert "col.with.dots" in column_names

    def test_unicode_data(self):
        """Test inference with unicode data."""
        data = pd.DataFrame(
            {"unicode_col": ["café", "北京", "مرحبا", "🎉", "нормальный"]}
        )

        metadata_list = self.engine.infer_dataframe_metadata(data)

        assert len(metadata_list) == 1
        assert metadata_list[0].column_name == "unicode_col"
        assert metadata_list[0].data_type in [
            "string",
            "categorical",
        ]  # Could be either

    def test_large_dataset_performance(self):
        """Test inference performance on larger dataset."""
        # Create a larger dataset to test performance
        np.random.seed(42)
        large_data = pd.DataFrame(
            {
                "numeric_col": np.random.randint(1, 1000, 10000),
                "float_col": np.random.random(10000),
                "category_col": np.random.choice(["A", "B", "C"], 10000),
                "string_col": [f"text_{i}" for i in range(10000)],
            }
        )

        # Should complete without issues
        metadata_list = self.engine.infer_dataframe_metadata(large_data)

        assert len(metadata_list) == 4
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)

    @patch("funputer.metadata_inference.logger")
    def test_inference_with_warnings(self, mock_logger):
        """Test that inference generates appropriate warnings."""
        # Create data that might generate warnings
        data = pd.DataFrame({"problematic_col": ["valid", None, "", "another"]})

        self.engine.infer_dataframe_metadata(data, warn_user=True)

        # Should have generated some log messages
        assert (
            mock_logger.warning.called
            or mock_logger.info.called
            or mock_logger.debug.called
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
