"""
Data models and enums for the imputation analysis service.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator


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

    MCAR = "MCAR"  # Missing Completely At Random
    MAR = "MAR"  # Missing At Random
    MNAR = "MNAR"  # Missing Not At Random
    UNKNOWN = "Unknown"


# Keep legacy alias for backward compatibility
MissingnessMechanism = MissingnessType


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

    This model contains 21 total fields, divided into two categories:

    AUTOMATICALLY INFERRABLE (15 fields):
    - Core: column_name, data_type, description
    - Characteristics: role, do_not_impute, time_index, group_by, unique_flag, nullable
    - Constraints: min_value, max_value, max_length, allowed_values, sentinel_values
    - Relationships: dependent_column (statistically inferred)

    REQUIRE MANUAL SPECIFICATION (6 fields):
    - business_rule: Business logic rules (domain knowledge required)
    - dependency_rule: Calculation/relationship rules (domain knowledge required)
    - meaning_of_missing: Business context of missing values
    - order_by: Ordering logic within groups
    - fallback_method: Guaranteed fallback imputation method
    - policy_version: Audit trail version

    The auto-inference system (metadata_inference.py) populates only the 15 inferrable
    fields. The remaining 6 fields must be manually specified if needed.
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
    business_rule: Optional[str] = None
    dependency_rule: Optional[str] = None  # Specific calculation/relationship rules
    allowed_values: Optional[str] = (
        None  # JSON string or comma-separated values for categorical validation
    )

    # Enhanced metadata for production use
    role: str = "feature"  # identifier, feature, target, time_index, group_by, ignore
    do_not_impute: bool = False  # Prevent imputation of this column
    sentinel_values: Optional[str] = None  # Special values like "-999,NULL,UNKNOWN"
    meaning_of_missing: Optional[str] = (
        None  # Business context: "refused", "not_applicable", etc.
    )
    time_index: bool = False  # Is this the time ordering column
    group_by: bool = False  # Is this a grouping/cohort column
    order_by: Optional[str] = None  # Column to order by within groups
    fallback_method: Optional[str] = (
        None  # Guaranteed imputation method: "mean", "median", "mode"
    )
    policy_version: str = "v1.0"  # Version for audit trail


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
    audit_log_path: str = "audit_logs.jsonl"
    metrics_port: int = Field(default=8001, ge=1024, le=65535)

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
