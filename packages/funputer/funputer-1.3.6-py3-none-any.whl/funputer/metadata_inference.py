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


# Centralized configuration constants
DEFAULT_CONFIG = {
    'categorical_threshold_ratio': 0.1,
    'categorical_threshold_absolute': 50,
    'datetime_sample_size': 100,
    'min_rows_for_stats': 10,
    'min_unique_threshold': 20,
    'sequential_id_threshold': 0.8,
}

DATETIME_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
    r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
    r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
]

ID_INDICATORS = ["id", "key", "pk", "uuid", "guid", "_id", "identifier"]
TIME_INDICATORS = ["time", "date", "timestamp", "created", "updated", "modified"]
GROUP_INDICATORS = ["category", "group", "type", "class", "status", "state", "region", "department"]


class MetadataInferenceEngine:
    """Intelligent metadata inference engine for pandas DataFrames."""

    def __init__(self, **config_overrides):
        """Initialize the inference engine with optional config overrides."""
        self.config = {**DEFAULT_CONFIG, **config_overrides}
        # Expose config as attributes for backward compatibility
        self.categorical_threshold_ratio = self.config['categorical_threshold_ratio']
        self.categorical_threshold_absolute = self.config['categorical_threshold_absolute']
        self.datetime_sample_size = self.config['datetime_sample_size']
        self.min_rows_for_stats = self.config['min_rows_for_stats']

    def infer_dataframe_metadata(
        self,
        df: pd.DataFrame,
        warn_user: bool = True,
        sample_size: Optional[int] = None,
        confidence_threshold: float = 0.7,
    ) -> List[ColumnMetadata]:
        """
        Infer metadata for all columns in a DataFrame.
        
        Args:
            df: Input DataFrame
            warn_user: Whether to warn user about inference limitations
            sample_size: Optional sample size for large datasets
            confidence_threshold: Minimum confidence for inferences
            
        Returns:
            List of ColumnMetadata objects
        """
        if df.empty:
            return []

        # Warn user about inference limitations if requested
        if warn_user:
            logger.info("Auto-inferring metadata from DataFrame. For production use, consider providing explicit metadata.")

        # Sample data for performance if needed
        working_df = df.sample(n=min(sample_size or len(df), len(df)), random_state=42) if sample_size else df
        
        metadata_list = []
        for col_name in df.columns:
            try:
                series = working_df[col_name]
                metadata = self._infer_column_metadata(series, working_df)
                if metadata:
                    metadata_list.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to infer metadata for column '{col_name}': {e}")
                # Create basic metadata as fallback
                metadata_list.append(self._create_fallback_metadata(col_name, df[col_name]))

        return metadata_list

    def _infer_column_metadata(self, series: pd.Series, df: pd.DataFrame) -> Optional[ColumnMetadata]:
        """Infer metadata for a single column."""
        if series.empty:
            return None

        column_name = str(series.name) if series.name else "unknown"
        non_null_series = series.dropna()
        
        # Core inference
        data_type = self._infer_data_type(series, non_null_series)
        constraints = self._infer_constraints(series, data_type)
        unique_flag = self._infer_uniqueness(series)
        
        # Behavioral inference
        role = self._infer_role(column_name, data_type, unique_flag, df)
        do_not_impute = self._infer_do_not_impute(role, unique_flag)
        
        # Feature flags
        time_index = self._infer_time_index(column_name, data_type)
        group_by = self._infer_group_by(column_name, series, data_type)
        
        # Value constraints
        allowed_values = self._infer_allowed_values(series, data_type) if data_type == "categorical" else None
        sentinel_values = self._infer_sentinel_values(series)
        
        # Dependencies and relationships
        dependent_column = self._infer_dependent_column(series, df) if len(df.columns) > 1 else None
        
        return ColumnMetadata(
            column_name=column_name,
            data_type=data_type,
            min_value=constraints.get("min_value"),
            max_value=constraints.get("max_value"),
            max_length=constraints.get("max_length"),
            unique_flag=unique_flag,
            nullable=len(non_null_series) < len(series),
            description=self._generate_description(column_name, data_type, series),
            dependent_column=dependent_column,
            allowed_values=allowed_values,
            role=role,
            do_not_impute=do_not_impute,
            time_index=time_index,
            group_by=group_by,
            sentinel_values=sentinel_values,
        )

    def _infer_data_type(self, series: pd.Series, non_null_series: pd.Series) -> str:
        """Infer the most appropriate data type for a series."""
        if len(non_null_series) == 0:
            return "string"  # Default for empty series

        # Check for boolean first (before numeric checks, since bool is numeric)
        if pd.api.types.is_bool_dtype(series) or self._is_boolean_column(non_null_series):
            return "boolean"

        # Check pandas dtype for numeric types
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_numeric_dtype(series):
            # Could be numeric stored as object - try to convert
            if self._could_be_integer(non_null_series):
                return "integer"
            return "float"

        # Check for datetime (but not on numeric data)
        if self._is_datetime_column(non_null_series):
            return "datetime"

        # For object types, infer string vs categorical
        if pd.api.types.is_object_dtype(series):
            return self._infer_object_type(non_null_series)

        return "string"  # Fallback

    def _could_be_integer(self, series: pd.Series) -> bool:
        """Check if an object series could be converted to integer."""
        try:
            sample = series.dropna().head(100)
            if len(sample) == 0:
                return False
            
            # Try to convert to numeric first
            numeric_vals = pd.to_numeric(sample, errors='raise')
            
            # Check if all values are whole numbers (no decimal part)
            return all(float(val).is_integer() if not pd.isna(val) else True for val in numeric_vals)
        except (ValueError, TypeError):
            return False

    def _infer_object_type(self, series: pd.Series) -> str:
        """Determine if object series is string or categorical."""
        if self._is_categorical_column(series):
            return "categorical"
        return "string"

    def _is_datetime_column(self, sample: pd.Series) -> bool:
        """Check if series contains datetime values."""
        if len(sample) == 0:
            return False
        
        # First check if already datetime type
        if pd.api.types.is_datetime64_any_dtype(sample):
            return True
            
        # Don't try to parse numeric types as datetime
        if pd.api.types.is_numeric_dtype(sample):
            return False
            
        # Check against common datetime patterns first (more restrictive)
        sample_str = sample.astype(str).head(50)
        pattern_matches = sum(1 for val in sample_str if any(re.search(pattern, str(val)) for pattern in DATETIME_PATTERNS))
        
        # Require strong evidence (>70% pattern match)
        if pattern_matches / len(sample_str) > 0.7 if len(sample_str) > 0 else False:
            # Only then try pandas parsing
            try:
                test_sample = sample.head(min(self.config['datetime_sample_size'], len(sample)))
                pd.to_datetime(test_sample, errors='raise')
                return True
            except (ValueError, TypeError):
                pass
                
        return False

    def _is_boolean_column(self, sample: pd.Series) -> bool:
        """Check if series contains boolean-like values."""
        if len(sample) == 0:
            return False
        
        unique_vals = set(str(v).lower() for v in sample.unique() if v is not None)
        bool_values = {'true', 'false', '1', '0', 'yes', 'no', 'y', 'n', 't', 'f'}
        return unique_vals.issubset(bool_values) and len(unique_vals) <= 4

    def _is_categorical_column(self, series: pd.Series) -> bool:
        """Determine if a column should be treated as categorical."""
        if len(series) < 2:
            return False
        
        unique_count = series.nunique()
        total_count = len(series)
        
        # Apply both ratio and absolute thresholds
        ratio_check = unique_count / total_count <= self.config['categorical_threshold_ratio']
        absolute_check = unique_count <= self.config['categorical_threshold_absolute']
        
        return ratio_check and absolute_check

    def _infer_constraints(self, series: pd.Series, data_type: str) -> Dict:
        """Infer value constraints for the series."""
        constraints = {}
        
        if len(series) == 0:
            return constraints
            
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return constraints

        if data_type in ["integer", "float"]:
            if len(non_null_series) >= 2:
                constraints["min_value"] = float(non_null_series.min())
                constraints["max_value"] = float(non_null_series.max())
                
        elif data_type in ["string", "categorical"]:
            max_length = non_null_series.astype(str).str.len().max()
            if max_length and max_length > 0:
                constraints["max_length"] = int(max_length)

        return constraints

    def _infer_uniqueness(self, series: pd.Series) -> bool:
        """Infer if column values should be unique."""
        if len(series) == 0:
            return False

        unique_count = series.nunique()
        column_name = str(series.name).lower() if series.name else ""
        
        # Check for ID-like column names first
        has_id_name = any(indicator in column_name for indicator in ID_INDICATORS)
        
        # Conservative uniqueness detection
        if has_id_name and unique_count == len(series):
            return True

        # For non-ID named columns, require strong evidence
        if unique_count == len(series) and len(series) >= self.config['min_unique_threshold']:
            return self._looks_like_identifier(series)
            
        return False

    def _looks_like_identifier(self, series: pd.Series) -> bool:
        """Check if values look like identifiers."""
        if series.dtype in ["int64", "int32"] and len(series) > 1:
            sorted_vals = sorted(series.dropna())
            if len(sorted_vals) >= 2:
                diffs = [sorted_vals[i+1] - sorted_vals[i] for i in range(len(sorted_vals)-1)]
                sequential_ratio = sum(1 for d in diffs if d == 1) / len(diffs)
                return sequential_ratio > self.config['sequential_id_threshold']
        return False

    def _generate_description(self, column_name: str, data_type: str, series: pd.Series) -> str:
        """Generate descriptive text for the column."""
        null_pct = (series.isnull().sum() / len(series)) * 100 if len(series) > 0 else 0
        
        if data_type in ["integer", "float"]:
            non_null = series.dropna()
            if len(non_null) > 0:
                return f"Numeric column ({data_type}) with values from {non_null.min():.2f} to {non_null.max():.2f}, {null_pct:.1f}% missing"
        elif data_type == "categorical":
            unique_count = series.nunique()
            return f"Categorical column with {unique_count} categories, {null_pct:.1f}% missing"
        elif data_type == "datetime":
            return f"Timestamp column, {null_pct:.1f}% missing"
        elif data_type == "boolean":
            return f"Boolean column, {null_pct:.1f}% missing"
        
        return f"Text column ({data_type}), {null_pct:.1f}% missing"

    def _infer_allowed_values(self, series: pd.Series, data_type: str) -> Optional[str]:
        """Infer allowed values for categorical columns."""
        if data_type != "categorical" or len(series) == 0:
            return None
            
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return None

        unique_values = sorted(non_null_series.unique())
        if len(unique_values) <= self.config['categorical_threshold_absolute']:
            return ",".join(str(v) for v in unique_values)
        
        return None

    def _infer_dependent_column(self, series: pd.Series, df: pd.DataFrame) -> Optional[str]:
        """Infer statistical dependencies between columns."""
        if len(df.columns) <= 1 or len(series.dropna()) < self.config['min_rows_for_stats']:
            return None

        column_name = series.name
        best_correlation = 0
        best_column = None

        try:
            numeric_df = df.select_dtypes(include=[np.number])
            if column_name in numeric_df.columns:
                correlations = numeric_df.corr()[column_name].abs().drop(column_name, errors='ignore')
                if not correlations.empty:
                    best_column = correlations.idxmax()
                    best_correlation = correlations.max()
        except Exception:
            pass

        return best_column if best_correlation > 0.7 else None

    def _infer_role(self, column_name: str, data_type: str, unique_flag: bool, df: pd.DataFrame) -> str:
        """Infer the analytical role of the column."""
        name_lower = column_name.lower()
        
        # Identifier columns
        if unique_flag or any(indicator in name_lower for indicator in ID_INDICATORS):
            return "identifier"
        
        # Time-based columns
        if data_type == "datetime" or any(indicator in name_lower for indicator in TIME_INDICATORS):
            return "time_index"
            
        # Group-by columns (categorical with reasonable cardinality)
        if (data_type == "categorical" or 
            any(indicator in name_lower for indicator in GROUP_INDICATORS)):
            return "group_by"

        # Target detection (simple heuristic)
        target_words = ["target", "label", "outcome", "result", "prediction"]
        if any(word in name_lower for word in target_words):
            return "target"

        return "feature"  # Default role

    def _infer_do_not_impute(self, role: str, unique_flag: bool) -> bool:
        """Determine if column should be excluded from imputation."""
        return role in ["identifier", "time"] or unique_flag

    def _infer_sentinel_values(self, series: pd.Series) -> Optional[str]:
        """Infer sentinel values that represent missing data."""
        if len(series) == 0:
            return None
        
        # Common sentinel patterns
        sentinels = {"", " ", "null", "NULL", "none", "NONE", "n/a", "N/A", "unknown", "UNKNOWN", "-", "?"}
        
        series_str = series.astype(str)
        found_sentinels = [val for val in sentinels if val in series_str.values]
        
        return ",".join(found_sentinels) if found_sentinels else None

    def _infer_time_index(self, column_name: str, data_type: str) -> bool:
        """Infer if column represents a time index."""
        if data_type != "datetime":
            return False
        
        name_lower = column_name.lower()
        return any(indicator in name_lower for indicator in TIME_INDICATORS)

    def _infer_group_by(self, column_name: str, series: pd.Series, data_type: str) -> bool:
        """Infer if column is suitable for grouping operations."""
        if len(series) == 0:
            return False
        
        name_lower = column_name.lower()
        if any(indicator in name_lower for indicator in GROUP_INDICATORS):
            return True
            
        # Categorical columns with reasonable cardinality
        if data_type == "categorical":
            unique_count = series.nunique()
            return 2 <= unique_count <= 50  # Reasonable for grouping
            
        return False

    def _create_fallback_metadata(self, column_name: str, series: pd.Series) -> ColumnMetadata:
        """Create basic fallback metadata when inference fails."""
        return ColumnMetadata(
            column_name=column_name,
            data_type="string",
            unique_flag=False,
            nullable=True,
            description=f"Column '{column_name}' (inference failed)",
            role="feature",
            do_not_impute=False,
            time_index=False,
            group_by=False,
        )


def infer_metadata_from_dataframe(
    df: pd.DataFrame, warn_user: bool = True, **kwargs
) -> List[ColumnMetadata]:
    """
    Convenience function to infer metadata from a DataFrame.
    
    Args:
        df: Input DataFrame
        warn_user: Whether to warn user about inference limitations
        **kwargs: Additional arguments passed to the inference engine
        
    Returns:
        List of ColumnMetadata objects
    """
    engine = MetadataInferenceEngine()
    return engine.infer_dataframe_metadata(df, warn_user=warn_user)