#!/usr/bin/env python3
"""
Critical Client Test - Production Pipeline
This test MUST pass after any refactoring and before any release.

Complete flow: Preflight -> Metadata Inference -> Analysis
"""

import warnings
import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to import funputer
sys.path.insert(0, str(Path(__file__).parent.parent))

from funputer.preflight import run_preflight, format_preflight_report
from funputer import infer_metadata_from_dataframe, analyze_dataframe
import pandas as pd


class TestClientPipeline:
    """Test the complete production pipeline that clients depend on."""
    
    def test_complete_production_pipeline(self):
        """
        CRITICAL TEST: This represents actual client usage.
        Must pass after any refactoring and before any release.
        """
        # Suppress harmless numpy warnings during correlation calculations
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="invalid value encountered in divide")
        
        # Configuration
        data_file = "data/industrial_equipment_data.csv"
        
        # Create temp directory for outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_file = os.path.join(temp_dir, "metadata.csv")
            output_file = os.path.join(temp_dir, "production_suggestions.csv")
            
            print("\n🚀 TESTING CLIENT PRODUCTION PIPELINE")
            print("=" * 50)
            
            # STAGE 1: PREFLIGHT CHECK
            print("\n📋 STAGE 1: PREFLIGHT CHECK")
            preflight_report = run_preflight(data_file)
            assert preflight_report is not None, "Preflight report should not be None"
            assert 'status' in preflight_report, "Preflight report must have status"
            assert preflight_report['status'] in ['ok', 'ok_with_warnings'], f"Preflight failed: {preflight_report['status']}"
            
            formatted_report = format_preflight_report(preflight_report)
            assert formatted_report is not None, "Formatted report should not be None"
            print("✅ Preflight passed")
            
            # STAGE 2: METADATA INFERENCE
            print("\n🔍 STAGE 2: METADATA INFERENCE")
            df = pd.read_csv(data_file)
            assert not df.empty, "Data should not be empty"
            
            metadata = infer_metadata_from_dataframe(df)
            assert metadata is not None, "Metadata should not be None"
            assert len(metadata) == len(df.columns), f"Metadata count {len(metadata)} != column count {len(df.columns)}"
            
            # Verify metadata structure
            for col_meta in metadata:
                assert hasattr(col_meta, 'column_name'), "Metadata must have column_name"
                assert hasattr(col_meta, 'data_type'), "Metadata must have data_type"
                assert hasattr(col_meta, 'role'), "Metadata must have role"
                assert hasattr(col_meta, 'description'), "Metadata must have description"
            
            # Save metadata (client code does this)
            metadata_df = pd.DataFrame([{
                'column_name': meta.column_name,
                'data_type': meta.data_type,
                'role': meta.role,
                'nullable': meta.nullable,
                'unique_flag': meta.unique_flag,
                'description': meta.description,
                'min_value': getattr(meta, 'min_value', None),
                'max_value': getattr(meta, 'max_value', None),
                'max_length': getattr(meta, 'max_length', None),
                'allowed_values': getattr(meta, 'allowed_values', None),
                'dependent_column': getattr(meta, 'dependent_column', None)
            } for meta in metadata])
            
            metadata_df.to_csv(metadata_file, index=False)
            assert os.path.exists(metadata_file), "Metadata file should be created"
            print(f"✅ Metadata inference passed - {len(metadata)} columns")
            
            # STAGE 3: ANALYSIS
            print("\n📊 STAGE 3: IMPUTATION ANALYSIS")
            suggestions = analyze_dataframe(df, metadata)
            assert suggestions is not None, "Suggestions should not be None"
            assert len(suggestions) > 0, "Should generate at least one suggestion"
            
            # Verify suggestion structure
            for suggestion in suggestions:
                assert hasattr(suggestion, 'column_name'), "Suggestion must have column_name"
                assert hasattr(suggestion, 'proposed_method'), "Suggestion must have proposed_method"
                assert hasattr(suggestion, 'confidence_score'), "Suggestion must have confidence_score"
                assert hasattr(suggestion, 'mechanism'), "Suggestion must have mechanism"
                assert hasattr(suggestion, 'rationale'), "Suggestion must have rationale"
                assert 0 <= suggestion.confidence_score <= 1, f"Invalid confidence score: {suggestion.confidence_score}"
            
            # Save results (client code does this)
            suggestions_df = pd.DataFrame([{
                'column_name': s.column_name,
                'method': s.proposed_method,
                'confidence_score': s.confidence_score,
                'missing_mechanism': s.mechanism,
                'reasoning': s.rationale,
                'missing_percentage': s.missing_percentage,
                'outlier_percentage': s.outlier_percentage
            } for s in suggestions])
            
            suggestions_df.to_csv(output_file, index=False)
            assert os.path.exists(output_file), "Output file should be created"
            
            # Verify high/medium confidence split works
            high_confidence = [s for s in suggestions if s.confidence_score > 0.7]
            medium_confidence = [s for s in suggestions if 0.4 <= s.confidence_score <= 0.7]
            print(f"✅ Analysis passed - {len(suggestions)} suggestions")
            print(f"   🟢 High confidence: {len(high_confidence)}")
            print(f"   🟡 Medium confidence: {len(medium_confidence)}")
            
            # SUMMARY
            print("\n🎉 CLIENT PIPELINE TEST COMPLETED SUCCESSFULLY")
            print("=" * 50)
            print(f"✅ All stages passed")
            print(f"✅ All imports working")
            print(f"✅ All outputs generated")
            print(f"✅ Client code compatibility verified")


def run_client_pipeline_standalone():
    """
    Run the client pipeline test standalone (not through pytest).
    Useful for manual testing before releases.
    """
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    # Configuration
    data_file = "data/industrial_equipment_data.csv"
    
    print("🚀 FUNPUTER PRODUCTION PIPELINE")
    print("=" * 50)
    
    # STAGE 1: PREFLIGHT CHECK
    print("\n📋 STAGE 1: PREFLIGHT CHECK")
    print("-" * 30)
    
    try:
        preflight_report = run_preflight(data_file)
        formatted_report = format_preflight_report(preflight_report)
        print(formatted_report)
        
        if preflight_report['status'] not in ['ok', 'ok_with_warnings']:
            print("❌ Preflight failed - cannot proceed")
            return False
            
        print("✅ Preflight passed - ready to proceed")
        
    except Exception as e:
        print(f"❌ Preflight error: {e}")
        return False
    
    # STAGE 2: METADATA INFERENCE
    print(f"\n🔍 STAGE 2: METADATA INFERENCE")
    print("-" * 30)
    
    try:
        df = pd.read_csv(data_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
        
        metadata = infer_metadata_from_dataframe(df)
        print(f"🎯 Inferred metadata for {len(metadata)} columns")
        
    except Exception as e:
        print(f"❌ Metadata inference error: {e}")
        return False
    
    # STAGE 3: ANALYSIS
    print(f"\n📊 STAGE 3: IMPUTATION ANALYSIS")
    print("-" * 30)
    
    try:
        suggestions = analyze_dataframe(df, metadata)
        print(f"💡 Generated {len(suggestions)} imputation suggestions")
        
        high_confidence = [s for s in suggestions if s.confidence_score > 0.7]
        medium_confidence = [s for s in suggestions if 0.4 <= s.confidence_score <= 0.7]
        
        print(f"   🟢 High confidence: {len(high_confidence)} suggestions")
        print(f"   🟡 Medium confidence: {len(medium_confidence)} suggestions")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False
    
    # SUMMARY
    print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print(f"✅ Preflight: {preflight_report['status']}")
    print(f"✅ Metadata: {len(metadata)} columns analyzed")
    print(f"✅ Analysis: {len(suggestions)} suggestions generated")
    
    return True


if __name__ == "__main__":
    # Run standalone when called directly
    success = run_client_pipeline_standalone()
    sys.exit(0 if success else 1)