#!/usr/bin/env python3
"""
Generic dataset test infrastructure for FunPuter.
Provides base classes and utilities for testing with any CSV dataset.
"""

import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from funputer.preflight import run_preflight
from funputer.metadata_inference import infer_metadata_from_dataframe
from funputer.simple_analyzer import analyze_imputation_requirements


class GenericDatasetTestBase:
    """Base class for generic dataset testing."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures with configurable dataset."""
        # Get dataset path from environment or use default
        dataset_name = os.environ.get('FUNPUTER_TEST_DATASET', 'industrial_equipment_data.csv')
        cls.data_path = Path(__file__).parent.parent / "data" / dataset_name
        
        if not cls.data_path.exists():
            pytest.skip(f"Test dataset {dataset_name} not found at {cls.data_path}")
        
        # Load and validate dataset
        cls.df = pd.read_csv(cls.data_path)
        cls._validate_dataset_requirements()
        
        # Convert datetime columns if detected
        for col in cls.df.columns:
            if cls.df[col].dtype == 'object' and 'timestamp' in col.lower():
                try:
                    cls.df[col] = pd.to_datetime(cls.df[col])
                except:
                    pass
        
        # Store dataset characteristics
        cls.dataset_info = cls._analyze_dataset_characteristics()
        
        print(f"\n📊 Generic Dataset Loaded: {dataset_name}")
        print(f"   Rows: {len(cls.df)}, Columns: {len(cls.df.columns)}")
        print(f"   Data types: {len(set(cls.df.dtypes.astype(str)))}")
        print(f"   Missing data columns: {len(cls.df.columns[cls.df.isnull().any()])}")
    
    @classmethod
    def _validate_dataset_requirements(cls):
        """Validate that the dataset meets minimum requirements for testing."""
        # Minimum requirements for comprehensive testing
        min_rows = 20
        min_columns = 15
        min_data_types = 3
        
        # Check basic size requirements
        if len(cls.df) < min_rows:
            pytest.skip(f"Dataset too small: {len(cls.df)} rows < {min_rows} required")
        
        if len(cls.df.columns) < min_columns:
            pytest.skip(f"Dataset too narrow: {len(cls.df.columns)} columns < {min_columns} required")
        
        # Check data type diversity
        data_types = set(cls.df.dtypes.astype(str))
        if len(data_types) < min_data_types:
            pytest.skip(f"Insufficient data type diversity: {len(data_types)} < {min_data_types} required")
        
        # Should have some missing data for imputation testing
        missing_columns = cls.df.columns[cls.df.isnull().any()].tolist()
        if len(missing_columns) < 3:
            pytest.skip(f"Insufficient missing data: {len(missing_columns)} columns < 3 required")
    
    @classmethod
    def _analyze_dataset_characteristics(cls):
        """Analyze dataset to understand its characteristics for adaptive testing."""
        return {
            'row_count': len(cls.df),
            'column_count': len(cls.df.columns),
            'data_types': set(cls.df.dtypes.astype(str)),
            'missing_columns': cls.df.columns[cls.df.isnull().any()].tolist(),
            'numeric_columns': cls.df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': cls.df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': cls.df.select_dtypes(include=['datetime64']).columns.tolist(),
            'high_cardinality_columns': [
                col for col in cls.df.columns 
                if cls.df[col].nunique() / len(cls.df) > 0.8
            ],
            'unique_columns': [
                col for col in cls.df.columns
                if cls.df[col].nunique() == len(cls.df)
            ]
        }
    
    def get_expected_roles(self) -> Dict[str, str]:
        """Get expected role classifications based on dataset analysis."""
        expected_roles = {}
        
        # Unique columns are likely identifiers
        for col in self.dataset_info['unique_columns']:
            if any(keyword in col.lower() for keyword in ['id', 'serial', 'number']):
                expected_roles[col] = 'identifier'
        
        # Datetime columns are time indices
        for col in self.dataset_info['datetime_columns']:
            expected_roles[col] = 'time_index'
        
        # High cardinality categorical columns might be grouping variables
        for col in self.dataset_info['categorical_columns']:
            cardinality = self.df[col].nunique()
            if 2 <= cardinality <= 10:  # Good grouping variable range
                if any(keyword in col.lower() for keyword in ['type', 'category', 'group', 'status', 'shift']):
                    expected_roles[col] = 'group_by'
        
        return expected_roles
    
    def get_minimum_accuracy_thresholds(self) -> Dict[str, float]:
        """Get minimum accuracy thresholds based on dataset complexity."""
        base_accuracy = 0.7
        
        # Adjust based on dataset complexity
        complexity_factor = min(self.dataset_info['column_count'] / 20, 2.0)  # Max 2x adjustment
        data_type_diversity = len(self.dataset_info['data_types']) / 5  # More diversity = easier inference
        
        adjusted_accuracy = base_accuracy * (1 + data_type_diversity - complexity_factor * 0.1)
        
        return {
            'role_classification': max(0.6, min(0.9, adjusted_accuracy)),
            'data_type_inference': max(0.8, min(0.95, adjusted_accuracy + 0.1)),
            'constraint_inference': max(0.5, min(0.8, adjusted_accuracy - 0.1))
        }


class DatasetTestUtilities:
    """Utility functions for dataset testing."""
    
    @staticmethod
    def discover_test_datasets(data_dir: Path) -> List[str]:
        """Discover all CSV files suitable for testing."""
        if not data_dir.exists():
            return []
        
        csv_files = []
        for file_path in data_dir.glob("*.csv"):
            try:
                # Quick validation
                df = pd.read_csv(file_path, nrows=5)
                if len(df.columns) >= 10 and len(df) >= 5:  # Basic requirements
                    csv_files.append(file_path.name)
            except:
                continue
        
        return sorted(csv_files)
    
    @staticmethod
    def create_minimal_test_dataset(temp_dir: str) -> str:
        """Create a minimal dataset for testing when no real data is available."""
        data = {
            'id': [f'ID_{i:03d}' for i in range(1, 26)],  # 25 rows
            'timestamp': pd.date_range('2024-01-01', periods=25, freq='1H'),
            'category_a': np.random.choice(['type1', 'type2', 'type3', 'type4'], 25),
            'category_b': np.random.choice(['group1', 'group2'], 25),
            'numeric_1': np.random.normal(100, 15, 25),
            'numeric_2': np.random.uniform(0, 1, 25),
            'numeric_3': np.random.randint(1, 1000, 25),
            'boolean_flag': np.random.choice([True, False], 25),
            'string_data': [f'text_{i}' for i in range(25)],
            'target_var': np.random.normal(50, 10, 25),
            'with_missing_1': [i if i % 4 != 0 else None for i in range(25)],
            'with_missing_2': [f'val_{i}' if i % 3 != 0 else None for i in range(25)],
            'sentinel_values': [i if i % 5 != 0 else -999 for i in range(25)],
            'high_cardinality': [f'unique_{i}' for i in range(25)],
            'debug_column': ['debug'] * 25,
            'system_version': np.random.choice(['v1.0', 'v2.0'], 25),
        }
        
        df = pd.DataFrame(data)
        file_path = os.path.join(temp_dir, 'minimal_test_data.csv')
        df.to_csv(file_path, index=False)
        
        return file_path
    
    @staticmethod
    def run_generic_preflight_test(data_path: Path) -> Dict[str, Any]:
        """Run preflight validation on any dataset."""
        report = run_preflight(str(data_path))
        
        # Generic validation
        assert report["status"] in ["ok", "ok_with_warnings"], f"PREFLIGHT failed: {report['status']}"
        assert report["file"]["format"] == "csv"
        assert report["structure"]["num_columns"] > 0
        
        return report
    
    @staticmethod
    def run_generic_inference_test(df: pd.DataFrame, min_accuracy: float = 0.7) -> List:
        """Run metadata inference on any dataset."""
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        # Generic validation
        assert len(metadata_list) == len(df.columns), "Should infer metadata for all columns"
        assert all(m.column_name is not None for m in metadata_list), "All columns should have names"
        assert all(m.data_type is not None for m in metadata_list), "All columns should have data types"
        assert all(m.role is not None for m in metadata_list), "All columns should have roles"
        
        return metadata_list
    
    @staticmethod
    def run_generic_analysis_test(data_path: Path, min_suggestions: int = 1) -> List:
        """Run imputation analysis on any dataset."""
        suggestions = analyze_imputation_requirements(str(data_path))
        
        # Generic validation
        assert isinstance(suggestions, list), "Should return list of suggestions"
        assert len(suggestions) >= min_suggestions, f"Should have at least {min_suggestions} suggestions"
        
        # Validate suggestion structure
        for suggestion in suggestions:
            assert hasattr(suggestion, 'column_name'), "Suggestions should have column names"
            assert hasattr(suggestion, 'proposed_method'), "Suggestions should have methods"
            assert hasattr(suggestion, 'confidence_score'), "Suggestions should have confidence scores"
            assert 0 <= suggestion.confidence_score <= 1, "Confidence should be between 0 and 1"
        
        return suggestions


def pytest_configure():
    """Configure pytest for generic dataset testing."""
    # Add markers for generic tests
    pytest.mark.generic = pytest.mark.generic or pytest.mark.parametrize
    pytest.mark.dataset_dependent = pytest.mark.dataset_dependent or pytest.mark.skipif


# Fixtures for generic testing
@pytest.fixture(scope="session")
def test_dataset_path():
    """Provide the path to the test dataset."""
    dataset_name = os.environ.get('FUNPUTER_TEST_DATASET', 'industrial_equipment_data.csv')
    return Path(__file__).parent.parent / "data" / dataset_name


@pytest.fixture(scope="session")
def test_dataset_df(test_dataset_path):
    """Load the test dataset as a DataFrame."""
    if not test_dataset_path.exists():
        pytest.skip(f"Test dataset not found: {test_dataset_path}")
    
    df = pd.read_csv(test_dataset_path)
    
    # Convert datetime columns
    for col in df.columns:
        if df[col].dtype == 'object' and any(keyword in col.lower() for keyword in ['timestamp', 'date', 'time']):
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
    
    return df


@pytest.fixture(scope="session")
def dataset_info(test_dataset_df):
    """Analyze the test dataset characteristics."""
    return {
        'row_count': len(test_dataset_df),
        'column_count': len(test_dataset_df.columns),
        'data_types': set(test_dataset_df.dtypes.astype(str)),
        'missing_columns': test_dataset_df.columns[test_dataset_df.isnull().any()].tolist(),
        'numeric_columns': test_dataset_df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': test_dataset_df.select_dtypes(include=['object', 'category']).columns.tolist(),
        'datetime_columns': test_dataset_df.select_dtypes(include=['datetime64']).columns.tolist(),
    }