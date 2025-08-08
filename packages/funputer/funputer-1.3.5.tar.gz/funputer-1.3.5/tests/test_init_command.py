"""
Tests for the new init command functionality.
"""

import pytest
import os
import tempfile
import csv
import pandas as pd
from click.testing import CliRunner
from unittest.mock import patch

from funputer.simple_cli import cli
from funputer.metadata_inference import infer_metadata_from_dataframe


class TestInitCommand:
    """Test the init command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def create_sample_data_file(self, temp_dir, filename="test_data.csv"):
        """Create a sample data file for testing init command."""
        data_content = """customer_id,age,income,category,is_active,registration_date,rating,notes
1001,25,50000.50,Premium,TRUE,2023-01-15,4.2,Good customer
1002,34,,Standard,FALSE,2023-02-20,3.8,Needs follow-up
1003,,89000.25,Premium,TRUE,,4.5,
1004,42,78000.00,Basic,TRUE,2023-01-08,,VIP
1005,28,52000.75,,FALSE,2023-03-10,3.9,Regular customer
1006,35,,Standard,TRUE,2023-01-25,4.1,
1007,,95000.50,Premium,TRUE,2023-02-14,4.7,New signup
1008,39,125000.00,Basic,FALSE,2023-03-05,,Loyal customer"""

        data_path = os.path.join(temp_dir, filename)
        with open(data_path, "w") as f:
            f.write(data_content)
        return data_path

    def test_init_basic_execution(self):
        """Test basic init command execution."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                assert result.exit_code == 0
                assert "✅ Metadata template created: metadata.csv" in result.output
                assert "📊 Analyzed 8 columns" in result.output
                assert "Next steps:" in result.output
                assert "funputer analyze -m metadata.csv" in result.output

                # Check that metadata.csv was created
                assert os.path.exists("metadata.csv")

                # Verify CSV structure
                with open("metadata.csv", "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                    assert len(rows) == 8  # 8 columns

                    # Check required headers (v1.3.4: 15 inferrable fields only)
                    expected_headers = [
                        "column_name",
                        "data_type",
                        "role",
                        "do_not_impute",
                        "time_index",
                        "group_by",
                        "unique_flag",
                        "nullable",
                        "min_value",
                        "max_value",
                        "max_length",
                        "allowed_values",
                        "dependent_column",
                        "sentinel_values",
                        "description",
                    ]
                    assert set(reader.fieldnames) == set(expected_headers)
                    assert len(reader.fieldnames) == 15  # Exactly 15 inferrable fields

                    # Check some specific inferences
                    column_types = {
                        row["column_name"]: row["data_type"] for row in rows
                    }
                    assert column_types["customer_id"] == "integer"
                    assert column_types["age"] == "integer"
                    assert column_types["income"] == "float"
                    assert column_types["category"] == "categorical"
                    assert column_types["is_active"] == "boolean"
                    assert column_types["registration_date"] == "datetime"
                    assert column_types["rating"] == "float"

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_with_custom_output(self):
        """Test init command with custom output file."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli, ["init", "-d", data_path, "-o", "custom_metadata.csv"]
                )

                assert result.exit_code == 0
                assert (
                    "✅ Metadata template created: custom_metadata.csv" in result.output
                )
                assert os.path.exists("custom_metadata.csv")
                assert not os.path.exists("metadata.csv")  # Default shouldn't exist

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_verbose_mode(self):
        """Test init command with verbose output."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path, "--verbose"])

                assert result.exit_code == 0
                assert "INFO: Analyzing data file:" in result.output
                assert "INFO: Loaded 8 rows and 8 columns" in result.output
                assert "INFO: Inferring metadata and data types..." in result.output
                assert "INFO: Writing metadata template to:" in result.output
                assert "🔍 Column summary:" in result.output
                assert "customer_id: integer" in result.output

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_file_not_found(self):
        """Test init command with non-existent data file."""
        result = self.runner.invoke(cli, ["init", "-d", "nonexistent_file.csv"])

        assert result.exit_code == 1
        assert "❌ Error: Data file not found: nonexistent_file.csv" in result.output

    def test_init_with_minimal_data(self):
        """Test init command with minimal data (edge case)."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create minimal data file
            minimal_data = "id\n1\n2\n3"
            data_path = os.path.join(temp_dir, "minimal.csv")
            with open(data_path, "w") as f:
                f.write(minimal_data)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                assert result.exit_code == 0
                assert "📊 Analyzed 1 columns" in result.output
                assert os.path.exists("metadata.csv")

                # Verify the single column was processed
                with open("metadata.csv", "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == 1
                    assert rows[0]["column_name"] == "id"
                    assert rows[0]["data_type"] == "integer"

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_with_all_missing_data(self):
        """Test init command with data containing all missing values."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create data with all missing values
            missing_data = "col1,col2,col3\n,,\n,,\n,,"
            data_path = os.path.join(temp_dir, "missing.csv")
            with open(data_path, "w") as f:
                f.write(missing_data)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                # Should still work, might infer as string/categorical
                assert result.exit_code == 0
                assert "📊 Analyzed 3 columns" in result.output

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_help_output(self):
        """Test init command help output."""
        result = self.runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert (
            "Generate a metadata template CSV by analyzing your data file"
            in result.output
        )
        assert "--data" in result.output
        assert "--output" in result.output
        assert "--verbose" in result.output
        assert "Examples:" in result.output
        assert "funputer init -d data.csv" in result.output

    def test_init_integration_with_analyze(self):
        """Test that init-generated metadata works with analyze command (comprehensive v1.3.4 validation)."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                # Step 1: Generate metadata template
                init_result = self.runner.invoke(cli, ["init", "-d", data_path])
                assert init_result.exit_code == 0
                assert os.path.exists("metadata.csv")

                # v1.3.4: Verify metadata structure before using it
                with open("metadata.csv", "r") as f:
                    import csv

                    reader = csv.DictReader(f)
                    rows = list(reader)

                    # Critical v1.3.4 validations
                    assert (
                        len(reader.fieldnames) == 15
                    ), f"Expected 15 fields, got {len(reader.fieldnames)}"
                    assert (
                        "business_rule" not in reader.fieldnames
                    ), "business_rule should not be in export"
                    assert (
                        "dependency_rule" not in reader.fieldnames
                    ), "dependency_rule should not be in export"
                    assert "role" in reader.fieldnames, "role should be in export"
                    assert (
                        "do_not_impute" in reader.fieldnames
                    ), "do_not_impute should be in export"

                # Step 2: Use generated metadata with analyze command
                analyze_result = self.runner.invoke(
                    cli, ["analyze", "-m", "metadata.csv", "-d", data_path]
                )

                assert analyze_result.exit_code == 0
                assert "✓ Analysis complete!" in analyze_result.output
                assert os.path.exists("suggestions.csv")

                # Step 3: Verify analysis output works correctly
                with open("suggestions.csv", "r") as f:
                    suggestions_reader = csv.DictReader(f)
                    suggestion_rows = list(suggestions_reader)

                    # Should have suggestions for columns with missing data
                    assert (
                        len(suggestion_rows) > 0
                    ), "Should have imputation suggestions"

                    # Verify the suggestions make sense
                    for suggestion in suggestion_rows:
                        assert "Column" in suggestion
                        assert "Proposed_Method" in suggestion
                        assert "Confidence_Score" in suggestion

                        # Check confidence score is valid
                        confidence = float(suggestion["Confidence_Score"])
                        assert (
                            0.0 <= confidence <= 1.0
                        ), f"Invalid confidence: {confidence}"

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_error_handling_with_corrupted_csv(self):
        """Test init command error handling with corrupted CSV."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create corrupted CSV file
            corrupted_data = 'col1,col2\n"unclosed quote,value\nmore,data'
            data_path = os.path.join(temp_dir, "corrupted.csv")
            with open(data_path, "w") as f:
                f.write(corrupted_data)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                # Should handle the error gracefully
                assert result.exit_code == 1
                assert "❌ Error generating metadata template:" in result.output

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_with_permission_error(self):
        """Test init command handling of permission errors."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                # Mock a permission error when writing output
                with patch(
                    "builtins.open", side_effect=PermissionError("Permission denied")
                ):
                    result = self.runner.invoke(cli, ["init", "-d", data_path])

                    assert result.exit_code == 1
                    assert "❌ Error generating metadata template:" in result.output

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_metadata_content_validation(self):
        """Test that generated metadata contains expected content and structure."""
        temp_dir = tempfile.mkdtemp()

        try:
            data_path = self.create_sample_data_file(temp_dir)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                assert result.exit_code == 0

                # Read and validate the generated metadata
                with open("metadata.csv", "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                # Find specific columns and validate their metadata
                customer_id_row = next(
                    row for row in rows if row["column_name"] == "customer_id"
                )
                assert customer_id_row["data_type"] == "integer"
                assert (
                    customer_id_row["unique_flag"] == "TRUE"
                )  # Should detect as unique
                assert customer_id_row["min_value"] == "1001.0"
                assert customer_id_row["max_value"] == "1008.0"

                income_row = next(row for row in rows if row["column_name"] == "income")
                assert income_row["data_type"] == "float"
                assert income_row["unique_flag"] == "FALSE"
                assert float(income_row["min_value"]) > 0

                # Check that non-inferrable fields are NOT present (v1.3.4 fix)
                for row in rows:
                    # These fields should NOT exist in v1.3.4 export
                    assert (
                        "dependency_rule" not in row
                    ), "dependency_rule should not be in export"
                    assert (
                        "business_rule" not in row
                    ), "business_rule should not be in export"

                    # Enhanced: allowed_values now auto-inferred for categorical data
                    if row["data_type"] == "categorical":
                        assert (
                            row["allowed_values"] != ""
                        )  # Should be auto-inferred for categorical

                    # v1.3.4: Check all inferrable fields are present and populated
                    assert row["role"] in [
                        "identifier",
                        "feature",
                        "target",
                        "time_index",
                        "group_by",
                        "ignore",
                    ]
                    assert row["do_not_impute"] in ["TRUE", "FALSE"]
                    assert row["time_index"] in ["TRUE", "FALSE"]
                    assert row["group_by"] in ["TRUE", "FALSE"]
                    assert row["nullable"] in ["TRUE", "FALSE"]
                    # Description should contain auto-inferred info
                    assert "Auto-inferred" in row["description"]

        finally:
            import shutil

            shutil.rmtree(temp_dir)


class TestInitCommandEdgeCases:
    """Test edge cases for the init command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_init_with_unicode_data(self):
        """Test init command with Unicode characters in data."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create data with Unicode characters
            unicode_data = """name,description,price
José,Café especial,€15.50
María,Niño pequeño,¥1000
François,Crème brûlée,£8.75"""

            data_path = os.path.join(temp_dir, "unicode.csv")
            with open(data_path, "w", encoding="utf-8") as f:
                f.write(unicode_data)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                assert result.exit_code == 0
                assert os.path.exists("metadata.csv")

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_init_with_large_dataset(self):
        """Test init command with larger dataset."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create a larger dataset
            import pandas as pd

            large_df = pd.DataFrame(
                {
                    "id": range(1000),
                    "value": [i * 1.5 for i in range(1000)],
                    "category": (["A", "B", "C"] * 334)[
                        :1000
                    ],  # Ensure exactly 1000 items
                    "flag": ([True, False] * 500)[:1000],  # Ensure exactly 1000 items
                }
            )

            data_path = os.path.join(temp_dir, "large.csv")
            large_df.to_csv(data_path, index=False)

            with self.runner.isolated_filesystem():
                result = self.runner.invoke(cli, ["init", "-d", data_path])

                assert result.exit_code == 0
                assert "📊 Analyzed 4 columns" in result.output

        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_v134_regression_protection(self):
        """Comprehensive test to prevent regression of v1.3.4 field export fix."""
        temp_dir = tempfile.mkdtemp()

        try:
            # Create realistic test data with various patterns
            test_data = """customer_id,age,income,category,loyalty_score,is_premium,last_purchase,num_orders
C001,25,45000,Electronics,8.5,true,2024-01-15,15
C002,32,65000,Clothing,7.2,false,2024-02-20,8
C003,,72000,Electronics,,true,,22
C004,45,,Books,9.1,false,2024-03-10,31
C005,28,58000,,6.8,false,2024-01-28,"""

            data_path = os.path.join(temp_dir, "regression_test.csv")
            with open(data_path, "w") as f:
                f.write(test_data)

            with self.runner.isolated_filesystem():
                # Test 1: Init command field count
                result = self.runner.invoke(
                    cli, ["init", "-d", data_path, "-o", "meta.csv"]
                )
                assert result.exit_code == 0

                with open("meta.csv", "r") as f:
                    import csv

                    reader = csv.DictReader(f)
                    fieldnames = reader.fieldnames
                    rows = list(reader)

                # Critical regression checks
                regression_checks = {
                    "Exactly 15 fields": len(fieldnames) == 15,
                    "No business_rule": "business_rule" not in fieldnames,
                    "No dependency_rule": "dependency_rule" not in fieldnames,
                    "No meaning_of_missing": "meaning_of_missing" not in fieldnames,
                    "No order_by": "order_by" not in fieldnames,
                    "No fallback_method": "fallback_method" not in fieldnames,
                    "Has role": "role" in fieldnames,
                    "Has do_not_impute": "do_not_impute" in fieldnames,
                    "Has time_index": "time_index" in fieldnames,
                    "Has group_by": "group_by" in fieldnames,
                    "Has sentinel_values": "sentinel_values" in fieldnames,
                    "All rows analyzed": len(rows) == 8,  # All 8 columns
                }

                # Report any failures
                failures = [
                    check for check, passed in regression_checks.items() if not passed
                ]
                assert len(failures) == 0, f"Regression checks failed: {failures}"

                # Test 2: Auto-inference API still works
                import pandas as pd
                from funputer import analyze_imputation_requirements

                df = pd.read_csv(data_path)
                suggestions = analyze_imputation_requirements(df)

                # Should have suggestions for columns with missing data
                cols_with_missing = [
                    col for col in df.columns if df[col].isna().sum() > 0
                ]
                suggestion_columns = [
                    s.column_name for s in suggestions if s.missing_count > 0
                ]

                for col in cols_with_missing:
                    assert col in suggestion_columns, f"Missing suggestion for {col}"

                # Test 3: Metadata → Analysis workflow
                from funputer import analyze_dataframe
                from funputer.metadata_inference import infer_metadata_from_dataframe

                inferred_meta = infer_metadata_from_dataframe(df, warn_user=False)
                suggestions2 = analyze_dataframe(df, inferred_meta)

                # Should get same suggestion count
                assert len(suggestions) == len(
                    suggestions2
                ), "Inconsistent suggestion counts"

        finally:
            import shutil

            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
