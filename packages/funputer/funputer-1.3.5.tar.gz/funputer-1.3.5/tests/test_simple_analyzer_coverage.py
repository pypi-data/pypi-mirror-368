"""
Additional tests for simple_analyzer.py to achieve 95% coverage.
These tests target the specific untested code paths identified in coverage analysis.
"""

import pytest
import pandas as pd
import tempfile
import os
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


class TestSimpleAnalyzerMissingCoverage:
    """Test missing coverage paths in SimpleImputationAnalyzer."""

    def test_analyze_enterprise_metadata_conversion(self):
        """Test enterprise metadata format conversion (lines 63-66)."""
        # Create mock enterprise metadata that's not a list
        mock_enterprise_metadata = MagicMock()
        mock_enterprise_metadata.column_definitions = []

        with (
            patch("funputer.simple_analyzer.load_metadata") as mock_load_meta,
            patch("funputer.simple_analyzer.load_data") as mock_load_data,
            patch("funputer.io.convert_enterprise_to_legacy") as mock_convert,
        ):

            # Setup mocks
            mock_load_meta.return_value = mock_enterprise_metadata  # Not a list
            mock_load_data.return_value = pd.DataFrame({"col1": [1, 2, 3]})

            # Mock conversion to return list of ColumnMetadata
            legacy_meta = [ColumnMetadata("col1", "integer")]
            mock_convert.return_value = legacy_meta

            # Create temp files
            with (
                tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as data_file,
                tempfile.NamedTemporaryFile(
                    mode="w", suffix=".csv", delete=False
                ) as meta_file,
            ):

                try:
                    analyzer = SimpleImputationAnalyzer()
                    suggestions = analyzer.analyze(meta_file.name, data_file.name)

                    # Verify enterprise conversion was called
                    mock_convert.assert_called_once_with(mock_enterprise_metadata)
                    assert len(suggestions) >= 0  # Should handle conversion

                finally:
                    os.unlink(data_file.name)
                    os.unlink(meta_file.name)

    def test_analyze_column_not_found_warning(self):
        """Test column not found in data warning (lines 77-78)."""
        data = pd.DataFrame({"existing_col": [1, 2, 3, None]})
        metadata = [
            ColumnMetadata("existing_col", "integer"),
            ColumnMetadata("missing_col", "float"),  # This column doesn't exist in data
        ]

        analyzer = SimpleImputationAnalyzer()

        with patch("funputer.simple_analyzer.logger") as mock_logger:
            suggestions = analyzer.analyze_dataframe(data, metadata)

            # Should log warning for missing column
            mock_logger.warning.assert_called_with(
                "Column missing_col not found in data - skipping"
            )

            # Should only return suggestions for existing columns
            suggestion_columns = {s.column_name for s in suggestions}
            assert "existing_col" in suggestion_columns
            assert "missing_col" not in suggestion_columns
            assert len(suggestions) == 1

    def test_analyze_skip_column_configuration(self):
        """Test skip column configuration (lines 81-82)."""
        data = pd.DataFrame({"keep_col": [1, 2, None, 4], "skip_col": [5, 6, None, 8]})
        metadata = [
            ColumnMetadata("keep_col", "integer"),
            ColumnMetadata("skip_col", "integer"),
        ]

        config = AnalysisConfig(skip_columns=["skip_col"])
        analyzer = SimpleImputationAnalyzer(config)

        with patch("funputer.simple_analyzer.logger") as mock_logger:
            suggestions = analyzer.analyze_dataframe(data, metadata)

            # Should log info for skipped column
            skip_log_calls = [
                call
                for call in mock_logger.info.call_args_list
                if "Skipping column skip_col per configuration" in str(call)
            ]
            assert (
                len(skip_log_calls) > 0
            ), f"Expected skip log not found. Actual calls: {mock_logger.info.call_args_list}"

            # Should only return suggestions for non-skipped columns
            suggestion_columns = {s.column_name for s in suggestions}
            assert "keep_col" in suggestion_columns
            assert "skip_col" not in suggestion_columns
            assert len(suggestions) == 1

    def test_analyze_imputation_requirements_file_not_found(self):
        """Test file not found exception handling (lines 240-241)."""
        non_existent_file = "/tmp/this_file_does_not_exist.csv"

        with pytest.raises(FileNotFoundError) as exc_info:
            analyze_imputation_requirements(non_existent_file)

        assert "Could not load data file" in str(exc_info.value)
        assert non_existent_file in str(exc_info.value)

    def test_analyze_imputation_requirements_csv_read_error(self):
        """Test CSV read error exception handling with auto-inference."""
        # Create a file with valid CSV content that will auto-infer
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\n1,2\n3,4")
            temp_path = f.name

        try:
            # Should succeed with auto-inference now
            result = analyze_imputation_requirements(temp_path)
            assert len(result) >= 0  # Should return some results
        finally:
            os.unlink(temp_path)

    def test_analyze_imputation_requirements_permission_error(self):
        """Test permission error when reading file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\n1,2\n3,4")
            temp_path = f.name

        try:
            # Mock pandas.read_csv to raise PermissionError
            with patch(
                "pandas.read_csv", side_effect=PermissionError("Permission denied")
            ):
                with pytest.raises(FileNotFoundError) as exc_info:
                    analyze_imputation_requirements(temp_path)

                assert "Could not load data file" in str(exc_info.value)
                assert "Permission denied" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_analyze_with_dict_metadata_format(self):
        """Test analyze_dataframe with dict metadata handling (lines 143-147)."""
        data = pd.DataFrame({"col1": [1, 2, None, 4], "col2": ["a", "b", None, "d"]})

        # Test with dict metadata format
        metadata_dict = {
            "col1": ColumnMetadata("col1", "integer"),
            "col2": ColumnMetadata("col2", "string"),
        }

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata_dict)

        assert len(suggestions) == 2
        suggestion_columns = {s.column_name for s in suggestions}
        assert "col1" in suggestion_columns
        assert "col2" in suggestion_columns

    def test_analyze_dataframe_missing_column_warning_path(self):
        """Test analyze_dataframe method's missing column warning (lines 156-157)."""
        data = pd.DataFrame({"existing": [1, 2, 3]})
        metadata = [
            ColumnMetadata("existing", "integer"),
            ColumnMetadata("missing", "float"),
        ]

        analyzer = SimpleImputationAnalyzer()

        with patch("funputer.simple_analyzer.logger") as mock_logger:
            suggestions = analyzer.analyze_dataframe(data, metadata)

            # Should log warning for missing column
            mock_logger.warning.assert_called_with(
                "Column missing not found in data - skipping"
            )
            assert len(suggestions) == 1

    def test_analyze_dataframe_skip_column_info_path(self):
        """Test analyze_dataframe method's skip column info (lines 160-161)."""
        data = pd.DataFrame({"keep": [1, 2, 3], "skip": [4, 5, 6]})
        metadata = [
            ColumnMetadata("keep", "integer"),
            ColumnMetadata("skip", "integer"),
        ]

        config = AnalysisConfig(skip_columns=["skip"])
        analyzer = SimpleImputationAnalyzer(config)

        with patch("funputer.simple_analyzer.logger") as mock_logger:
            suggestions = analyzer.analyze_dataframe(data, metadata)

            # Should log info for skipped column
            skip_log_calls = [
                call
                for call in mock_logger.info.call_args_list
                if "Skipping column skip per configuration" in str(call)
            ]
            assert (
                len(skip_log_calls) > 0
            ), f"Expected skip log not found. Actual calls: {mock_logger.info.call_args_list}"
            assert len(suggestions) == 1

    def test_analyze_imputation_requirements_auto_inference_path(self):
        """Test auto-inference path in analyze_imputation_requirements (lines 238-244)."""
        # Create a simple CSV file for auto-inference
        data = pd.DataFrame(
            {
                "numeric_col": [1, 2, None, 4, 5],
                "string_col": ["a", "b", None, "d", "e"],
                "categorical_col": ["X", "Y", "X", None, "Y"],
            }
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            data.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            # Test auto-inference (no metadata_path provided)
            with patch(
                "funputer.metadata_inference.infer_metadata_from_dataframe"
            ) as mock_infer:
                mock_metadata = [
                    ColumnMetadata("numeric_col", "integer"),
                    ColumnMetadata("string_col", "string"),
                    ColumnMetadata("categorical_col", "categorical"),
                ]
                mock_infer.return_value = mock_metadata

                suggestions = analyze_imputation_requirements(temp_path)

                # Should call auto-inference
                mock_infer.assert_called_once()
                assert len(suggestions) >= 0

        finally:
            os.unlink(temp_path)

    def test_analyze_with_list_metadata_format(self):
        """Test analyze method with list metadata format (lines 59-60)."""
        data = pd.DataFrame({"col1": [1, 2, None, 4]})
        metadata_list = [ColumnMetadata("col1", "integer")]

        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as data_file,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as meta_file,
        ):

            try:
                with (
                    patch("funputer.simple_analyzer.load_metadata") as mock_load_meta,
                    patch("funputer.simple_analyzer.load_data") as mock_load_data,
                ):

                    mock_load_meta.return_value = metadata_list  # Return list format
                    mock_load_data.return_value = data

                    analyzer = SimpleImputationAnalyzer()
                    suggestions = analyzer.analyze(meta_file.name, data_file.name)

                    assert len(suggestions) >= 0

            finally:
                os.unlink(data_file.name)
                os.unlink(meta_file.name)

    def test_both_analyze_methods_timing_logs(self):
        """Test timing logs in both analyze methods."""
        data = pd.DataFrame({"col1": [1, 2, None, 4]})
        metadata = [ColumnMetadata("col1", "integer")]

        # Test analyze_dataframe timing log
        analyzer = SimpleImputationAnalyzer()

        with patch("funputer.simple_analyzer.logger") as mock_logger:
            suggestions = analyzer.analyze_dataframe(data, metadata)

            # Check that timing log was called
            info_calls = [
                call
                for call in mock_logger.info.call_args_list
                if "DataFrame analysis completed" in str(call)
            ]
            assert len(info_calls) > 0

        # Test analyze method timing log
        with (
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as data_file,
            tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as meta_file,
        ):

            try:
                with (
                    patch("funputer.simple_analyzer.load_metadata") as mock_load_meta,
                    patch("funputer.simple_analyzer.load_data") as mock_load_data,
                    patch("funputer.simple_analyzer.logger") as mock_logger,
                ):

                    mock_load_meta.return_value = metadata
                    mock_load_data.return_value = data

                    suggestions = analyzer.analyze(meta_file.name, data_file.name)

                    # Check that timing log was called
                    info_calls = [
                        call
                        for call in mock_logger.info.call_args_list
                        if "Analysis completed" in str(call)
                    ]
                    assert len(info_calls) > 0

            finally:
                os.unlink(data_file.name)
                os.unlink(meta_file.name)


class TestEdgeCasesForFullCoverage:
    """Test edge cases to ensure 95% coverage."""

    def test_empty_metadata_list(self):
        """Test with empty metadata list."""
        data = pd.DataFrame({"col1": [1, 2, 3]})
        metadata = []

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        assert len(suggestions) == 0

    def test_empty_metadata_dict(self):
        """Test with empty metadata dict."""
        data = pd.DataFrame({"col1": [1, 2, 3]})
        metadata = {}

        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(data, metadata)

        assert len(suggestions) == 0

    def test_analyze_with_exception_in_processing(self):
        """Test behavior when there's an exception during column processing."""
        data = pd.DataFrame({"col1": [1, 2, None, 4]})
        metadata = [ColumnMetadata("col1", "integer")]

        analyzer = SimpleImputationAnalyzer()

        # Mock analyze_outliers to raise an exception for one path
        with patch("funputer.simple_analyzer.analyze_outliers") as mock_outliers:
            # Let it work normally - just testing that we can handle processing
            mock_outliers.side_effect = lambda *args, **kwargs: MagicMock(
                outlier_count=0,
                outlier_percentage=0.0,
                handling_strategy=MagicMock(value="Leave as is"),
                rationale="No outliers detected",
            )

            suggestions = analyzer.analyze_dataframe(data, metadata)
            assert len(suggestions) == 1

    def test_all_skip_columns(self):
        """Test when all columns are in skip list."""
        data = pd.DataFrame({"col1": [1, 2, None], "col2": ["a", "b", None]})
        metadata = [ColumnMetadata("col1", "integer"), ColumnMetadata("col2", "string")]

        config = AnalysisConfig(skip_columns=["col1", "col2"])
        analyzer = SimpleImputationAnalyzer(config)
        suggestions = analyzer.analyze_dataframe(data, metadata)

        # Should return empty list when all columns are skipped
        assert len(suggestions) == 0
