"""
JSON Schema validation for enterprise metadata.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Any, List
from pydantic import ValidationError

from .enterprise_models import EnterpriseMetadata, EnterpriseColumnMetadata


class MetadataValidationError(Exception):
    """Raised when metadata validation fails."""

    pass


class SchemaValidator:
    """Validates metadata against JSON Schema and Pydantic models."""

    def __init__(self, schema_path: str = None):
        """
        Initialize validator with schema.

        Args:
            schema_path: Path to JSON schema file. If None, uses bundled schema.
        """
        if schema_path is None:
            # Use bundled schema
            schema_path = (
                Path(__file__).parent.parent
                / "schemas"
                / "imputation_metadata_schema.json"
            )

        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise MetadataValidationError(f"Schema file not found: {self.schema_path}")
        except json.JSONDecodeError as e:
            raise MetadataValidationError(f"Invalid JSON in schema file: {e}")

    def validate_json_schema(self, metadata_dict: Dict[str, Any]) -> List[str]:
        """
        Validate metadata against JSON Schema.

        Args:
            metadata_dict: Metadata dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            jsonschema.validate(metadata_dict, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(
                f"JSON Schema validation failed: {e.message} at path: {'.'.join(str(p) for p in e.absolute_path)}"
            )
        except jsonschema.SchemaError as e:
            errors.append(f"Schema definition error: {e.message}")

        return errors

    def validate_pydantic_model(
        self, metadata_dict: Dict[str, Any]
    ) -> tuple[EnterpriseMetadata, List[str]]:
        """
        Validate metadata using Pydantic models.

        Args:
            metadata_dict: Metadata dictionary to validate

        Returns:
            Tuple of (parsed_metadata, validation_errors)
        """
        errors = []
        metadata = None

        try:
            metadata = EnterpriseMetadata(**metadata_dict)
        except ValidationError as e:
            for error in e.errors():
                field_path = ".".join(str(p) for p in error["loc"])
                errors.append(
                    f"Pydantic validation failed at {field_path}: {error['msg']}"
                )
        except Exception as e:
            errors.append(f"Unexpected validation error: {str(e)}")

        return metadata, errors

    def validate_business_rules(self, metadata: EnterpriseMetadata) -> List[str]:
        """
        Validate business rules syntax and references.

        Args:
            metadata: Parsed metadata object

        Returns:
            List of business rule validation errors
        """
        errors = []
        column_names = {col.name for col in metadata.columns}

        for col in metadata.columns:
            if not col.business_rules:
                continue

            for rule in col.business_rules:
                # Check for SQL injection patterns (basic check)
                dangerous_patterns = [
                    "DROP",
                    "DELETE",
                    "INSERT",
                    "UPDATE",
                    "ALTER",
                    "CREATE",
                ]
                rule_upper = rule.expression.upper()

                for pattern in dangerous_patterns:
                    if pattern in rule_upper:
                        errors.append(
                            f"Column '{col.name}', rule '{rule.rule_id}': Potentially dangerous SQL keyword '{pattern}' found"
                        )

                # Check column references in expressions
                # This is a simple check - in production, you'd use a proper SQL parser
                for other_col in column_names:
                    if other_col in rule.expression and other_col != col.name:
                        # This is expected - rules can reference other columns
                        pass

                # Validate rule ID uniqueness within column
                rule_ids = [r.rule_id for r in col.business_rules]
                if len(rule_ids) != len(set(rule_ids)):
                    errors.append(f"Column '{col.name}': Duplicate rule IDs found")

        return errors

    def validate_metadata_consistency(self, metadata: EnterpriseMetadata) -> List[str]:
        """
        Validate metadata consistency and logical constraints.

        Args:
            metadata: Parsed metadata object

        Returns:
            List of consistency validation errors
        """
        errors = []

        # Check for required unique columns
        unique_cols = metadata.get_unique_columns()
        if not unique_cols:
            errors.append(
                "No unique identifier columns found - at least one is recommended"
            )

        # Check for multiple unique columns (potential issue)
        if len(unique_cols) > 3:
            errors.append(
                f"Many unique columns found ({len(unique_cols)}) - verify this is intentional"
            )

        # Validate imputation configuration consistency
        for col in metadata.columns:
            if col.imputation_config:
                # Required columns shouldn't have missing strategy hints other than MNAR
                if col.required and col.imputation_config.missing_strategy_hint in [
                    "MCAR",
                    "MAR",
                ]:
                    errors.append(
                        f"Column '{col.name}': Required column with MCAR/MAR hint - consider MNAR"
                    )

                # Unique columns should use manual imputation
                if col.unique and col.imputation_config.default_imputer not in [
                    "manual",
                    None,
                ]:
                    errors.append(
                        f"Column '{col.name}': Unique column should use manual imputation"
                    )

                # Categorical columns with regression imputation
                if (
                    col.data_type == "categorical"
                    and col.imputation_config.default_imputer == "regression"
                ):
                    errors.append(
                        f"Column '{col.name}': Categorical column with regression imputation - consider mode or kNN"
                    )

        # Check governance consistency
        pii_cols = metadata.get_pii_columns()
        for col in pii_cols:
            if col.governance.data_classification in ["public", "internal"]:
                errors.append(
                    f"Column '{col.name}': PII column with public/internal classification"
                )

        return errors

    def validate_complete(
        self, metadata_dict: Dict[str, Any]
    ) -> tuple[EnterpriseMetadata, List[str]]:
        """
        Perform complete validation including JSON Schema, Pydantic, and business rules.

        Args:
            metadata_dict: Metadata dictionary to validate

        Returns:
            Tuple of (parsed_metadata, all_validation_errors)
        """
        all_errors = []

        # Step 1: JSON Schema validation
        json_errors = self.validate_json_schema(metadata_dict)
        all_errors.extend(json_errors)

        # Step 2: Pydantic model validation
        metadata, pydantic_errors = self.validate_pydantic_model(metadata_dict)
        all_errors.extend(pydantic_errors)

        # Step 3: Business rules validation (only if Pydantic validation passed)
        if metadata:
            business_errors = self.validate_business_rules(metadata)
            all_errors.extend(business_errors)

            # Step 4: Consistency validation
            consistency_errors = self.validate_metadata_consistency(metadata)
            all_errors.extend(consistency_errors)

        return metadata, all_errors


def validate_metadata_file(
    file_path: str, schema_path: str = None
) -> tuple[EnterpriseMetadata, List[str]]:
    """
    Validate metadata file against enterprise schema.

    Args:
        file_path: Path to metadata JSON file
        schema_path: Optional path to custom schema file

    Returns:
        Tuple of (parsed_metadata, validation_errors)

    Raises:
        MetadataValidationError: If file cannot be loaded
    """
    try:
        with open(file_path, "r") as f:
            metadata_dict = json.load(f)
    except FileNotFoundError:
        raise MetadataValidationError(f"Metadata file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise MetadataValidationError(f"Invalid JSON in metadata file: {e}")

    validator = SchemaValidator(schema_path)
    return validator.validate_complete(metadata_dict)


def convert_legacy_metadata(legacy_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert legacy CSV-based metadata to enterprise format.

    Args:
        legacy_metadata: List of legacy metadata dictionaries

    Returns:
        Enterprise metadata dictionary
    """
    from datetime import datetime

    # Create basic schema info
    enterprise_metadata = {
        "schema_info": {
            "schema_version": "1.0.0",
            "metadata_version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "owner": "system@company.com",
            "dataset_name": "converted_legacy_metadata",
        },
        "columns": [],
    }

    # Convert each column
    for legacy_col in legacy_metadata:
        enterprise_col = {
            "name": legacy_col.get("column_name", "unknown"),
            "data_type": legacy_col.get("data_type", "string"),
            "required": not legacy_col.get("nullable", True),
            "unique": legacy_col.get("unique_flag", False),
            "description": legacy_col.get("description", ""),
            "version": "1.0.0",
        }

        # Add constraints if present
        constraints = {}
        if legacy_col.get("min_value") is not None:
            constraints["min_value"] = legacy_col["min_value"]
        if legacy_col.get("max_value") is not None:
            constraints["max_value"] = legacy_col["max_value"]
        if legacy_col.get("max_length") is not None:
            constraints["max_length"] = legacy_col["max_length"]

        if constraints:
            enterprise_col["constraints"] = constraints

        # Add relationships if present
        relationships = {}
        if legacy_col.get("dependent_column"):
            relationships["dependent_columns"] = [legacy_col["dependent_column"]]

        if relationships:
            enterprise_col["relationships"] = relationships

        # Add business rules if present
        if legacy_col.get("business_rule"):
            enterprise_col["business_rules"] = [
                {
                    "rule_id": f"{enterprise_col['name']}_LEGACY_001",
                    "expression": legacy_col["business_rule"],
                    "description": f"Legacy business rule for {enterprise_col['name']}",
                    "severity": "warning",
                    "active": True,
                }
            ]

        enterprise_metadata["columns"].append(enterprise_col)

    return enterprise_metadata
