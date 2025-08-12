"""
Clustering plotting utilities for data analysis and visualization.

This module provides comprehensive plotting functions for clustering analysis,
including dendrograms, PCA plots, heatmaps, and cluster metadata visualization.
"""

from typing import Optional, Union

import matplotlib.figure as mpl_figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA

from isospec_data_tools.io_utils import save_fig


class ClusteringPlotter:
    """
    Plotting functions for clustering analysis and visualization.

    This class provides static methods for creating various clustering plots
    including dendrograms, PCA visualizations, heatmaps, and cluster metadata analysis.
    """

    @staticmethod
    def plot_dendrogram(
        features: Union[np.ndarray, pd.DataFrame],
        labels: Union[np.ndarray, list[int]],
        method: str = "ward",
        save_path: Optional[str] = None,
    ) -> mpl_figure.Figure:
        """
        Create a dendrogram plot with cluster labels.

        Parameters:
        -----------
        features : Union[np.ndarray, pd.DataFrame]
            Feature matrix used for clustering.
        labels : Union[np.ndarray, List[int]]
            Cluster labels for each sample.
        method : str
            Linkage method for hierarchical clustering (default: 'ward').
        save_path : Optional[str]
            Path to save the figure. If None, figure is not saved.

        Returns:
        --------
        matplotlib.figure.Figure
            Figure containing the dendrogram plot.
        """
        if isinstance(features, pd.DataFrame):
            features = features.values

        if isinstance(labels, list):
            labels = np.array(labels)

        # Perform hierarchical clustering
        linked = linkage(features, method=method)

        # Get unique clusters and create color palette
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels)
        palette = sns.color_palette("tab10", n_clusters)

        # Create label colors mapping
        [palette[label] for label in labels]

        # Prepare labels for plotting: C0, C1, ...
        leaf_labels = [f"C{label}" for label in labels]

        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot dendrogram
        dendrogram(linked, labels=leaf_labels, leaf_rotation=90, leaf_font_size=10, color_threshold=None)

        # Recolor the leaf labels according to cluster assignments
        xlbls = ax.get_xmajorticklabels()
        for _i, lbl in enumerate(xlbls):
            cluster_id = int(lbl.get_text()[1:])  # Extract number from "C2"
            lbl.set_color(palette[cluster_id])

        # Add legend with sample counts
        cluster_counts = np.bincount(labels)
        legend_labels = [f"C{i} (n={count})" for i, count in enumerate(cluster_counts)]
        handles = [
            plt.Line2D(
                [0], [0], marker="o", color="w", label=legend_labels[i], markerfacecolor=palette[i], markersize=10
            )
            for i in range(n_clusters)
        ]

        ax.legend(handles=handles, title="Clusters", loc="upper right")
        ax.set_title("Dendrogram with Cluster Labels")
        ax.set_xlabel("Samples (Colored by Clusters)")
        ax.set_ylabel("Distance")

        plt.tight_layout()

        if save_path:
            save_fig(fig, name="dendrogram", path=save_path)

        plt.close(fig)
        return fig

    @staticmethod
    def plot_cluster_metadata(
        metadata: pd.DataFrame,
        cluster_col: str = "Cluster",
        meta_cols: Optional[list[str]] = None,
        relative: bool = False,
        save_path: Optional[str] = None,
    ) -> list[mpl_figure.Figure]:
        """
        Plot metadata distributions by cluster.

        Parameters:
        -----------
        metadata : pd.DataFrame
            DataFrame containing metadata and cluster assignments.
        cluster_col : str
            Column name containing cluster assignments (default: 'Cluster').
        meta_cols : Optional[List[str]]
            List of metadata columns to plot. If None, uses all columns except cluster_col.
        relative : bool
            Whether to plot relative frequencies for categorical variables (default: False).
        save_path : Optional[str]
            Path to save the figures. If None, figures are not saved.

        Returns:
        --------
        List[matplotlib.figure.Figure]
            List of figures containing cluster metadata plots.
        """
        if cluster_col not in metadata.columns:
            raise ValueError(f"Cluster column '{cluster_col}' not found in metadata")

        if meta_cols is None:
            meta_cols = [col for col in metadata.columns if col != cluster_col]

        if not meta_cols:
            raise ValueError("No metadata columns specified for plotting")

        # Prepare cluster labels with counts
        cluster_counts = metadata[cluster_col].value_counts().sort_index()
        cluster_labels = {cl: f"{cl} (n={count})" for cl, count in cluster_counts.items()}
        metadata_copy = metadata.copy()
        metadata_copy["_cluster_label"] = metadata_copy[cluster_col].map(cluster_labels)

        figures = []

        for meta_col in meta_cols:
            if meta_col not in metadata_copy.columns:
                print(f"Warning: Column '{meta_col}' not found in metadata, skipping...")
                continue

            fig, ax = plt.subplots(figsize=(8, 6))

            if metadata_copy[meta_col].dtype == "object" or metadata_copy[meta_col].dtype.name == "category":
                if relative:
                    # Compute relative frequencies
                    rel_df = (
                        metadata_copy.groupby("_cluster_label")[meta_col]
                        .value_counts(normalize=True)
                        .rename("proportion")
                        .reset_index()
                    )
                    sns.barplot(data=rel_df, x="_cluster_label", y="proportion", hue=meta_col, ax=ax)
                    ax.set_ylabel("Proportion")
                else:
                    sns.countplot(data=metadata_copy, x="_cluster_label", hue=meta_col, ax=ax)
                    ax.set_ylabel("Count")
                ax.set_title(f"{meta_col} distribution by cluster")
                ax.set_xlabel("Cluster")
            else:
                sns.boxplot(data=metadata_copy, x="_cluster_label", y=meta_col, ax=ax)
                ax.set_title(f"{meta_col} distribution by cluster")
                ax.set_xlabel("Cluster")

            ax.tick_params(axis="x", rotation=45)
            plt.tight_layout()

            figures.append(fig)

            if save_path:
                save_fig(fig, name=f"cluster_metadata_{meta_col}", path=save_path)

            plt.close(fig)

        return figures

    @staticmethod
    def plot_clusters(
        features: Union[np.ndarray, pd.DataFrame],
        metadata: pd.DataFrame,
        agglo_labels: Union[np.ndarray, list[int]],
        top_categorical_pca: Optional[list[str]] = None,
        save_path: Optional[str] = None,
    ) -> list[mpl_figure.Figure]:
        """
        Analyze cluster results and create visualization plots.

        Parameters:
        -----------
        features : Union[np.ndarray, pd.DataFrame]
            Feature matrix used for clustering.
        metadata : pd.DataFrame
            Metadata for the samples.
        agglo_labels : Union[np.ndarray, List[int]]
            Cluster labels from agglomerative clustering.
        top_categorical_pca : Optional[List[str]]
            List of categorical columns to use for PCA visualization (default: None).
        save_path : Optional[str]
            Path to save the figures. If None, figures are not saved.

        Returns:
        --------
        List[matplotlib.figure.Figure]
            List of figures containing cluster analysis plots.
        """
        if top_categorical_pca is None:
            top_categorical_pca = ["copd"]

        figures = []

        # Create dendrogram
        dendro_fig = ClusteringPlotter.plot_dendrogram(features, agglo_labels)
        figures.append(dendro_fig)

        # Create composite hue for PCA if multiple categorical variables
        if len(top_categorical_pca) > 1:
            composite_hue_name = "_".join(top_categorical_pca)
            metadata_with_hue = metadata.assign(**{
                composite_hue_name: metadata[top_categorical_pca].astype(str).agg("|".join, axis=1)
            })
        else:
            metadata_with_hue = metadata

        # Plot cluster metadata
        metadata_with_clusters = metadata_with_hue.assign(Cluster=agglo_labels)
        cluster_plots = ClusteringPlotter.plot_cluster_metadata(
            metadata_with_clusters, cluster_col="Cluster", meta_cols=metadata.columns.tolist(), relative=True
        )
        figures.extend(cluster_plots)

        if save_path:
            for i, fig in enumerate(figures):
                save_fig(fig, name=f"cluster_plots_{i}", path=save_path)

        return figures

    @staticmethod
    def plot_pca_with_overlays(
        data: pd.DataFrame,
        feature_cols: Optional[list[str]] = None,
        hue_column: str = "SampleType",
        pca_components: int = 2,
        figsize: tuple[int, int] = (10, 8),
        xlim: tuple[float, float] = (-5, 5),
        ylim: tuple[float, float] = (-2, 2),
        palette: Optional[dict[str, str]] = None,
        save_path: Optional[str] = None,
    ) -> tuple[mpl_figure.Figure, PCA]:
        """
        Plot PCA with seaborn, with customizable hue and overlays.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing features and hue column.
        feature_cols : Optional[List[str]]
            List of feature columns to use. If None, uses columns starting with 'FT-'.
        hue_column : str
            Column name to use for coloring the points (default: 'SampleType').
        pca_components : int
            Number of PCA components to compute (default: 2).
        figsize : Tuple[int, int]
            Figure size for the plot (default: (10, 8)).
        xlim : Tuple[float, float]
            X-axis limits (min, max) (default: (-5, 5)).
        ylim : Tuple[float, float]
            Y-axis limits (min, max) (default: (-2, 2)).
        palette : Optional[Dict[str, str]]
            Custom color palette for hue categories (default: None).
        save_path : Optional[str]
            Path to save the figure. If None, figure is not saved.

        Returns:
        --------
        Tuple[matplotlib.figure.Figure, sklearn.decomposition.PCA]
            The figure object and fitted PCA object.

        Raises:
        -------
        ValueError
            If hue_column is not found in data or no valid features are found.
        """
        if hue_column not in data.columns:
            raise ValueError(f"Hue column '{hue_column}' not found in data")

        # Select features
        if feature_cols is None:
            feature_cols = [col for col in data.columns if col.startswith("FT-")]

        if not feature_cols:
            raise ValueError(
                "No feature columns found. Please specify feature_cols or ensure data contains 'FT-' prefixed columns."
            )

        X = data[feature_cols]

        # Perform PCA
        pca = PCA(n_components=pca_components)
        pca_result = pca.fit_transform(X)

        # Create DataFrame with PCA results
        pca_df = pd.DataFrame(data=pca_result, columns=[f"PC{i + 1}" for i in range(pca_components)], index=data.index)
        pca_df[hue_column] = data[hue_column]

        # Calculate variance explained
        var_explained = pca.explained_variance_ratio_ * 100

        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)

        # Base scatter plot
        sns.scatterplot(data=pca_df, x="PC1", y="PC2", hue=hue_column, style=hue_column, s=100, palette=palette, ax=ax)

        # Customize the plot
        ax.set_xlabel(f"PC1 ({var_explained[0]:.1f}%)")
        ax.set_ylabel(f"PC2 ({var_explained[1]:.1f}%)")
        ax.set_title(f"PCA Plot colored by {hue_column}")

        # Set axis limits
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)

        # Add legend
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles, labels=labels, title=hue_column, bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()

        if save_path:
            save_fig(fig, name="pca_with_overlays", path=save_path)

        plt.close(fig)
        return fig, pca

    @staticmethod
    def create_glycan_heatmap(
        data: pd.DataFrame,
        glycans: Optional[list[str]] = None,
        feature_prefix: str = "FT-",
        group_column: str = "copd",
        group_colors: Optional[dict[str, str]] = None,
        figsize: tuple[int, int] = (15, 10),
        cmap: str = "RdYlBu_r",
        title: str = "Glycan Features Clustered by COPD Status",
        row_cluster: bool = False,
        feature_mapping: Optional[dict[str, str]] = None,
        path: Optional[str] = None,
    ) -> Optional[mpl_figure.Figure]:
        """
        Create a heatmap of glycan features clustered by a grouping variable.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing the feature data and grouping column.
        glycans : Optional[List[str]]
            List of specific glycan features to include. If None, uses feature_prefix
            to identify features (default: None).
        feature_prefix : str
            Prefix to identify feature columns if glycans not provided (default: 'FT-').
        group_column : str
            Name of column containing grouping variable (default: 'copd').
        group_colors : Optional[Dict[str, str]]
            Mapping of group values to colors (default: None, uses default colors).
        figsize : Tuple[int, int]
            Figure size as (width, height) (default: (15, 10)).
        cmap : str
            Colormap to use for heatmap (default: 'RdYlBu_r').
        title : str
            Title for the plot (default: 'Glycan Features Clustered by COPD Status').
        row_cluster : bool
            Whether to perform row clustering (default: False).
        feature_mapping : Optional[Dict[str, str]]
            Dictionary mapping feature IDs to display names (e.g. IUPAC names).
        path : Optional[str]
            Path to save the figure. If None, figure is not saved.

        Returns:
        --------
        Optional[matplotlib.figure.Figure]
            The generated heatmap figure, or None if no valid data.
        """
        if group_colors is None:
            group_colors = {"Yes": "red", "No": "blue"}

        # Select feature columns
        if glycans is not None:
            feature_cols = [col for col in glycans if col in data.columns]
        else:
            feature_cols = [col for col in data.columns if col.startswith(feature_prefix)]

        if not feature_cols:
            print("No feature columns found matching the specified criteria")
            return None

        # Remove any columns with infinite or NaN values
        data_for_clustering = data[feature_cols].copy()
        data_for_clustering = data_for_clustering.replace([np.inf, -np.inf], np.nan)
        data_for_clustering = data_for_clustering.dropna(axis=1)

        if len(data_for_clustering.columns) == 0:
            print("No valid data columns remaining after removing infinite/NaN values")
            return None

        try:
            # Sort rows by group to keep them together
            sorted_data = data_for_clustering.copy()
            sorted_data["group"] = data[group_column]
            sorted_data = sorted_data.sort_values("group")
            row_colors = pd.Series(sorted_data["group"]).map(group_colors)
            sorted_data = sorted_data.drop("group", axis=1)

            # Rename columns if feature mapping is provided
            if feature_mapping is not None:
                sorted_data.columns = pd.Index([feature_mapping.get(col, col) for col in sorted_data.columns])

            # Create clustermap
            clustermap = sns.clustermap(
                sorted_data,
                method="complete",
                row_cluster=row_cluster,
                col_cluster=True,
                row_colors=row_colors,
                cmap=cmap,
                z_score=0,
                xticklabels=True,
                yticklabels=False,
                figsize=figsize,
            )

            # Rotate x-axis labels for better readability
            plt.setp(clustermap.ax_heatmap.get_xticklabels(), rotation=45, ha="right")

            # Create legend handles
            legend_elements = [Patch(facecolor=color, label=group) for group, color in group_colors.items()]

            # Add legend to the figure
            clustermap.ax_heatmap.legend(
                handles=legend_elements, title=group_column, bbox_to_anchor=(1.3, 1), loc="upper right"
            )
            clustermap.fig.suptitle(title, y=1.02)

            if path:
                save_fig(clustermap.fig, name="glycan_heatmap", path=path)

            return clustermap.fig

        except Exception as e:
            print(f"Error creating clustermap: {e!s}")
            # Create a simple heatmap without clustering as fallback
            fig, ax = plt.subplots(figsize=figsize)
            sns.heatmap(sorted_data, cmap=cmap, xticklabels=True, yticklabels=False, ax=ax)
            ax.set_title(f"{title} (Unclustered)")

            if path:
                save_fig(fig, name="glycan_heatmap_unclustered", path=path)

            plt.close(fig)
            return fig
