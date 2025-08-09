"""
Imputation method proposal with constraint-aware confidence scoring.
Includes adaptive threshold calculation based on data characteristics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from scipy import stats

from .models import (
    ImputationProposal,
    ImputationMethod,
    MissingnessMechanism,
    ColumnMetadata,
    MissingnessAnalysis,
    OutlierAnalysis,
    AnalysisConfig,
)
from .exceptions import apply_exception_handling


class AdaptiveThresholds:
    """Calculate adaptive thresholds based on dataset characteristics."""

    def __init__(
        self,
        data: pd.DataFrame,
        metadata_dict: Dict[str, ColumnMetadata],
        config: AnalysisConfig,
    ):
        """
        Initialize adaptive threshold calculator.

        Args:
            data: Full dataset
            metadata_dict: Dictionary mapping column names to metadata
            config: Base configuration
        """
        self.data = data
        self.metadata_dict = metadata_dict
        self.config = config
        self.data_characteristics = self._analyze_dataset_characteristics()

    def _analyze_dataset_characteristics(self) -> Dict[str, float]:
        """
        Analyze essential dataset characteristics for threshold adaptation.

        Returns:
            Dictionary of dataset characteristics
        """
        total_cells = self.data.shape[0] * self.data.shape[1]
        missing_cells = self.data.isna().sum().sum()
        
        characteristics = {
            "n_rows": len(self.data),
            "n_columns": len(self.data.columns),
            "data_density": 1.0 - (missing_cells / total_cells) if total_cells > 0 else 1.0,
            "avg_missing_rate": missing_cells / total_cells if total_cells > 0 else 0.0,
        }
        
        # Add numeric ratio for type-based adjustments
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        characteristics["numeric_ratio"] = len(numeric_cols) / len(self.data.columns) if len(self.data.columns) > 0 else 0
        
        return characteristics

    def _apply_bounded_adjustment(self, base: float, adjustments: Dict[str, float], 
                                 lower_bound: float, upper_bound: float) -> float:
        """
        Apply adjustments to a base value and bound the result.
        
        Args:
            base: Base value
            adjustments: Dictionary of adjustment values
            lower_bound: Minimum allowed value
            upper_bound: Maximum allowed value
            
        Returns:
            Adjusted and bounded value
        """
        total = base + sum(adjustments.values())
        return max(lower_bound, min(upper_bound, total))

    def get_adaptive_missing_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive missing data threshold for confidence scoring.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive threshold for missing data percentage
        """
        adjustments = {}
        
        # Size-based adjustment
        n_rows = self.data_characteristics["n_rows"]
        if n_rows < 100:
            adjustments["size"] = 0.02  # Small datasets - be more lenient
        elif n_rows > 10000:
            adjustments["size"] = -0.01  # Large datasets - can be more strict
            
        # Data quality adjustment
        density = self.data_characteristics["data_density"]
        if density < 0.8:
            adjustments["density"] = 0.03  # Low density - be more lenient
        elif density > 0.95:
            adjustments["density"] = -0.01  # High density - be stricter
            
        # Column importance adjustment
        metadata = self.metadata_dict.get(column_name)
        if metadata:
            if metadata.unique_flag:
                adjustments["importance"] = -0.02  # Stricter for unique columns
            elif getattr(metadata, 'business_rule', None):
                adjustments["importance"] = -0.01  # Stricter for business rule columns
        
        return self._apply_bounded_adjustment(0.05, adjustments, 0.01, 0.15)

    def get_adaptive_confidence_adjustment(
        self, column_name: str, missing_pct: float
    ) -> float:
        """
        Calculate adaptive confidence adjustment based on data characteristics.

        Args:
            column_name: Name of the column
            missing_pct: Missing percentage for the column

        Returns:
            Confidence adjustment factor (-0.3 to +0.3)
        """
        adjustments = {}
        
        # Sample size adjustment
        if column_name in self.data.columns:
            non_missing_count = len(self.data[column_name].dropna())
            if non_missing_count > 1000:
                adjustments["sample_size"] = 0.1
            elif non_missing_count < 50:
                adjustments["sample_size"] = -0.15
            elif non_missing_count < 20:
                adjustments["sample_size"] = -0.25
                
        # Data quality context adjustment
        density = self.data_characteristics["data_density"]
        if density > 0.95:
            adjustments["quality"] = 0.05
        elif density < 0.7:
            adjustments["quality"] = -0.1
            
        # Business context adjustment
        metadata = self.metadata_dict.get(column_name)
        if metadata:
            if metadata.unique_flag:
                adjustments["business"] = -0.1
            elif getattr(metadata, 'business_rule', None) and metadata.dependent_column:
                adjustments["business"] = 0.1
        
        return self._apply_bounded_adjustment(0.0, adjustments, -0.3, 0.3)

    def get_adaptive_skewness_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive skewness threshold for mean vs median decision.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive skewness threshold
        """
        base_threshold = self.config.skewness_threshold  # Default 2.0
        
        if column_name in self.data.columns:
            non_null_count = len(self.data[column_name].dropna())
            if non_null_count < 30:
                return base_threshold * 0.7  # Small samples - use median more often
            elif non_null_count > 1000:
                return base_threshold * 1.2  # Large samples - can be less conservative
                
        return base_threshold

    def get_adaptive_outlier_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive outlier percentage threshold.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive outlier threshold
        """
        base_threshold = self.config.outlier_threshold  # Default 0.05
        
        metadata = self.metadata_dict.get(column_name)
        if metadata:
            if metadata.min_value is not None or metadata.max_value is not None:
                return base_threshold * 0.8  # Defined ranges - be more strict
            elif metadata.unique_flag:
                return base_threshold * 0.6  # Unique columns - outliers more problematic
                
        return base_threshold

    def get_adaptive_correlation_threshold(self, column_name: str) -> float:
        """
        Calculate adaptive correlation threshold for relationship detection.

        Args:
            column_name: Name of the column

        Returns:
            Adaptive correlation threshold
        """
        base_threshold = self.config.correlation_threshold  # Default 0.3
        adjustments = {}
        
        # Dataset size adjustment
        n_rows = self.data_characteristics["n_rows"]
        if n_rows < 100:
            adjustments["size"] = base_threshold * 0.3  # Need stronger correlations
        elif n_rows > 5000:
            adjustments["size"] = base_threshold * -0.2  # Weaker correlations meaningful
            
        # Column count adjustment
        n_cols = self.data_characteristics["n_columns"]
        if n_cols > 20:
            adjustments["columns"] = base_threshold * 0.1  # Be more selective
        elif n_cols < 5:
            adjustments["columns"] = base_threshold * -0.1  # Be more inclusive
        
        return self._apply_bounded_adjustment(base_threshold, adjustments, 
                                            base_threshold * 0.5, base_threshold * 1.5)


def calculate_adaptive_confidence_score(
    column_name: str,
    missingness_analysis,
    outlier_analysis,
    metadata: ColumnMetadata,
    data_series: pd.Series,
    adaptive_thresholds: AdaptiveThresholds,
) -> float:
    """
    Calculate confidence score using adaptive thresholds.

    Args:
        column_name: Name of the column
        missingness_analysis: Results of missingness mechanism analysis
        outlier_analysis: Results of outlier analysis
        metadata: Column metadata
        data_series: The actual data series
        adaptive_thresholds: Adaptive threshold calculator

    Returns:
        Confidence score between 0 and 1
    """
    confidence = 0.5  # Base confidence
    
    # Missing data adjustment using adaptive threshold
    missing_threshold = adaptive_thresholds.get_adaptive_missing_threshold(column_name)
    missing_pct = missingness_analysis.missing_percentage
    
    if missing_pct < missing_threshold:
        confidence += 0.2
    elif missing_pct < missing_threshold * 2:
        confidence += 0.1
    elif missing_pct > 0.50:
        confidence -= 0.2
        
    # Apply adaptive confidence adjustment
    confidence += adaptive_thresholds.get_adaptive_confidence_adjustment(
        column_name, missing_pct
    )
    
    # Mechanism-based adjustment
    if missingness_analysis.mechanism == MissingnessMechanism.MCAR:
        if missingness_analysis.p_value is None or missingness_analysis.p_value > 0.1:
            confidence += 0.1
    elif missingness_analysis.mechanism == MissingnessMechanism.MAR:
        if missingness_analysis.p_value and missingness_analysis.p_value < 0.01:
            confidence += 0.15
            
    # Outlier adjustment using adaptive threshold
    outlier_threshold = adaptive_thresholds.get_adaptive_outlier_threshold(column_name)
    if outlier_analysis.outlier_percentage < outlier_threshold:
        confidence += 0.05
    elif outlier_analysis.outlier_percentage > outlier_threshold * 4:
        confidence -= 0.1
        
    # Metadata completeness adjustment
    if getattr(metadata, 'business_rule', None):
        confidence += 0.05
    if metadata.dependent_column:
        confidence += 0.05
        
    # Ensure confidence is within bounds
    return max(0.1, min(1.0, confidence))


# Confidence scoring factors and weights
CONFIDENCE_WEIGHTS = {
    'base': 0.5,
    'missing_low': 0.2,    # < 5% missing
    'missing_med': 0.1,    # < 20% missing  
    'missing_high': -0.2,  # > 50% missing
    'mcar_certain': 0.1,
    'mar_evidence': 0.05,
    'mechanism_unknown': -0.1,
    'outliers_low': 0.05,   # < 5% outliers
    'outliers_high': -0.1,  # > 20% outliers
    'has_constraints': 0.1,
    'constraint_compliance': 0.05,
    'non_nullable_violation': -0.15
}

def calculate_confidence_score(
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    metadata: ColumnMetadata,
    data_series: pd.Series,
) -> float:
    """Calculate constraint-aware confidence score for imputation proposals."""
    confidence = CONFIDENCE_WEIGHTS['base']
    
    # Missing data impact
    missing_pct = missingness_analysis.missing_percentage
    if missing_pct < 0.05:
        confidence += CONFIDENCE_WEIGHTS['missing_low']
    elif missing_pct < 0.20:
        confidence += CONFIDENCE_WEIGHTS['missing_med'] 
    elif missing_pct > 0.50:
        confidence += CONFIDENCE_WEIGHTS['missing_high']
    
    # Mechanism certainty
    if missingness_analysis.mechanism == MissingnessMechanism.MCAR:
        if not missingness_analysis.p_value or missingness_analysis.p_value > 0.1:
            confidence += CONFIDENCE_WEIGHTS['mcar_certain']
    elif missingness_analysis.mechanism == MissingnessMechanism.MAR:
        if missingness_analysis.related_columns:
            confidence += CONFIDENCE_WEIGHTS['mar_evidence']
    else:
        confidence += CONFIDENCE_WEIGHTS['mechanism_unknown']
    
    # Outlier impact
    if outlier_analysis.outlier_percentage < 0.05:
        confidence += CONFIDENCE_WEIGHTS['outliers_low']
    elif outlier_analysis.outlier_percentage > 0.20:
        confidence += CONFIDENCE_WEIGHTS['outliers_high']
    
    # Constraint awareness
    confidence += _calculate_constraint_impact(metadata, data_series, missingness_analysis.missing_count)
    
    return max(0.1, min(1.0, confidence))


def _propose_categorical_method(data_series, metadata, mechanism, missingness_analysis, get_confidence_score):
    """Propose imputation method for categorical data."""
    allowed_values = _get_allowed_values_list(metadata)
    
    if allowed_values:
        return _propose_constrained_categorical(data_series, metadata, mechanism, allowed_values, get_confidence_score)
    else:
        return _propose_unconstrained_categorical(data_series, mechanism, missingness_analysis, get_confidence_score)


def _propose_constrained_categorical(data_series, metadata, mechanism, allowed_values, get_confidence_score):
    """Propose method for categorical data with allowed_values constraints."""
    if mechanism == MissingnessMechanism.MCAR:
        valid_data = data_series.dropna()
        if len(valid_data) > 0:
            valid_data = valid_data[valid_data.astype(str).isin(allowed_values)]
            most_frequent = valid_data.mode().iloc[0] if len(valid_data.mode()) > 0 else allowed_values[0]
        else:
            most_frequent = allowed_values[0]
        
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale=f"Categorical MCAR with {len(allowed_values)} allowed values - use most frequent",
            parameters={"strategy": "most_frequent", "allowed_values": allowed_values, "fill_value": most_frequent},
            confidence_score=get_confidence_score()
        )
    else:
        return ImputationProposal(
            method=ImputationMethod.KNN,
            rationale=f"Categorical MAR with {len(allowed_values)} allowed values - use constrained kNN",
            parameters={
                "n_neighbors": min(5, max(3, data_series.count() // 20)),
                "weights": "distance",
                "allowed_values": allowed_values
            },
            confidence_score=get_confidence_score()
        )


def _propose_unconstrained_categorical(data_series, mechanism, missingness_analysis, get_confidence_score):
    """Propose method for categorical data without constraints."""
    if mechanism == MissingnessMechanism.MCAR:
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Categorical MCAR - use most frequent category",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score()
        )
    else:
        related = ', '.join(missingness_analysis.related_columns[:2]) if missingness_analysis.related_columns else 'unknown'
        return ImputationProposal(
            method=ImputationMethod.KNN,
            rationale=f"Categorical MAR (related to {related}) - use kNN",
            parameters={
                "n_neighbors": min(5, max(3, data_series.count() // 20)),
                "weights": "distance"
            },
            confidence_score=get_confidence_score()
        )


def _propose_string_method(data_series, metadata, mechanism, get_confidence_score):
    """Propose imputation method for string data."""
    base_params = {"strategy": "most_frequent"} if mechanism == MissingnessMechanism.MCAR else {
        "n_neighbors": min(5, max(3, data_series.count() // 20)),
        "weights": "distance"
    }
    
    if metadata.max_length:
        base_params["max_length"] = metadata.max_length
        constraint_info = f" and max_length={metadata.max_length}"
    else:
        constraint_info = ""
    
    method = ImputationMethod.MODE if mechanism == MissingnessMechanism.MCAR else ImputationMethod.KNN
    mech_name = "MCAR" if mechanism == MissingnessMechanism.MCAR else "MAR"
    
    return ImputationProposal(
        method=method,
        rationale=f"String data with {mech_name}{constraint_info} - use {'mode' if method == ImputationMethod.MODE else 'kNN'}",
        parameters=base_params,
        confidence_score=get_confidence_score()
    )


def _propose_numeric_method(data_series, metadata, mechanism, missingness_analysis, adaptive_thresholds, config, column_name, get_confidence_score):
    """Propose imputation method for numeric data."""
    non_null_data = data_series.dropna()
    skewness = abs(stats.skew(non_null_data)) if len(non_null_data) > 3 else 0
    
    skewness_threshold = (
        adaptive_thresholds.get_adaptive_skewness_threshold(column_name)
        if adaptive_thresholds else config.skewness_threshold
    )
    
    if mechanism == MissingnessMechanism.MCAR:
        if skewness > skewness_threshold:
            return ImputationProposal(
                method=ImputationMethod.MEDIAN,
                rationale=f"Numeric MCAR with high skewness ({skewness:.2f}) - use median",
                parameters={"strategy": "median"},
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.MEAN,
                rationale=f"Numeric MCAR with low skewness ({skewness:.2f}) - use mean",
                parameters={"strategy": "mean"},
                confidence_score=get_confidence_score()
            )
    else:
        # MAR mechanism
        if len(non_null_data) > 50 and missingness_analysis.related_columns:
            return ImputationProposal(
                method=ImputationMethod.REGRESSION,
                rationale=f"Numeric MAR - use regression with predictors: {', '.join(missingness_analysis.related_columns[:2])}",
                parameters={
                    "predictors": missingness_analysis.related_columns[:3],
                    "estimator": "BayesianRidge"
                },
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.KNN,
                rationale="Numeric MAR - use kNN (insufficient data for regression)",
                parameters={
                    "n_neighbors": min(5, max(3, len(non_null_data) // 10)),
                    "weights": "distance"
                },
                confidence_score=get_confidence_score()
            )


def _propose_simple_method(data_type, mechanism, get_confidence_score):
    """Propose method for simple data types (datetime, boolean) and fallback."""
    if data_type == "datetime":
        if mechanism == MissingnessMechanism.MCAR:
            return ImputationProposal(
                method=ImputationMethod.FORWARD_FILL,
                rationale="Datetime MCAR - forward fill for temporal continuity",
                parameters={"method": "ffill", "limit": 3},
                confidence_score=get_confidence_score()
            )
        else:
            return ImputationProposal(
                method=ImputationMethod.BUSINESS_RULE,
                rationale="Datetime MAR - requires business logic",
                parameters={"strategy": "business_logic_required"},
                confidence_score=get_confidence_score()
            )
    elif data_type == "boolean":
        return ImputationProposal(
            method=ImputationMethod.MODE,
            rationale="Boolean data - use most frequent value",
            parameters={"strategy": "most_frequent"},
            confidence_score=get_confidence_score()
        )
    else:
        # Unknown data type fallback
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Unknown data type ({data_type}) - safe fallback",
            parameters={"fill_value": "Missing"},
            confidence_score=0.3
        )


def _calculate_constraint_impact(metadata: ColumnMetadata, data_series: pd.Series, missing_count: int) -> float:
    """Calculate confidence impact from metadata constraints."""
    impact = 0.0
    
    # Constraint availability bonus
    if metadata.allowed_values and str(metadata.allowed_values).strip():
        if metadata.data_type in ["categorical", "string"]:
            impact += CONFIDENCE_WEIGHTS['has_constraints']
    
    if metadata.max_length and metadata.data_type in ["string", "categorical"]:
        impact += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Nullable constraint check
    if not metadata.nullable:
        if missing_count > 0:
            impact += CONFIDENCE_WEIGHTS['non_nullable_violation']
        else:
            impact += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Data quality compliance
    non_null_data = data_series.dropna()
    if len(non_null_data) > 0:
        impact += _check_data_compliance(metadata, non_null_data)
    
    return impact


def _check_data_compliance(metadata: ColumnMetadata, non_null_data: pd.Series) -> float:
    """Check how well data complies with metadata constraints."""
    compliance_bonus = 0.0
    
    # Max length compliance
    if metadata.data_type in ["string", "categorical"] and metadata.max_length:
        max_actual_length = non_null_data.astype(str).str.len().max()
        if max_actual_length <= metadata.max_length:
            compliance_bonus += CONFIDENCE_WEIGHTS['constraint_compliance']
    
    # Allowed values compliance
    if metadata.data_type in ["categorical", "string"] and metadata.allowed_values:
        allowed_values = [v.strip() for v in str(metadata.allowed_values).split(",") if v.strip()]
        if allowed_values:
            valid_ratio = non_null_data.astype(str).isin(allowed_values).mean()
            compliance_bonus += valid_ratio * 0.1
    
    return compliance_bonus


def _get_allowed_values_list(metadata: ColumnMetadata) -> list:
    """Parse allowed_values string into a list of valid values."""
    if not metadata.allowed_values:
        return []

    # Split by comma and clean up
    values = [v.strip() for v in str(metadata.allowed_values).split(",")]
    return [v for v in values if v]




def propose_imputation_method(
    column_name: str,
    data_series: pd.Series,
    metadata: ColumnMetadata,
    missingness_analysis: MissingnessAnalysis,
    outlier_analysis: OutlierAnalysis,
    config: AnalysisConfig,
    full_data: pd.DataFrame = None,
    metadata_dict: Dict[str, ColumnMetadata] = None,
) -> ImputationProposal:
    """
    Propose the best imputation method based on comprehensive analysis.

    Args:
        column_name: Name of the column
        data_series: The data series to analyze
        metadata: Column metadata
        missingness_analysis: Results of missingness analysis
        outlier_analysis: Results of outlier analysis
        config: Analysis configuration
        full_data: Full dataset for adaptive threshold calculation
        metadata_dict: Dictionary of all column metadata for adaptive thresholds

    Returns:
        ImputationProposal with method, rationale, and parameters
    """
    # FIRST: Apply exception handling rules
    exception_proposal = apply_exception_handling(
        column_name,
        data_series,
        metadata,
        missingness_analysis,
        outlier_analysis,
        config,
    )

    if exception_proposal is not None:
        return exception_proposal

    # Initialize adaptive thresholds if data is available
    adaptive_thresholds = None
    if full_data is not None and metadata_dict is not None:
        adaptive_thresholds = AdaptiveThresholds(full_data, metadata_dict, config)

    # Helper function to calculate confidence score
    def get_confidence_score():
        if adaptive_thresholds is not None:
            return calculate_adaptive_confidence_score(
                column_name,
                missingness_analysis,
                outlier_analysis,
                metadata,
                data_series,
                adaptive_thresholds,
            )
        else:
            return calculate_confidence_score(
                missingness_analysis, outlier_analysis, metadata, data_series
            )

    # If no exceptions apply, proceed with normal imputation logic
    missing_pct = missingness_analysis.missing_percentage
    mechanism = missingness_analysis.mechanism

    # Handle unique identifier columns (backup check)
    if metadata.unique_flag:
        return ImputationProposal(
            method=ImputationMethod.MANUAL_BACKFILL,
            rationale="Unique identifier column requires manual backfill to maintain data integrity",
            parameters={"strategy": "manual_review"},
            confidence_score=get_confidence_score(),
        )

    # Handle dependency rule columns (specific calculations)
    dependency_rule = getattr(metadata, 'dependency_rule', None)
    if dependency_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has dependency rule on {metadata.dependent_column}: {dependency_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": dependency_rule,
                "rule_type": "dependency",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle business rule columns (general constraints)
    business_rule = getattr(metadata, 'business_rule', None)
    if business_rule and metadata.dependent_column:
        return ImputationProposal(
            method=ImputationMethod.BUSINESS_RULE,
            rationale=f"Column has business rule dependency on {metadata.dependent_column}: {business_rule}",
            parameters={
                "dependent_column": metadata.dependent_column,
                "rule": business_rule,
                "rule_type": "business",
            },
            confidence_score=get_confidence_score(),
        )

    # Handle high missing percentage (>80%)
    if missing_pct > config.missing_threshold:
        return ImputationProposal(
            method=ImputationMethod.CONSTANT_MISSING,
            rationale=f"Very high missing percentage ({missing_pct:.1%}) suggests systematic absence - use constant 'Missing'",
            parameters={"fill_value": "Missing"},
            confidence_score=get_confidence_score(),
        )

    # Method selection by data type and mechanism
    if metadata.data_type == "categorical":
        return _propose_categorical_method(data_series, metadata, mechanism, missingness_analysis, get_confidence_score)

    elif metadata.data_type == "string":
        return _propose_string_method(data_series, metadata, mechanism, get_confidence_score)

    elif metadata.data_type in ["integer", "float"]:
        return _propose_numeric_method(
            data_series, metadata, mechanism, missingness_analysis, 
            adaptive_thresholds, config, column_name, get_confidence_score
        )

    else:
        return _propose_simple_method(metadata.data_type, mechanism, get_confidence_score)


# Backward compatibility function for tests
def _adjust_confidence_for_constraints(base_confidence: float, metadata: ColumnMetadata, data: pd.Series) -> float:
    """Legacy function for constraint-based confidence adjustment."""
    return _calculate_constraint_compliance(metadata, data)
