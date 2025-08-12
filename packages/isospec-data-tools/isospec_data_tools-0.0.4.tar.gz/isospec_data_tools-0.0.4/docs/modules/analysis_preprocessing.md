# Analysis Preprocessing Module

The preprocessing module provides comprehensive data normalization, transformation, and validation tools specifically designed for omics data analysis, with specialized support for metabolomics and glycomics workflows.

## Overview

The preprocessing module consists of several key components:

1. **Normalization Methods**: Total abundance, median quotient, and other omics-specific normalizations
2. **Missing Value Imputation**: QC-based imputation and statistical methods
3. **Data Transformations**: Log transformations, categorical encoding, and filtering
4. **Data Validation**: Quality checks and validation utilities
5. **Pipeline Management**: Structured preprocessing workflows

## Quick Start

### Basic Normalization

```python
from isospec_data_tools.analysis import (
    total_abundance_normalization,
    median_quotient_normalization,
    impute_missing_values
)

# Total abundance normalization
normalized_data = total_abundance_normalization(
    data=raw_data,
    prefix="FT-",  # Feature column prefix
    inplace=False  # Return new DataFrame
)

# Median quotient normalization
mqn_normalized = median_quotient_normalization(
    data=raw_data,
    prefix="FT-",
    reference_samples=qc_mask  # Use QC samples as reference
)

# QC-based missing value imputation
imputed_data = impute_missing_values(
    data=normalized_data,
    method="qc_min",  # Use minimum values from QC samples
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"]
)
```

### Complete Preprocessing Pipeline

```python
import pandas as pd
from isospec_data_tools.analysis import (
    filter_data_matrix_samples,
    total_abundance_normalization,
    impute_missing_values,
    log2_transform_numeric
)

# Load data
data = pd.read_csv("metabolomics_data.csv")

# Step 1: Filter samples based on quality criteria
filtered_data = filter_data_matrix_samples(
    data=data,
    cv_threshold=30.0,  # Remove features with CV > 30%
    missing_threshold=0.8,  # Remove features missing in >80% of samples
    feature_prefix="FT-"
)

# Step 2: Normalize data
normalized_data = total_abundance_normalization(
    data=filtered_data,
    prefix="FT-"
)

# Step 3: Impute missing values
imputed_data = impute_missing_values(
    data=normalized_data,
    method="qc_min",
    sample_type_col="SampleType",
    qc_samples=["QC"]
)

# Step 4: Log transformation
log_transformed = log2_transform_numeric(
    data=imputed_data,
    feature_columns=[col for col in imputed_data.columns if col.startswith("FT-")]
)

print(f"Preprocessing complete:")
print(f"  Original features: {len([c for c in data.columns if c.startswith('FT-')])}")
print(f"  Final features: {len([c for c in log_transformed.columns if c.startswith('FT-')])}")
```

## Normalization Methods

### Total Abundance Normalization

Normalizes each sample by its total feature abundance, accounting for differences in sample concentration:

```python
# Basic usage
normalized = total_abundance_normalization(
    data=metabolomics_data,
    prefix="FT-"
)

# Memory-efficient for large datasets
total_abundance_normalization(
    data=large_dataset,
    prefix="METABOLITE_",
    inplace=True  # Modify in place to save memory
)

# With custom feature selection
feature_columns = ["glucose", "lactate", "pyruvate", "citrate"]
normalized = total_abundance_normalization(
    data=targeted_data,
    prefix=None  # Will use all numeric columns
)
```

#### When to Use

- **Metabolomics**: Compensates for sample dilution effects
- **Glycomics**: Normalizes for total glycan content
- **General**: When samples may have different overall concentrations

### Median Quotient Normalization (MQN)

Robust normalization method that uses the median quotient relative to reference samples:

```python
# Using QC samples as reference (recommended)
qc_mask = data["SampleType"].str.contains("QC", na=False)
mqn_data = median_quotient_normalization(
    data=metabolomics_data,
    prefix="FT-",
    reference_samples=qc_mask
)

# Using all samples as reference
mqn_data = median_quotient_normalization(
    data=metabolomics_data,
    prefix="FT-",
    reference_samples=None  # Uses all samples
)

# With custom reference selection
high_quality_samples = data["CV"] < 15.0
mqn_data = median_quotient_normalization(
    data=metabolomics_data,
    prefix="FT-",
    reference_samples=high_quality_samples
)
```

#### Advantages

- **Robust**: Less sensitive to outliers than mean-based methods
- **Reference-based**: Can use high-quality samples (e.g., QCs) as reference
- **Widely accepted**: Standard method in metabolomics

### Sample Filtering

Remove low-quality samples and features:

```python
# Filter based on feature quality
filtered_data = filter_data_matrix_samples(
    data=raw_data,
    cv_threshold=30.0,  # Remove features with CV > 30% in QC samples
    missing_threshold=0.5,  # Remove features missing in >50% of samples
    feature_prefix="FT-",
    qc_samples=qc_mask
)

# Advanced filtering with custom criteria
def quality_filter(feature_data, qc_mask):
    """Custom quality filter function."""
    qc_data = feature_data[qc_mask]
    cv = qc_data.std() / qc_data.mean() * 100
    missing_rate = feature_data.isna().sum() / len(feature_data)

    return cv < 25.0 and missing_rate < 0.3

# Apply custom filter
feature_columns = [col for col in data.columns if col.startswith("FT-")]
quality_features = []

for feature in feature_columns:
    if quality_filter(data[feature], qc_mask):
        quality_features.append(feature)

filtered_data = data[["SampleID", "SampleType"] + quality_features]
print(f"Retained {len(quality_features)} high-quality features")
```

## Missing Value Imputation

### QC-Based Imputation (Recommended)

Uses QC samples as reference for imputation, the gold standard in analytical chemistry:

```python
# Default QC-based imputation (uses minimum values from QC samples)
imputed_data = impute_missing_values(
    data=normalized_data,
    method="qc_min",  # Use minimum QC values
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"],  # QC sample types
    replacement_value=1  # Replace this value with NaN before imputation
)

# QC-based median imputation
imputed_data = impute_missing_values(
    data=normalized_data,
    method="qc_median",
    sample_type_col="SampleType",
    qc_samples=["QC"]
)
```

#### Why QC-Based Imputation?

- **Analytically sound**: QC samples represent the analytical method's capability
- **Conservative**: Uses detection limit estimates from actual measurements
- **Consistent**: Maintains analytical chemistry principles

### Statistical Imputation Methods

For datasets without QC samples or specific analytical requirements:

```python
# Median imputation
median_imputed = impute_missing_values(
    data=normalized_data,
    method="median"
)

# Mean imputation
mean_imputed = impute_missing_values(
    data=normalized_data,
    method="mean"
)

# Zero imputation (for absent/undetected compounds)
zero_imputed = impute_missing_values(
    data=normalized_data,
    method="zero"
)

# Constant value imputation
constant_imputed = impute_missing_values(
    data=normalized_data,
    method="constant",
    constant_value=0.001  # Detection limit estimate
)
```

### Imputation Strategy Selection

```python
def select_imputation_strategy(data, sample_type_col="SampleType"):
    """Guide for selecting appropriate imputation strategy."""

    # Check for QC samples
    if sample_type_col in data.columns:
        qc_samples = data[sample_type_col].str.contains("QC", na=False).sum()
        if qc_samples >= 3:
            return "qc_min"  # Recommended for analytical data

    # Check missing data patterns
    missing_rates = data.select_dtypes(include=[np.number]).isna().mean()
    high_missing = (missing_rates > 0.5).sum()

    if high_missing > len(missing_rates) * 0.3:
        return "zero"  # Many features with high missingness
    else:
        return "median"  # Standard statistical imputation

# Apply strategy
strategy = select_imputation_strategy(metabolomics_data)
imputed_data = impute_missing_values(
    data=metabolomics_data,
    method=strategy,
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"] if strategy == "qc_min" else None
)
```

## Data Transformations

### Log Transformations

Essential for normalizing skewed distributions common in omics data:

```python
from isospec_data_tools.analysis import log2_transform_numeric

# Log2 transformation (recommended for omics data)
log_data = log2_transform_numeric(
    data=imputed_data,
    feature_columns=[col for col in imputed_data.columns if col.startswith("FT-")]
)

# Handle zeros before log transformation
def safe_log_transform(data, feature_columns, pseudo_count=1e-6):
    """Log transform with safe handling of zeros."""
    transformed_data = data.copy()

    for col in feature_columns:
        # Add small pseudo-count to avoid log(0)
        transformed_data[col] = np.log2(data[col] + pseudo_count)

    return transformed_data

# Apply safe log transformation
log_transformed = safe_log_transform(
    data=imputed_data,
    feature_columns=metabolite_columns,
    pseudo_count=1e-6
)
```

### Categorical Encoding

```python
from isospec_data_tools.analysis import encode_categorical_column

# Encode categorical variables
encoded_data = encode_categorical_column(
    data=metabolomics_data,
    column="treatment_group",
    encoding_type="label"  # or "onehot"
)

# One-hot encoding for multiple categories
onehot_encoded = encode_categorical_column(
    data=metabolomics_data,
    column="tissue_type",
    encoding_type="onehot"
)
```

### Data Filtering and Selection

```python
from isospec_data_tools.analysis import (
    filter_data_by_column_value,
    replace_column_values
)

# Filter samples by criteria
filtered_samples = filter_data_by_column_value(
    data=metabolomics_data,
    column="quality_flag",
    values_to_keep=["PASS", "WARNING"]  # Remove "FAIL" samples
)

# Replace specific values
cleaned_data = replace_column_values(
    data=metabolomics_data,
    column="treatment",
    value_mapping={"ctrl": "control", "trt": "treatment"}
)
```

## Advanced Preprocessing Workflows

### Metabolomics-Specific Pipeline

```python
def metabolomics_preprocessing_pipeline(
    data,
    feature_prefix="FT-",
    sample_type_col="SampleType",
    cv_threshold=30.0
):
    """Complete metabolomics preprocessing pipeline."""

    print("Starting metabolomics preprocessing...")

    # Step 1: Quality filtering
    print("1. Filtering low-quality features...")
    qc_mask = data[sample_type_col].str.contains("QC", na=False)

    filtered_data = filter_data_matrix_samples(
        data=data,
        cv_threshold=cv_threshold,
        missing_threshold=0.8,
        feature_prefix=feature_prefix
    )

    original_features = len([c for c in data.columns if c.startswith(feature_prefix)])
    remaining_features = len([c for c in filtered_data.columns if c.startswith(feature_prefix)])
    print(f"   Removed {original_features - remaining_features} low-quality features")

    # Step 2: Total abundance normalization
    print("2. Performing total abundance normalization...")
    normalized_data = total_abundance_normalization(
        data=filtered_data,
        prefix=feature_prefix
    )

    # Step 3: QC-based imputation
    print("3. Imputing missing values using QC samples...")
    imputed_data = impute_missing_values(
        data=normalized_data,
        method="qc_min",
        sample_type_col=sample_type_col,
        qc_samples=["QC", "EQC"]
    )

    # Step 4: Log2 transformation
    print("4. Applying log2 transformation...")
    feature_cols = [col for col in imputed_data.columns if col.startswith(feature_prefix)]
    final_data = log2_transform_numeric(
        data=imputed_data,
        feature_columns=feature_cols
    )

    print(f"Preprocessing complete! Final dataset: {len(final_data)} samples, {len(feature_cols)} features")
    return final_data

# Apply pipeline
processed_data = metabolomics_preprocessing_pipeline(
    data=raw_metabolomics_data,
    feature_prefix="METABOLITE_",
    cv_threshold=25.0
)
```

### Glycomics-Specific Pipeline

```python
def glycomics_preprocessing_pipeline(
    data,
    glycan_prefix="G",
    sample_type_col="SampleType",
    normalization_method="mqn"
):
    """Glycomics-specific preprocessing with specialized considerations."""

    print("Starting glycomics preprocessing...")

    # Step 1: Handle glycan-specific missing patterns
    print("1. Analyzing glycan missing patterns...")
    glycan_cols = [col for col in data.columns if col.startswith(glycan_prefix)]

    # Glycans often have structured missingness
    missing_analysis = {}
    for col in glycan_cols:
        missing_rate = data[col].isna().sum() / len(data)
        missing_analysis[col] = missing_rate

    # Keep glycans present in at least 30% of samples
    quality_glycans = [col for col, rate in missing_analysis.items() if rate < 0.7]
    data_filtered = data[data.columns.difference(glycan_cols).tolist() + quality_glycans]

    print(f"   Retained {len(quality_glycans)} of {len(glycan_cols)} glycan features")

    # Step 2: Glycan-appropriate normalization
    print(f"2. Applying {normalization_method} normalization...")
    if normalization_method == "mqn":
        qc_mask = data_filtered[sample_type_col].str.contains("QC", na=False)
        normalized_data = median_quotient_normalization(
            data=data_filtered,
            prefix=glycan_prefix,
            reference_samples=qc_mask
        )
    else:
        normalized_data = total_abundance_normalization(
            data=data_filtered,
            prefix=glycan_prefix
        )

    # Step 3: QC-based imputation (conservative for glycomics)
    print("3. Conservative QC-based imputation...")
    imputed_data = impute_missing_values(
        data=normalized_data,
        method="qc_min",  # Conservative approach
        sample_type_col=sample_type_col,
        qc_samples=["QC"]
    )

    # Step 4: Optional log transformation (less common for glycomics)
    print("4. Optional: Log transformation...")
    final_glycan_cols = [col for col in imputed_data.columns if col.startswith(glycan_prefix)]

    # Check if log transformation is beneficial
    skewness_scores = []
    for col in final_glycan_cols:
        skew = imputed_data[col].skew()
        skewness_scores.append(abs(skew))

    avg_skewness = np.mean(skewness_scores)

    if avg_skewness > 2.0:  # Highly skewed data benefits from log transform
        print("   Data is highly skewed, applying log2 transformation...")
        final_data = log2_transform_numeric(
            data=imputed_data,
            feature_columns=final_glycan_cols
        )
    else:
        print("   Data is approximately normal, skipping log transformation...")
        final_data = imputed_data

    print(f"Glycomics preprocessing complete!")
    return final_data

# Apply glycomics pipeline
processed_glycomics = glycomics_preprocessing_pipeline(
    data=raw_glycomics_data,
    glycan_prefix="G",
    normalization_method="mqn"
)
```

## Data Validation and Quality Control

### Preprocessing Validation

```python
from isospec_data_tools.analysis.preprocessing.validators import (
    validate_feature_columns,
    validate_statistical_analysis_data
)

# Validate feature columns
try:
    validate_feature_columns(
        data=processed_data,
        feature_prefix="FT-",
        min_features=10
    )
    print("Feature validation passed")
except ValueError as e:
    print(f"Feature validation failed: {e}")

# Validate data for statistical analysis
try:
    validate_statistical_analysis_data(
        data=processed_data,
        group_column="treatment",
        feature_columns=metabolite_columns,
        min_samples_per_group=3
    )
    print("Statistical analysis validation passed")
except ValueError as e:
    print(f"Statistical validation failed: {e}")
```

### Quality Assessment

```python
def assess_preprocessing_quality(original_data, processed_data, feature_prefix):
    """Assess the quality of preprocessing results."""

    # Feature retention
    orig_features = len([c for c in original_data.columns if c.startswith(feature_prefix)])
    proc_features = len([c for c in processed_data.columns if c.startswith(feature_prefix)])
    retention_rate = proc_features / orig_features * 100

    # Missing data reduction
    orig_missing = original_data.select_dtypes(include=[np.number]).isna().sum().sum()
    proc_missing = processed_data.select_dtypes(include=[np.number]).isna().sum().sum()
    missing_reduction = (orig_missing - proc_missing) / orig_missing * 100

    # Data range assessment
    feature_cols = [c for c in processed_data.columns if c.startswith(feature_prefix)]
    data_ranges = processed_data[feature_cols].max() - processed_data[feature_cols].min()

    report = {
        "feature_retention_rate": f"{retention_rate:.1f}%",
        "missing_data_reduction": f"{missing_reduction:.1f}%",
        "final_features": proc_features,
        "mean_data_range": data_ranges.mean(),
        "data_completeness": f"{(1 - processed_data[feature_cols].isna().sum().sum() / (len(processed_data) * len(feature_cols))) * 100:.1f}%"
    }

    return report

# Assess quality
quality_report = assess_preprocessing_quality(
    original_data=raw_data,
    processed_data=processed_data,
    feature_prefix="FT-"
)

for metric, value in quality_report.items():
    print(f"{metric.replace('_', ' ').title()}: {value}")
```

## Integration with Visualization

### Preprocessing Impact Visualization

```python
from isospec_data_tools.visualization.analysis import (
    PreprocessingPlotter,
    CVAnalysisPlotter
)

# Initialize plotter
plotter = PreprocessingPlotter(
    data=processed_data,
    feature_columns=metabolite_columns
)

# Visualize missing data patterns
missing_plots = plotter.plot_missing_data_analysis(
    output_dir="preprocessing_analysis"
)

# CV improvement analysis
cv_plotter = CVAnalysisPlotter(
    raw_data=raw_data,
    normalized_data=processed_data,
    feature_columns=metabolite_columns,
    qc_samples=qc_mask
)

cv_improvement_plots = cv_plotter.plot_cv_improvement_analysis(
    normalization_methods=["raw", "total_abundance", "mqn"],
    output_dir="cv_analysis"
)
```

## Best Practices

### 1. Always Use QC Samples

```python
# Check for QC samples before processing
def validate_qc_presence(data, sample_type_col="SampleType"):
    if sample_type_col not in data.columns:
        print("Warning: No sample type column found")
        return False

    qc_count = data[sample_type_col].str.contains("QC", na=False).sum()
    if qc_count < 3:
        print(f"Warning: Only {qc_count} QC samples found. Recommend ≥3 for reliable imputation")
        return False

    print(f"Found {qc_count} QC samples - sufficient for QC-based processing")
    return True

# Validate before processing
if validate_qc_presence(raw_data):
    # Use QC-based methods
    imputed_data = impute_missing_values(data, method="qc_min", ...)
else:
    # Fall back to statistical methods
    imputed_data = impute_missing_values(data, method="median")
```

### 2. Document Processing Steps

```python
def documented_preprocessing_pipeline(data, **kwargs):
    """Preprocessing pipeline with full documentation of steps."""

    processing_log = {
        "input_samples": len(data),
        "input_features": len([c for c in data.columns if c.startswith(kwargs.get("feature_prefix", "FT-"))]),
        "steps": []
    }

    # Step 1: Filtering
    filtered_data = filter_data_matrix_samples(data, **kwargs)
    processing_log["steps"].append({
        "step": "quality_filtering",
        "features_remaining": len([c for c in filtered_data.columns if c.startswith(kwargs.get("feature_prefix", "FT-"))]),
        "parameters": {k: v for k, v in kwargs.items() if k in ["cv_threshold", "missing_threshold"]}
    })

    # Continue with other steps...

    return processed_data, processing_log

# Use documented pipeline
processed_data, log = documented_preprocessing_pipeline(
    data=raw_data,
    feature_prefix="FT-",
    cv_threshold=30.0
)

# Save processing log
import json
with open("preprocessing_log.json", "w") as f:
    json.dump(log, f, indent=2)
```

### 3. Validate Each Step

```python
def robust_preprocessing_pipeline(data, **kwargs):
    """Preprocessing with validation at each step."""

    try:
        # Step 1: Initial validation
        assert not data.empty, "Input data is empty"
        assert len(data) > 10, "Insufficient samples for analysis"

        # Step 2: Filtering with validation
        filtered_data = filter_data_matrix_samples(data, **kwargs)
        feature_count = len([c for c in filtered_data.columns if c.startswith(kwargs.get("feature_prefix", "FT-"))])
        assert feature_count > 5, f"Too few features remaining ({feature_count})"

        # Step 3: Normalization with validation
        normalized_data = total_abundance_normalization(filtered_data, **kwargs)
        assert not normalized_data.isna().all().any(), "Normalization produced all-NaN columns"

        # Step 4: Imputation with validation
        imputed_data = impute_missing_values(normalized_data, **kwargs)
        remaining_missing = imputed_data.select_dtypes(include=[np.number]).isna().sum().sum()
        print(f"Imputation reduced missing values to {remaining_missing}")

        return imputed_data

    except AssertionError as e:
        print(f"Pipeline validation failed: {e}")
        raise
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise

# Use robust pipeline
try:
    processed_data = robust_preprocessing_pipeline(
        data=raw_data,
        feature_prefix="FT-",
        method="qc_min",
        sample_type_col="SampleType"
    )
except Exception as e:
    print(f"Preprocessing failed: {e}")
```

## Performance Optimization

### Memory-Efficient Processing

```python
# For large datasets, use in-place operations
def memory_efficient_preprocessing(data_path, output_path, chunk_size=1000):
    """Process large datasets in chunks to manage memory."""

    # Read data in chunks
    chunk_iter = pd.read_csv(data_path, chunksize=chunk_size)

    processed_chunks = []
    for i, chunk in enumerate(chunk_iter):
        print(f"Processing chunk {i+1}...")

        # Process chunk in-place
        total_abundance_normalization(chunk, prefix="FT-", inplace=True)

        # QC-based imputation
        imputed_chunk = impute_missing_values(
            chunk,
            method="qc_min",
            sample_type_col="SampleType"
        )

        processed_chunks.append(imputed_chunk)

    # Combine processed chunks
    final_data = pd.concat(processed_chunks, ignore_index=True)
    final_data.to_csv(output_path, index=False)

    return final_data

# Use for large datasets
large_processed = memory_efficient_preprocessing(
    data_path="large_metabolomics_data.csv",
    output_path="processed_large_data.csv"
)
```

## Troubleshooting

### Common Issues and Solutions

```python
# Issue 1: All features removed during filtering
def debug_feature_filtering(data, feature_prefix="FT-", cv_threshold=30.0):
    """Debug why features are being removed."""

    feature_cols = [col for col in data.columns if col.startswith(feature_prefix)]
    qc_mask = data["SampleType"].str.contains("QC", na=False)

    removal_reasons = {}
    for col in feature_cols:
        qc_data = data[qc_mask][col].dropna()

        if len(qc_data) < 3:
            removal_reasons[col] = "insufficient_qc_data"
        else:
            cv = qc_data.std() / qc_data.mean() * 100
            if cv > cv_threshold:
                removal_reasons[col] = f"high_cv_{cv:.1f}"
            else:
                removal_reasons[col] = "passed"

    # Summary
    reason_counts = {}
    for reason in removal_reasons.values():
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    print("Feature filtering debug:")
    for reason, count in reason_counts.items():
        print(f"  {reason}: {count} features")

    return removal_reasons

# Debug filtering
debug_results = debug_feature_filtering(raw_data, cv_threshold=25.0)
```

## API Reference

::: isospec_data_tools.analysis.preprocessing.normalizers
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.preprocessing.transformers
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.preprocessing.validators
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.preprocessing.pipeline
handler: python
options:
show_root_heading: true
show_source: false
