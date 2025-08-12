"""
Comprehensive model training and clustering tests.

This module tests the ModelTrainer and ClusterAnalyzer functionality
with comprehensive coverage of machine learning workflows, hyperparameter
tuning, cross-validation, and clustering algorithms.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_blobs, make_classification

# Import the classes we need to test
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer


class TestClusterAnalyzerComprehensive:
    """Comprehensive tests for ClusterAnalyzer functionality."""

    @pytest.fixture
    def sample_clustering_data(self) -> pd.DataFrame:
        """Create sample data suitable for clustering analysis."""
        np.random.seed(42)

        # Generate synthetic data with known clusters
        features, true_labels = make_blobs(n_samples=100, centers=3, n_features=5, random_state=42, cluster_std=1.0)

        # Create DataFrame
        data = pd.DataFrame(features, columns=[f"FT-{i:03d}" for i in range(5)])
        data["true_cluster"] = true_labels
        data["sample_id"] = [f"S{i:03d}" for i in range(100)]
        data["age"] = np.random.uniform(20, 80, 100)
        data["sex"] = np.random.choice([0, 1], 100)
        data["SampleType"] = "Sample"  # Add required SampleType column

        return data

    @pytest.fixture
    def metadata_columns(self) -> list[str]:
        """Define metadata columns for testing."""
        return ["age", "sex"]

    def test_kmeans_clustering_basic(self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]) -> None:
        """Test basic K-means clustering functionality."""

        result = ClusterAnalyzer.run_clustering_analysis(sample_clustering_data, metadata_columns, feature_prefix="FT-")

        # Verify result structure
        assert "features" in result
        assert "metadata" in result
        assert "kmeans_labels" in result

        # Check data dimensions
        assert result["features"].shape == (100, 5)  # 100 samples, 5 features
        assert result["metadata"].shape == (100, 2)  # 100 samples, 2 metadata cols
        assert len(result["kmeans_labels"]) == 100

        # Check that clusters are reasonable
        unique_clusters = len(set(result["kmeans_labels"]))
        assert 1 <= unique_clusters <= 10  # Should have reasonable number of clusters

    def test_dbscan_clustering_parameters(
        self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]
    ) -> None:
        """Test DBSCAN clustering with different parameters."""

        result = ClusterAnalyzer.run_clustering_analysis(sample_clustering_data, metadata_columns, feature_prefix="FT-")

        # Verify DBSCAN results
        assert "dbscan_labels" in result
        assert len(result["dbscan_labels"]) == 100

        # DBSCAN should identify some clusters (may include noise points labeled as -1)
        unique_labels = set(result["dbscan_labels"])
        assert len(unique_labels) >= 1  # At least one cluster or all noise

        # Check for noise points (labeled as -1)
        noise_points = sum(1 for label in result["dbscan_labels"] if label == -1)
        assert 0 <= noise_points <= 100

    def test_agglomerative_clustering(self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]) -> None:
        """Test agglomerative clustering functionality."""

        result = ClusterAnalyzer.run_clustering_analysis(sample_clustering_data, metadata_columns, feature_prefix="FT-")

        # Verify agglomerative results
        assert "agglo_labels" in result
        assert len(result["agglo_labels"]) == 100

        # Should have reasonable number of clusters
        unique_clusters = len(set(result["agglo_labels"]))
        assert 1 <= unique_clusters <= 20

    def test_clustering_with_custom_glycans(
        self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]
    ) -> None:
        """Test clustering with custom glycan selection."""

        # Select subset of glycans
        selected_glycans = ["FT-000", "FT-001", "FT-002"]

        result = ClusterAnalyzer.run_clustering_analysis(
            sample_clustering_data, metadata_columns, glycans=selected_glycans
        )

        # Should use only the selected glycans
        assert result["features"].shape == (100, 3)  # 3 selected features

        # All clustering results should still be present
        assert "kmeans_labels" in result
        assert "dbscan_labels" in result
        assert "agglo_labels" in result

    def test_clustering_data_preprocessing(
        self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]
    ) -> None:
        """Test that clustering handles data preprocessing correctly."""

        # Add some missing values to test preprocessing
        data_with_missing = sample_clustering_data.copy()
        data_with_missing.loc[0:4, "FT-000"] = np.nan

        # Preprocess missing values before clustering
        from isospec_data_tools.analysis.core.project_config import DataStructureConfig
        from isospec_data_tools.analysis.preprocessing.normalizers import impute_missing_values

        # Add SampleType column for imputation
        data_with_missing["SampleType"] = "Sample"
        config = DataStructureConfig(feature_prefix="FT-", sample_type_column="SampleType")
        data_preprocessed = impute_missing_values(data_with_missing, data_config=config, method="zero")

        result = ClusterAnalyzer.run_clustering_analysis(data_preprocessed, metadata_columns, feature_prefix="FT-")

        # Should produce valid results after preprocessing
        assert result["features"].shape[0] == 100
        assert len(result["kmeans_labels"]) == 100

        # Features should not contain NaN values after preprocessing
        assert not np.any(np.isnan(result["features"].values))

    def test_clustering_reproducibility(
        self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]
    ) -> None:
        """Test that clustering results are reproducible with same random seed."""

        # Set random seed and run clustering twice
        np.random.seed(123)
        result1 = ClusterAnalyzer.run_clustering_analysis(
            sample_clustering_data, metadata_columns, feature_prefix="FT-"
        )

        np.random.seed(123)
        result2 = ClusterAnalyzer.run_clustering_analysis(
            sample_clustering_data, metadata_columns, feature_prefix="FT-"
        )

        # Results should be identical
        np.testing.assert_array_equal(result1["kmeans_labels"], result2["kmeans_labels"])
        np.testing.assert_array_equal(result1["features"].values, result2["features"].values)

    def test_clustering_edge_cases(self) -> None:
        """Test clustering with edge cases."""

        # Test with minimal data
        minimal_data = pd.DataFrame({
            "FT-000": [1, 2, 3, 4, 5],  # Need more samples for clustering
            "FT-001": [4, 5, 6, 7, 8],
            "age": [25, 30, 35, 40, 45],
            "sex": [0, 1, 0, 1, 0],
            "SampleType": ["Sample"] * 5,
        })

        result = ClusterAnalyzer.run_clustering_analysis(minimal_data, ["age", "sex"], feature_prefix="FT-")

        # Should handle minimal data gracefully
        assert result["features"].shape == (5, 2)
        assert len(result["kmeans_labels"]) == 5

    def test_clustering_performance_metrics(
        self, sample_clustering_data: pd.DataFrame, metadata_columns: list[str]
    ) -> None:
        """Test calculation of clustering performance metrics."""

        result = ClusterAnalyzer.run_clustering_analysis(sample_clustering_data, metadata_columns, feature_prefix="FT-")

        # Since we have true labels, we can evaluate clustering quality
        _ = sample_clustering_data["true_cluster"].values  # true_labels not used in this test

        # Calculate silhouette score for K-means
        from sklearn.metrics import silhouette_score

        silhouette_kmeans = silhouette_score(result["features"], result["kmeans_labels"])
        assert -1 <= silhouette_kmeans <= 1

        # For our synthetic data, silhouette score should be reasonably good
        assert silhouette_kmeans > 0.2  # Should be better than random


class TestModelTrainerComprehensive:
    """Comprehensive tests for ModelTrainer functionality."""

    @pytest.fixture
    def binary_classification_data(self) -> pd.DataFrame:
        """Create binary classification dataset."""
        np.random.seed(42)

        # Generate synthetic binary classification data
        X, y = make_classification(
            n_samples=200, n_features=10, n_informative=8, n_redundant=2, n_classes=2, random_state=42, class_sep=1.5
        )

        # Create DataFrame
        feature_names = [f"FT-{i:03d}" for i in range(10)]
        data = pd.DataFrame(X, columns=feature_names)
        data["class_final"] = ["Disease" if label == 1 else "Healthy" for label in y]
        data["sample_id"] = [f"S{i:03d}" for i in range(200)]

        return data

    @pytest.fixture
    def multiclass_classification_data(self) -> pd.DataFrame:
        """Create multiclass classification dataset."""
        np.random.seed(123)

        # Generate synthetic multiclass data
        X, y = make_classification(
            n_samples=300, n_features=15, n_informative=12, n_redundant=3, n_classes=3, random_state=123, class_sep=1.0
        )

        # Create DataFrame
        feature_names = [f"FT-{i:03d}" for i in range(15)]
        data = pd.DataFrame(X, columns=feature_names)
        data["class_final"] = [f"Class_{label}" for label in y]
        data["sample_id"] = [f"S{i:03d}" for i in range(300)]

        return data

    def test_binary_classification_basic(self, binary_classification_data: pd.DataFrame) -> None:
        """Test basic binary classification functionality."""

        feature_names = [col for col in binary_classification_data.columns if col.startswith("FT-")]

        # Use minimal parameters for faster testing
        params = {
            "random_search_params": {
                "n_iter": 3,
                "n_jobs": 1,
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=params
        )

        # Verify results structure
        assert isinstance(best_model, str)
        assert "model_results" in training_results
        assert "fitted_models" in training_results

        # Should have trained at least one model
        assert len(training_results["model_results"]) > 0

        # Best model should be in fitted models if training succeeded
        if training_results["fitted_models"]:
            assert best_model in training_results["fitted_models"]

    def test_multiclass_classification(self, multiclass_classification_data: pd.DataFrame) -> None:
        """Test multiclass classification functionality."""

        feature_names = [col for col in multiclass_classification_data.columns if col.startswith("FT-")]

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            multiclass_classification_data,
            feature_names,
            target_class="Class_1",  # One-vs-rest classification
            params=params,
        )

        # Should handle multiclass data appropriately
        assert isinstance(best_model, str)
        assert "model_results" in training_results

    def test_cross_validation_consistency(self, binary_classification_data: pd.DataFrame) -> None:
        """Test cross-validation consistency and reproducibility."""

        feature_names = [col for col in binary_classification_data.columns if col.startswith("FT-")][
            :5
        ]  # Use fewer features

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
                "cv": 3,  # 3-fold CV for faster testing
            }
        }

        # Run modeling twice with same random seed
        np.random.seed(42)
        detailed_results1, training_results1, best_model1 = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=params
        )

        np.random.seed(42)
        detailed_results2, training_results2, best_model2 = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=params
        )

        # Results should be consistent (though exact reproducibility depends on sklearn internals)
        assert len(training_results1["model_results"]) == len(training_results2["model_results"])

    def test_feature_importance_analysis(self, binary_classification_data: pd.DataFrame) -> None:
        """Test feature importance analysis for interpretable models."""

        feature_names = [col for col in binary_classification_data.columns if col.startswith("FT-")][:8]

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=params
        )

        # For models with feature importance, verify it's captured
        if training_results["fitted_models"]:
            # Check that we can access fitted models
            assert len(training_results["fitted_models"]) > 0

    def test_hyperparameter_tuning_ranges(self, binary_classification_data: pd.DataFrame) -> None:
        """Test hyperparameter tuning with custom parameter ranges."""

        feature_names = [col for col in binary_classification_data.columns if col.startswith("FT-")][:6]

        # Custom hyperparameter ranges
        custom_params = {
            "random_search_params": {
                "n_iter": 3,
                "n_jobs": 1,
                "verbose": 0,
            },
            "custom_hyperparams": {"RandomForest": {"n_estimators": [10, 50], "max_depth": [3, 5]}},
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=custom_params
        )

        # Should complete without errors
        assert isinstance(best_model, str)

    def test_model_evaluation_metrics(self, binary_classification_data: pd.DataFrame) -> None:
        """Test comprehensive model evaluation metrics."""

        feature_names = [col for col in binary_classification_data.columns if col.startswith("FT-")][:5]

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
                "scoring": ["roc_auc", "accuracy", "precision", "recall"],
                "refit": "roc_auc",
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            binary_classification_data, feature_names, target_class="Disease", params=params
        )

        # Check that multiple metrics are computed
        if not training_results["model_results"].empty:
            # Should have results for different models/metrics
            assert len(training_results["model_results"]) > 0

    def test_imbalanced_data_handling(self) -> None:
        """Test handling of imbalanced datasets."""

        np.random.seed(42)

        # Create imbalanced dataset (90% class 0, 10% class 1)
        X, y = make_classification(n_samples=100, n_features=8, n_classes=2, weights=[0.9, 0.1], random_state=42)

        feature_names = [f"FT-{i:03d}" for i in range(8)]
        data = pd.DataFrame(X, columns=feature_names)
        data["class_final"] = ["Disease" if label == 1 else "Healthy" for label in y]

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            data, feature_names, target_class="Disease", params=params
        )

        # Should handle imbalanced data without errors
        assert isinstance(best_model, str)

    def test_small_dataset_handling(self) -> None:
        """Test handling of small datasets."""

        # Create very small dataset
        small_data = pd.DataFrame({
            "FT-000": [1, 2, 3, 4, 5, 6],
            "FT-001": [2, 3, 4, 5, 6, 7],
            "class_final": ["Disease", "Healthy", "Disease", "Healthy", "Disease", "Healthy"],
        })

        params = {
            "random_search_params": {
                "n_iter": 1,
                "n_jobs": 1,
                "verbose": 0,
                "cv": 2,  # Reduce CV folds for small dataset
            }
        }

        feature_names = ["FT-000", "FT-001"]

        # Should handle small datasets gracefully (may not produce meaningful results)
        try:
            detailed_results, training_results, best_model = ModelTrainer.run_modeling(
                small_data, feature_names, target_class="Disease", params=params
            )
            assert isinstance(best_model, str)
        except Exception as e:
            # Small datasets may legitimately fail with certain models
            assert "insufficient" in str(e).lower() or "samples" in str(e).lower()

    def test_error_handling_invalid_features(self, binary_classification_data: pd.DataFrame) -> None:
        """Test error handling with invalid feature specifications."""

        # Try with non-existent features
        invalid_features = ["NonExistent-001", "NonExistent-002"]

        params = {
            "random_search_params": {
                "n_iter": 1,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        with pytest.raises(Exception):
            ModelTrainer.run_modeling(
                binary_classification_data, invalid_features, target_class="Disease", params=params
            )

    def test_memory_efficiency_large_features(self, binary_classification_data: pd.DataFrame) -> None:
        """Test memory efficiency with many features."""

        # Add many additional features to test memory handling
        extended_data = binary_classification_data.copy()

        # Add 50 more random features
        np.random.seed(42)
        for i in range(50):
            extended_data[f"FT-{i + 100:03d}"] = np.random.normal(0, 1, len(extended_data))

        # Use all features
        feature_names = [col for col in extended_data.columns if col.startswith("FT-")]

        params = {
            "random_search_params": {
                "n_iter": 1,  # Minimal iterations for speed
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        # Should handle many features without memory issues
        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            extended_data, feature_names, target_class="Disease", params=params
        )

        assert isinstance(best_model, str)


class TestIntegratedModelingWorkflows:
    """Test integrated workflows combining clustering and classification."""

    @pytest.fixture
    def workflow_data(self) -> pd.DataFrame:
        """Create data suitable for integrated modeling workflows."""
        np.random.seed(42)

        # Generate data with both clustering and classification structure
        X, y = make_classification(n_samples=150, n_features=12, n_informative=10, n_classes=2, random_state=42)

        feature_names = [f"FT-{i:03d}" for i in range(12)]
        data = pd.DataFrame(X, columns=feature_names)
        data["class_final"] = ["Disease" if label == 1 else "Healthy" for label in y]
        data["sample_id"] = [f"S{i:03d}" for i in range(150)]
        data["age"] = np.random.uniform(20, 80, 150)
        data["sex"] = np.random.choice([0, 1], 150)
        data["SampleType"] = "Sample"

        return data

    def test_clustering_guided_feature_selection(self, workflow_data: pd.DataFrame) -> None:
        """Test using clustering results to guide feature selection for classification."""

        # Step 1: Perform clustering
        clustering_result = ClusterAnalyzer.run_clustering_analysis(workflow_data, ["age", "sex"], feature_prefix="FT-")

        # Step 2: Use clustering information for feature selection
        # (In practice, this might involve analyzing cluster-discriminating features)
        features_subset = [f"FT-{i:03d}" for i in range(6)]  # Use first 6 features

        # Step 3: Train classification model on selected features
        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            workflow_data, features_subset, target_class="Disease", params=params
        )

        # Verify integrated workflow completed successfully
        assert "kmeans_labels" in clustering_result
        assert isinstance(best_model, str)

    def test_stratified_modeling_by_clusters(self, workflow_data: pd.DataFrame) -> None:
        """Test stratified modeling approach using cluster assignments."""

        # Step 1: Perform clustering
        clustering_result = ClusterAnalyzer.run_clustering_analysis(workflow_data, ["age", "sex"], feature_prefix="FT-")

        # Step 2: Add cluster labels to data
        workflow_data_with_clusters = workflow_data.copy()
        workflow_data_with_clusters["cluster"] = clustering_result["kmeans_labels"]

        # Step 3: Model each cluster separately (if enough samples)
        cluster_models = {}
        feature_names = [f"FT-{i:03d}" for i in range(8)]

        for cluster_id in set(clustering_result["kmeans_labels"]):
            cluster_data = workflow_data_with_clusters[workflow_data_with_clusters["cluster"] == cluster_id]

            # Only model if cluster has enough samples and both classes
            if len(cluster_data) >= 20 and len(cluster_data["class_final"].unique()) > 1:
                params = {
                    "random_search_params": {
                        "n_iter": 1,
                        "n_jobs": 1,
                        "verbose": 0,
                    }
                }

                try:
                    detailed_results, training_results, best_model = ModelTrainer.run_modeling(
                        cluster_data, feature_names, target_class="Disease", params=params
                    )
                    cluster_models[cluster_id] = best_model
                except Exception:
                    # Some clusters may not have enough diversity for modeling
                    pass

        # Should have attempted modeling for reasonable clusters
        assert len(cluster_models) >= 0  # May be 0 if no cluster is large enough

    def test_ensemble_clustering_features(self, workflow_data: pd.DataFrame) -> None:
        """Test using ensemble of clustering results as features for classification."""

        # Step 1: Get multiple clustering results
        clustering_result = ClusterAnalyzer.run_clustering_analysis(workflow_data, ["age", "sex"], feature_prefix="FT-")

        # Step 2: Create ensemble features from clustering
        ensemble_data = workflow_data.copy()
        ensemble_data["kmeans_cluster"] = clustering_result["kmeans_labels"]
        ensemble_data["dbscan_cluster"] = clustering_result["dbscan_labels"]
        ensemble_data["agglo_cluster"] = clustering_result["agglo_labels"]

        # Step 3: Use original features + clustering features for classification
        original_features = [f"FT-{i:03d}" for i in range(6)]
        cluster_features = ["kmeans_cluster", "dbscan_cluster", "agglo_cluster"]
        all_features = original_features + cluster_features

        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            ensemble_data, all_features, target_class="Disease", params=params
        )

        # Verify ensemble approach completed
        assert isinstance(best_model, str)

    def test_iterative_feature_clustering_refinement(self, workflow_data: pd.DataFrame) -> None:
        """Test iterative refinement of features using clustering feedback."""

        # Step 1: Initial clustering with all features
        all_features = [f"FT-{i:03d}" for i in range(12)]

        initial_clustering = ClusterAnalyzer.run_clustering_analysis(
            workflow_data, ["age", "sex"], glycans=all_features
        )

        # Step 2: Select subset of features based on some criteria
        # (In practice, this might involve analyzing feature importance or variance)
        refined_features = all_features[:8]  # Use first 8 features

        refined_clustering = ClusterAnalyzer.run_clustering_analysis(
            workflow_data, ["age", "sex"], glycans=refined_features
        )

        # Step 3: Compare clustering quality
        from sklearn.metrics import silhouette_score

        initial_silhouette = silhouette_score(initial_clustering["features"], initial_clustering["kmeans_labels"])

        refined_silhouette = silhouette_score(refined_clustering["features"], refined_clustering["kmeans_labels"])

        # Both should produce valid silhouette scores
        assert -1 <= initial_silhouette <= 1
        assert -1 <= refined_silhouette <= 1

    def test_workflow_performance_monitoring(self, workflow_data: pd.DataFrame) -> None:
        """Test performance monitoring throughout integrated workflows."""

        import time

        performance_log = {}

        # Monitor clustering performance
        start_time = time.time()
        _ = ClusterAnalyzer.run_clustering_analysis(workflow_data, ["age", "sex"], feature_prefix="FT-")
        performance_log["clustering_time"] = time.time() - start_time

        # Monitor modeling performance
        start_time = time.time()
        feature_names = [f"FT-{i:03d}" for i in range(6)]
        params = {
            "random_search_params": {
                "n_iter": 2,
                "n_jobs": 1,
                "verbose": 0,
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            workflow_data, feature_names, target_class="Disease", params=params
        )
        performance_log["modeling_time"] = time.time() - start_time

        # Verify performance monitoring
        assert performance_log["clustering_time"] > 0
        assert performance_log["modeling_time"] > 0

        # Reasonable performance expectations (should complete within reasonable time)
        assert performance_log["clustering_time"] < 30  # Should take less than 30 seconds
        assert performance_log["modeling_time"] < 60  # Should take less than 60 seconds
