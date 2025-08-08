"""
I/O utilities for loading metadata, configuration, and data.
"""

import pandas as pd
import yaml
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json

from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from .enterprise_models import EnterpriseMetadata
from .enterprise_loader import load_enterprise_metadata, get_metadata_loader
from .exceptions import ConfigurationError, MetadataValidationError
from pydantic import ValidationError


def load_metadata(
    metadata_path: str, format_type: str = "auto", validate_enterprise: bool = True
) -> Union[List[ColumnMetadata], EnterpriseMetadata]:
    """
    Load metadata from CSV or JSON format with automatic format detection.

    Args:
        metadata_path: Path to metadata file
        format_type: Format type ("csv", "json", "auto")
        validate_enterprise: Whether to validate enterprise JSON metadata

    Returns:
        List of ColumnMetadata (legacy) or EnterpriseMetadata object

    Raises:
        ValueError: If metadata file is invalid or missing required fields
        MetadataValidationError: If enterprise metadata validation fails
    """
    metadata_path = Path(metadata_path)

    if not metadata_path.exists():
        raise ValueError(f"Metadata file not found: {metadata_path}")

    # Auto-detect format
    if format_type == "auto":
        if metadata_path.suffix.lower() == ".json":
            format_type = "json"
        elif metadata_path.suffix.lower() == ".csv":
            format_type = "csv"
        else:
            # Try to detect by content
            try:
                with open(metadata_path, "r") as f:
                    content = f.read().strip()
                    if content.startswith("{"):
                        format_type = "json"
                    else:
                        format_type = "csv"
            except:
                format_type = "csv"  # Default fallback

    # Load based on format
    if format_type == "json":
        return _load_enterprise_metadata(str(metadata_path), validate_enterprise)
    else:
        return _load_legacy_metadata_csv(str(metadata_path))


def _load_enterprise_metadata(
    metadata_path: str, validate: bool = True
) -> EnterpriseMetadata:
    """Load enterprise metadata from JSON file."""
    try:
        return load_enterprise_metadata(
            metadata_path, source_type="file", validate=validate
        )
    except MetadataValidationError as e:
        raise ValueError(f"Enterprise metadata validation failed: {e}")


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

    # Validate schema - only require essential columns
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
        if (
            not metadata_df[col].dtype == "object"
        ):  # String columns should be object type
            if expected_type == str:
                metadata_df[col] = metadata_df[col].astype(str)

    # Validate data_type values
    valid_data_types = {
        "integer",
        "float",
        "string",
        "datetime",
        "boolean",
        "categorical",
    }
    invalid_types = set(metadata_df["data_type"].unique()) - valid_data_types
    if invalid_types:
        raise MetadataValidationError(
            f"Invalid data types found: {invalid_types}. "
            f"Valid types: {valid_data_types}"
        )

    # Check for duplicate column names
    if metadata_df["column_name"].duplicated().any():
        duplicates = metadata_df[metadata_df["column_name"].duplicated()][
            "column_name"
        ].tolist()
        raise MetadataValidationError(f"Duplicate column names found: {duplicates}")

    # Validate numeric constraints if present
    if "min_value" in metadata_df.columns and "max_value" in metadata_df.columns:
        for idx, row in metadata_df.iterrows():
            if (
                pd.notna(row["min_value"])
                and pd.notna(row["max_value"])
                and row["min_value"] > row["max_value"]
            ):
                raise MetadataValidationError(
                    f"Column {row['column_name']}: min_value ({row['min_value']}) "
                    f"cannot be greater than max_value ({row['max_value']})"
                )

    # Convert to ColumnMetadata objects with defaults for missing columns
    metadata_list = []
    manual_fields = ['business_rule', 'dependency_rule', 'meaning_of_missing', 'order_by', 'fallback_method', 'policy_version']
    
    for _, row in metadata_df.iterrows():
        # Check if any manual fields are present with non-null values
        has_manual_fields = any(
            col in row and pd.notna(row.get(col)) and str(row.get(col)).strip() != ''
            for col in manual_fields if col in metadata_df.columns
        )
        
        # Base fields for both ColumnMetadata and CompleteColumnMetadata
        base_kwargs = {
            "column_name": row["column_name"],
            "data_type": row["data_type"],
            "min_value": row.get("min_value") if pd.notna(row.get("min_value")) else None,
            "max_value": row.get("max_value") if pd.notna(row.get("max_value")) else None,
            "max_length": (
                int(row.get("max_length")) if pd.notna(row.get("max_length")) else None
            ),
            "unique_flag": bool(row.get("unique_flag", False)),
            "nullable": bool(row.get("nullable", True)),
            "description": str(row.get("description", "")),
            "dependent_column": (
                row.get("dependent_column")
                if pd.notna(row.get("dependent_column"))
                else None
            ),
            "allowed_values": (
                row.get("allowed_values")
                if pd.notna(row.get("allowed_values"))
                else None
            ),
        }
        
        # Add enhanced fields if present
        for field in ["role", "do_not_impute", "sentinel_values", "time_index", "group_by"]:
            if field in row:
                if field in ["do_not_impute", "time_index", "group_by"]:
                    base_kwargs[field] = bool(row.get(field, False))
                else:
                    base_kwargs[field] = row.get(field, "feature" if field == "role" else None)
        
        # Always use basic ColumnMetadata
        metadata = ColumnMetadata(**base_kwargs)
        
        # Add manual fields dynamically if they exist
        if has_manual_fields:
            for field in manual_fields:
                if field in row:
                    value = row.get(field)
                    if pd.notna(value):
                        setattr(metadata, field, value)
        
        metadata_list.append(metadata)

    return metadata_list


def convert_enterprise_to_legacy(
    enterprise_metadata: EnterpriseMetadata,
) -> List[ColumnMetadata]:
    """
    Convert enterprise metadata to legacy format for backward compatibility.

    Args:
        enterprise_metadata: Enterprise metadata object

    Returns:
        List of legacy ColumnMetadata objects
    """
    loader = get_metadata_loader()
    return loader.convert_to_legacy_format(enterprise_metadata)


def get_column_metadata(
    metadata: Union[List[ColumnMetadata], EnterpriseMetadata], column_name: str
) -> Optional[ColumnMetadata]:
    """
    Get metadata for a specific column from either format.

    Args:
        metadata: Metadata in either legacy or enterprise format
        column_name: Name of the column

    Returns:
        Legacy ColumnMetadata object or None if not found
    """
    if isinstance(metadata, EnterpriseMetadata):
        # Convert enterprise column to legacy format
        enterprise_col = metadata.get_column(column_name)
        if enterprise_col is None:
            return None

        # Convert to legacy format
        legacy_metadata = convert_enterprise_to_legacy(metadata)
        for col in legacy_metadata:
            if col.column_name == column_name:
                return col
        return None
    else:
        # Legacy format - direct lookup
        for col in metadata:
            if col.column_name == column_name:
                return col
        return None


def validate_metadata_against_data(
    metadata: Union[List[ColumnMetadata], EnterpriseMetadata], data_path: str
) -> List[str]:
    """
    Validate metadata against actual data file.

    Args:
        metadata: Metadata in either format
        data_path: Path to data CSV file

    Returns:
        List of validation errors
    """
    if isinstance(metadata, EnterpriseMetadata):
        loader = get_metadata_loader()
        return loader.validate_against_data(metadata, data_path)
    else:
        # Legacy validation (simplified)
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


def load_configuration(config_path: Optional[str] = None) -> AnalysisConfig:
    """
    Load configuration from file with environment variable overrides.

    Args:
        config_path: Optional path to YAML/JSON config file

    Returns:
        AnalysisConfig object with loaded/default settings

    Raises:
        ConfigurationError: If configuration is invalid
    """
    config_dict = {}

    # Load from file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    config_dict = yaml.safe_load(f) or {}
                elif config_path.endswith(".json"):
                    config_dict = json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported config file format: {config_path}"
                    )
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file: {e}")

    # Override with environment variables
    env_overrides = {
        "iqr_multiplier": "FUNIMPUTE_IQR_MULTIPLIER",
        "outlier_percentage_threshold": "FUNIMPUTE_OUTLIER_THRESHOLD",
        "correlation_threshold": "FUNIMPUTE_CORRELATION_THRESHOLD",
        "chi_square_alpha": "FUNIMPUTE_CHI_SQUARE_ALPHA",
        "point_biserial_threshold": "FUNIMPUTE_POINT_BISERIAL_THRESHOLD",
        "skewness_threshold": "FUNIMPUTE_SKEWNESS_THRESHOLD",
        "missing_percentage_threshold": "FUNIMPUTE_MISSING_THRESHOLD",
        "metrics_port": "FUNIMPUTE_METRICS_PORT",
        "output_path": "FUNIMPUTE_OUTPUT_PATH",
        "audit_log_path": "FUNIMPUTE_AUDIT_LOG_PATH",
        "skip_columns": "FUNIMPUTE_SKIP_COLUMNS",
    }

    for config_key, env_var in env_overrides.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                if config_key == "metrics_port":
                    config_dict[config_key] = int(env_value)
                elif config_key in ["output_path", "audit_log_path"]:
                    config_dict[config_key] = env_value
                elif config_key == "skip_columns":
                    # Parse comma-separated list of column names
                    config_dict[config_key] = [
                        col.strip() for col in env_value.split(",") if col.strip()
                    ]
                else:
                    config_dict[config_key] = float(env_value)
            except ValueError as e:
                raise ConfigurationError(f"Invalid environment variable {env_var}: {e}")

    # Create and validate config
    try:
        return AnalysisConfig(**config_dict)
    except ValidationError as e:
        raise ConfigurationError(f"Configuration validation failed: {e}")


def save_suggestions(suggestions: List[ImputationSuggestion], output_path: str) -> None:
    """
    Save imputation suggestions to CSV file.

    Args:
        suggestions: List of ImputationSuggestion objects
        output_path: Path to output CSV file
    """
    if not suggestions:
        raise ValueError("No suggestions to save")

    # Convert to DataFrame
    suggestions_data = [suggestion.to_dict() for suggestion in suggestions]
    df = pd.DataFrame(suggestions_data)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save to CSV
    df.to_csv(output_path, index=False)


def append_audit_log(log_entry: Dict[str, Any], audit_log_path: str) -> None:
    """
    Append audit log entry to JSONL file.

    Args:
        log_entry: Dictionary containing log data
        audit_log_path: Path to audit log file
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(audit_log_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Append to JSONL file
    with open(audit_log_path, "a") as f:
        json.dump(log_entry, f, default=str)
        f.write("\n")


def load_data(data_path: str, metadata: List[ColumnMetadata]) -> pd.DataFrame:
    """
    Load data CSV with proper column validation.

    Args:
        data_path: Path to data CSV file
        metadata: List of column metadata for validation

    Returns:
        DataFrame with loaded data

    Raises:
        FileNotFoundError: If data file doesn't exist
        ValueError: If data validation fails
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    try:
        data_df = pd.read_csv(data_path)
    except Exception as e:
        raise ValueError(f"Failed to read data CSV: {e}")

    # Validate columns exist
    metadata_columns = {meta.column_name for meta in metadata}
    data_columns = set(data_df.columns)

    missing_columns = metadata_columns - data_columns
    if missing_columns:
        raise ValueError(f"Data missing columns from metadata: {missing_columns}")

    extra_columns = data_columns - metadata_columns
    if extra_columns:
        print(f"Warning: Data contains extra columns not in metadata: {extra_columns}")

    return data_df
