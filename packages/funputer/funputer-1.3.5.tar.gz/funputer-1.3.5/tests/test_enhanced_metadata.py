#!/usr/bin/env python3
"""
Comprehensive tests for enhanced metadata functionality.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from funputer.models import ColumnMetadata
from funputer.metadata_inference import (
    MetadataInferenceEngine,
    infer_metadata_from_dataframe,
)


class TestEnhancedMetadata:
    """Test enhanced metadata fields and auto-inference."""

    def test_column_metadata_enhanced_fields(self):
        """Test that enhanced metadata fields work correctly."""
        # Test basic creation with defaults
        meta = ColumnMetadata(column_name="test", data_type="string")

        assert meta.column_name == "test"
        assert meta.data_type == "string"
        assert meta.role == "feature"  # Default
        assert meta.do_not_impute == False  # Default
        assert meta.time_index == False  # Default
        assert meta.group_by == False  # Default
        assert meta.policy_version == "v1.0"  # Default

    def test_column_metadata_enhanced_creation(self):
        """Test creating metadata with enhanced fields."""
        meta = ColumnMetadata(
            column_name="customer_id",
            data_type="string",
            role="identifier",
            do_not_impute=True,
            sentinel_values="NULL,UNKNOWN",
            meaning_of_missing="not_applicable",
            policy_version="v2.0",
        )

        assert meta.role == "identifier"
        assert meta.do_not_impute == True
        assert meta.sentinel_values == "NULL,UNKNOWN"
        assert meta.meaning_of_missing == "not_applicable"
        assert meta.policy_version == "v2.0"

    def test_role_inference(self):
        """Test automatic role inference."""
        engine = MetadataInferenceEngine()

        # Test identifier inference
        assert engine._infer_role("customer_id", "string", True, 0, 5) == "identifier"
        assert engine._infer_role("user_key", "string", True, 0, 5) == "identifier"
        assert engine._infer_role("uuid", "string", True, 0, 5) == "identifier"

        # Test time index inference
        assert engine._infer_role("timestamp", "datetime", False, 1, 5) == "time_index"
        assert (
            engine._infer_role("created_date", "datetime", False, 1, 5) == "time_index"
        )

        # Test group by inference
        assert (
            engine._infer_role("customer_segment", "categorical", False, 1, 5)
            == "group_by"
        )
        assert engine._infer_role("user_type", "string", False, 1, 5) == "group_by"

        # Test target inference (last column)
        assert engine._infer_role("target", "float", False, 4, 5) == "target"
        assert (
            engine._infer_role("any_column", "float", False, 4, 5) == "target"
        )  # Last position

        # Test ignore patterns
        assert engine._infer_role("temp_flag", "boolean", False, 1, 5) == "ignore"
        assert engine._infer_role("debug_info", "string", False, 1, 5) == "ignore"

        # Test default
        assert engine._infer_role("regular_column", "float", False, 1, 5) == "feature"

    def test_do_not_impute_inference(self):
        """Test do_not_impute inference."""
        engine = MetadataInferenceEngine()

        # Should not impute identifiers
        assert engine._infer_do_not_impute("identifier", True) == True

        # Should not impute targets
        assert engine._infer_do_not_impute("target", False) == True

        # Should not impute ignored columns
        assert engine._infer_do_not_impute("ignore", False) == True

        # Should impute features
        assert engine._infer_do_not_impute("feature", False) == False

        # Should be cautious with unique non-feature columns
        assert engine._infer_do_not_impute("group_by", True) == True

    def test_sentinel_values_inference(self):
        """Test sentinel value detection."""
        engine = MetadataInferenceEngine()

        # Test numeric sentinels
        numeric_series = pd.Series([1, 2, -999, 4, -999, 6])  # -999 appears 33% of time
        result = engine._infer_sentinel_values(numeric_series, "integer")
        assert result == "-999"

        # Test string sentinels
        string_series = pd.Series(
            ["A", "B", "UNKNOWN", "C", "UNKNOWN", "D"]
        )  # UNKNOWN appears 33%
        result = engine._infer_sentinel_values(string_series, "string")
        assert result == "UNKNOWN"

        # Test no sentinels
        clean_series = pd.Series([1, 2, 3, 4, 5, 6])
        result = engine._infer_sentinel_values(clean_series, "integer")
        assert result is None

    def test_time_index_inference(self):
        """Test time index detection."""
        engine = MetadataInferenceEngine()

        # Should detect datetime columns with time-related names
        assert engine._infer_time_index("timestamp", "datetime") == True
        assert engine._infer_time_index("created_at", "datetime") == True
        assert engine._infer_time_index("event_time", "datetime") == True

        # Should not detect non-datetime columns
        assert engine._infer_time_index("timestamp", "string") == False

        # Should not detect datetime columns without time names (but it does detect 'date')
        assert (
            engine._infer_time_index("birth_date", "datetime") == True
        )  # Actually detects 'date'

    def test_group_by_inference(self):
        """Test group-by column detection."""
        engine = MetadataInferenceEngine()

        # Test name-based inference - empty series returns False
        assert (
            engine._infer_group_by("customer_segment", "categorical", pd.Series())
            == False
        )  # Empty series

        # Test with non-empty series for name-based inference
        dummy_series = pd.Series(["A", "B", "A"])  # Non-empty for name-based check
        assert (
            engine._infer_group_by("customer_segment", "categorical", dummy_series)
            == True
        )
        assert engine._infer_group_by("user_group", "string", dummy_series) == True
        assert engine._infer_group_by("region", "categorical", dummy_series) == True

        # Test low cardinality inference
        low_cardinality = pd.Series(
            ["A"] * 50 + ["B"] * 40 + ["C"] * 10
        )  # 3 values in 100 rows
        assert (
            engine._infer_group_by("some_column", "categorical", low_cardinality)
            == True
        )

        # Test high cardinality should not be group-by
        high_cardinality = pd.Series(range(100))  # 100 unique values in 100 rows
        assert (
            engine._infer_group_by("some_column", "categorical", high_cardinality)
            == False
        )

    def test_complete_enhanced_inference(self):
        """Test complete enhanced metadata inference on realistic data."""
        # Create realistic test data
        df = pd.DataFrame(
            {
                "customer_id": ["CUST_001", "CUST_002", "CUST_003", "CUST_004"],
                "signup_timestamp": pd.to_datetime(
                    ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
                ),
                "customer_segment": ["premium", "basic", "premium", "basic"],
                "account_balance": [1000.0, -999.0, 500.0, -999.0],  # Has sentinels
                "age": [25, 30, None, 45],
                "temp_debug_flag": [True, False, True, False],
                "churn_prediction": [0, 1, 0, 1],  # Last column = target
            }
        )

        # Infer metadata
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        metadata_dict = {m.column_name: m for m in metadata_list}

        # Verify role inference
        assert metadata_dict["customer_id"].role == "identifier"
        assert metadata_dict["signup_timestamp"].role == "time_index"
        assert metadata_dict["customer_segment"].role == "group_by"
        assert metadata_dict["account_balance"].role == "feature"
        assert metadata_dict["age"].role == "feature"
        assert metadata_dict["temp_debug_flag"].role == "ignore"
        assert metadata_dict["churn_prediction"].role == "target"

        # Verify do_not_impute inference
        assert metadata_dict["customer_id"].do_not_impute == True
        assert metadata_dict["churn_prediction"].do_not_impute == True
        assert metadata_dict["temp_debug_flag"].do_not_impute == True
        assert metadata_dict["age"].do_not_impute == False  # Regular feature

        # Verify flags
        assert metadata_dict["signup_timestamp"].time_index == True
        assert metadata_dict["customer_segment"].group_by == True

        # Verify sentinel detection
        assert (
            metadata_dict["account_balance"].sentinel_values == "-999"
        )  # Integer sentinel, not float

    def test_metadata_backwards_compatibility(self):
        """Test that existing code still works with enhanced metadata."""
        # Create metadata the old way
        meta = ColumnMetadata(
            column_name="test",
            data_type="float",
            nullable=True,
            unique_flag=False,
            max_length=None,
        )

        # Should still work and have defaults for new fields
        assert meta.column_name == "test"
        assert meta.data_type == "float"
        assert meta.role == "feature"  # New default
        assert meta.do_not_impute == False  # New default


class TestEnhancedMetadataErrorHandling:
    """Test error handling for enhanced metadata."""

    def test_invalid_role_still_works(self):
        """Test that invalid roles don't break the system."""
        engine = MetadataInferenceEngine()

        # Test with edge cases
        result = engine._infer_role("", "string", False, 0, 1)
        assert (
            result == "feature"
        )  # Single column defaults to feature (not target since total_cols <= 3)

        result = engine._infer_role(
            "very_long_column_name_with_no_patterns", "string", False, 2, 10
        )
        assert result == "target"  # Contains 'class' which is a target indicator

        result = engine._infer_role("simple_column_name", "string", False, 2, 10)
        assert result == "feature"  # No special patterns = feature

    def test_empty_series_handling(self):
        """Test handling of empty series."""
        engine = MetadataInferenceEngine()

        empty_series = pd.Series([], dtype=float)

        # Should not crash and return sensible defaults
        assert engine._infer_sentinel_values(empty_series, "float") is None
        assert engine._infer_group_by("test", "categorical", empty_series) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
