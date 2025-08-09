"""
Data models and enums for the imputation analysis service.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator

# Data type constants for faster access
DATA_TYPES = {
    "INTEGER": "integer",
    "FLOAT": "float", 
    "STRING": "string",
    "CATEGORICAL": "categorical",
    "BOOLEAN": "boolean",
    "DATETIME": "datetime"
}

class DataType(Enum):
    """Data types for columns."""
    INTEGER = DATA_TYPES["INTEGER"]
    FLOAT = DATA_TYPES["FLOAT"]
    STRING = DATA_TYPES["STRING"]
    CATEGORICAL = DATA_TYPES["CATEGORICAL"]
    BOOLEAN = DATA_TYPES["BOOLEAN"]
    DATETIME = DATA_TYPES["DATETIME"]


# Missingness mechanism constants
MISSINGNESS_TYPES = {
    "MCAR": "MCAR",  # Missing Completely At Random
    "MAR": "MAR",    # Missing At Random
    "MNAR": "MNAR",  # Missing Not At Random
    "UNKNOWN": "Unknown"
}

class MissingnessType(Enum):
    """Missingness mechanisms for statistical analysis."""
    MCAR = MISSINGNESS_TYPES["MCAR"]
    MAR = MISSINGNESS_TYPES["MAR"]
    MNAR = MISSINGNESS_TYPES["MNAR"]
    UNKNOWN = MISSINGNESS_TYPES["UNKNOWN"]

# Keep legacy alias for backward compatibility
MissingnessMechanism = MissingnessType


# Imputation method constants for consistency
IMPUTATION_METHODS = {
    "MEDIAN": "Median",
    "MEAN": "Mean",
    "MODE": "Mode",
    "REGRESSION": "Regression",
    "KNN": "kNN",
    "CONSTANT_MISSING": "Constant 'Missing'",
    "MANUAL_BACKFILL": "Manual Backfill",
    "BUSINESS_RULE": "Business Rule",
    "FORWARD_FILL": "Forward Fill",
    "BACKWARD_FILL": "Backward Fill",
    "NO_ACTION_NEEDED": "No action needed",
    "ERROR_INVALID_METADATA": "Error: Invalid metadata"
}

class ImputationMethod(Enum):
    """Available imputation methods."""
    MEDIAN = IMPUTATION_METHODS["MEDIAN"]
    MEAN = IMPUTATION_METHODS["MEAN"]
    MODE = IMPUTATION_METHODS["MODE"]
    REGRESSION = IMPUTATION_METHODS["REGRESSION"]
    KNN = IMPUTATION_METHODS["KNN"]
    CONSTANT_MISSING = IMPUTATION_METHODS["CONSTANT_MISSING"]
    MANUAL_BACKFILL = IMPUTATION_METHODS["MANUAL_BACKFILL"]
    BUSINESS_RULE = IMPUTATION_METHODS["BUSINESS_RULE"]
    FORWARD_FILL = IMPUTATION_METHODS["FORWARD_FILL"]
    BACKWARD_FILL = IMPUTATION_METHODS["BACKWARD_FILL"]
    NO_ACTION_NEEDED = IMPUTATION_METHODS["NO_ACTION_NEEDED"]
    ERROR_INVALID_METADATA = IMPUTATION_METHODS["ERROR_INVALID_METADATA"]


# Outlier handling and exception rule constants
OUTLIER_STRATEGIES = {
    "CAP_TO_BOUNDS": "Cap to bounds",
    "CONVERT_TO_NAN": "Convert to NaN",
    "LEAVE_AS_IS": "Leave as is",
    "REMOVE_ROWS": "Remove rows"
}

EXCEPTION_RULES = {
    "NO_MISSING_VALUES": "no_missing_values",
    "UNIQUE_IDENTIFIER": "unique_identifier",
    "ALL_VALUES_MISSING": "all_values_missing",
    "MNAR_NO_BUSINESS_RULE": "mnar_no_business_rule",
    "SKIP_COLUMN": "skip_column",
    "METADATA_VALIDATION_FAILURE": "metadata_validation_failure"
}

class OutlierHandling(Enum):
    """Outlier handling strategies."""
    CAP_TO_BOUNDS = OUTLIER_STRATEGIES["CAP_TO_BOUNDS"]
    CONVERT_TO_NAN = OUTLIER_STRATEGIES["CONVERT_TO_NAN"]
    LEAVE_AS_IS = OUTLIER_STRATEGIES["LEAVE_AS_IS"]
    REMOVE_ROWS = OUTLIER_STRATEGIES["REMOVE_ROWS"]

class ExceptionRule(Enum):
    """Exception handling rules for imputation suggestions."""
    NO_MISSING_VALUES = EXCEPTION_RULES["NO_MISSING_VALUES"]
    UNIQUE_IDENTIFIER = EXCEPTION_RULES["UNIQUE_IDENTIFIER"]
    ALL_VALUES_MISSING = EXCEPTION_RULES["ALL_VALUES_MISSING"]
    MNAR_NO_BUSINESS_RULE = EXCEPTION_RULES["MNAR_NO_BUSINESS_RULE"]
    SKIP_COLUMN = EXCEPTION_RULES["SKIP_COLUMN"]
    METADATA_VALIDATION_FAILURE = EXCEPTION_RULES["METADATA_VALIDATION_FAILURE"]


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
