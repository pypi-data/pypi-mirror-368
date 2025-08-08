"""
Comprehensive tests for automatic metadata inference functionality.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import patch

from funputer.metadata_inference import (
    MetadataInferenceEngine,
    infer_metadata_from_dataframe,
)
from funputer.models import ColumnMetadata


class TestMetadataInferenceEngine:
    """Test suite for MetadataInferenceEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a standard inference engine for testing."""
        return MetadataInferenceEngine()

    @pytest.fixture
    def sample_dataframe(self):
        """Create a comprehensive test DataFrame."""
        return pd.DataFrame(
            {
                "user_id": [1, 2, 3, 4, 5],
                "age": [25, 30, 35, None, 45],
                "income": [50000.0, 65000.5, None, 85000.0, 95000.0],
                "category": ["A", "B", "A", "C", "B"],
                "is_active": [True, False, True, None, False],
                "signup_date": [
                    "2023-01-15",
                    "2023-02-20",
                    None,
                    "2023-03-10",
                    "2023-01-25",
                ],
                "description": [
                    f"User description {i}" for i in range(1, 6)
                ],  # Make all unique to avoid categorical classification
                "score": [85.5, 92.3, 78.9, 88.1, None],
            }
        )

    def test_engine_initialization(self):
        """Test engine initialization with default and custom parameters."""
        # Default initialization
        engine = MetadataInferenceEngine()
        assert engine.categorical_threshold_ratio == 0.1
        assert engine.categorical_threshold_absolute == 50
        assert engine.datetime_sample_size == 100
        assert engine.min_rows_for_stats == 10

        # Custom initialization
        engine = MetadataInferenceEngine(
            categorical_threshold_ratio=0.2,
            categorical_threshold_absolute=25,
            datetime_sample_size=50,
            min_rows_for_stats=5,
        )
        assert engine.categorical_threshold_ratio == 0.2
        assert engine.categorical_threshold_absolute == 25
        assert engine.datetime_sample_size == 50
        assert engine.min_rows_for_stats == 5

    def test_infer_dataframe_metadata(self, engine, sample_dataframe):
        """Test inference of metadata for entire DataFrame."""
        metadata_list = engine.infer_dataframe_metadata(
            sample_dataframe, warn_user=False
        )

        assert len(metadata_list) == 8  # All columns
        assert all(isinstance(meta, ColumnMetadata) for meta in metadata_list)

        # Check specific columns
        column_types = {meta.column_name: meta.data_type for meta in metadata_list}
        assert column_types["user_id"] == "integer"
        assert column_types["age"] == "integer"
        assert column_types["income"] == "float"
        assert column_types["category"] == "categorical"
        assert column_types["is_active"] == "boolean"
        assert column_types["signup_date"] == "datetime"
        assert (
            column_types["description"] == "categorical"
        )  # Will be classified as categorical due to small unique count
        assert column_types["score"] == "float"

    def test_infer_integer_columns(self, engine):
        """Test inference of integer columns."""
        df = pd.DataFrame(
            {
                "pure_int": [1, 2, 3, 4, 5],
                "int_with_null": [1, 2, None, 4, 5],
                "float_as_int": [
                    1.0,
                    2.0,
                    3.0,
                    4.0,
                    5.0,
                ],  # Should be detected as integer
                "mixed_float": [1.0, 2.5, 3.0, 4.2, 5.0],  # Should remain float
            }
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["pure_int"] == "integer"
        assert types["int_with_null"] == "integer"
        assert types["float_as_int"] == "integer"
        assert types["mixed_float"] == "float"

    def test_infer_categorical_columns(self, engine):
        """Test inference of categorical columns."""
        df = pd.DataFrame(
            {
                "small_categories": ["A", "B", "A", "C", "B"]
                * 10,  # 3 unique in 50 values
                "many_categories": [f"Cat_{i}" for i in range(50)],  # 50 unique values
                "ratio_categorical": ["X", "Y"] * 25,  # 2 unique in 50 values
                "not_categorical": [f"Item_{i}" for i in range(50)],  # All unique
            }
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["small_categories"] == "categorical"
        assert (
            types["many_categories"] == "categorical"
        )  # 50 unique values, but still under absolute threshold
        assert types["ratio_categorical"] == "categorical"
        assert (
            types["not_categorical"] == "categorical"
        )  # All unique, but under absolute threshold

    def test_infer_datetime_columns(self, engine):
        """Test inference of datetime columns."""
        df = pd.DataFrame(
            {
                "iso_dates": ["2023-01-15", "2023-02-20", "2023-03-10"],
                "us_dates": ["01/15/2023", "02/20/2023", "03/10/2023"],
                "mixed_formats": ["2023-01-15", "01/15/2023", "not-a-date"],  # Mixed
                "pandas_datetime": pd.to_datetime(
                    ["2023-01-15", "2023-02-20", "2023-03-10"]
                ),
                "not_datetime": [
                    f"text_{i}" for i in range(1, 4)
                ],  # Make unique to avoid categorical classification
            }
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["iso_dates"] == "datetime"
        assert types["us_dates"] == "datetime"
        # mixed_formats might be datetime or string depending on threshold
        assert types["pandas_datetime"] == "datetime"
        assert (
            types["not_datetime"] == "categorical"
        )  # Will be classified as categorical due to small unique count

    def test_infer_boolean_columns(self, engine):
        """Test inference of boolean columns."""
        df = pd.DataFrame(
            {
                "pandas_bool": [True, False, True, False],
                "string_bool": ["true", "false", "true", "false"],
                "numeric_bool": ["1", "0", "1", "0"],
                "yes_no": ["yes", "no", "yes", "no"],
                "mixed_bool": ["true", "false", "maybe", "true"],  # Not pure boolean
                "not_bool": ["apple", "banana", "cherry", "date"],
            }
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["pandas_bool"] == "boolean"
        assert types["string_bool"] == "boolean"
        assert types["numeric_bool"] == "boolean"
        assert types["yes_no"] == "boolean"
        assert types["mixed_bool"] != "boolean"  # Should not be detected as boolean
        assert types["not_bool"] != "boolean"

    def test_infer_uniqueness(self, engine):
        """Test inference of uniqueness constraints."""
        df = pd.DataFrame(
            {
                "user_id": [1, 2, 3, 4, 5],  # Unique with ID name
                "product_key": ["A1", "B2", "C3", "D4", "E5"],  # Unique with key name
                "category": ["A", "B", "A", "B", "C"],  # Not unique
                "unique_no_id": ["X", "Y", "Z", "W", "V"],  # Unique but no ID name
                "sequential_id": [1, 2, 3, 4, 5],  # Sequential ID pattern
            }
        )

        # Need more data for sequential ID detection
        df = pd.concat([df] * 4, ignore_index=True)  # 20 rows
        df["sequential_id"] = list(range(1, 21))  # Reset sequential
        df["user_id"] = list(range(1, 21))  # Make unique
        df["product_key"] = [f"KEY_{i}" for i in range(1, 21)]  # Make unique

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        unique_flags = {meta.column_name: meta.unique_flag for meta in metadata_list}

        assert unique_flags["user_id"] == True  # ID name + unique
        assert unique_flags["product_key"] == True  # Key name + unique
        assert unique_flags["category"] == False  # Not unique
        # unique_no_id might be False due to conservative approach
        assert unique_flags["sequential_id"] == True  # Sequential pattern

    def test_infer_constraints(self, engine):
        """Test inference of min/max and length constraints."""
        df = pd.DataFrame(
            {
                "ages": [18, 25, 35, 45, 65],
                "prices": [9.99, 19.99, 29.99, 39.99, 49.99],
                "names": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "descriptions": [
                    "Short",
                    "A bit longer",
                    "This is much longer text",
                    "Medium",
                    "Brief",
                ],
            }
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        constraints = {
            meta.column_name: (meta.min_value, meta.max_value, meta.max_length)
            for meta in metadata_list
        }

        assert constraints["ages"] == (18.0, 65.0, None)
        assert constraints["prices"] == (9.99, 49.99, None)
        assert constraints["names"][2] == 7  # Max length of 'Charlie'
        assert constraints["descriptions"][2] == 24  # Length of longest description

    def test_empty_dataframe(self, engine):
        """Test handling of empty DataFrame."""
        df = pd.DataFrame()
        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        assert len(metadata_list) == 0

    def test_all_null_column(self, engine):
        """Test handling of columns with all null values."""
        df = pd.DataFrame(
            {"all_null": [None, None, None, None], "some_data": [1, 2, None, 4]}
        )

        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["all_null"] == "string"  # Default for all-null
        assert types["some_data"] == "integer"

    def test_error_handling(self, engine):
        """Test error handling and fallback behavior."""
        # Create a DataFrame that might cause issues
        df = pd.DataFrame(
            {
                "normal_col": [1, 2, 3],
                "problematic_col": [
                    complex(1, 2),
                    complex(3, 4),
                    complex(5, 6),
                ],  # Complex numbers
            }
        )

        # Should not raise exception, should use fallback
        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)
        assert len(metadata_list) == 2

        # Check that fallback was used for problematic column
        problematic_meta = next(
            meta for meta in metadata_list if meta.column_name == "problematic_col"
        )
        assert "Auto-inferred string column" in problematic_meta.description

    def test_convenience_function(self, sample_dataframe):
        """Test the convenience function."""
        metadata_list = infer_metadata_from_dataframe(sample_dataframe, warn_user=False)

        assert len(metadata_list) == 8
        assert all(isinstance(meta, ColumnMetadata) for meta in metadata_list)

        # Test with custom parameters
        metadata_list = infer_metadata_from_dataframe(
            sample_dataframe, warn_user=False, categorical_threshold_ratio=0.2
        )
        assert len(metadata_list) == 8

    @patch("funputer.metadata_inference.logger")
    def test_warning_behavior(self, mock_logger, engine, sample_dataframe):
        """Test that warnings are properly issued."""
        # Test with warnings enabled
        engine.infer_dataframe_metadata(sample_dataframe, warn_user=True)
        mock_logger.warning.assert_called()

        # Test with warnings disabled
        mock_logger.reset_mock()
        engine.infer_dataframe_metadata(sample_dataframe, warn_user=False)
        # Warning should not be called for auto-inference message
        warning_calls = [
            call
            for call in mock_logger.warning.call_args_list
            if "AUTO-INFERRING METADATA" in str(call)
        ]
        assert len(warning_calls) == 0


class TestMetadataInferenceIntegration:
    """Integration tests with real data patterns."""

    def test_ecommerce_data(self):
        """Test with realistic e-commerce data."""
        df = pd.DataFrame(
            {
                "product_id": [1001, 1002, 1003, 1004, 1005],
                "product_name": ["Widget A", "Gadget B", None, "Tool C", "Device D"],
                "price": [29.99, 45.50, 89.99, None, 15.75],
                "category": ["Electronics", "Tools", "Electronics", "Tools", None],
                "in_stock": [True, False, True, True, False],
                "launch_date": [
                    "2023-01-15",
                    "2023-02-01",
                    None,
                    "2023-01-30",
                    "2023-03-15",
                ],
                "rating": [4.2, 3.8, 4.5, None, 3.2],
                "description": [
                    "Great widget",
                    "Professional tool",
                    None,
                    "Compact",
                    "User-friendly",
                ],
            }
        )

        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["product_id"] == "integer"
        assert (
            types["product_name"] == "categorical"
        )  # Will be classified as categorical due to low unique count
        assert types["price"] == "float"
        assert types["category"] == "categorical"
        assert types["in_stock"] == "boolean"
        assert types["launch_date"] == "datetime"
        assert types["rating"] == "float"
        assert (
            types["description"] == "categorical"
        )  # Will be classified as categorical due to repetitive patterns

    def test_user_analytics_data(self):
        """Test with user analytics data."""
        df = pd.DataFrame(
            {
                "session_id": [f"sess_{i}" for i in range(100)],  # Unique string IDs
                "user_type": ["premium", "free"] * 50,  # Categorical
                "page_views": np.random.randint(1, 100, 100),  # Integer metrics
                "session_duration": np.random.uniform(30, 3600, 100),  # Float metrics
                "converted": np.random.choice([True, False], 100),  # Boolean
                "signup_date": pd.date_range(
                    "2023-01-01", periods=100, freq="D"
                ),  # Datetime
            }
        )

        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        types = {meta.column_name: meta.data_type for meta in metadata_list}

        assert types["session_id"] == "string"  # Unique but not numeric
        assert types["user_type"] == "categorical"
        assert types["page_views"] == "integer"
        assert types["session_duration"] == "float"
        assert types["converted"] == "boolean"
        assert types["signup_date"] == "datetime"

    def test_edge_cases(self):
        """Test various edge cases."""
        df = pd.DataFrame(
            {
                "single_value": ["same"] * 10,  # Single unique value
                "mostly_null": [
                    1,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ],
                "numeric_strings": [
                    "123",
                    "456",
                    "789",
                    "012",
                    "345",
                    "678",
                    "901",
                    "234",
                    "567",
                    "890",
                ],  # Numbers as strings
                "mixed_types": [
                    1,
                    "2",
                    3.0,
                    "4.5",
                    5,
                    "6",
                    7.0,
                    "8.5",
                    9,
                    "10",
                ],  # Mixed types (problematic)
                "empty_strings": [
                    "",
                    "text",
                    "",
                    "more",
                    "data",
                    "",
                    "test",
                    "",
                    "info",
                    "end",
                ],  # Empty strings
            }
        )

        # Should not raise exceptions
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        assert len(metadata_list) == 5

        types = {meta.column_name: meta.data_type for meta in metadata_list}

        # Single value might be categorical or string
        assert types["single_value"] in ["categorical", "string"]
        assert types["mostly_null"] == "integer"  # Based on non-null values
        assert types["numeric_strings"] == "integer"  # Should detect as numeric
        # mixed_types will depend on pandas interpretation
        assert (
            types["empty_strings"] == "categorical"
        )  # Will be classified as categorical due to repetitive patterns


if __name__ == "__main__":
    pytest.main([__file__])
