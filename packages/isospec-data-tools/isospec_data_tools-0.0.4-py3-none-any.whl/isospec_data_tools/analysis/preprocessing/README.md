# Preprocessing Pipeline

The preprocessing module provides comprehensive data preparation capabilities for omics data analysis, including normalization, imputation, validation, and transformation methods.

## Components

### Data Normalization (`normalizers.py`)

Comprehensive normalization methods for omics data with proper handling of missing values and batch effects.

#### Total Abundance Normalization

```python
from isospec_data_tools.analysis.preprocessing.normalizers import total_abundance_normalization

# Basic total abundance normalization
normalized_data = total_abundance_normalization(
    data=raw_data,
    feature_cols=metabolite_columns,
    exclude_zeros=True,
    min_abundance_threshold=1000
)
```

#### Median Quotient Normalization

```python
from isospec_data_tools.analysis.preprocessing.normalizers import median_quotient_normalization

# Median quotient normalization (recommended for metabolomics)
normalized_data = median_quotient_normalization(
    data=raw_data,
    feature_cols=metabolite_columns,
    reference_samples=qc_samples,
    exclude_zeros=True
)
```

#### Quantile Normalization

```python
from isospec_data_tools.analysis.preprocessing.normalizers import quantile_normalization

# Quantile normalization for cross-sample comparison
normalized_data = quantile_normalization(
    data=raw_data,
    feature_cols=metabolite_columns,
    reference_distribution="median"
)
```

#### Probabilistic Quotient Normalization (PQN)

```python
from isospec_data_tools.analysis.preprocessing.normalizers import probabilistic_quotient_normalization

# PQN normalization
normalized_data = probabilistic_quotient_normalization(
    data=raw_data,
    feature_cols=metabolite_columns,
    reference_samples=qc_samples
)
```

### Missing Value Imputation (`impute_missing_values` function)

**Critical Implementation Note**: The `impute_missing_values` function implements domain-specific imputation logic for analytical chemistry data.

#### QC-Based Imputation (Default Method)

```python
from isospec_data_tools.analysis.preprocessing.normalizers import impute_missing_values

# QC-based imputation using minimum values from QC samples
imputed_data = impute_missing_values(
    data=normalized_data,
    method="qc_min",  # Default method
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"],  # Default QC sample types
    replacement_value=1  # Replace 1s with NaN before imputation
)
```

**Key Parameters:**

- `method`: Imputation strategy - `"qc_min"` (default), `"median"`, `"mean"`, `"zero"`, `"constant"`
- `sample_type_col`: Column containing sample type information (default: `"SampleType"`)
- `qc_samples`: List of QC sample types for imputation reference (default: `["QC", "EQC"]`)
- `replacement_value`: Value to replace with NaN before imputation (default: `1`)

#### Statistical Imputation Methods

```python
# Median imputation
median_imputed = impute_missing_values(
    data=normalized_data,
    method="median",
    feature_cols=metabolite_columns
)

# Mean imputation
mean_imputed = impute_missing_values(
    data=normalized_data,
    method="mean",
    feature_cols=metabolite_columns
)

# Zero imputation
zero_imputed = impute_missing_values(
    data=normalized_data,
    method="zero",
    feature_cols=metabolite_columns
)

# Constant imputation
constant_imputed = impute_missing_values(
    data=normalized_data,
    method="constant",
    constant_value=0.5,
    feature_cols=metabolite_columns
)
```

### Data Transformation (`transformers.py`)

Various data transformation methods for omics data analysis.

#### Log Transformation

```python
from isospec_data_tools.analysis.preprocessing.transformers import log_transform

# Log10 transformation
log_transformed = log_transform(
    data=normalized_data,
    feature_cols=metabolite_columns,
    base=10,
    add_constant=1  # Add 1 to avoid log(0)
)
```

#### Scaling and Centering

```python
from isospec_data_tools.analysis.preprocessing.transformers import scale_data

# Standard scaling (z-score)
scaled_data = scale_data(
    data=normalized_data,
    feature_cols=metabolite_columns,
    method="standard"
)

# Min-max scaling
minmax_scaled = scale_data(
    data=normalized_data,
    feature_cols=metabolite_columns,
    method="minmax"
)

# Robust scaling
robust_scaled = scale_data(
    data=normalized_data,
    feature_cols=metabolite_columns,
    method="robust"
)
```

#### Pareto Scaling

```python
from isospec_data_tools.analysis.preprocessing.transformers import pareto_scale

# Pareto scaling (common in metabolomics)
pareto_scaled = pareto_scale(
    data=normalized_data,
    feature_cols=metabolite_columns
)
```

### Data Validation (`validators.py`)

Comprehensive data quality validation and outlier detection.

#### Data Quality Assessment

```python
from isospec_data_tools.analysis.preprocessing.validators import assess_data_quality

# Comprehensive data quality assessment
quality_report = assess_data_quality(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"]
)

print(f"Data quality score: {quality_report['overall_score']}")
print(f"Missing data percentage: {quality_report['missing_percentage']:.2f}%")
print(f"Outlier count: {quality_report['outlier_count']}")
```

#### Outlier Detection

```python
from isospec_data_tools.analysis.preprocessing.validators import detect_outliers

# Multiple outlier detection methods
outliers = detect_outliers(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    methods=["iqr", "zscore", "isolation_forest"],
    contamination=0.1
)

# Remove outliers
clean_data = preprocessed_data[~outliers['composite_outlier']]
```

#### Batch Effect Detection

```python
from isospec_data_tools.analysis.preprocessing.validators import detect_batch_effects

# Detect batch effects
batch_effects = detect_batch_effects(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    batch_col="batch",
    method="pca"
)

if batch_effects['significant']:
    print("Batch effects detected. Consider batch correction.")
```

## Complete Preprocessing Pipeline

### DataWrangler Class

The `DataWrangler` class provides a unified interface for all preprocessing operations:

```python
from isospec_data_tools.analysis.preprocessing import DataWrangler

# Initialize data wrangler
wrangler = DataWrangler()

# Complete preprocessing pipeline
processed_data = wrangler.preprocess_data(
    data=raw_data,
    feature_cols=metabolite_columns,
    normalization_method="total_abundance",
    imputation_method="qc_min",
    transformation_method="log10",
    scaling_method="standard",
    outlier_detection=True,
    batch_correction=True
)
```

### Step-by-Step Pipeline

```python
from isospec_data_tools.analysis.preprocessing import DataWrangler

# Initialize wrangler
wrangler = DataWrangler()

# Step 1: Data validation
validation_report = wrangler.validate_data_quality(
    data=raw_data,
    feature_cols=metabolite_columns,
    sample_type_col="SampleType"
)

# Step 2: Normalization
normalized_data = wrangler.total_abundance_normalization(
    data=raw_data,
    feature_cols=metabolite_columns
)

# Step 3: Missing value imputation
imputed_data = wrangler.impute_missing_values(
    data=normalized_data,
    method="qc_min",
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"]
)

# Step 4: Transformation
transformed_data = wrangler.log_transform(
    data=imputed_data,
    feature_cols=metabolite_columns,
    base=10
)

# Step 5: Scaling
scaled_data = wrangler.scale_data(
    data=transformed_data,
    feature_cols=metabolite_columns,
    method="standard"
)

# Step 6: Outlier detection and removal
outliers = wrangler.detect_outliers(
    data=scaled_data,
    feature_cols=metabolite_columns,
    methods=["iqr", "zscore"]
)

clean_data = scaled_data[~outliers['composite_outlier']]
```

## Advanced Preprocessing Techniques

### Batch Effect Correction

```python
from isospec_data_tools.analysis.preprocessing.batch_correction import correct_batch_effects

# ComBat batch correction
corrected_data = correct_batch_effects(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    batch_col="batch",
    method="combat"
)
```

### Signal Drift Correction

```python
from isospec_data_tools.analysis.preprocessing.drift_correction import correct_signal_drift

# QC-based drift correction
drift_corrected = correct_signal_drift(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    qc_samples=qc_sample_indices,
    method="loess"
)
```

### Feature Filtering

```python
from isospec_data_tools.analysis.preprocessing.feature_filtering import filter_features

# Filter features based on quality metrics
filtered_features = filter_features(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    min_detection_rate=0.5,
    max_missing_rate=0.3,
    min_cv_qc=0.3,
    qc_samples=["QC", "EQC"]
)
```

## Method Comparison and Selection

### Normalization Method Comparison

```python
from isospec_data_tools.analysis.preprocessing.method_comparison import compare_normalization_methods

# Compare different normalization methods
comparison_results = compare_normalization_methods(
    data=raw_data,
    feature_cols=metabolite_columns,
    methods=["total_abundance", "median_quotient", "quantile", "pqn"],
    evaluation_metrics=["cv_qc", "pca_separation", "correlation"]
)

# Select best method
best_method = comparison_results['best_method']
print(f"Best normalization method: {best_method}")
```

### Imputation Method Evaluation

```python
from isospec_data_tools.analysis.preprocessing.method_comparison import evaluate_imputation_methods

# Evaluate different imputation methods
imputation_evaluation = evaluate_imputation_methods(
    data=normalized_data,
    feature_cols=metabolite_columns,
    methods=["qc_min", "median", "mean", "knn"],
    missing_patterns=["mcar", "mar", "mnar"]
)

# Select best imputation method
best_imputation = imputation_evaluation['best_method']
print(f"Best imputation method: {best_imputation}")
```

## Quality Control and Validation

### QC Sample Analysis

```python
from isospec_data_tools.analysis.preprocessing.qc_analysis import analyze_qc_samples

# Analyze QC sample quality
qc_analysis = analyze_qc_samples(
    data=preprocessed_data,
    feature_cols=metabolite_columns,
    qc_samples=["QC", "EQC"],
    sample_type_col="SampleType"
)

print(f"QC CV median: {qc_analysis['cv_median']:.3f}")
print(f"QC clustering quality: {qc_analysis['clustering_quality']:.3f}")
```

### Preprocessing Validation

```python
from isospec_data_tools.analysis.preprocessing.validation import validate_preprocessing

# Validate preprocessing results
validation_results = validate_preprocessing(
    original_data=raw_data,
    processed_data=processed_data,
    feature_cols=metabolite_columns,
    sample_type_col="SampleType"
)

print(f"Preprocessing quality score: {validation_results['quality_score']:.3f}")
```

## Performance Optimization

### Memory-Efficient Processing

```python
from isospec_data_tools.analysis.preprocessing.memory_efficient import process_large_dataset

# Process large datasets in chunks
processed_data = process_large_dataset(
    data_path="large_dataset.csv",
    feature_cols=metabolite_columns,
    chunk_size=10000,
    preprocessing_steps=[
        "normalization",
        "imputation",
        "transformation"
    ]
)
```

### Parallel Processing

```python
from isospec_data_tools.analysis.preprocessing.parallel import parallel_preprocessing

# Parallel preprocessing
processed_data = parallel_preprocessing(
    data=raw_data,
    feature_cols=metabolite_columns,
    n_jobs=4,
    preprocessing_config=preprocessing_config
)
```

## Integration with Other Modules

### Integration with Statistical Analysis

```python
from isospec_data_tools.analysis import DataWrangler, StatisticalAnalyzer

# Combined preprocessing and analysis
wrangler = DataWrangler()
analyzer = StatisticalAnalyzer()

# Preprocess data
processed_data = wrangler.preprocess_data(
    data=raw_data,
    feature_cols=metabolite_columns,
    normalization_method="total_abundance",
    imputation_method="qc_min"
)

# Perform statistical analysis
results = analyzer.perform_t_test(
    data=processed_data,
    group_col="treatment",
    feature_cols=metabolite_columns
)
```

### Integration with Visualization

```python
from isospec_data_tools.visualization.analysis import plot_preprocessing_results

# Visualize preprocessing results
plot_preprocessing_results(
    original_data=raw_data,
    processed_data=processed_data,
    feature_cols=metabolite_columns,
    output_dir="preprocessing_plots"
)
```

## Best Practices

### Order of Operations

1. **Data validation**: Check data quality and structure
2. **Normalization**: Apply appropriate normalization method
3. **Imputation**: Handle missing values appropriately
4. **Transformation**: Apply log or other transformations
5. **Scaling**: Scale features for downstream analysis
6. **Outlier detection**: Identify and handle outliers
7. **Batch correction**: Correct for batch effects if needed

### Method Selection Guidelines

- **Normalization**: Use median quotient for metabolomics, total abundance for simple cases
- **Imputation**: Use QC-based methods for analytical chemistry data
- **Transformation**: Apply log transformation for right-skewed data
- **Scaling**: Use standard scaling for most machine learning applications

### Quality Control

- Always validate preprocessing results
- Use QC samples to monitor data quality
- Check for batch effects before and after correction
- Monitor feature distributions after each step

## Troubleshooting

### Common Issues

1. **Negative values after normalization**: Check for zeros in denominator
2. **Imputation failures**: Ensure QC samples are properly labeled
3. **Scaling issues**: Check for constant features or extreme outliers
4. **Memory errors**: Use chunked processing for large datasets

### Debugging Tips

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
wrangler = DataWrangler(debug=True)
```

For more examples and detailed API documentation, see the main analysis module documentation.
