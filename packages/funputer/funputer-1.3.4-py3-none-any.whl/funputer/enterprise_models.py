"""
Enterprise-grade metadata models with formal schema validation.
"""

from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import re


class DataType(str, Enum):
    """Supported data types for columns."""

    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    CATEGORICAL = "categorical"


class MissingStrategyHint(str, Enum):
    """Hints about expected missingness mechanism."""

    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    CUSTOM = "custom"


class DefaultImputer(str, Enum):
    """Available imputation methods."""

    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    REGRESSION = "regression"
    KNN = "knn"
    BUSINESS_RULE = "business_rule"
    MANUAL = "manual"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    CONSTANT = "constant"


class ExtractionMethod(str, Enum):
    """Data extraction methods."""

    FULL_LOAD = "full_load"
    INCREMENTAL = "incremental"
    CDC = "cdc"
    API = "api"
    MANUAL = "manual"


class DataClassification(str, Enum):
    """Data classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RuleSeverity(str, Enum):
    """Business rule severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class StringFormat(str, Enum):
    """String format types."""

    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    CURRENCY = "currency"


class SchemaInfo(BaseModel):
    """Schema versioning and metadata information."""

    schema_version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    metadata_version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: str = Field(..., description="Data owner email or identifier")
    steward: Optional[str] = None
    last_reviewed: Optional[date] = None
    reviewer_comments: Optional[str] = None
    dataset_name: Optional[str] = None
    dataset_description: Optional[str] = None


class Lineage(BaseModel):
    """Data lineage and source information."""

    source_system: Optional[str] = None
    source_table: Optional[str] = None
    extraction_method: Optional[ExtractionMethod] = None
    transformation_notes: Optional[str] = None
    data_classification: Optional[DataClassification] = None


class QualityThresholds(BaseModel):
    """Quality thresholds for alerting."""

    max_missing_percentage: float = Field(0.2, ge=0, le=1)
    max_outlier_percentage: float = Field(0.1, ge=0, le=1)
    min_data_freshness_hours: int = Field(24, ge=1)


class Constraints(BaseModel):
    """Value constraints and validation rules."""

    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = Field(None, ge=0)
    max_length: Optional[int] = Field(None, ge=1)
    allowed_values: Optional[List[Union[str, int, float, bool]]] = None
    pattern: Optional[str] = None
    format: Optional[StringFormat] = None


class ImputerParameters(BaseModel):
    """Parameters for specific imputation methods."""

    n_neighbors: Optional[int] = Field(None, ge=1)
    constant_value: Optional[Union[str, int, float, bool]] = None
    regression_features: Optional[List[str]] = None


class ImputationConfig(BaseModel):
    """Imputation-specific configuration."""

    missing_strategy_hint: Optional[MissingStrategyHint] = None
    default_imputer: Optional[DefaultImputer] = None
    imputer_parameters: Optional[ImputerParameters] = None
    quality_thresholds: Optional[QualityThresholds] = None


class ForeignKey(BaseModel):
    """Foreign key relationship definition."""

    table: str
    column: str


class Relationships(BaseModel):
    """Relationships with other columns."""

    dependent_columns: Optional[List[str]] = None
    influences_columns: Optional[List[str]] = None
    foreign_keys: Optional[List[ForeignKey]] = None


class BusinessRule(BaseModel):
    """Business rule definition."""

    rule_id: str
    expression: str
    description: str
    severity: RuleSeverity = RuleSeverity.WARNING
    active: bool = True


class Transformation(BaseModel):
    """Data transformation record."""

    type: str
    description: str
    applied_at: datetime


class ColumnLineage(BaseModel):
    """Column-specific lineage information."""

    source_column: Optional[str] = None
    transformations: Optional[List[Transformation]] = None


class Governance(BaseModel):
    """Governance and compliance information."""

    pii: bool = False
    sensitive: bool = False
    retention_policy: Optional[str] = None
    compliance_tags: Optional[List[str]] = None


class TopValue(BaseModel):
    """Top value statistics."""

    value: Union[str, int, float, bool]
    count: int = Field(..., ge=0)
    percentage: float = Field(..., ge=0, le=1)


class Statistics(BaseModel):
    """Statistical metadata."""

    last_profiled: Optional[datetime] = None
    distinct_count: Optional[int] = Field(None, ge=0)
    null_count: Optional[int] = Field(None, ge=0)
    null_percentage: Optional[float] = Field(None, ge=0, le=1)
    mean: Optional[float] = None
    median: Optional[float] = None
    std_dev: Optional[float] = Field(None, ge=0)
    min: Optional[float] = None
    max: Optional[float] = None
    top_values: Optional[List[TopValue]] = None


class EnterpriseColumnMetadata(BaseModel):
    """Comprehensive metadata for a single column."""

    name: str = Field(..., pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    display_name: Optional[str] = None
    description: Optional[str] = None
    data_type: DataType
    required: bool
    unique: bool
    constraints: Optional[Constraints] = None
    imputation_config: Optional[ImputationConfig] = None
    relationships: Optional[Relationships] = None
    business_rules: Optional[List[BusinessRule]] = None
    lineage: Optional[ColumnLineage] = None
    governance: Optional[Governance] = None
    statistics: Optional[Statistics] = None
    version: str = Field("1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: Optional[List[str]] = None


class EnterpriseMetadata(BaseModel):
    """Complete enterprise metadata schema."""

    schema_info: SchemaInfo
    lineage: Optional[Lineage] = None
    quality_thresholds: Optional[QualityThresholds] = None
    columns: List[EnterpriseColumnMetadata] = Field(..., min_items=1)

    def get_column(self, name: str) -> Optional[EnterpriseColumnMetadata]:
        """Get column metadata by name."""
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def get_columns_by_tag(self, tag: str) -> List[EnterpriseColumnMetadata]:
        """Get all columns with a specific tag."""
        return [col for col in self.columns if col.tags and tag in col.tags]

    def get_required_columns(self) -> List[EnterpriseColumnMetadata]:
        """Get all required columns."""
        return [col for col in self.columns if col.required]

    def get_unique_columns(self) -> List[EnterpriseColumnMetadata]:
        """Get all unique identifier columns."""
        return [col for col in self.columns if col.unique]

    def get_sensitive_columns(self) -> List[EnterpriseColumnMetadata]:
        """Get all sensitive columns."""
        return [
            col for col in self.columns if col.governance and col.governance.sensitive
        ]

    def get_pii_columns(self) -> List[EnterpriseColumnMetadata]:
        """Get all PII columns."""
        return [col for col in self.columns if col.governance and col.governance.pii]
