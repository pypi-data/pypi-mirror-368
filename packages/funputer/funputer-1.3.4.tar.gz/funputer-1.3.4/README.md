# FunPuter v1.3.3 - Intelligent Imputation Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/funputer.svg)](https://pypi.org/project/funputer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/coverage-71%25-brightgreen.svg)](#test-coverage)

**Production-ready intelligent imputation analysis with automatic data validation and metadata inference.**

FunPuter analyzes your data and suggests the best imputation methods based on:
- 🤖 **15 metadata fields automatically inferred**
- 🔍 **Missing data mechanisms** (MCAR, MAR, MNAR detection)
- 📊 **Data types and statistical properties**  
- ⚡ **Metadata constraints** (nullable, allowed_values, max_length validation)
- 🛡️ **Automatic data validation** and recommendations
- 🎯 **Adaptive thresholds** based on your dataset characteristics

## 🚀 Quick Start

### Installation
```bash
pip install funputer
```

### 30-Second Demo

**🤖 Auto-Inference Mode (Zero Configuration!)**
```python
import funputer

# Just point to your CSV - FunPuter figures out everything automatically!
suggestions = funputer.analyze_imputation_requirements("your_data.csv")

# Get intelligent suggestions
for suggestion in suggestions:
    if suggestion.missing_count > 0:
        print(f"📊 {suggestion.column_name}: {suggestion.proposed_method}")
        print(f"   Confidence: {suggestion.confidence_score:.3f}")
        print(f"   Reason: {suggestion.rationale}")
        print(f"   Missing: {suggestion.missing_count} ({suggestion.missing_percentage:.1f}%)")
```

**📋 Production Mode (Full Control)**
```python
import funputer
from funputer.models import ColumnMetadata

# Define your data structure with constraints
metadata = [
    ColumnMetadata('customer_id', 'integer', unique_flag=True),
    ColumnMetadata('age', 'integer', min_value=18, max_value=100),
    ColumnMetadata('income', 'float', min_value=0),
    ColumnMetadata('category', 'categorical', allowed_values='A,B,C'),
]

# Get production-grade suggestions
suggestions = funputer.analyze_dataframe(your_dataframe, metadata)
```

**🖥️ Command Line Interface**
```bash
# Auto-inference - easiest way
funputer analyze -d your_data.csv

# Production analysis with metadata
funputer analyze -d your_data.csv -m metadata.csv --verbose

# Data quality check first
funputer preflight -d your_data.csv

# Generate metadata template
funputer init -d your_data.csv -o metadata.csv
```

## 🚨 **IMPORTANT: v1.3.0 Breaking Change**

**🎯 Consistent Naming**: Starting with v1.3.0, all imports and CLI commands use consistent `funputer` naming:

```python
# ✅ NEW (v1.3.0+): Consistent naming
import funputer
funputer.analyze_imputation_requirements("data.csv")
```

```bash
# ✅ NEW CLI command (v1.3.0+)
funputer analyze -d data.csv
```

**🔄 Migration**: For backward compatibility, old imports still work with deprecation warnings:

```python
# ⚠️ DEPRECATED (still works but shows warning)
import funimpute
# Old funimputer CLI command also still works
```

**📅 Timeline**: Deprecated imports will be removed in v2.0.0. Please update your code!

## 🎯 Enhanced Features (v1.3.0)

**What's New in v1.3.0:**
- 🎯 **Consistent Naming**: All imports and CLI use `funputer` (backward compatible)
- 🔄 **JSON Metadata Support**: SimpleImputationAnalyzer now handles both CSV and JSON metadata formats
- 📋 **Enhanced Documentation**: Updated examples and migration guides

**Previous Features (v1.2.1):**
- 🚨 **Data Validation System**: Comprehensive checks that run before analysis to prevent crashes
- 🔍 **Smart Auto-Inference**: Intelligent metadata detection with confidence scoring
- ⚡ **Constraint Validation**: Real-time nullable, allowed_values, and max_length checking
- 🎯 **Enhanced Proposals**: Metadata-aware imputation method selection
- 🛡️ **Exception Detection**: Comprehensive constraint violation handling
- 📈 **Improved Confidence**: Dynamic scoring based on metadata compliance
- 🧹 **Warning Suppression**: Clean output with optimized pandas datetime parsing
- ✅ **Quality Assurance**: 71% overall test coverage with comprehensive test suite

## 🚨 Data Validation System (NEW!)

**Fast validation to prevent crashes and guide your workflow**

### What the Validation System Does
- **Runs automatically** before `init` and `analyze` commands
- **Comprehensive checks**: file access, format detection, encoding, structure, memory estimation
- **Advisory recommendations**: "generate metadata first" vs "analyze now"
- **Zero crashes**: Catches problems before they break your workflow
- **Backward compatible**: All existing commands work exactly as before

### Independent Usage
```bash
# Basic validation check
funputer preflight -d your_data.csv

# With custom options
funputer preflight -d data.csv --sample-rows 5000 --encoding utf-8

# JSON report output
funputer preflight -d data.csv --json-out report.json
```

### Exit Codes
- **0**: ✅ Ready for analysis
- **2**: ⚠️ OK with warnings (can proceed)
- **10**: ❌ Hard error (cannot proceed)

### Example Output
```bash
🔍 VALIDATION REPORT
==================================================
Status: ✅ OK
File: data.csv
Size: 2.5 MB (csv)  
Columns: 12
Recommendation: Analyze Infer Only
```

FunPuter now supports comprehensive metadata fields that actively influence imputation recommendations:

### Metadata Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `column_name` | string | Column identifier | `"age"` |
| `data_type` | string | Data type (integer, float, string, categorical, datetime) | `"integer"` |
| `nullable` | boolean | Allow null values | `false` |
| `min_value` | number | Minimum allowed value | `0` |
| `max_value` | number | Maximum allowed value | `120` |
| `max_length` | integer | Maximum string length | `50` |
| `allowed_values` | string | Comma-separated list of allowed values | `"A,B,C"` |
| `unique_flag` | boolean | Require unique values | `true` |
| `dependent_column` | string | Column dependencies | `"age"` |
| `business_rule` | string | Custom validation rules | `"Must be positive"` |
| `description` | string | Human-readable description | `"User age in years"` |

### 🛠️ Creating Metadata

**Method 1: CLI Template Generation**
```bash
# Generate a metadata template from your data
funputer init -d data.csv -o metadata.csv

# Edit the generated file to add constraints
# Then analyze with enhanced metadata
funputer analyze -d data.csv -m metadata.csv
```

**Method 2: Manual CSV Creation**
```csv
# metadata.csv
# column_name,data_type,nullable,min_value,max_value,max_length,allowed_values,unique_flag,dependent_column,business_rule,description
user_id,integer,false,,,50,,true,,,"Unique user identifier"
age,integer,false,0,120,,,,,Must be positive,"User age in years"
income,float,true,0,,,,,age,Higher with age,"Annual income in USD"
category,categorical,false,,,10,"A,B,C",,,,"User category classification"
email,string,true,,,255,,true,,,"User email address"
```

### 🎯 Metadata in Action

**Example 1: Nullable Constraints**
```python
# When nullable=False but data has missing values
metadata = ColumnMetadata(
    column_name="age",
    data_type="integer",
    nullable=False,
    min_value=0,
    max_value=120
)

# FunPuter will:
# - Detect nullable constraint violations
# - Recommend immediate data quality fixes
# - Lower confidence score due to constraint violations
```

**Example 2: Allowed Values**
```python
# For categorical data with specific allowed values
metadata = ColumnMetadata(
    column_name="status",
    data_type="categorical",
    allowed_values="active,inactive,pending"
)

# FunPuter will:
# - Validate all values against allowed list
# - Recommend mode imputation using only allowed values
# - Increase confidence when data respects constraints
```

**Example 3: String Length Constraints**
```python
# For string data with length limits
metadata = ColumnMetadata(
    column_name="username",
    data_type="string",
    max_length=20,
    unique_flag=True
)

# FunPuter will:
# - Check string lengths against max_length
# - Recommend imputation respecting length limits
# - Consider uniqueness requirements in recommendations
```

### 📊 Enhanced Analysis Results

```python
# Results include comprehensive imputation analysis
for suggestion in suggestions:
    print(f"Column: {suggestion.column_name}")
    print(f"Method: {suggestion.proposed_method}")
    print(f"Confidence: {suggestion.confidence_score:.3f}")
    print(f"Rationale: {suggestion.rationale}")
    print(f"Missing: {suggestion.missing_count} ({suggestion.missing_percentage:.1f}%)")
    
    # Outlier information when relevant
    if suggestion.outlier_count > 0:
        print(f"Outliers: {suggestion.outlier_count} ({suggestion.outlier_percentage:.1f}%)")
        print(f"Outlier handling: {suggestion.outlier_handling}")
```

## 🔍 Confidence-Score Heuristics

FunPuter assigns a **`confidence_score`** (range **0 – 1**) to every imputation recommendation.  The value is a transparent, rule-based estimate of how reliable the proposed method is, **not** a formal statistical uncertainty.  Two calculators are used:

### Base heuristic
When only column-level data is available (no full DataFrame), the score is computed as follows:

| Signal | Condition | Δ Score |
|--------|-----------|---------|
| **Starting value** | | **0.50** |
| Missing % | `< 5 %` +0.20 • `5 – 20 %` +0.10 • `> 50 %` −0.20 |
| Mechanism | MCAR (weak evidence) +0.10 • MAR (related cols) +0.05 • MNAR/UNKNOWN −0.10 |
| Outliers | `< 5 %` +0.05 • `> 20 %` −0.10 |
| Metadata constraints | `allowed_values` (categorical/string) +0.10 • `max_length` (string) +0.05 |
| Nullable constraint | `nullable=False` **with** missing −0.15 • **without** missing +0.05 |
| Data-quality checks | Strings within `max_length` +0.05 • Categorical values inside `allowed_values` + *(valid_ratio × 0.10)* |

The final score is clipped to the **[0.10, 1.00]** interval.

### Adaptive variant
When the analyzer receives the full DataFrame **and** complete metadata, it builds dataset-specific thresholds using `AdaptiveThresholds` and applies `calculate_adaptive_confidence_score`:

* Adaptive missing/outlier thresholds (based on row-count, variability, etc.)
* An additional adjustment factor (−0.30 … +0.30) reflecting dataset characteristics

This yields a context-aware score that remains interpretable yet sensitive to each dataset.

### Future work
For maximum transparency and speed we use heuristics today.  Future releases may include probabilistic or conformal approaches (e.g., multiple-imputation variance or ensemble uncertainty) to provide statistically grounded confidence estimates.

## 🚀 Advanced Usage

### Programmatic Metadata Creation
```python
from funputer.models import ColumnMetadata

metadata = [
    ColumnMetadata(
        column_name="product_code",
        data_type="string",
        max_length=10,
        allowed_values="A1,A2,B1,B2",
        nullable=False,
        description="Product classification code"
    ),
    ColumnMetadata(
        column_name="price",
        data_type="float",
        min_value=0,
        max_value=10000,
        business_rule="Must be non-negative"
    )
]

# Analyze with custom metadata
import pandas as pd
data = pd.read_csv("products.csv")
from funputer.simple_analyzer import SimpleImputationAnalyzer

analyzer = SimpleImputationAnalyzer()
results = analyzer.analyze_dataframe(data, metadata)
```

### CLI Usage with Enhanced Metadata & PREFLIGHT
```bash
# PREFLIGHT runs automatically before init/analyze
funputer init -d products.csv -o products_metadata.csv
# 🔍 Preflight Check: ✅ OK - File validated, ready for processing

# Edit metadata.csv to add constraints, then:
funputer analyze -d products.csv -m products_metadata.csv -o results.csv
# 🔍 Preflight Check: ✅ OK - Recommendation: Analyze Now

# Run standalone preflight validation
funputer preflight -d products.csv --json-out validation_report.json

# Disable preflight if needed (not recommended)
export FUNPUTER_PREFLIGHT=off
funputer analyze -d products.csv

# Results are automatically saved in CSV format for easy viewing
```

## 📋 Requirements

- **Python**: 3.9 or higher
- **Dependencies**: pandas, numpy, scipy, scikit-learn

## 🔧 Installation from Source

```bash
git clone https://github.com/RajeshRamachander/funputer.git
cd funputer
pip install -e .
```

## 📚 Comprehensive Examples

FunPuter comes with extensive real-world examples covering every feature:

### 🎯 **Quick Start Examples**
- **[quick_start_guide.py](examples/quick_start_guide.py)** - Get started in 5 minutes with common patterns
- **[comprehensive_usage_guide.py](examples/comprehensive_usage_guide.py)** - Every feature demonstrated
- **[cli_examples.sh](examples/cli_examples.sh)** - Complete CLI usage guide

### 🏭 **Industry Examples**
- **[real_world_examples.py](examples/real_world_examples.py)** - Production scenarios across industries:
  - 🛒 **E-commerce Customer Analytics** - Customer behavior, churn prediction
  - 🏥 **Healthcare Patient Records** - Clinical data with regulatory constraints  
  - 💰 **Financial Risk Assessment** - Credit scoring, loan applications
  - 📢 **Marketing Campaign Analysis** - ROI optimization, A/B testing
  - 🌡️ **IoT Sensor Data** - Time series, equipment monitoring

### 📊 **Usage Patterns**

**Auto-Inference (Zero Configuration)**
```python
# Perfect for data exploration and prototyping
suggestions = funputer.analyze_imputation_requirements("mystery_data.csv")
```

**Production Mode (Full Control)**
```python
# Enterprise-grade with constraint validation
from funputer.models import ColumnMetadata, AnalysisConfig

metadata = [
    ColumnMetadata('customer_id', 'integer', unique_flag=True, nullable=False),
    ColumnMetadata('age', 'integer', min_value=18, max_value=100),
    ColumnMetadata('income', 'float', dependent_column='age', 
                   business_rule='Income correlates with age'),
    ColumnMetadata('category', 'categorical', allowed_values='A,B,C,D')
]

config = AnalysisConfig(missing_percentage_threshold=0.25, skip_columns=['id'])
suggestions = funputer.analyze_dataframe(df, metadata, config)
```

**CLI Automation**
```bash
# Batch processing workflow
for file in data/*.csv; do
    funputer preflight "$file" && \
    funputer analyze -d "$file" --output "results/$(basename "$file" .csv)_plan.csv"
done
```

### 🎓 **Learning Path**

1. **Start Here**: `quick_start_guide.py` - Master the basics in 5 minutes
2. **Go Deeper**: `comprehensive_usage_guide.py` - Learn every feature  
3. **Real World**: `real_world_examples.py` - See industry applications
4. **CLI Mastery**: `cli_examples.sh` - Automate your workflows
5. **Production**: Use the patterns in your specific domain

### 💡 **Pro Tips**

- **Exploration**: Use auto-inference for quick insights
- **Production**: Always use explicit metadata with constraints
- **Automation**: CLI is perfect for CI/CD and batch processing
- **Validation**: Run preflight checks before expensive analysis
- **Performance**: Skip unnecessary columns, tune thresholds appropriately

## 📚 Documentation

- **Examples Directory**: [examples/](examples/) - Comprehensive usage examples
- **API Reference**: See docstrings and type hints in the code
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history and features

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Focus**: Get intelligent imputation recommendations with enhanced metadata support, not complex infrastructure.