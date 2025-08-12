"""
Modular plotting classes for preprocessing pipeline visualization.

This module provides comprehensive visualization capabilities for data preprocessing
operations, including missing data analysis, imputation impact assessment,
CV improvement tracking, and transformation pipeline visualization.

Classes adapted for isospec-data-tools integration while maintaining external API compatibility.
"""

# Standard library imports
from collections.abc import Callable
from typing import Any, Optional, Union

# Third-party imports
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Local package imports - Core configuration
from isospec_data_tools.analysis.core.project_config import (
    DataStructureConfig,
    NormalizationConfig,
    PlottingConfig,
    StatisticalConfig,
    TransformationPipelineConfig,
    VisualizationConfig,
)

# Local package imports - Utilities
from isospec_data_tools.io_utils import save_fig

# Local package imports - Analysis components (to avoid code duplication)
from isospec_data_tools.visualization.analysis.confounder_plots import PlotHelper, StatisticalAnalyzer
from isospec_data_tools.visualization.analysis.method_plot import CVAnalyzer, PlotStyler


# Simple plugin registry implementation for extensibility
class PluginRegistry:
    """Simple plugin registry for feature analyzer extensions."""

    def __init__(self) -> None:
        self.plugins: dict[str, Any] = {}

    def register(self, name: str, plugin: Any) -> None:
        """Register a plugin."""
        self.plugins[name] = plugin

    def get(self, name: str, default: Any = None) -> Any:
        """Get a plugin by name."""
        return self.plugins.get(name, default)


# Global plugin registry instance
PLUGIN_REGISTRY = PluginRegistry()


# =============================================================================
# MAIN PLOTTING CLASSES - API compatible, internally using isospec utilities
# =============================================================================


class PreprocessingPlotter:
    """
    Main plotting class for preprocessing pipeline visualization.

    This class provides comprehensive visualization capabilities for data preprocessing
    operations, including missing data analysis, imputation impact assessment, and
    preprocessing pipeline overview plots.

    Maintains original API for external notebook compatibility while using
    existing isospec-data-tools utilities internally to avoid duplication.

    Examples:
        Basic usage for missing data visualization:

        >>> import pandas as pd
        >>> from isospec_data_tools.visualization.analysis import PreprocessingPlotter
        >>>
        >>> # Initialize plotter
        >>> plotter = PreprocessingPlotter()
        >>>
        >>> # Plot missing data analysis
        >>> fig = plotter.plot_missing_data_analysis(
        ...     data=metabolomics_data,
        ...     feature_columns=["FT001", "FT002", "FT003"],
        ...     save_path="missing_data_analysis.png"
        ... )

        With custom configuration:

        >>> from isospec_data_tools.visualization.analysis import (
        ...     DataStructureConfig, StatisticalConfig, VisualizationConfig
        ... )
        >>>
        >>> # Configure data structure
        >>> data_config = DataStructureConfig(
        ...     sample_column="SampleID",
        ...     sample_type_column="SampleType",
        ...     qc_identifier=["QC", "EQC"]
        ... )
        >>>
        >>> # Configure statistical thresholds
        >>> stats_config = StatisticalConfig(
        ...     cv_threshold=30.0,
        ...     percentile_thresholds=(25.0, 75.0)
        ... )
        >>>
        >>> # Initialize with custom configs
        >>> plotter = PreprocessingPlotter(
        ...     data_config=data_config,
        ...     stats_config=stats_config
        ... )

        Imputation impact visualization:

        >>> # Compare before and after imputation
        >>> fig = plotter.plot_imputation_cv_impact(
        ...     data_before=raw_data,
        ...     data_after=imputed_data,
        ...     glycan_columns=feature_columns,
        ...     save_path="imputation_impact.png"
        ... )
    """

    def __init__(
        self,
        project_config: Optional[Any] = None,
        data_config: Optional[DataStructureConfig] = None,
        stats_config: Optional[StatisticalConfig] = None,
        viz_config: Optional[VisualizationConfig] = None,
        plugin_registry: Optional[Any] = None,
    ):
        """
        Initialize preprocessing plotter.
        Maintains original constructor signature for user compatibility.
        """
        self.project_config = project_config
        self.data_config = data_config or DataStructureConfig()
        self.stats_config = stats_config or StatisticalConfig()
        self.viz_config = viz_config or VisualizationConfig()

        # Use existing isospec-data-tools utilities internally
        self._cv_analyzer = CVAnalyzer()
        self._stat_analyzer = StatisticalAnalyzer()

        # Setup styling using existing PlotStyler
        PlotStyler.setup_seaborn_style()

    def _get_figure_layout(self, plot_type: str) -> tuple[int, int]:
        """Get figure layout for plot type."""
        return self.viz_config.figure_layouts.get(plot_type, (12, 8))

    def _get_color_scheme(self, scheme_name: str) -> dict[str, str]:
        """Get color scheme by name."""
        return self.viz_config.color_schemes.get(scheme_name, {})

    def _get_histogram_bins(self, hist_type: str) -> int:
        """Get histogram bin count for type."""
        return self.stats_config.histogram_bins.get(hist_type, 20)

    def plot_missing_data_analysis(
        self,
        data_matrix: pd.DataFrame,
        feature_columns: list[str],
        sample_column: Optional[str] = None,
        qc_identifier: Optional[Union[str, Callable]] = None,
        max_samples_display: int = 80,
        max_features_display: int = 40,
        top_missing_count: int = 10,
        feature_name_truncate: int = 15,
        save_path: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Create comprehensive missing data visualization.

        Maintains original API while using existing isospec utilities internally.
        """
        # Use configuration defaults if not provided
        sample_col = sample_column or self.data_config.sample_column

        # Calculate missing data statistics
        feature_data = data_matrix[feature_columns]
        missing_counts = feature_data.isnull().sum()
        total_missing = missing_counts.sum()

        # Get layout configuration
        fig_size = self._get_figure_layout("missing_data")

        if total_missing <= self.stats_config.missing_data_threshold:
            # Create simple "no missing data" visualization
            fig, ax = plt.subplots(1, 1, figsize=fig_size)
            ax.text(
                0.5,
                0.5,
                f"No Missing Data Found\n{len(feature_columns)} features complete",
                ha="center",
                va="center",
                fontsize=self.viz_config.style_config["title_fontsize"] + 4,
                bbox={"boxstyle": "round", "facecolor": "lightgreen", "alpha": 0.8},
            )
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            ax.set_title(
                "Missing Data Analysis", fontsize=self.viz_config.style_config["title_fontsize"], fontweight="bold"
            )
            return fig

        # Use existing PlotHelper for subplot creation instead of custom implementation
        fig, axes = PlotHelper.create_subplot_grid(6, plots_per_row=3)

        # 1. Missing data heatmap
        missing_matrix = feature_data.isnull().astype(int)
        if sample_col in data_matrix.columns:
            sample_order = data_matrix.sort_values(sample_col).index
            missing_matrix_sorted = missing_matrix.loc[sample_order]
        else:
            missing_matrix_sorted = missing_matrix

        subset_samples = min(max_samples_display, len(data_matrix))
        subset_features = min(max_features_display, len(feature_columns))

        im = axes[0].imshow(missing_matrix_sorted.iloc[:subset_samples, :subset_features].T, cmap="Reds", aspect="auto")
        axes[0].set_title(f"Missing Data Pattern\n(Sorted by {sample_col})", fontweight="bold")
        axes[0].set_xlabel("Samples")
        axes[0].set_ylabel("Features")
        plt.colorbar(im, ax=axes[0], label="Missing (1) vs Present (0)")

        # 2. Missing data per sample
        missing_per_sample = missing_matrix.sum(axis=1)
        bins = self._get_histogram_bins("default")
        axes[1].hist(
            missing_per_sample,
            bins=bins,
            alpha=self.viz_config.style_config["alpha"],
            color="skyblue",
            edgecolor="black",
        )
        axes[1].set_xlabel("Missing Features per Sample")
        axes[1].set_ylabel("Frequency")
        axes[1].set_title("Missing Data Distribution\n(Per Sample)", fontweight="bold")
        axes[1].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 3. Missing data per feature
        missing_per_feature = missing_matrix.sum(axis=0)
        axes[2].hist(
            missing_per_feature,
            bins=bins,
            alpha=self.viz_config.style_config["alpha"],
            color="lightcoral",
            edgecolor="black",
        )
        axes[2].set_xlabel("Missing Samples per Feature")
        axes[2].set_ylabel("Frequency")
        axes[2].set_title("Missing Data Distribution\n(Per Feature)", fontweight="bold")
        axes[2].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 4. QC vs Sample missing data (if QC samples exist)
        try:
            qc_mask = self.data_config.identify_qc_samples(data_matrix)
            if qc_mask.sum() > 0:
                qc_missing = missing_per_sample[qc_mask]
                sample_missing = missing_per_sample[~qc_mask]

                sample_colors = self._get_color_scheme("sample_types")
                box_data = [qc_missing, sample_missing]
                box_labels = ["QC", "Biological"]

                bp = axes[3].boxplot(box_data, labels=box_labels, patch_artist=True)
                if sample_colors:
                    bp["boxes"][0].set_facecolor(sample_colors.get("qc", "red"))
                    bp["boxes"][1].set_facecolor(sample_colors.get("biological", "blue"))

                axes[3].set_ylabel("Missing Features")
                axes[3].set_title("Missing Data by Sample Type", fontweight="bold")
                axes[3].grid(True, alpha=self.viz_config.style_config["grid_alpha"])
            else:
                axes[3].text(
                    0.5,
                    0.5,
                    "No QC samples identified",
                    ha="center",
                    va="center",
                    transform=axes[3].transAxes,
                    fontsize=12,
                )
                axes[3].set_title("Missing Data by Sample Type\n(No QC Found)", fontweight="bold")
        except Exception:
            axes[3].text(
                0.5,
                0.5,
                "Cannot identify sample types",
                ha="center",
                va="center",
                transform=axes[3].transAxes,
                fontsize=12,
            )
            axes[3].set_title("Missing Data by Sample Type\n(Error)", fontweight="bold")

        # 5. Most affected features
        if (missing_counts > 0).sum() > 0:
            top_missing = missing_counts[missing_counts > 0].sort_values(ascending=False).head(top_missing_count)
            axes[4].barh(
                range(len(top_missing)), top_missing.values, color="orange", alpha=self.viz_config.style_config["alpha"]
            )
            axes[4].set_yticks(range(len(top_missing)))
            axes[4].set_yticklabels([
                f"{name[:feature_name_truncate]}..." if len(name) > feature_name_truncate else name
                for name in top_missing.index
            ])
            axes[4].set_xlabel("Missing Count")
            axes[4].set_title("Most Affected Features", fontweight="bold")
            axes[4].grid(True, alpha=self.viz_config.style_config["grid_alpha"])
        else:
            axes[4].text(
                0.5,
                0.5,
                "No missing data to display",
                ha="center",
                va="center",
                transform=axes[4].transAxes,
                fontsize=12,
            )
            axes[4].set_title("Most Affected Features\n(None)", fontweight="bold")

        # 6. Missing data summary statistics
        axes[5].text(
            0.1,
            0.9,
            "Missing Data Summary:",
            fontsize=self.viz_config.style_config["title_fontsize"],
            fontweight="bold",
            transform=axes[5].transAxes,
        )

        axes[5].text(
            0.1,
            0.8,
            f"Total missing: {total_missing}",
            fontsize=self.viz_config.style_config["font_size"] + 1,
            transform=axes[5].transAxes,
        )
        axes[5].text(
            0.1,
            0.7,
            f"Affected features: {(missing_counts > 0).sum()}/{len(feature_columns)}",
            fontsize=self.viz_config.style_config["font_size"] + 1,
            transform=axes[5].transAxes,
        )

        total_data_points = len(data_matrix) * len(feature_columns)
        missing_percentage = total_missing / total_data_points * 100 if total_data_points > 0 else 0
        axes[5].text(
            0.1,
            0.6,
            f"Missing %: {missing_percentage:.2f}%",
            fontsize=self.viz_config.style_config["font_size"] + 1,
            transform=axes[5].transAxes,
        )
        axes[5].text(
            0.1,
            0.5,
            f"Max missing per feature: {missing_per_feature.max()}",
            fontsize=self.viz_config.style_config["font_size"] + 1,
            transform=axes[5].transAxes,
        )
        axes[5].text(
            0.1,
            0.4,
            f"Max missing per sample: {missing_per_sample.max()}",
            fontsize=self.viz_config.style_config["font_size"] + 1,
            transform=axes[5].transAxes,
        )
        axes[5].axis("off")

        plt.tight_layout()

        # Use existing save_fig utility instead of custom implementation
        if save_path:
            save_fig(fig, "missing_data_analysis", save_path)

        return fig

    def plot_imputation_cv_impact(
        self,
        data_before: pd.DataFrame,
        data_after: pd.DataFrame,
        glycan_columns: list[str],
        save_path: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Show CV impact of imputation.

        Uses existing CVAnalyzer instead of custom CV calculation logic.
        """
        # Identify QC samples using configured method
        qc_mask = self.data_config.identify_qc_samples(data_before)

        # Use existing CVAnalyzer to compute CV values instead of custom logic
        cv_params = {
            "feature_prefix": self.data_config.feature_prefix,
            "sample_type_col": self.data_config.sample_type_column or "SampleType",
            "qc_identifier": "QC",
            "sample_column": self.data_config.sample_column,
        }

        # Prepare data for CV analysis - add SampleType column if needed
        data_before_cv = data_before.copy()
        data_after_cv = data_after.copy()

        if cv_params["sample_type_col"] not in data_before_cv.columns:
            data_before_cv[cv_params["sample_type_col"]] = cv_params["qc_identifier"] if qc_mask.any() else "Sample"
            data_after_cv[cv_params["sample_type_col"]] = cv_params["qc_identifier"] if qc_mask.any() else "Sample"
            data_before_cv.loc[~qc_mask, cv_params["sample_type_col"]] = "Sample"
            data_after_cv.loc[~qc_mask, cv_params["sample_type_col"]] = "Sample"

        # Calculate CV using existing analyzer
        cv_results_before = self._cv_analyzer.compute_cv_by_sample_type(
            data_before_cv, feature_prefix=self.data_config.feature_prefix, sample_type_col=cv_params["sample_type_col"]
        )
        cv_results_after = self._cv_analyzer.compute_cv_by_sample_type(
            data_after_cv, feature_prefix=self.data_config.feature_prefix, sample_type_col=cv_params["sample_type_col"]
        )

        # Filter for features that had missing data and QC samples
        qc_cv_before = cv_results_before[cv_results_before[cv_params["sample_type_col"]] == cv_params["qc_identifier"]]
        qc_cv_after = cv_results_after[cv_results_after[cv_params["sample_type_col"]] == cv_params["qc_identifier"]]

        # Only analyze features that had missing data
        features_with_missing: list[str] = []
        cv_before_vals: list[float] = []
        cv_after_vals: list[float] = []

        for feature in glycan_columns:
            if data_before[feature].isnull().sum() > 0:
                before_cv = qc_cv_before[qc_cv_before["Feature"] == feature]["CV"]
                after_cv = qc_cv_after[qc_cv_after["Feature"] == feature]["CV"]

                if len(before_cv) > 0 and len(after_cv) > 0:
                    features_with_missing.append(feature)
                    cv_before_vals.append(before_cv.iloc[0])
                    cv_after_vals.append(after_cv.iloc[0])

        cv_before_array = np.array(cv_before_vals)
        cv_after_array = np.array(cv_after_vals)

        # Create visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # 1. CV before vs after imputation
        if len(cv_before_array) > 0:
            axes[0].scatter(cv_before_array, cv_after_array, alpha=0.7, color="blue", s=50)
            max_cv = max(cv_before_array.max(), cv_after_array.max())
            axes[0].plot([0, max_cv], [0, max_cv], "r--", label="y=x")
            axes[0].set_xlabel("CV Before Imputation (%)")
            axes[0].set_ylabel("CV After Imputation (%)")
            axes[0].set_title("CV Impact of Imputation", fontweight="bold")
            axes[0].legend()
            axes[0].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 2. CV improvement distribution
        if len(cv_before_array) > 0:
            cv_improvement = cv_before_array - cv_after_array
            axes[1].hist(cv_improvement, bins=15, alpha=0.7, color="green", edgecolor="black")
            axes[1].axvline(0, color="red", linestyle="--", label="No improvement")
            axes[1].set_xlabel("CV Improvement (percentage points)")
            axes[1].set_ylabel("Frequency")
            axes[1].set_title("CV Improvement Distribution", fontweight="bold")
            axes[1].legend()
            axes[1].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 3. Summary statistics
        if len(cv_before_array) > 0:
            cv_improvement = cv_before_array - cv_after_array
            axes[2].text(
                0.1, 0.9, "Imputation Impact Summary:", fontsize=12, fontweight="bold", transform=axes[2].transAxes
            )
            axes[2].text(
                0.1, 0.8, f"Features imputed: {len(features_with_missing)}", fontsize=11, transform=axes[2].transAxes
            )
            axes[2].text(
                0.1, 0.7, f"Mean CV before: {cv_before_array.mean():.1f}%", fontsize=11, transform=axes[2].transAxes
            )
            axes[2].text(
                0.1, 0.6, f"Mean CV after: {cv_after_array.mean():.1f}%", fontsize=11, transform=axes[2].transAxes
            )
            axes[2].text(
                0.1, 0.5, f"Mean improvement: {cv_improvement.mean():.1f}pp", fontsize=11, transform=axes[2].transAxes
            )
            axes[2].text(
                0.1,
                0.4,
                f"Features improved: {(cv_improvement > 0).sum()}/{len(cv_improvement)}",
                fontsize=11,
                transform=axes[2].transAxes,
            )
            axes[2].axis("off")
        else:
            axes[2].text(
                0.5,
                0.5,
                "No features required imputation",
                ha="center",
                va="center",
                fontsize=14,
                transform=axes[2].transAxes,
            )
            axes[2].axis("off")

        plt.tight_layout()

        # Use existing save_fig utility
        if save_path:
            save_fig(fig, "imputation_cv_impact", save_path)

        return fig


class FeatureAbundanceClassifier:
    """
    Class for standardized feature abundance classification.

    This class provides comprehensive tools for classifying and visualizing feature
    abundance distributions, helping users understand data quality and identify
    features suitable for different analytical approaches.

    Maintains original API while using existing isospec utilities internally.

    Examples:
        Basic feature abundance classification:

        >>> import pandas as pd
        >>> from isospec_data_tools.visualization.analysis import FeatureAbundanceClassifier
        >>>
        >>> # Initialize classifier
        >>> classifier = FeatureAbundanceClassifier()
        >>>
        >>> # Classify features
        >>> results = classifier.classify_feature_abundance(
        ...     data=metabolomics_data,
        ...     feature_columns=["FT001", "FT002", "FT003"]
        ... )
        >>>
        >>> # Access classification results
        >>> print(f"High abundance features: {len(results['high'])}")
        >>> print(f"Medium abundance features: {len(results['medium'])}")
        >>> print(f"Low abundance features: {len(results['low'])}")

        With custom configuration and QC analysis:

        >>> from isospec_data_tools.visualization.analysis import StatisticalConfig
        >>>
        >>> # Configure thresholds
        >>> stats_config = StatisticalConfig(
        ...     percentile_thresholds=(25.0, 75.0),
        ...     cv_threshold=20.0
        ... )
        >>>
        >>> # Initialize with custom config
        >>> classifier = FeatureAbundanceClassifier(stats_config=stats_config)
        >>>
        >>> # Classify with QC analysis
        >>> qc_mask = data["SampleType"].isin(["QC", "EQC"])
        >>> results = classifier.classify_feature_abundance(
        ...     data=metabolomics_data,
        ...     feature_columns=feature_columns,
        ...     qc_samples=qc_mask
        ... )

        Visualizing feature abundance distributions:

        >>> # Create abundance distribution plot
        >>> fig = classifier.plot_abundance_distributions(
        ...     data=metabolomics_data,
        ...     feature_columns=feature_columns,
        ...     classification_results=results,
        ...     save_path="abundance_distributions.png"
        ... )
    """

    def __init__(
        self,
        project_config: Optional[Any] = None,
        data_config: Optional[DataStructureConfig] = None,
        stats_config: Optional[StatisticalConfig] = None,
        viz_config: Optional[VisualizationConfig] = None,
        plugin_registry: Optional[Any] = None,
    ):
        """Initialize feature abundance classifier."""
        self.project_config = project_config
        self.data_config = data_config or DataStructureConfig()
        self.stats_config = stats_config or StatisticalConfig()
        self.viz_config = viz_config or VisualizationConfig()

        # Use existing isospec utilities
        self._stat_analyzer = StatisticalAnalyzer()

    def _get_qc_mask(self, data_matrix: pd.DataFrame) -> pd.Series:
        """Get mask for QC samples using existing patterns."""
        return self.data_config.identify_qc_samples(data_matrix)

    def _get_color_scheme(self, scheme_name: str) -> dict[str, str]:
        """Get color scheme from configuration."""
        return self.viz_config.color_schemes.get(
            scheme_name, {"low": "lightcoral", "medium": "lightyellow", "high": "lightgreen"}
        )

    def _get_figure_layout(self, plot_type: str) -> tuple[int, int]:
        """Get figure layout from configuration."""
        return self.viz_config.figure_layouts.get(plot_type, (15, 5))

    def classify_by_total_abundance(
        self,
        data_matrix: pd.DataFrame,
        feature_columns: list[str],
        use_qc_only: Optional[bool] = None,
        percentile_thresholds: Optional[tuple[float, float]] = None,
    ) -> dict[str, Any]:
        """
        Classify features by total abundance.

        Maintains original API while using simplified internal logic.
        """
        try:
            # Validate inputs
            if not isinstance(data_matrix, pd.DataFrame):
                raise TypeError("data_matrix must be a pandas DataFrame")

            if not feature_columns:
                raise ValueError("feature_columns cannot be empty")

            # Use configuration defaults if not specified
            if use_qc_only is None:
                use_qc_only = True  # Default behavior

            if percentile_thresholds is None:
                percentile_thresholds = self.stats_config.percentile_thresholds

            # Validate feature columns
            missing_columns = [col for col in feature_columns if col not in data_matrix.columns]
            if missing_columns:
                raise ValueError(f"Missing columns in data_matrix: {missing_columns}")

            # Determine which samples to use for threshold calculation
            if use_qc_only:
                qc_mask = self._get_qc_mask(data_matrix)
                if qc_mask.sum() > 0:
                    feature_totals = data_matrix[qc_mask][feature_columns].sum(axis=0)
                    calculation_basis = "QC samples"
                else:
                    # Fallback to all samples if no QC samples found
                    feature_totals = data_matrix[feature_columns].sum(axis=0)
                    calculation_basis = "all samples (no QC samples found)"
            else:
                feature_totals = data_matrix[feature_columns].sum(axis=0)
                calculation_basis = "all samples"

            # Handle edge case where all totals are zero or NaN
            if feature_totals.isna().all() or (feature_totals == 0).all():
                num_features = len(feature_columns)
                third = num_features // 3

                return {
                    "low_abundance": feature_columns[:third],
                    "medium_abundance": feature_columns[third : 2 * third],
                    "high_abundance": feature_columns[2 * third :],
                    "thresholds": {"low_threshold": 0.0, "high_threshold": 0.0},
                    "criteria": {
                        "low": "No abundance data available - equal distribution (first third)",
                        "medium": "No abundance data available - equal distribution (middle third)",
                        "high": "No abundance data available - equal distribution (last third)",
                    },
                    "feature_totals": feature_totals,
                    "calculation_basis": calculation_basis,
                }

            # Define thresholds using configurable percentiles
            low_percentile, high_percentile = percentile_thresholds
            low_threshold = feature_totals.quantile(low_percentile / 100.0)
            high_threshold = feature_totals.quantile(high_percentile / 100.0)

            # Handle edge case where thresholds are identical
            if low_threshold == high_threshold:
                median_threshold = feature_totals.median()
                low_abundance = feature_totals[feature_totals < median_threshold].index.tolist()
                high_abundance = feature_totals[feature_totals > median_threshold].index.tolist()
                medium_abundance = feature_totals[feature_totals == median_threshold].index.tolist()

                return {
                    "low_abundance": low_abundance,
                    "medium_abundance": medium_abundance,
                    "high_abundance": high_abundance,
                    "thresholds": {"low_threshold": median_threshold, "high_threshold": median_threshold},
                    "criteria": {
                        "low": f"Total abundance < {median_threshold:.4f} (below median of {calculation_basis})",
                        "medium": f"Total abundance = {median_threshold:.4f} (at median of {calculation_basis})",
                        "high": f"Total abundance > {median_threshold:.4f} (above median of {calculation_basis})",
                    },
                    "feature_totals": feature_totals,
                    "calculation_basis": calculation_basis,
                }

            # Normal classification
            low_abundance = feature_totals[feature_totals <= low_threshold].index.tolist()
            medium_abundance = feature_totals[
                (feature_totals > low_threshold) & (feature_totals <= high_threshold)
            ].index.tolist()
            high_abundance = feature_totals[feature_totals > high_threshold].index.tolist()

            return {
                "low_abundance": low_abundance,
                "medium_abundance": medium_abundance,
                "high_abundance": high_abundance,
                "thresholds": {"low_threshold": low_threshold, "high_threshold": high_threshold},
                "criteria": {
                    "low": f"Total abundance ≤ {low_threshold:.4f} ({low_percentile}th percentile of {calculation_basis})",
                    "medium": f"Total abundance {low_threshold:.4f} - {high_threshold:.4f} ({low_percentile}th-{high_percentile}th percentile of {calculation_basis})",
                    "high": f"Total abundance > {high_threshold:.4f} ({high_percentile}th percentile of {calculation_basis})",
                },
                "feature_totals": feature_totals,
                "calculation_basis": calculation_basis,
            }

        except Exception as e:
            # Return error classification with minimal structure
            return {
                "low_abundance": [],
                "medium_abundance": [],
                "high_abundance": feature_columns,  # Put all features in high category as fallback
                "thresholds": {"low_threshold": 0.0, "high_threshold": 0.0},
                "criteria": {
                    "low": f"Classification error: {e!s}",
                    "medium": f"Classification error: {e!s}",
                    "high": f"All features (classification error): {e!s}",
                },
                "feature_totals": pd.Series(index=feature_columns, data=0.0),
                "error": str(e),
            }

    def plot_abundance_classification(
        self, classification: dict[str, Any], save_path: Optional[str] = None
    ) -> matplotlib.figure.Figure:
        """
        Visualize feature abundance classification.

        Uses existing plotting utilities internally.
        """
        # Get configuration values
        fig_size = self._get_figure_layout("abundance_classification")
        colors = ["lightcoral", "lightyellow", "lightgreen"]

        fig, axes = plt.subplots(1, 3, figsize=fig_size)

        # 1. Classification distribution
        categories = ["Low\nAbundance", "Medium\nAbundance", "High\nAbundance"]
        counts = [
            len(classification["low_abundance"]),
            len(classification["medium_abundance"]),
            len(classification["high_abundance"]),
        ]

        axes[0].bar(categories, counts, color=colors, alpha=0.7, edgecolor="black")
        axes[0].set_ylabel("Number of Features")
        axes[0].set_title("Feature Abundance Classification", fontweight="bold")
        axes[0].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # Add percentages on bars
        total_features = sum(counts)
        for i, count in enumerate(counts):
            percentage = count / total_features * 100 if total_features > 0 else 0
            axes[0].text(i, count + 0.5, f"{percentage:.1f}%", ha="center", va="bottom", fontweight="bold")

        # 2. Abundance distribution with thresholds
        feature_totals = classification["feature_totals"]
        axes[1].hist(feature_totals, bins=30, alpha=0.7, color="skyblue", edgecolor="black")
        axes[1].axvline(
            classification["thresholds"]["low_threshold"], color="red", linestyle="--", label="Low threshold"
        )
        axes[1].axvline(
            classification["thresholds"]["high_threshold"], color="green", linestyle="--", label="High threshold"
        )
        axes[1].set_xlabel("Total Abundance")
        axes[1].set_ylabel("Frequency")
        axes[1].set_title("Feature Abundance Distribution\nwith Thresholds", fontweight="bold")
        axes[1].legend()
        axes[1].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 3. Classification criteria
        axes[2].text(0.1, 0.9, "Classification Criteria:", fontsize=12, fontweight="bold", transform=axes[2].transAxes)
        axes[2].text(
            0.1, 0.8, f"Low: {classification['criteria']['low']}", fontsize=10, transform=axes[2].transAxes, color="red"
        )
        axes[2].text(
            0.1,
            0.7,
            f"Medium: {classification['criteria']['medium']}",
            fontsize=10,
            transform=axes[2].transAxes,
            color="orange",
        )
        axes[2].text(
            0.1,
            0.6,
            f"High: {classification['criteria']['high']}",
            fontsize=10,
            transform=axes[2].transAxes,
            color="green",
        )

        axes[2].text(0.1, 0.5, "Statistics:", fontsize=12, fontweight="bold", transform=axes[2].transAxes)
        axes[2].text(0.1, 0.4, f"Total features: {total_features}", fontsize=10, transform=axes[2].transAxes)
        axes[2].text(
            0.1,
            0.3,
            f"Low: {len(classification['low_abundance'])} ({len(classification['low_abundance']) / total_features * 100:.1f}%)",
            fontsize=10,
            transform=axes[2].transAxes,
        )
        axes[2].text(
            0.1,
            0.2,
            f"Medium: {len(classification['medium_abundance'])} ({len(classification['medium_abundance']) / total_features * 100:.1f}%)",
            fontsize=10,
            transform=axes[2].transAxes,
        )
        axes[2].text(
            0.1,
            0.1,
            f"High: {len(classification['high_abundance'])} ({len(classification['high_abundance']) / total_features * 100:.1f}%)",
            fontsize=10,
            transform=axes[2].transAxes,
        )
        axes[2].axis("off")

        plt.tight_layout()

        # Use existing save_fig utility
        if save_path:
            save_fig(fig, "abundance_classification", save_path)

        return fig


class CVAnalysisPlotter:
    """
    Specialized plotting class for CV-focused analysis.

    This class provides comprehensive visualization tools for tracking coefficient of
    variation (CV) improvements through data preprocessing pipelines, helping users
    evaluate the effectiveness of normalization and quality control procedures.

    Uses existing CVAnalyzer internally to avoid duplication.

    Examples:
        Basic CV improvement analysis:

        >>> import pandas as pd
        >>> from isospec_data_tools.visualization.analysis import CVAnalysisPlotter
        >>>
        >>> # Initialize CV plotter
        >>> cv_plotter = CVAnalysisPlotter()
        >>>
        >>> # Calculate and plot CV improvements
        >>> fig = cv_plotter.plot_cv_improvements(
        ...     data_before=raw_data,
        ...     data_after=normalized_data,
        ...     feature_columns=["FT001", "FT002", "FT003"],
        ...     qc_samples=qc_mask,
        ...     save_path="cv_improvements.png"
        ... )

        Normalization method comparison:

        >>> # Compare multiple normalization methods
        >>> methods_data = {
        ...     "raw": raw_data,
        ...     "total_abundance": ta_normalized,
        ...     "median_quotient": mq_normalized
        ... }
        >>>
        >>> fig = cv_plotter.plot_cv_comparison_methods(
        ...     methods_data=methods_data,
        ...     feature_columns=feature_columns,
        ...     qc_samples=qc_mask,
        ...     save_path="cv_method_comparison.png"
        ... )

        Detailed CV distribution analysis:

        >>> from isospec_data_tools.visualization.analysis import StatisticalConfig
        >>>
        >>> # Configure CV thresholds
        >>> stats_config = StatisticalConfig(
        ...     cv_threshold=30.0,
        ...     cv_ranges=[(0, 10, "Excellent"), (10, 20, "Good"),
        ...                (20, 30, "Acceptable"), (30, float("inf"), "Poor")]
        ... )
        >>>
        >>> # Initialize with custom config
        >>> cv_plotter = CVAnalysisPlotter(stats_config=stats_config)
        >>>
        >>> # Plot CV distributions with custom categories
        >>> fig = cv_plotter.plot_cv_distributions(
        ...     data=normalized_data,
        ...     feature_columns=feature_columns,
        ...     qc_samples=qc_mask,
        ...     save_path="cv_distributions.png"
        ... )
    """

    def __init__(
        self,
        project_config: Optional[Any] = None,
        data_config: Optional[DataStructureConfig] = None,
        stats_config: Optional[StatisticalConfig] = None,
        viz_config: Optional[VisualizationConfig] = None,
        plugin_registry: Optional[Any] = None,
    ):
        """Initialize CV analysis plotter."""
        self.project_config = project_config
        self.data_config = data_config or DataStructureConfig()
        self.stats_config = stats_config or StatisticalConfig()
        self.viz_config = viz_config or VisualizationConfig()
        self.plot_config = PlottingConfig()
        self.plot_config.setup_style()
        # Use existing isospec utilities
        self._cv_analyzer = CVAnalyzer()
        self._stat_analyzer = StatisticalAnalyzer()

        # Setup styling
        PlotStyler.setup_seaborn_style()

    def _get_figure_layout(self, plot_type: str) -> tuple[int, int]:
        """Get figure layout from configuration."""
        return self.viz_config.figure_layouts.get(plot_type, (15, 5))

    def _get_color_scheme(self, scheme_name: str) -> dict[str, str]:
        """Get color scheme from configuration."""
        return self.viz_config.color_schemes.get(scheme_name, {})

    def _get_subplot_arrangement(self, plot_type: str) -> tuple[int, int]:
        """Get subplot arrangement from configuration."""
        return self.viz_config.subplot_arrangements.get(plot_type, (1, 2))

    def plot_feature_cv_improvement(
        self,
        cv_before: np.ndarray,
        cv_after: np.ndarray,
        feature_names: list[str],
        title_override: Optional[str] = None,
        normalization_method: Optional[NormalizationConfig] = None,
        save_path: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Show which features improved and by how much.

        Uses existing statistical utilities instead of custom implementations.
        """
        cv_improvement = cv_before - cv_after

        # Get configuration values
        fig_size = self._get_figure_layout("cv_improvement")
        colors = self._get_color_scheme("improvements")
        categories = self.stats_config.improvement_categories

        # Generate dynamic title
        if title_override:
            main_title = title_override
        elif normalization_method:
            main_title = f"{normalization_method.method_name} Impact on CV"
        else:
            main_title = "CV Improvement Analysis"

        fig, axes = plt.subplots(1, 3, figsize=fig_size)

        # 1. CV before vs after scatter plot
        scatter_color = colors.get("scatter", "blue")
        diagonal_color = colors.get("diagonal", "red")

        axes[0].scatter(cv_before, cv_after, alpha=0.7, color=scatter_color, s=50)
        max_cv = max(cv_before.max(), cv_after.max())
        axes[0].plot([0, max_cv], [0, max_cv], "--", color=diagonal_color, label="y=x")
        axes[0].set_xlabel("CV Before (%)")
        axes[0].set_ylabel("CV After (%)")
        method_name = normalization_method.method_abbreviation if normalization_method else "Normalization"
        axes[0].set_title(f"{method_name} CV Impact\nBefore vs After", fontweight="bold")
        axes[0].legend()
        axes[0].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 2. CV improvement distribution
        hist_bins = self.stats_config.histogram_bins.get("cv_improvement", 20)
        hist_color = colors.get("histogram", "green")
        no_improve_color = colors.get("no_improvement_line", "red")

        axes[1].hist(cv_improvement, bins=hist_bins, alpha=0.7, color=hist_color, edgecolor="black")
        axes[1].axvline(0, color=no_improve_color, linestyle="--", label="No improvement")
        axes[1].set_xlabel("CV Improvement (percentage points)")
        axes[1].set_ylabel("Frequency")
        axes[1].set_title("CV Improvement Distribution", fontweight="bold")
        axes[1].legend()
        axes[1].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # 3. Feature performance categories with configurable thresholds
        category_labels = []
        category_counts = []
        category_colors = []

        for min_threshold, max_threshold, label, color_key in categories:
            if max_threshold == float("inf"):
                count = (cv_improvement > min_threshold).sum()
            elif min_threshold == float("-inf"):
                count = (cv_improvement <= max_threshold).sum()
            else:
                count = ((cv_improvement > min_threshold) & (cv_improvement <= max_threshold)).sum()

            category_labels.append(label)
            category_counts.append(count)
            category_colors.append(colors.get(color_key, color_key))  # Use color_key as fallback

        axes[2].bar(category_labels, category_counts, color=category_colors, alpha=0.7)
        axes[2].set_ylabel("Number of Features")
        axes[2].set_title("Feature Performance Categories", fontweight="bold")
        axes[2].grid(True, alpha=self.viz_config.style_config["grid_alpha"])

        # Add percentages on bars
        for i, count in enumerate(category_counts):
            percentage = count / len(cv_improvement) * 100 if len(cv_improvement) > 0 else 0
            axes[2].text(i, count + 0.5, f"{percentage:.1f}%", ha="center", va="bottom", fontweight="bold")

        plt.suptitle(main_title, fontsize=16, fontweight="bold")
        plt.tight_layout()

        # Use existing save_fig utility
        if save_path:
            save_fig(fig, "cv_improvement_analysis", save_path)

        return fig

    def plot_cv_distribution_shift(
        self,
        cv_before: np.ndarray,
        cv_after: np.ndarray,
        title_override: Optional[str] = None,
        normalization_method: Optional[NormalizationConfig] = None,
        layout_override: Optional[tuple[int, int]] = None,
        color_scheme_override: Optional[dict[str, str]] = None,
        histogram_bins: Optional[int] = None,
    ) -> matplotlib.figure.Figure:
        """
        Show CV distribution changes with configurable styling and layout.

        Args:
            cv_before: CV values before normalization
            cv_after: CV values after normalization
            title_override: Override main title
            normalization_method: Configuration for normalization method information
            layout_override: Override figure size (width, height)
            color_scheme_override: Override color scheme
            histogram_bins: Override number of histogram bins

        Returns:
            Figure showing CV distribution shift
        """
        # Get configuration values
        fig_size = layout_override or self._get_figure_layout("cv_distribution_shift")
        subplot_arrange = self._get_subplot_arrangement("cv_distribution_shift")
        colors = color_scheme_override or self._get_color_scheme("cv_distribution")
        bins = histogram_bins or self.stats_config.histogram_bins.get("cv_distribution", 25)

        # Generate dynamic title
        if title_override:
            main_title = title_override
        elif normalization_method:
            main_title = f"{normalization_method.method_name} CV Distribution Shift"
        else:
            main_title = "CV Distribution Shift"

        fig: matplotlib.figure.Figure
        axes: Any
        fig, axes = plt.subplots(*subplot_arrange, figsize=fig_size)

        # 1. Overlaid histograms with configurable colors
        before_color = colors.get("before", "red")
        after_color = colors.get("after", "green")

        axes[0].hist(cv_before, bins=bins, alpha=0.6, label="Before", color=before_color, density=True)
        axes[0].hist(cv_after, bins=bins, alpha=0.6, label="After", color=after_color, density=True)
        axes[0].set_xlabel("CV (%)")
        axes[0].set_ylabel("Density")
        method_name = normalization_method.method_abbreviation if normalization_method else "Normalization"
        axes[0].set_title(f"{method_name} Distribution Shift\nOverlay", fontweight="bold")
        axes[0].legend()
        grid_alpha = getattr(self.plot_config, "grid_alpha", 0.3)
        axes[0].grid(True, alpha=grid_alpha)

        # 2. Box plot comparison
        box_plot = axes[1].boxplot([cv_before, cv_after], labels=["Before", "After"], patch_artist=True)
        box_plot["boxes"][0].set_facecolor(before_color)
        box_plot["boxes"][0].set_alpha(0.6)
        box_plot["boxes"][1].set_facecolor(after_color)
        box_plot["boxes"][1].set_alpha(0.6)

        axes[1].set_ylabel("CV (%)")
        axes[1].set_title(f"{main_title}\nDistribution Comparison", fontweight="bold")
        axes[1].grid(True, alpha=grid_alpha)

        # Add improvement statistics
        improvement = cv_before.mean() - cv_after.mean()
        axes[1].text(
            0.5,
            0.95,
            f"Mean improvement: {improvement:.1f}pp",
            transform=axes[1].transAxes,
            ha="center",
            va="top",
            bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
        )

        plt.suptitle(main_title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        return fig

    def analyze_non_improved_features(
        self,
        cv_before: np.ndarray,
        cv_after: np.ndarray,
        abundance_data: pd.DataFrame,
        feature_names: list[str],
        improvement_threshold: Optional[float] = None,
        percentile_thresholds: Optional[tuple[float, float]] = None,
        layout_override: Optional[tuple[int, int]] = None,
        color_scheme_override: Optional[dict[str, str]] = None,
        title_override: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Analyze features that didn't improve vs abundance levels with configurable thresholds.

        Args:
            cv_before: CV values before normalization
            cv_after: CV values after normalization
            abundance_data: Feature abundance data
            feature_names: Names of features
            improvement_threshold: Threshold for considering improvement (default: 0)
            percentile_thresholds: Tuple of (low_percentile, high_percentile) for abundance classification
            layout_override: Override figure size (width, height)
            color_scheme_override: Override color scheme
            title_override: Override main title

        Returns:
            Figure showing non-improved feature analysis
        """
        cv_improvement = cv_before - cv_after

        # Get configuration values
        if improvement_threshold is None:
            improvement_threshold = 0.0

        if percentile_thresholds is None:
            percentile_thresholds = self.stats_config.percentile_thresholds

        colors = color_scheme_override or self._get_color_scheme("abundance_analysis")
        main_title = title_override or "Non-Improved Feature Analysis"

        # Calculate median abundances per feature
        median_abundances = abundance_data.median()

        # Use configurable percentiles for abundance classification
        low_percentile, high_percentile = percentile_thresholds
        abundance_low_threshold = median_abundances.quantile(low_percentile / 100.0)
        abundance_high_threshold = median_abundances.quantile(high_percentile / 100.0)

        # Classify features by abundance levels
        low_abundance_mask = median_abundances <= abundance_low_threshold
        medium_abundance_mask = (median_abundances > abundance_low_threshold) & (
            median_abundances <= abundance_high_threshold
        )
        high_abundance_mask = median_abundances > abundance_high_threshold

        # Classify features by improvement
        improved_mask = cv_improvement > 0

        # Create visualization
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 1. CV improvement vs abundance with configurable colors and thresholds
        scatter_color = colors.get("scatter", "blue")
        no_improve_color = colors.get("no_improvement_line", "red")

        axes[0, 0].scatter(median_abundances, cv_improvement, alpha=0.7, color=scatter_color, s=50)
        axes[0, 0].axhline(improvement_threshold, color=no_improve_color, linestyle="--", label="No improvement")
        # axes[0, 0].axvline(abundance_low_threshold, color=low_threshold_color, linestyle='--', label=f'{low_percentile}th percentile')
        # axes[0, 0].axvline(abundance_high_threshold, color=high_threshold_color, linestyle='--', label=f'{high_percentile}th percentile')
        axes[0, 0].set_xlabel("Median Abundance")
        axes[0, 0].set_ylabel("CV Improvement (pp)")
        axes[0, 0].set_title("CV Improvement vs Abundance", fontweight="bold")
        axes[0, 0].legend()
        grid_alpha = getattr(self.plot_config, "grid_alpha", 0.3)
        axes[0, 0].grid(True, alpha=grid_alpha)

        # 2. Feature classification matrix (3x2: abundance levels x improvement status)
        high_improved = (high_abundance_mask & improved_mask).sum()
        high_not_improved = (high_abundance_mask & ~improved_mask).sum()
        medium_improved = (medium_abundance_mask & improved_mask).sum()
        medium_not_improved = (medium_abundance_mask & ~improved_mask).sum()
        low_improved = (low_abundance_mask & improved_mask).sum()
        low_not_improved = (low_abundance_mask & ~improved_mask).sum()

        classification_data = np.array([
            [high_improved, high_not_improved],
            [medium_improved, medium_not_improved],
            [low_improved, low_not_improved],
        ])

        im = axes[0, 1].imshow(classification_data, cmap="YlOrRd", aspect="auto")
        axes[0, 1].set_xticks([0, 1])
        axes[0, 1].set_xticklabels(["Improved", "Not Improved"])
        axes[0, 1].set_yticks([0, 1, 2])
        axes[0, 1].set_yticklabels(["High Abundance", "Medium Abundance", "Low Abundance"])
        axes[0, 1].set_title("Feature Classification Matrix", fontweight="bold")

        # Add text annotations
        for i in range(3):
            for j in range(2):
                axes[0, 1].text(j, i, f"{classification_data[i, j]}", ha="center", va="center", fontweight="bold")

        plt.colorbar(im, ax=axes[0, 1])

        # 3. Non-improved feature abundance distribution
        non_improved_features = np.array(feature_names)[~improved_mask]
        if len(non_improved_features) > 0:
            non_improved_abundances = median_abundances[~improved_mask]
            overall_median = median_abundances.median()
            axes[1, 0].hist(non_improved_abundances, bins=20, alpha=0.7, color="orange", edgecolor="black")
            axes[1, 0].axvline(overall_median, color="green", linestyle="--", label="Overall median")
            axes[1, 0].set_xlabel("Median Abundance")
            axes[1, 0].set_ylabel("Frequency")
            axes[1, 0].set_title("Non-Improved Feature Abundances", fontweight="bold")
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=self.plot_config.grid_alpha)

        # 4. Summary statistics
        axes[1, 1].text(
            0.1, 0.9, "Non-Improved Feature Analysis:", fontsize=12, fontweight="bold", transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(0.1, 0.8, f"Total features: {len(feature_names)}", fontsize=11, transform=axes[1, 1].transAxes)
        axes[1, 1].text(
            0.1, 0.7, f"Improved features: {improved_mask.sum()}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1, 0.6, f"Non-improved features: {(~improved_mask).sum()}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1, 0.5, f"High abundance, improved: {high_improved}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1, 0.45, f"High abundance, not improved: {high_not_improved}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1, 0.4, f"Medium abundance, improved: {medium_improved}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1,
            0.35,
            f"Medium abundance, not improved: {medium_not_improved}",
            fontsize=11,
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].text(
            0.1, 0.3, f"Low abundance, improved: {low_improved}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].text(
            0.1, 0.25, f"Low abundance, not improved: {low_not_improved}", fontsize=11, transform=axes[1, 1].transAxes
        )
        axes[1, 1].axis("off")

        plt.suptitle(main_title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        return fig

    def plot_comprehensive_cv_analysis(
        self, pipeline_config: TransformationPipelineConfig, cv_data_final_str: str, data_config: DataStructureConfig
    ) -> matplotlib.figure.Figure:
        """
        Create comprehensive CV analysis showing all transformation steps.

        Parameters:
        -----------
        pipeline_config : TransformationPipelineConfig
            Configuration containing all transformation stages and CV data
        cv_data_final_str : str
            Final CV  from CVAnalyzer

        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure showing comprehensive CV analysis
        """
        # Extract data from pipeline config
        stages = pipeline_config.stage_names
        cv_all_steps = pipeline_config.transformations  # This should contain the CV dataframes
        # Extract CV values for each step and sample type
        qc_cv_by_stage = {}
        sample_cv_by_stage = {}
        cv_data_final = pipeline_config.transformations[cv_data_final_str]

        for stage in stages:
            if stage in cv_all_steps:
                stage_data = cv_all_steps[stage]
                if "CV" in stage_data.columns and data_config.sample_type_column in stage_data.columns:
                    qc_cv_by_stage[stage] = stage_data[
                        stage_data[data_config.sample_type_column] == data_config.qc_identifier
                    ]["CV"].values
                    sample_cv_by_stage[stage] = stage_data[
                        stage_data[data_config.sample_type_column] == data_config.biological_sample_identifier
                    ]["CV"].values

        # Create comprehensive visualization
        fig, axes = plt.subplots(2, 4, figsize=(20, 12))

        # 1. QC CV progression comparison
        qc_data_plot = [qc_cv_by_stage[stage] for stage in stages if stage in qc_cv_by_stage]
        qc_labels = [
            pipeline_config.stage_descriptions.get(stage, stage) for stage in stages if stage in qc_cv_by_stage
        ]
        qc_colors = [pipeline_config.stage_colors.get(stage, "blue") for stage in stages if stage in qc_cv_by_stage]

        bp = axes[0, 0].boxplot(qc_data_plot, labels=qc_labels, patch_artist=True)
        for patch, color in zip(bp["boxes"], qc_colors, strict=False):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        axes[0, 0].set_ylabel("CV (%)")
        axes[0, 0].set_title("QC CV Progression\n(All Transformation Steps)", fontweight="bold")
        axes[0, 0].grid(True, alpha=self.plot_config.grid_alpha)

        # 2. Biological sample CV progression
        sample_data_plot = [sample_cv_by_stage[stage] for stage in stages if stage in sample_cv_by_stage]
        sample_labels = [
            pipeline_config.stage_descriptions.get(stage, stage) for stage in stages if stage in sample_cv_by_stage
        ]
        sample_colors = [
            pipeline_config.stage_colors.get(stage, "blue") for stage in stages if stage in sample_cv_by_stage
        ]

        bp = axes[0, 1].boxplot(sample_data_plot, labels=sample_labels, patch_artist=True)
        for patch, color in zip(bp["boxes"], sample_colors, strict=False):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        axes[0, 1].set_ylabel("CV (%)")
        axes[0, 1].set_title("Biological Sample CV Progression\n(All Transformation Steps)", fontweight="bold")
        axes[0, 1].grid(True, alpha=self.plot_config.grid_alpha)

        # 3. QC CV distribution overlays
        for stage in stages:
            if stage in qc_cv_by_stage:
                axes[0, 2].hist(
                    qc_cv_by_stage[stage],
                    bins=25,
                    alpha=0.5,
                    label=pipeline_config.stage_descriptions.get(stage, stage),
                    color=pipeline_config.stage_colors.get(stage, "blue"),
                    density=True,
                )
        axes[0, 2].set_xlabel("CV (%)")
        axes[0, 2].set_ylabel("Density")
        axes[0, 2].set_title("QC CV Distribution\n(All Steps)", fontweight="bold")
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=self.plot_config.grid_alpha)

        # 4. Biological sample CV distribution overlays
        for stage in stages:
            if stage in sample_cv_by_stage:
                axes[0, 3].hist(
                    sample_cv_by_stage[stage],
                    bins=25,
                    alpha=0.5,
                    label=pipeline_config.stage_descriptions.get(stage, stage),
                    color=pipeline_config.stage_colors.get(stage, "blue"),
                    density=True,
                )
        axes[0, 3].set_xlabel("CV (%)")
        axes[0, 3].set_ylabel("Density")
        axes[0, 3].set_title("Biological Sample CV Distribution\n(All Steps)", fontweight="bold")
        axes[0, 3].legend()
        axes[0, 3].grid(True, alpha=self.plot_config.grid_alpha)

        # 5. Step-by-step improvement analysis
        # Calculate improvements between consecutive stages
        if len(stages) >= 2:
            for i in range(1, len(stages)):
                prev_stage = stages[i - 1]
                curr_stage = stages[i]
                if prev_stage in qc_cv_by_stage and curr_stage in qc_cv_by_stage:
                    improvement = np.array(qc_cv_by_stage[prev_stage]) - np.array(qc_cv_by_stage[curr_stage])
                    label = f"{pipeline_config.stage_descriptions.get(prev_stage, prev_stage)} → {pipeline_config.stage_descriptions.get(curr_stage, curr_stage)}"
                    axes[1, 0].hist(improvement, bins=20, alpha=0.6, label=label)

            # Add total improvement if we have first and last stage
            if stages[0] in qc_cv_by_stage and stages[-1] in qc_cv_by_stage:
                total_improvement = np.array(qc_cv_by_stage[stages[0]]) - np.array(qc_cv_by_stage[stages[-1]])
                axes[1, 0].hist(total_improvement, bins=20, alpha=0.6, label="Total improvement", color="green")

        axes[1, 0].axvline(0, color="red", linestyle="--", alpha=0.5)
        axes[1, 0].set_xlabel("CV Improvement (percentage points)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].set_title("QC CV Improvement by Step", fontweight="bold")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=self.plot_config.grid_alpha)

        # 6. Feature-wise transformation effectiveness
        if len(stages) >= 2 and stages[0] in qc_cv_by_stage and stages[-1] in qc_cv_by_stage:
            first_cv = qc_cv_by_stage[stages[0]]
            last_cv = qc_cv_by_stage[stages[-1]]
            axes[1, 1].scatter(first_cv, last_cv, alpha=0.6, color="purple", s=30)
            max_cv = max(np.array(first_cv).max(), np.array(last_cv).max())
            axes[1, 1].plot([0, max_cv], [0, max_cv], "r--", label="y=x")
            axes[1, 1].set_xlabel(f"{pipeline_config.stage_descriptions.get(stages[0], stages[0])} CV (%)")
            axes[1, 1].set_ylabel(f"{pipeline_config.stage_descriptions.get(stages[-1], stages[-1])} CV (%)")
            axes[1, 1].set_title("QC CV: First vs Final Stage", fontweight="bold")
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=self.plot_config.grid_alpha)

        # 7. CV reduction effectiveness
        if (
            len(stages) >= 2
            and stages[0] in qc_cv_by_stage
            and stages[-1] in qc_cv_by_stage
            and stages[0] in sample_cv_by_stage
            and stages[-1] in sample_cv_by_stage
        ):
            qc_start = np.array(qc_cv_by_stage[stages[0]])
            qc_end = np.array(qc_cv_by_stage[stages[-1]])
            sample_start = np.array(sample_cv_by_stage[stages[0]])
            sample_end = np.array(sample_cv_by_stage[stages[-1]])
            cv_reduction_qc = (qc_start - qc_end) / qc_start * 100
            cv_reduction_sample = (sample_start - sample_end) / sample_start * 100

            axes[1, 2].boxplot([cv_reduction_qc, cv_reduction_sample], labels=["QC", "Biological"], patch_artist=True)
            axes[1, 2].set_ylabel("CV Reduction (%)")
            axes[1, 2].set_title("Relative CV Reduction\n(% of original CV)", fontweight="bold")
            axes[1, 2].grid(True, alpha=self.plot_config.grid_alpha)

        # 8. Final CV quality assessment
        qc_data_subset = cv_data_final[cv_data_final[data_config.sample_type_column] == data_config.qc_identifier]
        sample_data_subset = cv_data_final[
            cv_data_final[data_config.sample_type_column] == data_config.biological_sample_identifier
        ]

        axes[1, 3].boxplot([qc_data_subset["CV"], sample_data_subset["CV"]], labels=["QC", "Sample"], patch_artist=True)
        axes[1, 3].set_ylabel("CV (%)")
        # Use the last stage name for the title
        final_stage_name = pipeline_config.stage_descriptions.get(stages[-1], stages[-1]) if stages else "Final"
        axes[1, 3].set_title(f"Final CV Quality\n({final_stage_name})", fontweight="bold")
        axes[1, 3].grid(True, alpha=self.plot_config.grid_alpha)

        plt.tight_layout()
        return fig


class FeatureAnalyzer:
    """
    Class for analyzing feature performance and characteristics with complete configurability.

    Provides comprehensive analysis capabilities for feature performance assessment,
    classification, and visualization with full configuration support.
    """

    def __init__(
        self,
        project_config: Optional[Any] = None,
        data_config: Optional[DataStructureConfig] = None,
        stats_config: Optional[StatisticalConfig] = None,
        viz_config: Optional[VisualizationConfig] = None,
        plugin_registry: Optional[PluginRegistry] = None,
    ) -> None:
        """Initialize feature analyzer with configuration injection.

        Parameters:
        -----------
        project_config : Any, optional
            Legacy project configuration (deprecated)
        data_config : DataStructureConfig, optional
            Data structure configuration
        stats_config : StatisticalConfig, optional
            Statistical configuration
        viz_config : VisualizationConfig, optional
            Visualization configuration
        plugin_registry : PluginRegistry, optional
            Plugin registry for extensibility
        """
        self.project_config = project_config
        self.data_config = data_config or DataStructureConfig()
        self.stats_config = stats_config or StatisticalConfig()
        self.viz_config = viz_config or VisualizationConfig()
        self.plugin_registry = plugin_registry or PLUGIN_REGISTRY

        # Legacy support
        self.config = project_config

    def _get_color_scheme(self, scheme_name: str) -> dict[str, str]:
        """Get color scheme from configuration."""
        return self.viz_config.color_schemes.get(
            scheme_name,
            {
                "high_performers": "darkgreen",
                "moderate_performers": "green",
                "low_performers": "lightgreen",
                "non_responders": "orange",
            },
        )

    def _get_figure_layout(self, plot_type: str) -> tuple[int, int]:
        """Get figure layout from configuration."""
        return self.viz_config.figure_layouts.get(plot_type, (12, 10))

    def classify_feature_performance(
        self,
        cv_before: np.ndarray,
        cv_after: np.ndarray,
        feature_names: list[str],
        performance_thresholds: Optional[list[tuple[float, float, str]]] = None,
    ) -> dict[str, Any]:
        """
        Classify features by their performance improvement with configurable thresholds.

        Parameters:
        -----------
        cv_before : np.ndarray
            CV values before normalization
        cv_after : np.ndarray
            CV values after normalization
        feature_names : list[str]
            Names of features
        performance_thresholds : list[tuple[float, float, str]], optional
            List of (min_threshold, max_threshold, category_name) tuples

        Returns:
        --------
        dict[str, Any]
            Dictionary with feature performance classifications
        """
        cv_improvement = cv_before - cv_after

        # Use configurable thresholds or defaults
        if performance_thresholds is None:
            performance_thresholds = [
                (10, float("inf"), "high_performers"),
                (5, 10, "moderate_performers"),
                (0, 5, "low_performers"),
                (float("-inf"), 0, "non_responders"),
            ]

        # Initialize classification dictionary
        classification: dict[str, Any] = {category: [] for _, _, category in performance_thresholds}
        classification["improvements"] = (
            cv_improvement.tolist() if hasattr(cv_improvement, "tolist") else list(cv_improvement)
        )

        # Classify features based on configurable thresholds
        for i, improvement in enumerate(cv_improvement):
            for min_thresh, max_thresh, category in performance_thresholds:
                if min_thresh < improvement <= max_thresh:
                    classification[category].append(feature_names[i])
                    break

        return classification

    def plot_feature_performance_analysis(
        self,
        classification: dict[str, Any],
        abundance_data: pd.DataFrame,
        layout_override: Optional[tuple[int, int]] = None,
        color_scheme_override: Optional[dict[str, str]] = None,
        title_override: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Create comprehensive feature performance analysis with configurable styling.

        Parameters:
        -----------
        classification : dict[str, Any]
            Feature performance classification
        abundance_data : pd.DataFrame
            Feature abundance data
        layout_override : tuple[int, int], optional
            Override figure size (width, height)
        color_scheme_override : dict[str, str], optional
            Override color scheme
        title_override : str, optional
            Override main title

        Returns:
        --------
        matplotlib.figure.Figure
            Figure showing feature performance analysis
        """
        # Get configuration values
        fig_size = layout_override or self._get_figure_layout("feature_performance_analysis")
        colors = color_scheme_override or self._get_color_scheme("performance_categories")
        main_title = title_override or "Feature Performance Analysis"

        fig, axes = plt.subplots(2, 2, figsize=fig_size)

        # 1. Performance category distribution with configurable categories
        performance_categories = [cat for cat in classification if cat != "improvements"]
        category_labels = [cat.replace("_", "\n").title() for cat in performance_categories]
        counts = [len(classification[cat]) for cat in performance_categories]
        category_colors = [colors.get(cat, f"C{i}") for i, cat in enumerate(performance_categories)]

        axes[0, 0].pie(counts, labels=category_labels, colors=category_colors, autopct="%1.1f%%", startangle=90)
        axes[0, 0].set_title("Feature Performance Distribution", fontweight="bold")

        # 2. Performance vs abundance
        all_features = []
        for cat in performance_categories:
            all_features.extend(classification[cat])

        performance_scores = []
        abundances = []

        for category, score in [
            ("high_performers", 3),
            ("moderate_performers", 2),
            ("low_performers", 1),
            ("non_responders", 0),
        ]:
            if category in classification:
                for feature in classification[category]:
                    if feature in abundance_data.columns:
                        performance_scores.append(score)
                        abundances.append(abundance_data[feature].median())

        if abundances:
            axes[0, 1].scatter(abundances, performance_scores, alpha=0.7, color="blue", s=50)
            axes[0, 1].set_xlabel("Median Abundance")
            axes[0, 1].set_ylabel("Performance Score")
            axes[0, 1].set_title("Performance vs Abundance", fontweight="bold")
            axes[0, 1].set_yticks([0, 1, 2, 3])
            axes[0, 1].set_yticklabels(["Non-Responder", "Low", "Moderate", "High"])
            axes[0, 1].grid(True, alpha=self.viz_config.style_config.get("grid_alpha", 0.3))

        # 3. Improvement distribution
        improvements = classification["improvements"]
        axes[1, 0].hist(improvements, bins=20, alpha=0.7, color="green", edgecolor="black")
        axes[1, 0].axvline(0, color="red", linestyle="--", label="No improvement")
        axes[1, 0].set_xlabel("CV Improvement (percentage points)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].set_title("CV Improvement Distribution", fontweight="bold")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=self.viz_config.style_config.get("grid_alpha", 0.3))

        # 4. Summary statistics
        axes[1, 1].text(
            0.1, 0.9, "Feature Performance Summary:", fontsize=12, fontweight="bold", transform=axes[1, 1].transAxes
        )

        y_pos = 0.8
        for category in performance_categories:
            if category in classification:
                count = len(classification[category])
                axes[1, 1].text(
                    0.1,
                    y_pos,
                    f"{category.replace('_', ' ').title()}: {count}",
                    fontsize=11,
                    transform=axes[1, 1].transAxes,
                )
                y_pos -= 0.1

        axes[1, 1].text(
            0.1,
            y_pos - 0.1,
            f"Mean improvement: {improvements.mean():.1f}pp",
            fontsize=11,
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].text(
            0.1,
            y_pos - 0.2,
            f"Median improvement: {np.median(improvements):.1f}pp",
            fontsize=11,
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].text(
            0.1,
            y_pos - 0.3,
            f"Success rate: {(improvements > 0).sum()}/{len(improvements)} ({(improvements > 0).sum() / len(improvements) * 100:.1f}%)",
            fontsize=11,
            transform=axes[1, 1].transAxes,
        )
        axes[1, 1].axis("off")

        plt.suptitle(main_title, fontsize=16, fontweight="bold")
        plt.tight_layout()
        return fig
