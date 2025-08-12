# Specialized Analyzers

The specialized module provides domain-specific analysis tools for omics data, including ANCOVA analysis, confounder identification, and glycowork integration for glycomics research.

## Components

### ANCOVA Analysis (`ancova_analysis.py`)

Comprehensive Analysis of Covariance (ANCOVA) implementation for controlling continuous covariates while testing categorical factors.

#### Basic ANCOVA

```python
from isospec_data_tools.analysis.specialized.ancova_analysis import ANCOVAAnalyzer

# Initialize ANCOVA analyzer
ancova = ANCOVAAnalyzer(
    data=metabolomics_data,
    dependent_vars=metabolite_columns,
    factor_col="treatment",
    covariate_cols=["age", "bmi"]
)

# Perform ANCOVA analysis
results = ancova.perform_ancova_analysis()
```

#### Advanced ANCOVA with Interactions

```python
# ANCOVA with interaction terms
ancova_results = ancova.perform_ancova_analysis(
    interaction_terms=True,
    interaction_pairs=[("treatment", "age")],
    multiple_testing_correction="bonferroni"
)

# Extract significant results
significant_features = ancova.get_significant_features(
    alpha=0.05,
    effect_type="factor"  # Options: "factor", "covariate", "interaction"
)
```

#### Assumption Checking

```python
# Check ANCOVA assumptions
assumptions = ancova.check_assumptions(
    features=metabolite_columns[:10],  # Check subset for efficiency
    significance_level=0.05
)

# Print assumption results
for feature, checks in assumptions.items():
    print(f"Feature: {feature}")
    print(f"  Normality: {'✓' if checks['normality']['passed'] else '✗'}")
    print(f"  Homoscedasticity: {'✓' if checks['homoscedasticity']['passed'] else '✗'}")
    print(f"  Linearity: {'✓' if checks['linearity']['passed'] else '✗'}")
```

#### Effect Size Analysis

```python
# Calculate effect sizes for ANCOVA
effect_sizes = ancova.calculate_effect_sizes(
    results=ancova_results,
    method="eta_squared"  # Options: "eta_squared", "partial_eta_squared", "omega_squared"
)

# Interpret effect sizes
interpretation = ancova.interpret_effect_sizes(effect_sizes)
```

### Confounder Analysis (`confounder_analysis.py`)

Systematic identification and analysis of potential confounders in omics studies.

#### Confounder Identification

```python
from isospec_data_tools.analysis.specialized.confounder_analysis import ConfounderAnalyzer

# Initialize confounder analyzer
confounder = ConfounderAnalyzer(
    data=study_data,
    target_col="disease_status",
    feature_cols=metabolite_columns
)

# Identify potential confounders
confounders = confounder.identify_confounders(
    potential_confounders=["age", "sex", "bmi", "smoking_status"],
    significance_threshold=0.05,
    effect_size_threshold=0.2
)

print(f"Identified confounders: {confounders}")
```

#### Detailed Confounder Analysis

```python
# Analyze individual confounders
for confounder_var in confounders:
    analysis = confounder.analyze_confounder_effects(
        confounder_var=confounder_var,
        feature_subset=metabolite_columns,
        test_method="spearman"  # Options: "pearson", "spearman", "kendall"
    )

    print(f"\nConfounder: {confounder_var}")
    print(f"  Affected features: {analysis['affected_features']}")
    print(f"  Mean correlation: {analysis['mean_correlation']:.3f}")
    print(f"  Significant associations: {analysis['significant_count']}")
```

#### Confounder Strength Assessment

```python
# Assess confounder strength
strength_assessment = confounder.assess_confounder_strength(
    confounders=confounders,
    strength_metrics=["correlation", "mutual_information", "variance_explained"]
)

# Rank confounders by strength
ranked_confounders = confounder.rank_confounders(
    strength_assessment=strength_assessment,
    ranking_method="composite"
)
```

#### Adjusted Analysis

```python
# Perform analysis adjusted for confounders
adjusted_results = confounder.perform_adjusted_analysis(
    confounders=confounders,
    adjustment_method="linear_regression",
    feature_cols=metabolite_columns
)

# Compare adjusted vs unadjusted results
comparison = confounder.compare_adjusted_unadjusted(
    adjusted_results=adjusted_results,
    unadjusted_results=original_results
)

print(f"Features with changed significance: {comparison['changed_significance']}")
print(f"Mean effect size change: {comparison['mean_effect_change']:.3f}")
```

### Glycowork Integration (`glycowork_integration.py`)

Integration with the glycowork library for specialized glycomics analysis.

#### Glycan Structure Analysis

```python
from isospec_data_tools.analysis.specialized.glycowork_integration import GlycoworkAnalyzer

# Initialize glycowork analyzer
glyco = GlycoworkAnalyzer(
    glycan_data=glycomics_data,
    glycan_columns=glycan_feature_columns
)

# Analyze glycan structures
structure_analysis = glyco.analyze_glycan_structures(
    group_col="treatment",
    analysis_type="linkage_analysis",
    include_motifs=True
)
```

#### Glycan Motif Analysis

```python
# Motif enrichment analysis
motif_analysis = glyco.analyze_glycan_motifs(
    glycan_structures=glycan_structures,
    motif_database="glycowork_default",
    enrichment_method="fisher_exact"
)

# Identify significant motifs
significant_motifs = glyco.get_significant_motifs(
    motif_results=motif_analysis,
    p_value_threshold=0.05,
    fold_change_threshold=1.5
)
```

#### Pathway Analysis

```python
# Glycan pathway analysis
pathway_results = glyco.perform_pathway_analysis(
    significant_glycans=significant_glycans,
    pathway_database="kegg_glycan",
    analysis_method="gsea"
)

# Visualize pathway results
pathway_visualization = glyco.visualize_pathway_results(
    pathway_results=pathway_results,
    top_pathways=10,
    output_dir="glycan_pathways"
)
```

#### Biosynthetic Network Analysis

```python
# Analyze biosynthetic networks
network_analysis = glyco.analyze_biosynthetic_networks(
    glycan_data=glycomics_data,
    network_type="biosynthetic_tree",
    include_enzymes=True
)

# Identify key regulatory points
regulatory_analysis = glyco.identify_regulatory_points(
    network_results=network_analysis,
    expression_data=enzyme_expression_data
)
```

## Integration Examples

### Combined ANCOVA and Confounder Analysis

```python
# Identify confounders first
confounders = confounder.identify_confounders(
    potential_confounders=["age", "sex", "bmi"],
    significance_threshold=0.05
)

# Include confounders in ANCOVA
ancova_with_confounders = ANCOVAAnalyzer(
    data=metabolomics_data,
    dependent_vars=metabolite_columns,
    factor_col="treatment",
    covariate_cols=["age", "bmi"] + confounders
)

# Perform analysis
results = ancova_with_confounders.perform_ancova_analysis()
```

### Glycowork with Statistical Analysis

```python
# Perform glycan structure analysis
structure_results = glyco.analyze_glycan_structures(
    group_col="treatment",
    analysis_type="linkage_analysis"
)

# Extract significant structures
significant_structures = structure_results['significant_structures']

# Perform statistical analysis on significant structures
from isospec_data_tools.analysis.core.statistical_tests import perform_welch_t_test

structure_stats = []
for structure in significant_structures:
    control_data = glycomics_data[glycomics_data['treatment'] == 'control'][structure]
    treatment_data = glycomics_data[glycomics_data['treatment'] == 'treatment'][structure]

    stat_result = perform_welch_t_test(control_data, treatment_data)
    structure_stats.append({
        'structure': structure,
        'p_value': stat_result['p_value'],
        'statistic': stat_result['statistic']
    })
```

## Advanced Features

### Multi-factor ANCOVA

```python
# Multi-factor ANCOVA
multi_ancova = ANCOVAAnalyzer(
    data=metabolomics_data,
    dependent_vars=metabolite_columns,
    factor_cols=["treatment", "timepoint"],  # Multiple factors
    covariate_cols=["age", "bmi"]
)

# Analyze main effects and interactions
multi_results = multi_ancova.perform_multifactor_ancova(
    include_interactions=True,
    max_interaction_order=2
)
```

### Hierarchical Confounder Analysis

```python
# Hierarchical confounder analysis
hierarchical_analysis = confounder.perform_hierarchical_analysis(
    confounders=confounders,
    hierarchy_levels=["demographic", "clinical", "technical"],
    confounder_mapping={
        "demographic": ["age", "sex"],
        "clinical": ["bmi", "medication"],
        "technical": ["batch", "injection_order"]
    }
)
```

### Temporal Confounder Analysis

```python
# Temporal confounder analysis for longitudinal studies
temporal_analysis = confounder.analyze_temporal_confounders(
    data=longitudinal_data,
    time_col="timepoint",
    subject_col="subject_id",
    potential_confounders=["age", "medication_change"]
)
```

## Visualization Integration

### ANCOVA Visualization

```python
from isospec_data_tools.visualization.analysis import plot_ancova_results

# Generate ANCOVA plots
plot_ancova_results(
    ancova_results=ancova_results,
    data=metabolomics_data,
    top_features=20,
    output_dir="ancova_plots"
)
```

### Confounder Visualization

```python
from isospec_data_tools.visualization.analysis import plot_confounder_relationships

# Generate confounder plots
plot_confounder_relationships(
    confounder_results=confounder_results,
    data=study_data,
    confounders=confounders,
    output_dir="confounder_plots"
)
```

### Glycowork Visualization

```python
# Generate glycowork-specific visualizations
glyco.plot_glycan_heatmap(
    glycan_data=glycomics_data,
    group_col="treatment",
    clustering_method="hierarchical",
    output_dir="glycan_plots"
)

glyco.plot_motif_enrichment(
    motif_results=motif_analysis,
    top_motifs=15,
    output_dir="glycan_plots"
)
```

## Quality Control and Validation

### ANCOVA Validation

```python
# Validate ANCOVA results
validation_results = ancova.validate_results(
    results=ancova_results,
    validation_method="cross_validation",
    cv_folds=5
)

# Check model assumptions
assumption_summary = ancova.summarize_assumptions(
    assumption_results=assumptions,
    feature_threshold=0.8  # Require 80% of features to pass
)
```

### Confounder Validation

```python
# Validate confounder identification
validation = confounder.validate_confounder_identification(
    identified_confounders=confounders,
    validation_method="permutation_test",
    n_permutations=1000
)

# Cross-validate adjusted results
cv_results = confounder.cross_validate_adjusted_analysis(
    adjusted_results=adjusted_results,
    cv_folds=10
)
```

### Glycowork Quality Control

```python
# Quality control for glycan analysis
qc_results = glyco.perform_quality_control(
    glycan_data=glycomics_data,
    qc_metrics=["completeness", "consistency", "structure_validity"]
)

# Validate glycan structures
structure_validation = glyco.validate_glycan_structures(
    glycan_structures=identified_structures,
    validation_database="glycowork_reference"
)
```

## Performance Optimization

### Parallel Processing

```python
# Parallel ANCOVA analysis
parallel_results = ancova.perform_parallel_ancova(
    feature_chunks=100,
    n_jobs=4
)

# Parallel confounder analysis
parallel_confounders = confounder.identify_confounders_parallel(
    potential_confounders=potential_confounders,
    n_jobs=4
)
```

### Memory-Efficient Processing

```python
# Memory-efficient ANCOVA for large datasets
memory_efficient_results = ancova.perform_memory_efficient_ancova(
    chunk_size=1000,
    intermediate_storage="disk"
)
```

## Best Practices

### ANCOVA Best Practices

1. **Check assumptions**: Always validate normality, homoscedasticity, and linearity
2. **Covariate selection**: Choose meaningful covariates based on study design
3. **Interaction testing**: Test for interactions between factors and covariates
4. **Effect size reporting**: Report effect sizes alongside p-values

### Confounder Analysis Best Practices

1. **A priori identification**: Identify potential confounders before analysis
2. **Biological relevance**: Consider biological plausibility of confounders
3. **Temporal relationships**: Ensure confounders precede outcomes
4. **Adjustment methods**: Choose appropriate adjustment methods

### Glycowork Integration Best Practices

1. **Structure validation**: Validate glycan structures before analysis
2. **Database consistency**: Use consistent glycan databases
3. **Motif significance**: Apply appropriate multiple testing corrections
4. **Pathway interpretation**: Consider biological context in pathway analysis

## Troubleshooting

### Common ANCOVA Issues

1. **Assumption violations**: Use robust methods or transformations
2. **Multicollinearity**: Check correlation between covariates
3. **Insufficient power**: Ensure adequate sample size
4. **Missing data**: Handle missing values appropriately

### Common Confounder Issues

1. **Over-adjustment**: Avoid adjusting for intermediate variables
2. **Residual confounding**: Consider unmeasured confounders
3. **Collider bias**: Avoid adjusting for colliders
4. **Selection bias**: Consider selection mechanisms

### Common Glycowork Issues

1. **Structure parsing**: Ensure correct glycan structure format
2. **Database compatibility**: Check database version compatibility
3. **Memory limitations**: Use chunked processing for large datasets
4. **Network analysis**: Validate network topology

For more examples and detailed API documentation, see the main analysis module documentation.
