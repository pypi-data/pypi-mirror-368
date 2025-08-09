"""
Central definition of metadata field structure to ensure consistency across the package.

This module defines the complete metadata schema including both inferrable fields
(automatically detected from data) and non-inferrable fields (requiring manual input).
"""

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

# Legacy field order (for backward compatibility)
LEGACY_FIELD_ORDER = [
    'column_name', 'data_type', 'min_value', 'max_value', 'max_length',
    'unique_flag', 'nullable', 'allowed_values', 'dependent_column',
    'dependency_rule', 'business_rule', 'description'
]

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