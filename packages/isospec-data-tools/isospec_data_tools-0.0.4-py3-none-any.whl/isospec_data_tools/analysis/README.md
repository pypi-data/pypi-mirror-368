# Analysis Package

The analysis package provides comprehensive statistical analysis capabilities for omics data, with a focus on metabolomics, proteomics, and glycomics research.

## Architecture Overview

The package is organized into a modular architecture following the MECE (Mutually Exclusive, Collectively Exhaustive) principle:

```
analysis/
├── __init__.py                 # Main exports and entry points
├── core/                       # Statistical building blocks
│   ├── effect_sizes.py        # Effect size calculations
│   ├── multiple_comparisons.py # Multiple testing corrections
│   ├── project_config.py      # Configuration system
│   └── statistical_tests.py   # Core statistical functions
├── preprocessing/              # Data preparation
│   ├── normalizers.py         # Data normalization methods
│   ├── transformers.py        # Data transformation utilities
│   └── validators.py          # Data quality validation
├── specialized/                # Domain-specific analysis
│   ├── ancova_analysis.py     # ANCOVA statistical analysis
│   ├── confounder_analysis.py # Confounder identification
│   └── glycowork_integration.py # Glycowork library integration
├── modeling/                   # Machine learning utilities
│   ├── clustering.py          # Clustering algorithms
│   └── model_evaluation.py    # Model training and evaluation
└── utils/                      # Shared utilities
    ├── data_helpers.py        # Data manipulation helpers
    └── exceptions.py          # Custom exceptions
```

## Key Components

### Core Statistical Functions

The core module provides fundamental statistical building blocks:

- **Statistical Tests**: T-tests (Student's, Welch's), ANCOVA, chi-square tests
- **Effect Sizes**: Cohen's d, fold change calculations
- **Multiple Comparisons**: Bonferroni, Benjamini-Hochberg, Holm corrections
- **Project Configuration**: Dataclass-based configuration system

### Preprocessing Pipeline

The preprocessing module handles data preparation:

- **Normalization**: Total abundance, median quotient normalization
- **Imputation**: QC-based imputation (default), statistical methods
- **Validation**: Data quality checks and outlier detection
- **Transformation**: Log transformation, scaling, centering

### Specialized Analyzers

Domain-specific analysis tools:

- **ConfounderAnalyzer**: Systematic confounder identification and visualization
- **ANCOVAAnalyzer**: ANCOVA with multiple covariates and factors
- **GlycoworkAnalyzer**: Integration with glycowork library for glycan analysis

### Machine Learning Utilities

- **ClusterAnalyzer**: Multiple clustering algorithms with evaluation metrics
- **ModelTrainer**: Classification models with hyperparameter tuning

## Quick Start

### Basic Usage

```python
from isospec_data_tools.analysis import StatisticalAnalyzer, DataWrangler

# Initialize components
analyzer = StatisticalAnalyzer()
wrangler = DataWrangler()

# Preprocess data
normalized_data = wrangler.total_abundance_normalization(
    data=raw_data,
    feature_cols=metabolite_columns
)

# Perform statistical analysis
results = analyzer.perform_t_test(
    data=normalized_data,
    group_col="treatment",
    feature_cols=metabolite_columns
)
```

### Using Configuration System

```python
from isospec_data_tools.analysis import ProjectConfig, StatisticalAnalyzer

# Create configuration
config = ProjectConfig(
    study_name="metabolomics_study",
    normalization_method="total_abundance",
    imputation_method="qc_min",
    statistical_test="welch",
    multiple_testing_correction="bonferroni"
)

# Use configuration
analyzer = StatisticalAnalyzer(config=config)
results = analyzer.run_full_analysis(data=study_data)
```

## Data Requirements

### Input Data Format

The analysis package expects data in "tidy" format:

```
sample_id | feature_1 | feature_2 | ... | group | batch | SampleType
sample_1  | 1000.5    | 2500.3    | ... | ctrl  | B1    | Sample
sample_2  | 1200.8    | 2300.1    | ... | trt   | B1    | Sample
qc_1      | 1100.2    | 2400.5    | ... | QC    | B1    | QC
```

### Required Columns

- **Feature columns**: Numeric data (metabolites, proteins, etc.)
- **Group column**: Categorical variable for comparisons
- **SampleType**: Sample classification (Sample, QC, Blank, etc.)
- **Batch**: Batch information (optional but recommended)

## Common Workflows

### 1. Basic Statistical Analysis

```python
from isospec_data_tools.analysis import StatisticalAnalyzer, DataWrangler

# Step 1: Preprocess data
wrangler = DataWrangler()
normalized_data = wrangler.total_abundance_normalization(data, feature_cols)
imputed_data = wrangler.impute_missing_values(normalized_data, method="qc_min")

# Step 2: Statistical analysis
analyzer = StatisticalAnalyzer()
t_results = analyzer.perform_t_test(
    data=imputed_data,
    group_col="treatment",
    feature_cols=feature_cols
)

# Step 3: Multiple testing correction
corrected_results = analyzer.adjust_p_values(t_results, method="bonferroni")
```

### 2. Confounder Analysis

```python
from isospec_data_tools.analysis import ConfounderAnalyzer

# Initialize analyzer
confounder = ConfounderAnalyzer(
    data=study_data,
    target_col="disease_status",
    feature_cols=metabolite_columns
)

# Identify confounders
confounders = confounder.identify_confounders(
    potential_confounders=["age", "sex", "bmi"],
    significance_threshold=0.05
)

# Generate visualization
confounder.plot_confounder_relationships(output_dir="plots")
```

### 3. ANCOVA Analysis

```python
from isospec_data_tools.analysis import ANCOVAAnalyzer

# Initialize analyzer
ancova = ANCOVAAnalyzer(
    data=metabolomics_data,
    dependent_vars=metabolite_columns,
    factor_col="treatment",
    covariate_cols=["age", "bmi"]
)

# Perform analysis
results = ancova.perform_ancova_analysis()
significant_features = ancova.get_significant_features(alpha=0.05)
```

### 4. Machine Learning Analysis

```python
from isospec_data_tools.analysis import ClusterAnalyzer, ModelTrainer

# Clustering analysis
cluster = ClusterAnalyzer(data, feature_cols)
cluster_results = cluster.perform_clustering(
    methods=["kmeans", "hierarchical"],
    n_clusters_range=(2, 8)
)

# Classification
trainer = ModelTrainer(data, target_col="disease_status", feature_cols=feature_cols)
models = trainer.train_classification_models(
    algorithms=["random_forest", "svm"]
)
```

## Design Principles

### Code Quality Standards

- **Type Hints**: All functions have comprehensive type annotations
- **Google-style Docstrings**: Detailed documentation for all public APIs
- **Error Handling**: Robust exception handling with informative messages
- **Logging**: Strategic logging for debugging and monitoring

### Statistical Rigor

- **Multiple Comparison Corrections**: Automatic handling of multiple testing
- **Effect Size Calculations**: Beyond p-values, includes effect sizes
- **Assumption Checking**: Validates statistical assumptions where applicable
- **Reproducibility**: Consistent random seeds and deterministic algorithms

### Modular Architecture

- **Single Responsibility**: Each module has one well-defined purpose
- **Composition over Inheritance**: Favor composition for flexibility
- **Configuration-Driven**: Behavior controlled through configuration objects
- **Extensibility**: Easy to add new statistical methods or analyzers

## Testing and Validation

The package includes comprehensive testing:

- **Unit Tests**: Individual function validation
- **Integration Tests**: Full workflow testing
- **Statistical Validation**: Correctness of statistical methods
- **Edge Case Testing**: Robustness with missing data, outliers

```bash
# Run all tests
make test

# Run specific module tests
uv run python -m pytest tests/test_analysis/ -v

# Run with coverage
uv run python -m pytest tests/test_analysis/ --cov=src/isospec_data_tools/analysis
```

## Performance Considerations

### Optimization Strategies

- **Vectorized Operations**: Uses NumPy/Pandas for efficient computation
- **Memory Management**: Efficient handling of large datasets
- **Caching**: Results caching for expensive computations
- **Parallel Processing**: Multi-core support where applicable

### Scalability

- **Chunked Processing**: Handles datasets larger than memory
- **Sparse Matrix Support**: Efficient handling of sparse omics data
- **Streaming**: Process data in chunks for memory efficiency

## Integration with Other Modules

### Visualization Integration

```python
from isospec_data_tools.visualization.analysis import plot_differential_analysis

# Generate plots directly from analysis results
plot_differential_analysis(
    statistical_results=t_test_results,
    data=metabolomics_data,
    output_dir="plots"
)
```

### IO Utilities Integration

```python
from isospec_data_tools.io_utils import MZMineFeatureTable

# Load data using IO utilities
loader = MZMineFeatureTable("feature_table.csv")
data = loader.load_data()

# Process with analysis module
normalized_data = wrangler.total_abundance_normalization(data, feature_cols)
```

## Migration Guide

### From Legacy Interfaces

The package provides backward compatibility wrappers:

```python
# Legacy interface (deprecated)
from isospec_data_tools.analysis import normalize_data, perform_ttest

# New interface (recommended)
from isospec_data_tools.analysis import DataWrangler, StatisticalAnalyzer

wrangler = DataWrangler()
analyzer = StatisticalAnalyzer()
```

### Configuration Migration

```python
# Old approach
results = perform_analysis(
    data=data,
    normalization="total_abundance",
    imputation="qc_min",
    test="welch"
)

# New approach
config = ProjectConfig(
    normalization_method="total_abundance",
    imputation_method="qc_min",
    statistical_test="welch"
)
analyzer = StatisticalAnalyzer(config=config)
results = analyzer.run_full_analysis(data)
```

## Troubleshooting

### Common Issues

1. **Missing QC Samples**: Ensure QC samples are properly labeled in SampleType column
2. **Normalization Errors**: Check for negative values or zeros in feature data
3. **Statistical Assumptions**: Verify data distribution assumptions for tests
4. **Memory Issues**: Use chunked processing for large datasets

### Debugging Tips

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging
analyzer = StatisticalAnalyzer(debug=True)
```

## Contributing

1. Follow the existing code patterns and conventions
2. Add comprehensive tests for new functionality
3. Update documentation for API changes
4. Ensure all quality checks pass (`make check`)

For detailed development guidelines, see the project's CLAUDE.md file.

## License

This package is part of the isospec-data-tools project, licensed under the MIT License.
