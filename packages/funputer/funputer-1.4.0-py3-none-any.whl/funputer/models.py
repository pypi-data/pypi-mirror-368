"""
Data models, enums, and metadata field definitions for the imputation analysis service.

This module consolidates all data structures including field definitions, Pydantic models,
and enums to ensure consistency across the package.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# METADATA FIELD DEFINITIONS
# ============================================================================
# Consolidated from metadata_fields.py for better organization

# All metadata fields in logical order
ALL_METADATA_FIELDS = [
    # Core identification (3 fields)
    'column_name',          # Column identifier
    'data_type',            # Data type (integer, float, string, categorical, datetime, boolean)
    'description',          # Human-readable description
    
    # Data characteristics (6 fields) - All inferrable
    'role',                 # Column role (identifier, feature, target, time_index, group_by, ignore)
    'do_not_impute',       # Flag to prevent imputation (TRUE/FALSE)
    'time_index',          # Is this a time ordering column (TRUE/FALSE)
    'group_by',            # Is this a grouping column (TRUE/FALSE)
    'unique_flag',         # Should values be unique (TRUE/FALSE)
    'nullable',            # Can contain null values (TRUE/FALSE)
    
    # Value constraints (5 fields) - All inferrable
    'min_value',           # Minimum numeric value
    'max_value',           # Maximum numeric value
    'max_length',          # Maximum string length
    'allowed_values',      # Comma-separated list of allowed values
    'sentinel_values',     # Special values like -999, NULL, UNKNOWN
    
    # Relationships (1 field) - Inferrable
    'dependent_column',    # Statistically dependent column
    
    # Business context (6 fields) - All require manual input
    'business_rule',       # Business logic constraints
    'dependency_rule',     # Calculation formulas/rules
    'meaning_of_missing',  # Why data is missing (refused, not_applicable, etc.)
    'order_by',           # Ordering logic within groups
    'fallback_method',    # Guaranteed imputation method
    'policy_version'      # Metadata version for audit trail
]

# Fields that can be auto-inferred from data (15 fields)
INFERRABLE_FIELDS = ALL_METADATA_FIELDS[:15]  # First 15 fields

# Fields requiring manual input (6 fields)
NON_INFERRABLE_FIELDS = ALL_METADATA_FIELDS[15:]  # Last 6 fields

# Field descriptions for documentation
FIELD_DESCRIPTIONS = {
    'column_name': "Name of the column in the dataset",
    'data_type': "Data type: integer, float, string, categorical, datetime, boolean",
    'description': "Human-readable description of the column",
    'role': "Column role: identifier, feature, target, time_index, group_by, ignore",
    'do_not_impute': "Prevent imputation of this column (TRUE/FALSE)",
    'time_index': "Is this the time ordering column (TRUE/FALSE)",
    'group_by': "Is this a grouping/cohort column (TRUE/FALSE)",
    'unique_flag': "Should values be unique (TRUE/FALSE)",
    'nullable': "Can this column contain null values (TRUE/FALSE)",
    'min_value': "Minimum allowed numeric value",
    'max_value': "Maximum allowed numeric value",
    'max_length': "Maximum string length",
    'allowed_values': "Comma-separated list of allowed values for categorical data",
    'sentinel_values': "Special values indicating missing data (e.g., -999, NULL)",
    'dependent_column': "Column this depends on statistically",
    'business_rule': "Business logic constraints (manual input required)",
    'dependency_rule': "Calculation formulas or dependency rules (manual input required)",
    'meaning_of_missing': "Business context of missing values (manual input required)",
    'order_by': "Ordering logic within groups (manual input required)",
    'fallback_method': "Guaranteed imputation method to use (manual input required)",
    'policy_version': "Version for audit trail (default: v1.0)"
}

# Default values for optional fields
FIELD_DEFAULTS = {
    'description': 'Auto-inferred column',
    'role': 'feature',
    'do_not_impute': False,
    'time_index': False,
    'group_by': False,
    'unique_flag': False,
    'nullable': True,
    'min_value': None,
    'max_value': None,
    'max_length': None,
    'allowed_values': None,
    'sentinel_values': None,
    'dependent_column': None,
    'business_rule': '',
    'dependency_rule': '',
    'meaning_of_missing': '',
    'order_by': '',
    'fallback_method': '',
    'policy_version': 'v1.0'
}


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class DataType(Enum):
    """Data types for columns."""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    DATETIME = "datetime"


class MissingnessType(Enum):
    """Missingness mechanisms for statistical analysis."""
    MCAR = "MCAR"    # Missing Completely At Random
    MAR = "MAR"      # Missing At Random
    MNAR = "MNAR"    # Missing Not At Random
    UNKNOWN = "Unknown"


class ImputationMethod(Enum):
    """Available imputation methods."""
    MEDIAN = "Median"
    MEAN = "Mean"
    MODE = "Mode"
    REGRESSION = "Regression"
    KNN = "kNN"
    CONSTANT_MISSING = "Constant 'Missing'"
    MANUAL_BACKFILL = "Manual Backfill"
    BUSINESS_RULE = "Business Rule"
    FORWARD_FILL = "Forward Fill"
    BACKWARD_FILL = "Backward Fill"
    NO_ACTION_NEEDED = "No action needed"
    ERROR_INVALID_METADATA = "Error: Invalid metadata"


class OutlierHandling(Enum):
    """Outlier handling strategies."""
    CAP_TO_BOUNDS = "Cap to bounds"
    CONVERT_TO_NAN = "Convert to NaN"
    LEAVE_AS_IS = "Leave as is"
    REMOVE_ROWS = "Remove rows"


class ExceptionRule(Enum):
    """Exception handling rules for imputation suggestions."""
    NO_MISSING_VALUES = "no_missing_values"
    UNIQUE_IDENTIFIER = "unique_identifier"
    ALL_VALUES_MISSING = "all_values_missing"
    MNAR_NO_BUSINESS_RULE = "mnar_no_business_rule"
    SKIP_COLUMN = "skip_column"
    METADATA_VALIDATION_FAILURE = "metadata_validation_failure"


@dataclass
class ColumnMetadata:
    """
    Metadata for a single column.

    This model contains the 15 fields that can be automatically inferred:

    AUTOMATICALLY INFERRABLE (15 fields):
    - Core: column_name, data_type, description
    - Characteristics: role, do_not_impute, time_index, group_by, unique_flag, nullable
    - Constraints: min_value, max_value, max_length, allowed_values, sentinel_values
    - Relationships: dependent_column (statistically inferred)

    Additional manual-only fields (business_rule, dependency_rule, meaning_of_missing, 
    order_by, fallback_method, policy_version) can be added dynamically when needed.
    """

    column_name: str
    data_type: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    unique_flag: bool = False
    nullable: bool = True
    description: str = ""
    dependent_column: Optional[str] = None
    allowed_values: Optional[str] = (
        None  # JSON string or comma-separated values for categorical validation
    )

    # Enhanced metadata for production use (using constants for consistency)
    role: str = "feature"  # identifier, feature, target, time_index, group_by, ignore
    do_not_impute: bool = False  # Prevent imputation of this column
    sentinel_values: Optional[str] = None  # Special values like "-999,NULL,UNKNOWN"
    time_index: bool = False  # Is this the time ordering column
    group_by: bool = False  # Is this a grouping/cohort column
    
    # Optional fields for test compatibility
    business_rule: Optional[str] = None  # Business rule for MNAR imputation
    meaning_of_missing: Optional[str] = None  # Semantic meaning of missing values
    dependency_rule: Optional[str] = None  # Dependency rules for validation
    order_by: Optional[str] = None  # Column for ordering data
    fallback_method: Optional[str] = None  # Fallback imputation method
    policy_version: Optional[str] = None  # Policy version for compliance




class AnalysisConfig(BaseModel):
    """Configuration for the analysis process."""

    iqr_multiplier: float = Field(default=1.5, ge=0.1, le=5.0)
    outlier_threshold: float = Field(
        default=0.05, ge=0.001, le=0.5, alias="outlier_percentage_threshold"
    )
    correlation_threshold: float = Field(default=0.3, ge=0.1, le=0.9)
    chi_square_alpha: float = Field(default=0.05, ge=0.001, le=0.1)
    point_biserial_threshold: float = Field(default=0.2, ge=0.1, le=0.8)
    skewness_threshold: float = Field(default=2.0, ge=0.5, le=10.0)
    missing_threshold: float = Field(
        default=0.8, ge=0.1, le=0.95, alias="missing_percentage_threshold"
    )
    skip_columns: List[str] = Field(default_factory=list)
    metadata_path: Optional[str] = None
    data_path: Optional[str] = None
    output_path: str = "imputation_suggestions.csv"

    @field_validator("iqr_multiplier")
    def validate_iqr_multiplier(cls, v):
        if v <= 0:
            raise ValueError("IQR multiplier must be positive")
        return v


class OutlierAnalysis(BaseModel):
    """Results of outlier analysis for a column."""

    outlier_count: int
    outlier_percentage: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    outlier_values: List[float] = Field(default_factory=list)
    handling_strategy: OutlierHandling
    rationale: str


class MissingnessAnalysis(BaseModel):
    """Results of missingness mechanism analysis."""

    missing_count: int
    missing_percentage: float
    mechanism: MissingnessType
    test_statistic: Optional[float]
    p_value: Optional[float]
    related_columns: List[str]
    rationale: str


class ImputationProposal(BaseModel):
    """Proposed imputation method with rationale."""

    method: ImputationMethod
    rationale: str
    parameters: Dict[str, Any]
    confidence_score: float


class ColumnAnalysis(BaseModel):
    """Complete analysis results for a single column."""

    column_name: str
    data_type: str
    outlier_analysis: OutlierAnalysis
    missingness_analysis: MissingnessAnalysis
    imputation_proposal: ImputationProposal
    metadata: ColumnMetadata
    analysis_timestamp: str
    processing_duration_seconds: float


class ImputationSuggestion(BaseModel):
    """Final suggestion output format."""

    column_name: str
    missing_count: int = 0
    missing_percentage: float = 0.0
    mechanism: str = "UNKNOWN"
    proposed_method: str
    rationale: str
    outlier_count: int = 0
    outlier_percentage: float = 0.0
    outlier_handling: str = "Leave as is"
    outlier_rationale: str = ""
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV output."""
        return {
            "Column": self.column_name,
            "Missing_Count": self.missing_count,
            "Missing_Percentage": f"{self.missing_percentage:.1f}%",
            "Missingness_Mechanism": self.mechanism,
            "Proposed_Method": self.proposed_method,
            "Rationale": self.rationale,
            "Outlier_Count": self.outlier_count,
            "Outlier_Percentage": f"{self.outlier_percentage:.1f}%",
            "Outlier_Handling": self.outlier_handling,
            "Outlier_Rationale": self.outlier_rationale,
            "Confidence_Score": f"{self.confidence_score:.3f}",
        }


class DataQualityMetrics(BaseModel):
    """Overall data quality metrics for a dataset."""

    total_missing_values: int
    total_outliers: int
    data_quality_score: float
    average_confidence: float
    columns_analyzed: int = 0
    analysis_duration: float = 0.0
