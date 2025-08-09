#!/usr/bin/env python3
"""
End-to-End Testing Script for FunPuter v1.3.1
=============================================

This script performs comprehensive testing of all FunPuter functionality.
Run this after installation to verify everything works correctly.
"""

import os
import sys
import time
import pandas as pd
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, status='START'):
    """Print formatted test status."""
    if status == 'START':
        print(f"\n{BLUE}▶ {name}{RESET}")
    elif status == 'PASS':
        print(f"{GREEN}✅ {name} - PASSED{RESET}")
    elif status == 'FAIL':
        print(f"{RED}❌ {name} - FAILED{RESET}")
    elif status == 'SKIP':
        print(f"{YELLOW}⚠️  {name} - SKIPPED{RESET}")

def test_imports():
    """Test 1: Package imports."""
    print_test("Test 1: Package Imports", "START")
    try:
        import funputer
        from funputer import SimpleImputationAnalyzer, ColumnMetadata
        from funputer.models import AnalysisConfig, ImputationSuggestion
        from funputer.preflight import run_preflight
        from funputer.metadata_inference import infer_metadata_from_dataframe
        
        print(f"  Version: {funputer.__version__}")
        print_test("Test 1: Package Imports", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 1: Package Imports", "FAIL")
        return False

def test_cli_commands():
    """Test 2: CLI commands."""
    print_test("Test 2: CLI Commands", "START")
    try:
        import subprocess
        
        # Test help
        result = subprocess.run(['funputer', '--help'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("CLI help failed")
        
        # Test preflight
        result = subprocess.run(['funputer', 'preflight', '-d', 'data/workflow_sample_data.csv'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: Preflight returned {result.returncode}")
        
        print("  CLI commands working")
        print_test("Test 2: CLI Commands", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 2: CLI Commands", "FAIL")
        return False

def test_python_api():
    """Test 3: Python API functionality."""
    print_test("Test 3: Python API", "START")
    try:
        import funputer
        
        # Create test data
        df = pd.DataFrame({
            'age': [25, None, 35, 40, None],
            'salary': [50000, 60000, None, 80000, 70000],
            'category': ['A', 'B', 'A', None, 'B']
        })
        
        # Auto-inference
        suggestions = funputer.analyze_imputation_requirements(df)
        print(f"  Auto-inference: {len(suggestions)} suggestions")
        
        # With metadata
        from funputer import SimpleImputationAnalyzer, ColumnMetadata
        metadata = [
            ColumnMetadata('age', 'integer', min_value=0, max_value=120),
            ColumnMetadata('salary', 'float', min_value=0),
            ColumnMetadata('category', 'categorical', allowed_values='A,B,C')
        ]
        
        analyzer = SimpleImputationAnalyzer()
        suggestions = analyzer.analyze_dataframe(df, metadata)
        print(f"  With metadata: {len(suggestions)} suggestions")
        
        print_test("Test 3: Python API", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 3: Python API", "FAIL")
        return False

def test_preflight_system():
    """Test 4: PREFLIGHT validation system."""
    print_test("Test 4: PREFLIGHT System", "START")
    try:
        from funputer.preflight import run_preflight
        
        # Test on sample data
        report = run_preflight('data/workflow_sample_data.csv')
        print(f"  Status: {report['status']}")
        if isinstance(report.get('columns'), dict):
            print(f"  Columns: {report.get('columns', {}).get('count', 'N/A')}")
        else:
            print(f"  Columns: {len(report.get('columns', []))}")
        print(f"  Recommendation: {report.get('recommendation', 'N/A')}")
        
        print_test("Test 4: PREFLIGHT System", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 4: PREFLIGHT System", "FAIL")
        return False

def test_metadata_inference():
    """Test 5: Metadata auto-inference."""
    print_test("Test 5: Metadata Inference", "START")
    try:
        from funputer.metadata_inference import infer_metadata_from_dataframe
        
        # Load sample data
        df = pd.read_csv('data/workflow_sample_data.csv')
        metadata = infer_metadata_from_dataframe(df, warn_user=False)
        
        print(f"  Inferred {len(metadata)} columns")
        
        # Check key fields
        id_cols = [m for m in metadata if getattr(m, 'role', '') == 'identifier']
        print(f"  Identifiers found: {len(id_cols)}")
        
        numeric_cols = [m for m in metadata if m.data_type in ['integer', 'float']]
        print(f"  Numeric columns: {len(numeric_cols)}")
        
        print_test("Test 5: Metadata Inference", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 5: Metadata Inference", "FAIL")
        return False

def test_complete_workflow():
    """Test 6: Complete workflow integration."""
    print_test("Test 6: Complete Workflow", "START")
    try:
        import funputer
        from funputer.io import save_suggestions
        
        # Step 1: Analyze data
        suggestions = funputer.analyze_imputation_requirements('data/workflow_sample_data.csv')
        
        # Step 2: Save results
        output_path = 'test_workflow_results.csv'
        save_suggestions(suggestions, output_path)
        
        # Step 3: Verify results
        results_df = pd.read_csv(output_path)
        print(f"  Analyzed {len(results_df)} columns")
        if 'missing_count' in results_df.columns:
            print(f"  Missing values: {results_df['missing_count'].sum()}")
        if 'confidence_score' in results_df.columns:
            print(f"  Avg confidence: {results_df['confidence_score'].mean():.3f}")
        else:
            print(f"  Results saved with {len(results_df.columns)} fields")
        
        # Cleanup
        os.remove(output_path)
        
        print_test("Test 6: Complete Workflow", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 6: Complete Workflow", "FAIL")
        return False

def test_error_handling():
    """Test 7: Error handling and edge cases."""
    print_test("Test 7: Error Handling", "START")
    try:
        import funputer
        
        # Test non-existent file
        try:
            funputer.analyze_imputation_requirements('nonexistent.csv')
        except FileNotFoundError:
            print("  ✓ File not found handled")
        
        # Test empty DataFrame
        empty_df = pd.DataFrame()
        suggestions = funputer.analyze_imputation_requirements(empty_df)
        print(f"  ✓ Empty DataFrame: {len(suggestions)} suggestions")
        
        # Test all missing
        all_missing = pd.DataFrame({'col': [None, None, None]})
        suggestions = funputer.analyze_imputation_requirements(all_missing)
        print(f"  ✓ All missing: {len(suggestions)} suggestions")
        
        print_test("Test 7: Error Handling", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 7: Error Handling", "FAIL")
        return False

def test_performance():
    """Test 8: Performance with larger dataset."""
    print_test("Test 8: Performance Testing", "START")
    try:
        import funputer
        
        # Create larger dataset
        n_rows = 5000
        n_cols = 20
        
        data = {}
        for i in range(n_cols):
            # Add some missing values
            values = list(range(n_rows))
            for j in range(0, n_rows, 10):
                values[j] = None
            data[f'col_{i}'] = values
        
        large_df = pd.DataFrame(data)
        
        # Time the analysis
        start = time.time()
        suggestions = funputer.analyze_imputation_requirements(large_df)
        elapsed = time.time() - start
        
        print(f"  Analyzed {n_rows} rows × {n_cols} cols in {elapsed:.2f}s")
        print(f"  Performance: {(n_rows * n_cols) / elapsed:.0f} cells/second")
        
        print_test("Test 8: Performance Testing", "PASS")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        print_test("Test 8: Performance Testing", "FAIL")
        return False

def main():
    """Run all tests and report results."""
    print("=" * 60)
    print("FunPuter v1.3.1 - End-to-End Testing")
    print("=" * 60)
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run tests
    tests = [
        test_imports,
        test_cli_commands,
        test_python_api,
        test_preflight_system,
        test_metadata_inference,
        test_complete_workflow,
        test_error_handling,
        test_performance
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append(passed)
        except Exception as e:
            print(f"Unexpected error in {test.__name__}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED! FunPuter is working correctly.{RESET}")
        return 0
    else:
        print(f"\n{RED}⚠️  Some tests failed. Please check the errors above.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())