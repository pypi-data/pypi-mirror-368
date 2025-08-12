# Core Statistical Functions

The core module provides fundamental statistical building blocks for omics data analysis. This module focuses on robust, well-tested statistical methods with proper error handling and comprehensive documentation.

## Components

### Statistical Tests (`statistical_tests.py`)

Core statistical testing functions with proper assumption checking and error handling.

#### T-tests

```python
from isospec_data_tools.analysis.core.statistical_tests import (
    perform_student_t_test,
    perform_welch_t_test
)

# Student's t-test (assumes equal variances)
result = perform_student_t_test(
    group1_data=control_values,
    group2_data=treatment_values,
    alternative="two-sided"
)

# Welch's t-test (unequal variances) - recommended for metabolomics
result = perform_welch_t_test(
    group1_data=control_values,
    group2_data=treatment_values,
    alternative="two-sided"
)
```

#### ANCOVA

```python
from isospec_data_tools.analysis.core.statistical_tests import perform_ancova

# Analysis of covariance
ancova_result = perform_ancova(
    data=metabolomics_data,
    dependent_var="metabolite_concentration",
    factor_vars=["treatment"],
    covariate_vars=["age", "bmi"],
    interaction_terms=True
)
```

#### Chi-square Tests

```python
from isospec_data_tools.analysis.core.statistical_tests import perform_chi_square_test

# Chi-square test for categorical associations
chi_result = perform_chi_square_test(
    contingency_table=cross_table,
    correction=True  # Yates' continuity correction
)
```

### Effect Sizes (`effect_sizes.py`)

Effect size calculations to complement statistical significance testing.

#### Cohen's d

```python
from isospec_data_tools.analysis.core.effect_sizes import (
    calculate_cohens_d,
    calculate_pooled_std
)

# Calculate Cohen's d effect size
effect_size = calculate_cohens_d(
    group1_data=control_values,
    group2_data=treatment_values,
    pooled_std=True
)

# Interpret effect size
interpretation = interpret_cohens_d(effect_size)
print(f"Effect size: {effect_size:.3f} ({interpretation})")
```

#### Fold Change

```python
from isospec_data_tools.analysis.core.effect_sizes import calculate_fold_change

# Calculate fold change
fold_change = calculate_fold_change(
    group1_data=control_values,
    group2_data=treatment_values,
    log_transform=True
)
```

### Multiple Comparisons (`multiple_comparisons.py`)

Comprehensive multiple testing correction methods.

#### Bonferroni Correction

```python
from isospec_data_tools.analysis.core.multiple_comparisons import bonferroni_correction

# Simple Bonferroni correction
corrected_p_values = bonferroni_correction(
    p_values=raw_p_values,
    alpha=0.05
)
```

#### Benjamini-Hochberg FDR

```python
from isospec_data_tools.analysis.core.multiple_comparisons import benjamini_hochberg_correction

# FDR correction
fdr_results = benjamini_hochberg_correction(
    p_values=raw_p_values,
    alpha=0.05
)
```

#### Comprehensive Adjustment

```python
from isospec_data_tools.analysis.core.multiple_comparisons import adjust_p_values

# Multiple methods available
adjusted_results = adjust_p_values(
    p_values=raw_p_values,
    method="holm",  # Options: bonferroni, holm, benjamini_hochberg, sidak
    alpha=0.05
)
```

### Project Configuration (`project_config.py`)

Dataclass-based configuration system for reproducible analysis.

#### Basic Configuration

```python
from isospec_data_tools.analysis.core.project_config import ProjectConfig

# Create configuration
config = ProjectConfig(
    study_name="metabolomics_pilot",
    normalization_method="total_abundance",
    imputation_method="qc_min",
    statistical_test="welch",
    multiple_testing_correction="bonferroni",
    significance_threshold=0.05,
    effect_size_threshold=0.2
)
```

#### Advanced Configuration

```python
# Advanced configuration with custom parameters
config = ProjectConfig(
    study_name="proteomics_longitudinal",
    normalization_method="median_quotient",
    imputation_method="median",
    statistical_test="student",
    multiple_testing_correction="benjamini_hochberg",
    significance_threshold=0.01,
    effect_size_threshold=0.5,

    # Custom parameters
    custom_parameters={
        "batch_correction": True,
        "outlier_detection": "iqr",
        "transformation": "log10"
    }
)
```

#### Preset Configurations

```python
# Load preset configurations
metabolomics_config = ProjectConfig.load_preset("metabolomics_default")
proteomics_config = ProjectConfig.load_preset("proteomics_default")
glycomics_config = ProjectConfig.load_preset("glycomics_default")

# Modify preset
custom_config = metabolomics_config.modify(
    significance_threshold=0.01,
    effect_size_threshold=0.3
)
```

## Usage Examples

### Complete Statistical Analysis

```python
from isospec_data_tools.analysis.core import (
    perform_welch_t_test,
    calculate_cohens_d,
    adjust_p_values
)

# Perform statistical test
t_results = perform_welch_t_test(
    group1_data=control_group,
    group2_data=treatment_group
)

# Calculate effect size
effect_size = calculate_cohens_d(
    group1_data=control_group,
    group2_data=treatment_group
)

# Apply multiple testing correction
corrected_p_value = adjust_p_values(
    p_values=[t_results['p_value']],
    method="bonferroni"
)[0]

# Combine results
result = {
    'statistic': t_results['statistic'],
    'p_value': t_results['p_value'],
    'p_value_corrected': corrected_p_value,
    'effect_size': effect_size,
    'significant': corrected_p_value < 0.05
}
```

### Batch Processing

```python
import pandas as pd
from isospec_data_tools.analysis.core import perform_welch_t_test, adjust_p_values

# Batch processing for multiple features
results = []
for feature in metabolite_columns:
    control_data = data[data['group'] == 'control'][feature]
    treatment_data = data[data['group'] == 'treatment'][feature]

    t_result = perform_welch_t_test(control_data, treatment_data)
    results.append({
        'feature': feature,
        'statistic': t_result['statistic'],
        'p_value': t_result['p_value']
    })

# Convert to DataFrame
results_df = pd.DataFrame(results)

# Apply multiple testing correction
results_df['p_value_corrected'] = adjust_p_values(
    results_df['p_value'],
    method="benjamini_hochberg"
)
```

### Configuration-Driven Analysis

```python
from isospec_data_tools.analysis.core import ProjectConfig

# Load configuration
config = ProjectConfig.load_from_file("analysis_config.json")

# Use configuration to drive analysis
def run_configured_analysis(data, config):
    # Normalization based on config
    if config.normalization_method == "total_abundance":
        normalized_data = total_abundance_normalization(data)
    elif config.normalization_method == "median_quotient":
        normalized_data = median_quotient_normalization(data)

    # Statistical test based on config
    if config.statistical_test == "welch":
        test_func = perform_welch_t_test
    elif config.statistical_test == "student":
        test_func = perform_student_t_test

    # Multiple testing correction based on config
    def correct_p_values(p_values):
        return adjust_p_values(p_values, method=config.multiple_testing_correction)

    return {
        'normalized_data': normalized_data,
        'test_function': test_func,
        'correction_function': correct_p_values
    }

# Run analysis
analysis_components = run_configured_analysis(data, config)
```

## Statistical Considerations

### Assumptions and Validation

Each statistical function includes assumption checking:

```python
# Example: T-test with assumption checking
def perform_welch_t_test_with_checks(group1_data, group2_data):
    # Check for normality
    from scipy.stats import shapiro

    shapiro_stat1, shapiro_p1 = shapiro(group1_data)
    shapiro_stat2, shapiro_p2 = shapiro(group2_data)

    if shapiro_p1 < 0.05 or shapiro_p2 < 0.05:
        warnings.warn("Data may not be normally distributed. Consider non-parametric tests.")

    # Perform test
    return perform_welch_t_test(group1_data, group2_data)
```

### Power Analysis

```python
from isospec_data_tools.analysis.core.power_analysis import calculate_power

# Calculate statistical power
power = calculate_power(
    effect_size=0.5,
    alpha=0.05,
    n1=20,
    n2=20,
    test_type="welch"
)

print(f"Statistical power: {power:.3f}")
```

### Sample Size Calculations

```python
from isospec_data_tools.analysis.core.power_analysis import calculate_sample_size

# Calculate required sample size
n_required = calculate_sample_size(
    effect_size=0.5,
    alpha=0.05,
    power=0.80,
    test_type="welch"
)

print(f"Required sample size per group: {n_required}")
```

## Error Handling

The core module provides comprehensive error handling:

```python
from isospec_data_tools.analysis.utils.exceptions import (
    StatisticalError,
    InsufficientDataError,
    AssumptionViolationError
)

try:
    result = perform_welch_t_test(group1_data, group2_data)
except InsufficientDataError as e:
    print(f"Insufficient data: {e}")
except AssumptionViolationError as e:
    print(f"Assumption violation: {e}")
except StatisticalError as e:
    print(f"Statistical error: {e}")
```

## Performance Considerations

### Vectorized Operations

```python
import numpy as np

# Vectorized t-test for multiple features
def vectorized_t_test(data, group_col, feature_cols):
    results = []

    for feature in feature_cols:
        group1 = data[data[group_col] == 'control'][feature].values
        group2 = data[data[group_col] == 'treatment'][feature].values

        result = perform_welch_t_test(group1, group2)
        results.append(result)

    return results
```

### Memory Efficiency

```python
# Memory-efficient processing for large datasets
def process_large_dataset(data, chunk_size=1000):
    feature_cols = [col for col in data.columns if col.startswith('feature_')]

    results = []
    for i in range(0, len(feature_cols), chunk_size):
        chunk = feature_cols[i:i+chunk_size]
        chunk_results = vectorized_t_test(data, 'group', chunk)
        results.extend(chunk_results)

    return results
```

## Testing and Validation

The core module includes comprehensive tests:

```python
# Example test structure
def test_welch_t_test():
    # Test with known data
    control = np.array([1, 2, 3, 4, 5])
    treatment = np.array([3, 4, 5, 6, 7])

    result = perform_welch_t_test(control, treatment)

    assert 'statistic' in result
    assert 'p_value' in result
    assert 0 <= result['p_value'] <= 1

    # Test with identical groups
    result_identical = perform_welch_t_test(control, control)
    assert result_identical['p_value'] > 0.05
```

## Integration with Other Modules

The core module integrates seamlessly with other analysis components:

```python
# Example integration with preprocessing
from isospec_data_tools.analysis.preprocessing import DataWrangler
from isospec_data_tools.analysis.core import perform_welch_t_test

# Combined workflow
wrangler = DataWrangler()
normalized_data = wrangler.total_abundance_normalization(data, feature_cols)

# Apply core statistical functions
results = []
for feature in feature_cols:
    control = normalized_data[normalized_data['group'] == 'control'][feature]
    treatment = normalized_data[normalized_data['group'] == 'treatment'][feature]

    result = perform_welch_t_test(control, treatment)
    results.append(result)
```

For more examples and detailed API documentation, see the main analysis module documentation.
