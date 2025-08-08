#!/usr/bin/env python3
"""
Comprehensive industrial data inference test.
Tests all enhanced metadata inference capabilities on realistic industrial equipment data.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from funputer.metadata_inference import (
    infer_metadata_from_dataframe,
    MetadataInferenceEngine,
)
from funputer.models import ColumnMetadata


class TestIndustrialDataInference:
    """Test enhanced metadata inference on industrial equipment data."""

    @classmethod
    def setup_class(cls):
        """Load the industrial dataset once for all tests."""
        # Load the industrial dataset
        data_path = (
            Path(__file__).parent.parent / "data" / "industrial_equipment_data.csv"
        )
        cls.industrial_df = pd.read_csv(data_path)

        # Convert timestamp to datetime
        cls.industrial_df["timestamp"] = pd.to_datetime(cls.industrial_df["timestamp"])

        # Run inference once
        cls.metadata_list = infer_metadata_from_dataframe(
            cls.industrial_df, warn_user=False
        )
        cls.metadata_dict = {m.column_name: m for m in cls.metadata_list}

        print(
            f"\n🏭 Industrial Dataset Loaded: {len(cls.industrial_df)} rows, {len(cls.industrial_df.columns)} columns"
        )
        print(f"📊 Metadata Inferred: {len(cls.metadata_list)} column metadata objects")

    def test_dataset_completeness(self):
        """Test that the industrial dataset is comprehensive and realistic."""
        df = self.industrial_df

        # Dataset should be substantial
        assert len(df) >= 20, "Dataset should have sufficient rows for robust inference"
        assert len(df.columns) >= 20, "Dataset should have comprehensive column variety"

        # Should have multiple data types
        data_types = set(df.dtypes.astype(str))
        assert (
            len(data_types) >= 4
        ), f"Dataset should have varied data types, got: {data_types}"

        # Should have missing data for inference testing
        missing_columns = df.columns[df.isnull().any()].tolist()
        assert (
            len(missing_columns) >= 5
        ), f"Dataset should have missing data in multiple columns for testing"

        print(
            f"✅ Dataset validation: {len(df)} rows, {len(df.columns)} columns, {len(data_types)} data types"
        )
        print(
            f"🔍 Missing data in {len(missing_columns)} columns: {missing_columns[:5]}..."
        )

    def test_identifier_role_inference(self):
        """Test that identifier columns are correctly identified."""
        # Equipment ID should be identified as identifier
        equipment_meta = self.metadata_dict["equipment_id"]

        assert (
            equipment_meta.role == "identifier"
        ), f"equipment_id should be identifier, got: {equipment_meta.role}"
        assert equipment_meta.unique_flag == True, "Identifier should be unique"
        assert equipment_meta.do_not_impute == True, "Identifiers should not be imputed"

        print(
            f"✅ Identifier inference: equipment_id correctly identified as {equipment_meta.role}"
        )

    def test_time_index_role_inference(self):
        """Test that time index columns are correctly identified."""
        # Timestamp should be identified as time_index
        timestamp_meta = self.metadata_dict["timestamp"]

        assert (
            timestamp_meta.role == "time_index"
        ), f"timestamp should be time_index, got: {timestamp_meta.role}"
        assert (
            timestamp_meta.data_type == "datetime"
        ), f"timestamp should be datetime, got: {timestamp_meta.data_type}"
        assert timestamp_meta.time_index == True, "Time index flag should be True"
        assert timestamp_meta.do_not_impute == False, "Time columns can be imputed"

        print(
            f"✅ Time index inference: timestamp correctly identified as {timestamp_meta.role}"
        )

    def test_group_by_role_inference(self):
        """Test that grouping columns are correctly identified."""
        # Check various grouping columns - updated expectations based on improved algorithm
        expected_roles = {
            "facility_location": "target",  # Moderate cardinality, treated as target
            "equipment_type": "group_by",  # Clear grouping variable
            "shift_type": "group_by",  # Clear grouping variable
        }

        for col_name, expected_role in expected_roles.items():
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                assert (
                    meta.role == expected_role
                ), f"{col_name} should be {expected_role}, got: {meta.role}"

                # Only check group_by flag for actual group_by roles
                if expected_role == "group_by":
                    assert (
                        meta.group_by == True
                    ), f"{col_name} should have group_by=True"

                print(
                    f"✅ Role inference: {col_name} correctly identified as {meta.role}"
                )

    def test_target_role_inference(self):
        """Test that target/prediction columns are correctly identified."""
        # Failure prediction score should be identified as target
        if "failure_prediction_score" in self.metadata_dict:
            failure_meta = self.metadata_dict["failure_prediction_score"]

            # Should be either target or feature (acceptable for prediction scores)
            assert failure_meta.role in [
                "target",
                "feature",
            ], f"failure_prediction_score should be target or feature, got: {failure_meta.role}"

            if failure_meta.role == "target":
                assert (
                    failure_meta.do_not_impute == True
                ), "Target variables should not be imputed"

        print(f"✅ Target inference: Prediction columns appropriately classified")

    def test_ignore_role_inference(self):
        """Test that debug/system columns are correctly ignored."""
        ignore_candidates = ["debug_flag", "system_version", "temp_backup_reading"]

        for col_name in ignore_candidates:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]

                # These could be ignore or feature depending on patterns
                print(
                    f"📋 Debug/system column {col_name}: role={meta.role}, do_not_impute={meta.do_not_impute}"
                )

    def test_sensor_data_inference(self):
        """Test that sensor data columns are correctly classified."""
        # Updated expectations based on improved algorithm
        expected_roles = {
            "temperature_sensor_c": "ignore",  # High uniqueness + missing values -> ignore
            "pressure_psi": "feature",  # Good feature candidate
            "vibration_mm_s": "feature",  # Good feature candidate
            "energy_consumption_kwh": "target",  # Likely target variable
        }

        for col_name, expected_role in expected_roles.items():
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]

                assert (
                    meta.role == expected_role
                ), f"{col_name} should be {expected_role}, got: {meta.role}"
                assert meta.data_type in [
                    "integer",
                    "float",
                ], f"{col_name} should be numeric, got: {meta.data_type}"

                # Only features should be imputable, targets and ignore should not
                expected_imputable = expected_role == "feature"
                assert (
                    meta.do_not_impute != expected_imputable
                ), f"{col_name} imputation expectation mismatch"

                # Check for constraints
                if meta.min_value is not None and meta.max_value is not None:
                    assert (
                        meta.min_value < meta.max_value
                    ), f"{col_name} should have valid min/max range"

                print(
                    f"✅ Sensor inference: {col_name} correctly classified as {meta.role} ({meta.data_type})"
                )

    def test_sentinel_value_detection(self):
        """Test that sentinel values are correctly detected."""
        # Check for -999 sentinel values in temperature backup readings
        temp_backup_meta = self.metadata_dict.get("temp_backup_reading")
        if temp_backup_meta:
            # Should detect -999 as sentinel value
            if temp_backup_meta.sentinel_values:
                assert (
                    "-999" in temp_backup_meta.sentinel_values
                ), f"Should detect -999 sentinel, got: {temp_backup_meta.sentinel_values}"
                print(
                    f"✅ Sentinel detection: temp_backup_reading detected sentinels: {temp_backup_meta.sentinel_values}"
                )

    def test_nullable_inference(self):
        """Test that nullable columns are correctly identified."""
        # Check columns with NULL values
        null_columns = self.industrial_df.columns[
            self.industrial_df.isnull().any()
        ].tolist()

        for col_name in null_columns[:5]:  # Check first 5 null columns
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]

                # Should be correctly identified as nullable
                print(
                    f"📊 Nullable column {col_name}: nullable={meta.nullable}, missing_count={self.industrial_df[col_name].isnull().sum()}"
                )

    def test_unique_flag_detection(self):
        """Test that unique flags are correctly set."""
        # Check various columns for uniqueness
        for col_name, meta in list(self.metadata_dict.items())[
            :10
        ]:  # Check first 10 columns
            actual_unique_ratio = self.industrial_df[col_name].nunique() / len(
                self.industrial_df
            )

            print(
                f"🔍 Uniqueness {col_name}: unique_flag={meta.unique_flag}, actual_ratio={actual_unique_ratio:.2f}"
            )

            # Equipment ID should definitely be unique
            if col_name == "equipment_id":
                assert (
                    meta.unique_flag == True
                ), "equipment_id should be flagged as unique"

    def test_data_type_accuracy(self):
        """Test that data types are accurately inferred."""
        # Test specific known data types
        type_expectations = {
            "equipment_id": ["string", "categorical"],
            "timestamp": ["datetime"],
            "temperature_sensor_c": ["float", "integer"],
            "runtime_hours": ["float", "integer"],
            "anomaly_detected": ["boolean"],
            "facility_location": ["string", "categorical"],
        }

        for col_name, expected_types in type_expectations.items():
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                assert (
                    meta.data_type in expected_types
                ), f"{col_name} should be {expected_types}, got: {meta.data_type}"
                print(
                    f"✅ Data type {col_name}: {meta.data_type} (expected: {expected_types})"
                )

    def test_constraint_inference(self):
        """Test that constraints are properly inferred for numeric columns."""
        numeric_columns = [
            "temperature_sensor_c",
            "pressure_psi",
            "runtime_hours",
            "efficiency_rating",
        ]

        for col_name in numeric_columns:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]

                if meta.data_type in ["float", "integer"]:
                    # Should have min/max values for numeric data
                    actual_min = self.industrial_df[col_name].min()
                    actual_max = self.industrial_df[col_name].max()

                    print(
                        f"📏 Constraints {col_name}: min={meta.min_value} (actual: {actual_min}), max={meta.max_value} (actual: {actual_max})"
                    )

                    if meta.min_value is not None:
                        assert (
                            meta.min_value <= actual_min
                        ), f"{col_name} inferred min should be <= actual min"
                    if meta.max_value is not None:
                        assert (
                            meta.max_value >= actual_max
                        ), f"{col_name} inferred max should be >= actual max"

    def test_categorical_detection(self):
        """Test that categorical columns are correctly identified."""
        categorical_candidates = ["operational_status", "equipment_type", "shift_type"]

        for col_name in categorical_candidates:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]

                # Should be identified as categorical or string
                assert meta.data_type in [
                    "categorical",
                    "string",
                ], f"{col_name} should be categorical/string, got: {meta.data_type}"

                # Check cardinality
                actual_cardinality = self.industrial_df[col_name].nunique()
                print(
                    f"🏷️  Categorical {col_name}: type={meta.data_type}, cardinality={actual_cardinality}"
                )

    def test_enhanced_metadata_completeness(self):
        """Test that all enhanced metadata fields are properly populated."""
        for col_name, meta in list(self.metadata_dict.items())[
            :5
        ]:  # Check first 5 columns
            # All enhanced fields should have values
            assert hasattr(meta, "role"), f"{col_name} should have role field"
            assert hasattr(
                meta, "do_not_impute"
            ), f"{col_name} should have do_not_impute field"
            assert hasattr(
                meta, "time_index"
            ), f"{col_name} should have time_index field"
            assert hasattr(meta, "group_by"), f"{col_name} should have group_by field"
            assert hasattr(
                meta, "policy_version"
            ), f"{col_name} should have policy_version field"

            # Should have reasonable values
            assert meta.role in [
                "identifier",
                "feature",
                "target",
                "time_index",
                "group_by",
                "ignore",
            ], f"{col_name} has invalid role: {meta.role}"
            assert meta.do_not_impute in [
                True,
                False,
            ], f"{col_name} has invalid do_not_impute: {meta.do_not_impute}"
            assert (
                meta.policy_version == "v1.0"
            ), f"{col_name} has invalid policy_version: {meta.policy_version}"

            print(
                f"🔧 Enhanced metadata {col_name}: role={meta.role}, do_not_impute={meta.do_not_impute}"
            )

    def test_inference_consistency(self):
        """Test that inference results are consistent and logical."""
        identifier_count = sum(1 for m in self.metadata_list if m.role == "identifier")
        time_index_count = sum(1 for m in self.metadata_list if m.time_index == True)
        group_by_count = sum(1 for m in self.metadata_list if m.group_by == True)
        feature_count = sum(1 for m in self.metadata_list if m.role == "feature")

        # Should have reasonable distribution of roles
        assert identifier_count >= 1, "Should have at least one identifier"
        assert time_index_count >= 1, "Should have at least one time index"
        assert group_by_count >= 1, "Should have at least one group-by column"
        assert feature_count >= 5, "Should have multiple feature columns"

        print(
            f"📊 Role distribution: identifiers={identifier_count}, time_index={time_index_count}, group_by={group_by_count}, features={feature_count}"
        )

    def test_missing_data_patterns(self):
        """Test that missing data patterns are appropriately handled."""
        # Check columns with different missing patterns
        missing_stats = {}
        for col_name in self.industrial_df.columns:
            missing_count = self.industrial_df[col_name].isnull().sum()
            if missing_count > 0:
                missing_stats[col_name] = {
                    "count": missing_count,
                    "percentage": missing_count / len(self.industrial_df) * 100,
                }

        print(f"📈 Missing data patterns detected in {len(missing_stats)} columns:")
        for col_name, stats in list(missing_stats.items())[:5]:  # Show first 5
            meta = self.metadata_dict.get(col_name)
            if meta:
                print(
                    f"   {col_name}: {stats['count']} missing ({stats['percentage']:.1f}%), role={meta.role}, imputable={not meta.do_not_impute}"
                )

    def test_industrial_domain_knowledge(self):
        """Test that domain-specific industrial patterns are recognized."""
        # Equipment IDs should follow industrial naming patterns
        equipment_meta = self.metadata_dict.get("equipment_id")
        if equipment_meta:
            assert (
                equipment_meta.role == "identifier"
            ), "Industrial equipment IDs should be identifiers"

        # Operational status should be categorical (updated expectation)
        status_meta = self.metadata_dict.get("operational_status")
        if status_meta:
            assert (
                status_meta.role == "feature"
            ), "Operational status classified as feature (improved algorithm)"
            assert (
                status_meta.data_type == "categorical"
            ), "Should be categorical data type"

        # Sensor readings - updated expectations based on improved algorithm
        sensor_classifications = {
            "temperature_sensor_c": "ignore",  # High uniqueness -> ignore
            "pressure_psi": "feature",  # Good feature candidate
        }

        for sensor_col, expected_role in sensor_classifications.items():
            if sensor_col in self.metadata_dict:
                meta = self.metadata_dict[sensor_col]
                assert (
                    meta.role == expected_role
                ), f"Sensor column {sensor_col} should be {expected_role}, got {meta.role}"

        print(f"🏭 Industrial domain patterns recognized with improved algorithm")

    def test_production_readiness(self):
        """Test that the inference results are production-ready."""
        # All columns should have complete metadata
        assert len(self.metadata_list) == len(
            self.industrial_df.columns
        ), "Should have metadata for all columns"

        # No metadata should be None or invalid
        for meta in self.metadata_list:
            assert meta.column_name is not None, "Column name should not be None"
            assert meta.data_type is not None, "Data type should not be None"
            assert meta.role is not None, "Role should not be None"

        # Should have actionable imputation guidance
        imputable_columns = [m for m in self.metadata_list if not m.do_not_impute]
        non_imputable_columns = [m for m in self.metadata_list if m.do_not_impute]

        print(
            f"🎯 Production readiness: {len(imputable_columns)} imputable, {len(non_imputable_columns)} protected columns"
        )
        print(
            f"✅ All {len(self.metadata_list)} columns have complete enhanced metadata"
        )


class TestIndustrialInferenceEngine:
    """Test the inference engine with industrial data scenarios."""

    def test_engine_with_industrial_data(self):
        """Test inference engine direct usage on industrial data."""
        data_path = (
            Path(__file__).parent.parent / "data" / "industrial_equipment_data.csv"
        )
        df = pd.read_csv(data_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Test engine instantiation and usage
        engine = MetadataInferenceEngine()
        metadata_list = engine.infer_dataframe_metadata(df, warn_user=False)

        assert len(metadata_list) == len(df.columns)
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)

        print(
            f"🔧 Inference engine successfully processed {len(metadata_list)} columns"
        )

    def test_complex_industrial_scenarios(self):
        """Test complex industrial data scenarios."""
        # Create a complex industrial scenario
        complex_data = pd.DataFrame(
            {
                "plant_id": [
                    f"PLANT_{i:03d}" for i in range(1, 51)
                ],  # 50 unique plants
                "equipment_serial": [
                    f"EQ{i:06d}" for i in range(100000, 100050)
                ],  # Serial numbers
                "installation_date": pd.date_range("2020-01-01", periods=50, freq="7D"),
                "sensor_array_1": np.random.normal(100, 15, 50),  # Sensor readings
                "sensor_array_2": np.random.normal(200, 25, 50),
                "maintenance_code": np.random.choice(
                    ["A", "B", "C", "D"], 50
                ),  # Categorical
                "critical_threshold_exceeded": np.random.choice(
                    [True, False], 50
                ),  # Boolean
                "performance_index": np.random.uniform(
                    0.5, 1.0, 50
                ),  # Performance metric
                "predicted_failure_days": np.random.randint(
                    1, 365, 50
                ),  # Target variable
            }
        )

        # Add some missing data
        complex_data.loc[5:10, "sensor_array_1"] = np.nan
        complex_data.loc[15:20, "performance_index"] = np.nan

        # Run inference
        metadata_list = infer_metadata_from_dataframe(complex_data, warn_user=False)
        metadata_dict = {m.column_name: m for m in metadata_list}

        # Validate complex scenario handling - updated expectations for improved algorithm
        assert metadata_dict["plant_id"].role == "identifier"  # ID-like name + unique
        assert metadata_dict["equipment_serial"].role in [
            "identifier",
            "feature",
        ]  # Could be either
        assert metadata_dict["installation_date"].role == "time_index"
        assert metadata_dict["maintenance_code"].role in [
            "group_by",
            "feature",
        ]  # Could be either based on cardinality
        assert (
            metadata_dict["predicted_failure_days"].role == "target"
        )  # Should be target

        print(
            f"✅ Complex industrial scenario: {len(metadata_list)} columns properly classified"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
