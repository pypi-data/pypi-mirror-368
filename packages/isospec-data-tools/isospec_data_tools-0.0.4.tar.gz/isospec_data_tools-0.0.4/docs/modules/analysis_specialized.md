# Analysis Specialized Module

The specialized analysis module provides domain-specific analysis tools for advanced statistical methods, confounder analysis, and glycowork integration, designed for complex omics research workflows.

## Overview

The specialized module consists of three main analyzers:

1. **ANCOVAAnalyzer**: Analysis of Covariance for controlling covariates in group comparisons
2. **ConfounderAnalyzer**: Systematic identification and analysis of confounding variables
3. **GlycoworkAnalyzer**: Integration with the glycowork library for glycan structural analysis

## Quick Start

### ANCOVA Analysis

```python
from isospec_data_tools.analysis import ANCOVAAnalyzer

# Basic ANCOVA analysis
significant_results, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
    data=glycomics_data,
    feature_prefix="G",  # Glycan feature prefix
    class_column="disease_status",
    covar_columns=["age", "sex", "bmi"],
    alpha=0.05
)

print(f"Found {len(significant_glycans)} significant glycans after controlling for covariates")
```

### Confounder Analysis

```python
from isospec_data_tools.analysis import ConfounderAnalyzer

# Identify confounders
confounders, significant_glycans = ConfounderAnalyzer.analyze_confounders(
    data=metabolomics_data,
    glycan_list=None,  # Use all features
    glycan_prefix="FT-",
    confounders=["age", "sex", "bmi", "medication"],
    alpha=0.05,
    correction_method="fdr_bh"
)

print(f"Identified confounders affecting {len(significant_glycans)} features")
```

### Glycowork Integration

```python
from isospec_data_tools.analysis import GlycoworkAnalyzer

# Initialize glycowork analyzer
glyco_analyzer = GlycoworkAnalyzer(
    glycan_data=glycomics_data,
    glycan_columns=[col for col in glycomics_data.columns if col.startswith("G")]
)

# Perform structural analysis
structural_results = glyco_analyzer.analyze_glycan_structures(
    group_col="treatment",
    analysis_type="linkage_analysis"
)
```

## ANCOVA Analysis

### Basic ANCOVA Workflow

ANCOVA (Analysis of Covariance) allows testing for group differences while controlling for continuous covariates:

```python
import pandas as pd
from isospec_data_tools.analysis import ANCOVAAnalyzer

# Load glycomics data with covariates
data = pd.read_csv("glycomics_with_covariates.csv")

# Perform ANCOVA analysis
significant_results, all_results, significant_features = ANCOVAAnalyzer.analyze_glycans_ancova(
    data=data,
    feature_prefix="G",
    class_column="treatment_group",
    covar_columns=["age", "baseline_glucose", "bmi"],
    alpha=0.05,
    glycan_composition_map=None  # Optional: map feature IDs to compositions
)

# Examine results
print(f"Analyzed {len(all_results)} glycan features")
print(f"Found {len(significant_results)} significant results")
print(f"Significant features: {list(significant_features)}")

# View detailed results
print("Top 5 most significant results:")
top_results = significant_results.nsmallest(5, 'p_adjusted')
for _, row in top_results.iterrows():
    print(f"  {row['feature']}: p={row['p_value']:.2e}, adj_p={row['p_adjusted']:.2e}")
```

### Advanced ANCOVA Configuration

```python
# Custom glycan composition mapping
glycan_map = {
    "G1": "H5N4F1",
    "G2": "H6N5F1",
    "G3": "H7N6F2"
    # ... more mappings
}

# ANCOVA with composition mapping
results = ANCOVAAnalyzer.analyze_glycans_ancova(
    data=glycomics_data,
    feature_prefix="G",
    class_column="disease_status",
    covar_columns=["age", "sex"],
    alpha=0.01,  # More stringent significance
    glycan_composition_map=glycan_map
)

# Filter results by effect size
significant_results, all_results, _ = results
large_effect_results = significant_results[
    significant_results['effect_size'] > 0.5  # Medium to large effect
]

print(f"Found {len(large_effect_results)} features with significant and meaningful effects")
```

### ANCOVA with Multiple Comparisons

```python
# Perform ANCOVA across multiple treatment groups
multi_group_data = pd.read_csv("multi_treatment_glycomics.csv")

# ANCOVA handles multiple groups automatically
results = ANCOVAAnalyzer.analyze_glycans_ancova(
    data=multi_group_data,
    feature_prefix="FT-",
    class_column="treatment_arm",  # Multiple treatment arms
    covar_columns=["baseline_age", "baseline_severity"],
    alpha=0.05
)

significant_results, all_results, significant_features = results

# Post-hoc analysis for significant features
from isospec_data_tools.analysis import perform_tukey_hsd_test

post_hoc_results = {}
for feature in significant_features:
    tukey_result = perform_tukey_hsd_test(
        data=multi_group_data,
        group_col="treatment_arm",
        feature_cols=[feature]
    )
    post_hoc_results[feature] = tukey_result

print(f"Completed post-hoc analysis for {len(post_hoc_results)} significant features")
```

## Confounder Analysis

### Systematic Confounder Identification

```python
# Comprehensive confounder analysis
confounders, affected_features = ConfounderAnalyzer.analyze_confounders(
    data=metabolomics_data,
    glycan_list=None,  # Analyze all features
    glycan_prefix="METABOLITE_",
    confounders=["age", "sex", "bmi", "smoking_status", "medication_use"],
    alpha=0.05,
    correction_method="fdr_bh",
    min_glycans=10  # Minimum features affected to consider significant
)

# Examine confounder effects
print("Confounder Analysis Results:")
for confounder, effects in confounders.items():
    print(f"\n{confounder.upper()}:")
    for effect_type, features in effects.items():
        print(f"  {effect_type}: {len(features)} features affected")
        if len(features) <= 5:  # Show feature names if few
            print(f"    Features: {features}")

print(f"\nTotal features affected by confounders: {len(affected_features)}")
```

### Statistical Testing for Confounders

```python
# Detailed statistical testing
statistical_results = ConfounderAnalyzer.perform_statistical_tests(
    data=study_data,
    target_column="disease_status",
    value_column="age",
    binary_split_column="sex"
)

# Analyze within-group and between-group effects
print("Within-group tests (e.g., age differences within disease groups by sex):")
for result in statistical_results["within_group"]:
    print(f"  Group {result['group']}, Sex {result['binary_group']}: p={result['p_value']:.3f}")

print("\nBetween-group tests (e.g., age differences between disease groups):")
for result in statistical_results["between_group"]:
    print(f"  {result['comparison']}: p={result['p_value']:.3f}, effect_size={result.get('effect_size', 'N/A')}")
```

### Confounder Visualization Integration

```python
from isospec_data_tools.visualization.analysis import plot_confounder_relationships

# Generate confounder plots
plot_confounder_relationships(
    confounder_results=confounders,
    data=metabolomics_data,
    output_dir="confounder_analysis_plots",
    save_plots=True
)

# Custom confounder analysis plot
import matplotlib.pyplot as plt
import seaborn as sns

def plot_confounder_heatmap(confounders, affected_features):
    """Create heatmap showing confounder effects across features."""

    # Create matrix of confounder effects
    confounder_matrix = pd.DataFrame(index=affected_features)

    for confounder, effects in confounders.items():
        # Mark features affected by each confounder
        confounder_matrix[confounder] = 0
        for effect_type, features in effects.items():
            for feature in features:
                if feature in confounder_matrix.index:
                    confounder_matrix.loc[feature, confounder] = 1

    # Plot heatmap
    plt.figure(figsize=(10, max(8, len(affected_features) * 0.3)))
    sns.heatmap(
        confounder_matrix,
        cmap="RdYlBu_r",
        cbar_kws={"label": "Confounder Effect"},
        fmt="d"
    )
    plt.title("Confounder Effects Across Features")
    plt.xlabel("Potential Confounders")
    plt.ylabel("Metabolic Features")
    plt.tight_layout()
    plt.savefig("confounder_heatmap.png", dpi=300, bbox_inches="tight")
    plt.show()

# Generate custom plot
plot_confounder_heatmap(confounders, affected_features)
```

### Advanced Confounder Analysis

```python
def comprehensive_confounder_pipeline(
    data,
    target_col,
    feature_prefix,
    potential_confounders,
    alpha=0.05
):
    """Complete confounder analysis pipeline with reporting."""

    results = {
        "summary": {},
        "detailed_results": {},
        "recommendations": []
    }

    # Step 1: Basic confounder identification
    confounders, affected_features = ConfounderAnalyzer.analyze_confounders(
        data=data,
        glycan_prefix=feature_prefix,
        confounders=potential_confounders,
        alpha=alpha
    )

    results["detailed_results"]["confounders"] = confounders
    results["detailed_results"]["affected_features"] = affected_features

    # Step 2: Quantify confounder strength
    confounder_strength = {}
    for confounder, effects in confounders.items():
        total_affected = sum(len(features) for features in effects.values())
        confounder_strength[confounder] = total_affected

    results["summary"]["confounder_strength"] = confounder_strength

    # Step 3: Generate recommendations
    if not confounders:
        results["recommendations"].append("No significant confounders detected.")
    else:
        # Rank confounders by impact
        ranked_confounders = sorted(
            confounder_strength.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results["recommendations"].append("Priority confounders to control for:")
        for confounder, count in ranked_confounders[:3]:  # Top 3
            results["recommendations"].append(f"  - {confounder}: affects {count} features")

        # Suggest analysis approach
        if len(affected_features) > len(data.columns) * 0.1:  # >10% of features affected
            results["recommendations"].append(
                "Consider ANCOVA or linear mixed models to control for confounders"
            )
        else:
            results["recommendations"].append(
                "Consider excluding affected features or stratified analysis"
            )

    return results

# Run comprehensive analysis
confounder_results = comprehensive_confounder_pipeline(
    data=metabolomics_data,
    target_col="treatment_response",
    feature_prefix="FT-",
    potential_confounders=["age", "sex", "bmi", "baseline_severity"]
)

# Print recommendations
print("Confounder Analysis Recommendations:")
for rec in confounder_results["recommendations"]:
    print(rec)
```

## Glycowork Integration

### Basic Glycowork Analysis

```python
from isospec_data_tools.analysis import GlycoworkAnalyzer

# Initialize with glycan data
glyco_analyzer = GlycoworkAnalyzer(
    glycan_data=glycomics_data,
    glycan_columns=[col for col in glycomics_data.columns if col.startswith("G")]
)

# Structural analysis
structural_results = glyco_analyzer.analyze_glycan_structures(
    group_col="disease_status",
    analysis_type="linkage_analysis"
)

print("Glycowork structural analysis completed")
print(f"Analysis type: {structural_results.get('analysis_type', 'Unknown')}")
```

### Advanced Glycowork Workflows

```python
# Multiple analysis types
analysis_types = ["linkage_analysis", "motif_analysis", "pathway_analysis"]

glycowork_results = {}
for analysis_type in analysis_types:
    try:
        result = glyco_analyzer.analyze_glycan_structures(
            group_col="treatment_group",
            analysis_type=analysis_type
        )
        glycowork_results[analysis_type] = result
        print(f"Completed {analysis_type}")
    except Exception as e:
        print(f"Failed {analysis_type}: {e}")

# Combine results for comprehensive glycan characterization
combined_results = {
    "structural_patterns": glycowork_results.get("linkage_analysis", {}),
    "functional_motifs": glycowork_results.get("motif_analysis", {}),
    "pathway_associations": glycowork_results.get("pathway_analysis", {})
}
```

### Integrating Glycowork with Statistical Analysis

```python
# Combine glycowork structural analysis with differential analysis
def integrated_glycan_analysis(
    glycan_data,
    group_col,
    glycan_columns,
    covariates=None
):
    """Integrated analysis combining structural and statistical approaches."""

    results = {"structural": {}, "statistical": {}, "integrated": {}}

    # Step 1: Structural analysis with glycowork
    print("Performing glycowork structural analysis...")
    glyco_analyzer = GlycoworkAnalyzer(
        glycan_data=glycan_data,
        glycan_columns=glycan_columns
    )

    structural_results = glyco_analyzer.analyze_glycan_structures(
        group_col=group_col,
        analysis_type="linkage_analysis"
    )
    results["structural"] = structural_results

    # Step 2: Statistical analysis
    print("Performing statistical analysis...")
    if covariates:
        # Use ANCOVA if covariates present
        stat_results = ANCOVAAnalyzer.analyze_glycans_ancova(
            data=glycan_data,
            feature_prefix="G",
            class_column=group_col,
            covar_columns=covariates,
            alpha=0.05
        )
        results["statistical"]["method"] = "ANCOVA"
    else:
        # Use t-tests for simple group comparison
        from isospec_data_tools.analysis import perform_welch_t_test

        groups = glycan_data[group_col].unique()
        if len(groups) == 2:
            group1_data = glycan_data[glycan_data[group_col] == groups[0]]
            group2_data = glycan_data[glycan_data[group_col] == groups[1]]

            t_test_results = []
            for glycan in glycan_columns:
                try:
                    result = perform_welch_t_test(
                        group1_data=group1_data[glycan].dropna(),
                        group2_data=group2_data[glycan].dropna()
                    )
                    result["feature"] = glycan
                    t_test_results.append(result)
                except:
                    continue

            stat_results = (pd.DataFrame(t_test_results), None, None)
            results["statistical"]["method"] = "t-test"

    results["statistical"]["results"] = stat_results

    # Step 3: Integration
    print("Integrating structural and statistical results...")
    significant_features = []
    if covariates:
        significant_features = stat_results[2]  # significant_glycans from ANCOVA
    else:
        stat_df = stat_results[0]
        significant_features = stat_df[stat_df["p_value"] < 0.05]["feature"].tolist()

    results["integrated"]["significant_features"] = significant_features
    results["integrated"]["structural_patterns_in_significant"] = []

    # Analyze structural patterns in significant glycans
    for feature in significant_features:
        if feature in structural_results:
            results["integrated"]["structural_patterns_in_significant"].append({
                "feature": feature,
                "structural_info": structural_results[feature]
            })

    return results

# Run integrated analysis
integrated_results = integrated_glycan_analysis(
    glycan_data=glycomics_data,
    group_col="disease_status",
    glycan_columns=[col for col in glycomics_data.columns if col.startswith("G")],
    covariates=["age", "sex"]
)

print("Integrated Glycan Analysis Complete:")
print(f"  Significant features: {len(integrated_results['integrated']['significant_features'])}")
print(f"  Features with structural patterns: {len(integrated_results['integrated']['structural_patterns_in_significant'])}")
```

## Complete Specialized Analysis Workflows

### Multi-Modal Analysis Pipeline

```python
def complete_specialized_analysis_pipeline(
    data,
    feature_prefix="FT-",
    target_col="treatment",
    potential_confounders=None,
    covariates=None,
    use_glycowork=False
):
    """Complete pipeline integrating all specialized analysis tools."""

    pipeline_results = {
        "confounder_analysis": {},
        "statistical_analysis": {},
        "glycowork_analysis": {},
        "summary": {}
    }

    print("Starting complete specialized analysis pipeline...")

    # Step 1: Confounder Analysis
    if potential_confounders:
        print("1. Analyzing confounders...")
        confounders, affected_features = ConfounderAnalyzer.analyze_confounders(
            data=data,
            glycan_prefix=feature_prefix,
            confounders=potential_confounders,
            alpha=0.05
        )

        pipeline_results["confounder_analysis"] = {
            "confounders": confounders,
            "affected_features": affected_features,
            "summary": f"Found {len(affected_features)} features affected by confounders"
        }

        # Update covariates based on confounder analysis
        if not covariates:
            # Use confounders with strongest effects as covariates
            confounder_strength = {
                conf: sum(len(effects[effect_type]) for effect_type in effects)
                for conf, effects in confounders.items()
            }
            top_confounders = sorted(confounder_strength.items(),
                                   key=lambda x: x[1], reverse=True)[:3]
            covariates = [conf for conf, _ in top_confounders]
            print(f"   Using top confounders as covariates: {covariates}")

    # Step 2: Statistical Analysis (ANCOVA or t-tests)
    print("2. Performing statistical analysis...")
    if covariates:
        print("   Using ANCOVA with covariates...")
        significant_results, all_results, significant_features = ANCOVAAnalyzer.analyze_glycans_ancova(
            data=data,
            feature_prefix=feature_prefix,
            class_column=target_col,
            covar_columns=covariates,
            alpha=0.05
        )

        pipeline_results["statistical_analysis"] = {
            "method": "ANCOVA",
            "significant_results": significant_results,
            "all_results": all_results,
            "significant_features": significant_features,
            "covariates_used": covariates
        }
    else:
        print("   Using direct group comparison...")
        # Implement basic statistical testing
        feature_cols = [col for col in data.columns if col.startswith(feature_prefix)]
        groups = data[target_col].unique()

        if len(groups) == 2:
            from isospec_data_tools.analysis import perform_welch_t_test, adjust_p_values

            group1_data = data[data[target_col] == groups[0]]
            group2_data = data[data[target_col] == groups[1]]

            t_test_results = []
            for feature in feature_cols:
                try:
                    result = perform_welch_t_test(
                        group1_data=group1_data[feature].dropna(),
                        group2_data=group2_data[feature].dropna()
                    )
                    result["feature"] = feature
                    t_test_results.append(result)
                except:
                    continue

            if t_test_results:
                results_df = pd.DataFrame(t_test_results)
                results_df["p_adjusted"] = adjust_p_values(
                    results_df["p_value"].tolist(), method="fdr_bh"
                )

                significant_features = results_df[
                    results_df["p_adjusted"] < 0.05
                ]["feature"].tolist()

                pipeline_results["statistical_analysis"] = {
                    "method": "t-test",
                    "results_df": results_df,
                    "significant_features": significant_features
                }

    # Step 3: Glycowork Analysis (if requested and applicable)
    if use_glycowork and feature_prefix.lower() in ["g", "glyc", "glycan"]:
        print("3. Performing glycowork structural analysis...")
        try:
            glycan_cols = [col for col in data.columns if col.startswith(feature_prefix)]
            glyco_analyzer = GlycoworkAnalyzer(
                glycan_data=data,
                glycan_columns=glycan_cols
            )

            structural_results = glyco_analyzer.analyze_glycan_structures(
                group_col=target_col,
                analysis_type="linkage_analysis"
            )

            pipeline_results["glycowork_analysis"] = {
                "structural_results": structural_results,
                "analyzed_glycans": len(glycan_cols)
            }
        except Exception as e:
            print(f"   Glycowork analysis failed: {e}")
            pipeline_results["glycowork_analysis"] = {"error": str(e)}

    # Step 4: Generate Summary
    print("4. Generating summary...")
    summary = {
        "total_features_analyzed": len([col for col in data.columns if col.startswith(feature_prefix)]),
        "significant_features": len(pipeline_results["statistical_analysis"].get("significant_features", [])),
        "confounders_identified": len(pipeline_results["confounder_analysis"].get("confounders", {})),
        "analysis_methods_used": []
    }

    if pipeline_results["confounder_analysis"]:
        summary["analysis_methods_used"].append("Confounder Analysis")

    if pipeline_results["statistical_analysis"]:
        method = pipeline_results["statistical_analysis"]["method"]
        summary["analysis_methods_used"].append(f"Statistical Testing ({method})")

    if pipeline_results["glycowork_analysis"] and "error" not in pipeline_results["glycowork_analysis"]:
        summary["analysis_methods_used"].append("Glycowork Structural Analysis")

    pipeline_results["summary"] = summary

    print("Specialized analysis pipeline complete!")
    print(f"  Methods used: {', '.join(summary['analysis_methods_used'])}")
    print(f"  Significant features: {summary['significant_features']}/{summary['total_features_analyzed']}")

    return pipeline_results

# Run complete pipeline
complete_results = complete_specialized_analysis_pipeline(
    data=metabolomics_data,
    feature_prefix="FT-",
    target_col="disease_status",
    potential_confounders=["age", "sex", "bmi"],
    use_glycowork=False  # Set to True for glycomics data
)
```

### Results Integration and Reporting

```python
def generate_specialized_analysis_report(pipeline_results, output_dir="specialized_analysis"):
    """Generate comprehensive report from specialized analysis results."""

    import os
    import json
    from pathlib import Path

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate text report
    report_lines = [
        "# Specialized Analysis Report",
        f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        f"- Total features analyzed: {pipeline_results['summary']['total_features_analyzed']}",
        f"- Significant features: {pipeline_results['summary']['significant_features']}",
        f"- Analysis methods: {', '.join(pipeline_results['summary']['analysis_methods_used'])}",
        ""
    ]

    # Confounder analysis section
    if pipeline_results["confounder_analysis"]:
        report_lines.extend([
            "## Confounder Analysis",
            f"- Features affected by confounders: {len(pipeline_results['confounder_analysis']['affected_features'])}",
            ""
        ])

        for confounder, effects in pipeline_results["confounder_analysis"]["confounders"].items():
            total_affected = sum(len(features) for features in effects.values())
            report_lines.append(f"- {confounder}: {total_affected} features affected")

    # Statistical analysis section
    if pipeline_results["statistical_analysis"]:
        method = pipeline_results["statistical_analysis"]["method"]
        report_lines.extend([
            "",
            f"## Statistical Analysis ({method})",
            f"- Significant features: {len(pipeline_results['statistical_analysis']['significant_features'])}",
            ""
        ])

        if "covariates_used" in pipeline_results["statistical_analysis"]:
            covariates = pipeline_results["statistical_analysis"]["covariates_used"]
            report_lines.append(f"- Covariates controlled: {', '.join(covariates)}")

    # Glycowork analysis section
    if pipeline_results["glycowork_analysis"] and "error" not in pipeline_results["glycowork_analysis"]:
        report_lines.extend([
            "",
            "## Glycowork Structural Analysis",
            f"- Glycans analyzed: {pipeline_results['glycowork_analysis']['analyzed_glycans']}",
            "- Structural patterns identified (see detailed results)"
        ])

    # Write text report
    with open(os.path.join(output_dir, "analysis_report.md"), "w") as f:
        f.write("\n".join(report_lines))

    # Save detailed results as JSON
    # Convert non-serializable objects to strings
    serializable_results = {}
    for key, value in pipeline_results.items():
        if key == "statistical_analysis" and "results_df" in value:
            # Convert DataFrame to dict
            value = value.copy()
            if "results_df" in value:
                value["results_df"] = value["results_df"].to_dict("records")
        serializable_results[key] = value

    with open(os.path.join(output_dir, "detailed_results.json"), "w") as f:
        json.dump(serializable_results, f, indent=2, default=str)

    print(f"Specialized analysis report saved to: {output_dir}")
    return os.path.join(output_dir, "analysis_report.md")

# Generate report
report_path = generate_specialized_analysis_report(complete_results)
print(f"Report saved to: {report_path}")
```

## Best Practices

### 1. Choose Appropriate Analysis Method

```python
def recommend_analysis_method(data, target_col, potential_confounders=None):
    """Recommend appropriate specialized analysis method based on data characteristics."""

    recommendations = []

    # Check sample size
    sample_size = len(data)
    groups = data[target_col].nunique()

    if sample_size < 30:
        recommendations.append("Warning: Small sample size may limit statistical power")

    # Check for potential confounders
    if potential_confounders:
        confounders_present = [col for col in potential_confounders if col in data.columns]
        if confounders_present:
            recommendations.append(f"Use ANCOVA to control for: {', '.join(confounders_present)}")
        else:
            recommendations.append("Specified confounders not found in data")

    # Check group balance
    group_sizes = data[target_col].value_counts()
    min_group_size = group_sizes.min()
    max_group_size = group_sizes.max()

    if max_group_size / min_group_size > 3:
        recommendations.append("Warning: Unbalanced groups - consider stratified analysis")

    # Check for glycan data
    glycan_cols = [col for col in data.columns if col.lower().startswith('g')]
    if len(glycan_cols) > 10:
        recommendations.append("Consider glycowork integration for structural analysis")

    return recommendations

# Get recommendations
recommendations = recommend_analysis_method(
    data=metabolomics_data,
    target_col="disease_status",
    potential_confounders=["age", "sex", "bmi"]
)

for rec in recommendations:
    print(f"• {rec}")
```

### 2. Validate Analysis Assumptions

```python
def validate_analysis_assumptions(data, target_col, feature_cols):
    """Validate assumptions for specialized analyses."""

    validation_results = {
        "normality": {},
        "homoscedasticity": {},
        "independence": {},
        "linearity": {}
    }

    from scipy import stats

    groups = data[target_col].unique()

    # Test normality for each feature within each group
    for feature in feature_cols[:5]:  # Test first 5 features as example
        validation_results["normality"][feature] = {}
        for group in groups:
            group_data = data[data[target_col] == group][feature].dropna()
            if len(group_data) > 3:
                _, p_value = stats.shapiro(group_data)
                validation_results["normality"][feature][group] = {
                    "shapiro_p": p_value,
                    "normal": p_value > 0.05
                }

    # Test homoscedasticity (equal variances)
    for feature in feature_cols[:5]:
        group_data = [data[data[target_col] == group][feature].dropna() for group in groups]
        group_data = [g for g in group_data if len(g) > 3]

        if len(group_data) >= 2:
            _, p_value = stats.levene(*group_data)
            validation_results["homoscedasticity"][feature] = {
                "levene_p": p_value,
                "equal_variances": p_value > 0.05
            }

    return validation_results

# Validate assumptions
assumptions = validate_analysis_assumptions(
    data=metabolomics_data,
    target_col="treatment",
    feature_cols=[col for col in metabolomics_data.columns if col.startswith("FT-")]
)

# Summary of assumption violations
for assumption, results in assumptions.items():
    if results:
        violations = sum(1 for feature_results in results.values()
                        for test_result in feature_results.values()
                        if isinstance(test_result, dict) and not test_result.get(list(test_result.keys())[-1]))
        print(f"{assumption.title()}: {violations} violations detected")
```

## Troubleshooting

### Common Issues and Solutions

```python
# Issue 1: ANCOVA fails due to missing covariates
def handle_missing_covariates(data, covar_columns):
    """Handle missing values in covariate columns."""

    missing_counts = data[covar_columns].isna().sum()
    print("Missing covariate data:")
    for col, count in missing_counts.items():
        print(f"  {col}: {count} missing values")

    # Options for handling missing covariates
    if missing_counts.sum() > 0:
        print("\nOptions:")
        print("1. Remove samples with missing covariates (complete case analysis)")
        print("2. Impute missing covariate values")
        print("3. Exclude problematic covariates")

        # Complete case analysis
        complete_cases = data.dropna(subset=covar_columns)
        print(f"\nComplete case analysis would retain {len(complete_cases)} of {len(data)} samples")

        return complete_cases

    return data

# Issue 2: No significant results
def diagnose_no_significant_results(data, target_col, feature_cols):
    """Diagnose why no significant results were found."""

    print("Diagnosing lack of significant results...")

    # Check sample sizes
    group_sizes = data[target_col].value_counts()
    print(f"Group sizes: {dict(group_sizes)}")

    if group_sizes.min() < 5:
        print("Warning: Very small group sizes may lack statistical power")

    # Check effect sizes
    from isospec_data_tools.analysis import perform_welch_t_test

    groups = data[target_col].unique()
    if len(groups) == 2:
        effect_sizes = []
        for feature in feature_cols[:10]:  # Sample first 10 features
            try:
                group1_data = data[data[target_col] == groups[0]][feature].dropna()
                group2_data = data[data[target_col] == groups[1]][feature].dropna()

                result = perform_welch_t_test(group1_data, group2_data)
                if 'effect_size' in result:
                    effect_sizes.append(abs(result['effect_size']))
            except:
                continue

        if effect_sizes:
            avg_effect_size = np.mean(effect_sizes)
            print(f"Average effect size: {avg_effect_size:.3f}")

            if avg_effect_size < 0.2:
                print("Small effect sizes suggest true differences may be minimal")
            elif avg_effect_size < 0.5:
                print("Medium effect sizes - may need larger sample size for detection")
            else:
                print("Large effect sizes - check for technical issues")

# Issue 3: Glycowork integration fails
def troubleshoot_glycowork_integration(data, glycan_columns):
    """Troubleshoot glycowork integration issues."""

    print("Troubleshooting glycowork integration...")

    # Check glycan column naming
    print(f"Glycan columns found: {len(glycan_columns)}")
    if len(glycan_columns) == 0:
        print("No glycan columns detected - check feature prefix")
        return False

    # Check for required glycowork dependencies
    try:
        import glycowork
        print("Glycowork library available")
    except ImportError:
        print("Error: Glycowork library not installed")
        print("Install with: pip install glycowork")
        return False

    # Check data format
    glycan_data_sample = data[glycan_columns].head()
    print("Sample glycan data:")
    print(glycan_data_sample)

    # Check for missing values
    missing_in_glycans = data[glycan_columns].isna().sum().sum()
    total_values = len(data) * len(glycan_columns)
    missing_rate = missing_in_glycans / total_values * 100

    print(f"Missing data in glycans: {missing_rate:.1f}%")
    if missing_rate > 50:
        print("Warning: High missing data rate may affect glycowork analysis")

    return True
```

## API Reference

::: isospec_data_tools.analysis.specialized.ancova_analysis.ANCOVAAnalyzer
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.specialized.confounder_analysis.ConfounderAnalyzer
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.analysis.specialized.glycowork_integration.GlycoworkAnalyzer
handler: python
options:
show_root_heading: true
show_source: false
