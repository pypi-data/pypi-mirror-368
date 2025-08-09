"""
Streamlined I/O operations with centralized validation patterns.
"""

import pandas as pd
import yaml
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json

from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from .exceptions import ConfigurationError, MetadataValidationError
from pydantic import ValidationError


# File format detection patterns
FORMAT_PATTERNS = {
    'json_ext': ['.json'],
    'csv_ext': ['.csv'],
    'json_content': lambda content: content.strip().startswith('{'),
    'csv_fallback': 'csv'
}

def load_metadata(
    metadata_path: str, format_type: str = "auto", validate_enterprise: bool = True
) -> List[ColumnMetadata]:
    """Load metadata from CSV file."""
    metadata_path = Path(metadata_path)
    
    if not metadata_path.exists():
        raise ValueError(f"Metadata file not found: {metadata_path}")
    
    # Always load as CSV (JSON format no longer supported)
    return _load_legacy_metadata_csv(str(metadata_path))


def _detect_metadata_format(metadata_path: Path) -> str:
    """Detect metadata format from file extension and content."""
    suffix = metadata_path.suffix.lower()
    
    if suffix in FORMAT_PATTERNS['json_ext']:
        return "json"
    elif suffix in FORMAT_PATTERNS['csv_ext']:
        return "csv"
    else:
        # Content-based detection
        try:
            with open(metadata_path, "r") as f:
                content = f.read()
                return "json" if FORMAT_PATTERNS['json_content'](content) else "csv"
        except:
            return FORMAT_PATTERNS['csv_fallback']




def _load_legacy_metadata_csv(metadata_path: str) -> List[ColumnMetadata]:
    """
    Load and validate column metadata from CSV file.

    Args:
        metadata_path: Path to metadata CSV file

    Returns:
        List of ColumnMetadata objects

    Raises:
        FileNotFoundError: If metadata file doesn't exist
        MetadataValidationError: If validation fails
    """
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    try:
        metadata_df = pd.read_csv(metadata_path)
    except Exception as e:
        raise MetadataValidationError(f"Failed to read metadata CSV: {e}")

    # Schema validation with centralized patterns
    _validate_metadata_schema(metadata_df)
    _validate_metadata_content(metadata_df)

    # Convert to ColumnMetadata objects
    return [_create_column_metadata(row, metadata_df.columns) for _, row in metadata_df.iterrows()]




def get_column_metadata(
    metadata: List[ColumnMetadata], column_name: str
) -> Optional[ColumnMetadata]:
    """
    Get metadata for a specific column.

    Args:
        metadata: List of column metadata
        column_name: Name of the column

    Returns:
        ColumnMetadata object or None if not found
    """
    for col in metadata:
        if col.column_name == column_name:
            return col
    return None


def validate_metadata_against_data(
    metadata: List[ColumnMetadata], data_path: str
) -> List[str]:
    """Validate metadata against actual data file."""
    return _validate_legacy_metadata(metadata, data_path)


# Environment variable mappings
ENV_OVERRIDES = {
    "iqr_multiplier": ("FUNIMPUTE_IQR_MULTIPLIER", float),
    "outlier_percentage_threshold": ("FUNIMPUTE_OUTLIER_THRESHOLD", float),
    "correlation_threshold": ("FUNIMPUTE_CORRELATION_THRESHOLD", float),
    "chi_square_alpha": ("FUNIMPUTE_CHI_SQUARE_ALPHA", float),
    "point_biserial_threshold": ("FUNIMPUTE_POINT_BISERIAL_THRESHOLD", float),
    "skewness_threshold": ("FUNIMPUTE_SKEWNESS_THRESHOLD", float),
    "missing_percentage_threshold": ("FUNIMPUTE_MISSING_THRESHOLD", float),
    "output_path": ("FUNIMPUTE_OUTPUT_PATH", str),
    "skip_columns": ("FUNIMPUTE_SKIP_COLUMNS", lambda x: [col.strip() for col in x.split(",") if col.strip()]),
}

def load_configuration(config_path: Optional[str] = None) -> AnalysisConfig:
    """Load configuration with file and environment variable support."""
    config_dict = {}
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        config_dict = _load_config_file(config_path)
    
    # Apply environment overrides
    _apply_env_overrides(config_dict)
    
    # Create and validate config
    try:
        return AnalysisConfig(**config_dict)
    except ValidationError as e:
        raise ConfigurationError(f"Configuration validation failed: {e}")


def save_suggestions(suggestions: List[ImputationSuggestion], output_path: str) -> None:
    """Save imputation suggestions to CSV file."""
    if not suggestions:
        raise ValueError("No suggestions to save")
    
    df = pd.DataFrame([suggestion.to_dict() for suggestion in suggestions])
    _ensure_dir_exists(output_path)
    df.to_csv(output_path, index=False)




def load_data(data_path: str, metadata: List[ColumnMetadata]) -> pd.DataFrame:
    """Load data CSV with streamlined validation."""
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    try:
        data_df = pd.read_csv(data_path)
    except Exception as e:
        raise ValueError(f"Failed to read data CSV: {e}")
    
    # Validate column alignment
    _validate_data_columns(data_df, metadata)
    return data_df


# Helper functions for validation and processing
def _validate_metadata_schema(metadata_df: pd.DataFrame) -> None:
    """Validate metadata DataFrame has required columns and data types."""
    required_columns = {"column_name": str, "data_type": str}
    
    # Check required columns exist
    missing_columns = set(required_columns.keys()) - set(metadata_df.columns)
    if missing_columns:
        raise MetadataValidationError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {list(metadata_df.columns)}"
        )
    
    # Validate data types
    for col, expected_type in required_columns.items():
        if not metadata_df[col].dtype == "object":
            if expected_type == str:
                metadata_df[col] = metadata_df[col].astype(str)


def _validate_metadata_content(metadata_df: pd.DataFrame) -> None:
    """Validate metadata content for data types, duplicates, and constraints."""
    # Valid data types
    valid_data_types = {"integer", "float", "string", "datetime", "boolean", "categorical"}
    invalid_types = set(metadata_df["data_type"].unique()) - valid_data_types
    if invalid_types:
        raise MetadataValidationError(
            f"Invalid data types found: {invalid_types}. Valid types: {valid_data_types}"
        )
    
    # Check for duplicate column names
    if metadata_df["column_name"].duplicated().any():
        duplicates = metadata_df[metadata_df["column_name"].duplicated()]["column_name"].tolist()
        raise MetadataValidationError(f"Duplicate column names found: {duplicates}")
    
    # Validate numeric constraints if present
    if "min_value" in metadata_df.columns and "max_value" in metadata_df.columns:
        for idx, row in metadata_df.iterrows():
            if (pd.notna(row["min_value"]) and pd.notna(row["max_value"]) 
                and row["min_value"] > row["max_value"]):
                raise MetadataValidationError(
                    f"Column {row['column_name']}: min_value ({row['min_value']}) "
                    f"cannot be greater than max_value ({row['max_value']})"
                )


def _create_column_metadata(row: pd.Series, available_columns: pd.Index) -> ColumnMetadata:
    """Create ColumnMetadata object from DataFrame row with dynamic field handling."""
    manual_fields = ['business_rule', 'dependency_rule', 'meaning_of_missing', 'order_by', 'fallback_method', 'policy_version']
    
    # Base metadata fields
    base_kwargs = {
        "column_name": row["column_name"],
        "data_type": row["data_type"],
        "min_value": row.get("min_value") if pd.notna(row.get("min_value")) else None,
        "max_value": row.get("max_value") if pd.notna(row.get("max_value")) else None,
        "max_length": int(row.get("max_length")) if pd.notna(row.get("max_length")) else None,
        "unique_flag": bool(row.get("unique_flag", False)),
        "nullable": bool(row.get("nullable", True)),
        "description": str(row.get("description", "")),
        "dependent_column": row.get("dependent_column") if pd.notna(row.get("dependent_column")) else None,
        "allowed_values": row.get("allowed_values") if pd.notna(row.get("allowed_values")) else None,
    }
    
    # Add enhanced fields if present
    for field in ["role", "do_not_impute", "sentinel_values", "time_index", "group_by"]:
        if field in available_columns:
            if field in ["do_not_impute", "time_index", "group_by"]:
                base_kwargs[field] = bool(row.get(field, False))
            else:
                base_kwargs[field] = row.get(field, "feature" if field == "role" else None)
    
    # Create metadata object
    metadata = ColumnMetadata(**base_kwargs)
    
    # Add manual fields dynamically if they exist with non-null values
    has_manual_fields = any(
        col in available_columns and pd.notna(row.get(col)) and str(row.get(col)).strip() != ''
        for col in manual_fields
    )
    
    if has_manual_fields:
        for field in manual_fields:
            if field in available_columns:
                value = row.get(field)
                if pd.notna(value):
                    setattr(metadata, field, value)
    
    return metadata


def _load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file."""
    try:
        with open(config_path, "r") as f:
            if config_path.endswith((".yaml", ".yml")):
                return yaml.safe_load(f) or {}
            elif config_path.endswith(".json"):
                return json.load(f)
            else:
                raise ConfigurationError(f"Unsupported config file format: {config_path}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load config file: {e}")


def _apply_env_overrides(config_dict: Dict[str, Any]) -> None:
    """Apply environment variable overrides to configuration."""
    for config_key, (env_var, converter) in ENV_OVERRIDES.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                config_dict[config_key] = converter(env_value)
            except ValueError as e:
                raise ConfigurationError(f"Invalid environment variable {env_var}: {e}")


def _validate_legacy_metadata(metadata: List[ColumnMetadata], data_path: str) -> List[str]:
    """Validate legacy metadata against data file."""
    errors = []
    try:
        data = pd.read_csv(data_path)
        data_columns = set(data.columns)
        metadata_columns = {col.column_name for col in metadata}
        
        missing_in_data = metadata_columns - data_columns
        if missing_in_data:
            errors.append(f"Columns in metadata but not in data: {missing_in_data}")
        
        extra_in_data = data_columns - metadata_columns
        if extra_in_data:
            errors.append(f"Columns in data but not in metadata: {extra_in_data}")
    except Exception as e:
        errors.append(f"Failed to validate against data: {e}")
    
    return errors


def _ensure_dir_exists(file_path: str) -> None:
    """Ensure the directory for the given file path exists."""
    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)


def _validate_data_columns(data_df: pd.DataFrame, metadata: List[ColumnMetadata]) -> None:
    """Validate that data columns align with metadata expectations."""
    metadata_columns = {meta.column_name for meta in metadata}
    data_columns = set(data_df.columns)
    
    missing_columns = metadata_columns - data_columns
    if missing_columns:
        raise ValueError(f"Data missing columns from metadata: {missing_columns}")
    
    extra_columns = data_columns - metadata_columns
    if extra_columns:
        print(f"Warning: Data contains extra columns not in metadata: {extra_columns}")
