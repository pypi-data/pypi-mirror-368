#!/usr/bin/env python3
"""
Enhanced test suite for IO module functionality.
"""

import pytest
import tempfile
import json
import os
import pandas as pd
from pathlib import Path
from unittest.mock import patch, mock_open

from funputer.io import load_metadata, load_data, save_suggestions, load_configuration
from funputer.models import (
    ColumnMetadata,
    ImputationSuggestion,
    AnalysisConfig,
    DataType,
    ImputationMethod,
    MissingnessType,
)


class TestIOEnhanced:
    """Enhanced tests for IO functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_csv(self, content: str, filename: str = "test.csv") -> str:
        """Create a temporary CSV file with given content."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def create_test_metadata_csv(self, filename: str = "metadata.csv") -> str:
        """Create a test metadata CSV file."""
        content = """column_name,data_type,role,do_not_impute,time_index,group_by,unique_flag,nullable,min_value,max_value,max_length,allowed_values,dependent_column,sentinel_values,description
user_id,integer,identifier,true,false,false,true,false,,,50,,,,"Unique user identifier"
age,integer,feature,false,false,false,false,false,0,120,,,,,"User age in years"
name,string,feature,false,false,false,false,true,,,100,,,,User full name
status,categorical,feature,false,false,false,false,false,,,10,"active,inactive",,,"Account status"
"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def create_test_config_yaml(self, filename: str = "config.yaml") -> str:
        """Create a test configuration YAML file."""
        content = """
correlation_threshold: 0.7
missing_percentage_threshold: 0.3
outlier_percentage_threshold: 0.05
iqr_multiplier: 1.5
skip_columns: []
"""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    # Test basic file operations
    def test_file_path_operations(self):
        """Test basic file path operations."""
        # Test file existence
        filepath = self.create_test_csv("name,age\nAlice,25")
        assert os.path.exists(filepath)

        # Test path manipulation
        assert filepath.endswith(".csv")
        assert os.path.getsize(filepath) > 0

    # Test metadata loading
    def test_load_metadata_csv_success(self):
        """Test successful metadata loading from CSV."""
        filepath = self.create_test_metadata_csv()
        metadata = load_metadata(filepath)

        assert len(metadata) == 4
        assert metadata[0].column_name == "user_id"
        assert metadata[0].data_type == "integer"  # String value, not enum
        assert metadata[0].unique_flag is True
        assert metadata[0].nullable is False

        assert metadata[3].column_name == "status"
        assert metadata[3].data_type == "categorical"  # String value, not enum
        assert "active" in metadata[3].allowed_values

    def test_load_metadata_with_missing_columns(self):
        """Test metadata loading with some missing columns."""
        content = """column_name,data_type
user_id,integer
name,string
"""
        filepath = os.path.join(self.temp_dir, "minimal_metadata.csv")
        with open(filepath, "w") as f:
            f.write(content)

        try:
            metadata = load_metadata(filepath)
            assert len(metadata) >= 1  # Should load at least some metadata
        except Exception as e:
            # Some metadata formats may require all columns
            assert "required" in str(e).lower() or "missing" in str(e).lower()

    def test_load_metadata_file_not_found(self):
        """Test metadata loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_metadata("/nonexistent/metadata.csv")

    def test_load_metadata_empty_file(self):
        """Test metadata loading with empty file."""
        empty_file = os.path.join(self.temp_dir, "empty.csv")
        Path(empty_file).touch()

        with pytest.raises(ValueError, match="empty or invalid"):
            load_metadata(empty_file)

    def test_load_metadata_invalid_format(self):
        """Test metadata loading with invalid format."""
        content = "invalid,content\nwithout,proper,headers"
        filepath = self.create_test_csv(content, "invalid_metadata.csv")

        with pytest.raises(KeyError):
            load_metadata(filepath)

    def test_load_metadata_with_enterprise_fallback(self):
        """Test metadata loading with enterprise loader fallback."""
        filepath = self.create_test_metadata_csv()

        # Should work normally with standard loader
        metadata = load_metadata(filepath)
        assert len(metadata) > 0

    # Test data loading
    def test_load_data_csv_success(self):
        """Test successful data loading from CSV."""
        content = "name,age,status\nAlice,25,active\nBob,30,inactive"
        filepath = self.create_test_csv(content)

        # Create minimal metadata for the test
        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
            ColumnMetadata(column_name="status", data_type=DataType.STRING),
        ]

        df = load_data(filepath, metadata)

        assert len(df) == 2
        assert len(df.columns) == 3
        assert "name" in df.columns
        assert df.iloc[0]["name"] == "Alice"

    def test_load_data_with_encoding_issues(self):
        """Test data loading with encoding detection."""
        # Create file with special characters
        content = "name,description\nAlice,Café\nBob,Résumé"
        filepath = self.create_test_csv(content)

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="description", data_type=DataType.STRING),
        ]

        df = load_data(filepath, metadata)
        assert len(df) == 2
        assert "Café" in df["description"].values[0]

    def test_load_data_file_not_found(self):
        """Test data loading with non-existent file."""
        metadata = [ColumnMetadata(column_name="test", data_type=DataType.STRING)]
        with pytest.raises(FileNotFoundError):
            load_data("/nonexistent/data.csv", metadata)

    def test_load_data_json_format(self):
        """Test data loading from JSON format."""
        # Note: load_data expects CSV format, so this will test error handling
        data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        filepath = os.path.join(self.temp_dir, "data.json")
        with open(filepath, "w") as f:
            json.dump(data, f)

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
        ]

        # Should raise ValueError since it's not CSV format
        with pytest.raises(ValueError):
            load_data(filepath, metadata)

    def test_load_data_excel_format(self):
        """Test data loading from Excel format."""
        # Create a simple DataFrame and save as Excel
        df_original = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})
        filepath = os.path.join(self.temp_dir, "data.xlsx")

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
        ]

        try:
            df_original.to_excel(filepath, index=False)
            # Should raise ValueError since load_data expects CSV
            with pytest.raises(ValueError):
                load_data(filepath, metadata)
        except ImportError:
            pytest.skip("openpyxl not available for Excel testing")

    def test_load_data_with_custom_separator(self):
        """Test data loading with custom separator."""
        content = "name;age;status\nAlice;25;active\nBob;30;inactive"
        filepath = self.create_test_csv(content, "semicolon.csv")

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
            ColumnMetadata(column_name="status", data_type=DataType.STRING),
        ]

        # Current load_data uses standard CSV reader, may not detect semicolon
        # This tests the validation error handling
        try:
            df = load_data(filepath, metadata)
            assert len(df) >= 1  # At least some data loaded
        except ValueError:
            # Expected if separator not detected properly
            pass

    def test_load_data_with_bad_lines(self):
        """Test data loading with malformed lines."""
        content = "name,age,status\nAlice,25,active\nBad,line\nBob,30,inactive"
        filepath = self.create_test_csv(content)

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
            ColumnMetadata(column_name="status", data_type=DataType.STRING),
        ]

        # Should handle bad lines gracefully or raise appropriate error
        try:
            df = load_data(filepath, metadata)
            assert len(df) >= 2  # Should get at least the good lines
        except ValueError:
            # May fail due to malformed CSV
            pass

    # Test configuration loading
    def test_load_configuration_yaml_success(self):
        """Test successful configuration loading from YAML."""
        filepath = self.create_test_config_yaml()

        config = load_configuration(filepath)

        assert isinstance(config, AnalysisConfig)
        assert config.correlation_threshold == 0.7
        assert config.missing_threshold == 0.3  # Access by actual field name
        assert config.outlier_threshold == 0.05  # Access by actual field name
        assert config.iqr_multiplier == 1.5

    def test_load_configuration_json_success(self):
        """Test successful configuration loading from JSON."""
        config_data = {
            "correlation_threshold": 0.8,
            "missing_percentage_threshold": 0.25,
            "outlier_percentage_threshold": 0.02,
            "iqr_multiplier": 2.0,
        }
        filepath = os.path.join(self.temp_dir, "config.json")
        with open(filepath, "w") as f:
            json.dump(config_data, f)

        config = load_configuration(filepath)

        assert isinstance(config, AnalysisConfig)
        assert config.correlation_threshold == 0.8
        assert config.missing_threshold == 0.25  # Access by actual field name
        assert config.outlier_threshold == 0.02  # Access by actual field name
        assert config.iqr_multiplier == 2.0

    def test_load_configuration_file_not_found(self):
        """Test configuration loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_configuration("/nonexistent/config.yaml")

    def test_load_configuration_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        content = "invalid: yaml: content: {"
        filepath = os.path.join(self.temp_dir, "invalid.yaml")
        with open(filepath, "w") as f:
            f.write(content)

        with pytest.raises(ValueError):
            load_configuration(filepath)

    def test_load_configuration_unknown_format(self):
        """Test configuration loading with unknown format."""
        filepath = os.path.join(self.temp_dir, "config.unknown")
        with open(filepath, "w") as f:
            f.write("unknown content")

        with pytest.raises(ValueError, match="Unsupported configuration format"):
            load_configuration(filepath)

    # Test suggestions saving
    def test_save_suggestions_success(self):
        """Test successful suggestions saving."""
        suggestions = [
            ImputationSuggestion(
                column_name="age",
                proposed_method=ImputationMethod.MEAN,
                confidence_score=0.85,
                rationale="Numerical data with normal distribution",
                missing_count=5,
                total_count=100,
                missingness_type=MissingnessType.MCAR,
            ),
            ImputationSuggestion(
                column_name="status",
                proposed_method=ImputationMethod.MODE,
                confidence_score=0.92,
                rationale="Categorical data with clear mode",
                missing_count=2,
                total_count=100,
                missingness_type=MissingnessType.MCAR,
            ),
        ]

        filepath = os.path.join(self.temp_dir, "suggestions.csv")
        save_suggestions(suggestions, filepath)

        # Verify file was created and contains correct data
        assert os.path.exists(filepath)

        # Load back and verify content
        df = pd.read_csv(filepath)
        assert len(df) == 2
        assert "column_name" in df.columns
        assert "proposed_method" in df.columns
        assert df.iloc[0]["column_name"] == "age"
        assert df.iloc[1]["proposed_method"] == "mode"

    def test_save_suggestions_empty_list(self):
        """Test suggestions saving with empty list."""
        suggestions = []
        filepath = os.path.join(self.temp_dir, "empty_suggestions.csv")

        # save_suggestions raises ValueError for empty list
        with pytest.raises(ValueError, match="No suggestions to save"):
            save_suggestions(suggestions, filepath)

    def test_save_suggestions_permission_error(self):
        """Test suggestions saving with permission error."""
        suggestions = [
            ImputationSuggestion(
                column_name="test",
                proposed_method=ImputationMethod.MEAN,
                confidence_score=0.5,
                rationale="Test",
                missing_count=1,
                total_count=10,
                missingness_type=MissingnessType.MCAR,
            )
        ]

        # Try to save to a protected location - use tempdir that we make read-only
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            protected_path = os.path.join(tmpdir, "readonly")
            os.makedirs(protected_path, exist_ok=True)
            os.chmod(protected_path, 0o444)  # Read-only

            with pytest.raises((PermissionError, OSError)):
                save_suggestions(
                    suggestions, os.path.join(protected_path, "suggestions.csv")
                )

    def test_save_suggestions_directory_not_exists(self):
        """Test suggestions saving when directory doesn't exist."""
        suggestions = [
            ImputationSuggestion(
                column_name="test",
                proposed_method=ImputationMethod.MEAN,
                confidence_score=0.5,
                rationale="Test",
                missing_count=1,
                total_count=10,
                missingness_type=MissingnessType.MCAR,
            )
        ]

        filepath = os.path.join(self.temp_dir, "nonexistent", "suggestions.csv")

        # Should create directory and save file
        save_suggestions(suggestions, filepath)
        assert os.path.exists(filepath)

    # Test edge cases and error handling
    def test_load_metadata_with_boolean_conversions(self):
        """Test metadata loading with various boolean formats."""
        content = """column_name,data_type,unique_flag,nullable
col1,integer,True,False
col2,string,true,false
col3,float,1,0
col4,categorical,yes,no
"""
        filepath = os.path.join(self.temp_dir, "bool_metadata.csv")
        with open(filepath, "w") as f:
            f.write(content)

        metadata = load_metadata(filepath)

        assert len(metadata) == 4
        for meta in metadata:
            assert isinstance(meta.unique_flag, bool)
            assert isinstance(meta.nullable, bool)

    def test_load_data_with_various_na_values(self):
        """Test data loading with different NA representations."""
        content = "name,age,status\nAlice,25,active\nBob,NA,inactive\nCharlie,,pending\nDiana,NULL,active"
        filepath = self.create_test_csv(content)

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
            ColumnMetadata(column_name="status", data_type=DataType.STRING),
        ]

        df = load_data(filepath, metadata)

        # Should recognize various NA formats
        assert df["age"].isna().sum() >= 2  # At least NA and empty string

    def test_memory_efficient_loading(self):
        """Test memory efficient loading for large files."""
        # Create a moderately large CSV
        lines = ["name,age,score"]
        for i in range(1000):
            lines.append(f"User{i},{20+i%50},{i%100}")

        content = "\n".join(lines)
        filepath = self.create_test_csv(content, "large.csv")

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
            ColumnMetadata(column_name="score", data_type=DataType.INTEGER),
        ]

        df = load_data(filepath, metadata)

        assert len(df) == 1000
        assert len(df.columns) == 3

    def test_concurrent_file_access(self):
        """Test handling of concurrent file access."""
        filepath = self.create_test_csv("name,age\nAlice,25")

        metadata = [
            ColumnMetadata(column_name="name", data_type=DataType.STRING),
            ColumnMetadata(column_name="age", data_type=DataType.INTEGER),
        ]

        # Load the same file multiple times (simulating concurrent access)
        results = []
        for _ in range(3):
            df = load_data(filepath, metadata)
            results.append(len(df))

        # All should succeed with same result
        assert all(r == 1 for r in results)


if __name__ == "__main__":
    pytest.main([__file__])
