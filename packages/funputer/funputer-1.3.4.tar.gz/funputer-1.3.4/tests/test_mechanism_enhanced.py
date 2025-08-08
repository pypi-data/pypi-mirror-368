#!/usr/bin/env python3
"""
Enhanced test suite for mechanism detection module.
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

from funputer.mechanism import (
    analyze_missingness_mechanism,
    find_related_columns,
    chi_square_test,
    point_biserial_test,
)
from funputer.models import (
    MissingnessAnalysis,
    MissingnessType,
    ColumnMetadata,
    AnalysisConfig,
)


class TestMechanismEnhanced:
    """Enhanced tests for missingness mechanism detection."""

    def create_test_dataframe(self, missing_pattern="random"):
        """Create test DataFrame with different missing patterns."""
        np.random.seed(42)  # For reproducibility

        n_rows = 1000

        # Base data
        df = pd.DataFrame(
            {
                "age": np.random.normal(35, 10, n_rows),
                "income": np.random.normal(50000, 15000, n_rows),
                "education": np.random.choice(["HS", "College", "Graduate"], n_rows),
                "score": np.random.normal(75, 15, n_rows),
            }
        )

        if missing_pattern == "random":
            # MCAR - completely random missing
            missing_mask = np.random.random(n_rows) < 0.1
            df.loc[missing_mask, "income"] = np.nan

        elif missing_pattern == "age_dependent":
            # MAR - missing depends on age
            missing_mask = (
                df["age"] > 50
            )  # Older people more likely to have missing income
            missing_mask = missing_mask & (np.random.random(n_rows) < 0.3)
            df.loc[missing_mask, "income"] = np.nan

        elif missing_pattern == "income_dependent":
            # MNAR - missing depends on income itself (high earners don't report)
            missing_mask = df["income"] > 70000
            missing_mask = missing_mask & (np.random.random(n_rows) < 0.4)
            df.loc[missing_mask, "income"] = np.nan

        elif missing_pattern == "complex":
            # Complex MAR pattern - depends on multiple variables
            missing_mask = ((df["age"] > 40) & (df["education"] == "Graduate")) | (
                (df["score"] < 60) & (df["education"] == "HS")
            )
            missing_mask = missing_mask & (np.random.random(n_rows) < 0.2)
            df.loc[missing_mask, "income"] = np.nan

        return df

    # Test mechanism analysis
    def test_analyze_missingness_mechanism_basic(self):
        """Test basic mechanism analysis."""
        df = self.create_test_dataframe("random")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        config = AnalysisConfig()
        result = analyze_missingness_mechanism("income", df, metadata_dict, config)

        assert isinstance(result, MissingnessAnalysis)
        assert result.missing_count >= 0

    def test_mechanism_analysis_with_age_dependent(self):
        """Test mechanism analysis with age-dependent missing data."""
        df = self.create_test_dataframe("age_dependent")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        config = AnalysisConfig()
        result = analyze_missingness_mechanism("income", df, metadata_dict, config)

        assert isinstance(result, MissingnessAnalysis)
        assert result.mechanism in [
            MissingnessType.MAR,
            MissingnessType.MCAR,
            MissingnessType.UNKNOWN,
        ]

    def test_mechanism_with_insufficient_data(self):
        """Test mechanism analysis with insufficient data."""
        df = pd.DataFrame({"col1": [1, 2, np.nan], "col2": [1, 2, 3]})

        metadata_dict = {
            "col1": ColumnMetadata(column_name="col1", data_type="float"),
            "col2": ColumnMetadata(column_name="col2", data_type="float"),
        }
        config = AnalysisConfig()
        result = analyze_missingness_mechanism("col1", df, metadata_dict, config)

        # Should handle gracefully
        assert isinstance(result, MissingnessAnalysis)
        assert result.missing_count >= 0

    def test_mechanism_no_missing_data(self):
        """Test mechanism analysis with no missing data."""
        df = pd.DataFrame({"col1": [1, 2, 3, 4, 5], "col2": [1, 2, 3, 4, 5]})

        metadata_dict = {
            "col1": ColumnMetadata(column_name="col1", data_type="float"),
            "col2": ColumnMetadata(column_name="col2", data_type="float"),
        }
        config = AnalysisConfig()
        result = analyze_missingness_mechanism("col1", df, metadata_dict, config)

        # Should return appropriate result for no missing data
        assert isinstance(result, MissingnessAnalysis)
        assert result.missing_count == 0

    def test_mechanism_all_missing_data(self):
        """Test mechanism analysis with all missing data."""
        df = pd.DataFrame({"col1": [np.nan, np.nan, np.nan], "col2": [1, 2, 3]})

        metadata_dict = {
            "col1": ColumnMetadata(column_name="col1", data_type="float"),
            "col2": ColumnMetadata(column_name="col2", data_type="float"),
        }
        config = AnalysisConfig()
        result = analyze_missingness_mechanism("col1", df, metadata_dict, config)

        # Should handle all-missing case
        assert isinstance(result, MissingnessAnalysis)
        assert result.missing_count == 3

    # Test related columns finding
    def test_find_related_columns_basic(self):
        """Test finding related columns with correlation."""
        df = self.create_test_dataframe("age_dependent")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        result = find_related_columns("income", df, metadata_dict)

        assert isinstance(result, list)
        # Should find some related columns

    def test_find_related_columns_random(self):
        """Test finding related columns with random missing data."""
        df = self.create_test_dataframe("random")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        result = find_related_columns("income", df, metadata_dict)

        assert isinstance(result, list)
        # May find some columns but fewer than with systematic missingness

    def test_find_related_columns_multiple(self):
        """Test finding related columns with complex patterns."""
        df = self.create_test_dataframe("complex")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        result = find_related_columns("income", df, metadata_dict)

        assert isinstance(result, list)

    def test_chi_square_test_basic(self):
        """Test chi-square test with basic data."""
        df = self.create_test_dataframe("random")

        result = chi_square_test(df["income"], df["education"])

        # Should return some statistical result
        assert result is not None

    def test_point_biserial_test_basic(self):
        """Test point-biserial correlation test."""
        df = self.create_test_dataframe("random")

        # Create binary variable for point-biserial test
        df["binary"] = df["age"] > df["age"].median()

        result = point_biserial_test(df["income"], df["binary"])

        # Should return correlation result
        assert result is not None

    def test_mechanism_detection_with_invalid_column(self):
        """Test mechanism detection with invalid column."""
        df = self.create_test_dataframe("random")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float")
        }
        config = AnalysisConfig()
        with pytest.raises(KeyError):
            analyze_missingness_mechanism(
                "nonexistent_column", df, metadata_dict, config
            )

    # Test edge cases and error handling
    def test_mechanism_detection_with_constant_column(self):
        """Test mechanism detection with constant values."""
        df = pd.DataFrame(
            {"constant": [1, 1, 1, 1, np.nan], "variable": [1, 2, 3, 4, 5]}
        )

        metadata_dict = {
            "constant": ColumnMetadata(column_name="constant", data_type="float"),
            "variable": ColumnMetadata(column_name="variable", data_type="float"),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("constant", df, metadata_dict, config)

        # Should handle constant values gracefully
        assert isinstance(analysis, MissingnessAnalysis)

    def test_mechanism_detection_with_extreme_outliers(self):
        """Test mechanism detection with extreme outliers."""
        df = pd.DataFrame({"col1": [1, 2, 3, 1000000, np.nan], "col2": [1, 2, 3, 4, 5]})

        metadata_dict = {
            "col1": ColumnMetadata(column_name="col1", data_type="float"),
            "col2": ColumnMetadata(column_name="col2", data_type="float"),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("col1", df, metadata_dict, config)

        # Should handle outliers without crashing
        assert isinstance(analysis, MissingnessAnalysis)

    def test_mechanism_detection_mixed_data_types(self):
        """Test mechanism detection with mixed data types."""
        df = pd.DataFrame(
            {"mixed": [1, "text", 3.14, True, np.nan], "numeric": [1, 2, 3, 4, 5]}
        )

        metadata_dict = {
            "mixed": ColumnMetadata(column_name="mixed", data_type="string"),
            "numeric": ColumnMetadata(column_name="numeric", data_type="float"),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("mixed", df, metadata_dict, config)

        # Should handle mixed types
        assert isinstance(analysis, MissingnessAnalysis)

    def test_large_dataset_performance(self):
        """Test mechanism detection performance on larger dataset."""
        np.random.seed(42)
        n_rows = 10000

        df = pd.DataFrame(
            {
                "target": np.random.normal(0, 1, n_rows),
                "predictor1": np.random.normal(0, 1, n_rows),
                "predictor2": np.random.choice(["A", "B", "C"], n_rows),
            }
        )

        # Add some missing values
        missing_mask = np.random.random(n_rows) < 0.05
        df.loc[missing_mask, "target"] = np.nan

        # Should complete in reasonable time
        metadata_dict = {
            "target": ColumnMetadata(column_name="target", data_type="float"),
            "predictor1": ColumnMetadata(column_name="predictor1", data_type="float"),
            "predictor2": ColumnMetadata(
                column_name="predictor2", data_type="categorical"
            ),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("target", df, metadata_dict, config)

        assert isinstance(analysis, MissingnessAnalysis)
        assert analysis.missing_count > 0

    def test_mechanism_detection_confidence_scores(self):
        """Test that mechanism detection provides confidence scores."""
        df = self.create_test_dataframe("age_dependent")

        metadata_dict = {
            "income": ColumnMetadata(column_name="income", data_type="float"),
            "age": ColumnMetadata(column_name="age", data_type="float"),
            "education": ColumnMetadata(
                column_name="education", data_type="categorical"
            ),
            "score": ColumnMetadata(column_name="score", data_type="float"),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("income", df, metadata_dict, config)

        assert hasattr(analysis, "confidence")
        if hasattr(analysis, "confidence"):
            assert 0 <= analysis.confidence <= 1

    def test_mechanism_detection_with_multicollinearity(self):
        """Test mechanism detection with highly correlated predictors."""
        df = pd.DataFrame(
            {
                "target": np.random.normal(0, 1, 1000),
                "pred1": np.random.normal(0, 1, 1000),
            }
        )
        df["pred2"] = df["pred1"] + np.random.normal(0, 0.1, 1000)  # Highly correlated

        # Add missing values
        missing_mask = df["pred1"] > 1
        df.loc[missing_mask, "target"] = np.nan

        metadata_dict = {
            "target": ColumnMetadata(column_name="target", data_type="float"),
            "pred1": ColumnMetadata(column_name="pred1", data_type="float"),
            "pred2": ColumnMetadata(column_name="pred2", data_type="float"),
        }
        config = AnalysisConfig()
        analysis = analyze_missingness_mechanism("target", df, metadata_dict, config)

        # Should handle multicollinearity without crashing
        assert isinstance(analysis, MissingnessAnalysis)


if __name__ == "__main__":
    pytest.main([__file__])
