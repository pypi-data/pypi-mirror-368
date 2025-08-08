"""
Main imputation analysis service orchestrating all components.
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

from .models import ColumnAnalysis, ImputationSuggestion, ColumnMetadata, AnalysisConfig
from .io import (
    load_metadata,
    load_configuration,
    load_data,
    save_suggestions,
    append_audit_log,
)
from .exceptions import should_skip_column
from .outliers import analyze_outliers
from .mechanism import analyze_missingness_mechanism
from .proposal import propose_imputation_method
from .metrics import get_metrics_collector, start_metrics_server, MetricsContext
from collections import Counter


class ImputationAnalyzer:
    """
    Enterprise-grade imputation analysis and suggestion service.

    This class orchestrates the complete analysis pipeline:
    1. Validates metadata schema
    2. Loads configuration with environment overrides
    3. Performs modular analysis per column (outliers, mechanism, proposal)
    4. Emits structured audit logs and quality metrics
    5. Generates comprehensive imputation suggestions
    """

    def __init__(self, config: AnalysisConfig):
        """
        Initialize the analyzer with configuration.

        Args:
            config: Analysis configuration object
        """
        self.config = config
        self.metrics = get_metrics_collector(config.metrics_port)
        self.analysis_results: List[ColumnAnalysis] = []

        # Start metrics server
        start_metrics_server(config.metrics_port)

    def analyze_dataset(
        self,
        metadata_path: str,
        data_path: str,
        metadata_format: str = "auto",
        validate_enterprise: bool = True,
    ) -> List[ImputationSuggestion]:
        """
        Perform complete analysis of a dataset.

        Args:
            metadata_path: Path to metadata CSV file
            data_path: Path to data CSV file
            metadata_format: Metadata format ("csv", "json", "auto")
            validate_enterprise: Whether to validate enterprise metadata

        Returns:
            List of ImputationSuggestion objects

        Raises:
            Various exceptions for validation failures
        """
        start_time = time.time()

        try:
            # Step 1: Load and validate metadata
            print("Loading and validating metadata...")
            metadata_list = load_metadata(
                metadata_path, metadata_format, validate_enterprise
            )
            metadata_dict = {meta.column_name: meta for meta in metadata_list}

            # Step 2: Load data
            print("Loading data...")
            data = load_data(data_path, metadata_list)

            # Step 3: Analyze each column
            print(f"Analyzing {len(metadata_list)} columns...")
            suggestions = []
            total_missing = 0
            total_outliers = 0

            for metadata in metadata_list:
                column_name = metadata.column_name

                if column_name not in data.columns:
                    print(f"Warning: Column {column_name} not found in data - skipping")
                    continue

                # Check if column should be skipped per configuration
                if should_skip_column(column_name, self.config):
                    print(f"Skipping column {column_name} per configuration")
                    continue

                # Analyze single column
                analysis_result = self._analyze_column(column_name, data, metadata_dict)

                self.analysis_results.append(analysis_result)

                # Convert to suggestion format
                suggestion = self._create_suggestion(analysis_result)
                suggestions.append(suggestion)

                # Update totals for metrics
                total_missing += analysis_result.missingness_analysis.missing_count
                total_outliers += analysis_result.outlier_analysis.outlier_count

                # Record metrics
                self.metrics.record_column_processed(
                    metadata.data_type,
                    analysis_result.missingness_analysis.mechanism.value,
                )
                self.metrics.record_confidence_score(
                    analysis_result.imputation_proposal.method.value,
                    analysis_result.missingness_analysis.mechanism.value,
                    analysis_result.imputation_proposal.confidence_score,
                )

            # Update aggregate metrics
            self.metrics.update_missing_values_total(total_missing)
            self.metrics.update_outliers_total(total_outliers)

            # Calculate and record data quality score
            quality_score = self.metrics.calculate_data_quality_score(
                self.analysis_results
            )
            self.metrics.update_data_quality_score("current_dataset", quality_score)

            # Record total analysis time
            total_duration = time.time() - start_time
            self.metrics.update_total_analysis_duration(total_duration)

            print(f"Analysis completed in {total_duration:.2f} seconds")
            print(f"Data quality score: {quality_score:.3f}")

            return suggestions

        except Exception as e:
            # Log error to audit log
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": "ERROR",
                "message": f"Analysis failed: {str(e)}",
                "metadata_path": metadata_path,
                "data_path": data_path,
            }
            append_audit_log(error_entry, self.config.audit_log_path)
            raise

    def analyze_dataset_cli(
        self,
        metadata_path: str,
        data_path: str,
        metadata_format: str = "auto",
        validate_enterprise: bool = True,
    ) -> Dict[str, Any]:
        """
        CLI-compatible version that returns detailed results dictionary.

        Args:
            metadata_path: Path to metadata file
            data_path: Path to data CSV file
            metadata_format: Metadata format ("csv", "json", "auto")
            validate_enterprise: Whether to validate enterprise metadata

        Returns:
            Dictionary with suggestions, metrics, and metadata
        """
        import time

        start_time = time.time()
        suggestions = self.analyze_dataset(
            metadata_path, data_path, metadata_format, validate_enterprise
        )
        analysis_duration = time.time() - start_time

        # Calculate quality metrics
        total_missing = sum(s.missing_count for s in suggestions)
        total_outliers = sum(s.outlier_count for s in suggestions)
        avg_confidence = (
            sum(s.confidence_score for s in suggestions) / len(suggestions)
            if suggestions
            else 0
        )
        # Get the calculated quality score using existing analysis results
        data_quality_score = self.metrics.calculate_data_quality_score(
            self.analysis_results
        )

        from .models import DataQualityMetrics

        quality_metrics = DataQualityMetrics(
            total_missing_values=total_missing,
            total_outliers=total_outliers,
            data_quality_score=data_quality_score,
            average_confidence=avg_confidence,
            columns_analyzed=len(suggestions),
            analysis_duration=analysis_duration,
        )

        return {
            "suggestions": suggestions,
            "quality_metrics": quality_metrics,
            "analysis_duration": analysis_duration,
            "metadata_format": metadata_format,
            "validation_errors": [],  # Could be populated if needed
            "output_files": {
                "suggestions": self.config.output_path,
                "audit_log": self.config.audit_log_path,
            },
        }

    def get_method_distribution(
        self, suggestions: List[ImputationSuggestion]
    ) -> Dict[str, int]:
        """Get distribution of proposed methods."""
        methods = [s.proposed_method for s in suggestions]
        return dict(Counter(methods))

    def _analyze_column(
        self,
        column_name: str,
        data: pd.DataFrame,
        metadata_dict: Dict[str, ColumnMetadata],
    ) -> ColumnAnalysis:
        """
        Perform comprehensive analysis of a single column.

        Args:
            column_name: Name of the column to analyze
            data: Full dataset
            metadata_dict: Dictionary mapping column names to metadata

        Returns:
            ColumnAnalysis object with complete results
        """
        metadata = metadata_dict[column_name]
        data_series = data[column_name]

        with MetricsContext(column_name, metadata.data_type) as ctx:
            analysis_start = time.time()

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

            analysis_duration = time.time() - analysis_start

            # Create analysis result
            analysis_result = ColumnAnalysis(
                column_name=column_name,
                data_type=metadata.data_type,
                outlier_analysis=outlier_analysis,
                missingness_analysis=missingness_analysis,
                imputation_proposal=imputation_proposal,
                metadata=metadata,
                analysis_timestamp=datetime.now().isoformat(),
                processing_duration_seconds=analysis_duration,
            )

            # Log to audit trail
            self._log_analysis_result(analysis_result)

            return analysis_result

    def _create_suggestion(
        self, analysis_result: ColumnAnalysis
    ) -> ImputationSuggestion:
        """
        Convert ColumnAnalysis to ImputationSuggestion format.

        Args:
            analysis_result: Complete analysis results

        Returns:
            ImputationSuggestion object for output
        """
        return ImputationSuggestion(
            column_name=analysis_result.column_name,
            missing_count=analysis_result.missingness_analysis.missing_count,
            missing_percentage=analysis_result.missingness_analysis.missing_percentage,
            mechanism=analysis_result.missingness_analysis.mechanism.value,
            proposed_method=analysis_result.imputation_proposal.method.value,
            rationale=analysis_result.imputation_proposal.rationale,
            outlier_count=analysis_result.outlier_analysis.outlier_count,
            outlier_percentage=analysis_result.outlier_analysis.outlier_percentage,
            outlier_handling=analysis_result.outlier_analysis.handling_strategy.value,
            outlier_rationale=analysis_result.outlier_analysis.rationale,
            confidence_score=analysis_result.imputation_proposal.confidence_score,
        )

    def _log_analysis_result(self, analysis_result: ColumnAnalysis) -> None:
        """
        Log detailed analysis results to audit log.

        Args:
            analysis_result: Complete analysis results to log
        """
        log_entry = {
            "timestamp": analysis_result.analysis_timestamp,
            "column_name": analysis_result.column_name,
            "data_type": analysis_result.data_type,
            "processing_duration_seconds": analysis_result.processing_duration_seconds,
            "missing_analysis": {
                "missing_count": analysis_result.missingness_analysis.missing_count,
                "missing_percentage": analysis_result.missingness_analysis.missing_percentage,
                "mechanism": analysis_result.missingness_analysis.mechanism.value,
                "test_statistic": analysis_result.missingness_analysis.test_statistic,
                "p_value": analysis_result.missingness_analysis.p_value,
                "related_columns": analysis_result.missingness_analysis.related_columns,
                "rationale": analysis_result.missingness_analysis.rationale,
            },
            "outlier_analysis": {
                "outlier_count": analysis_result.outlier_analysis.outlier_count,
                "outlier_percentage": analysis_result.outlier_analysis.outlier_percentage,
                "lower_bound": analysis_result.outlier_analysis.lower_bound,
                "upper_bound": analysis_result.outlier_analysis.upper_bound,
                "handling_strategy": analysis_result.outlier_analysis.handling_strategy.value,
                "rationale": analysis_result.outlier_analysis.rationale,
            },
            "imputation_proposal": {
                "method": analysis_result.imputation_proposal.method.value,
                "rationale": analysis_result.imputation_proposal.rationale,
                "parameters": analysis_result.imputation_proposal.parameters,
                "confidence_score": analysis_result.imputation_proposal.confidence_score,
            },
            "metadata": {
                "min_value": analysis_result.metadata.min_value,
                "max_value": analysis_result.metadata.max_value,
                "unique_flag": analysis_result.metadata.unique_flag,
                "dependent_column": analysis_result.metadata.dependent_column,
                "business_rule": getattr(analysis_result.metadata, 'business_rule', None),
            },
        }

        append_audit_log(log_entry, self.config.audit_log_path)

    def save_results(self, suggestions: List[ImputationSuggestion]) -> None:
        """
        Save analysis results to output files.

        Args:
            suggestions: List of imputation suggestions to save
        """
        # Save suggestions CSV
        save_suggestions(suggestions, self.config.output_path)
        print(f"Imputation suggestions saved to: {self.config.output_path}")
        print(f"Audit logs saved to: {self.config.audit_log_path}")

        # Calculate and display data quality score
        data_quality = self.metrics.calculate_data_quality_score(suggestions)
        print(f"Data quality score: {data_quality:.2f}/1.0")


def analyze_imputation_requirements(
    metadata_path: str,
    data_path: str,
    config_path: str = None,
    metadata_format: str = "auto",
    validate_enterprise: bool = True,
) -> List[ImputationSuggestion]:
    """
    Main entry point for imputation analysis.

    Args:
        metadata_path: Path to metadata CSV file
        data_path: Path to data CSV file
        config_path: Optional path to configuration file
        metadata_format: Metadata format ("csv", "json", "auto")
        validate_enterprise: Whether to validate enterprise metadata

    Returns:
        List of ImputationSuggestion objects
    """
    # Load configuration
    config = load_configuration(config_path)

    # Override paths from parameters
    config.metadata_path = metadata_path
    config.data_path = data_path

    # Create analyzer and run analysis
    analyzer = ImputationAnalyzer(config)
    suggestions = analyzer.analyze_dataset(
        metadata_path, data_path, metadata_format, validate_enterprise
    )

    # Save results
    analyzer.save_results(suggestions)

    return suggestions
