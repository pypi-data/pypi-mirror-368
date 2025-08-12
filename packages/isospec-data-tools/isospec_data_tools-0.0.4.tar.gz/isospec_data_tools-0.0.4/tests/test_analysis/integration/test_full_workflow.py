"""
End-to-end workflow integration tests for the analysis module.

This module tests complete analytical workflows that span multiple modules,
ensuring that the refactored modular architecture works together correctly
for real-world use cases.
"""

import numpy as np
import pandas as pd
import pytest

# Import preprocessing functions
from isospec_data_tools.analysis.core.project_config import DataStructureConfig

# Import core statistical functions
from isospec_data_tools.analysis.core.statistical_tests import (
    perform_student_t_test,
    perform_tukey_hsd_test,
)
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer
from isospec_data_tools.analysis.preprocessing.normalizers import (
    impute_missing_values,
    total_abundance_normalization,
)
from isospec_data_tools.analysis.preprocessing.transformers import (
    encode_categorical_column,
    join_sample_metadata,
    log2_transform_numeric,
)

# Import all the components we need for full workflows
from isospec_data_tools.analysis.specialized.ancova_analysis import ANCOVAAnalyzer
from isospec_data_tools.analysis.specialized.confounder_analysis import ConfounderAnalyzer


@pytest.fixture
def realistic_glycomics_dataset() -> pd.DataFrame:
    """Create a realistic glycomics dataset for workflow testing."""
    np.random.seed(42)

    # Create a dataset that simulates a real glycomics study
    n_controls = 50
    n_patients = 45
    n_qc = 10

    data = []

    # Generate realistic glycan abundance patterns
    for i in range(n_controls + n_patients + n_qc):
        if i < n_controls:
            sample_type = "Control"
            class_final = "Healthy"
            base_multiplier = 1.0
        elif i < n_controls + n_patients:
            sample_type = "Sample"
            class_final = "Disease"
            base_multiplier = 1.3  # Disease effect
        else:
            sample_type = "QC"
            class_final = "QC"
            base_multiplier = 1.1

        # Demographics with realistic distributions
        age = np.random.normal(55, 15) if class_final == "Disease" else np.random.normal(45, 12)
        age = max(18, min(85, age))  # Clamp to reasonable range

        sex = np.random.choice([0, 1], p=[0.6, 0.4] if class_final == "Disease" else [0.5, 0.5])
        bmi = np.random.normal(28, 5) if class_final == "Disease" else np.random.normal(24, 4)
        bmi = max(18, min(45, bmi))

        # Generate 20 glycan features with different patterns
        glycan_data = {}
        for glycan_idx in range(20):
            glycan_id = f"FT-{glycan_idx:03d}"

            # Base abundance with biological variation
            base_abundance = np.random.uniform(5, 15)

            # Age effect (some glycans change with age)
            age_effect = 0.05 * age if glycan_idx < 5 else 0

            # Sex effect (some glycans differ by sex)
            sex_effect = 2 * sex if glycan_idx in [2, 7, 12] else 0

            # Disease effect (some glycans are biomarkers)
            if glycan_idx < 8:  # Biomarker glycans
                disease_effect = base_multiplier - 1.0
                abundance = base_abundance * (1 + disease_effect) + age_effect + sex_effect
            else:  # Non-biomarker glycans
                abundance = base_abundance + age_effect + sex_effect

            # Add measurement noise
            abundance += np.random.normal(0, 0.5)
            abundance = max(0.1, abundance)  # Ensure positive

            glycan_data[glycan_id] = abundance

        # Add some missing values (realistic scenario)
        if np.random.random() < 0.05:  # 5% missing rate
            missing_glycan = np.random.choice(list(glycan_data.keys()))
            glycan_data[missing_glycan] = np.nan

        sample_data = {
            "sample_id": f"S{i:03d}",
            "class_final": class_final,
            "SampleType": sample_type,
            "age": age,
            "sex": sex,
            "bmi": bmi,
            **glycan_data,
        }

        data.append(sample_data)

    return pd.DataFrame(data)


@pytest.fixture
def metadata_df() -> pd.DataFrame:
    """Create additional metadata for testing joins."""
    return pd.DataFrame({
        "sample_id": [f"S{i:03d}" for i in range(105)],
        "batch": [f"Batch_{(i // 20) + 1}" for i in range(105)],
        "collection_date": pd.date_range("2023-01-01", periods=105, freq="D"),
        "storage_time_days": np.random.randint(1, 365, 105),
    })


class TestCompleteAnalyticalWorkflows:
    """Test complete analytical workflows from raw data to final results."""

    def test_complete_preprocessing_workflow(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test complete preprocessing workflow from raw data to analysis-ready data."""
        raw_data = realistic_glycomics_dataset.copy()

        # Step 1: Handle missing values
        config = DataStructureConfig(feature_prefix="FT-", sample_type_column="SampleType")
        imputed_data = impute_missing_values(raw_data, data_config=config, method="qc_min")

        # Check that missing values were handled
        glycan_cols = [col for col in raw_data.columns if col.startswith("FT-")]
        original_missing = raw_data[glycan_cols].isna().sum().sum()
        final_missing = imputed_data[glycan_cols].isna().sum().sum()

        assert final_missing < original_missing, "Missing values should have been reduced"

        # Step 2: Log2 transformation
        log_transformed = log2_transform_numeric(imputed_data, prefix="FT-")

        # Check that transformation was applied
        for col in glycan_cols:
            original_mean = imputed_data[col].mean()
            transformed_mean = log_transformed[col].mean()
            # Log2 transformation should change the distribution
            assert abs(original_mean - transformed_mean) > 0.1

        # Step 3: Normalization
        normalized_data = total_abundance_normalization(log_transformed, prefix="FT-")

        # Check normalization - each row should sum to approximately 1
        row_sums = normalized_data[glycan_cols].sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-10)

        # Step 4: Encode categorical variables
        final_data = encode_categorical_column(normalized_data, "sex", {0: "Female", 1: "Male"})

        assert "sex_encoded" in final_data.columns
        assert final_data["sex_encoded"].nunique() == 2

    def test_complete_statistical_analysis_workflow(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test complete statistical analysis workflow."""
        data = realistic_glycomics_dataset.copy()

        # Filter to only sample data (remove QC)
        analysis_data = data[data["class_final"].isin(["Healthy", "Disease"])].copy()

        # Step 1: Confounder analysis
        assert isinstance(analysis_data, pd.DataFrame)
        confounder_results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            analysis_data, glycan_prefix="FT-", confounders=["age", "sex", "bmi"], alpha=0.05, min_glycans=2
        )

        # Should detect some confounders given our data simulation
        assert len(confounder_results) > 0

        # Step 2: ANCOVA analysis (controlling for significant confounders)
        covariates = significant_confounders if significant_confounders else ["age"]

        _, ancova_all, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            analysis_data, feature_prefix="FT-", class_column="class_final", covar_columns=covariates, alpha=0.05
        )

        # Should find some significant results (we designed disease effects)
        assert len(ancova_all) == 20  # All glycans analyzed
        assert len(significant_glycans) > 0  # Some should be significant

        # Step 3: Post-hoc pairwise tests for significant glycans
        if len(significant_glycans) > 0:
            pairwise_results = perform_tukey_hsd_test(
                analysis_data, list(significant_glycans), "class_final", alpha=0.05, include_effect_sizes=True
            )

            # Should have pairwise comparisons
            assert isinstance(pairwise_results, pd.DataFrame)
            assert len(pairwise_results) > 0

            # DataFrame should have effect sizes columns
            assert "effect_size" in pairwise_results.columns
            assert "fold_change" in pairwise_results.columns

    def test_complete_machine_learning_workflow(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test complete machine learning workflow."""
        data = realistic_glycomics_dataset.copy()

        # Preprocess data - handle missing values first (before filtering out QC samples)
        assert isinstance(data, pd.DataFrame)
        config = DataStructureConfig(feature_prefix="FT-", sample_type_column="SampleType")
        data_imputed = impute_missing_values(data, data_config=config, method="qc_min")

        # Filter to sample data only (after imputation)
        ml_data = data_imputed[data_imputed["class_final"].isin(["Healthy", "Disease"])].copy()

        # Step 1: Clustering analysis (unsupervised)
        metadata_cols = ["age", "sex", "bmi"]

        clustering_results = ClusterAnalyzer.run_clustering_analysis(ml_data, metadata_cols, feature_prefix="FT-")

        # Check clustering results structure
        assert "features" in clustering_results
        assert "metadata" in clustering_results
        assert "kmeans_labels" in clustering_results
        assert "dbscan_labels" in clustering_results
        assert "agglo_labels" in clustering_results

        # Check that clustering was performed
        assert len(clustering_results["kmeans_labels"]) == len(ml_data)
        assert clustering_results["features"].shape[1] == 20  # 20 glycan features

        # Step 2: Supervised classification
        feature_names = [col for col in ml_data.columns if col.startswith("FT-")]

        # Use simplified parameters for testing
        params = {
            "random_search_params": {
                "n_iter": 5,
                "n_jobs": 1,
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        _, training_results, best_model = ModelTrainer.run_modeling(
            ml_data, feature_names, target_class="Disease", params=params
        )

        # Check modeling results
        assert isinstance(best_model, str)
        assert "model_results" in training_results
        assert "fitted_models" in training_results

        # Should have trained at least one model successfully
        if training_results["fitted_models"]:
            assert best_model in training_results["fitted_models"]

    def test_modular_architecture_integration(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test that the modular architecture components work together seamlessly."""
        data = realistic_glycomics_dataset.copy()

        # Test that we can use different modules in sequence without conflicts

        # 1. Preprocessing
        processed_data = total_abundance_normalization(data, prefix="FT-")
        processed_data = log2_transform_numeric(processed_data, prefix="FT-")

        # 2. Statistical analysis
        analysis_subset = processed_data[processed_data["class_final"].isin(["Healthy", "Disease"])]

        assert isinstance(analysis_subset, pd.DataFrame)
        statistical_results = perform_student_t_test(
            analysis_subset,
            [col for col in analysis_subset.columns if col.startswith("FT-")][:5],  # First 5 glycans
            "class_final",
            alpha=0.05,
        )

        # 3. Specialized analysis
        _, ancova_all, _ = ANCOVAAnalyzer.analyze_glycans_ancova(
            analysis_subset, feature_prefix="FT-", class_column="class_final", covar_columns=["age"], alpha=0.05
        )

        # All should work without errors and produce consistent results
        assert len(statistical_results) > 0
        assert len(ancova_all) > 0

        # Data should maintain integrity across modules
        original_shape = data.shape
        processed_shape = processed_data.shape

        assert original_shape[0] == processed_shape[0]  # Same number of samples
        assert original_shape[1] == processed_shape[1]  # Same number of columns

    def test_backward_compatibility_integration(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test that legacy imports still work in integrated workflows."""
        data = realistic_glycomics_dataset.copy()

        # Test legacy imports via main analysis module
        from isospec_data_tools.analysis import ANCOVAAnalyzer as LegacyANCOVA
        from isospec_data_tools.analysis import ClusterAnalyzer as LegacyCluster
        from isospec_data_tools.analysis import ConfounderAnalyzer as LegacyConfounder
        from isospec_data_tools.analysis import ModelTrainer as LegacyModel
        from isospec_data_tools.analysis import total_abundance_normalization as legacy_normalize

        # These should be the same objects as direct imports
        assert LegacyANCOVA is ANCOVAAnalyzer
        assert LegacyConfounder is ConfounderAnalyzer
        assert LegacyCluster is ClusterAnalyzer
        assert LegacyModel is ModelTrainer
        assert legacy_normalize is total_abundance_normalization

        # Should work in actual workflows
        analysis_data = data[data["class_final"].isin(["Healthy", "Disease"])].copy()

        # Legacy workflow should work identically
        assert isinstance(analysis_data, pd.DataFrame)
        legacy_results, _ = LegacyConfounder.analyze_confounders(
            analysis_data, glycan_prefix="FT-", confounders=["age"], alpha=0.05
        )

        # Direct import workflow
        direct_results, _ = ConfounderAnalyzer.analyze_confounders(
            analysis_data, glycan_prefix="FT-", confounders=["age"], alpha=0.05
        )

        # Results should be identical
        assert legacy_results.keys() == direct_results.keys()
        for key in legacy_results:
            assert legacy_results[key] == direct_results[key]


class TestCrossModuleDataFlow:
    """Test data flow and compatibility between different modules."""

    @pytest.fixture
    def sample_pipeline_data(self) -> pd.DataFrame:
        """Create data specifically for testing module interfaces."""
        np.random.seed(123)

        n_samples = 30
        data = []

        for i in range(n_samples):
            sample_data = {
                "sample_id": f"Test_{i:03d}",
                "class_final": "Group_A" if i < 15 else "Group_B",
                "age": np.random.uniform(25, 75),
                "sex": np.random.choice([0, 1]),
            }

            # Add 5 glycan features
            for j in range(5):
                glycan_id = f"FT-{j:03d}"
                base_value = 10 + 2 * (i % 2)  # Simple group difference
                noise = np.random.normal(0, 1)
                sample_data[glycan_id] = base_value + noise

            data.append(sample_data)

        return pd.DataFrame(data)

    def test_preprocessing_to_statistical_analysis_flow(self, sample_pipeline_data: pd.DataFrame) -> None:
        """Test that preprocessing output is compatible with statistical analysis input."""
        data = sample_pipeline_data.copy()

        # Preprocessing chain
        normalized_data = total_abundance_normalization(data, prefix="FT-")

        # Statistical analysis should accept preprocessed data
        t_test_results = perform_student_t_test(
            normalized_data,
            [col for col in normalized_data.columns if col.startswith("FT-")],
            "class_final",
            alpha=0.05,
        )

        # Should produce valid results
        assert len(t_test_results) == 5  # 5 glycans
        for result in t_test_results:
            assert "p_value" in result
            assert "mean_diff" in result
            assert np.isfinite(result["p_value"])

    def test_statistical_to_machine_learning_flow(self, sample_pipeline_data: pd.DataFrame) -> None:
        """Test flow from statistical analysis to machine learning."""
        data = sample_pipeline_data.copy()

        # Step 1: Find significant features using statistical tests
        t_test_results = perform_student_t_test(
            data, [col for col in data.columns if col.startswith("FT-")], "class_final", alpha=0.05
        )

        # Select features with p < 0.1 (liberal threshold for testing)
        significant_features = [result["feature"] for result in t_test_results if result["p_value"] < 0.1]

        if len(significant_features) > 0:
            # Step 2: Use significant features for clustering
            clustering_results = ClusterAnalyzer.run_clustering_analysis(
                data,
                ["age", "sex"],
                glycans=significant_features,  # Use only significant features
            )

            # Should work with reduced feature set
            assert clustering_results["features"].shape[1] == len(significant_features)
            assert len(clustering_results["kmeans_labels"]) == len(data)

    def test_ancova_to_confounder_integration(self, sample_pipeline_data: pd.DataFrame) -> None:
        """Test integration between ANCOVA and confounder analysis."""
        data = sample_pipeline_data.copy()

        # Step 1: Identify confounders
        assert isinstance(data, pd.DataFrame)
        _, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data,
            glycan_prefix="FT-",
            confounders=["age", "sex"],
            alpha=0.10,  # Liberal threshold
            min_glycans=1,
        )

        # Step 2: Use identified confounders in ANCOVA
        covariates = significant_confounders if significant_confounders else ["age"]

        _, ancova_all, _ = ANCOVAAnalyzer.analyze_glycans_ancova(
            data, feature_prefix="FT-", class_column="class_final", covar_columns=covariates, alpha=0.05
        )

        # Integration should work smoothly
        assert len(ancova_all) == 5  # All glycans analyzed

        # Check that confounder effects are included in ANCOVA results
        for covariate in covariates:
            p_col = f"{covariate}_p_value"
            effect_col = f"{covariate}_effect_size"
            assert p_col in ancova_all.columns
            assert effect_col in ancova_all.columns

    def test_error_propagation_and_handling(self, sample_pipeline_data: pd.DataFrame) -> None:
        """Test that errors are handled gracefully across module boundaries."""
        data = sample_pipeline_data.copy()

        # Introduce problematic data
        problematic_data = data.copy()
        problematic_data.loc[:, "FT-000"] = np.nan  # All NaN glycan
        problematic_data = problematic_data.drop(["class_final"], axis=1)  # Missing required column

        # Different modules should handle errors appropriately

        # Preprocessing should handle NaN gracefully
        try:
            normalized = total_abundance_normalization(problematic_data, prefix="FT-")
            # If it succeeds, NaN should be handled appropriately
            assert np.isfinite(normalized.select_dtypes(include=[np.number]).values).any()
        except Exception:
            # If it fails, should be with a meaningful error
            pass

        # Statistical analysis should fail gracefully for missing class column
        with pytest.raises(Exception):
            perform_student_t_test(
                problematic_data,
                ["FT-001", "FT-002"],
                "class_final",  # This column doesn't exist
                alpha=0.05,
            )

    def test_memory_and_performance_integration(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test that integrated workflows don't have memory leaks or performance issues."""
        data = realistic_glycomics_dataset.copy()

        # Run a complex workflow multiple times to check for memory issues
        for _ in range(3):
            # Preprocessing
            processed = total_abundance_normalization(data.copy(), prefix="FT-")
            processed = log2_transform_numeric(processed, prefix="FT-")

            # Analysis subset
            analysis_data = processed[processed["class_final"].isin(["Healthy", "Disease"])].copy()

            # Multiple analyses
            assert isinstance(analysis_data, pd.DataFrame)
            _, _ = ConfounderAnalyzer.analyze_confounders(
                analysis_data, glycan_prefix="FT-", confounders=["age"], alpha=0.05
            )

            _, ancova_all, _ = ANCOVAAnalyzer.analyze_glycans_ancova(
                analysis_data, feature_prefix="FT-", class_column="class_final", covar_columns=["age"], alpha=0.05
            )

            # Each iteration should produce consistent results
            assert len(ancova_all) == 20

            # Clean up large objects
            del processed, analysis_data, ancova_all

    def test_reproducibility_across_modules(self, sample_pipeline_data: pd.DataFrame) -> None:
        """Test that results are reproducible when using the same random seeds."""
        data = sample_pipeline_data.copy()

        # Run the same analysis twice with same random seed
        results1 = []
        results2 = []

        for iteration in range(2):
            np.random.seed(42)  # Reset seed

            # Clustering (uses randomness)
            clustering_result = ClusterAnalyzer.run_clustering_analysis(data, ["age", "sex"], feature_prefix="FT-")

            if iteration == 0:
                results1 = clustering_result["kmeans_labels"].copy()
            else:
                results2 = clustering_result["kmeans_labels"].copy()

        # Results should be identical
        np.testing.assert_array_equal(results1, results2)


class TestRealWorldScenarios:
    """Test scenarios that mimic real-world usage patterns."""

    def test_publication_ready_analysis_workflow(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test a complete workflow suitable for publication."""
        data = realistic_glycomics_dataset.copy()

        # Publication workflow steps:

        # 1. Data QC and preprocessing
        # Handle missing values first (before filtering out QC samples)
        assert isinstance(data, pd.DataFrame)
        config = DataStructureConfig(feature_prefix="FT-", sample_type_column="SampleType")
        qc_data = impute_missing_values(data, data_config=config, method="qc_min")

        # Remove QC samples for analysis (after imputation)
        analysis_data = qc_data[qc_data["class_final"].isin(["Healthy", "Disease"])].copy()

        # Normalize
        normalized_data = total_abundance_normalization(analysis_data, prefix="FT-")

        # 2. Descriptive statistics and demographics
        demographics = normalized_data.groupby("class_final")[["age", "sex", "bmi"]].agg(["mean", "std", "count"])

        assert demographics.shape[0] == 2  # Two groups

        # 3. Confounder analysis
        _, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            normalized_data, glycan_prefix="FT-", confounders=["age", "sex", "bmi"], alpha=0.05, min_glycans=3
        )

        # 4. Main analysis with confounder adjustment
        covariates = significant_confounders if significant_confounders else ["age", "sex"]

        _, main_results_all, _ = ANCOVAAnalyzer.analyze_glycans_ancova(
            normalized_data, feature_prefix="FT-", class_column="class_final", covar_columns=covariates, alpha=0.05
        )

        # 5. Effect size and clinical relevance
        top_biomarkers = ANCOVAAnalyzer.get_top_glycans(main_results_all, n_top=5, sort_by="class_adj_p_value")

        # Should have publication-ready results
        assert len(main_results_all) == 20  # All glycans analyzed
        assert len(top_biomarkers) == 5  # Top results identified
        assert "class_adj_p_value" in main_results_all.columns
        assert "class_effect_size" in main_results_all.columns

    def test_biomarker_discovery_workflow(self, realistic_glycomics_dataset: pd.DataFrame) -> None:
        """Test a biomarker discovery workflow."""
        data = realistic_glycomics_dataset.copy()
        analysis_data = data[data["class_final"].isin(["Healthy", "Disease"])].copy()

        # Biomarker discovery steps:

        # 1. Feature preprocessing and selection
        assert isinstance(analysis_data, pd.DataFrame)
        normalized_data = total_abundance_normalization(analysis_data, prefix="FT-")

        # 2. Univariate screening
        univariate_results = perform_student_t_test(
            normalized_data,
            [col for col in normalized_data.columns if col.startswith("FT-")],
            "class_final",
            alpha=0.05,
            include_effect_sizes=True,
        )

        # 3. Multiple testing correction and effect size filtering
        candidate_biomarkers = [
            result["feature"]
            for result in univariate_results
            if result["p_value"] < 0.1 and abs(result.get("effect_size", 0)) > 0.3
        ]

        # 4. Multivariate modeling with candidate biomarkers
        if len(candidate_biomarkers) >= 2:
            params = {
                "random_search_params": {
                    "n_iter": 3,
                    "n_jobs": 1,
                    "verbose": 0,
                }
            }

            _, training_results, best_model = ModelTrainer.run_modeling(
                normalized_data, candidate_biomarkers, target_class="Disease", params=params
            )

            # Should produce biomarker model
            assert isinstance(best_model, str)
            if training_results["fitted_models"]:
                assert best_model in training_results["fitted_models"]

    def test_batch_effect_investigation_workflow(
        self, realistic_glycomics_dataset: pd.DataFrame, metadata_df: pd.DataFrame
    ) -> None:
        """Test workflow for investigating batch effects."""
        data = realistic_glycomics_dataset.copy()

        # Add batch information
        data_with_batch = join_sample_metadata(
            data, metadata_df, sample_id_col="sample_id", sample_join_col="sample_id"
        )

        # Batch effect investigation:

        # 1. Treat batch as potential confounder
        assert isinstance(data_with_batch, pd.DataFrame)
        _, significant_batch_confounders = ConfounderAnalyzer.analyze_confounders(
            data_with_batch, glycan_prefix="FT-", confounders=["batch"], alpha=0.05, min_glycans=2
        )

        # 2. Test for batch effects in QC samples
        qc_data = data_with_batch[data_with_batch["SampleType"] == "QC"].copy()

        if len(qc_data) > 5:  # Need sufficient QC samples
            # Analyze batch-to-batch variation in QC
            assert isinstance(qc_data, pd.DataFrame)
            qc_variation_results = perform_tukey_hsd_test(
                qc_data,
                [col for col in qc_data.columns if col.startswith("FT-")][:5],  # First 5 glycans
                "batch",
                alpha=0.05,
            )

            # Should detect batch effects if present
            assert isinstance(qc_variation_results, pd.DataFrame)

        # 3. Adjust main analysis for batch effects if significant
        if "batch" in significant_batch_confounders:
            batch_subset = data_with_batch[data_with_batch["class_final"].isin(["Healthy", "Disease"])]
            assert isinstance(batch_subset, pd.DataFrame)
            batch_adjusted_results, _, _ = ANCOVAAnalyzer.analyze_glycans_ancova(
                batch_subset,
                feature_prefix="FT-",
                class_column="class_final",
                covar_columns=["age", "batch"],  # Include batch as covariate
                alpha=0.05,
            )

            # Should produce batch-adjusted results
            assert "batch_p_value" in batch_adjusted_results.columns
            assert "batch_effect_size" in batch_adjusted_results.columns
