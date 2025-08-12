# Analysis Visualization Guide

The visualization module provides comprehensive plotting functions specifically designed for the analysis package, enabling clear and informative visualizations of statistical results, clustering outcomes, and model performance.

## Overview

The analysis visualization components are organized into specialized modules:

- **Preprocessing Plots**: Visualizations for data preprocessing operations
- **Cluster Plots**: Visualizations for clustering analysis results
- **Confounder Plots**: Visualizations for confounder analysis
- **Differential Plots**: Visualizations for statistical testing results
- **Method Comparison Plots**: Visualizations for method comparison studies

## Preprocessing Visualization

The preprocessing visualization module provides comprehensive tools for visualizing data quality, missing value patterns, imputation impact, and normalization effects.

### Missing Data Analysis

```python
from isospec_data_tools.visualization.analysis import PreprocessingPlotter

# Initialize preprocessing plotter
plotter = PreprocessingPlotter(
    data=metabolomics_data,
    feature_columns=metabolite_columns,
    sample_column="SampleID",
    sample_type_column="SampleType"
)

# Visualize missing data patterns
missing_plots = plotter.plot_missing_data_analysis(
    output_dir="missing_data_plots"
)

# Generate missing data heatmap
missing_heatmap = plotter.plot_missing_data_heatmap(
    cluster_samples=True,
    cluster_features=True,
    output_path="missing_data_heatmap.png"
)

# Plot missing data statistics
missing_stats = plotter.plot_missing_data_statistics(
    output_path="missing_data_stats.png"
)
```

### Imputation Impact Analysis

```python
# Compare data before and after imputation
imputation_plots = plotter.plot_imputation_impact(
    original_data=raw_data,
    imputed_data=imputed_data,
    method="qc_min",
    output_dir="imputation_impact"
)

# Visualize imputation method comparison
method_comparison = plotter.plot_imputation_method_comparison(
    imputation_methods=["qc_min", "median", "mean"],
    output_dir="imputation_comparison"
)

# Show QC-based imputation details
qc_imputation = plotter.plot_qc_imputation_details(
    qc_samples=["QC", "EQC"],
    output_path="qc_imputation_details.png"
)
```

### Feature Abundance Classification

```python
from isospec_data_tools.visualization.analysis import FeatureAbundanceClassifier

# Initialize feature classifier
classifier = FeatureAbundanceClassifier(
    data=metabolomics_data,
    feature_columns=metabolite_columns
)

# Classify and visualize feature abundance distributions
abundance_plots = classifier.plot_abundance_classification(
    output_dir="abundance_classification"
)

# Generate feature abundance heatmap
abundance_heatmap = classifier.plot_abundance_heatmap(
    classification_results=abundance_results,
    output_path="abundance_heatmap.png"
)

# Plot abundance distribution statistics
abundance_stats = classifier.plot_abundance_statistics(
    output_path="abundance_statistics.png"
)

# Feature quality assessment with QC samples
quality_plots = classifier.plot_feature_quality_assessment(
    qc_samples=qc_mask,
    cv_threshold=30.0,
    output_dir="feature_quality"
)
```

### CV Improvement Tracking

```python
from isospec_data_tools.visualization.analysis import CVAnalysisPlotter

# Initialize CV analyzer
cv_plotter = CVAnalysisPlotter(
    raw_data=raw_data,
    normalized_data=normalized_data,
    feature_columns=metabolite_columns,
    qc_samples=qc_mask
)

# Track CV improvements through normalization pipeline
cv_improvement = cv_plotter.plot_cv_improvement_analysis(
    normalization_methods=["raw", "total_abundance", "median_quotient"],
    output_dir="cv_improvement"
)

# Compare normalization methods
normalization_comparison = cv_plotter.plot_normalization_comparison(
    methods=["total_abundance", "median_quotient", "quantile"],
    output_dir="normalization_comparison"
)

# Visualize CV distributions
cv_distributions = cv_plotter.plot_cv_distributions(
    methods=["raw", "normalized"],
    output_path="cv_distributions.png"
)

# Plot CV improvement heatmap
cv_heatmap = cv_plotter.plot_cv_improvement_heatmap(
    improvement_threshold=5.0,
    output_path="cv_improvement_heatmap.png"
)
```

### Configuration and Customization

```python
from isospec_data_tools.visualization.analysis import (
    DataStructureConfig,
    StatisticalConfig,
    VisualizationConfig
)

# Configure data structure mapping
data_config = DataStructureConfig(
    sample_column="SampleID",
    sample_type_column="SampleType",
    feature_prefix="FT-",
    qc_identifier=["QC", "EQC"],
    metadata_columns=["injection_order", "batch"]
)

# Configure statistical thresholds
stats_config = StatisticalConfig(
    cv_threshold=30.0,
    cv_ranges=[(0, 10, "<10%"), (10, 20, "10-20%"), (20, 30, "20-30%"), (30, float("inf"), ">30%")],
    percentile_thresholds=(33.0, 67.0),
    improvement_categories=[
        (5, float("inf"), "Highly\nImproved\n(>5pp)", "darkgreen"),
        (2, 5, "Moderately\nImproved\n(2-5pp)", "green"),
        (-2, 2, "No Change\n(±2pp)", "gray"),
        (float("-inf"), -2, "Degraded\n(<-2pp)", "red")
    ]
)

# Configure visualization settings
viz_config = VisualizationConfig(
    figure_size=(12, 8),
    color_palette="viridis",
    save_format="png",
    dpi=300,
    show_plots=True
)

# Apply configurations to plotter
plotter = PreprocessingPlotter(
    data=metabolomics_data,
    feature_columns=metabolite_columns,
    data_config=data_config,
    stats_config=stats_config,
    viz_config=viz_config
)
```

### Legacy API Compatibility

```python
# For existing users, legacy wrapper classes are available
from isospec_data_tools.visualization.analysis import (
    LegacyPreprocessingPlotter,
    LegacyFeatureAbundanceClassifier
)

# Legacy preprocessing plotter (with deprecation warning)
legacy_plotter = LegacyPreprocessingPlotter(
    data=metabolomics_data,
    feature_columns=metabolite_columns
)

# Legacy feature classifier (with deprecation warning)
legacy_classifier = LegacyFeatureAbundanceClassifier(
    data=metabolomics_data,
    feature_columns=metabolite_columns
)

# Migration guide: Users need only change import paths
# Old: from preprocessing import PreprocessingPlotter
# New: from isospec_data_tools.visualization.analysis import PreprocessingPlotter
```

## Cluster Visualization

### Basic Cluster Plots

```python
from isospec_data_tools.visualization.analysis import plot_cluster_analysis

# Generate comprehensive cluster plots
plot_cluster_analysis(
    cluster_results=cluster_results,
    data=metabolomics_data,
    feature_cols=metabolite_columns[:2],  # Use first 2 features for 2D visualization
    output_dir="cluster_plots"
)
```

### Cluster Heatmaps

```python
from isospec_data_tools.visualization.analysis.cluster_plots import plot_cluster_heatmap

# Generate cluster heatmap
plot_cluster_heatmap(
    data=metabolomics_data,
    cluster_labels=cluster_results['kmeans']['labels'],
    feature_cols=metabolite_columns,
    cluster_method="kmeans",
    output_path="cluster_heatmap.png"
)
```

### Cluster Evaluation Plots

```python
from isospec_data_tools.visualization.analysis.cluster_plots import (
    plot_silhouette_analysis,
    plot_elbow_curve,
    plot_cluster_validation_metrics
)

# Silhouette analysis
plot_silhouette_analysis(
    data=metabolomics_data,
    cluster_labels=cluster_results['kmeans']['labels'],
    feature_cols=metabolite_columns,
    output_path="silhouette_analysis.png"
)

# Elbow curve for optimal k
plot_elbow_curve(
    k_range=range(2, 11),
    inertia_values=kmeans_inertias,
    output_path="elbow_curve.png"
)

# Cluster validation metrics
plot_cluster_validation_metrics(
    evaluation_results=cluster_evaluation_results,
    metrics=["silhouette", "calinski_harabasz", "davies_bouldin"],
    output_path="cluster_validation.png"
)
```

### PCA Cluster Visualization

```python
from isospec_data_tools.visualization.analysis.cluster_plots import plot_pca_clusters

# PCA visualization of clusters
plot_pca_clusters(
    data=metabolomics_data,
    cluster_labels=cluster_results['kmeans']['labels'],
    feature_cols=metabolite_columns,
    n_components=2,
    output_path="pca_clusters.png"
)
```

## Confounder Visualization

### Confounder Relationship Plots

```python
from isospec_data_tools.visualization.analysis import plot_confounder_relationships

# Generate confounder plots
plot_confounder_relationships(
    confounder_results=confounder_results,
    data=study_data,
    confounders=["age", "sex", "bmi"],
    output_dir="confounder_plots"
)
```

### Confounder Heatmaps

```python
from isospec_data_tools.visualization.analysis.confounder_plots import plot_confounder_heatmap

# Confounder correlation heatmap
plot_confounder_heatmap(
    data=study_data,
    confounders=["age", "sex", "bmi"],
    feature_cols=metabolite_columns,
    correlation_method="spearman",
    output_path="confounder_heatmap.png"
)
```

### Confounder Effect Plots

```python
from isospec_data_tools.visualization.analysis.confounder_plots import (
    plot_confounder_effects,
    plot_confounder_strength
)

# Confounder effect visualization
plot_confounder_effects(
    confounder_results=confounder_results,
    confounders=["age", "bmi"],
    effect_threshold=0.2,
    output_path="confounder_effects.png"
)

# Confounder strength visualization
plot_confounder_strength(
    strength_results=confounder_strength_results,
    confounders=["age", "sex", "bmi"],
    output_path="confounder_strength.png"
)
```

### Before/After Adjustment Plots

```python
from isospec_data_tools.visualization.analysis.confounder_plots import plot_adjustment_comparison

# Compare results before and after confounder adjustment
plot_adjustment_comparison(
    unadjusted_results=original_results,
    adjusted_results=adjusted_results,
    comparison_metric="p_value",
    output_path="adjustment_comparison.png"
)
```

## Differential Analysis Plots

### Volcano Plots

```python
from isospec_data_tools.visualization.analysis import plot_differential_analysis

# Generate differential analysis plots including volcano plots
plot_differential_analysis(
    statistical_results=t_test_results,
    data=metabolomics_data,
    analysis_type="t_test",
    output_dir="differential_plots"
)
```

### MA Plots

```python
from isospec_data_tools.visualization.analysis.differential_plots import plot_ma_plot

# MA plot for differential analysis
plot_ma_plot(
    statistical_results=t_test_results,
    log_fold_change_col="log_fold_change",
    mean_expression_col="mean_expression",
    p_value_col="p_value_adjusted",
    significance_threshold=0.05,
    output_path="ma_plot.png"
)
```

### P-value Distribution Plots

```python
from isospec_data_tools.visualization.analysis.differential_plots import (
    plot_p_value_distribution,
    plot_qq_plot
)

# P-value distribution
plot_p_value_distribution(
    p_values=t_test_results['p_value'],
    output_path="p_value_distribution.png"
)

# Q-Q plot for p-values
plot_qq_plot(
    p_values=t_test_results['p_value'],
    output_path="qq_plot.png"
)
```

### Effect Size Plots

```python
from isospec_data_tools.visualization.analysis.differential_plots import (
    plot_effect_size_distribution,
    plot_effect_size_vs_significance
)

# Effect size distribution
plot_effect_size_distribution(
    effect_sizes=t_test_results['effect_size'],
    effect_size_type="cohens_d",
    output_path="effect_size_distribution.png"
)

# Effect size vs significance
plot_effect_size_vs_significance(
    statistical_results=t_test_results,
    effect_size_col="effect_size",
    p_value_col="p_value_adjusted",
    output_path="effect_size_vs_significance.png"
)
```

## Method Comparison Plots

### Method Performance Comparison

```python
from isospec_data_tools.visualization.analysis import plot_method_comparison

# Compare different analysis methods
plot_method_comparison(
    comparison_results=method_comparison_results,
    methods=["normalization", "imputation", "statistical_test"],
    output_dir="method_comparison_plots"
)
```

### Normalization Method Comparison

```python
from isospec_data_tools.visualization.analysis.method_plot import plot_normalization_comparison

# Compare normalization methods
plot_normalization_comparison(
    data=raw_data,
    normalized_data_dict={
        "total_abundance": ta_normalized,
        "median_quotient": mq_normalized,
        "quantile": q_normalized
    },
    feature_cols=metabolite_columns,
    output_path="normalization_comparison.png"
)
```

### Imputation Method Comparison

```python
from isospec_data_tools.visualization.analysis.method_plot import plot_imputation_comparison

# Compare imputation methods
plot_imputation_comparison(
    original_data=data_with_missing,
    imputed_data_dict={
        "qc_min": qc_min_imputed,
        "median": median_imputed,
        "mean": mean_imputed
    },
    feature_cols=metabolite_columns,
    output_path="imputation_comparison.png"
)
```

### Statistical Test Comparison

```python
from isospec_data_tools.visualization.analysis.method_plot import plot_statistical_test_comparison

# Compare statistical tests
plot_statistical_test_comparison(
    test_results_dict={
        "student_t": student_results,
        "welch_t": welch_results,
        "mann_whitney": mann_whitney_results
    },
    comparison_metric="p_value",
    output_path="statistical_test_comparison.png"
)
```

## Model Performance Visualization

### Classification Performance Plots

```python
from isospec_data_tools.visualization.analysis import plot_model_performance

# Generate model performance plots
plot_model_performance(
    performance_results=model_performance_results,
    models=trained_models,
    output_dir="model_performance_plots"
)
```

### ROC Curves

```python
from isospec_data_tools.visualization.analysis.model_plots import plot_roc_curves

# ROC curves for multiple models
plot_roc_curves(
    models=trained_models,
    X_test=test_features,
    y_test=test_labels,
    output_path="roc_curves.png"
)
```

### Precision-Recall Curves

```python
from isospec_data_tools.visualization.analysis.model_plots import plot_precision_recall_curves

# Precision-recall curves
plot_precision_recall_curves(
    models=trained_models,
    X_test=test_features,
    y_test=test_labels,
    output_path="precision_recall_curves.png"
)
```

### Feature Importance Plots

```python
from isospec_data_tools.visualization.analysis.model_plots import plot_feature_importance

# Feature importance visualization
plot_feature_importance(
    feature_importance_results=feature_importance_results,
    top_n=20,
    output_path="feature_importance.png"
)
```

## Advanced Visualization Features

### Interactive Plots

```python
from isospec_data_tools.visualization.analysis.interactive_plots import (
    create_interactive_cluster_plot,
    create_interactive_volcano_plot
)

# Interactive cluster plot
interactive_cluster_plot = create_interactive_cluster_plot(
    data=metabolomics_data,
    cluster_labels=cluster_labels,
    feature_cols=metabolite_columns[:2],
    output_path="interactive_cluster_plot.html"
)

# Interactive volcano plot
interactive_volcano_plot = create_interactive_volcano_plot(
    statistical_results=t_test_results,
    log_fold_change_col="log_fold_change",
    p_value_col="p_value_adjusted",
    output_path="interactive_volcano_plot.html"
)
```

### Multi-panel Plots

```python
from isospec_data_tools.visualization.analysis.multi_panel_plots import create_analysis_summary_plot

# Create multi-panel summary plot
summary_plot = create_analysis_summary_plot(
    data=metabolomics_data,
    statistical_results=t_test_results,
    cluster_results=cluster_results,
    confounder_results=confounder_results,
    output_path="analysis_summary.png"
)
```

### Publication-Ready Plots

```python
from isospec_data_tools.visualization.analysis.publication_plots import (
    create_publication_volcano_plot,
    create_publication_cluster_plot
)

# Publication-ready volcano plot
pub_volcano_plot = create_publication_volcano_plot(
    statistical_results=t_test_results,
    log_fold_change_col="log_fold_change",
    p_value_col="p_value_adjusted",
    style="nature",  # Options: "nature", "science", "cell"
    output_path="publication_volcano.png"
)

# Publication-ready cluster plot
pub_cluster_plot = create_publication_cluster_plot(
    data=metabolomics_data,
    cluster_labels=cluster_labels,
    feature_cols=metabolite_columns[:2],
    style="nature",
    output_path="publication_cluster.png"
)
```

## Customization Options

### Color Schemes

```python
# Custom color schemes
custom_colors = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "background": "#F5F5F5"
}

# Apply custom colors
plot_cluster_analysis(
    cluster_results=cluster_results,
    data=metabolomics_data,
    feature_cols=metabolite_columns[:2],
    color_scheme=custom_colors,
    output_dir="custom_cluster_plots"
)
```

### Plot Styles

```python
# Different plot styles
plot_differential_analysis(
    statistical_results=t_test_results,
    data=metabolomics_data,
    plot_style="seaborn",  # Options: "seaborn", "ggplot", "classic"
    figure_size=(10, 8),
    dpi=300,
    output_dir="styled_differential_plots"
)
```

### Layout Options

```python
# Custom layout options
layout_options = {
    "figure_size": (12, 10),
    "subplot_spacing": 0.3,
    "title_fontsize": 14,
    "axis_labelsize": 12,
    "tick_labelsize": 10
}

plot_method_comparison(
    comparison_results=method_comparison_results,
    methods=["normalization", "imputation"],
    layout_options=layout_options,
    output_dir="custom_layout_plots"
)
```

## Integration with Analysis Workflow

### Automated Visualization Pipeline

```python
from isospec_data_tools.analysis import AnalysisPipeline
from isospec_data_tools.visualization.analysis import VisualizationPipeline

# Create analysis pipeline
analysis_pipeline = AnalysisPipeline(config=analysis_config)
analysis_results = analysis_pipeline.run_full_analysis(
    data=metabolomics_data,
    feature_cols=metabolite_columns,
    target_col="disease_status"
)

# Create visualization pipeline
viz_pipeline = VisualizationPipeline(config=visualization_config)
viz_results = viz_pipeline.generate_all_plots(
    analysis_results=analysis_results,
    output_dir="automated_plots"
)
```

### Conditional Visualization

```python
# Generate plots based on analysis results
if analysis_results['clustering']['performed']:
    plot_cluster_analysis(
        cluster_results=analysis_results['clustering']['results'],
        data=metabolomics_data,
        feature_cols=metabolite_columns[:2],
        output_dir="cluster_plots"
    )

if analysis_results['differential']['significant_features'] > 0:
    plot_differential_analysis(
        statistical_results=analysis_results['differential']['results'],
        data=metabolomics_data,
        output_dir="differential_plots"
    )
```

## Performance and Optimization

### Large Dataset Visualization

```python
# Optimize for large datasets
plot_cluster_analysis(
    cluster_results=cluster_results,
    data=large_dataset,
    feature_cols=metabolite_columns[:2],
    sample_size=1000,  # Subsample for visualization
    alpha=0.6,  # Use transparency
    output_dir="large_dataset_plots"
)
```

### Memory-Efficient Plotting

```python
# Memory-efficient plotting
from isospec_data_tools.visualization.analysis.memory_efficient import plot_large_heatmap

# Plot large heatmap efficiently
plot_large_heatmap(
    data=large_metabolomics_data,
    feature_cols=metabolite_columns,
    chunk_size=1000,
    output_path="large_heatmap.png"
)
```

### Batch Plot Generation

```python
# Generate multiple plots in batch
plot_configs = [
    {"type": "cluster", "method": "kmeans"},
    {"type": "cluster", "method": "hierarchical"},
    {"type": "differential", "test": "welch"},
    {"type": "confounder", "confounders": ["age", "sex"]}
]

for config in plot_configs:
    generate_plot_from_config(
        config=config,
        data=metabolomics_data,
        analysis_results=analysis_results,
        output_dir="batch_plots"
    )
```

## Best Practices

### Plot Quality Guidelines

1. **Resolution**: Use high DPI (300+) for publication plots
2. **Color schemes**: Use colorblind-friendly palettes
3. **Font sizes**: Ensure readability at intended size
4. **Legends**: Include clear, informative legends
5. **Axis labels**: Use descriptive axis labels with units

### Visualization Strategy

1. **Exploratory plots**: Start with basic exploratory visualizations
2. **Diagnostic plots**: Include diagnostic plots for assumption checking
3. **Result visualization**: Create clear visualizations of main results
4. **Comparison plots**: Show method comparisons when relevant

### File Organization

```python
# Organize plots by analysis type
plot_organization = {
    "exploratory": ["pca_plot.png", "data_distribution.png"],
    "clustering": ["cluster_analysis.png", "silhouette_plot.png"],
    "differential": ["volcano_plot.png", "ma_plot.png"],
    "model_performance": ["roc_curves.png", "feature_importance.png"]
}
```

## Troubleshooting

### Common Issues

1. **Memory errors**: Use subsampling for large datasets
2. **Slow rendering**: Optimize plot complexity
3. **Overlapping labels**: Adjust label positioning
4. **Color issues**: Use appropriate color schemes

### Performance Tips

1. **Vectorized operations**: Use efficient plotting libraries
2. **Caching**: Cache expensive plot computations
3. **Parallel processing**: Generate multiple plots in parallel
4. **Format optimization**: Choose appropriate file formats

For more detailed examples and API documentation, see the individual visualization module documentation.
