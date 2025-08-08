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

# Constants
DEFAULT_SAMPLE_ROWS = 2000
DEFAULT_MAX_SNIFF_BYTES = 65536
SUPPORTED_FORMATS = ["csv", "json", "jsonl", "parquet", "xlsx"]
SUPPORTED_COMPRESSIONS = ["none", "gz", "zip"]


def run_preflight(
    path: str,
    *,
    sample_rows: int = DEFAULT_SAMPLE_ROWS,
    max_sniff_bytes: int = DEFAULT_MAX_SNIFF_BYTES,
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
    hints = hints or {}
    report = {
        "status": "ok",
        "file": {},
        "encoding": {},
        "structure": {},
        "memory": {},
        "sample": {},
        "columns": [],
        "recommendation": "analyze_infer_only",
        "hints": [],
    }

    try:
        # A1. Path & size checks
        file_info = _check_path_and_size(path)
        if file_info["error"]:
            report["status"] = "hard_error"
            report["file"] = file_info
            return report
        report["file"] = file_info

        # A2. Format & compression detection
        format_info = _detect_format_and_compression(path, max_sniff_bytes)
        report["file"].update(format_info)

        # A3. Encoding probe
        encoding_info = _probe_encoding(path, hints.get("encoding"))
        report["encoding"] = encoding_info

        # A4. CSV dialect detection (CSV only)
        csv_dialect = None
        if report["file"]["format"] == "csv":
            csv_dialect = _sniff_csv_dialect(path, encoding_info["selected"], hints)
            if csv_dialect:
                report["csv_dialect"] = csv_dialect

        # A5-A8. Sample-based analysis
        sample_data = _read_sample(
            path,
            report["file"]["format"],
            report["file"]["compression"],
            encoding_info["selected"],
            csv_dialect,
            sample_rows,
        )

        if sample_data is None:
            report["status"] = "hard_error"
            report["sample"] = {"error": "Unable to read sample data"}
            return report

        # A5. Structure sanity
        structure_info = _analyze_structure(sample_data)
        report["structure"] = structure_info

        # A6. Memory estimation
        memory_info = _estimate_memory(
            report["file"]["size_bytes"], len(sample_data), sample_data.shape[1]
        )
        report["memory"] = memory_info

        # A7. Type inference (coarse)
        # A8. Nulls snapshot
        columns_info = _analyze_columns(sample_data)
        report["columns"] = columns_info

        # Sample metadata
        report["sample"] = {
            "rows_sampled": len(sample_data),
            "warnings": _collect_sample_warnings(sample_data, columns_info),
        }

        # Decision rule
        recommendation, hints_list = _decide_recommendation(
            structure_info, columns_info, csv_dialect
        )
        report["recommendation"] = recommendation
        report["hints"] = hints_list

        # Set warning status if needed
        if (
            structure_info.get("issues")
            or memory_info.get("suggest_chunked")
            or report["sample"]["warnings"]
        ):
            report["status"] = "ok_with_warnings"

    except FileNotFoundError as e:
        logger.error(f"Preflight failed - file not found: {e}")
        report["status"] = "hard_error"
        report["file"] = {"error": f"File not found: {path}"}
        report["error"] = str(e)
    except PermissionError as e:
        logger.error(f"Preflight failed - permission denied: {e}")
        report["status"] = "hard_error"
        report["file"] = {"error": f"Permission denied: {path}"}
        report["error"] = str(e)
    except UnicodeDecodeError as e:
        logger.error(f"Preflight failed - encoding issue: {e}")
        report["status"] = "hard_error"
        report["encoding"] = {"error": f"Encoding error: {e}"}
        report["error"] = str(e)
    except pd.errors.EmptyDataError as e:
        logger.error(f"Preflight failed - empty data: {e}")
        report["status"] = "hard_error"
        report["sample"] = {"error": "Empty data file"}
        report["error"] = str(e)
    except pd.errors.ParserError as e:
        logger.error(f"Preflight failed - parse error: {e}")
        report["status"] = "ok_with_warnings"  # Can still provide recommendations
        report["sample"] = {"error": f"Parse error: {e}"}
        report["hints"] = ["File has parsing issues - consider fixing format"]
    except (OSError, IOError) as e:
        logger.error(f"Preflight failed - I/O error: {e}")
        report["status"] = "hard_error"
        report["file"] = {"error": f"I/O error: {e}"}
        report["error"] = str(e)
    except Exception as e:
        logger.error(f"Preflight failed - unexpected error: {e}")
        report["status"] = "hard_error"
        report["error"] = f"Unexpected error: {e}"
        # Add debugging info for unexpected errors
        import traceback

        logger.debug(f"Full traceback: {traceback.format_exc()}")

    return report


def _check_path_and_size(path: str) -> Dict[str, Any]:
    """Check if file exists, is readable, and non-zero."""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return {"error": f"File not found: {path}"}

        if not path_obj.is_file():
            return {"error": f"Not a file: {path}"}

        size = path_obj.stat().st_size
        if size == 0:
            return {"error": f"Empty file: {path}"}

        # Test readability
        try:
            with open(path, "rb") as f:
                f.read(1)
        except PermissionError:
            return {"error": f"Cannot read file: {path}"}

        return {"path": str(path_obj.absolute()), "size_bytes": size, "error": None}
    except Exception as e:
        return {"error": f"Path check failed: {e}"}


def _detect_format_and_compression(path: str, max_bytes: int) -> Dict[str, str]:
    """Detect file format and compression."""
    path_obj = Path(path)

    # Check compression from extension
    compression = "none"
    stem = path_obj.name
    if stem.endswith(".gz"):
        compression = "gz"
        stem = stem[:-3]  # Remove .gz
    elif stem.endswith(".zip"):
        compression = "zip"
        stem = stem[:-4]  # Remove .zip

    # Detect format from extension
    format_detected = "csv"  # default
    if stem.endswith(".json"):
        format_detected = "json"
    elif stem.endswith(".jsonl") or stem.endswith(".ndjson"):
        format_detected = "jsonl"
    elif stem.endswith(".parquet"):
        format_detected = "parquet"
    elif stem.endswith((".xlsx", ".xls")):
        format_detected = "xlsx"
    elif stem.endswith(".csv"):
        format_detected = "csv"

    # Verify by reading a sample if uncertain
    try:
        if compression == "gz":
            with gzip.open(path, "rb") as f:
                sample = f.read(max_bytes)
        elif compression == "zip":
            with zipfile.ZipFile(path, "r") as zf:
                # Use first file in zip
                names = zf.namelist()
                if names:
                    with zf.open(names[0]) as f:
                        sample = f.read(max_bytes)
                else:
                    sample = b""
        else:
            with open(path, "rb") as f:
                sample = f.read(max_bytes)

        # Simple format validation
        if sample.startswith(b"PAR1") or sample.endswith(b"PAR1"):
            format_detected = "parquet"
        elif sample.startswith((b"PK\x03\x04", b"PK\x05\x06")):
            # Excel files start with ZIP signature
            if stem.endswith((".xlsx", ".xls")):
                format_detected = "xlsx"
    except Exception:
        # If we can't read sample, trust the extension
        pass

    return {"format": format_detected, "compression": compression}


def _probe_encoding(path: str, hint: Optional[str] = None) -> Dict[str, Any]:
    """Probe file encoding."""
    encodings_to_try = []
    if hint:
        encodings_to_try.append(hint)
    encodings_to_try.extend(["utf-8", "latin-1", "cp1252"])

    # Remove duplicates while preserving order
    seen = set()
    encodings_to_try = [x for x in encodings_to_try if not (x in seen or seen.add(x))]

    selected = "utf-8"  # default
    tried = []

    for encoding in encodings_to_try:
        try:
            with open(path, "r", encoding=encoding) as f:
                f.read(1024)  # Try to read a small chunk
            selected = encoding
            tried.append(encoding)
            break
        except (UnicodeDecodeError, UnicodeError):
            tried.append(encoding)
            continue
        except Exception:
            tried.append(encoding)
            continue

    return {"selected": selected, "tried": tried}


def _sniff_csv_dialect(
    path: str, encoding: str, hints: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Detect CSV dialect."""
    try:
        with open(path, "r", encoding=encoding) as f:
            sample = f.read(8192)  # Read sample for dialect detection

        # Use pandas to detect delimiter and other parameters
        from io import StringIO

        # Try user hints first
        delimiter = hints.get("delimiter", ",")
        has_header = not hints.get("no_header", False)

        # Simple validation
        try:
            test_df = pd.read_csv(StringIO(sample), delimiter=delimiter, nrows=5)
            if len(test_df.columns) < 2:
                # Try other delimiters
                for alt_delim in [";", "\t", "|"]:
                    try:
                        test_df2 = pd.read_csv(
                            StringIO(sample), delimiter=alt_delim, nrows=5
                        )
                        if len(test_df2.columns) > len(test_df.columns):
                            delimiter = alt_delim
                            break
                    except:
                        continue
        except:
            pass

        # Detect quote character (simple heuristic)
        quotechar = '"'
        if sample.count('"') > sample.count("'") * 2:
            quotechar = '"'
        elif sample.count("'") > sample.count('"') * 2:
            quotechar = "'"

        return {
            "delimiter": delimiter,
            "quotechar": quotechar,
            "has_header": has_header,
        }
    except Exception as e:
        logger.warning(f"CSV dialect detection failed: {e}")
        return None


def _read_sample(
    path: str,
    format_type: str,
    compression: str,
    encoding: str,
    csv_dialect: Optional[Dict],
    sample_rows: int,
) -> Optional[pd.DataFrame]:
    """Read a sample of the data."""
    file_obj = None
    zf = None

    try:
        if format_type == "csv":
            # Handle compression
            if compression == "gz":
                try:
                    file_obj = gzip.open(path, "rt", encoding=encoding)
                except (gzip.BadGzipFile, OSError) as e:
                    logger.warning(f"Failed to open gzipped file: {e}")
                    return None
            elif compression == "zip":
                try:
                    zf = zipfile.ZipFile(path)
                    names = zf.namelist()
                    if not names:
                        logger.warning("ZIP file contains no files")
                        return None
                    file_obj = zf.open(names[0])
                except (zipfile.BadZipFile, KeyError) as e:
                    logger.warning(f"Failed to open ZIP file: {e}")
                    return None
            else:
                try:
                    file_obj = open(path, "r", encoding=encoding)
                except (UnicodeDecodeError, PermissionError) as e:
                    logger.warning(f"Failed to open file: {e}")
                    return None

            try:
                delimiter = csv_dialect.get("delimiter", ",") if csv_dialect else ","
                has_header = (
                    csv_dialect.get("has_header", True) if csv_dialect else True
                )

                df = pd.read_csv(
                    file_obj,
                    delimiter=delimiter,
                    nrows=sample_rows,
                    header=0 if has_header else None,
                    low_memory=False,
                    on_bad_lines="skip",  # Skip problematic lines
                )
                return df
            except pd.errors.EmptyDataError:
                logger.warning("CSV file is empty")
                return None
            except pd.errors.ParserError as e:
                logger.warning(f"CSV parsing error: {e}")
                # Try fallback approach
                try:
                    df = pd.read_csv(
                        file_obj,
                        delimiter=delimiter,
                        nrows=sample_rows,
                        header=0 if has_header else None,
                        low_memory=False,
                        on_bad_lines="skip",
                        engine="python",  # More forgiving parser
                    )
                    return df
                except Exception:
                    return None

        elif format_type == "json":
            try:
                df = pd.read_json(path, lines=False, encoding=encoding)
                return df.head(sample_rows)
            except (ValueError, UnicodeDecodeError) as e:
                logger.warning(f"JSON parsing error: {e}")
                return None

        elif format_type == "jsonl":
            try:
                df = pd.read_json(path, lines=True, encoding=encoding)
                return df.head(sample_rows)
            except (ValueError, UnicodeDecodeError) as e:
                logger.warning(f"JSONL parsing error: {e}")
                return None

        elif format_type == "parquet":
            try:
                df = pd.read_parquet(path)
                return df.head(sample_rows)
            except Exception as e:
                logger.warning(f"Parquet reading error: {e}")
                return None

        elif format_type == "xlsx":
            try:
                df = pd.read_excel(path)
                return df.head(sample_rows)
            except Exception as e:
                logger.warning(f"Excel reading error: {e}")
                return None

    except Exception as e:
        logger.error(f"Unexpected error reading sample: {e}")
        return None

    finally:
        # Clean up file handles
        if file_obj and hasattr(file_obj, "close"):
            try:
                file_obj.close()
            except Exception:
                pass
        if zf:
            try:
                zf.close()
            except Exception:
                pass

    return None


def _analyze_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze DataFrame structure for issues."""
    issues = []

    # Check for duplicate column names
    duplicates = df.columns[df.columns.duplicated()].tolist()
    if duplicates:
        issues.append(f"duplicate_names: {', '.join(duplicates)}")

    # Check for blank column names
    blank_cols = [
        i
        for i, col in enumerate(df.columns)
        if not str(col).strip() or str(col).startswith("Unnamed:")
    ]
    if blank_cols:
        issues.append(f"blank_names: columns {blank_cols}")

    # Check for very wide data
    if len(df.columns) > 1000:
        issues.append(f"too_many_columns: {len(df.columns)}")

    # Check for inconsistent row length (shouldn't happen with pandas, but just in case)
    if df.shape[0] > 0 and df.isnull().all().all():
        issues.append("all_null_data")

    return {
        "num_columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "issues": issues,
    }


def _estimate_memory(
    file_size_bytes: int, sample_rows: int, num_columns: int
) -> Dict[str, Any]:
    """Estimate memory usage for full file."""
    if sample_rows == 0:
        return {"estimated_read_mb": 0, "suggest_chunked": False}

    # Rough estimation: assume 8 bytes per cell on average
    bytes_per_cell = 8
    estimated_total_cells = (
        (file_size_bytes / sample_rows) * num_columns if sample_rows > 0 else 0
    )
    estimated_mb = (estimated_total_cells * bytes_per_cell) / (1024 * 1024)

    # Suggest chunking for files > 500MB estimated memory
    suggest_chunked = estimated_mb > 500

    return {
        "estimated_read_mb": round(estimated_mb, 1),
        "suggest_chunked": suggest_chunked,
    }


def _analyze_columns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Analyze each column for type and missing data."""
    columns_info = []

    for col in df.columns:
        series = df[col]

        # Calculate missing percentage
        missing_pct = series.isnull().sum() / len(series) if len(series) > 0 else 0

        # Infer type (coarse)
        inferred_type = _infer_coarse_type(series)

        columns_info.append(
            {
                "name": str(col),
                "inferred_type": inferred_type,
                "missing_pct_sample": round(missing_pct, 3),
            }
        )

    return columns_info


def _infer_coarse_type(series: pd.Series) -> str:
    """Coarse type inference for preflight."""
    if len(series) == 0:
        return "string"

    # Drop nulls for type checking
    non_null = series.dropna()
    if len(non_null) == 0:
        return "string"

    # Check for boolean
    if (
        series.dtype == bool
        or non_null.map(lambda x: str(x).lower())
        .isin(["true", "false", "1", "0", "yes", "no"])
        .all()
    ):
        return "boolean"

    # Check for integer
    if pd.api.types.is_integer_dtype(series):
        return "integer"

    # Check for float
    if pd.api.types.is_float_dtype(series):
        return "float"

    # Check for datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Try to parse as datetime
    try:
        pd.to_datetime(non_null.head(10), errors="raise")
        return "datetime"
    except:
        pass

    # Check for categorical (low cardinality)
    if pd.api.types.is_object_dtype(series):
        unique_count = non_null.nunique()
        if unique_count <= 20 or unique_count / len(non_null) < 0.5:
            return "categorical"

    return "string"


def _collect_sample_warnings(df: pd.DataFrame, columns_info: List[Dict]) -> List[str]:
    """Collect warnings from sample analysis."""
    warnings = []

    # Check for mixed types within columns
    for col_info in columns_info:
        col_name = col_info["name"]
        if col_name in df.columns:
            series = df[col_name].dropna()
            if len(series) > 1:
                # Simple mixed type detection
                types_seen = set()
                for val in series.head(20):  # Check first 20 values
                    val_type = type(val).__name__
                    types_seen.add(val_type)

                if len(types_seen) > 2:  # Allow for some type variety
                    warnings.append(f"mixed_types in {col_name}")

    # Check for very high missing data
    high_missing_cols = [
        col["name"] for col in columns_info if col["missing_pct_sample"] > 0.95
    ]
    if high_missing_cols:
        warnings.append(f"high_missing_data: {', '.join(high_missing_cols)}")

    return warnings


def _decide_recommendation(
    structure_info: Dict, columns_info: List[Dict], csv_dialect: Optional[Dict]
) -> Tuple[str, List[str]]:
    """Decide whether to recommend metadata generation or direct analysis."""
    hints = []

    # Count problematic conditions
    issues_count = 0

    # Structure issues
    if structure_info.get("issues"):
        issues_count += len(structure_info["issues"])
        hints.append("Fix column name issues before analysis")

    # No header detected
    if csv_dialect and not csv_dialect.get("has_header", True):
        issues_count += 1
        hints.append("--no-header flag may be needed")

    # Many ambiguous types (>25% of columns)
    ambiguous_types = sum(1 for col in columns_info if col["inferred_type"] == "string")
    ambiguous_ratio = ambiguous_types / len(columns_info) if columns_info else 0

    if ambiguous_ratio > 0.25:
        issues_count += 1
        hints.append("Many columns have ambiguous types - metadata would help")

    # Very high missing data columns
    high_missing_count = sum(
        1 for col in columns_info if col["missing_pct_sample"] > 0.8
    )
    if high_missing_count > 0:
        issues_count += 1
        hints.append(f"{high_missing_count} columns have >80% missing data")

    # Decision rule
    if issues_count >= 2 or structure_info.get("issues"):
        recommendation = "generate_metadata"
        if not hints:
            hints.append("Generate metadata template first for better analysis")
    else:
        recommendation = "analyze_infer_only"

    return recommendation, hints


def format_preflight_report(report: Dict[str, Any]) -> str:
    """Format preflight report for display."""
    lines = []
    lines.append("🔍 PREFLIGHT REPORT")
    lines.append("=" * 50)

    # Status
    status_emoji = {"ok": "✅", "ok_with_warnings": "⚠️", "hard_error": "❌"}
    lines.append(
        f"Status: {status_emoji.get(report['status'], '❓')} {report['status'].upper()}"
    )

    # File info
    file_info = report.get("file", {})
    if file_info:
        lines.append(f"File: {file_info.get('path', 'N/A')}")
        size_mb = file_info.get("size_bytes", 0) / (1024 * 1024)
        lines.append(f"Size: {size_mb:.1f} MB ({file_info.get('format', 'unknown')})")

        if file_info.get("compression") != "none":
            lines.append(f"Compression: {file_info.get('compression')}")

    # Structure
    structure = report.get("structure", {})
    if structure:
        lines.append(f"Columns: {structure.get('num_columns', 0)}")
        if structure.get("issues"):
            lines.append(f"Issues: {', '.join(structure['issues'])}")

    # Recommendation
    rec = report.get("recommendation", "")
    lines.append(f"Recommendation: {rec.replace('_', ' ').title()}")

    # Hints
    hints = report.get("hints", [])
    if hints:
        lines.append("Hints:")
        for hint in hints:
            lines.append(f"  • {hint}")

    return "\n".join(lines)
