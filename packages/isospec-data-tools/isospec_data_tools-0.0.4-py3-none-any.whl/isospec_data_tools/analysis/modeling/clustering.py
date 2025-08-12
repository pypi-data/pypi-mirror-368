"""Clustering algorithms and analysis utilities.

This module provides various clustering algorithms including K-means, DBSCAN,
and hierarchical clustering, along with cluster evaluation and analysis tools.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score

# Import custom exceptions
from ..utils.exceptions import ClusteringError

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[np.ndarray, pd.Series]
DataFrame = pd.DataFrame


class ClusterAnalyzer:
    """Handles various clustering algorithms with evaluation and analysis."""

    @staticmethod
    def run_kmeans(
        features: DataFrame,
        max_k: int = 10,
        min_k: int = 2,
        plot: bool = False,
        random_state: int = 42,
    ) -> tuple[np.ndarray, KMeans]:
        """
        Run KMeans clustering with automatic k selection using silhouette analysis.

        Args:
            features: Feature matrix for clustering
            max_k: Maximum number of clusters to try
            min_k: Minimum number of clusters to try
            plot: Whether to plot elbow and silhouette analysis
            random_state: Random state for reproducibility

        Returns:
            Tuple of (cluster_labels, fitted_kmeans_model)

        Raises:
            ClusteringError: If clustering fails or invalid parameters provided
        """
        if min_k >= max_k:
            raise ClusteringError("min_k must be less than max_k")

        if min_k < 2:
            raise ClusteringError("min_k must be at least 2")

        if features.empty:
            raise ClusteringError("Features dataframe cannot be empty")

        logger.info(f"Running K-means clustering with k range {min_k}-{max_k}")

        distortions = []
        silhouettes = []
        k_range = range(min_k, max_k + 1)

        for k in k_range:
            try:
                kmeans = KMeans(n_clusters=k, random_state=random_state)
                labels = kmeans.fit_predict(features)
                distortions.append(kmeans.inertia_)
                silhouettes.append(silhouette_score(features, labels))
                logger.debug(f"K={k}: inertia={kmeans.inertia_:.3f}, silhouette={silhouettes[-1]:.3f}")
            except Exception as e:
                logger.warning(f"KMeans failed for k={k}: {e}")
                distortions.append(np.inf)
                silhouettes.append(-1)

        if plot:
            ClusterAnalyzer._plot_kmeans_analysis(k_range, distortions, silhouettes)

        best_k_idx = np.argmax(silhouettes)
        best_k = k_range[best_k_idx]
        best_silhouette = silhouettes[best_k_idx]

        logger.info(f"Best k: {best_k}, silhouette score: {best_silhouette:.3f}")

        final_model = KMeans(n_clusters=best_k, random_state=random_state)
        final_labels = final_model.fit_predict(features)

        return final_labels, final_model

    @staticmethod
    def _plot_kmeans_analysis(k_range: range, distortions: list[float], silhouettes: list[float]) -> None:
        """Plot KMeans elbow and silhouette analysis."""
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        ax1.plot(k_range, distortions, "bo-", label="Inertia (Elbow)")
        ax2.plot(k_range, silhouettes, "go--", label="Silhouette")

        ax1.set_xlabel("k")
        ax1.set_ylabel("Inertia", color="b")
        ax2.set_ylabel("Silhouette Score", color="g")

        plt.title("KMeans Elbow & Silhouette Analysis")
        fig.tight_layout()
        plt.show()

    @staticmethod
    def run_dbscan(features: DataFrame, eps: float = 0.5, min_samples: int = 5) -> tuple[np.ndarray, DBSCAN]:
        """
        Run DBSCAN clustering.

        Args:
            features: Feature matrix for clustering
            eps: Maximum distance between points to be considered neighbors
            min_samples: Minimum number of samples in a neighborhood

        Returns:
            Tuple of (cluster_labels, fitted_dbscan_model)

        Raises:
            ClusteringError: If invalid parameters provided
        """
        if eps <= 0:
            raise ClusteringError("eps must be positive")

        if min_samples < 1:
            raise ClusteringError("min_samples must be at least 1")

        logger.info(f"Running DBSCAN clustering with eps={eps}, min_samples={min_samples}")

        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(features)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)

        logger.info(f"DBSCAN found {n_clusters} clusters with {n_noise} noise points")

        return labels, model

    @staticmethod
    def run_agglomerative_auto(
        features: DataFrame, min_clusters: int = 2, max_clusters: int = 10
    ) -> tuple[np.ndarray, AgglomerativeClustering]:
        """
        Run Agglomerative clustering with automatic cluster number selection.

        Args:
            features: Feature matrix for clustering
            min_clusters: Minimum number of clusters to try
            max_clusters: Maximum number of clusters to try

        Returns:
            Tuple of (cluster_labels, fitted_agglomerative_model)

        Raises:
            ClusteringError: If clustering fails or invalid parameters
        """
        if min_clusters >= max_clusters:
            raise ClusteringError("min_clusters must be less than max_clusters")

        logger.info(f"Running Agglomerative clustering with cluster range {min_clusters}-{max_clusters}")

        best_score = -1
        best_model: Optional[AgglomerativeClustering] = None
        best_labels: Optional[np.ndarray] = None
        best_k = None

        for k in range(min_clusters, max_clusters + 1):
            try:
                model = AgglomerativeClustering(n_clusters=k)
                labels = model.fit_predict(features)

                # Skip if all points are in same cluster or each point is its own cluster
                unique_labels = set(labels)
                if len(unique_labels) < 2 or len(unique_labels) == len(labels):
                    logger.debug(f"Skipping k={k}: degenerate clustering")
                    continue

                score = silhouette_score(features, labels)
                logger.debug(f"K={k}: silhouette={score:.3f}")

                if score > best_score:
                    best_score = score
                    best_model = model
                    best_labels = labels
                    best_k = k

            except Exception as e:
                logger.warning(f"Agglomerative clustering failed for k={k}: {e}")
                continue

        if best_model is None or best_labels is None:
            raise ClusteringError("No valid clustering found")

        logger.info(f"[Agglomerative] Best number of clusters: {best_k} (Silhouette = {best_score:.3f})")

        return best_labels, best_model

    @staticmethod
    def evaluate_clustering(features: DataFrame, labels: np.ndarray) -> float:
        """
        Evaluate clustering using silhouette score.

        Args:
            features: Feature matrix used for clustering
            labels: Cluster labels

        Returns:
            Silhouette score, or -1 if evaluation fails
        """
        try:
            if len(set(labels)) > 1:
                score = silhouette_score(features, labels)
                logger.debug(f"Clustering silhouette score: {score:.3f}")
                return float(score)
        except Exception as e:
            logger.warning(f"Clustering evaluation failed: {e}")
            return -1.0
        return -1.0

    @staticmethod
    def analyze_clusters(
        cluster_labels: np.ndarray,
        metadata: DataFrame,
        top_n: int = 5,
        imbalance_threshold: float = 0.3,
    ) -> tuple[DataFrame, list[str], list[str]]:
        """
        Analyze cluster characteristics and identify distinguishing features.

        Args:
            cluster_labels: Cluster assignments for each sample
            metadata: Metadata dataframe with sample information
            top_n: Number of top features to return
            imbalance_threshold: Threshold for categorical feature imbalance

        Returns:
            Tuple of (cluster_summary, top_numeric_features, top_categorical_features)
        """
        logger.info(f"Analyzing clusters for {len(np.unique(cluster_labels))} clusters")

        metadata_copy = metadata.copy()
        metadata_copy["Cluster"] = cluster_labels

        numeric_cols = metadata_copy.select_dtypes(include="number").columns.drop("Cluster", errors="ignore")
        categorical_cols = metadata_copy.select_dtypes(exclude="number").columns

        grouped = metadata_copy.groupby("Cluster")
        numeric_summary = grouped[numeric_cols].mean().round(2)

        categorical_summary = pd.DataFrame()
        max_imbalances = {}

        for col in categorical_cols:
            proportions = grouped[col].value_counts(normalize=True).unstack().fillna(0)
            proportions.columns = pd.Index([f"{col}={val}" for val in proportions.columns])
            max_diff = proportions.max() - proportions.min()
            max_imbalances[col] = max_diff.max()
            proportions = proportions.round(2)
            categorical_summary = pd.concat([categorical_summary, proportions], axis=1)

        summary = pd.concat([numeric_summary, categorical_summary], axis=1)

        # Get top numeric features by standard deviation
        top_numeric = numeric_summary.std().sort_values(ascending=False).head(top_n).index.tolist()

        # Get top categorical features by imbalance
        top_categorical = [col for col, diff in max_imbalances.items() if diff > imbalance_threshold]
        top_categorical = sorted(top_categorical, key=lambda x: max_imbalances[x], reverse=True)[:top_n]

        logger.info(
            f"Found {len(top_numeric)} distinguishing numeric features and {len(top_categorical)} categorical features"
        )

        return summary, top_numeric, top_categorical

    @staticmethod
    def run_clustering_analysis(
        data_matrix: DataFrame,
        selected_metadata: list[str],
        glycans: Optional[list[str]] = None,
        feature_prefix: str = "FT-",
    ) -> dict[str, Any]:
        """
        Run complete clustering analysis with multiple algorithms.

        Args:
            data_matrix: Complete data matrix with features and metadata
            selected_metadata: List of metadata column names
            glycans: List of glycan feature names (if None, uses feature_prefix)
            feature_prefix: Prefix to identify feature columns

        Returns:
            Dictionary containing clustering results and metadata

        Raises:
            ClusteringError: If no features found or clustering fails
        """
        logger.info("Starting comprehensive clustering analysis")

        if glycans is not None:
            sig_glycans_refined = glycans
        else:
            sig_glycans_refined = [col for col in data_matrix.columns if col.startswith(feature_prefix)]

        if not sig_glycans_refined:
            raise ClusteringError("No features found matching the criteria")

        logger.info(f"Using {len(sig_glycans_refined)} features for clustering")

        features = data_matrix[sig_glycans_refined]
        metadata = data_matrix[selected_metadata]

        # Run different clustering algorithms
        kmeans_labels, _ = ClusterAnalyzer.run_kmeans(features, min_k=3, max_k=10)
        dbscan_labels, _ = ClusterAnalyzer.run_dbscan(features, eps=0.5, min_samples=2)
        agglo_labels, _ = ClusterAnalyzer.run_agglomerative_auto(features, min_clusters=3, max_clusters=10)

        # Evaluate clustering quality
        kmeans_score = ClusterAnalyzer.evaluate_clustering(features, kmeans_labels)
        dbscan_score = ClusterAnalyzer.evaluate_clustering(features, dbscan_labels)
        agglo_score = ClusterAnalyzer.evaluate_clustering(features, agglo_labels)

        logger.info(f"KMeans Silhouette: {kmeans_score:.3f}")
        logger.info(f"DBSCAN Silhouette: {dbscan_score:.3f}")
        logger.info(f"Agglomerative Silhouette: {agglo_score:.3f}")

        return {
            "features": features,
            "metadata": metadata,
            "kmeans_labels": kmeans_labels,
            "dbscan_labels": dbscan_labels,
            "agglo_labels": agglo_labels,
            "kmeans_score": kmeans_score,
            "dbscan_score": dbscan_score,
            "agglo_score": agglo_score,
        }
