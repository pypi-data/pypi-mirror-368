"""
Simple, intelligent imputation analysis for data science.
"""

__version__ = "1.3.5"
__author__ = "Rajesh Ramachander"

# Simple API for client applications
from .simple_analyzer import (
    SimpleImputationAnalyzer,
    analyze_imputation_requirements,
    analyze_dataframe,
)

# Metadata inference for auto-detection
from .metadata_inference import infer_metadata_from_dataframe

# Core models for advanced usage
from .models import ColumnMetadata, AnalysisConfig, ImputationSuggestion

# Legacy analyzer for backward compatibility
from .analyzer import ImputationAnalyzer

__all__ = [
    # Simple API (recommended for most users)
    "analyze_imputation_requirements",
    "analyze_dataframe",
    "SimpleImputationAnalyzer",
    # Metadata inference
    "infer_metadata_from_dataframe",
    # Core models
    "ColumnMetadata",
    "AnalysisConfig",
    "ImputationSuggestion",
    # Advanced/legacy
    "ImputationAnalyzer",
]
