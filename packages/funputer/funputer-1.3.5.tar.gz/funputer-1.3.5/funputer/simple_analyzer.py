"""
Simple imputation analyzer for client applications.
Clean, lightweight interface focused on core functionality.
"""

import time
import logging
from typing import List, Dict, Any, Union, Optional
import pandas as pd

from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion
from .io import load_metadata, load_data
from .exceptions import should_skip_column
from .outliers import analyze_outliers
from .mechanism import analyze_missingness_mechanism
from .proposal import propose_imputation_method

# Set up simple logging
logger = logging.getLogger(__name__)


class SimpleImputationAnalyzer:
    """
    Lightweight imputation analyzer for client applications.

    Focuses on core functionality:
    - Intelligent imputation recommendations
    - Adaptive thresholds
    - Business rule integration
    - Simple, fast API
    """

    def __init__(self, config: AnalysisConfig = None):
        """Initialize analyzer with configuration."""
        self.config = config or AnalysisConfig()

    def _load_metadata_auto_format(self, metadata_path: str) -> List[ColumnMetadata]:
        """
        Load metadata from either CSV or JSON format, auto-detecting the format.

        Args:
            metadata_path: Path to metadata file

        Returns:
            List of ColumnMetadata objects

        Raises:
            Exception: If metadata cannot be loaded in either format
        """
        import os
        import json

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        # Try JSON format first (enterprise metadata)
        if metadata_path.lower().endswith(".json"):
            try:
                logger.info(f"Loading JSON metadata: {metadata_path}")

                # First try enterprise metadata loader
                try:
                    from .enterprise_loader import (
                        load_enterprise_metadata,
                        get_metadata_loader,
                    )

                    enterprise_metadata = load_enterprise_metadata(
                        metadata_path, source_type="file", validate=False
                    )
                    loader = get_metadata_loader()
                    legacy_metadata = loader.convert_to_legacy_format(
                        enterprise_metadata
                    )
                    logger.info(
                        f"Loaded enterprise JSON metadata: {len(legacy_metadata)} columns"
                    )
                    return legacy_metadata
                except Exception as enterprise_error:
                    logger.debug(f"Enterprise loader failed: {enterprise_error}")

                    # Try simple JSON to CSV conversion
                    with open(metadata_path, "r") as f:
                        json_data = json.load(f)

                    # Convert simple JSON format to legacy metadata
                    legacy_metadata = self._convert_simple_json_to_legacy(json_data)
                    logger.info(
                        f"Converted simple JSON metadata: {len(legacy_metadata)} columns"
                    )
                    return legacy_metadata

            except Exception as e:
                logger.warning(f"Failed to load JSON metadata: {e}")
                # Fall through to try CSV format

        # Try CSV format (legacy metadata)
        try:
            logger.info(f"Loading legacy metadata (CSV): {metadata_path}")
            metadata_list = load_metadata(metadata_path)

            if isinstance(metadata_list, list):
                return metadata_list
            else:
                # Handle enterprise metadata format from CSV conversion
                from .io import convert_enterprise_to_legacy

                legacy_metadata = convert_enterprise_to_legacy(metadata_list)
                return legacy_metadata

        except Exception as csv_error:
            # If both formats fail, provide helpful error message
            error_msg = f"Failed to load metadata from {metadata_path}. "
            if metadata_path.lower().endswith(".json"):
                error_msg += f"JSON format error: {csv_error}. "
            else:
                error_msg += f"CSV format error: {csv_error}. "
            error_msg += "Please ensure the file is in valid CSV or JSON enterprise metadata format."

            logger.error(error_msg)
            raise Exception(error_msg)

    def _convert_simple_json_to_legacy(self, json_data: dict) -> List[ColumnMetadata]:
        """
        Convert simple JSON metadata format to legacy ColumnMetadata objects.

        Supports both enterprise format and simple column-based formats.
        """
        legacy_columns = []

        # Handle enterprise format with 'columns' array
        if "columns" in json_data:
            columns_data = json_data["columns"]
        # Handle direct column array format
        elif isinstance(json_data, list):
            columns_data = json_data
        # Handle flat format where top level keys are column names
        else:
            columns_data = [
                {"name": k, **v} for k, v in json_data.items() if isinstance(v, dict)
            ]

        for col_data in columns_data:
            # Get column name (try multiple field names)
            column_name = col_data.get("name") or col_data.get("column_name")
            if not column_name:
                continue

            # Get data type
            data_type = col_data.get("data_type", "string")

            # Create basic metadata object
            metadata = ColumnMetadata(
                column_name=column_name,
                data_type=data_type,
                unique_flag=col_data.get("unique", False),
                nullable=not col_data.get("required", False),
                description=col_data.get("description", ""),
            )

            # Extract constraints
            constraints = col_data.get("constraints", {})
            if constraints:
                metadata.min_value = constraints.get("min_value")
                metadata.max_value = constraints.get("max_value")
                metadata.max_length = constraints.get("max_length")

                # Handle allowed_values as either list or string
                allowed_values = constraints.get("allowed_values")
                if allowed_values:
                    if isinstance(allowed_values, list):
                        metadata.allowed_values = ",".join(map(str, allowed_values))
                    else:
                        metadata.allowed_values = str(allowed_values)

            # Handle relationships
            relationships = col_data.get("relationships", {})
            if relationships and relationships.get("dependent_columns"):
                dependent_cols = relationships["dependent_columns"]
                if isinstance(dependent_cols, list) and dependent_cols:
                    metadata.dependent_column = dependent_cols[0]
                elif isinstance(dependent_cols, str):
                    metadata.dependent_column = dependent_cols

            # Handle business rules - add dynamically if present
            business_rules = col_data.get("business_rules", [])
            if business_rules and isinstance(business_rules, list) and business_rules:
                # Add business_rule field dynamically
                metadata.business_rule = business_rules[0].get("description", "")

            legacy_columns.append(metadata)

        logger.info(
            f"Converted {len(legacy_columns)} columns from JSON to legacy format"
        )
        return legacy_columns

    def analyze(self, metadata_path: str, data_path: str) -> List[ImputationSuggestion]:
        """
        Analyze dataset and return imputation suggestions.

        Args:
            metadata_path: Path to metadata file (CSV or JSON format)
            data_path: Path to data CSV file

        Returns:
            List of ImputationSuggestion objects
        """
        logger.info(f"Analyzing dataset: {data_path}")
        start_time = time.time()

        # Load metadata - auto-detect format and handle both CSV and JSON
        metadata_list = self._load_metadata_auto_format(metadata_path)
        metadata_dict = {meta.column_name: meta for meta in metadata_list}

        data = load_data(data_path, metadata_list)

        # Analyze each column
        suggestions = []
        for metadata in metadata_list:
            column_name = metadata.column_name

            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue

            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue

            # Analyze single column
            data_series = data[column_name]

            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, metadata, self.config)

            # Step 2: Missingness mechanism analysis
            missingness_analysis = analyze_missingness_mechanism(
                column_name, data, metadata_dict, self.config
            )

            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name,
                data_series,
                metadata,
                missingness_analysis,
                outlier_analysis,
                self.config,
                data,
                metadata_dict,
            )

            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score,
            )

            suggestions.append(suggestion)

        duration = time.time() - start_time
        logger.info(
            f"Analysis completed in {duration:.2f}s - {len(suggestions)} suggestions"
        )

        return suggestions

    def analyze_dataframe(
        self,
        data: pd.DataFrame,
        metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]],
    ) -> List[ImputationSuggestion]:
        """
        Analyze DataFrame directly with metadata objects.

        Args:
            data: Pandas DataFrame to analyze
            metadata: List or dict of ColumnMetadata objects

        Returns:
            List of ImputationSuggestion objects
        """
        logger.info(
            f"Analyzing DataFrame with {len(data)} rows, {len(data.columns)} columns"
        )
        start_time = time.time()

        # Normalize metadata to dict format
        if isinstance(metadata, list):
            metadata_dict = {meta.column_name: meta for meta in metadata}
            metadata_list = metadata
        else:
            metadata_dict = metadata
            metadata_list = list(metadata.values())

        # Analyze each column
        suggestions = []
        for meta in metadata_list:
            column_name = meta.column_name

            # Skip if column doesn't exist or should be skipped
            if column_name not in data.columns:
                logger.warning(f"Column {column_name} not found in data - skipping")
                continue

            if should_skip_column(column_name, self.config):
                logger.info(f"Skipping column {column_name} per configuration")
                continue

            # Analyze single column
            data_series = data[column_name]

            # Step 1: Outlier analysis
            outlier_analysis = analyze_outliers(data_series, meta, self.config)

            # Step 2: Missingness mechanism analysis
            missingness_analysis = analyze_missingness_mechanism(
                column_name, data, metadata_dict, self.config
            )

            # Step 3: Imputation method proposal
            imputation_proposal = propose_imputation_method(
                column_name,
                data_series,
                meta,
                missingness_analysis,
                outlier_analysis,
                self.config,
                data,
                metadata_dict,
            )

            # Create suggestion
            suggestion = ImputationSuggestion(
                column_name=column_name,
                missing_count=missingness_analysis.missing_count,
                missing_percentage=missingness_analysis.missing_percentage,
                mechanism=missingness_analysis.mechanism.value,
                proposed_method=imputation_proposal.method.value,
                rationale=imputation_proposal.rationale,
                outlier_count=outlier_analysis.outlier_count,
                outlier_percentage=outlier_analysis.outlier_percentage,
                outlier_handling=outlier_analysis.handling_strategy.value,
                outlier_rationale=outlier_analysis.rationale,
                confidence_score=imputation_proposal.confidence_score,
            )

            suggestions.append(suggestion)

        duration = time.time() - start_time
        logger.info(
            f"DataFrame analysis completed in {duration:.2f}s - {len(suggestions)} suggestions"
        )

        return suggestions


# Simple convenience function for client applications
def analyze_imputation_requirements(
    data_path: Union[str, pd.DataFrame],
    metadata_path: Optional[str] = None,
    config: AnalysisConfig = None,
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze imputation requirements with optional metadata.

    Args:
        data_path: Path to data CSV file OR pandas DataFrame
        metadata_path: Path to metadata file - CSV or JSON format (optional - will auto-infer if not provided)
        config: Optional analysis configuration

    Returns:
        List of ImputationSuggestion objects

    Examples:
        >>> # With explicit CSV metadata (recommended for production)
        >>> suggestions = analyze_imputation_requirements('data.csv', 'meta.csv')
        >>>
        >>> # With enterprise JSON metadata (enterprise production)
        >>> suggestions = analyze_imputation_requirements('data.csv', 'enterprise_meta.json')
        >>>
        >>> # With auto-inferred metadata (quick analysis)
        >>> suggestions = analyze_imputation_requirements('data.csv')
        >>>
        >>> for s in suggestions:
        ...     print(f"{s.column_name}: {s.proposed_method}")
    """
    from .metadata_inference import infer_metadata_from_dataframe

    if metadata_path:
        # Use explicit metadata file
        analyzer = SimpleImputationAnalyzer(config)
        return analyzer.analyze(metadata_path, data_path)
    else:
        # Auto-infer metadata from data
        if isinstance(data_path, pd.DataFrame):
            df = data_path
        else:
            try:
                df = pd.read_csv(data_path)
            except Exception as e:
                raise FileNotFoundError(f"Could not load data file {data_path}: {e}")

        inferred_metadata = infer_metadata_from_dataframe(df, warn_user=True)
        return analyze_dataframe(data=df, metadata=inferred_metadata, config=config)


def analyze_dataframe(
    data: pd.DataFrame,
    metadata: Union[List[ColumnMetadata], Dict[str, ColumnMetadata]],
    config: AnalysisConfig = None,
) -> List[ImputationSuggestion]:
    """
    Simple function to analyze DataFrame directly.

    Args:
        data: Pandas DataFrame to analyze
        metadata: Column metadata (list or dict)
        config: Optional analysis configuration

    Returns:
        List of ImputationSuggestion objects

    Example:
        >>> import pandas as pd
        >>> from funimpute.models import ColumnMetadata
        >>>
        >>> data = pd.DataFrame({'age': [25, None, 30], 'name': ['A', 'B', None]})
        >>> metadata = [
        ...     ColumnMetadata('age', 'integer'),
        ...     ColumnMetadata('name', 'string')
        ... ]
        >>> suggestions = analyze_dataframe(data, metadata)
    """
    analyzer = SimpleImputationAnalyzer(config)
    return analyzer.analyze_dataframe(data, metadata)
