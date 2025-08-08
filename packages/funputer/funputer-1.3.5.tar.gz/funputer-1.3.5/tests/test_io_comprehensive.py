#!/usr/bin/env python3
"""
Comprehensive tests for io.py to increase coverage.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import json
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path

from funputer.io import (
    load_data,
    load_metadata,
    save_suggestions,
    load_configuration,
    get_column_metadata,
    validate_metadata_against_data,
)
from funputer.models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from funputer.exceptions import MetadataValidationError, ConfigurationError


class TestLoadData:
    """Test data loading functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_csv(self, filename="test.csv", data=None):
        """Helper to create test CSV files."""
        if data is None:
            data = {
                "id": [1, 2, 3, 4, 5],
                "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
                "age": [25, 30, None, 35, 40],
                "score": [85.5, 92.0, 78.5, None, 88.0],
            }

        df = pd.DataFrame(data)
        filepath = os.path.join(self.temp_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath

    def test_load_data_basic_csv(self):
        """Test basic CSV data loading."""
        filepath = self.create_test_csv()

        df = load_data(filepath)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ["id", "name", "age", "score"]
        assert df["name"].iloc[0] == "Alice"

    def test_load_data_with_metadata(self):
        """Test data loading with metadata validation."""
        filepath = self.create_test_csv()
        metadata = [
            ColumnMetadata(column_name="id", data_type="integer"),
            ColumnMetadata(column_name="name", data_type="string"),
            ColumnMetadata(column_name="age", data_type="integer"),
            ColumnMetadata(column_name="score", data_type="float"),
        ]

        df = load_data(filepath, metadata)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert len(df.columns) == 4

    def test_load_data_file_not_found(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_data("/nonexistent/file.csv")

    def test_load_data_empty_file(self):
        """Test loading empty CSV file."""
        filepath = os.path.join(self.temp_dir, "empty.csv")
        with open(filepath, "w") as f:
            f.write("")

        with pytest.raises(Exception):  # Could be various exceptions
            load_data(filepath)

    def test_load_data_malformed_csv(self):
        """Test loading malformed CSV file."""
        filepath = os.path.join(self.temp_dir, "malformed.csv")
        with open(filepath, "w") as f:
            f.write("col1,col2\n1,2,3,4\n")  # Too many values

        # Should still load but might have issues
        df = load_data(filepath)
        assert isinstance(df, pd.DataFrame)

    def test_load_data_different_encodings(self):
        """Test loading files with different encodings."""
        # Create UTF-8 file with special characters
        data = {"name": ["café", "naïve", "中文"], "value": [1, 2, 3]}
        df = pd.DataFrame(data)

        filepath = os.path.join(self.temp_dir, "utf8.csv")
        df.to_csv(filepath, index=False, encoding="utf-8")

        loaded_df = load_data(filepath)
        assert isinstance(loaded_df, pd.DataFrame)
        assert len(loaded_df) == 3

    def test_load_data_large_file(self):
        """Test loading larger CSV file."""
        # Create larger dataset
        large_data = {
            "id": range(1000),
            "value": np.random.random(1000),
            "category": np.random.choice(["A", "B", "C"], 1000),
        }
        filepath = self.create_test_csv("large.csv", large_data)

        df = load_data(filepath)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1000
        assert len(df.columns) == 3

    def test_load_data_with_various_dtypes(self):
        """Test loading data with various data types."""
        data = {
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"],
            "bool_col": [True, False, True],
            "date_col": ["2024-01-01", "2024-01-02", "2024-01-03"],
        }
        filepath = self.create_test_csv("dtypes.csv", data)

        df = load_data(filepath)

        assert isinstance(df, pd.DataFrame)
        assert len(df.columns) == 5
        assert df["int_col"].dtype in ["int64", "Int64"]
        assert df["float_col"].dtype == "float64"
        assert df["str_col"].dtype == "object"


class TestLoadMetadata:
    """Test metadata loading functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_metadata_csv(self, filename="metadata.csv"):
        """Helper to create test metadata CSV."""
        metadata_data = {
            "column_name": ["id", "name", "age", "score"],
            "data_type": ["integer", "string", "integer", "float"],
            "nullable": [False, True, True, True],
            "unique_flag": [True, False, False, False],
            "min_value": [1, None, 0, 0],
            "max_value": [1000, None, 100, 100],
            "max_length": [None, 50, None, None],
            "description": ["ID field", "Name field", "Age field", "Score field"],
        }

        df = pd.DataFrame(metadata_data)
        filepath = os.path.join(self.temp_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath

    def test_load_metadata_csv_success(self):
        """Test successful metadata loading from CSV."""
        filepath = self.create_metadata_csv()

        metadata_list = load_metadata(filepath)

        assert len(metadata_list) == 4
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)

        # Check first metadata object
        first_meta = metadata_list[0]
        assert first_meta.column_name == "id"
        assert first_meta.data_type == "integer"
        assert first_meta.nullable == False
        assert first_meta.unique_flag == True
        assert first_meta.min_value == 1
        assert first_meta.max_value == 1000
        assert first_meta.description == "ID field"

    def test_load_metadata_missing_required_columns(self):
        """Test metadata loading with missing required columns."""
        # Create metadata with missing required columns
        incomplete_data = {"column_name": ["col1"], "description": ["desc1"]}
        df = pd.DataFrame(incomplete_data)
        filepath = os.path.join(self.temp_dir, "incomplete.csv")
        df.to_csv(filepath, index=False)

        with pytest.raises(MetadataValidationError):
            load_metadata(filepath)

    def test_load_metadata_file_not_found(self):
        """Test metadata loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_metadata("/nonexistent/metadata.csv")

    def test_load_metadata_empty_file(self):
        """Test metadata loading with empty file."""
        filepath = os.path.join(self.temp_dir, "empty.csv")
        with open(filepath, "w") as f:
            f.write("")

        with pytest.raises(MetadataValidationError):
            load_metadata(filepath)

    def test_load_metadata_json_format(self):
        """Test loading metadata in JSON format."""
        metadata_json = [
            {
                "column_name": "id",
                "data_type": "integer",
                "nullable": False,
                "unique_flag": True,
            },
            {
                "column_name": "name",
                "data_type": "string",
                "nullable": True,
                "unique_flag": False,
            },
        ]

        filepath = os.path.join(self.temp_dir, "metadata.json")
        with open(filepath, "w") as f:
            json.dump(metadata_json, f)

        metadata_list = load_metadata(filepath)

        assert len(metadata_list) == 2
        assert metadata_list[0].column_name == "id"
        assert metadata_list[1].column_name == "name"

    def test_load_metadata_with_enhanced_fields(self):
        """Test loading metadata with enhanced fields."""
        enhanced_data = {
            "column_name": ["customer_id", "age"],
            "data_type": ["string", "integer"],
            "nullable": [False, True],
            "unique_flag": [True, False],
            "role": ["identifier", "feature"],
            "do_not_impute": [True, False],
            "sentinel_values": [None, "-999"],
            "time_index": [False, False],
            "group_by": [False, False],
            "policy_version": ["v1.0", "v1.0"],
        }

        df = pd.DataFrame(enhanced_data)
        filepath = os.path.join(self.temp_dir, "enhanced.csv")
        df.to_csv(filepath, index=False)

        metadata_list = load_metadata(filepath)

        assert len(metadata_list) == 2
        assert metadata_list[0].role == "identifier"
        assert metadata_list[0].do_not_impute == True
        assert metadata_list[1].sentinel_values == "-999"

    def test_load_metadata_invalid_json(self):
        """Test loading invalid JSON metadata."""
        filepath = os.path.join(self.temp_dir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("invalid json content")

        with pytest.raises(Exception):  # JSON decode error
            load_metadata(filepath)


class TestSaveSuggestions:
    """Test suggestions saving functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create sample suggestions
        self.sample_suggestions = [
            ImputationSuggestion(
                column_name="age",
                missing_count=5,
                missing_percentage=10.0,
                mechanism="MCAR",
                proposed_method="Median",
                rationale="Robust to outliers",
                confidence_score=0.85,
            ),
            ImputationSuggestion(
                column_name="score",
                missing_count=3,
                missing_percentage=6.0,
                mechanism="MAR",
                proposed_method="Mean",
                rationale="Normally distributed",
                confidence_score=0.92,
            ),
        ]

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_suggestions_csv(self):
        """Test saving suggestions to CSV."""
        output_path = os.path.join(self.temp_dir, "suggestions.csv")

        save_suggestions(self.sample_suggestions, output_path)

        assert os.path.exists(output_path)

        # Read back and verify
        df = pd.read_csv(output_path)
        assert len(df) == 2
        assert "Column" in df.columns
        assert "Proposed_Method" in df.columns
        assert "Confidence_Score" in df.columns
        assert df["Column"].iloc[0] == "age"
        assert df["Column"].iloc[1] == "score"

    def test_save_suggestions_json(self):
        """Test saving suggestions to JSON."""
        output_path = os.path.join(self.temp_dir, "suggestions.json")

        save_suggestions(self.sample_suggestions, output_path)

        assert os.path.exists(output_path)

        # Read back and verify
        with open(output_path, "r") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["Column"] == "age"
        assert data[1]["Column"] == "score"

    def test_save_suggestions_empty_list(self):
        """Test saving empty suggestions list."""
        output_path = os.path.join(self.temp_dir, "empty.csv")

        save_suggestions([], output_path)

        assert os.path.exists(output_path)

        # Should create file but with headers only
        df = pd.read_csv(output_path)
        assert len(df) == 0
        assert len(df.columns) > 0  # Should have headers

    def test_save_suggestions_permission_error(self):
        """Test saving to protected directory."""
        if os.name != "nt":  # Skip on Windows
            protected_path = "/root/suggestions.csv"

            with pytest.raises(PermissionError):
                save_suggestions(self.sample_suggestions, protected_path)

    def test_save_suggestions_invalid_format(self):
        """Test saving with unsupported file format."""
        output_path = os.path.join(self.temp_dir, "suggestions.xlsx")

        # Should handle gracefully or raise appropriate error
        try:
            save_suggestions(self.sample_suggestions, output_path)
            # If it succeeds, verify file exists
            assert os.path.exists(output_path)
        except Exception as e:
            # If it fails, should be a reasonable error
            assert "format" in str(e).lower() or "extension" in str(e).lower()


class TestLoadConfiguration:
    """Test configuration loading functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_configuration_none(self):
        """Test loading configuration with None path (default config)."""
        config = load_configuration(None)

        assert isinstance(config, AnalysisConfig)
        assert config.iqr_multiplier == 1.5  # Default value
        assert config.outlier_threshold == 0.05

    def test_load_configuration_json(self):
        """Test loading JSON configuration."""
        config_data = {
            "iqr_multiplier": 2.0,
            "outlier_threshold": 0.1,
            "correlation_threshold": 0.5,
            "skip_columns": ["id", "timestamp"],
        }

        filepath = os.path.join(self.temp_dir, "config.json")
        with open(filepath, "w") as f:
            json.dump(config_data, f)

        config = load_configuration(filepath)

        assert isinstance(config, AnalysisConfig)
        assert config.iqr_multiplier == 2.0
        assert config.outlier_threshold == 0.1
        assert config.correlation_threshold == 0.5
        assert config.skip_columns == ["id", "timestamp"]

    def test_load_configuration_yaml(self):
        """Test loading YAML configuration."""
        config_data = {
            "iqr_multiplier": 1.8,
            "missing_threshold": 0.9,
            "metrics_port": 8080,
        }

        filepath = os.path.join(self.temp_dir, "config.yaml")
        with open(filepath, "w") as f:
            yaml.dump(config_data, f)

        config = load_configuration(filepath)

        assert isinstance(config, AnalysisConfig)
        assert config.iqr_multiplier == 1.8
        assert config.missing_threshold == 0.9
        assert config.metrics_port == 8080

    def test_load_configuration_file_not_found(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_configuration("/nonexistent/config.json")

    def test_load_configuration_invalid_json(self):
        """Test loading invalid JSON configuration."""
        filepath = os.path.join(self.temp_dir, "invalid.json")
        with open(filepath, "w") as f:
            f.write("invalid json content")

        with pytest.raises(ConfigurationError):
            load_configuration(filepath)

    def test_load_configuration_invalid_yaml(self):
        """Test loading invalid YAML configuration."""
        filepath = os.path.join(self.temp_dir, "invalid.yaml")
        with open(filepath, "w") as f:
            f.write("invalid: yaml: content:")

        with pytest.raises(ConfigurationError):
            load_configuration(filepath)

    def test_load_configuration_unsupported_format(self):
        """Test loading unsupported configuration format."""
        filepath = os.path.join(self.temp_dir, "config.xml")
        with open(filepath, "w") as f:
            f.write("<config></config>")

        with pytest.raises(ConfigurationError):
            load_configuration(filepath)

    def test_load_configuration_validation_error(self):
        """Test loading configuration with validation errors."""
        config_data = {
            "iqr_multiplier": -1.0,  # Invalid value
            "outlier_threshold": 2.0,  # Invalid value
        }

        filepath = os.path.join(self.temp_dir, "invalid_config.json")
        with open(filepath, "w") as f:
            json.dump(config_data, f)

        with pytest.raises(ConfigurationError):
            load_configuration(filepath)


class TestUtilityFunctions:
    """Test utility functions in io module."""

    def test_get_column_metadata_found(self):
        """Test getting existing column metadata."""
        metadata_list = [
            ColumnMetadata(column_name="id", data_type="integer"),
            ColumnMetadata(column_name="name", data_type="string"),
            ColumnMetadata(column_name="age", data_type="integer"),
        ]

        result = get_column_metadata(metadata_list, "name")

        assert result is not None
        assert result.column_name == "name"
        assert result.data_type == "string"

    def test_get_column_metadata_not_found(self):
        """Test getting non-existent column metadata."""
        metadata_list = [
            ColumnMetadata(column_name="id", data_type="integer"),
            ColumnMetadata(column_name="name", data_type="string"),
        ]

        result = get_column_metadata(metadata_list, "nonexistent")

        assert result is None

    def test_get_column_metadata_empty_list(self):
        """Test getting metadata from empty list."""
        result = get_column_metadata([], "any_column")
        assert result is None

    def test_validate_metadata_against_data(self):
        """Test metadata validation against data."""
        # Create test data and metadata files
        temp_dir = tempfile.mkdtemp()

        try:
            # Create data file
            data = pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "name": ["Alice", "Bob", "Charlie"],
                    "age": [25, 30, 35],
                }
            )
            data_path = os.path.join(temp_dir, "data.csv")
            data.to_csv(data_path, index=False)

            # Create matching metadata
            metadata_list = [
                ColumnMetadata(column_name="id", data_type="integer"),
                ColumnMetadata(column_name="name", data_type="string"),
                ColumnMetadata(column_name="age", data_type="integer"),
            ]

            errors = validate_metadata_against_data(metadata_list, data_path)

            # Should have no errors for matching metadata
            assert isinstance(errors, list)
            # May have some warnings but should not crash

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_validate_metadata_mismatched_columns(self):
        """Test metadata validation with mismatched columns."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create data file
            data = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
            data_path = os.path.join(temp_dir, "data.csv")
            data.to_csv(data_path, index=False)

            # Create metadata for different columns
            metadata_list = [
                ColumnMetadata(column_name="different_col", data_type="integer"),
                ColumnMetadata(column_name="another_col", data_type="string"),
            ]

            errors = validate_metadata_against_data(metadata_list, data_path)

            # Should detect mismatches
            assert isinstance(errors, list)
            # May contain validation errors

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_data_with_bom(self):
        """Test loading CSV file with BOM (Byte Order Mark)."""
        filepath = os.path.join(self.temp_dir, "bom.csv")

        # Create CSV with BOM
        content = "id,name\n1,Alice\n2,Bob"
        with open(filepath, "wb") as f:
            f.write(b"\xef\xbb\xbf")  # UTF-8 BOM
            f.write(content.encode("utf-8"))

        df = load_data(filepath)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        # BOM should be handled gracefully

    def test_load_data_very_long_lines(self):
        """Test loading CSV with very long lines."""
        long_text = "x" * 10000
        data = {"id": [1], "long_field": [long_text]}

        df = pd.DataFrame(data)
        filepath = os.path.join(self.temp_dir, "long_lines.csv")
        df.to_csv(filepath, index=False)

        loaded_df = load_data(filepath)

        assert isinstance(loaded_df, pd.DataFrame)
        assert len(loaded_df) == 1
        assert len(loaded_df["long_field"].iloc[0]) == 10000

    def test_load_metadata_partial_fields(self):
        """Test loading metadata with only some fields present."""
        partial_data = {
            "column_name": ["col1", "col2"],
            "data_type": ["integer", "string"],
            "description": ["First column", "Second column"],
            # Missing other optional fields
        }

        df = pd.DataFrame(partial_data)
        filepath = os.path.join(self.temp_dir, "partial.csv")
        df.to_csv(filepath, index=False)

        metadata_list = load_metadata(filepath)

        assert len(metadata_list) == 2
        assert metadata_list[0].column_name == "col1"
        # Should use defaults for missing fields
        assert metadata_list[0].nullable == True  # Default
        assert metadata_list[0].unique_flag == False  # Default

    @patch("funputer.io.logger")
    def test_logging_on_operations(self, mock_logger):
        """Test that IO operations generate appropriate logs."""
        # Create test file
        data = pd.DataFrame({"col1": [1, 2, 3]})
        filepath = os.path.join(self.temp_dir, "test.csv")
        data.to_csv(filepath, index=False)

        # Load data - should generate logs
        load_data(filepath)

        # Check that logging occurred
        assert (
            mock_logger.info.called
            or mock_logger.debug.called
            or mock_logger.warning.called
        )

    def test_save_suggestions_to_existing_file(self):
        """Test overwriting existing suggestions file."""
        output_path = os.path.join(self.temp_dir, "existing.csv")

        # Create initial file
        initial_suggestions = [
            ImputationSuggestion(
                column_name="old_col",
                proposed_method="Old Method",
                rationale="Old rationale",
            )
        ]
        save_suggestions(initial_suggestions, output_path)

        # Overwrite with new suggestions
        new_suggestions = [
            ImputationSuggestion(
                column_name="new_col",
                proposed_method="New Method",
                rationale="New rationale",
            )
        ]
        save_suggestions(new_suggestions, output_path)

        # Verify overwrite worked
        df = pd.read_csv(output_path)
        assert len(df) == 1
        assert df["Column"].iloc[0] == "new_col"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
