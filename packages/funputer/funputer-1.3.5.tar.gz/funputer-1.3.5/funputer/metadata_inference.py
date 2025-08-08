"""
Automatic metadata inference from pandas DataFrames.

This module provides intelligent inference of column metadata when no explicit
metadata file is provided, making funimputer more accessible while maintaining accuracy.
"""

import pandas as pd
import numpy as np
import logging
import warnings
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import re

from .models import ColumnMetadata

# Suppress pandas warnings for cleaner output
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)
warnings.filterwarnings("ignore", message="Could not infer format")
warnings.filterwarnings("ignore", message=".*falling back to `dateutil`.*")

logger = logging.getLogger(__name__)


class MetadataInferenceEngine:
    """Intelligent metadata inference engine for pandas DataFrames."""

    def __init__(
        self,
        categorical_threshold_ratio: float = 0.1,
        categorical_threshold_absolute: int = 50,
        datetime_sample_size: int = 100,
        min_rows_for_stats: int = 10,
    ):
        """
        Initialize the inference engine.

        Args:
            categorical_threshold_ratio: Ratio of unique values to total for categorical detection
            categorical_threshold_absolute: Absolute max unique values for categorical
            datetime_sample_size: Number of samples to check for datetime patterns
            min_rows_for_stats: Minimum rows needed for statistical analysis
        """
        self.categorical_threshold_ratio = categorical_threshold_ratio
        self.categorical_threshold_absolute = categorical_threshold_absolute
        self.datetime_sample_size = datetime_sample_size
        self.min_rows_for_stats = min_rows_for_stats

        # Common datetime patterns to detect
        self.datetime_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
            r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
            r"\d{4}/\d{2}/\d{2}",  # YYYY/MM/DD
            r"\d{2}/\d{2}/\d{2}",  # MM/DD/YY
        ]

        # Common boolean representations
        self.boolean_values = {
            "true",
            "false",
            "yes",
            "no",
            "1",
            "0",
            "y",
            "n",
            "t",
            "f",
            "on",
            "off",
        }

    def infer_dataframe_metadata(
        self, df: pd.DataFrame, warn_user: bool = True
    ) -> List[ColumnMetadata]:
        """
        Infer metadata for all columns in a DataFrame.

        Args:
            df: DataFrame to analyze
            warn_user: Whether to warn about inference limitations

        Returns:
            List of ColumnMetadata objects
        """
        if warn_user:
            logger.warning(
                "🤖 AUTO-INFERRING METADATA: No metadata file provided. "
                "Using intelligent inference with reduced accuracy. "
                "For best results, provide explicit metadata file."
            )

        logger.info(
            f"Inferring metadata for {len(df.columns)} columns in DataFrame with {len(df)} rows"
        )

        metadata_list = []

        for column_name in df.columns:
            try:
                metadata = self._infer_column_metadata(df, column_name)
                metadata_list.append(metadata)
                logger.debug(f"Inferred {column_name}: {metadata.data_type}")
            except Exception as e:
                logger.warning(
                    f"Failed to infer metadata for column '{column_name}': {e}"
                )
                # Fallback to string type
                fallback_metadata = ColumnMetadata(
                    column_name=str(column_name),
                    data_type="string",
                    nullable=True,
                    description=f"Fallback inference (error: {str(e)[:50]})",
                )
                metadata_list.append(fallback_metadata)

        logger.info(f"Successfully inferred metadata for {len(metadata_list)} columns")
        return metadata_list

    def _infer_column_metadata(
        self, df: pd.DataFrame, column_name: str
    ) -> ColumnMetadata:
        """Infer metadata for a single column."""
        series = df[column_name]

        # Basic info
        total_count = len(series)
        null_count = series.isnull().sum()
        non_null_series = series.dropna()

        # Determine data type
        data_type = self._infer_data_type(series, non_null_series)

        # Determine constraints
        min_value, max_value, max_length = self._infer_constraints(
            non_null_series, data_type
        )

        # Determine uniqueness
        unique_flag = self._infer_uniqueness(non_null_series, total_count)

        # Infer allowed values for categorical/boolean data
        allowed_values = self._infer_allowed_values(non_null_series, data_type)

        # Infer dependent column relationships
        dependent_column = self._infer_dependent_column(column_name, df, data_type)

        # Generate description
        description = self._generate_description(series, data_type, unique_flag)

        # Infer enhanced metadata
        role = self._infer_role(
            column_name,
            data_type,
            unique_flag,
            df.columns.get_loc(column_name),
            len(df.columns),
        )
        do_not_impute = self._infer_do_not_impute(role, unique_flag)
        sentinel_values = self._infer_sentinel_values(non_null_series, data_type)
        time_index = self._infer_time_index(column_name, data_type)
        group_by = self._infer_group_by(column_name, data_type, non_null_series)

        # Return inference-only ColumnMetadata (15 fields)
        return ColumnMetadata(
            column_name=str(column_name),
            data_type=data_type,
            min_value=min_value,
            max_value=max_value,
            max_length=max_length,
            unique_flag=unique_flag,
            nullable=(null_count > 0),
            allowed_values=allowed_values,
            dependent_column=dependent_column,
            description=description,
            # Enhanced fields
            role=role,
            do_not_impute=do_not_impute,
            sentinel_values=sentinel_values,
            time_index=time_index,
            group_by=group_by,
        )

    def _infer_data_type(self, series: pd.Series, non_null_series: pd.Series) -> str:
        """Infer the data type of a series."""
        if len(non_null_series) == 0:
            return "string"  # Default for all-null columns

        # Check pandas dtype first
        dtype_str = str(series.dtype).lower()

        # Handle numeric types
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "integer" if self._could_be_integer(non_null_series) else "float"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        # Handle object/string columns - need deeper analysis
        if dtype_str in ["object", "string"]:
            return self._infer_object_type(non_null_series)

        # Handle categorical
        if pd.api.types.is_categorical_dtype(series):
            return "categorical"

        # Default fallback
        return "string"

    def _could_be_integer(self, series: pd.Series) -> bool:
        """Check if float series could actually be integer."""
        if not pd.api.types.is_float_dtype(series):
            return False

        # Check if all non-null values are whole numbers
        non_null = series.dropna()
        if len(non_null) == 0:
            return False

        return np.all(non_null == non_null.astype(int))

    def _infer_object_type(self, series: pd.Series) -> str:
        """Infer type for object/string columns."""
        sample_size = min(len(series), self.datetime_sample_size)
        sample = series.head(sample_size)

        # Check for datetime patterns
        if self._is_datetime_column(sample):
            return "datetime"

        # Check for boolean patterns
        if self._is_boolean_column(sample):
            return "boolean"

        # Check for numeric strings
        if self._is_numeric_string_column(sample):
            return "float" if self._has_decimal_numbers(sample) else "integer"

        # Check for categorical
        if self._is_categorical_column(series):
            return "categorical"

        return "string"

    def _is_datetime_column(self, sample: pd.Series) -> bool:
        """Check if string column contains datetime values."""
        import warnings

        if len(sample) == 0:
            return False

        # Try pandas datetime parsing with common formats first
        common_formats = [
            "%Y-%m-%d",  # 2023-01-15
            "%m/%d/%Y",  # 01/15/2023
            "%d/%m/%Y",  # 15/01/2023
            "%Y/%m/%d",  # 2023/01/15
            "%m-%d-%Y",  # 01-15-2023
            "%d-%m-%Y",  # 15-01-2023
        ]

        # Try specific formats first to avoid warnings
        for fmt in common_formats:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    parsed = pd.to_datetime(sample, format=fmt, errors="coerce")
                    valid_ratio = parsed.notna().sum() / len(sample)
                    if valid_ratio > 0.8:  # 80% valid dates
                        return True
            except:
                continue

        # Fallback to general parsing with warning suppression
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(sample, errors="coerce")
                valid_ratio = parsed.notna().sum() / len(sample)
                if valid_ratio > 0.8:  # 80% valid dates
                    return True
        except:
            pass

        # Check regex patterns
        string_sample = sample.astype(str)
        for pattern in self.datetime_patterns:
            matches = string_sample.str.match(pattern, na=False).sum()
            if matches / len(sample) > 0.8:
                return True

        return False

    def _is_boolean_column(self, sample: pd.Series) -> bool:
        """Check if column contains boolean values."""
        if len(sample) == 0:
            return False

        unique_values = set(str(v).lower().strip() for v in sample.unique())
        return unique_values.issubset(self.boolean_values)

    def _is_numeric_string_column(self, sample: pd.Series) -> bool:
        """Check if string column contains numeric values."""
        if len(sample) == 0:
            return False

        try:
            numeric_converted = pd.to_numeric(sample, errors="coerce")
            valid_ratio = numeric_converted.notna().sum() / len(sample)
            return valid_ratio > 0.8  # 80% valid numbers
        except:
            return False

    def _has_decimal_numbers(self, sample: pd.Series) -> bool:
        """Check if numeric strings contain decimal numbers."""
        try:
            numeric_converted = pd.to_numeric(sample, errors="coerce")
            non_null = numeric_converted.dropna()
            if len(non_null) == 0:
                return False
            return not np.all(non_null == non_null.astype(int))
        except:
            return False

    def _is_categorical_column(self, series: pd.Series) -> bool:
        """Determine if a string column should be treated as categorical."""
        if len(series) < 2:
            return False

        unique_count = series.nunique()
        total_count = len(series)

        # Use both ratio and absolute thresholds
        ratio_check = (unique_count / total_count) <= self.categorical_threshold_ratio
        absolute_check = unique_count <= self.categorical_threshold_absolute

        return ratio_check or absolute_check

    def _infer_constraints(
        self, series: pd.Series, data_type: str
    ) -> Tuple[Optional[float], Optional[float], Optional[int]]:
        """Infer min/max values and max length constraints."""
        min_value = None
        max_value = None
        max_length = None

        if len(series) == 0:
            return min_value, max_value, max_length

        try:
            if data_type in ["integer", "float"]:
                # Set constraints if we have any data (be more permissive for small datasets)
                if len(series) >= 2:  # Need at least 2 values
                    min_value = float(series.min())
                    max_value = float(series.max())

            elif data_type in ["string", "categorical"]:
                # Get maximum string length
                string_lengths = series.astype(str).str.len()
                max_length = (
                    int(string_lengths.max()) if len(string_lengths) > 0 else None
                )

        except Exception as e:
            logger.debug(f"Failed to infer constraints: {e}")

        return min_value, max_value, max_length

    def _infer_uniqueness(self, series: pd.Series, total_count: int) -> bool:
        """Infer if column values should be unique."""
        if len(series) == 0 or total_count == 0:
            return False

        unique_count = series.nunique()

        # Check for ID-like column names first
        column_name = str(series.name).lower() if series.name else ""
        id_indicators = ["id", "key", "pk", "uuid", "guid", "_id", "identifier"]
        has_id_name = any(indicator in column_name for indicator in id_indicators)

        # Be conservative about uniqueness - only flag as unique if:
        # 1. Column name suggests it's an ID, OR
        # 2. All values are unique AND we have sufficient data AND values look like IDs
        if has_id_name and unique_count == len(series):
            return True

        # For non-ID named columns, require more evidence
        if unique_count == len(series) and len(series) >= 20:  # Need more data points
            # Check if values look like identifiers (sequential integers, etc.)
            if series.dtype in ["int64", "int32"] and len(series) > 1:
                # Check if it's a sequential ID (common pattern)
                sorted_vals = sorted(series.dropna())
                if len(sorted_vals) >= 2:
                    diffs = [
                        sorted_vals[i + 1] - sorted_vals[i]
                        for i in range(len(sorted_vals) - 1)
                    ]
                    # If mostly sequential (diff of 1), it's likely an ID
                    if sum(1 for d in diffs if d == 1) / len(diffs) > 0.8:
                        return True

        return False

    def _generate_description(
        self, series: pd.Series, data_type: str, unique_flag: bool
    ) -> str:
        """Generate a helpful description for the inferred column."""
        descriptions = []

        # Add type info
        descriptions.append(f"Auto-inferred {data_type} column")

        # Add uniqueness info
        if unique_flag:
            descriptions.append("appears to be unique identifier")

        # Add data characteristics
        null_pct = (series.isnull().sum() / len(series)) * 100 if len(series) > 0 else 0
        if null_pct > 10:
            descriptions.append(f"{null_pct:.1f}% missing values")

        if data_type == "categorical" and len(series) > 0:
            unique_count = series.nunique()
            descriptions.append(f"{unique_count} unique categories")

        return "; ".join(descriptions)

    def _infer_allowed_values(
        self, non_null_series: pd.Series, data_type: str
    ) -> Optional[str]:
        """
        Infer allowed values for categorical, boolean, and low-cardinality data.

        Returns comma-separated string of allowed values or None.
        """
        if len(non_null_series) == 0:
            return None

        unique_values = non_null_series.unique()
        num_unique = len(unique_values)

        # Boolean columns - always infer allowed values
        if data_type == "boolean":
            bool_values = sorted([str(v) for v in unique_values])
            return ",".join(bool_values)

        # Categorical columns with low cardinality
        if data_type == "categorical" and num_unique <= 20:
            # Sort values for consistency
            cat_values = sorted([str(v) for v in unique_values])
            return ",".join(cat_values)

        # String columns that look enum-like (low cardinality)
        if data_type == "string" and num_unique <= 10:
            str_values = sorted([str(v) for v in unique_values])
            return ",".join(str_values)

        # Integer columns that look enum-like (very low cardinality)
        if (
            data_type == "integer"
            and num_unique <= 5
            and all(isinstance(v, (int, np.integer)) for v in unique_values)
        ):
            int_values = sorted([str(int(v)) for v in unique_values])
            return ",".join(int_values)

        return None

    def _infer_dependent_column(
        self, column_name: str, df: pd.DataFrame, data_type: str
    ) -> Optional[str]:
        """
        Infer potential dependent column relationships through correlation analysis.

        Returns the most likely dependent column name or None.
        """
        if len(df) < 10:  # Need sufficient data for correlation
            return None

        target_series = df[column_name]
        if target_series.isnull().all():
            return None

        max_correlation = 0.0
        best_dependent = None
        correlation_threshold = 0.7  # Strong correlation threshold

        for other_col in df.columns:
            if other_col == column_name:
                continue

            other_series = df[other_col]
            if other_series.isnull().all():
                continue

            try:
                # Handle different data type combinations
                if data_type in ["integer", "float"] and pd.api.types.is_numeric_dtype(
                    other_series
                ):
                    # Numeric-numeric correlation
                    corr = target_series.corr(other_series)
                    if (
                        pd.notna(corr)
                        and abs(corr) > correlation_threshold
                        and abs(corr) > max_correlation
                    ):
                        max_correlation = abs(corr)
                        best_dependent = other_col

                elif (
                    data_type == "categorical"
                    and len(target_series.dropna().unique()) < 10
                ):
                    # Categorical dependency - check if one predicts the other
                    from scipy.stats import chi2_contingency

                    # Create contingency table
                    ct = pd.crosstab(target_series.dropna(), other_series.dropna())
                    if ct.size > 1:
                        chi2, p_value, _, _ = chi2_contingency(ct)
                        if p_value < 0.01:  # Strong statistical dependence
                            # Use Cramér's V as correlation measure
                            n = ct.sum().sum()
                            cramers_v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
                            if cramers_v > 0.7 and cramers_v > max_correlation:
                                max_correlation = cramers_v
                                best_dependent = other_col

            except (ValueError, Exception):
                # Skip if correlation calculation fails
                continue

        return best_dependent

    def _infer_role(
        self,
        column_name: str,
        data_type: str,
        unique_flag: bool,
        position: int,
        total_cols: int,
    ) -> str:
        """Infer the role of a column."""
        name_lower = column_name.lower()

        # Identifier patterns - first priority
        if unique_flag and (
            "id" in name_lower or "key" in name_lower or "uuid" in name_lower
        ):
            return "identifier"

        # Time index patterns
        if data_type == "datetime" and any(
            x in name_lower for x in ["time", "date", "timestamp"]
        ):
            return "time_index"

        # Target patterns (common ML target names or last column)
        target_indicators = [
            "target",
            "label",
            "outcome",
            "prediction",
            "y_",
            "class",
            "response",
        ]
        if any(x in name_lower for x in target_indicators) or (
            position == total_cols - 1 and total_cols > 3
        ):
            return "target"

        # Group-by patterns
        group_indicators = [
            "segment",
            "group",
            "category",
            "type",
            "class",
            "cohort",
            "bucket",
        ]
        if any(x in name_lower for x in group_indicators):
            return "group_by"

        # Ignore patterns
        ignore_indicators = ["temp", "debug", "test", "flag", "_internal", "system"]
        if any(x in name_lower for x in ignore_indicators):
            return "ignore"

        return "feature"  # Default

    def _infer_do_not_impute(self, role: str, unique_flag: bool) -> bool:
        """Infer if column should not be imputed."""
        # Never impute identifiers or targets
        if role in ["identifier", "target"]:
            return True

        # Never impute system/debug columns
        if role == "ignore":
            return True

        # Be cautious with unique columns that aren't features
        if unique_flag and role != "feature":
            return True

        return False

    def _infer_sentinel_values(
        self, series: pd.Series, data_type: str
    ) -> Optional[str]:
        """Infer sentinel/special values."""
        if len(series) == 0:
            return None

        value_counts = series.value_counts()
        total_count = len(series)

        # Common sentinel patterns
        if data_type in ["integer", "float"]:
            # Look for suspicious round numbers that appear frequently
            for sentinel in [-999, -99, -1, 999999, 0]:
                if (
                    sentinel in value_counts
                    and value_counts[sentinel] / total_count > 0.05
                ):
                    return str(sentinel)

        elif data_type in ["string", "categorical"]:
            # Look for obvious sentinel strings
            for sentinel in ["NULL", "UNKNOWN", "N/A", "MISSING", "TBD", "NONE"]:
                if (
                    sentinel in value_counts
                    and value_counts[sentinel] / total_count > 0.05
                ):
                    return sentinel

        return None

    def _infer_time_index(self, column_name: str, data_type: str) -> bool:
        """Infer if column is a time index."""
        if data_type != "datetime":
            return False

        name_lower = column_name.lower()
        time_indicators = [
            "timestamp",
            "time",
            "date",
            "created",
            "updated",
            "occurred",
            "recorded",
        ]

        return any(indicator in name_lower for indicator in time_indicators)

    def _infer_group_by(
        self, column_name: str, data_type: str, series: pd.Series
    ) -> bool:
        """Infer if column is used for grouping."""
        if len(series) == 0:
            return False

        name_lower = column_name.lower()

        # Name-based inference
        group_indicators = [
            "segment",
            "group",
            "category",
            "type",
            "class",
            "cohort",
            "bucket",
            "region",
            "zone",
        ]
        if any(indicator in name_lower for indicator in group_indicators):
            return True

        # Low cardinality categorical columns are likely group-by columns
        if data_type == "categorical":
            unique_ratio = series.nunique() / len(series)
            return unique_ratio < 0.1 and series.nunique() > 1

        return False


# Standard metadata template for inference results
INFERRABLE_METADATA_FIELDS = {
    # Core identification
    "column_name": "Column name",
    "data_type": "Inferred data type",
    "description": "Auto-generated description",
    # Data characteristics
    "role": "Column role (identifier, feature, target, etc.)",
    "do_not_impute": "Should not be imputed flag",
    "time_index": "Time ordering column flag",
    "group_by": "Grouping column flag",
    "unique_flag": "Values should be unique flag",
    "nullable": "Column allows null values",
    # Value constraints (inferrable)
    "min_value": "Minimum numeric value",
    "max_value": "Maximum numeric value",
    "max_length": "Maximum string length",
    "allowed_values": "Comma-separated allowed values for categorical",
    "sentinel_values": "Special/sentinel values detected",
    # Relationships (inferrable)
    "dependent_column": "Statistically dependent column",
}

# Standard CSV column layout for inference results
STANDARD_CSV_LAYOUT = [
    "Column",
    "Data_Type",
    "Role",
    "Do_Not_Impute",
    "Time_Index",
    "Group_By",
    "Unique_Flag",
    "Nullable",
    "Min_Value",
    "Max_Value",
    "Max_Length",
    "Allowed_Values",
    "Dependent_Column",
    "Sentinel_Values",
    "Description",
]

# Statistics fields that are calculated but not part of core metadata
STATISTICS_FIELDS = [
    "Missing_Count",
    "Missing_Pct",
    "Unique_Count",
    "Unique_Pct",
    "Sample_Values",
]

# Combined layout with statistics
FULL_CSV_LAYOUT = STANDARD_CSV_LAYOUT + STATISTICS_FIELDS

# Non-inferrable fields (require business knowledge)
NON_INFERRABLE_FIELDS = {
    "business_rule": "Business logic rule (requires domain knowledge)",
    "dependency_rule": "Calculation dependency rule (requires domain knowledge)",
    "meaning_of_missing": "Business context of missing values",
    "order_by": "Ordering logic within groups",
    "fallback_method": "Guaranteed fallback imputation method",
    "policy_version": "Audit trail version",
}


# Convenience function for easy import
def infer_metadata_from_dataframe(
    df: pd.DataFrame, warn_user: bool = True, **kwargs
) -> List[ColumnMetadata]:
    """
    Convenience function to infer metadata from a DataFrame.

    Args:
        df: DataFrame to analyze
        warn_user: Whether to warn user about inference limitations
        **kwargs: Additional parameters for MetadataInferenceEngine

    Returns:
        List of ColumnMetadata objects
    """
    engine = MetadataInferenceEngine(**kwargs)
    return engine.infer_dataframe_metadata(df, warn_user=warn_user)
