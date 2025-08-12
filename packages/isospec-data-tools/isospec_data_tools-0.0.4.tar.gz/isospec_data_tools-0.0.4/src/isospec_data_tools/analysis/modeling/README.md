# Machine Learning Utilities

The modeling module provides comprehensive machine learning capabilities for omics data analysis, including clustering algorithms, classification models, and evaluation metrics.

## Components

### Clustering Analysis (`clustering.py`)

Comprehensive clustering algorithms with evaluation metrics and visualization support.

#### ClusterAnalyzer Class

```python
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer

# Initialize cluster analyzer
cluster = ClusterAnalyzer(
    data=metabolomics_data,
    feature_cols=metabolite_columns
)
```

#### Multiple Clustering Methods

```python
# Perform multiple clustering methods
cluster_results = cluster.perform_clustering(
    methods=["kmeans", "hierarchical", "dbscan", "gaussian_mixture"],
    n_clusters_range=(2, 10),
    scaling_method="standard"
)

# Access individual clustering results
kmeans_results = cluster_results['kmeans']
hierarchical_results = cluster_results['hierarchical']
dbscan_results = cluster_results['dbscan']
```

#### K-means Clustering

```python
# K-means clustering with parameter optimization
kmeans_results = cluster.perform_kmeans_clustering(
    n_clusters_range=(2, 10),
    init_method="k-means++",
    max_iter=300,
    n_init=10,
    random_state=42
)

# Optimal number of clusters
optimal_k = cluster.determine_optimal_clusters(
    kmeans_results,
    method="elbow"  # Options: "elbow", "silhouette", "gap_statistic"
)
```

#### Hierarchical Clustering

```python
# Hierarchical clustering
hierarchical_results = cluster.perform_hierarchical_clustering(
    linkage_method="ward",  # Options: "ward", "complete", "average", "single"
    distance_metric="euclidean",
    n_clusters_range=(2, 10)
)

# Generate dendrogram
dendrogram_plot = cluster.plot_dendrogram(
    hierarchical_results,
    output_path="dendrogram.png"
)
```

#### DBSCAN Clustering

```python
# DBSCAN clustering
dbscan_results = cluster.perform_dbscan_clustering(
    eps_range=(0.1, 2.0),
    min_samples_range=(2, 10),
    metric="euclidean",
    algorithm="auto"
)

# Optimal DBSCAN parameters
optimal_params = cluster.optimize_dbscan_parameters(
    dbscan_results,
    optimization_metric="silhouette"
)
```

#### Gaussian Mixture Models

```python
# Gaussian Mixture Models
gmm_results = cluster.perform_gmm_clustering(
    n_components_range=(2, 10),
    covariance_type="full",  # Options: "full", "tied", "diag", "spherical"
    init_params="kmeans",
    max_iter=100
)

# Model selection using information criteria
best_gmm = cluster.select_best_gmm(
    gmm_results,
    criterion="bic"  # Options: "bic", "aic"
)
```

### Cluster Evaluation

```python
# Evaluate clustering quality
evaluation_results = cluster.evaluate_clustering_quality(
    cluster_results=cluster_results,
    metrics=["silhouette", "calinski_harabasz", "davies_bouldin", "adjusted_rand_index"]
)

# Detailed evaluation report
evaluation_report = cluster.generate_evaluation_report(
    evaluation_results=evaluation_results,
    output_dir="cluster_evaluation"
)
```

### Classification and Model Training (`model_evaluation.py`)

Comprehensive model training and evaluation capabilities.

#### ModelTrainer Class

```python
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer

# Initialize model trainer
trainer = ModelTrainer(
    data=metabolomics_data,
    target_col="disease_status",
    feature_cols=metabolite_columns
)
```

#### Feature Selection

```python
# Feature selection methods
selected_features = trainer.select_features(
    method="univariate",  # Options: "univariate", "recursive", "lasso", "mutual_info"
    k_features=100,
    scoring="f_classif"
)

# Recursive feature elimination
rfe_features = trainer.recursive_feature_elimination(
    estimator_name="random_forest",
    n_features_to_select=50,
    cv_folds=5
)

# LASSO feature selection
lasso_features = trainer.lasso_feature_selection(
    alpha_range=(0.001, 1.0),
    cv_folds=5
)
```

#### Model Training

```python
# Train multiple classification models
models = trainer.train_classification_models(
    feature_cols=selected_features,
    algorithms=["random_forest", "svm", "logistic_regression", "xgboost"],
    cv_folds=5,
    hyperparameter_tuning=True,
    random_state=42
)

# Individual model training
rf_model = trainer.train_random_forest(
    n_estimators_range=(50, 200),
    max_depth_range=(3, 15),
    min_samples_split_range=(2, 10),
    cv_folds=5
)
```

#### Hyperparameter Tuning

```python
# Grid search hyperparameter tuning
grid_search_results = trainer.grid_search_hyperparameters(
    algorithm="random_forest",
    param_grid={
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 10],
        'min_samples_split': [2, 5, 10]
    },
    cv_folds=5,
    scoring="f1_weighted"
)

# Random search hyperparameter tuning
random_search_results = trainer.random_search_hyperparameters(
    algorithm="svm",
    param_distributions={
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
        'kernel': ['rbf', 'linear', 'poly']
    },
    n_iter=100,
    cv_folds=5
)
```

#### Model Evaluation

```python
# Comprehensive model evaluation
performance_results = trainer.evaluate_model_performance(
    models=models,
    metrics=["accuracy", "precision", "recall", "f1", "roc_auc"],
    cv_folds=5,
    stratified=True
)

# Detailed performance analysis
performance_analysis = trainer.analyze_model_performance(
    performance_results=performance_results,
    include_confidence_intervals=True,
    alpha=0.05
)
```

#### Feature Importance Analysis

```python
# Feature importance analysis
feature_importance = trainer.analyze_feature_importance(
    models=models,
    feature_names=selected_features,
    importance_methods=["permutation", "shap", "native"],
    top_n=20
)

# SHAP analysis
shap_analysis = trainer.perform_shap_analysis(
    model=models['random_forest'],
    feature_data=metabolomics_data[selected_features],
    sample_size=100
)
```

### Advanced Machine Learning Techniques

#### Ensemble Methods

```python
# Ensemble model creation
ensemble_model = trainer.create_ensemble_model(
    base_models=models,
    ensemble_method="voting",  # Options: "voting", "stacking", "bagging"
    voting_type="soft"
)

# Stacking ensemble
stacking_model = trainer.create_stacking_ensemble(
    base_models=models,
    meta_learner="logistic_regression",
    cv_folds=5
)
```

#### Cross-Validation Strategies

```python
# Stratified cross-validation
cv_results = trainer.stratified_cross_validation(
    model=models['random_forest'],
    cv_folds=10,
    stratify_col="disease_status"
)

# Time series cross-validation
ts_cv_results = trainer.time_series_cross_validation(
    model=models['random_forest'],
    time_col="sample_date",
    n_splits=5
)

# Group cross-validation
group_cv_results = trainer.group_cross_validation(
    model=models['random_forest'],
    group_col="subject_id",
    cv_folds=5
)
```

#### Model Interpretation

```python
# LIME interpretation
lime_explanation = trainer.explain_predictions_lime(
    model=models['random_forest'],
    sample_data=test_samples,
    feature_names=selected_features,
    n_features=10
)

# Partial dependence plots
pdp_analysis = trainer.generate_partial_dependence_plots(
    model=models['random_forest'],
    feature_names=selected_features[:5],
    output_dir="pdp_plots"
)
```

### Model Validation and Testing

#### Performance Validation

```python
# Cross-validation performance
cv_performance = trainer.cross_validate_performance(
    models=models,
    cv_strategy="stratified",
    cv_folds=10,
    metrics=["accuracy", "precision", "recall", "f1"]
)

# Bootstrap validation
bootstrap_results = trainer.bootstrap_validation(
    models=models,
    n_bootstrap=1000,
    confidence_level=0.95
)
```

#### Model Comparison

```python
# Statistical model comparison
comparison_results = trainer.compare_models_statistically(
    models=models,
    comparison_metric="f1",
    statistical_test="wilcoxon",
    alpha=0.05
)

# Model ranking
model_ranking = trainer.rank_models(
    performance_results=performance_results,
    ranking_metrics=["f1", "roc_auc"],
    weights=[0.6, 0.4]
)
```

#### Overfitting Detection

```python
# Learning curve analysis
learning_curves = trainer.generate_learning_curves(
    models=models,
    train_sizes=[0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
    cv_folds=5
)

# Validation curve analysis
validation_curves = trainer.generate_validation_curves(
    algorithm="random_forest",
    param_name="n_estimators",
    param_range=[10, 50, 100, 200, 500],
    cv_folds=5
)
```

## Integration Examples

### Combined Clustering and Classification

```python
# Use clustering results for semi-supervised learning
cluster_labels = cluster_results['kmeans']['labels']

# Add cluster labels as features
enhanced_data = metabolomics_data.copy()
enhanced_data['cluster_label'] = cluster_labels

# Train models with cluster information
enhanced_trainer = ModelTrainer(
    data=enhanced_data,
    target_col="disease_status",
    feature_cols=metabolite_columns + ['cluster_label']
)

enhanced_models = enhanced_trainer.train_classification_models(
    algorithms=["random_forest", "svm"],
    cv_folds=5
)
```

### Clustering-Based Feature Selection

```python
# Use clustering for feature selection
cluster_features = cluster.select_representative_features(
    cluster_results=cluster_results['hierarchical'],
    feature_cols=metabolite_columns,
    n_features_per_cluster=5
)

# Train models with cluster-selected features
cluster_based_models = trainer.train_classification_models(
    feature_cols=cluster_features,
    algorithms=["random_forest", "svm"],
    cv_folds=5
)
```

## Visualization Integration

### Clustering Visualization

```python
from isospec_data_tools.visualization.analysis import plot_cluster_analysis

# Generate cluster plots
plot_cluster_analysis(
    cluster_results=cluster_results,
    data=metabolomics_data,
    feature_cols=metabolite_columns[:2],  # First 2 features for 2D plot
    output_dir="cluster_plots"
)
```

### Model Performance Visualization

```python
from isospec_data_tools.visualization.analysis import plot_model_performance

# Generate model performance plots
plot_model_performance(
    performance_results=performance_results,
    models=models,
    output_dir="model_performance_plots"
)
```

### Feature Importance Visualization

```python
# Plot feature importance
trainer.plot_feature_importance(
    feature_importance=feature_importance,
    top_n=20,
    output_dir="feature_importance_plots"
)
```

## Performance Optimization

### Parallel Processing

```python
# Parallel model training
parallel_models = trainer.train_models_parallel(
    algorithms=["random_forest", "svm", "logistic_regression"],
    n_jobs=4,
    cv_folds=5
)

# Parallel hyperparameter tuning
parallel_tuning = trainer.parallel_hyperparameter_tuning(
    algorithms=["random_forest", "svm"],
    n_jobs=4,
    cv_folds=5
)
```

### Memory-Efficient Processing

```python
# Memory-efficient feature selection
memory_efficient_features = trainer.memory_efficient_feature_selection(
    method="univariate",
    chunk_size=1000,
    k_features=100
)

# Batch processing for large datasets
batch_results = trainer.batch_process_large_dataset(
    data_path="large_dataset.csv",
    batch_size=10000,
    model_config=model_config
)
```

## Best Practices

### Clustering Best Practices

1. **Data preprocessing**: Scale features before clustering
2. **Method selection**: Try multiple clustering methods
3. **Cluster validation**: Use multiple evaluation metrics
4. **Optimal clusters**: Use multiple methods to determine optimal number

### Classification Best Practices

1. **Feature selection**: Perform proper feature selection
2. **Cross-validation**: Use appropriate CV strategies
3. **Hyperparameter tuning**: Optimize model parameters
4. **Model evaluation**: Use multiple evaluation metrics
5. **Overfitting prevention**: Monitor learning curves

### Model Validation Best Practices

1. **Train-test split**: Use proper data splitting
2. **Cross-validation**: Use stratified CV for imbalanced data
3. **Performance metrics**: Choose appropriate metrics for problem type
4. **Statistical testing**: Test for significant differences between models

## Quality Control

### Clustering Quality Control

```python
# Clustering stability analysis
stability_results = cluster.assess_clustering_stability(
    cluster_results=cluster_results,
    n_bootstrap=100,
    stability_metric="adjusted_rand_index"
)

# Cluster validation
validation_results = cluster.validate_clustering_results(
    cluster_results=cluster_results,
    validation_metrics=["silhouette", "calinski_harabasz"]
)
```

### Model Quality Control

```python
# Model stability analysis
stability_analysis = trainer.assess_model_stability(
    models=models,
    n_bootstrap=100,
    stability_metrics=["accuracy", "f1"]
)

# Cross-validation consistency
cv_consistency = trainer.check_cv_consistency(
    models=models,
    cv_folds=10,
    consistency_threshold=0.05
)
```

## Troubleshooting

### Common Clustering Issues

1. **Scaling problems**: Ensure features are properly scaled
2. **Curse of dimensionality**: Use dimensionality reduction
3. **Outliers**: Handle outliers before clustering
4. **Cluster validation**: Use multiple evaluation metrics

### Common Classification Issues

1. **Overfitting**: Use cross-validation and regularization
2. **Imbalanced data**: Use appropriate sampling techniques
3. **Feature selection**: Avoid feature leakage
4. **Hyperparameter tuning**: Use proper validation sets

### Performance Issues

1. **Large datasets**: Use batch processing
2. **High dimensionality**: Use feature selection
3. **Computational resources**: Use parallel processing
4. **Memory limitations**: Use memory-efficient algorithms

For more examples and detailed API documentation, see the main analysis module documentation.
