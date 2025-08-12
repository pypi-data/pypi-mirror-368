# Analysis Workflows

This guide provides comprehensive workflows for common analysis tasks using the isospec-data-tools analysis module.

## Table of Contents

1. [Basic Statistical Analysis](#basic-statistical-analysis)
2. [Confounder Analysis](#confounder-analysis)
3. [ANCOVA Analysis](#ancova-analysis)
4. [Machine Learning Analysis](#machine-learning-analysis)
5. [Glycowork Integration](#glycowork-integration)
6. [Full Analysis Pipeline](#full-analysis-pipeline)

## Basic Statistical Analysis

### Workflow Overview

This workflow demonstrates a complete statistical analysis pipeline from data preprocessing through result interpretation.

### Step 1: Data Preparation

```python
import pandas as pd
from isospec_data_tools.analysis import DataWrangler, StatisticalAnalyzer, create_project_config

# Load your data
data = pd.read_csv("metabolomics_data.csv")

# Define feature columns (metabolites)
feature_cols = [col for col in data.columns if col.startswith("metabolite_")]

# Initialize data wrangler
wrangler = DataWrangler()
```

### Step 2: Data Preprocessing

```python
# Step 2a: Data normalization
normalized_data = wrangler.total_abundance_normalization(
    data=data,
    feature_cols=feature_cols
)

# Step 2b: Handle missing values using QC-based imputation
imputed_data = wrangler.impute_missing_values(
    data=normalized_data,
    method="qc_min",
    sample_type_col="SampleType",
    qc_samples=["QC", "EQC"],
    replacement_value=1  # Replace 1s with NaN before imputation
)

# Step 2c: Data validation
validation_results = wrangler.validate_data_quality(
    data=imputed_data,
    feature_cols=feature_cols,
    sample_type_col="SampleType"
)
print(f"Data quality score: {validation_results['quality_score']}")
```

### Step 3: Statistical Analysis

```python
# Initialize statistical analyzer
analyzer = StatisticalAnalyzer()

# Perform Welch's t-test (recommended for metabolomics)
t_results = analyzer.perform_t_test(
    data=imputed_data,
    group_col="treatment",
    feature_cols=feature_cols,
    test_type="welch"
)

# Calculate effect sizes
effect_sizes = analyzer.calculate_effect_sizes(
    data=imputed_data,
    group_col="treatment",
    feature_cols=feature_cols,
    method="cohens_d"
)

# Merge results
results = pd.merge(t_results, effect_sizes, on="feature")
```

### Step 4: Multiple Testing Correction

```python
# Apply Bonferroni correction
corrected_results = analyzer.adjust_p_values(
    results,
    p_value_col="p_value",
    method="bonferroni"
)

# Filter significant results
significant_results = corrected_results[
    corrected_results["p_value_adjusted"] < 0.05
]

print(f"Significant features: {len(significant_results)}")
```

### Step 5: Results Interpretation

```python
# Sort by effect size
significant_results_sorted = significant_results.sort_values(
    "effect_size",
    key=abs,
    ascending=False
)

# Generate summary statistics
summary = analyzer.generate_summary_statistics(
    results=significant_results_sorted,
    effect_size_threshold=0.5
)

print("Analysis Summary:")
print(f"- Total features tested: {len(results)}")
print(f"- Significant features: {len(significant_results)}")
print(f"- Large effect sizes (>0.5): {summary['large_effects']}")
print(f"- Medium effect sizes (0.2-0.5): {summary['medium_effects']}")
```

## Confounder Analysis

### Workflow Overview

Systematic identification and visualization of potential confounders in your study.

### Step 1: Initialize Confounder Analyzer

```python
from isospec_data_tools.analysis import ConfounderAnalyzer

# Initialize analyzer
confounder = ConfounderAnalyzer(
    data=study_data,
    target_col="disease_status",
    feature_cols=metabolite_columns
)
```

### Step 2: Identify Potential Confounders

```python
# Define potential confounders
potential_confounders = [
    "age", "sex", "bmi", "smoking_status",
    "medication_use", "sample_collection_time"
]

# Systematic confounder identification
confounders = confounder.identify_confounders(
    potential_confounders=potential_confounders,
    significance_threshold=0.05,
    effect_size_threshold=0.2
)

print(f"Identified confounders: {confounders}")
```

### Step 3: Detailed Confounder Analysis

```python
# Analyze each confounder
for confounder_var in confounders:
    analysis_results = confounder.analyze_confounder_effects(
        confounder_var=confounder_var,
        feature_subset=metabolite_columns[:50]  # Analyze subset for efficiency
    )

    print(f"\nConfounder: {confounder_var}")
    print(f"- Features affected: {analysis_results['affected_features']}")
    print(f"- Mean effect size: {analysis_results['mean_effect_size']:.3f}")
```

### Step 4: Visualization

```python
# Generate confounder visualizations
confounder.plot_confounder_relationships(
    confounders=confounders,
    output_dir="confounder_plots",
    plot_types=["heatmap", "scatter", "boxplot"]
)

# Generate confounder report
report = confounder.generate_confounder_report(
    confounders=confounders,
    output_dir="confounder_analysis",
    include_plots=True
)
```

### Step 5: Adjusted Analysis

```python
# Perform analysis accounting for confounders
adjusted_results = confounder.perform_adjusted_analysis(
    confounders=confounders,
    method="linear_regression",
    feature_cols=metabolite_columns
)

# Compare with unadjusted results
comparison = confounder.compare_adjusted_unadjusted(
    adjusted_results=adjusted_results,
    unadjusted_results=t_results
)
```

## ANCOVA Analysis

### Workflow Overview

Analysis of covariance (ANCOVA) for controlling continuous covariates while testing categorical factors.

### Step 1: Initialize ANCOVA Analyzer

```python
from isospec_data_tools.analysis import ANCOVAAnalyzer

# Initialize ANCOVA analyzer
ancova = ANCOVAAnalyzer(
    data=metabolomics_data,
    dependent_vars=metabolite_columns,
    factor_col="treatment",
    covariate_cols=["age", "bmi"]
)
```

### Step 2: Assumption Checking

```python
# Check ANCOVA assumptions
assumptions = ancova.check_assumptions(
    sample_size=len(metabolomics_data),
    significance_level=0.05
)

print("ANCOVA Assumptions:")
for assumption, result in assumptions.items():
    print(f"- {assumption}: {'✓' if result['passed'] else '✗'}")
    if not result['passed']:
        print(f"  Warning: {result['warning']}")
```

### Step 3: Perform ANCOVA Analysis

```python
# Run ANCOVA analysis
ancova_results = ancova.perform_ancova_analysis(
    interaction_terms=True,  # Include interaction terms
    multiple_testing_correction="bonferroni"
)

# Extract results components
factor_effects = ancova_results['factor_effects']
covariate_effects = ancova_results['covariate_effects']
interaction_effects = ancova_results['interaction_effects']
```

### Step 4: Result Interpretation

```python
# Get significant features
significant_features = ancova.get_significant_features(
    alpha=0.05,
    multiple_testing_method="bonferroni"
)

# Analyze effect sizes
effect_analysis = ancova.analyze_effect_sizes(
    results=ancova_results,
    effect_size_threshold=0.1
)

print(f"Significant features for treatment: {len(significant_features['treatment'])}")
print(f"Significant features for age: {len(significant_features['age'])}")
print(f"Significant features for BMI: {len(significant_features['bmi'])}")
```

### Step 5: Post-hoc Analysis

```python
# Perform post-hoc comparisons
posthoc_results = ancova.perform_posthoc_analysis(
    significant_features=significant_features['treatment'],
    method="tukey"
)

# Generate ANCOVA report
report = ancova.generate_ancova_report(
    output_dir="ancova_analysis",
    include_plots=True,
    include_assumptions=True
)
```

## Machine Learning Analysis

### Workflow Overview

Comprehensive machine learning analysis including clustering and classification.

### Step 1: Clustering Analysis

```python
from isospec_data_tools.analysis import ClusterAnalyzer

# Initialize cluster analyzer
cluster = ClusterAnalyzer(
    data=metabolomics_data,
    feature_cols=metabolite_columns
)

# Perform multiple clustering methods
cluster_results = cluster.perform_clustering(
    methods=["kmeans", "hierarchical", "dbscan"],
    n_clusters_range=(2, 10),
    scaling_method="standard"
)

# Evaluate clustering quality
evaluation = cluster.evaluate_clustering_quality(
    cluster_results=cluster_results,
    metrics=["silhouette", "calinski_harabasz", "davies_bouldin"]
)

# Select optimal clustering
optimal_clustering = cluster.select_optimal_clustering(
    evaluation_results=evaluation,
    selection_criteria="silhouette"
)
```

### Step 2: Classification Analysis

```python
from isospec_data_tools.analysis import ModelTrainer

# Initialize model trainer
trainer = ModelTrainer(
    data=metabolomics_data,
    target_col="disease_status",
    feature_cols=metabolite_columns
)

# Feature selection
selected_features = trainer.select_features(
    method="univariate",
    k_features=100,
    scoring="f_classif"
)

# Train multiple models
models = trainer.train_classification_models(
    feature_cols=selected_features,
    algorithms=["random_forest", "svm", "logistic_regression", "xgboost"],
    cv_folds=5,
    hyperparameter_tuning=True
)
```

### Step 3: Model Evaluation

```python
# Evaluate model performance
performance = trainer.evaluate_model_performance(
    models=models,
    metrics=["accuracy", "precision", "recall", "f1", "roc_auc"],
    cv_folds=5
)

# Feature importance analysis
feature_importance = trainer.analyze_feature_importance(
    models=models,
    feature_names=selected_features,
    top_n=20
)

# Generate model comparison report
model_report = trainer.generate_model_report(
    models=models,
    performance_results=performance,
    feature_importance=feature_importance,
    output_dir="ml_analysis"
)
```

### Step 4: Visualization

```python
from isospec_data_tools.visualization.analysis import (
    plot_cluster_analysis,
    plot_model_performance
)

# Generate clustering plots
plot_cluster_analysis(
    cluster_results=cluster_results,
    data=metabolomics_data,
    feature_cols=metabolite_columns[:2],  # Use first 2 features for visualization
    output_dir="cluster_plots"
)

# Generate model performance plots
plot_model_performance(
    performance_results=performance,
    output_dir="model_plots"
)
```

## Glycowork Integration

### Workflow Overview

Integration with glycowork library for specialized glycan analysis.

### Step 1: Initialize Glycowork Analyzer

```python
from isospec_data_tools.analysis import GlycoworkAnalyzer

# Initialize glycowork analyzer
glyco = GlycoworkAnalyzer(
    glycan_data=glycomics_data,
    glycan_columns=glycan_feature_columns
)
```

### Step 2: Glycan Structure Analysis

```python
# Analyze glycan structures
structure_analysis = glyco.analyze_glycan_structures(
    group_col="treatment",
    analysis_type="linkage_analysis",
    include_motifs=True
)

# Pathway analysis
pathway_results = glyco.perform_pathway_analysis(
    significant_glycans=structure_analysis['significant_structures'],
    pathway_database="kegg"
)
```

### Step 3: Comparative Analysis

```python
# Compare glycan profiles between groups
comparison_results = glyco.compare_glycan_profiles(
    group_col="treatment",
    statistical_method="welch_t_test",
    multiple_testing_correction="bonferroni"
)

# Identify discriminative glycans
discriminative_glycans = glyco.identify_discriminative_glycans(
    comparison_results=comparison_results,
    effect_size_threshold=0.5
)
```

### Step 4: Visualization

```python
# Generate glycowork-specific visualizations
glyco.plot_glycan_heatmap(
    glycan_data=glycomics_data,
    group_col="treatment",
    output_dir="glycan_plots"
)

glyco.plot_pathway_network(
    pathway_results=pathway_results,
    output_dir="glycan_plots"
)
```

## Full Analysis Pipeline

### Workflow Overview

Complete end-to-end analysis pipeline combining all components.

### Step 1: Configuration Setup

```python
from isospec_data_tools.analysis import create_project_config
from isospec_data_tools.analysis.core.project_config import (
    DataStructureConfig,
    StatisticalConfig
)

# Create comprehensive configuration
data_config = DataStructureConfig(
    sample_column="SampleID",
    sample_type_column="SampleType",
    feature_prefix="metabolite_",
    qc_identifier=["QC", "EQC"]
)

stats_config = StatisticalConfig(
    cv_threshold=30.0,
    effect_size_threshold=0.2,
    p_value_threshold=0.05
)

config = create_project_config(
    data_config=data_config,
    stats_config=stats_config
)
```

### Step 2: Automated Analysis Pipeline

```python
from isospec_data_tools.analysis import AnalysisPipeline

# Initialize pipeline
pipeline = AnalysisPipeline(config=config)

# Run complete analysis
results = pipeline.run_full_analysis(
    data=study_data,
    feature_cols=metabolite_columns,
    target_col="disease_status",
    output_dir="full_analysis_results"
)
```

### Step 3: Results Summary

```python
# Generate comprehensive report
summary_report = pipeline.generate_comprehensive_report(
    results=results,
    output_dir="analysis_summary",
    include_plots=True,
    include_raw_data=False
)

# Print key findings
print("Analysis Summary:")
print(f"- Preprocessing: {results['preprocessing']['status']}")
print(f"- Statistical tests: {results['statistical']['significant_features']} significant")
print(f"- Confounders identified: {len(results['confounders']['identified'])}")
print(f"- ANCOVA significant: {results['ancova']['significant_features']}")
print(f"- Best ML model: {results['ml']['best_model']['algorithm']}")
print(f"- ML accuracy: {results['ml']['best_model']['accuracy']:.3f}")
```

## Best Practices

### Data Quality Considerations

1. **Missing Data**: Always check missing data patterns before imputation
2. **Outliers**: Identify and handle outliers appropriately
3. **Batch Effects**: Include batch information in analysis
4. **QC Samples**: Ensure adequate QC samples for normalization

### Statistical Considerations

1. **Multiple Testing**: Always apply appropriate corrections
2. **Effect Sizes**: Report effect sizes alongside p-values
3. **Assumptions**: Check statistical assumptions
4. **Power Analysis**: Consider statistical power for your study

### Computational Considerations

1. **Memory Usage**: Monitor memory usage with large datasets
2. **Parallelization**: Use parallel processing when available
3. **Reproducibility**: Set random seeds for reproducible results
4. **Caching**: Use caching for expensive computations

### Documentation

1. **Parameter Logging**: Log all analysis parameters
2. **Version Control**: Track software versions
3. **Metadata**: Include comprehensive metadata
4. **Validation**: Document validation steps

## Troubleshooting

### Common Issues

1. **Normalization Failures**: Check for negative values or zeros
2. **Imputation Errors**: Ensure QC samples are properly labeled
3. **Statistical Errors**: Verify data distributions and assumptions
4. **Memory Issues**: Use chunked processing for large datasets

### Performance Optimization

1. **Feature Selection**: Reduce dimensionality before analysis
2. **Sampling**: Use representative subsets for exploration
3. **Parallel Processing**: Utilize multiple cores
4. **Caching**: Cache intermediate results

For additional support, consult the API documentation or create an issue on the project repository.
