#!/usr/bin/env python3
"""
Preflight checks for data files before analysis.

Lean, fast validation to prevent crashes and advise workflow.
Sample-only analysis, no heavy computation.
"""

import os
import gzip
import zipfile
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings

# Core dependencies
import pandas as pd
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

# Consolidated constants and configuration
CONFIG = {
    'DEFAULT_SAMPLE_ROWS': 2000,
    'DEFAULT_MAX_SNIFF_BYTES': 65536,
    'SUPPORTED_FORMATS': ["csv", "json", "jsonl", "parquet", "xlsx"],
    'SUPPORTED_COMPRESSIONS': ["none", "gz", "zip"],
    'ENCODING_CANDIDATES': ['utf-8', 'utf-16', 'latin1', 'cp1252', 'iso-8859-1'],
    'CSV_DELIMITERS': [',', ';', '\t', '|'],
    'MEMORY_WARNING_THRESHOLD': 1024 * 1024 * 1024,  # 1GB
    'MIN_SAMPLE_THRESHOLD': 50,
    'NULL_PERCENTAGE_WARNING': 50.0,
}

# Compiled regex patterns for performance
PATTERNS = {
    'DATETIME': [
        re.compile(r'\d{4}-\d{2}-\d{2}'),
        re.compile(r'\d{2}/\d{2}/\d{4}'),
        re.compile(r'\d{4}/\d{2}/\d{2}'),
    ],
    'NUMERIC': re.compile(r'^-?[\d,]+\.?\d*$'),
    'BOOLEAN': re.compile(r'^(true|false|yes|no|y|n|1|0)$', re.IGNORECASE),
}


def run_preflight(
    path: str,
    *,
    sample_rows: int = None,
    max_sniff_bytes: int = None,
    hints: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run preflight checks on a data file.

    Args:
        path: Path to data file
        sample_rows: Maximum rows to sample for analysis
        max_sniff_bytes: Maximum bytes to read for format detection
        hints: Optional user hints (delimiter, encoding, etc.)

    Returns:
        Preflight report dictionary
    """
    sample_rows = sample_rows or CONFIG['DEFAULT_SAMPLE_ROWS']
    max_sniff_bytes = max_sniff_bytes or CONFIG['DEFAULT_MAX_SNIFF_BYTES']
    hints = hints or {}

    # Initialize report
    report = {
        'path': path,
        'exit_code': 0,
        'status': 'ok',
        'checks': {},
        'warnings': [],
        'recommendation': {'action': 'unknown'},
    }

    try:
        # Run all checks in sequence
        checks = [
            ('A1_path_size', _check_path_and_size),
            ('A2_format_compression', lambda p: _detect_format_and_compression(p, max_sniff_bytes)),
            ('A3_encoding', lambda p: _probe_encoding(p, hints.get('encoding'))),
            ('A4_csv_dialect', lambda p: _sniff_csv_dialect(p, hints)),
            ('A5_structure', lambda p: _analyze_structure_and_sample(p, sample_rows, hints)),
            ('A6_memory', lambda p: _estimate_memory_usage(p, sample_rows)),
        ]

        for check_name, check_func in checks:
            try:
                result = check_func(path)
                report['checks'][check_name] = result
                
                # Aggregate warnings
                if 'warnings' in result:
                    report['warnings'].extend(result['warnings'])
                    
                # Check for hard errors
                if result.get('error'):
                    report['exit_code'] = 10
                    report['status'] = 'error'
                    report['error'] = result['error']
                    break
                    
            except Exception as e:
                logger.warning(f"Check {check_name} failed: {e}")
                report['checks'][check_name] = {'error': str(e)}
                report['warnings'].append(f"Check {check_name} failed: {e}")

        # Generate final recommendation
        if report['exit_code'] != 10:  # Only if no hard errors
            report['recommendation'] = _decide_recommendation(report)
            if report['warnings']:
                report['exit_code'] = 2
                report['status'] = 'ok_with_warnings'

    except Exception as e:
        logger.error(f"Preflight failed with unexpected error: {e}")
        report.update({
            'exit_code': 10,
            'status': 'error',
            'error': f"Unexpected error: {e}"
        })

    return report


def _check_path_and_size(path: str) -> Dict[str, Any]:
    """A1: Check file path, existence, size, and basic accessibility."""
    result = {'path_exists': False, 'readable': False, 'size_bytes': 0}
    
    try:
        if not os.path.exists(path):
            return {**result, 'error': f"File does not exist: {path}"}
            
        if not os.path.isfile(path):
            return {**result, 'error': f"Path is not a file: {path}"}
            
        if not os.access(path, os.R_OK):
            return {**result, 'error': f"File is not readable: {path}"}
            
        size = os.path.getsize(path)
        if size == 0:
            return {**result, 'error': "File is empty"}
            
        result.update({
            'path_exists': True,
            'readable': True,
            'size_bytes': size,
            'size_mb': round(size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        result['error'] = f"Path check failed: {e}"
        
    return result


def _detect_format_and_compression(path: str, max_bytes: int) -> Dict[str, str]:
    """A2: Detect file format and compression."""
    path_obj = Path(path)
    
    # Check compression from extension
    compression = 'none'
    if path_obj.suffix.lower() == '.gz':
        compression = 'gz'
    elif path_obj.suffix.lower() == '.zip':
        compression = 'zip'
    
    # Detect format from extension and content sniffing
    stem = path_obj.stem if compression != 'none' else path_obj.name
    stem_suffix = Path(stem).suffix.lower()
    
    format_from_ext = {
        '.csv': 'csv',
        '.json': 'json',
        '.jsonl': 'jsonl',
        '.parquet': 'parquet',
        '.xlsx': 'xlsx',
        '.xls': 'xlsx'
    }.get(stem_suffix, 'unknown')
    
    # Content-based detection for ambiguous cases
    detected_format = format_from_ext
    try:
        sample_bytes = _read_file_bytes(path, max_bytes, compression)
        if sample_bytes:
            detected_format = _infer_format_from_content(sample_bytes) or format_from_ext
    except Exception as e:
        logger.debug(f"Content detection failed: {e}")
    
    return {
        'format': detected_format,
        'compression': compression,
        'format_from_extension': format_from_ext,
        'supported': detected_format in CONFIG['SUPPORTED_FORMATS']
    }


def _probe_encoding(path: str, hint: Optional[str] = None) -> Dict[str, Any]:
    """A3: Probe character encoding."""
    result = {'encoding': 'utf-8', 'confidence': 0.0}
    
    # If hint provided, try it first
    candidates = [hint] + CONFIG['ENCODING_CANDIDATES'] if hint else CONFIG['ENCODING_CANDIDATES']
    
    try:
        sample_bytes = _read_file_bytes(path, 8192)  # Smaller sample for encoding
        
        for encoding in candidates:
            if encoding:
                try:
                    sample_bytes.decode(encoding)
                    result['encoding'] = encoding
                    result['confidence'] = 1.0 if encoding == hint else 0.8
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
                    
    except Exception as e:
        result['warnings'] = [f"Encoding detection failed: {e}"]
    
    return result


def _sniff_csv_dialect(path: str, hints: Dict[str, Any]) -> Dict[str, Any]:
    """A4: Detect CSV delimiter, quote char, and header presence."""
    result = {'delimiter': ',', 'quotechar': '"', 'has_header': True}
    
    if hints.get('format') not in ['csv', 'unknown']:
        return result
        
    try:
        sample_text = _read_file_text(path, hints.get('encoding', 'utf-8'), 4096)
        
        # Detect delimiter
        delimiter_counts = {delim: sample_text.count(delim) for delim in CONFIG['CSV_DELIMITERS']}
        if delimiter_counts:
            result['delimiter'] = max(delimiter_counts, key=delimiter_counts.get)
            
        # Simple header detection - check if first line looks like column names
        lines = sample_text.split('\n')[:5]  # Check first 5 lines
        if lines:
            first_line_parts = lines[0].split(result['delimiter'])
            # If first line has non-numeric, non-empty strings, likely header
            has_header = any(part.strip() and not part.strip().replace('.', '').isdigit() 
                           for part in first_line_parts)
            result['has_header'] = has_header
            
    except Exception as e:
        result['warnings'] = [f"CSV dialect detection failed: {e}"]
    
    return result


def _analyze_structure_and_sample(path: str, sample_rows: int, hints: Dict[str, Any]) -> Dict[str, Any]:
    """A5: Read sample data and analyze structure."""
    result = {'columns': [], 'sample_rows': 0, 'estimated_total_rows': 0}
    
    try:
        # Read sample data
        df = _read_sample_dataframe(path, sample_rows, hints)
        
        if df is not None and not df.empty:
            result.update({
                'sample_rows': len(df),
                'total_columns': len(df.columns),
                'columns': [{'name': col, 'type': _infer_coarse_type(df[col]), 
                            'null_count': df[col].isnull().sum(),
                            'null_percentage': (df[col].isnull().sum() / len(df)) * 100}
                           for col in df.columns],
                'estimated_total_rows': _estimate_total_rows(path, len(df), sample_rows),
                'sample_warnings': _collect_sample_warnings(df)
            })
        else:
            result['warnings'] = ["Unable to read sample data"]
            
    except Exception as e:
        result['error'] = f"Structure analysis failed: {e}"
    
    return result


def _estimate_memory_usage(path: str, sample_rows: int) -> Dict[str, Any]:
    """A6: Estimate memory requirements for full processing."""
    result = {'estimated_memory_mb': 0, 'memory_warning': False}
    
    try:
        file_size = os.path.getsize(path)
        
        # Rough estimate: CSV files typically expand 2-3x in memory as DataFrame
        # Other formats vary, but this is a reasonable baseline
        estimated_memory = file_size * 3
        estimated_memory_mb = estimated_memory / (1024 * 1024)
        
        result.update({
            'estimated_memory_mb': round(estimated_memory_mb, 2),
            'memory_warning': estimated_memory > CONFIG['MEMORY_WARNING_THRESHOLD']
        })
        
        if result['memory_warning']:
            result['warnings'] = [f"Large file may require {estimated_memory_mb:.0f} MB of memory"]
            
    except Exception as e:
        result['warnings'] = [f"Memory estimation failed: {e}"]
    
    return result


# Helper functions
def _read_file_bytes(path: str, max_bytes: int, compression: str = None) -> bytes:
    """Read raw bytes from file with compression support."""
    if compression == 'gz':
        with gzip.open(path, 'rb') as f:
            return f.read(max_bytes)
    elif compression == 'zip':
        with zipfile.ZipFile(path, 'r') as zf:
            # Read from first file in zip
            names = zf.namelist()
            if names:
                with zf.open(names[0]) as f:
                    return f.read(max_bytes)
    else:
        with open(path, 'rb') as f:
            return f.read(max_bytes)
    return b''


def _read_file_text(path: str, encoding: str, max_chars: int) -> str:
    """Read text from file with encoding."""
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read(max_chars)
    except Exception:
        # Fallback to bytes reading and decoding
        raw_bytes = _read_file_bytes(path, max_chars * 2)  # Estimate 2 bytes per char
        return raw_bytes.decode(encoding, errors='ignore')


def _infer_format_from_content(content_bytes: bytes) -> Optional[str]:
    """Infer file format from content bytes."""
    try:
        content_str = content_bytes.decode('utf-8', errors='ignore')[:1000]
        
        # JSON detection
        if content_str.strip().startswith(('{', '[')):
            try:
                json.loads(content_str.strip())
                return 'json'
            except json.JSONDecodeError:
                # Check for JSONL
                lines = content_str.strip().split('\n')
                if all(line.strip().startswith('{') for line in lines[:3] if line.strip()):
                    return 'jsonl'
        
        # CSV detection (fallback)
        if any(delim in content_str for delim in CONFIG['CSV_DELIMITERS']):
            return 'csv'
            
    except Exception:
        pass
    
    return None


# Backward compatibility aliases for tests
def _read_sample(path: str, sample_rows: int, hints: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Legacy alias for _read_sample_dataframe."""
    return _read_sample_dataframe(path, sample_rows, hints)

def _analyze_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Legacy function for structure analysis."""
    warnings = []
    
    # Check for duplicate columns
    if len(df.columns) != len(set(df.columns)):
        warnings.append("Duplicate column names detected")
    
    # Check for blank column names
    blank_cols = [col for col in df.columns if not str(col).strip()]
    if blank_cols:
        warnings.append(f"Blank column names found: {len(blank_cols)} columns")
    
    # Check for too many columns
    if len(df.columns) > 100:
        warnings.append(f"Large number of columns: {len(df.columns)}")
    
    # Check for all-null columns
    null_cols = [col for col in df.columns if df[col].isnull().all()]
    if null_cols:
        warnings.append(f"Columns with all null values: {len(null_cols)}")
    
    return {
        'total_columns': len(df.columns),
        'column_names': list(df.columns),
        'duplicate_columns': len(df.columns) != len(set(df.columns)),
        'blank_columns': len(blank_cols),
        'all_null_columns': len(null_cols),
        'warnings': warnings
    }

def _estimate_memory(file_size: int, sample_rows: int, num_columns: int) -> Dict[str, Any]:
    """Legacy function for memory estimation."""
    if sample_rows == 0:
        return {
            'estimated_memory_mb': 0,
            'recommendation': 'empty_file'
        }
    
    # Rough memory estimation (very approximate)
    estimated_memory_mb = (file_size / (1024 * 1024)) * 2  # Rough 2x multiplier
    
    recommendation = 'proceed'
    if estimated_memory_mb > 1000:  # > 1GB
        recommendation = 'large_memory_warning'
    elif estimated_memory_mb > 100:  # > 100MB
        recommendation = 'memory_watch'
    
    return {
        'estimated_memory_mb': estimated_memory_mb,
        'file_size_mb': file_size / (1024 * 1024),
        'recommendation': recommendation
    }

def _analyze_columns(df: pd.DataFrame) -> Dict[str, Any]:
    """Legacy function for column analysis."""
    column_types = {}
    warnings = []
    
    for col in df.columns:
        try:
            col_type = _infer_coarse_type(df[col])
            column_types[col] = col_type
        except Exception:
            column_types[col] = 'unknown'
            warnings.append(f"Could not analyze column '{col}'")
    
    return {
        'column_types': column_types,
        'type_summary': {t: sum(1 for ct in column_types.values() if ct == t) 
                        for t in set(column_types.values())},
        'warnings': warnings
    }

def _read_sample_dataframe(path: str, sample_rows: int, hints: Dict[str, Any]) -> Optional[pd.DataFrame]:
    """Read a sample DataFrame with format-specific logic."""
    detected_format = hints.get('format', 'csv')
    
    try:
        if detected_format == 'csv':
            return pd.read_csv(
                path,
                nrows=sample_rows,
                delimiter=hints.get('delimiter', ','),
                encoding=hints.get('encoding', 'utf-8'),
                on_bad_lines='skip'
            )
        elif detected_format == 'json':
            return pd.read_json(path, lines=False).head(sample_rows)
        elif detected_format == 'jsonl':
            return pd.read_json(path, lines=True).head(sample_rows)
        elif detected_format == 'parquet':
            return pd.read_parquet(path).head(sample_rows)
        elif detected_format == 'xlsx':
            return pd.read_excel(path, nrows=sample_rows)
            
    except Exception as e:
        logger.debug(f"Failed to read as {detected_format}: {e}")
        # Fallback to CSV
        try:
            return pd.read_csv(path, nrows=sample_rows, on_bad_lines='skip')
        except Exception:
            pass
    
    return None


def _infer_coarse_type(series: pd.Series) -> str:
    """Infer coarse data type from series."""
    if len(series.dropna()) == 0:
        return 'unknown'
    
    non_null = series.dropna()
    
    # Check pandas dtypes first
    if pd.api.types.is_integer_dtype(series):
        return 'integer'
    elif pd.api.types.is_float_dtype(series):
        return 'float'
    elif pd.api.types.is_datetime64_any_dtype(series):
        return 'datetime'
    elif pd.api.types.is_bool_dtype(series):
        return 'boolean'
    
    # For object types, sample and infer
    sample = non_null.astype(str).head(100)
    
    # Boolean patterns
    if all(PATTERNS['BOOLEAN'].match(val) for val in sample):
        return 'boolean'
    
    # Numeric patterns
    numeric_count = sum(1 for val in sample if PATTERNS['NUMERIC'].match(val.replace(',', '')))
    if numeric_count / len(sample) > 0.8:
        return 'numeric'
    
    # Datetime patterns
    datetime_count = sum(1 for val in sample 
                        if any(pattern.search(val) for pattern in PATTERNS['DATETIME']))
    if datetime_count / len(sample) > 0.7:
        return 'datetime'
    
    # Categorical vs text
    unique_ratio = len(sample.unique()) / len(sample)
    return 'categorical' if unique_ratio < 0.5 else 'text'


def _estimate_total_rows(path: str, sample_size: int, sample_rows_requested: int) -> int:
    """Estimate total rows based on file size and sample."""
    try:
        if sample_size >= sample_rows_requested:
            return sample_size  # We got all the data
            
        file_size = os.path.getsize(path)
        
        # Rough estimation based on file size
        # Average CSV row might be 100-500 bytes
        estimated_avg_row_size = max(100, file_size // max(sample_size * 10, 1000))
        return max(sample_size, file_size // estimated_avg_row_size)
        
    except Exception:
        return sample_size


def _collect_sample_warnings(df: pd.DataFrame) -> List[str]:
    """Collect warnings from sample data analysis."""
    warnings = []
    
    if len(df) < CONFIG['MIN_SAMPLE_THRESHOLD']:
        warnings.append(f"Small sample size: {len(df)} rows")
    
    # Check for high null percentages
    for col in df.columns:
        null_pct = (df[col].isnull().sum() / len(df)) * 100
        if null_pct > CONFIG['NULL_PERCENTAGE_WARNING']:
            warnings.append(f"Column '{col}' has {null_pct:.1f}% null values")
    
    # Check for duplicate column names
    if len(df.columns) != len(set(df.columns)):
        warnings.append("Duplicate column names detected")
    
    return warnings


def _decide_recommendation(report: Dict[str, Any]) -> Dict[str, Any]:
    """Generate recommendation based on preflight results."""
    # Extract key information
    structure = report['checks'].get('A5_structure', {})
    total_columns = structure.get('total_columns', 0)
    has_warnings = bool(report.get('warnings', []))
    
    # Decision logic
    if total_columns == 0:
        action = 'manual_review'
        reason = "No columns detected - file may be corrupted or unsupported format"
    elif total_columns > 50 or has_warnings:
        action = 'generate_metadata'
        reason = "Complex dataset or warnings detected - metadata template recommended"
    else:
        action = 'analyze_infer_only'
        reason = "Simple dataset suitable for direct analysis with auto-inference"
    
    return {
        'action': action,
        'reason': reason,
        'next_steps': _get_next_steps(action)
    }


def _get_next_steps(action: str) -> List[str]:
    """Get recommended next steps based on action."""
    steps_map = {
        'analyze_infer_only': [
            "Run: funimputer analyze -d <file> (auto-inference mode)",
            "Review imputation recommendations",
            "Apply suggested methods"
        ],
        'generate_metadata': [
            "Run: funimputer init -d <file> (generate metadata template)",
            "Review and customize metadata.csv",
            "Run: funimputer analyze -d <file> -m metadata.csv"
        ],
        'manual_review': [
            "Manually inspect the data file",
            "Check file format and encoding",
            "Consider data cleaning or format conversion"
        ]
    }
    return steps_map.get(action, ["Review preflight report for details"])


def format_preflight_report(report: Dict[str, Any]) -> str:
    """Format preflight report for human reading."""
    lines = [
        f"Preflight Report: {report.get('path', 'Unknown')}",
        f"Status: {report.get('status', 'Unknown')} (Exit Code: {report.get('exit_code', 'Unknown')})",
        ""
    ]
    
    # Add warnings if any
    if report.get('warnings'):
        lines.append("WARNINGS:")
        for warning in report['warnings']:
            lines.append(f"  • {warning}")
        lines.append("")
    
    # Add recommendation
    rec = report.get('recommendation', {})
    if rec.get('action'):
        lines.append(f"RECOMMENDATION: {rec['action']}")
        if rec.get('reason'):
            lines.append(f"Reason: {rec['reason']}")
        if rec.get('next_steps'):
            lines.append("Next Steps:")
            for step in rec['next_steps']:
                lines.append(f"  • {step}")
        lines.append("")
    
    # Add detailed checks
    checks = report.get('checks', {})
    if checks:
        lines.append("DETAILED CHECKS:")
        for check_name, result in checks.items():
            lines.append(f"  {check_name}: {'✓' if not result.get('error') else '✗'}")
            if result.get('error'):
                lines.append(f"    Error: {result['error']}")
    
    return '\n'.join(lines)