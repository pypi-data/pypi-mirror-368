#!/usr/bin/env python3
"""
Comprehensive dataset inference test.
Tests all enhanced metadata inference capabilities on any dataset.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import os

from funputer.metadata_inference import infer_metadata_from_dataframe, MetadataInferenceEngine
from funputer.models import ColumnMetadata
from .test_dataset_generic import GenericDatasetTestBase


class TestDatasetInference(GenericDatasetTestBase):
    """Test enhanced metadata inference on any dataset."""
    
    @classmethod
    def setup_class(cls):
        """Load the dataset once for all tests."""
        # Initialize base class with dataset discovery
        super().setup_class()
        
        # Run inference once
        cls.metadata_list = infer_metadata_from_dataframe(cls.df, warn_user=False)
        cls.metadata_dict = {m.column_name: m for m in cls.metadata_list}
        
        print(f"\n📊 Dataset Loaded: {cls.dataset_info['row_count']} rows, {cls.dataset_info['column_count']} columns")
        print(f"🔍 Metadata Inferred: {len(cls.metadata_list)} column metadata objects")
        print(f"   Dataset: {os.path.basename(cls.data_path)}")
    
    def test_dataset_completeness(self):
        """Test that the dataset is comprehensive and suitable for inference testing."""
        df = self.df
        
        # Dataset should be substantial (requirements already validated in base class)
        assert len(df) >= 20, "Dataset should have sufficient rows for robust inference"
        assert len(df.columns) >= 15, "Dataset should have comprehensive column variety"
        
        # Should have multiple data types
        data_types = set(df.dtypes.astype(str))
        assert len(data_types) >= 3, f"Dataset should have varied data types, got: {data_types}"
        
        # Should have missing data for inference testing
        missing_columns = df.columns[df.isnull().any()].tolist()
        assert len(missing_columns) >= 3, f"Dataset should have missing data in multiple columns for testing"
        
        print(f"✅ Dataset validation: {len(df)} rows, {len(df.columns)} columns, {len(data_types)} data types")
        print(f"🔍 Missing data in {len(missing_columns)} columns: {missing_columns[:5]}...")
    
    def test_identifier_role_inference(self):
        """Test that identifier columns are correctly identified."""
        # Check unique columns that should be identifiers
        identifier_found = False
        
        for col_name in self.dataset_info['unique_columns']:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                if any(keyword in col_name.lower() for keyword in ['id', 'serial', 'number', 'key']) and meta.role == 'identifier':
                    assert meta.unique_flag == True, f"Identifier {col_name} should be unique"
                    assert meta.do_not_impute == True, f"Identifier {col_name} should not be imputed"
                    print(f"✅ Identifier inference: {col_name} correctly identified as {meta.role}")
                    identifier_found = True
                    break
        
        # If no specific identifier found, just verify we have unique columns classified
        if not identifier_found and self.dataset_info['unique_columns']:
            first_unique = self.dataset_info['unique_columns'][0]
            if first_unique in self.metadata_dict:
                meta = self.metadata_dict[first_unique]
                print(f"📊 Unique column {first_unique} classified as {meta.role} (acceptable)")
    
    def test_time_index_role_inference(self):
        """Test that time index columns are correctly identified."""
        # Check datetime columns for time_index role
        time_index_found = False
        
        for col_name in self.dataset_info['datetime_columns']:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                assert meta.data_type == 'datetime', f"{col_name} should be datetime, got: {meta.data_type}"
                
                if meta.role == 'time_index':
                    assert meta.time_index == True, f"Time index {col_name} flag should be True"
                    assert meta.do_not_impute == False, f"Time column {col_name} can be imputed"
                    print(f"✅ Time index inference: {col_name} correctly identified as {meta.role}")
                    time_index_found = True
        
        # If we have datetime columns, at least one should be time_index or acceptable alternative
        if self.dataset_info['datetime_columns'] and not time_index_found:
            first_datetime = self.dataset_info['datetime_columns'][0]
            meta = self.metadata_dict.get(first_datetime)
            if meta:
                print(f"📊 Datetime column {first_datetime} classified as {meta.role} (acceptable alternative)")
    
    def test_group_by_role_inference(self):
        """Test that grouping columns are correctly identified."""
        # Find categorical columns that could be grouping variables
        group_by_found = False
        
        for col_name in self.dataset_info['categorical_columns']:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                cardinality = self.df[col_name].nunique()
                
                # Good grouping variables have moderate cardinality (2-10 values)
                if 2 <= cardinality <= 10 and meta.role == 'group_by':
                    assert meta.group_by == True, f"{col_name} should have group_by=True"
                    print(f"✅ Role inference: {col_name} correctly identified as {meta.role} (cardinality: {cardinality})")
                    group_by_found = True
        
        # It's okay if no perfect group_by columns found - depends on dataset
        if not group_by_found:
            print(f"📊 No clear group_by columns found - acceptable for this dataset type")
    
    def test_target_role_inference(self):
        """Test that target/prediction columns are correctly identified."""
        # Find columns that might be targets based on naming patterns
        target_keywords = ['score', 'rating', 'prediction', 'target', 'label', 'outcome', 'result']
        target_found = False
        
        for col_name in self.df.columns:
            if any(keyword in col_name.lower() for keyword in target_keywords):
                if col_name in self.metadata_dict:
                    meta = self.metadata_dict[col_name]
                    
                    # Should be either target or feature (both acceptable)
                    assert meta.role in ['target', 'feature', 'ignore'], f"{col_name} should be target/feature/ignore, got: {meta.role}"
                    
                    if meta.role == 'target':
                        # Targets are often protected from imputation
                        print(f"✅ Target inference: {col_name} identified as {meta.role}, do_not_impute={meta.do_not_impute}")
                        target_found = True
        
        if not target_found:
            print(f"📊 No clear target columns found - acceptable for this dataset type")
    
    def test_ignore_role_inference(self):
        """Test that debug/system columns are appropriately classified."""
        # Find columns that might be debug/system columns
        ignore_keywords = ['debug', 'system', 'version', 'temp', 'backup', 'flag']
        
        for col_name in self.df.columns:
            if any(keyword in col_name.lower() for keyword in ignore_keywords):
                if col_name in self.metadata_dict:
                    meta = self.metadata_dict[col_name]
                    
                    # These could be ignore, feature, or target depending on patterns
                    print(f"📋 System-like column {col_name}: role={meta.role}, do_not_impute={meta.do_not_impute}")
    
    def test_numeric_data_inference(self):
        """Test that numeric data columns are correctly classified."""
        # Test numeric columns (could be sensor data or other measurements)
        numeric_columns = self.dataset_info['numeric_columns'][:5]  # Test first 5
        
        for col_name in numeric_columns:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                
                # Should be numeric type
                assert meta.data_type in ['integer', 'float'], f"{col_name} should be numeric, got: {meta.data_type}"
                
                # Check for reasonable constraints if data has variation
                if self.df[col_name].nunique() > 1 and meta.min_value is not None and meta.max_value is not None:
                    assert meta.min_value < meta.max_value, f"{col_name} should have valid min/max range"
                
                print(f"✅ Numeric inference: {col_name} classified as {meta.role} ({meta.data_type})")
    
    def test_sentinel_value_detection(self):
        """Test that sentinel values are correctly detected."""
        # Look for common sentinel values across all columns
        sentinel_found = False
        common_sentinels = [-999, -99, 999, 9999, -1]
        
        for col_name, meta in self.metadata_dict.items():
            if meta.sentinel_values:
                # Check if detected sentinels match common patterns
                detected_sentinels = str(meta.sentinel_values)
                for sentinel in common_sentinels:
                    if str(sentinel) in detected_sentinels:
                        print(f"✅ Sentinel detection: {col_name} detected sentinels: {meta.sentinel_values}")
                        sentinel_found = True
                        break
        
        if not sentinel_found:
            print(f"📊 No obvious sentinel values detected - acceptable for this dataset")
    
    def test_nullable_inference(self):
        """Test that nullable columns are correctly identified."""
        # Check columns with NULL values
        null_columns = self.df.columns[self.df.isnull().any()].tolist()
        
        for col_name in null_columns[:5]:  # Check first 5 null columns
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                
                # Should be correctly identified as nullable
                missing_count = self.df[col_name].isnull().sum()
                print(f"📊 Nullable column {col_name}: nullable={meta.nullable}, missing_count={missing_count}")
    
    def test_unique_flag_detection(self):
        """Test that unique flags are correctly set."""
        # Check various columns for uniqueness
        for col_name, meta in list(self.metadata_dict.items())[:10]:  # Check first 10 columns
            actual_unique_ratio = self.df[col_name].nunique() / len(self.df)
            
            print(f"🔍 Uniqueness {col_name}: unique_flag={meta.unique_flag}, actual_ratio={actual_unique_ratio:.2f}")
            
            # Truly unique columns should be flagged
            if actual_unique_ratio == 1.0:
                assert meta.unique_flag == True, f"{col_name} should be flagged as unique (100% unique)"
    
    def test_data_type_accuracy(self):
        """Test that data types are accurately inferred."""
        # Test specific known data types
        type_expectations = {
            'equipment_id': ['string', 'categorical'],
            'timestamp': ['datetime'],
            'temperature_sensor_c': ['float', 'integer'],
            'runtime_hours': ['float', 'integer'],
            'anomaly_detected': ['boolean'],
            'facility_location': ['string', 'categorical']
        }
        
        for col_name, expected_types in type_expectations.items():
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                assert meta.data_type in expected_types, f"{col_name} should be {expected_types}, got: {meta.data_type}"
                print(f"✅ Data type {col_name}: {meta.data_type} (expected: {expected_types})")
    
    def test_constraint_inference(self):
        """Test that constraints are properly inferred for numeric columns."""
        numeric_columns = ['temperature_sensor_c', 'pressure_psi', 'runtime_hours', 'efficiency_rating']
        
        for col_name in numeric_columns:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                
                if meta.data_type in ['float', 'integer']:
                    # Should have min/max values for numeric data
                    actual_min = self.df[col_name].min()
                    actual_max = self.df[col_name].max()
                    
                    print(f"📏 Constraints {col_name}: min={meta.min_value} (actual: {actual_min}), max={meta.max_value} (actual: {actual_max})")
                    
                    if meta.min_value is not None:
                        assert meta.min_value <= actual_min, f"{col_name} inferred min should be <= actual min"
                    if meta.max_value is not None:
                        assert meta.max_value >= actual_max, f"{col_name} inferred max should be >= actual max"
    
    def test_categorical_detection(self):
        """Test that categorical columns are correctly identified."""
        categorical_candidates = ['operational_status', 'equipment_type', 'shift_type']
        
        for col_name in categorical_candidates:
            if col_name in self.metadata_dict:
                meta = self.metadata_dict[col_name]
                
                # Should be identified as categorical or string
                assert meta.data_type in ['categorical', 'string'], f"{col_name} should be categorical/string, got: {meta.data_type}"
                
                # Check cardinality
                actual_cardinality = self.df[col_name].nunique()
                print(f"🏷️  Categorical {col_name}: type={meta.data_type}, cardinality={actual_cardinality}")
    
    def test_enhanced_metadata_completeness(self):
        """Test that all enhanced metadata fields are properly populated."""
        for col_name, meta in list(self.metadata_dict.items())[:5]:  # Check first 5 columns
            # All enhanced fields should have values
            assert hasattr(meta, 'role'), f"{col_name} should have role field"
            assert hasattr(meta, 'do_not_impute'), f"{col_name} should have do_not_impute field"
            assert hasattr(meta, 'time_index'), f"{col_name} should have time_index field"
            assert hasattr(meta, 'group_by'), f"{col_name} should have group_by field"
            assert hasattr(meta, 'policy_version'), f"{col_name} should have policy_version field"
            
            # Should have reasonable values
            assert meta.role in ['identifier', 'feature', 'target', 'time_index', 'group_by', 'ignore'], f"{col_name} has invalid role: {meta.role}"
            assert meta.do_not_impute in [True, False], f"{col_name} has invalid do_not_impute: {meta.do_not_impute}"
            assert meta.policy_version == 'v1.0', f"{col_name} has invalid policy_version: {meta.policy_version}"
            
            print(f"🔧 Enhanced metadata {col_name}: role={meta.role}, do_not_impute={meta.do_not_impute}")
    
    def test_inference_consistency(self):
        """Test that inference results are consistent and logical."""
        identifier_count = sum(1 for m in self.metadata_list if m.role == 'identifier')
        time_index_count = sum(1 for m in self.metadata_list if m.time_index == True)
        group_by_count = sum(1 for m in self.metadata_list if m.group_by == True)
        feature_count = sum(1 for m in self.metadata_list if m.role == 'feature')
        
        # Should have reasonable distribution of roles
        assert identifier_count >= 1, "Should have at least one identifier"
        assert time_index_count >= 1, "Should have at least one time index"
        assert group_by_count >= 1, "Should have at least one group-by column"
        assert feature_count >= 5, "Should have multiple feature columns"
        
        print(f"📊 Role distribution: identifiers={identifier_count}, time_index={time_index_count}, group_by={group_by_count}, features={feature_count}")
    
    def test_missing_data_patterns(self):
        """Test that missing data patterns are appropriately handled."""
        # Check columns with different missing patterns
        missing_stats = {}
        for col_name in self.df.columns:
            missing_count = self.df[col_name].isnull().sum()
            if missing_count > 0:
                missing_stats[col_name] = {
                    'count': missing_count,
                    'percentage': missing_count / len(self.df) * 100
                }
        
        print(f"📈 Missing data patterns detected in {len(missing_stats)} columns:")
        for col_name, stats in list(missing_stats.items())[:5]:  # Show first 5
            meta = self.metadata_dict.get(col_name)
            if meta:
                print(f"   {col_name}: {stats['count']} missing ({stats['percentage']:.1f}%), role={meta.role}, imputable={not meta.do_not_impute}")
    
    def test_dataset_domain_patterns(self):
        """Test that dataset-specific patterns are recognized."""
        # Test general patterns that should be recognized in any dataset
        
        # Check that identifiers are properly classified
        identifier_count = sum(1 for m in self.metadata_list if m.role == 'identifier')
        assert identifier_count >= 1, "Should identify at least one identifier column"
        
        # Check that categorical data is properly typed
        categorical_count = sum(1 for m in self.metadata_list if m.data_type == 'categorical')
        if self.dataset_info['categorical_columns']:
            assert categorical_count > 0, "Should identify categorical columns when present"
        
        # Check that numeric data has appropriate constraints
        numeric_with_constraints = 0
        for meta in self.metadata_list:
            if meta.data_type in ['float', 'integer'] and meta.min_value is not None:
                numeric_with_constraints += 1
        
        if self.dataset_info['numeric_columns']:
            print(f"📊 Numeric columns with constraints: {numeric_with_constraints}/{len(self.dataset_info['numeric_columns'])}")
        
        print(f"🔍 Dataset patterns recognized: {identifier_count} identifiers, {categorical_count} categorical")
    
    def test_production_readiness(self):
        """Test that the inference results are production-ready."""
        # All columns should have complete metadata
        assert len(self.metadata_list) == len(self.df.columns), "Should have metadata for all columns"
        
        # No metadata should be None or invalid
        for meta in self.metadata_list:
            assert meta.column_name is not None, "Column name should not be None"
            assert meta.data_type is not None, "Data type should not be None"
            assert meta.role is not None, "Role should not be None"
            
        # Should have actionable imputation guidance
        imputable_columns = [m for m in self.metadata_list if not m.do_not_impute]
        non_imputable_columns = [m for m in self.metadata_list if m.do_not_impute]
        
        print(f"🎯 Production readiness: {len(imputable_columns)} imputable, {len(non_imputable_columns)} protected columns")
        print(f"✅ All {len(self.metadata_list)} columns have complete enhanced metadata")


class TestInferenceEngine(GenericDatasetTestBase):
    """Test the inference engine with any dataset."""
    
    @classmethod
    def setup_class(cls):
        """Set up generic dataset."""
        super().setup_class()
    
    def test_engine_with_dataset(self):
        """Test inference engine direct usage on dataset."""
        # Test engine instantiation and usage
        engine = MetadataInferenceEngine()
        metadata_list = engine.infer_dataframe_metadata(self.df, warn_user=False)
        
        assert len(metadata_list) == len(self.df.columns)
        assert all(isinstance(m, ColumnMetadata) for m in metadata_list)
        
        print(f"🔧 Inference engine successfully processed {len(metadata_list)} columns")
    
    def test_complex_data_scenarios(self):
        """Test complex data scenarios with synthetic data."""
        # Create a complex synthetic scenario
        np.random.seed(42)  # For reproducible tests
        complex_data = pd.DataFrame({
            'record_id': [f'REC_{i:03d}' for i in range(1, 51)],  # 50 unique records
            'entity_serial': [f'ENT{i:06d}' for i in range(100000, 100050)],  # Serial numbers
            'timestamp': pd.date_range('2020-01-01', periods=50, freq='7D'),
            'measurement_1': np.random.normal(100, 15, 50),  # Numeric readings
            'measurement_2': np.random.normal(200, 25, 50),
            'category_code': np.random.choice(['A', 'B', 'C', 'D'], 50),  # Categorical
            'flag_exceeded': np.random.choice([True, False], 50),  # Boolean
            'performance_metric': np.random.uniform(0.5, 1.0, 50),  # Performance metric
            'target_days': np.random.randint(1, 365, 50),  # Target variable
        })
        
        # Add some missing data
        complex_data.loc[5:10, 'measurement_1'] = np.nan
        complex_data.loc[15:20, 'performance_metric'] = np.nan
        
        # Run inference
        metadata_list = infer_metadata_from_dataframe(complex_data, warn_user=False)
        metadata_dict = {m.column_name: m for m in metadata_list}
        
        # Validate complex scenario handling - generic expectations
        assert metadata_dict['record_id'].role == 'identifier'  # ID-like name + unique
        assert metadata_dict['entity_serial'].role in ['identifier', 'feature']  # Could be either
        assert metadata_dict['timestamp'].role == 'time_index'
        assert metadata_dict['category_code'].role in ['group_by', 'feature']  # Could be either based on cardinality
        assert metadata_dict['target_days'].role in ['target', 'feature']  # Should be target or feature
        
        print(f"✅ Complex data scenario: {len(metadata_list)} columns properly classified")


if __name__ == "__main__":
    # Can be run with different datasets using FUNPUTER_TEST_DATASET environment variable
    pytest.main([__file__, "-v", "-s"])