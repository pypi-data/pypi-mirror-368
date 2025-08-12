# Analysis Core Module

The analysis core module provides fundamental statistical operations, effect size calculations, and project configuration management that form the foundation of the isospec-data-tools analysis pipeline.

## Overview

The core module consists of several key components:

1. **Statistical Tests**: T-tests, chi-square tests, Tukey HSD, and other fundamental statistical operations
2. **Effect Size Calculations**: Cohen's d, fold change, and other effect size metrics
3. **Multiple Comparison Corrections**: FDR, Bonferroni, and other correction methods
4. **Project Configuration**: Modular configuration system for analysis workflows

## Quick Start

### Basic Statistical Testing

```python
from isospec_data_tools.analysis import (
    perform_student_t_test,
    perform_welch_t_test,
    perform_tukey_hsd_test,
    adjust_p_values
)

# Student's t-test (equal variances)
student_result = perform_student_t_test(
    group1_data=control_group,
    group2_data=treatment_group
)

# Welch's t-test (unequal variances) - recommended default
welch_result = perform_welch_t_test(
    group1_data=control_group,
    group2_data=treatment_group
)

# Multiple comparison correction
corrected_p_values = adjust_p_values(
    p_values=[0.01, 0.05, 0.15, 0.003],
    method="fdr_bh"
)
```

### Project Configuration

```python
from isospec_data_tools.analysis import create_project_config
from isospec_data_tools.analysis.core.project_config import (
    DataStructureConfig,
    StatisticalConfig,
    VisualizationConfig
)

# Create default configuration
config = create_project_config()

# Create custom configuration
data_config = DataStructureConfig(
    sample_column="SampleID",
    sample_type_column="SampleType",
    feature_prefix="FT-",
    qc_identifier=["QC", "EQC"]
)

stats_config = StatisticalConfig(
    cv_threshold=30.0,
    effect_size_threshold=0.5,
    p_value_threshold=0.05
)

config = create_project_config(
    data_config=data_config,
    stats_config=stats_config
)
```

## Statistical Tests

### T-Tests

The module provides robust t-test implementations with automatic effect size calculations:

#### Student's T-Test

```python
# Student's t-test assumes equal variances
result = perform_student_t_test(
    group1_data=control_samples,
    group2_data=treatment_samples
)

print(f"T-statistic: {result['t_statistic']:.3f}")
print(f"P-value: {result['p_value']:.3f}")
print(f"Effect size (Cohen's d): {result['effect_size']:.3f}")
print(f"95% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
```

#### Welch's T-Test

```python
# Welch's t-test handles unequal variances (recommended)
result = perform_welch_t_test(
    group1_data=control_samples,
    group2_data=treatment_samples
)

# Results include comprehensive statistics
print(f"Mean difference: {result['mean_diff']:.3f}")
print(f"Fold change: {result['fold_change']:.3f}")
print(f"Degrees of freedom: {result['degrees_freedom']:.1f}")
```

#### Batch T-Test Analysis

```python
import pandas as pd

# Perform t-tests across multiple features
metabolomics_data = pd.read_csv("metabolomics_data.csv")
feature_columns = [col for col in metabolomics_data.columns if col.startswith("FT-")]

control_mask = metabolomics_data["treatment"] == "control"
treatment_mask = metabolomics_data["treatment"] == "treatment"

results = []
for feature in feature_columns:
    control_data = metabolomics_data.loc[control_mask, feature].dropna()
    treatment_data = metabolomics_data.loc[treatment_mask, feature].dropna()

    if len(control_data) >= 3 and len(treatment_data) >= 3:
        result = perform_welch_t_test(control_data, treatment_data)
        result["feature"] = feature
        results.append(result)

results_df = pd.DataFrame(results)

# Apply multiple comparison correction
results_df["p_value_corrected"] = adjust_p_values(
    results_df["p_value"].tolist(),
    method="fdr_bh"
)

# Filter significant results
significant_features = results_df[
    results_df["p_value_corrected"] < 0.05
].sort_values("p_value_corrected")

print(f"Found {len(significant_features)} significant features")
```

### Tukey HSD Test

For post-hoc multiple comparisons after ANOVA:

```python
# Tukey HSD for multiple group comparisons
tukey_results = perform_tukey_hsd_test(
    data=metabolomics_data,
    group_col="treatment_group",
    feature_cols=["metabolite_1", "metabolite_2", "metabolite_3"]
)

# Results are returned as DataFrame for easier analysis
print(tukey_results.head())
```

### Chi-Square Tests

```python
from isospec_data_tools.analysis import (
    perform_chi_square_test,
    perform_independence_test
)

# Chi-square goodness of fit
chi2_result = perform_chi_square_test(
    observed_frequencies=[20, 30, 25, 25],
    expected_frequencies=[25, 25, 25, 25]
)

# Chi-square test of independence
independence_result = perform_independence_test(
    data=clinical_data,
    var1="treatment_response",
    var2="patient_sex"
)
```

## Effect Size Calculations

### Cohen's d

```python
from isospec_data_tools.analysis.core.effect_sizes import calculate_cohens_d

# Calculate Cohen's d for effect size
cohens_d = calculate_cohens_d(
    group1_data=control_group,
    group2_data=treatment_group
)

# Interpret effect size
if abs(cohens_d) < 0.2:
    effect_interpretation = "Small effect"
elif abs(cohens_d) < 0.5:
    effect_interpretation = "Medium effect"
else:
    effect_interpretation = "Large effect"

print(f"Cohen's d: {cohens_d:.3f} ({effect_interpretation})")
```

### Fold Change

```python
from isospec_data_tools.analysis.core.effect_sizes import calculate_fold_change

# Calculate fold change
fold_change = calculate_fold_change(
    group1_data=control_group,
    group2_data=treatment_group
)

print(f"Fold change: {fold_change:.3f}")
print(f"Log2 fold change: {np.log2(fold_change):.3f}")
```

## Multiple Comparison Corrections

### Available Methods

```python
# False Discovery Rate (Benjamini-Hochberg) - recommended
fdr_corrected = adjust_p_values(p_values, method="fdr_bh")

# Bonferroni correction (conservative)
bonferroni_corrected = adjust_p_values(p_values, method="bonferroni")

# Holm correction
holm_corrected = adjust_p_values(p_values, method="holm")

# Benjamini-Yekutieli (for dependent tests)
by_corrected = adjust_p_values(p_values, method="fdr_by")
```

### Practical Example

```python
import numpy as np

# Simulate multiple testing scenario
np.random.seed(42)
p_values = np.random.uniform(0, 1, 100)  # 100 random p-values

# Apply different correction methods
corrections = {
    "Uncorrected": p_values,
    "FDR (B-H)": adjust_p_values(p_values, method="fdr_bh"),
    "Bonferroni": adjust_p_values(p_values, method="bonferroni"),
    "Holm": adjust_p_values(p_values, method="holm")
}

# Count significant results at α = 0.05
for method, corrected_p in corrections.items():
    significant_count = np.sum(corrected_p < 0.05)
    print(f"{method}: {significant_count} significant results")
```

## Project Configuration System

### Configuration Classes

#### DataStructureConfig

Manages data structure mapping and QC sample identification:

```python
from isospec_data_tools.analysis.core.project_config import DataStructureConfig

# Flexible QC sample identification
data_config = DataStructureConfig(
    sample_column="SampleID",
    sample_type_column="SampleType",
    feature_prefix="FT-",
    qc_identifier=["QC", "EQC", "POOLED_QC"],  # List of QC types
    qc_detection_method="contains",  # or "equals"
    metadata_columns=["injection_order", "batch", "acquisition_date"]
)

# QC sample detection
qc_mask = data_config.identify_qc_samples(metabolomics_data)
print(f"Identified {qc_mask.sum()} QC samples")
```

#### StatisticalConfig

Defines statistical thresholds and analysis parameters:

```python
from isospec_data_tools.analysis.core.project_config import StatisticalConfig

stats_config = StatisticalConfig(
    cv_threshold=30.0,  # CV threshold for quality assessment
    cv_ranges=[  # CV categorization ranges
        (0, 10, "Excellent (<10%)"),
        (10, 20, "Good (10-20%)"),
        (20, 30, "Acceptable (20-30%)"),
        (30, float("inf"), "Poor (>30%)")
    ],
    percentile_thresholds=(25.0, 75.0),  # For abundance classification
    effect_size_threshold=0.5,  # Minimum meaningful effect size
    p_value_threshold=0.05,  # Significance threshold
    alpha_level=0.05
)
```

#### VisualizationConfig

Controls visual presentation settings:

```python
from isospec_data_tools.analysis.core.project_config import VisualizationConfig

viz_config = VisualizationConfig(
    figure_size=(12, 8),
    color_palette="viridis",
    font_sizes={
        "title": 16,
        "axis_labels": 12,
        "tick_labels": 10,
        "legend": 11
    },
    save_format="png",
    dpi=300,
    layout_configs={
        "cluster_plot": {"figsize": (10, 8), "ncols": 2},
        "confounder_plot": {"figsize": (14, 10), "ncols": 3},
        "differential_plot": {"figsize": (12, 9), "ncols": 2}
    }
)
```

### Configuration Factory

Pre-defined configurations for common use cases:

```python
from isospec_data_tools.analysis.core.project_config import ConfigFactory

# Load CoLaus study defaults
data_config, stats_config, viz_config = ConfigFactory.colaus_defaults()

# Use in analysis workflow
config = create_project_config(
    data_config=data_config,
    stats_config=stats_config,
    viz_config=viz_config
)
```

### Configuration Persistence

```python
from isospec_data_tools.analysis import (
    save_project_config,
    load_project_config
)

# Save configuration
save_project_config(config, "my_analysis_config.json")

# Load configuration
loaded_config = load_project_config("my_analysis_config.json")

# Use in analysis
normalized_data = total_abundance_normalization(
    data=raw_data,
    prefix=loaded_config.data_config.feature_prefix
)
```

## Advanced Configuration Examples

### Custom QC Detection

```python
# Custom QC detection function
def custom_qc_detector(sample_name):
    """Custom function to identify QC samples."""
    qc_patterns = ["QC", "POOL", "BLANK", "STANDARD"]
    return any(pattern in sample_name.upper() for pattern in qc_patterns)

data_config = DataStructureConfig(
    sample_column="SampleID",
    qc_identifier=custom_qc_detector  # Use custom function
)
```

### Study-Specific Configuration

```python
# Metabolomics study configuration
metabolomics_config = DataStructureConfig(
    sample_column="SampleID",
    sample_type_column="SampleType",
    feature_prefix="METABOLITE_",
    qc_identifier=["QC", "POOL"],
    metadata_columns=["age", "sex", "bmi", "treatment"]
)

# Glycomics study configuration
glycomics_config = DataStructureConfig(
    sample_column="sample_id",
    sample_type_column="sample_class",
    feature_prefix="G",  # Glycan features
    qc_identifier="QC",
    metadata_columns=["patient_id", "visit", "timepoint"]
)
```

## Error Handling and Validation

### Statistical Test Validation

```python
try:
    result = perform_welch_t_test(group1_data, group2_data)
except ValueError as e:
    if "Insufficient data" in str(e):
        print("Not enough samples for reliable statistical testing")
    elif "Invalid input" in str(e):
        print("Data contains invalid values (NaN, infinite)")
    else:
        print(f"Statistical test failed: {e}")
```

### Configuration Validation

```python
# Configuration automatically validates inputs
try:
    data_config = DataStructureConfig(
        sample_column="SampleID",
        cv_threshold=-5.0  # Invalid: negative CV threshold
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Performance Considerations

### Batch Processing

```python
# Efficient batch statistical testing
def batch_t_tests(data, group_col, feature_cols):
    """Perform t-tests across multiple features efficiently."""
    results = []

    groups = data[group_col].unique()
    if len(groups) != 2:
        raise ValueError("T-test requires exactly 2 groups")

    group1_data = data[data[group_col] == groups[0]]
    group2_data = data[data[group_col] == groups[1]]

    for feature in feature_cols:
        try:
            g1_values = group1_data[feature].dropna()
            g2_values = group2_data[feature].dropna()

            if len(g1_values) >= 3 and len(g2_values) >= 3:
                result = perform_welch_t_test(g1_values, g2_values)
                result["feature"] = feature
                results.append(result)
        except Exception as e:
            print(f"Warning: Failed to test {feature}: {e}")
            continue

    return pd.DataFrame(results)

# Usage
feature_columns = [col for col in data.columns if col.startswith("FT-")]
t_test_results = batch_t_tests(
    data=metabolomics_data,
    group_col="treatment",
    feature_cols=feature_columns
)
```

## Integration with Other Modules

### With Preprocessing

```python
from isospec_data_tools.analysis import (
    create_project_config,
    total_abundance_normalization,
    perform_welch_t_test
)

# Create configuration
config = create_project_config()

# Use configuration in preprocessing
normalized_data = total_abundance_normalization(
    data=raw_data,
    prefix=config.data_config.feature_prefix
)

# Use in statistical testing
feature_cols = [col for col in normalized_data.columns
                if col.startswith(config.data_config.feature_prefix)]

statistical_results = []
for feature in feature_cols:
    result = perform_welch_t_test(
        group1_data=normalized_data[control_mask][feature],
        group2_data=normalized_data[treatment_mask][feature]
    )
    statistical_results.append(result)
```

### With Visualization

```python
from isospec_data_tools.visualization.analysis import plot_differential_analysis

# Statistical testing with visualization
t_test_results = batch_t_tests(data, "treatment", feature_cols)

# Apply multiple comparison correction
t_test_results["p_adjusted"] = adjust_p_values(
    t_test_results["p_value"].tolist(),
    method="fdr_bh"
)

# Generate visualization
plot_differential_analysis(
    statistical_results=t_test_results,
    data=metabolomics_data,
    output_dir="differential_analysis_plots"
)
```

## Testing and Validation

The core module includes comprehensive testing:

```python
# Run core module tests
import subprocess
subprocess.run(["uv", "run", "python", "-m", "pytest", "tests/test_analysis/test_core/", "-v"])
```

## API Reference

::: isospec_data_tools.analysis.core.statistical_tests
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.core.effect_sizes
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.core.multiple_comparisons
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.core.project_config
handler: python
options:
show_root_heading: true
show_source: false
