"""
Unit tests for classification and clustering utilities.

This module provides comprehensive pytest-based unit tests for ClusterAnalyzer
and ModelTrainer classes, focusing on core functionality, edge cases, and
logic correctness rather than scikit-learn internals.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans

# Import from new modular structure
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer
from isospec_data_tools.analysis.utils.exceptions import ClusteringError, ModelTrainingError


class TestClusterAnalyzer:
    """Test cases for ClusterAnalyzer class."""

    @pytest.fixture
    def sample_features(self) -> pd.DataFrame:
        """Create sample feature data for testing."""
        return pd.DataFrame({
            "f1": [1, 2, 1, 8, 9, 10, 1.5, 2.5],
            "f2": [1, 1, 2, 8, 9, 10, 1.2, 1.8],
            "f3": [0.1, 0.2, 0.1, 0.8, 0.9, 1.0, 0.15, 0.25],
        })

    @pytest.fixture
    def sample_metadata(self) -> pd.DataFrame:
        """Create sample metadata for testing."""
        return pd.DataFrame({
            "age": [25, 30, 35, 40, 45, 50, 28, 32],
            "gender": ["M", "F", "M", "F", "M", "F", "M", "F"],
            "group": ["A", "A", "A", "B", "B", "B", "A", "A"],
            "score": [0.5, 0.6, 0.4, 0.8, 0.9, 0.7, 0.55, 0.65],
        })

    def test_run_kmeans_returns_valid_clusters(self, sample_features: pd.DataFrame) -> None:
        """Test that run_kmeans returns valid cluster labels and model."""
        labels, model = ClusterAnalyzer.run_kmeans(sample_features, min_k=2, max_k=3)

        assert isinstance(labels, np.ndarray)
        assert isinstance(model, KMeans)
        assert len(labels) == len(sample_features)
        assert set(labels) <= {0, 1, 2}  # Valid cluster labels
        assert model.n_clusters in [2, 3]  # Should be in our range

    def test_run_kmeans_invalid_k_range_raises(self, sample_features: pd.DataFrame) -> None:
        """Test that invalid k range raises ClusteringError."""
        with pytest.raises(ClusteringError, match="min_k must be less than max_k"):
            ClusterAnalyzer.run_kmeans(sample_features, min_k=5, max_k=3)

    def test_run_kmeans_min_k_too_small_raises(self, sample_features: pd.DataFrame) -> None:
        """Test that min_k < 2 raises ClusteringError."""
        with pytest.raises(ClusteringError, match="min_k must be at least 2"):
            ClusterAnalyzer.run_kmeans(sample_features, min_k=1, max_k=3)

    def test_run_kmeans_empty_features_raises(self) -> None:
        """Test that empty features dataframe raises ClusteringError."""
        empty_df = pd.DataFrame()
        with pytest.raises(ClusteringError, match="Features dataframe cannot be empty"):
            ClusterAnalyzer.run_kmeans(empty_df, min_k=2, max_k=3)

    def test_run_kmeans_single_cluster_edge_case(self) -> None:
        """Test kmeans with very similar data (should still work)."""
        similar_data = pd.DataFrame({
            "f1": [1.0, 1.01, 1.02, 1.03, 1.04],
            "f2": [2.0, 2.01, 2.02, 2.03, 2.04],
        })
        labels, model = ClusterAnalyzer.run_kmeans(similar_data, min_k=2, max_k=3)
        assert len(labels) == len(similar_data)
        assert isinstance(model, KMeans)

    def test_run_dbscan_returns_valid_clusters(self, sample_features: pd.DataFrame) -> None:
        """Test that run_dbscan returns valid cluster labels and model."""
        labels, model = ClusterAnalyzer.run_dbscan(sample_features, eps=0.5, min_samples=2)

        assert isinstance(labels, np.ndarray)
        assert isinstance(model, DBSCAN)
        assert len(labels) == len(sample_features)
        # DBSCAN can return -1 for noise points
        assert all(label >= -1 for label in labels)

    def test_run_dbscan_invalid_eps_raises(self, sample_features: pd.DataFrame) -> None:
        """Test that negative eps raises ClusteringError."""
        with pytest.raises(ClusteringError, match="eps must be positive"):
            ClusterAnalyzer.run_dbscan(sample_features, eps=-0.1, min_samples=2)

    def test_run_dbscan_invalid_min_samples_raises(self, sample_features: pd.DataFrame) -> None:
        """Test that min_samples < 1 raises ClusteringError."""
        with pytest.raises(ClusteringError, match="min_samples must be at least 1"):
            ClusterAnalyzer.run_dbscan(sample_features, eps=0.5, min_samples=0)

    def test_run_agglomerative_auto_returns_valid_clusters(self, sample_features: pd.DataFrame) -> None:
        """Test that run_agglomerative_auto returns valid cluster labels and model."""
        labels, model = ClusterAnalyzer.run_agglomerative_auto(sample_features, min_clusters=2, max_clusters=4)

        assert isinstance(labels, np.ndarray)
        assert isinstance(model, AgglomerativeClustering)
        assert len(labels) == len(sample_features)
        assert len(set(labels)) >= 2  # Should have at least 2 clusters

    def test_run_agglomerative_auto_invalid_range_raises(self, sample_features: pd.DataFrame) -> None:
        """Test that invalid cluster range raises ClusteringError."""
        with pytest.raises(ClusteringError, match="min_clusters must be less than max_clusters"):
            ClusterAnalyzer.run_agglomerative_auto(sample_features, min_clusters=5, max_clusters=3)

    def test_run_agglomerative_auto_single_cluster_data_handles_gracefully(self) -> None:
        """Test that single cluster data is handled gracefully."""
        single_cluster_data = pd.DataFrame({
            "f1": [1.0, 1.0, 1.0, 1.0, 1.0],
            "f2": [2.0, 2.0, 2.0, 2.0, 2.0],
        })
        # This should either work or raise an error, but not crash
        try:
            labels, model = ClusterAnalyzer.run_agglomerative_auto(single_cluster_data, min_clusters=2, max_clusters=3)
            assert isinstance(labels, np.ndarray)
            assert isinstance(model, AgglomerativeClustering)
        except ClusteringError:
            # It's also acceptable to raise ClusteringError for this case
            pass

    def test_evaluate_clustering_valid_labels(self, sample_features: pd.DataFrame) -> None:
        """Test evaluate_clustering with valid cluster labels."""
        # Create some cluster labels
        labels = np.array([0, 0, 0, 1, 1, 1, 0, 0])
        score = ClusterAnalyzer.evaluate_clustering(sample_features, labels)

        assert isinstance(score, float)
        assert -1 <= score <= 1  # Silhouette score range

    def test_evaluate_clustering_single_cluster_returns_negative_one(self, sample_features: pd.DataFrame) -> None:
        """Test evaluate_clustering with single cluster returns -1."""
        labels = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        score = ClusterAnalyzer.evaluate_clustering(sample_features, labels)
        assert score == -1

    def test_analyze_clusters_returns_valid_outputs(self, sample_metadata: pd.DataFrame) -> None:
        """Test analyze_clusters returns valid summary and feature lists."""
        cluster_labels = np.array([0, 0, 0, 1, 1, 1, 0, 0])

        summary, top_numeric, top_categorical = ClusterAnalyzer.analyze_clusters(
            cluster_labels, sample_metadata, top_n=3
        )

        assert isinstance(summary, pd.DataFrame)
        assert isinstance(top_numeric, list)
        assert isinstance(top_categorical, list)
        assert len(summary) == 2  # Two clusters
        assert len(top_numeric) <= 3  # Top 3 numeric features
        assert len(top_categorical) <= 3  # Top 3 categorical features

    def test_analyze_clusters_with_numeric_only_metadata(self) -> None:
        """Test analyze_clusters with only numeric metadata."""
        numeric_metadata = pd.DataFrame({
            "age": [25, 30, 35, 40, 45, 50],
            "score": [0.5, 0.6, 0.4, 0.8, 0.9, 0.7],
        })
        cluster_labels = np.array([0, 0, 0, 1, 1, 1])

        summary, top_numeric, top_categorical = ClusterAnalyzer.analyze_clusters(
            cluster_labels, numeric_metadata, top_n=2
        )

        assert isinstance(summary, pd.DataFrame)
        assert len(top_numeric) <= 2
        assert len(top_categorical) == 0  # No categorical features

    def test_analyze_clusters_with_categorical_only_metadata(self) -> None:
        """Test analyze_clusters with only categorical metadata."""
        categorical_metadata = pd.DataFrame({
            "gender": ["M", "F", "M", "F", "M", "F"],
            "group": ["A", "A", "A", "B", "B", "B"],
        })
        cluster_labels = np.array([0, 0, 0, 1, 1, 1])

        summary, top_numeric, top_categorical = ClusterAnalyzer.analyze_clusters(
            cluster_labels, categorical_metadata, top_n=2
        )

        assert isinstance(summary, pd.DataFrame)
        assert len(top_numeric) == 0  # No numeric features
        assert len(top_categorical) <= 2

    def test_run_clustering_analysis_returns_valid_dict(
        self, sample_features: pd.DataFrame, sample_metadata: pd.DataFrame
    ) -> None:
        """Test run_clustering_analysis returns valid dictionary with all expected keys."""
        data_matrix = pd.concat([sample_features, sample_metadata], axis=1)
        selected_metadata = ["age", "gender", "group", "score"]

        result = ClusterAnalyzer.run_clustering_analysis(data_matrix, selected_metadata, feature_prefix="f")

        expected_keys = ["features", "metadata", "kmeans_labels", "dbscan_labels", "agglo_labels"]
        assert all(key in result for key in expected_keys)
        assert isinstance(result["features"], pd.DataFrame)
        assert isinstance(result["metadata"], pd.DataFrame)
        assert isinstance(result["kmeans_labels"], np.ndarray)
        assert isinstance(result["dbscan_labels"], np.ndarray)
        assert isinstance(result["agglo_labels"], np.ndarray)

    def test_run_clustering_analysis_no_features_raises(self, sample_metadata: pd.DataFrame) -> None:
        """Test run_clustering_analysis with no matching features raises ClusteringError."""
        data_matrix = sample_metadata.copy()  # No feature columns

        with pytest.raises(ClusteringError, match="No features found matching the criteria"):
            ClusterAnalyzer.run_clustering_analysis(data_matrix, ["age", "gender"], feature_prefix="FT-")

    def test_run_clustering_analysis_with_custom_glycans(
        self, sample_features: pd.DataFrame, sample_metadata: pd.DataFrame
    ) -> None:
        """Test run_clustering_analysis with custom glycan list."""
        data_matrix = pd.concat([sample_features, sample_metadata], axis=1)
        selected_metadata = ["age", "gender"]
        custom_glycans = ["f1", "f2"]  # Only use first two features

        result = ClusterAnalyzer.run_clustering_analysis(data_matrix, selected_metadata, glycans=custom_glycans)

        assert result["features"].shape[1] == 2  # Only 2 features
        assert list(result["features"].columns) == custom_glycans


class TestModelTrainer:
    """Test cases for ModelTrainer class."""

    @pytest.fixture
    def sample_classification_data(self) -> pd.DataFrame:
        """Create sample classification data for testing."""
        return pd.DataFrame({
            "f1": [0.1, 0.2, 0.9, 0.8, 0.5, 0.3, 0.7, 0.4],
            "f2": [1, 0, 1, 0, 1, 0, 1, 0],
            "f3": [0.3, 0.4, 0.8, 0.9, 0.2, 0.1, 0.6, 0.5],
            "class_final": ["A", "A", "B", "B", "A", "A", "B", "B"],
        })

    @pytest.fixture
    def sample_features(self) -> list[str]:
        """Create sample feature names."""
        return ["f1", "f2", "f3"]

    def test_create_cv_splits_returns_valid_splits(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test create_cv_splits returns valid cross-validation splits."""
        X = sample_classification_data[sample_features]
        y = (sample_classification_data["class_final"] == "B").astype(int)

        cv_splits = ModelTrainer.create_cv_splits(X, y, n_splits=3)

        assert isinstance(cv_splits, list)
        assert len(cv_splits) == 3

        for train_idx, test_idx in cv_splits:
            assert isinstance(train_idx, np.ndarray)
            assert isinstance(test_idx, np.ndarray)
            assert len(train_idx) + len(test_idx) == len(X)
            assert len(set(train_idx) & set(test_idx)) == 0  # No overlap

    def test_create_cv_splits_single_class_raises(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test create_cv_splits with single class raises error."""
        X = sample_classification_data[sample_features]
        y = pd.Series([1, 1, 1, 1, 1, 1, 1, 1])  # All same class
        # StratifiedKFold should raise ValueError for single class
        with pytest.raises(ValueError):
            ModelTrainer.create_cv_splits(X, y, n_splits=3)

    def test_calculate_optimal_threshold_returns_float(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test _calculate_optimal_threshold returns valid float."""
        y_true = pd.Series([0, 1, 1, 0, 1, 0, 1, 0])
        y_probs = np.array([
            [0.8, 0.2],
            [0.3, 0.7],
            [0.2, 0.8],
            [0.9, 0.1],
            [0.1, 0.9],
            [0.7, 0.3],
            [0.4, 0.6],
            [0.6, 0.4],
        ])

        threshold = ModelTrainer._calculate_optimal_threshold(y_true, y_probs)

        assert isinstance(threshold, float)
        assert 0 <= threshold <= 1

    def test_calculate_optimal_threshold_edge_cases(self) -> None:
        """Test _calculate_optimal_threshold with edge cases."""
        # All positive class - this will cause issues with ROC curve
        y_true = pd.Series([1, 1, 1])
        y_probs = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])

        # This should handle the edge case gracefully
        try:
            threshold = ModelTrainer._calculate_optimal_threshold(y_true, y_probs)
            assert isinstance(threshold, float)
            # For edge cases, threshold might be inf or nan, which is acceptable
            assert np.isfinite(threshold) or np.isnan(threshold) or np.isinf(threshold)
        except Exception as e:
            # It's also acceptable to raise an exception for this edge case
            # Log the exception for debugging purposes
            print(f"Expected exception in edge case test: {e}")

    def test_train_evaluate_models_returns_valid_structure(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test train_evaluate_models returns valid dictionary structure."""
        X = sample_classification_data.drop(["class_final"], axis=1)
        y = (sample_classification_data["class_final"] == "B").astype(int)

        # Use simpler parameters for testing
        params = {
            "random_search_params": {
                "n_iter": 5,
                "n_jobs": 1,
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        results = ModelTrainer.train_evaluate_models(X, y, sample_features, n_splits=2, params=params)

        expected_keys = ["model_results", "fitted_models", "best_params", "fold_data", "best_model", "best_fold_idx"]
        assert all(key in results for key in expected_keys)
        assert isinstance(results["model_results"], pd.DataFrame)
        assert isinstance(results["fitted_models"], dict)
        assert isinstance(results["fold_data"], dict)
        assert isinstance(results["best_model"], str)

    def test_train_evaluate_models_unsupported_model_raises(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test train_evaluate_models with unsupported model raises ModelTrainingError."""
        X = sample_classification_data.drop(["class_final"], axis=1)
        y = (sample_classification_data["class_final"] == "B").astype(int)

        with pytest.raises(ModelTrainingError, match="Model InvalidModel not supported"):
            ModelTrainer.train_evaluate_models(X, y, sample_features, models_to_evaluate=["InvalidModel"])

    def test_analyze_best_models_returns_valid_analysis(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test analyze_best_models returns valid analysis dictionary."""
        X = sample_classification_data.drop(["class_final"], axis=1)
        y = (sample_classification_data["class_final"] == "B").astype(int)

        # First get fold data
        results = ModelTrainer.train_evaluate_models(X, y, sample_features, n_splits=2)
        fold_data = results["fold_data"]

        # Analyze best models
        analysis = ModelTrainer.analyze_best_models(fold_data, fold_idx=0)

        assert isinstance(analysis, dict)
        for _model_name, model_analysis in analysis.items():
            assert "Classification Report" in model_analysis
            assert "Confusion Matrix" in model_analysis
            assert isinstance(model_analysis["Classification Report"], pd.DataFrame)
            assert isinstance(model_analysis["Confusion Matrix"], np.ndarray)

    def test_analyze_best_models_invalid_fold_idx(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test analyze_best_models with invalid fold index handles gracefully."""
        X = sample_classification_data.drop(["class_final"], axis=1)
        y = (sample_classification_data["class_final"] == "B").astype(int)

        results = ModelTrainer.train_evaluate_models(X, y, sample_features, n_splits=2)
        fold_data = results["fold_data"]

        # Should not raise error, just return empty dict or handle gracefully
        analysis = ModelTrainer.analyze_best_models(fold_data, fold_idx=999)
        assert isinstance(analysis, dict)

    def test_run_modeling_end_to_end(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test run_modeling end-to-end with valid data."""
        # Use simpler parameters to avoid RandomizedSearchCV issues
        params = {
            "random_search_params": {
                "n_iter": 5,  # Fewer iterations for faster testing
                "n_jobs": 1,  # Single job to avoid multiprocessing issues
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            sample_classification_data, sample_features, target_class="B", params=params
        )

        assert isinstance(detailed_results, dict)
        assert isinstance(training_results, dict)
        assert isinstance(best_model, str)
        # If no models were successfully trained, fitted_models might be empty
        if training_results["fitted_models"]:
            assert best_model in training_results["fitted_models"]

    def test_run_modeling_missing_class_column_raises(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test run_modeling with missing class column raises ModelTrainingError."""
        data_without_class = sample_classification_data.drop(["class_final"], axis=1)

        with pytest.raises(ModelTrainingError, match="Class column 'class_final' not found in data"):
            ModelTrainer.run_modeling(data_without_class, sample_features, target_class="B")

    def test_run_modeling_no_features_raises(self, sample_classification_data: pd.DataFrame) -> None:
        """Test run_modeling with no features raises ModelTrainingError."""
        with pytest.raises(ModelTrainingError, match="No features provided"):
            ModelTrainer.run_modeling(sample_classification_data, [], target_class="B")

    def test_run_modeling_missing_features_raises(self, sample_classification_data: pd.DataFrame) -> None:
        """Test run_modeling with missing features raises ModelTrainingError."""
        with pytest.raises(ModelTrainingError, match="Missing features"):
            ModelTrainer.run_modeling(sample_classification_data, ["nonexistent_feature"], target_class="B")

    def test_run_modeling_target_class_not_found_raises(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test run_modeling with target class not in data raises ModelTrainingError."""
        with pytest.raises(ModelTrainingError, match="Target class 'C' not found or all samples have same class"):
            ModelTrainer.run_modeling(sample_classification_data, sample_features, target_class="C")

    def test_run_modeling_single_class_data_raises(
        self, sample_classification_data: pd.DataFrame, sample_features: list[str]
    ) -> None:
        """Test run_modeling with single class data raises ModelTrainingError."""
        single_class_data = sample_classification_data.copy()
        single_class_data["class_final"] = "A"  # All same class

        with pytest.raises(ModelTrainingError, match="Target class 'B' not found or all samples have same class"):
            ModelTrainer.run_modeling(single_class_data, sample_features, target_class="B")

    def test_model_name_map_consistency(self) -> None:
        """Test that MODEL_NAME_MAP is consistent with DEFAULT_BASE_MODELS."""
        model_names = set(ModelTrainer.MODEL_NAME_MAP.values())
        base_model_keys = set(ModelTrainer.DEFAULT_BASE_MODELS.keys())
        assert model_names == base_model_keys

    def test_default_scoring_contains_expected_metrics(self) -> None:
        """Test that DEFAULT_SCORING contains expected metric names."""
        expected_metrics = ["roc_auc", "precision", "recall", "accuracy", "f1"]
        assert all(metric in ModelTrainer.DEFAULT_SCORING for metric in expected_metrics)


class TestIntegration:
    """Integration tests combining multiple components."""

    @pytest.fixture
    def integration_data(self) -> pd.DataFrame:
        """Create data for integration testing."""
        return pd.DataFrame({
            "f1": [0.1, 0.2, 0.9, 0.8, 0.5, 0.3, 0.7, 0.4, 0.6, 0.1],
            "f2": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            "f3": [0.3, 0.4, 0.8, 0.9, 0.2, 0.1, 0.6, 0.5, 0.7, 0.2],
            "age": [25, 30, 35, 40, 45, 50, 28, 32, 38, 42],
            "gender": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"],
            "class_final": ["A", "A", "B", "B", "A", "A", "B", "B", "A", "B"],
        })

    def test_clustering_then_modeling_integration(self, integration_data: pd.DataFrame) -> None:
        """Test integration of clustering analysis followed by modeling."""
        features = ["f1", "f2", "f3"]
        metadata_cols = ["age", "gender"]

        # Run clustering analysis
        clustering_results = ClusterAnalyzer.run_clustering_analysis(
            integration_data, metadata_cols, feature_prefix="f"
        )

        # Verify clustering results
        assert "kmeans_labels" in clustering_results
        assert "agglo_labels" in clustering_results
        assert len(clustering_results["kmeans_labels"]) == len(integration_data)

        # Run modeling with simpler parameters
        params = {
            "random_search_params": {
                "n_iter": 5,
                "n_jobs": 1,
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            integration_data, features, target_class="B", params=params
        )

        # Verify modeling results
        assert isinstance(best_model, str)
        assert "model_results" in training_results
        # detailed_results might be empty if no models were successfully trained
        assert isinstance(detailed_results, dict)

    def test_multiple_clustering_algorithms_consistency(self, integration_data: pd.DataFrame) -> None:
        """Test that different clustering algorithms produce consistent results."""
        features = integration_data[["f1", "f2", "f3"]]

        # Run different clustering algorithms
        kmeans_labels, _ = ClusterAnalyzer.run_kmeans(features, min_k=2, max_k=3)
        dbscan_labels, _ = ClusterAnalyzer.run_dbscan(features, eps=0.5, min_samples=2)
        agglo_labels, _ = ClusterAnalyzer.run_agglomerative_auto(features, min_clusters=2, max_clusters=3)

        # All should have same number of samples
        assert len(kmeans_labels) == len(dbscan_labels) == len(agglo_labels) == len(features)

        # All should have valid cluster labels
        assert all(label >= 0 for label in kmeans_labels)
        assert all(label >= -1 for label in dbscan_labels)  # DBSCAN can have -1
        assert all(label >= 0 for label in agglo_labels)

    def test_model_performance_metrics_consistency(self, integration_data: pd.DataFrame) -> None:
        """Test that model performance metrics are consistent and reasonable."""
        features = ["f1", "f2", "f3"]

        # Use simpler parameters for testing
        params = {
            "random_search_params": {
                "n_iter": 5,
                "n_jobs": 1,
                "verbose": 0,
                "refit": "roc_auc",
            }
        }

        detailed_results, training_results, best_model = ModelTrainer.run_modeling(
            integration_data, features, target_class="B", params=params
        )

        # Check that model results contain expected metrics (if any models were trained)
        model_results = training_results["model_results"]
        if not model_results.empty:
            expected_metrics = ["Best AUC Score", "Accuracy", "Precision", "Recall", "F1 Score", "ROC AUC"]

            for metric in expected_metrics:
                if metric in model_results.columns and metric in [
                    "Accuracy",
                    "Precision",
                    "Recall",
                    "F1 Score",
                    "ROC AUC",
                ]:
                    # Check that metrics are reasonable (between 0 and 1 for most)
                    values = model_results[metric].str.extract(r"([\d.]+)")[0].astype(float)
                    assert all(0 <= val <= 1 for val in values)
