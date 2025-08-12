"""
Plotting utilities for confounder analysis.

This module provides functions for visualizing the relationship between glycans
and confounders, including scatter plots, regression lines, and statistical
analysis.
"""

from __future__ import annotations

import math
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import levene
from statsmodels.formula.api import ols

from isospec_data_tools.io_utils import save_fig

# Constants
DEFAULT_ALPHA = 0.05
DEFAULT_FIGSIZE = (8, 6)
DEFAULT_PLOTS_PER_ROW = 3
DEFAULT_PLOTS_PER_PAGE = 6
MIN_P_VALUE = 1e-10
SIGNIFICANCE_LEVELS = {0.001: "***", 0.01: "**", 0.05: "*"}
DEFAULT_COVAR_COLUMNS = ["sex", "age"]
DEFAULT_CLASS_COLUMN = "class_final"


class PlotConfig:
    """Configuration class for plotting parameters."""

    def __init__(
        self,
        figsize: tuple[int, int] = DEFAULT_FIGSIZE,
        alpha: float = DEFAULT_ALPHA,
        plots_per_row: int = DEFAULT_PLOTS_PER_ROW,
        plots_per_page: int = DEFAULT_PLOTS_PER_PAGE,
        scatter_alpha: float = 0.5,
        line_color: str = "red",
        cmap: str = "Blues",
        text_fontsize: int = 8,
    ):
        self.figsize = figsize
        self.alpha = alpha
        self.plots_per_row = plots_per_row
        self.plots_per_page = plots_per_page
        self.scatter_alpha = scatter_alpha
        self.line_color = line_color
        self.cmap = cmap
        self.text_fontsize = text_fontsize


class StatisticalAnalyzer:
    """Handles statistical calculations and tests."""

    @staticmethod
    def calculate_correlation_and_pvalue(x: pd.Series, y: pd.Series) -> tuple[float, float]:
        """Calculate Pearson correlation and p-value between two series."""
        try:
            correlation, p_value = stats.pearsonr(x, y)
            return float(correlation), float(p_value)
        except ValueError as e:
            raise ValueError(f"Error calculating correlation: {e}") from e

    @staticmethod
    def get_significance_stars(p_value: float) -> str:
        """Get significance stars based on p-value."""
        for threshold, stars in sorted(SIGNIFICANCE_LEVELS.items()):
            if p_value < threshold:
                return stars
        return ""

    @staticmethod
    def perform_normality_test(residuals: pd.Series) -> float:
        """Perform Shapiro-Wilk normality test on residuals."""
        try:
            # Explicitly cast the p-value to float since shapiro returns a tuple of Any
            _, p_value = stats.shapiro(residuals)
            return float(p_value)
        except ValueError as e:
            raise ValueError(f"Error in normality test: {e}") from e

    @staticmethod
    def perform_variance_test(residuals: pd.Series, groups: pd.Series) -> float:
        """Perform Levene's test for variance homogeneity."""
        try:
            grouped_residuals = [group for _, group in residuals.groupby(groups)]
            return float(levene(*grouped_residuals)[1])
        except ValueError as e:
            raise ValueError(f"Error in variance test: {e}") from e


class DataValidator:
    """Validates input data and parameters."""

    @staticmethod
    def validate_dataframe(data: pd.DataFrame, required_columns: list[str]) -> None:
        """Validate that DataFrame contains required columns."""
        missing_cols = set(required_columns) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    @staticmethod
    def validate_feature_names(features: list[str], data: pd.DataFrame) -> None:
        """Validate that all features exist in the data."""
        missing_features = set(features) - set(data.columns)
        if missing_features:
            raise ValueError(f"Features not found in data: {missing_features}")

    @staticmethod
    def validate_alpha(alpha: float) -> None:
        """Validate significance level."""
        if not 0 < alpha < 1:
            raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")


class PlotHelper:
    """Helper methods for common plotting operations."""

    @staticmethod
    def create_subplot_grid(n_items: int, plots_per_row: int = DEFAULT_PLOTS_PER_ROW) -> tuple[plt.Figure, np.ndarray]:
        """Create a subplot grid with appropriate dimensions."""
        n_cols = min(plots_per_row, n_items)
        n_rows = math.ceil(n_items / plots_per_row)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows))

        if n_rows == 1 and n_cols == 1:
            axes = np.array([axes])

        return fig, axes.flatten()

    @staticmethod
    def cleanup_unused_subplots(axes: np.ndarray, used_count: int) -> None:
        """Remove unused subplots from the grid."""
        for idx in range(used_count, len(axes)):
            axes[idx].set_visible(False)

    @staticmethod
    def get_display_name(feature: str, feature_names_dict: Optional[dict[str, str]]) -> str:
        """Get display name for a feature."""
        if feature_names_dict and feature in feature_names_dict:
            return feature_names_dict[feature]
        return feature

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by replacing problematic characters."""
        return filename.replace("/", "_").replace("\\", "_")

    @staticmethod
    def get_abundance_label(log_transformed: bool) -> str:
        """Get appropriate y-axis label based on transformation."""
        return "Log2 Normalized Abundance" if log_transformed else "Normalized Abundance"


class ConfounderPlotter:
    """Main class for creating confounder analysis plots."""

    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()
        self.validator = DataValidator()
        self.stats = StatisticalAnalyzer()
        self.helper = PlotHelper()

    def visualize_confounders(
        self, results: dict[str, dict[str, list]], alpha: Optional[float] = None, path: Optional[str] = None
    ) -> Optional[plt.Figure]:
        """
        Visualize the relationship between glycans and confounders.

        Args:
            results: Results dictionary from analyze_confounders
            alpha: Significance threshold (uses config default if None)
            path: Optional path to save the figure

        Returns:
            Figure object if created, None if no results

        Raises:
            ValueError: If results are invalid or empty
        """
        if not results:
            print("No results to visualize")
            return None

        alpha = alpha or self.config.alpha
        self.validator.validate_alpha(alpha)

        n_confounders = len(results)
        glycan_cols = results[next(iter(results))]["glycans"]

        fig, axes = self.helper.create_subplot_grid(n_confounders)

        for i, (confounder, res) in enumerate(results.items()):
            self._plot_confounder_summary(axes[i], confounder, res, glycan_cols, alpha)

        self.helper.cleanup_unused_subplots(axes, n_confounders)
        plt.tight_layout(w_pad=3)

        if path:
            save_fig(fig, name="confounders_plot", path=path)

        plt.close()
        return fig

    def _plot_confounder_summary(
        self, ax: plt.Axes, confounder: str, res: dict[str, Any], glycan_cols: list[str], alpha: float
    ) -> None:
        """Create a single confounder summary plot."""
        # Transform p-values for visualization
        neg_log_p = -np.log10([max(p, MIN_P_VALUE) for p in res["adj_p_values"]])

        # Determine effect measure type
        effect_measure, effect_label, effect_abs = self._get_effect_measure(res)

        # Create scatter plot
        scatter = ax.scatter(
            range(len(glycan_cols)),
            neg_log_p,
            s=50,
            c=effect_abs,
            alpha=0.7,
            cmap=self.config.cmap,
            vmin=0,
            vmax=max(max(effect_abs), 0.05),
        )

        # Add threshold line and customize
        ax.axhline(-np.log10(alpha), color="black", linestyle="--")
        ax.set_title(confounder.capitalize())
        ax.set_xlabel("Glycans")
        ax.set_ylabel("-log₁₀ p")
        ax.set_xticks([])

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(effect_label)

    def _get_effect_measure(self, res: dict[str, Any]) -> tuple[list[float], str, list[float]]:
        """Determine whether to use correlation or effect size."""
        correlations = res.get("correlations", [])
        effect_sizes = res.get("effect_sizes", [])

        # Check if correlations are meaningful
        has_correlations = any(c != 0 and not np.isnan(c) for c in correlations)

        if has_correlations:
            effect_measure = correlations
            effect_label = "|Coef. Corr.|"
            effect_abs = [abs(c) if not np.isnan(c) else 0 for c in effect_measure]
        else:
            effect_measure = effect_sizes
            effect_label = "|Cohen's d|"
            effect_abs = [e if not np.isnan(e) else 0 for e in effect_measure]

        return effect_measure, effect_label, effect_abs

    def create_single_confounding_plot(
        self,
        data: pd.DataFrame,
        feature: str,
        confounder: str,
        feature_names_dict: Optional[dict[str, str]] = None,
        ax: Optional[plt.Axes] = None,
        figsize: Optional[tuple[int, int]] = None,
        log: bool = True,
        hue: Optional[str] = None,
    ) -> tuple[Optional[plt.Figure], plt.Axes]:
        """
        Create a single confounding plot for one feature against a confounder.

        Args:
            data: Data matrix containing features and metadata
            feature: Feature name to plot
            confounder: Name of the confounding variable to plot against
            feature_names_dict: Dictionary mapping feature IDs to display names
            ax: Axes object to plot on (creates new figure if None)
            figsize: Figure size if creating new figure
            log: Whether the data is log transformed
            hue: Column name to use for color-coding the points

        Returns:
            Tuple of (figure object if created, axes object)

        Raises:
            ValueError: If required columns are missing
        """
        # Validate inputs
        required_cols = [feature, confounder]
        if hue:
            required_cols.append(hue)
        self.validator.validate_dataframe(data, required_cols)

        # Create figure if needed
        fig = None
        if ax is None:
            figsize = figsize or self.config.figsize
            fig, ax = plt.subplots(figsize=figsize)

        # Get display name and filter valid data
        display_name = self.helper.get_display_name(feature, feature_names_dict)
        valid_data = data[~data[confounder].isna()]

        if len(valid_data) < 3:
            raise ValueError(f"Insufficient valid data for {feature} vs {confounder}")

        # Create the plot
        self._create_scatter_with_regression(valid_data, feature, confounder, ax, hue)

        # Add statistics
        self._add_statistics_to_plot(valid_data, feature, confounder, ax)

        # Set labels
        self._set_plot_labels(ax, display_name, confounder, log)

        return fig, ax

    def _create_scatter_with_regression(
        self, data: pd.DataFrame, feature: str, confounder: str, ax: plt.Axes, hue: Optional[str]
    ) -> None:
        """Create scatter plot with regression line."""
        if hue is not None:
            sns.scatterplot(data=data, x=confounder, y=feature, hue=hue, alpha=self.config.scatter_alpha, ax=ax)
            sns.regplot(
                data=data, x=confounder, y=feature, scatter=False, line_kws={"color": self.config.line_color}, ax=ax
            )
        else:
            sns.regplot(
                data=data,
                x=confounder,
                y=feature,
                scatter_kws={"alpha": self.config.scatter_alpha},
                line_kws={"color": self.config.line_color},
                ax=ax,
            )

    def _add_statistics_to_plot(self, data: pd.DataFrame, feature: str, confounder: str, ax: plt.Axes) -> None:
        """Add correlation statistics to the plot."""
        try:
            correlation, p_value = self.stats.calculate_correlation_and_pvalue(data[confounder], data[feature])

            stats_text = f"r = {correlation:.3f}\np = {p_value:.2e}"
            stats_text += self.stats.get_significance_stars(p_value)

            ax.text(
                0.05,
                0.95,
                stats_text,
                transform=ax.transAxes,
                verticalalignment="top",
                bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
            )
        except ValueError as e:
            print(f"Warning: Could not calculate statistics: {e}")

    def _set_plot_labels(self, ax: plt.Axes, display_name: str, confounder: str, log: bool) -> None:
        """Set plot labels and title."""
        # Set x-label
        if confounder == "age":
            ax.set_xlabel("Age (years)")
        else:
            ax.set_xlabel(confounder.capitalize())

        # Set y-label
        abundance_label = self.helper.get_abundance_label(log)
        ax.set_ylabel(f"{display_name}\n{abundance_label}")

        # Set title
        ax.set_title(f"{display_name} vs {confounder.capitalize()}")

    def plot_confounding_features(
        self,
        data: pd.DataFrame,
        confounded_features: list[str],
        confounder: str = "age",
        feature_names_dict: Optional[dict[str, str]] = None,
        save_path: Optional[str] = None,
        log: bool = True,
        hue: Optional[str] = None,
    ) -> plt.Figure:
        """
        Plot confounding features against a specified confounder.

        Args:
            data: Data matrix containing features and metadata
            confounded_features: List of feature names that are confounded
            confounder: Name of the confounding variable to plot against
            feature_names_dict: Dictionary mapping feature IDs to display names
            save_path: Directory path to save individual plots
            log: Whether the data is log transformed
            hue: Column name to use for color-coding the points

        Returns:
            Figure object containing the plot

        Raises:
            ValueError: If features are not found in data
        """
        if not confounded_features:
            raise ValueError("No features provided for plotting")

        self.validator.validate_feature_names(confounded_features, data)

        # Create subplot grid
        fig, axes = self.helper.create_subplot_grid(len(confounded_features), self.config.plots_per_row)

        # Plot each feature
        for idx, feature in enumerate(confounded_features):
            try:
                self.create_single_confounding_plot(
                    data, feature, confounder, feature_names_dict=feature_names_dict, ax=axes[idx], log=log, hue=hue
                )
            except Exception as e:
                print(f"Warning: Could not plot {feature}: {e}")
                axes[idx].text(
                    0.5, 0.5, f"Error plotting {feature}", ha="center", va="center", transform=axes[idx].transAxes
                )

        # Clean up unused subplots
        self.helper.cleanup_unused_subplots(axes, len(confounded_features))
        plt.tight_layout()

        # Save individual plots if requested
        if save_path:
            self._save_individual_plots(data, confounded_features, confounder, feature_names_dict, save_path, log, hue)

        plt.close()
        return fig

    def _save_individual_plots(
        self,
        data: pd.DataFrame,
        features: list[str],
        confounder: str,
        feature_names_dict: Optional[dict[str, str]],
        save_path: str,
        log: bool,
        hue: Optional[str],
    ) -> None:
        """Save individual plots for each feature."""
        for feature in features:
            try:
                display_name = self.helper.get_display_name(feature, feature_names_dict)
                fig_single, _ = self.create_single_confounding_plot(
                    data, feature, confounder, feature_names_dict=feature_names_dict, log=log, hue=hue
                )

                safe_filename = self.helper.sanitize_filename(display_name)
                save_fig(fig_single, name=f"{safe_filename}_vs_{confounder}", path=save_path)
                plt.close(fig_single)
            except Exception as e:
                print(f"Warning: Could not save plot for {feature}: {e}")

    def plot_confounded_features_by_variable(
        self,
        confounded_features: pd.DataFrame,
        data: pd.DataFrame,
        variable: str,
        feature_names_dict: Optional[dict[str, str]] = None,
        save_path: Optional[str] = None,
        hue: Optional[str] = None,
    ) -> plt.Figure:
        """
        Plot confounded features for a specific variable of interest.

        Args:
            confounded_features: DataFrame containing confounding analysis results
            data: DataFrame containing the data to plot
            variable: Variable of interest (e.g. 'age')
            feature_names_dict: Dictionary mapping feature names to display names
            save_path: Optional path to save plots
            hue: Optional column name to use for color-coding points

        Returns:
            Figure object containing the plot
        """
        # Filter confounded features for specified variable
        filtered_features = confounded_features[confounded_features["confounder"] == variable]

        if filtered_features.empty:
            raise ValueError(f"No confounded features found for variable: {variable}")

        # Plot confounded features
        return self.plot_confounding_features(
            data,
            filtered_features.feature.tolist(),
            confounder=variable,
            feature_names_dict=feature_names_dict,
            save_path=save_path,
            hue=hue,
        )

    def plot_all_glycans_assumptions(
        self,
        data: pd.DataFrame,
        glycan_features: list[str],
        class_column: str = DEFAULT_CLASS_COLUMN,
        covar_columns: list[str] = DEFAULT_COVAR_COLUMNS,
        plots_per_page: Optional[int] = None,
        feature_mapping: Optional[dict[str, str]] = None,
        path: Optional[str] = None,
    ) -> Optional[plt.Figure]:
        """
        Create diagnostic plots for all glycans, organized in pages.

        Args:
            data: DataFrame containing the data
            glycan_features: List of glycan column names to analyze
            class_column: Name of the class/group column
            covar_columns: List of covariate column names
            plots_per_page: Number of glycans to show per page
            feature_mapping: Dictionary mapping feature IDs to display names
            path: Optional path to save the figure

        Returns:
            Figure object if created, None if no glycans

        Raises:
            ValueError: If required columns are missing
        """
        if not glycan_features:
            print("No glycan features provided")
            return None

        # Validate inputs
        required_cols = [class_column, *covar_columns, *glycan_features]
        self.validator.validate_dataframe(data, required_cols)

        plots_per_page = plots_per_page or self.config.plots_per_page
        n_glycans = len(glycan_features)
        n_pages = math.ceil(n_glycans / plots_per_page)

        for page in range(n_pages):
            fig = self._create_assumptions_page(
                data, glycan_features, class_column, covar_columns, plots_per_page, feature_mapping, page, n_pages
            )

            if path:
                save_fig(fig, name=f"glycan_assumptions_page_{page + 1}", path=path)
                plt.close(fig)

            self._print_detailed_results(
                data, glycan_features, class_column, covar_columns, feature_mapping, page, plots_per_page, n_pages
            )

            if not path:
                plt.close(fig)

        return fig

    def _create_assumptions_page(
        self,
        data: pd.DataFrame,
        glycan_features: list[str],
        class_column: str,
        covar_columns: list[str],
        plots_per_page: int,
        feature_mapping: Optional[dict[str, str]],
        page: int,
        n_pages: int,
    ) -> plt.Figure:
        """Create a single page of assumption plots."""
        start_idx = page * plots_per_page
        end_idx = min((page + 1) * plots_per_page, len(glycan_features))
        page_glycans = glycan_features[start_idx:end_idx]

        fig = plt.figure(figsize=(20, 3 * len(page_glycans)))

        for i, glycan in enumerate(page_glycans):
            try:
                self._create_glycan_assumption_plots(
                    data, glycan, class_column, covar_columns, feature_mapping, i, len(page_glycans)
                )
            except Exception as e:
                print(f"Warning: Could not create assumption plots for {glycan}: {e}")

        plt.tight_layout()
        plt.subplots_adjust(left=0.15)

        return fig

    def _create_glycan_assumption_plots(
        self,
        data: pd.DataFrame,
        glycan: str,
        class_column: str,
        covar_columns: list[str],
        feature_mapping: Optional[dict[str, str]],
        plot_index: int,
        total_plots: int,
    ) -> None:
        """Create assumption plots for a single glycan."""
        # Fit the model
        formula = f"Q('{glycan}') ~ C(Q('{class_column}')) + {' + '.join(covar_columns)}"
        model = ols(formula, data=data).fit()
        residuals = model.resid
        fitted_values = model.fittedvalues

        # 1. Q-Q plot
        ax1 = plt.subplot(total_plots, 4, 4 * plot_index + 1)
        stats.probplot(residuals, dist="norm", plot=ax1)
        display_name = self.helper.get_display_name(glycan, feature_mapping)
        ax1.set_title(f"Q-Q Plot\n{display_name}")

        # 2. Residuals vs Fitted
        ax2 = plt.subplot(total_plots, 4, 4 * plot_index + 2)
        ax2.scatter(fitted_values, residuals, alpha=self.config.scatter_alpha)
        ax2.axhline(y=0, color="r", linestyle="--")
        ax2.set_xlabel("Fitted values")
        ax2.set_ylabel("Residuals")
        ax2.set_title("Residuals vs Fitted")

        # 3. Scale-Location Plot
        ax3 = plt.subplot(total_plots, 4, 4 * plot_index + 3)
        standardized_residuals = residuals / np.std(residuals)
        ax3.scatter(fitted_values, np.sqrt(np.abs(standardized_residuals)), alpha=self.config.scatter_alpha)
        ax3.set_xlabel("Fitted values")
        ax3.set_ylabel("√|Std. residuals|")
        ax3.set_title("Scale-Location")

        # Remove grids
        for ax in [ax1, ax2, ax3]:
            ax.grid(False)

        # Add test results
        self._add_assumption_test_results(
            residuals, data[class_column], glycan, feature_mapping, plot_index, total_plots
        )

    def _add_assumption_test_results(
        self,
        residuals: pd.Series,
        groups: pd.Series,
        glycan: str,
        feature_mapping: Optional[dict[str, str]],
        plot_index: int,
        total_plots: int,
    ) -> None:
        """Add statistical test results to the plot."""
        try:
            sw_pval = self.stats.perform_normality_test(residuals)
            levene_pval = self.stats.perform_variance_test(residuals, groups)

            display_name = self.helper.get_display_name(glycan, feature_mapping)
            test_text = f"{display_name}:\nNormality p={sw_pval:.4f}\nVariance p={levene_pval:.4f}"

            plt.figtext(
                0.01, 0.98 - (plot_index / total_plots), test_text, fontsize=self.config.text_fontsize, va="top"
            )
        except Exception as e:
            print(f"Warning: Could not add test results for {glycan}: {e}")

    def _print_detailed_results(
        self,
        data: pd.DataFrame,
        glycan_features: list[str],
        class_column: str,
        covar_columns: list[str],
        feature_mapping: Optional[dict[str, str]],
        page: int,
        plots_per_page: int,
        n_pages: int,
    ) -> None:
        """Print detailed statistical results for the page."""
        start_idx = page * plots_per_page
        end_idx = min((page + 1) * plots_per_page, len(glycan_features))
        page_glycans = glycan_features[start_idx:end_idx]

        print(f"\nDetailed Results - Page {page + 1}/{n_pages}")
        print("=" * 50)

        for glycan in page_glycans:
            try:
                self._print_glycan_results(data, glycan, class_column, covar_columns, feature_mapping)
            except Exception as e:
                print(f"Warning: Could not print results for {glycan}: {e}")

    def _print_glycan_results(
        self,
        data: pd.DataFrame,
        glycan: str,
        class_column: str,
        covar_columns: list[str],
        feature_mapping: Optional[dict[str, str]],
    ) -> None:
        """Print detailed results for a single glycan."""
        display_name = self.helper.get_display_name(glycan, feature_mapping)
        print(f"\n{display_name}:")
        print("-" * 30)

        # Fit model and get residuals
        formula = f"Q('{glycan}') ~ C(Q('{class_column}')) + {' + '.join(covar_columns)}"
        model = ols(formula, data=data).fit()
        residuals = model.resid

        # Normality test
        sw_pval = self.stats.perform_normality_test(residuals)
        print(f"Normality test p-value: {sw_pval:.4f}")

        # Variance homogeneity test
        levene_pval = self.stats.perform_variance_test(residuals, data[class_column])
        print(f"Variance homogeneity p-value: {levene_pval:.4f}")

        # Slope homogeneity tests
        for covar in covar_columns:
            if data[covar].dtype.kind in "bifc":  # numeric types
                self._print_slope_homogeneity_results(data, glycan, class_column, covar)

    def _print_slope_homogeneity_results(self, data: pd.DataFrame, glycan: str, class_column: str, covar: str) -> None:
        """Print slope homogeneity test results."""
        try:
            formula_int = f"Q('{glycan}') ~ C(Q('{class_column}')) * {covar}"
            model_int = ols(formula_int, data=data).fit()
            int_pvals = {col: pval for col, pval in model_int.pvalues.items() if ":" in col}

            print(f"\nSlope homogeneity ({covar}):")
            for term, pval in int_pvals.items():
                print(f"  {term}: {pval:.4f}")
        except Exception as e:
            print(f"  Warning: Could not test slope homogeneity for {covar}: {e}")


# Backward compatibility: create default instance
_default_plotter = ConfounderPlotter()


# Convenience functions for backward compatibility
def visualize_confounders(
    results: dict[str, dict[str, list]], alpha: float = DEFAULT_ALPHA, path: Optional[str] = None
) -> Optional[plt.Figure]:
    """Backward compatibility function."""
    return _default_plotter.visualize_confounders(results, alpha, path)


def create_single_confounding_plot(
    data: pd.DataFrame,
    feature: str,
    confounder: str,
    feature_names_dict: Optional[dict[str, str]] = None,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[int, int] = DEFAULT_FIGSIZE,
    log: bool = True,
    hue: Optional[str] = None,
) -> tuple[Optional[plt.Figure], plt.Axes]:
    """Backward compatibility function."""
    return _default_plotter.create_single_confounding_plot(
        data, feature, confounder, feature_names_dict, ax, figsize, log, hue
    )


def plot_confounding_features(
    data: pd.DataFrame,
    confounded_features: list[str],
    confounder: str = "age",
    feature_names_dict: Optional[dict[str, str]] = None,
    save_path: Optional[str] = None,
    log: bool = True,
    hue: Optional[str] = None,
) -> plt.Figure:
    """Backward compatibility function."""
    return _default_plotter.plot_confounding_features(
        data, confounded_features, confounder, feature_names_dict, save_path, log, hue
    )


def plot_confounded_features_by_variable(
    confounded_features: pd.DataFrame,
    data: pd.DataFrame,
    variable: str,
    feature_names_dict: Optional[dict[str, str]] = None,
    save_path: Optional[str] = None,
    hue: Optional[str] = None,
) -> plt.Figure:
    """Backward compatibility function."""
    return _default_plotter.plot_confounded_features_by_variable(
        confounded_features, data, variable, feature_names_dict, save_path, hue
    )


def plot_all_glycans_assumptions(
    data: pd.DataFrame,
    glycan_features: list[str],
    class_column: str = DEFAULT_CLASS_COLUMN,
    covar_columns: list[str] = DEFAULT_COVAR_COLUMNS,
    plots_per_page: int = DEFAULT_PLOTS_PER_PAGE,
    feature_mapping: Optional[dict[str, str]] = None,
    path: Optional[str] = None,
) -> Optional[plt.Figure]:
    """Backward compatibility function."""
    return _default_plotter.plot_all_glycans_assumptions(
        data, glycan_features, class_column, covar_columns, plots_per_page, feature_mapping, path
    )
