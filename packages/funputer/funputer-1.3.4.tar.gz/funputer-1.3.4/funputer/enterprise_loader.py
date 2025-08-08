"""
Enterprise metadata loader with caching and API integration.
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import hashlib
import pickle

from .enterprise_models import EnterpriseMetadata, EnterpriseColumnMetadata
from .schema_validator import (
    SchemaValidator,
    validate_metadata_file,
    convert_legacy_metadata,
    MetadataValidationError,
)
from .models import ColumnMetadata  # Legacy model


class MetadataCache:
    """Simple file-based cache for metadata."""

    def __init__(self, cache_dir: str = ".metadata_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, source: str) -> str:
        """Generate cache key from source identifier."""
        return hashlib.md5(source.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.pkl"

    def get(self, source: str, max_age_hours: int = 24) -> Optional[EnterpriseMetadata]:
        """
        Get cached metadata if available and not expired.

        Args:
            source: Source identifier (file path, URL, etc.)
            max_age_hours: Maximum age in hours before cache expires

        Returns:
            Cached metadata or None if not available/expired
        """
        cache_key = self._get_cache_key(source)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            # Check file age
            file_age = datetime.now() - datetime.fromtimestamp(
                cache_path.stat().st_mtime
            )
            if file_age > timedelta(hours=max_age_hours):
                cache_path.unlink()  # Remove expired cache
                return None

            # Load cached metadata
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception:
            # If cache is corrupted, remove it
            try:
                cache_path.unlink()
            except:
                pass
            return None

    def set(self, source: str, metadata: EnterpriseMetadata) -> None:
        """
        Cache metadata.

        Args:
            source: Source identifier
            metadata: Metadata to cache
        """
        cache_key = self._get_cache_key(source)
        cache_path = self._get_cache_path(cache_key)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(metadata, f)
        except Exception:
            # Ignore cache write failures
            pass

    def clear(self) -> None:
        """Clear all cached metadata."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except:
                pass


class EnterpriseMetadataLoader:
    """Loads and validates enterprise metadata from various sources."""

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_max_age_hours: int = 24,
        schema_path: str = None,
    ):
        """
        Initialize metadata loader.

        Args:
            cache_enabled: Whether to enable metadata caching
            cache_max_age_hours: Maximum cache age in hours
            schema_path: Path to custom JSON schema file
        """
        self.cache_enabled = cache_enabled
        self.cache_max_age_hours = cache_max_age_hours
        self.cache = MetadataCache() if cache_enabled else None
        self.validator = SchemaValidator(schema_path)

    def load_from_file(
        self, file_path: str, validate: bool = True
    ) -> EnterpriseMetadata:
        """
        Load metadata from JSON file.

        Args:
            file_path: Path to metadata JSON file
            validate: Whether to validate metadata

        Returns:
            Parsed and validated metadata

        Raises:
            MetadataValidationError: If validation fails
        """
        file_path = str(Path(file_path).resolve())

        # Check cache first
        if self.cache_enabled:
            cached = self.cache.get(file_path, self.cache_max_age_hours)
            if cached:
                return cached

        # Load and validate
        if validate:
            metadata, errors = validate_metadata_file(
                file_path, self.validator.schema_path
            )
            if errors:
                raise MetadataValidationError(
                    f"Metadata validation failed:\n" + "\n".join(errors)
                )
        else:
            try:
                with open(file_path, "r") as f:
                    metadata_dict = json.load(f)
                metadata = EnterpriseMetadata(**metadata_dict)
            except Exception as e:
                raise MetadataValidationError(f"Failed to load metadata: {e}")

        # Cache the result
        if self.cache_enabled and metadata:
            self.cache.set(file_path, metadata)

        return metadata

    def load_from_url(
        self,
        url: str,
        headers: Dict[str, str] = None,
        timeout: int = 30,
        validate: bool = True,
    ) -> EnterpriseMetadata:
        """
        Load metadata from REST API endpoint.

        Args:
            url: API endpoint URL
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            validate: Whether to validate metadata

        Returns:
            Parsed and validated metadata

        Raises:
            MetadataValidationError: If loading or validation fails
        """
        # Check cache first
        if self.cache_enabled:
            cached = self.cache.get(url, self.cache_max_age_hours)
            if cached:
                return cached

        # Fetch from API
        try:
            response = requests.get(url, headers=headers or {}, timeout=timeout)
            response.raise_for_status()
            metadata_dict = response.json()
        except requests.RequestException as e:
            raise MetadataValidationError(f"Failed to fetch metadata from {url}: {e}")
        except json.JSONDecodeError as e:
            raise MetadataValidationError(f"Invalid JSON response from {url}: {e}")

        # Validate if requested
        if validate:
            metadata, errors = self.validator.validate_complete(metadata_dict)
            if errors:
                raise MetadataValidationError(
                    f"Metadata validation failed:\n" + "\n".join(errors)
                )
        else:
            try:
                metadata = EnterpriseMetadata(**metadata_dict)
            except Exception as e:
                raise MetadataValidationError(f"Failed to parse metadata: {e}")

        # Cache the result
        if self.cache_enabled and metadata:
            self.cache.set(url, metadata)

        return metadata

    def load_from_legacy_csv(
        self, csv_path: str, validate: bool = True
    ) -> EnterpriseMetadata:
        """
        Load metadata from legacy CSV format and convert to enterprise format.

        Args:
            csv_path: Path to legacy CSV metadata file
            validate: Whether to validate converted metadata

        Returns:
            Converted and validated metadata

        Raises:
            MetadataValidationError: If conversion or validation fails
        """
        import pandas as pd

        try:
            # Load legacy CSV
            df = pd.read_csv(csv_path)
            legacy_metadata = df.to_dict("records")

            # Convert to enterprise format
            enterprise_dict = convert_legacy_metadata(legacy_metadata)

            # Validate if requested
            if validate:
                metadata, errors = self.validator.validate_complete(enterprise_dict)
                if errors:
                    raise MetadataValidationError(
                        f"Converted metadata validation failed:\n" + "\n".join(errors)
                    )
            else:
                metadata = EnterpriseMetadata(**enterprise_dict)

            return metadata

        except Exception as e:
            raise MetadataValidationError(f"Failed to convert legacy metadata: {e}")

    def convert_to_legacy_format(
        self, metadata: EnterpriseMetadata
    ) -> List[ColumnMetadata]:
        """
        Convert enterprise metadata to legacy format for backward compatibility.

        Args:
            metadata: Enterprise metadata object

        Returns:
            List of legacy ColumnMetadata objects
        """
        legacy_columns = []

        for col in metadata.columns:
            # Extract basic fields
            legacy_col = ColumnMetadata(
                column_name=col.name,
                data_type=col.data_type.value,
                unique_flag=col.unique,
                description=col.description or "",
            )

            # Extract constraints
            if col.constraints:
                legacy_col.min_value = col.constraints.min_value
                legacy_col.max_value = col.constraints.max_value
                legacy_col.max_length = col.constraints.max_length

            # Extract relationships
            if col.relationships and col.relationships.dependent_columns:
                legacy_col.dependent_column = col.relationships.dependent_columns[0]

            # Extract business rules (take first one)
            if col.business_rules:
                legacy_col.business_rule = col.business_rules[0].expression

            legacy_columns.append(legacy_col)

        return legacy_columns

    def get_column_metadata(
        self, metadata: EnterpriseMetadata, column_name: str
    ) -> Optional[EnterpriseColumnMetadata]:
        """
        Get metadata for a specific column.

        Args:
            metadata: Enterprise metadata object
            column_name: Name of the column

        Returns:
            Column metadata or None if not found
        """
        return metadata.get_column(column_name)

    def validate_against_data(
        self, metadata: EnterpriseMetadata, data_path: str
    ) -> List[str]:
        """
        Validate metadata against actual data.

        Args:
            metadata: Metadata to validate
            data_path: Path to data file

        Returns:
            List of validation errors
        """
        import pandas as pd

        errors = []

        try:
            # Load data
            data = pd.read_csv(data_path)
            data_columns = set(data.columns)
            metadata_columns = {col.name for col in metadata.columns}

            # Check for missing columns in data
            missing_in_data = metadata_columns - data_columns
            if missing_in_data:
                errors.append(f"Columns in metadata but not in data: {missing_in_data}")

            # Check for extra columns in data
            extra_in_data = data_columns - metadata_columns
            if extra_in_data:
                errors.append(f"Columns in data but not in metadata: {extra_in_data}")

            # Validate data types and constraints
            for col in metadata.columns:
                if col.name not in data_columns:
                    continue

                series = data[col.name]

                # Check data type compatibility
                if col.data_type == "integer" and not pd.api.types.is_integer_dtype(
                    series
                ):
                    if not pd.api.types.is_numeric_dtype(series):
                        errors.append(
                            f"Column '{col.name}': Expected integer, found {series.dtype}"
                        )
                elif col.data_type == "float" and not pd.api.types.is_numeric_dtype(
                    series
                ):
                    errors.append(
                        f"Column '{col.name}': Expected numeric, found {series.dtype}"
                    )

                # Check constraints
                if col.constraints:
                    non_null_series = series.dropna()

                    if (
                        col.constraints.min_value is not None
                        and pd.api.types.is_numeric_dtype(series)
                    ):
                        if (non_null_series < col.constraints.min_value).any():
                            errors.append(
                                f"Column '{col.name}': Values below min_value {col.constraints.min_value}"
                            )

                    if (
                        col.constraints.max_value is not None
                        and pd.api.types.is_numeric_dtype(series)
                    ):
                        if (non_null_series > col.constraints.max_value).any():
                            errors.append(
                                f"Column '{col.name}': Values above max_value {col.constraints.max_value}"
                            )

                    if col.constraints.allowed_values:
                        invalid_values = set(non_null_series) - set(
                            col.constraints.allowed_values
                        )
                        if invalid_values:
                            errors.append(
                                f"Column '{col.name}': Invalid values found: {invalid_values}"
                            )

                # Check required constraint
                if col.required and series.isna().any():
                    errors.append(
                        f"Column '{col.name}': Required column has missing values"
                    )

                # Check unique constraint
                if col.unique and series.duplicated().any():
                    errors.append(
                        f"Column '{col.name}': Unique column has duplicate values"
                    )

        except Exception as e:
            errors.append(f"Failed to validate against data: {e}")

        return errors


# Global loader instance
_metadata_loader = None


def get_metadata_loader(**kwargs) -> EnterpriseMetadataLoader:
    """Get or create global metadata loader instance."""
    global _metadata_loader
    if _metadata_loader is None:
        _metadata_loader = EnterpriseMetadataLoader(**kwargs)
    return _metadata_loader


def load_enterprise_metadata(
    source: str, source_type: str = "auto", validate: bool = True, **loader_kwargs
) -> EnterpriseMetadata:
    """
    Convenience function to load enterprise metadata from various sources.

    Args:
        source: Source path, URL, or identifier
        source_type: Type of source ("file", "url", "legacy_csv", "auto")
        validate: Whether to validate metadata
        **loader_kwargs: Additional arguments for loader

    Returns:
        Loaded and validated metadata

    Raises:
        MetadataValidationError: If loading or validation fails
    """
    loader = get_metadata_loader(**loader_kwargs)

    # Auto-detect source type
    if source_type == "auto":
        if source.startswith(("http://", "https://")):
            source_type = "url"
        elif source.endswith(".csv"):
            source_type = "legacy_csv"
        else:
            source_type = "file"

    # Load based on type
    if source_type == "file":
        return loader.load_from_file(source, validate)
    elif source_type == "url":
        return loader.load_from_url(source, validate=validate)
    elif source_type == "legacy_csv":
        return loader.load_from_legacy_csv(source, validate)
    else:
        raise MetadataValidationError(f"Unsupported source type: {source_type}")
