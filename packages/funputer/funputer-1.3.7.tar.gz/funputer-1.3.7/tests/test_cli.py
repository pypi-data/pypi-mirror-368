"""
Tests for CLI interfaces.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from funputer.simple_cli import cli
from funputer.models import ImputationSuggestion


class TestSimpleCLI:
    """Test the simple CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def create_temp_files(self):
        """Create temporary CSV files for testing."""
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Create sample data CSV
        data_content = """id,age,income,category
1,25,50000,A
2,,60000,B
3,35,,A
4,42,80000,C
5,,55000,B"""

        data_path = os.path.join(temp_dir, "test_data.csv")
        with open(data_path, "w") as f:
            f.write(data_content)

        # Create sample metadata CSV
        metadata_content = """column_name,data_type,role,do_not_impute,time_index,group_by,unique_flag,nullable,min_value,max_value,max_length,allowed_values,dependent_column,sentinel_values,description
id,integer,identifier,true,false,false,true,false,1,999999,,,,,User identifier
age,integer,feature,false,false,false,false,true,18,100,,,,,User age
income,float,feature,false,false,false,false,true,0,,,,age,,Annual income
category,categorical,feature,false,false,false,false,true,,,10,,,,"User category" """

        metadata_path = os.path.join(temp_dir, "test_metadata.csv")
        with open(metadata_path, "w") as f:
            f.write(metadata_content)

        return data_path, metadata_path, temp_dir

    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze dataset and suggest imputation methods" in result.output
        assert "--metadata" in result.output
        assert "--data" in result.output
        assert "--output" in result.output
        assert "--verbose" in result.output

    def test_cli_missing_required_args(self):
        """Test CLI with missing required arguments."""
        # Missing both metadata and data - should fail
        result = self.runner.invoke(cli, ["analyze"])
        assert result.exit_code != 0

        # Missing data argument - should fail
        result = self.runner.invoke(cli, ["analyze", "-m", "metadata.csv"])
        assert result.exit_code != 0

        # Data only is now valid (auto-inference mode) - should succeed with valid data
        # But will fail with non-existent file
        result = self.runner.invoke(cli, ["analyze", "-d", "nonexistent.csv"])
        assert result.exit_code != 0

    def test_cli_basic_execution(self):
        """Test basic CLI execution with valid files."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli, ["analyze", "-m", metadata_path, "-d", data_path]
                )

                assert result.exit_code == 0
                assert "✓ Analysis complete!" in result.output
                assert "Columns analyzed:" in result.output
                assert "Total missing values:" in result.output
                assert "Average confidence:" in result.output
                assert "Results saved to:" in result.output

                # Check that default output file was created
                assert os.path.exists("suggestions.csv")
        finally:
            # Cleanup
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_with_custom_output(self):
        """Test CLI with custom output file."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "-m",
                        metadata_path,
                        "-d",
                        data_path,
                        "-o",
                        "custom_output.csv",
                    ],
                )

                assert result.exit_code == 0
                assert "Results saved to: custom_output.csv" in result.output
                assert os.path.exists("custom_output.csv")
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_verbose_mode(self):
        """Test CLI with verbose output."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli, ["analyze", "-m", metadata_path, "-d", data_path, "--verbose"]
                )

                assert result.exit_code == 0
                # Verbose mode should show INFO level logs
                assert "INFO:" in result.output or "Analyzing" in result.output
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_with_config_file(self):
        """Test CLI with configuration file."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        # Create config file
        config_content = """iqr_multiplier: 2.0
correlation_threshold: 0.4
skewness_threshold: 1.5
missing_percentage_threshold: 0.8
outlier_percentage_threshold: 0.1"""

        config_path = os.path.join(temp_dir, "config.yml")
        with open(config_path, "w") as f:
            f.write(config_content)

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "-m",
                        metadata_path,
                        "-d",
                        data_path,
                        "-c",
                        config_path,
                    ],
                )

                assert result.exit_code == 0
                assert "✓ Analysis complete!" in result.output
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_file_not_found_error(self):
        """Test CLI with non-existent files."""
        result = self.runner.invoke(
            cli,
            ["analyze", "-m", "nonexistent_metadata.csv", "-d", "nonexistent_data.csv"],
        )

        assert result.exit_code == 1
        assert "Error: File not found" in result.output

    def test_cli_invalid_config_file(self):
        """Test CLI with invalid configuration file."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        # Create invalid config file
        config_path = os.path.join(temp_dir, "invalid_config.yml")
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "-m",
                        metadata_path,
                        "-d",
                        data_path,
                        "-c",
                        config_path,
                    ],
                )

                assert result.exit_code == 1
                assert "Error:" in result.output
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_output_format(self):
        """Test CLI output format and content."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli, ["analyze", "-m", metadata_path, "-d", data_path]
                )

                assert result.exit_code == 0

                # Check output format
                lines = result.output.split("\n")
                summary_lines = [
                    line
                    for line in lines
                    if "Columns analyzed:" in line
                    or "Total missing values:" in line
                    or "Average confidence:" in line
                ]

                assert len(summary_lines) >= 3

                # Check that method distribution is shown
                method_lines = [
                    line
                    for line in lines
                    if ":" in line
                    and any(
                        method in line
                        for method in [
                            "Mean",
                            "Median",
                            "Mode",
                            "Business Rule",
                            "No action needed",
                        ]
                    )
                ]
                assert len(method_lines) > 0
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_empty_suggestions_handling(self):
        """Test CLI handling when no suggestions are generated."""
        # Create minimal files that might result in no suggestions
        temp_dir = tempfile.mkdtemp()

        data_content = "id\n1\n2\n3"
        data_path = os.path.join(temp_dir, "minimal_data.csv")
        with open(data_path, "w") as f:
            f.write(data_content)

        metadata_content = """column_name,data_type
id,integer"""
        metadata_path = os.path.join(temp_dir, "minimal_metadata.csv")
        with open(metadata_path, "w") as f:
            f.write(metadata_content)

        try:
            with self.runner.isolated_filesystem():
                result = self.runner.invoke(
                    cli, ["analyze", "-m", metadata_path, "-d", data_path]
                )

                # Should handle empty or minimal suggestions gracefully
                assert result.exit_code == 0
                assert "✓ Analysis complete!" in result.output
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    @patch("funputer.simple_cli.analyze_imputation_requirements")
    def test_cli_analysis_exception_handling(self, mock_analyze):
        """Test CLI handling of analysis exceptions."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        # Mock the analysis function to raise an exception
        mock_analyze.side_effect = Exception("Analysis failed")

        try:
            result = self.runner.invoke(
                cli, ["analyze", "-m", metadata_path, "-d", data_path]
            )

            assert result.exit_code == 1
            assert "Error: Analysis failed" in result.output
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_short_and_long_options(self):
        """Test that both short and long option forms work."""
        data_path, metadata_path, temp_dir = self.create_temp_files()

        try:
            with self.runner.isolated_filesystem():
                # Test short options
                result_short = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "-m",
                        metadata_path,
                        "-d",
                        data_path,
                        "-o",
                        "short_output.csv",
                        "-v",
                    ],
                )

                assert result_short.exit_code == 0

                # Test long options
                result_long = self.runner.invoke(
                    cli,
                    [
                        "analyze",
                        "--metadata",
                        metadata_path,
                        "--data",
                        data_path,
                        "--output",
                        "long_output.csv",
                        "--verbose",
                    ],
                )

                assert result_long.exit_code == 0

                # Both should create output files
                assert os.path.exists("short_output.csv")
                assert os.path.exists("long_output.csv")
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    def test_cli_examples_in_help(self):
        """Test that CLI help includes usage examples."""
        result = self.runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0

        # Should contain examples
        assert "Examples:" in result.output
        assert "funputer analyze -m" in result.output


class TestCLIIntegration:
    """Test CLI integration with core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("funputer.simple_cli.analyze_imputation_requirements")
    @patch("funputer.simple_cli.save_suggestions")
    def test_cli_calls_correct_functions(self, mock_save, mock_analyze):
        """Test that CLI calls the correct underlying functions."""
        # Mock return value
        mock_suggestions = [
            ImputationSuggestion(
                column_name="test_col",
                proposed_method="Mean",
                rationale="Test rationale",
                missing_count=5,
                confidence_score=0.8,
            )
        ]
        mock_analyze.return_value = mock_suggestions

        result = self.runner.invoke(
            cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv", "-o", "output.csv"]
        )

        # Should call analyze function with correct parameters
        mock_analyze.assert_called_once()
        call_args = mock_analyze.call_args
        assert call_args[1]["metadata_path"] == "metadata.csv"
        assert call_args[1]["data_path"] == "data.csv"

        # Should call save function with suggestions and output path
        mock_save.assert_called_once_with(mock_suggestions, "output.csv")

        assert result.exit_code == 0

    def test_cli_confidence_score_division_by_zero_fix(self):
        """Test that the division by zero fix in CLI works correctly."""
        with patch(
            "funputer.simple_cli.analyze_imputation_requirements"
        ) as mock_analyze:
            # Mock empty suggestions (edge case that caused division by zero)
            mock_analyze.return_value = []

            with patch("funputer.simple_cli.save_suggestions"):
                result = self.runner.invoke(
                    cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv"]
                )

                # Should not crash with division by zero
                assert result.exit_code == 0
                assert (
                    "Average confidence: 0.000" in result.output
                )  # Should show 0.000 for empty list

    def test_cli_method_distribution_display(self):
        """Test that CLI correctly displays method distribution."""
        mock_suggestions = [
            ImputationSuggestion(
                column_name="col1", proposed_method="Mean", rationale="Test"
            ),
            ImputationSuggestion(
                column_name="col2", proposed_method="Mean", rationale="Test"
            ),
            ImputationSuggestion(
                column_name="col3", proposed_method="Mode", rationale="Test"
            ),
            ImputationSuggestion(
                column_name="col4", proposed_method="Business Rule", rationale="Test"
            ),
        ]

        with patch(
            "funputer.simple_cli.analyze_imputation_requirements"
        ) as mock_analyze:
            mock_analyze.return_value = mock_suggestions

            with patch("funputer.simple_cli.save_suggestions"):
                result = self.runner.invoke(
                    cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv"]
                )

                assert result.exit_code == 0

                # Should show method distribution
                assert "Proposed methods:" in result.output
                assert "Mean: 2" in result.output
                assert "Mode: 1" in result.output
                assert "Business Rule: 1" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_permission_error(self):
        """Test CLI handling of permission errors during file operations."""
        with patch(
            "funputer.simple_cli.analyze_imputation_requirements"
        ) as mock_analyze:
            mock_analyze.side_effect = PermissionError("Permission denied")

            result = self.runner.invoke(
                cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv"]
            )

            assert result.exit_code == 1
            assert "Error:" in result.output

    def test_cli_keyboard_interrupt(self):
        """Test CLI handling of keyboard interrupt."""
        with patch(
            "funputer.simple_cli.analyze_imputation_requirements"
        ) as mock_analyze:
            mock_analyze.side_effect = KeyboardInterrupt()

            result = self.runner.invoke(
                cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv"]
            )

            assert result.exit_code == 1

    def test_cli_memory_error(self):
        """Test CLI handling of memory errors."""
        with patch(
            "funputer.simple_cli.analyze_imputation_requirements"
        ) as mock_analyze:
            mock_analyze.side_effect = MemoryError("Out of memory")

            result = self.runner.invoke(
                cli, ["analyze", "-m", "metadata.csv", "-d", "data.csv"]
            )

            assert result.exit_code == 1
            assert "Error:" in result.output
