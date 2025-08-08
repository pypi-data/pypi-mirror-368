"""
Command-line interface for the imputation analysis service.
"""

import click
import sys
import os
from pathlib import Path
from typing import Optional

from .analyzer import ImputationAnalyzer
from .io import load_configuration
from .enterprise_loader import MetadataValidationError


@click.command()
@click.option(
    "--metadata", "-m", required=True, help="Path to metadata file (CSV or JSON format)"
)
@click.option("--data", "-d", required=True, help="Path to data CSV file")
@click.option("--config", "-c", help="Path to configuration YAML file")
@click.option(
    "--metadata-format",
    "-f",
    type=click.Choice(["csv", "json", "auto"]),
    default="auto",
    help="Metadata format (auto-detected by default)",
)
@click.option(
    "--validate-enterprise/--no-validate-enterprise",
    default=True,
    help="Validate enterprise JSON metadata (default: enabled)",
)
@click.option("--output", "-o", help="Output path for suggestions CSV")
@click.option("--audit-log", "-a", help="Output path for audit log JSONL")
@click.option(
    "--iqr-multiplier", type=float, help="IQR multiplier for outlier detection"
)
@click.option("--outlier-threshold", type=float, help="Outlier percentage threshold")
@click.option(
    "--correlation-threshold",
    type=float,
    help="Correlation threshold for MAR detection",
)
@click.option("--chi-square-alpha", type=float, help="Chi-square test alpha level")
@click.option(
    "--point-biserial-threshold",
    type=float,
    help="Point-biserial correlation threshold",
)
@click.option(
    "--skewness-threshold", type=float, help="Skewness threshold for method selection"
)
@click.option("--missing-threshold", type=float, help="Missing percentage threshold")
@click.option("--skip-columns", help="Comma-separated list of columns to skip")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def main(
    metadata: str,
    data: str,
    config: Optional[str],
    metadata_format: str,
    validate_enterprise: bool,
    output: Optional[str],
    audit_log: Optional[str],
    iqr_multiplier: Optional[float],
    outlier_threshold: Optional[float],
    correlation_threshold: Optional[float],
    chi_square_alpha: Optional[float],
    point_biserial_threshold: Optional[float],
    skewness_threshold: Optional[float],
    missing_threshold: Optional[float],
    skip_columns: Optional[str],
    verbose: bool,
):
    """
    Analyze data and suggest imputation methods for missing values.

    This tool analyzes your dataset and metadata to suggest appropriate
    imputation methods for each column with missing values. It considers
    data types, missingness mechanisms, outliers, and business rules.

    Examples:

    \b
    # Basic usage with legacy CSV metadata
    impute-analyze -m data/metadata.csv -d data/material_master_data.csv

    \b
    # Using enterprise JSON metadata with validation
    impute-analyze -m examples/sample_enterprise_metadata.json -d data/material_master_data.csv -f json

    \b
    # Skip validation for enterprise metadata
    impute-analyze -m metadata.json -d data/material_master_data.csv --no-validate-enterprise

    \b
    # With custom configuration and output paths
    impute-analyze -m data/metadata.csv -d data/material_master_data.csv -c config.yml -o output/suggestions.csv

    \b
    # Override specific parameters
    impute-analyze -m data/metadata.csv -d data/material_master_data.csv --iqr-multiplier 2.0 --skip-columns "id,timestamp"
    """

    # Set up logging
    import logging

    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    try:
        # Validate input files
        if not os.path.exists(metadata):
            raise click.ClickException(f"Metadata file not found: {metadata}")
        if not os.path.exists(data):
            raise click.ClickException(f"Data file not found: {data}")

        # Load configuration with CLI overrides
        analysis_config = load_configuration(config)

        # Apply CLI parameter overrides
        if output:
            analysis_config.output_path = output
        if audit_log:
            analysis_config.audit_log_path = audit_log
        if iqr_multiplier is not None:
            analysis_config.iqr_multiplier = iqr_multiplier
        if outlier_threshold is not None:
            analysis_config.outlier_threshold = outlier_threshold
        if correlation_threshold is not None:
            analysis_config.correlation_threshold = correlation_threshold
        if chi_square_alpha is not None:
            analysis_config.chi_square_alpha = chi_square_alpha
        if point_biserial_threshold is not None:
            analysis_config.point_biserial_threshold = point_biserial_threshold
        if skewness_threshold is not None:
            analysis_config.skewness_threshold = skewness_threshold
        if missing_threshold is not None:
            analysis_config.missing_threshold = missing_threshold
        if skip_columns:
            analysis_config.skip_columns = [
                col.strip() for col in skip_columns.split(",")
            ]

        logger.info(f"Starting imputation analysis...")
        logger.info(f"Metadata: {metadata} (format: {metadata_format})")
        logger.info(f"Data: {data}")
        logger.info(f"Enterprise validation: {validate_enterprise}")

        # Create analyzer and run analysis
        analyzer = ImputationAnalyzer(analysis_config)
        try:
            results = analyzer.analyze_dataset_cli(
                metadata_path=metadata,
                data_path=data,
                metadata_format=metadata_format,
                validate_enterprise=validate_enterprise,
            )

            # Display results summary
            suggestions = results["suggestions"]
            quality_metrics = results["quality_metrics"]

            click.echo(f"\n{'='*60}")
            click.echo(f"IMPUTATION ANALYSIS COMPLETE")
            click.echo(f"{'='*60}")
            click.echo(f"Metadata format: {results['metadata_format']}")
            click.echo(f"Columns analyzed: {len(suggestions)}")
            click.echo(f"Analysis duration: {results['analysis_duration']:.2f} seconds")
            click.echo(f"Data quality score: {quality_metrics.data_quality_score:.3f}")
            click.echo(
                f"Total missing values: {quality_metrics.total_missing_values:,}"
            )
            click.echo(f"Total outliers detected: {quality_metrics.total_outliers:,}")
            click.echo(
                f"Average confidence score: {quality_metrics.average_confidence:.3f}"
            )

            # Show validation warnings if any
            if results["validation_errors"]:
                click.echo(f"\nValidation warnings:")
                for error in results["validation_errors"]:
                    click.echo(f"  {error}")

            # Show method distribution
            method_dist = analyzer.get_method_distribution(suggestions)
            if method_dist:
                click.echo(f"\nProposed methods distribution:")
                for method, count in sorted(method_dist.items()):
                    click.echo(f"  {method}: {count}")

            # Save output files
            from .io import save_suggestions

            output_path = output or analysis_config.output_path
            save_suggestions(suggestions, output_path)

            # Show output files
            click.echo(f"\nOutput files:")
            click.echo(f"  Suggestions: {output_path}")
            click.echo(f"  Audit log: {results['output_files']['audit_log']}")

            click.echo(f"\n{'='*60}")
            click.echo(f"ANALYSIS COMPLETE")
            click.echo(f"{'='*60}")

        finally:
            # Clean up analyzer resources if needed
            if hasattr(analyzer, "metrics_collector"):
                try:
                    analyzer.metrics_collector.stop_server()
                except Exception as e:
                    logger.warning(f"Error stopping metrics server: {e}")

    except MetadataValidationError as e:
        logger.error(f"Metadata validation failed: {e}")
        raise click.ClickException(f"Metadata validation failed: {e}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise click.ClickException(str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.ClickException(f"Analysis failed: {e}")


if __name__ == "__main__":
    main()
