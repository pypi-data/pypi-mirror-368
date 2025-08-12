"""Plotting utilities for method evaluation and statistical analysis.

This module provides a comprehensive set of plotting functions for analyzing
coefficient of variation (CV) distributions, group comparisons, and statistical
significance testing with visualization.
"""

from typing import Any, Optional

import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from isospec_data_tools.io_utils import save_fig


class SignificanceMarker:
    """Utility class for handling significance markers and p-value conversions."""

    @staticmethod
    def pvalue_to_marker(pvalue: float) -> str:
        """
        Convert p-value to significance marker.

        Args:
            pvalue: P-value to convert

        Returns:
            Significance marker string
        """
        if pvalue < 0.001:
            return "***"
        elif pvalue < 0.01:
            return "**"
        elif pvalue < 0.05:
            return "*"
        else:
            return "ns"


class CVAnalyzer:
    """Handles coefficient of variation calculations and analysis."""

    @staticmethod
    def compute_cv_by_sample_type(
        data: pd.DataFrame, feature_prefix: str = "FT-", sample_type_col: str = "SampleType"
    ) -> pd.DataFrame:
        """
        Compute coefficient of variation (CV) for feature columns grouped by sample type.

        Args:
            data: Input DataFrame containing sample type and feature columns
            feature_prefix: Prefix used to identify feature columns
            sample_type_col: Name of column containing sample type information

        Returns:
            DataFrame with CV values for each feature by sample type

        Raises:
            ValueError: If required columns are missing or data is empty
        """
        if data.empty:
            raise ValueError("Input DataFrame is empty")

        if sample_type_col not in data.columns:
            raise ValueError(f"Sample type column '{sample_type_col}' not found in data")

        # Get feature columns based on prefix
        feature_cols = [col for col in data.columns if col.startswith(feature_prefix)]

        if not feature_cols:
            raise ValueError(f"No feature columns found with prefix '{feature_prefix}'")

        results = []

        # Group by sample type and compute CV for each feature
        for sample_type in data[sample_type_col].unique():
            subset = data[data[sample_type_col] == sample_type]

            for col in feature_cols:
                values = subset[col].dropna()

                if len(values) < 2:
                    # Skip features with insufficient data
                    continue

                # Calculate coefficient of variation (standard deviation / mean) * 100%
                mean_val = values.mean()
                cv = (np.inf if values.std() > 0 else 0) if mean_val == 0 else (values.std() / mean_val) * 100

                results.append({sample_type_col: sample_type, "Feature": col, "CV": cv})

        return pd.DataFrame(results)

    @staticmethod
    def extract_cv(
        cv_data: pd.DataFrame, sample_type_col: str = "SampleType", sample_type: str = "Biological Sample"
    ) -> pd.Series:
        """
        Extract CV values for samples from CV data.

        Args:
            cv_data: DataFrame containing CV data with SampleType and CV columns
            sample_type: Sample type identifier to filter for (default: 'Biological Sample')

        Returns:
            Series containing CV values for biological samples

        Raises:
            ValueError: If required columns are missing or no biological samples found
        """
        if sample_type_col not in cv_data.columns or "CV" not in cv_data.columns:
            raise ValueError("CV data must contain 'SampleType' and 'CV' columns")

        biological_cv = cv_data[cv_data[sample_type_col] == sample_type]["CV"]

        if biological_cv.empty:
            raise ValueError(f"No samples found with SampleType '{sample_type}'")

        return biological_cv


class PlotStyler:
    """Handles plot styling and appearance customization."""

    @staticmethod
    def setup_seaborn_style() -> None:
        """Configure seaborn plotting style for consistent appearance."""
        sns.set_style("whitegrid")

    @staticmethod
    def remove_grid(ax: matplotlib.axes.Axes) -> None:
        """Remove grid from the plot."""
        ax.grid(False)

    @staticmethod
    def apply_despine() -> None:
        """Apply seaborn despine for cleaner appearance."""
        sns.despine()


class MethodPlotter:
    """
    Comprehensive plotting functions for method evaluation and statistical analysis.

    This class provides methods for creating various types of plots including
    CV distributions, group comparisons with statistical significance markers,
    and other analytical visualizations.
    """

    def __init__(self) -> None:
        """Initialize the plotter with default styling."""
        PlotStyler.setup_seaborn_style()

    @staticmethod
    def plot_cv(
        cv_results: pd.DataFrame,
        x_col: str = "CV",
        hue_col: str = "SampleType",
        color_mapping: Optional[dict[str, str]] = None,
        save_path: Optional[str] = None,
        figsize: tuple[int, int] = (10, 6),
    ) -> matplotlib.figure.Figure:
        """
        Plot distribution of CV values by sample type with threshold line.

        Args:
            cv_results: DataFrame containing CV data to plot
            x_col: Column name for x-axis values
            hue_col: Column name for color grouping
            color_mapping: Dictionary mapping hue values to colors
            save_path: Path to save the figure
            figsize: Figure size as (width, height) tuple

        Returns:
            The generated matplotlib figure

        Raises:
            ValueError: If required columns are missing or data is empty
        """
        if cv_results.empty:
            raise ValueError("CV results DataFrame is empty")

        required_cols = [x_col, hue_col, "Feature"]
        missing_cols = [col for col in required_cols if col not in cv_results.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        fig, ax = plt.subplots(figsize=figsize)

        # Create histogram with density curves overlaid
        sns.histplot(
            data=cv_results,
            x=x_col,
            hue=hue_col,
            alpha=0.3,
            palette=color_mapping,
            ax=ax,
            stat="count",
            common_norm=False,
            kde=True,
        )

        # Get number of features and set title
        num_features = cv_results["Feature"].nunique()
        ax.set_title(f"Distribution of CV Values by {hue_col} ({num_features} features)", fontsize=14)

        # Handle legend and threshold line
        MethodPlotter._add_cv_legend_and_threshold(ax)

        # Set axis labels
        ax.set_xlabel("Coefficient of Variation (%)", fontsize=12)
        ax.set_ylabel("Number of features", fontsize=12)

        # Apply styling
        PlotStyler.remove_grid(ax)
        PlotStyler.apply_despine()

        # Save figure if path provided
        if save_path:
            save_fig(fig, name="cv_distribution", path=save_path)

        return fig

    @staticmethod
    def _add_cv_legend_and_threshold(ax: matplotlib.axes.Axes) -> None:
        """
        Add legend and threshold line to CV plot.

        Args:
            ax: Matplotlib axes to modify
        """
        # Get existing legend
        legend = ax.get_legend()

        # Only proceed if legend exists
        if legend is not None:
            # Store existing handles and labels
            existing_handles = legend.legend_handles
            existing_labels = [text.get_text() for text in legend.get_texts()]

            # Remove existing legend
            legend.remove()

            # Add vertical threshold line at 30%
            threshold_line = ax.axvline(x=30, color="red", linestyle="--", linewidth=1.5)

            # Combine handles and labels
            all_handles = [*existing_handles, threshold_line]
            all_labels = [*existing_labels, "30% Threshold"]

            # Create new legend
            ax.legend(handles=all_handles, labels=all_labels, loc="best")

    @staticmethod
    def plot_distribution_by_groups(
        data: pd.DataFrame,
        test_results: Optional[dict[str, list[dict[str, Any]]]] = None,
        value_column: str = "age",
        group_column: str = "class_final",
        binary_column: str = "sex",
        figsize: tuple[int, int] = (6, 6),
        title: Optional[str] = "Age Distribution by Condition and Sex",
        save_path: Optional[str] = None,
        y_max: Optional[float] = None,
        binary_labels: Optional[list[str]] = None,
        value_label: Optional[str] = None,
        group_label: Optional[str] = None,
    ) -> matplotlib.figure.Figure:
        """
        Create boxplot showing distribution by groups with binary split and significance lines.

        Args:
            data: DataFrame containing the data
            test_results: Dictionary containing statistical test results
            value_column: Name of column containing continuous values
            group_column: Name of column containing group categories
            binary_column: Name of column containing binary split
            figsize: Figure size as (width, height) tuple
            title: Plot title
            save_path: Path to save the plot
            y_max: Maximum y-axis value
            binary_labels: Labels for binary split
            value_label: Label for y-axis
            group_label: Label for x-axis

        Returns:
            The generated matplotlib figure

        Raises:
            ValueError: If required columns are missing or data is empty
        """
        if data.empty:
            raise ValueError("Input DataFrame is empty")

        required_cols = [value_column, group_column, binary_column]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Set default labels
        binary_labels = binary_labels or ["Group 1", "Group 2"]
        value_label = value_label or value_column
        group_label = group_label or group_column

        # Create figure with seaborn context
        with sns.plotting_context("notebook", font_scale=1.2):
            fig, ax = plt.subplots(figsize=figsize)

            # Create the main plot
            MethodPlotter._create_group_boxplot(data, value_column, group_column, binary_column, ax)

            # Add significance markers if test results provided
            if test_results:
                MethodPlotter._add_significance_markers(data, test_results, value_column, group_column, ax)

            # Customize plot appearance
            MethodPlotter._customize_group_plot(
                ax, title, value_label, group_label, binary_column, binary_labels, y_max
            )

            # Adjust layout and save
            plt.tight_layout()

            if save_path:
                save_fig(fig, name="distribution_by_groups", path=save_path)

            return fig

    @staticmethod
    def _create_group_boxplot(
        data: pd.DataFrame, value_column: str, group_column: str, binary_column: str, ax: matplotlib.axes.Axes
    ) -> None:
        """
        Create the main boxplot with individual points.

        Args:
            data: DataFrame containing the data
            value_column: Name of value column
            group_column: Name of group column
            binary_column: Name of binary column
            ax: Matplotlib axes to plot on
        """
        # Create boxplot
        sns.boxplot(x=group_column, y=value_column, hue=binary_column, data=data, width=0.6, linewidth=1.5, ax=ax)

        # Add individual points
        sns.swarmplot(
            x=group_column,
            y=value_column,
            hue=binary_column,
            data=data,
            dodge=True,
            size=4,
            palette="dark:.3",
            alpha=0.6,
            legend=False,
            ax=ax,
        )

    @staticmethod
    def _add_significance_markers(
        data: pd.DataFrame,
        test_results: dict[str, list[dict[str, Any]]],
        value_column: str,
        group_column: str,
        ax: matplotlib.axes.Axes,
    ) -> None:
        """
        Add significance markers to the plot.

        Args:
            data: DataFrame containing the data
            test_results: Dictionary containing test results
            value_column: Name of value column
            group_column: Name of group column
            ax: Matplotlib axes to add markers to
        """
        # Convert group column to string type
        data_copy = data.copy()
        data_copy[group_column] = data_copy[group_column].astype(str)

        # Calculate positioning parameters
        y_max_data = data_copy[value_column].max()
        y_range = data_copy[value_column].max() - data_copy[value_column].min()
        base_height = y_max_data + 0.05 * y_range
        height_increment = 0.08 * y_range

        # Add between-group significance markers
        MethodPlotter._add_between_group_markers(
            test_results.get("between_group", []), data_copy, group_column, base_height, height_increment, y_range, ax
        )

        # Add within-group significance markers
        MethodPlotter._add_within_group_markers(
            test_results.get("within_group", []), data_copy, group_column, base_height, y_range, ax
        )

    @staticmethod
    def _add_between_group_markers(
        between_results: list[dict[str, Any]],
        data: pd.DataFrame,
        group_column: str,
        base_height: float,
        height_increment: float,
        y_range: float,
        ax: matplotlib.axes.Axes,
    ) -> None:
        """
        Add between-group significance markers.

        Args:
            between_results: List of between-group test results
            data: DataFrame containing the data
            group_column: Name of group column
            base_height: Base height for markers
            height_increment: Height increment between markers
            y_range: Range of y values
            ax: Matplotlib axes to add markers to
        """
        # Sort results by significance and control group priority
        sorted_results = sorted(
            between_results,
            key=lambda x: ("Controls" in (x.get("group1", ""), x.get("group2", "")), x.get("p_value", 1.0)),
            reverse=True,
        )

        current_height = base_height
        unique_groups = sorted(data[group_column].unique())

        for result in sorted_results:
            if result.get("p_value", 1.0) < 0.05:
                group1 = result.get("group1", "")
                group2 = result.get("group2", "")

                if group1 in unique_groups and group2 in unique_groups:
                    group1_idx = unique_groups.index(group1)
                    group2_idx = unique_groups.index(group2)

                    # Draw the line
                    ax.plot([group1_idx, group2_idx], [current_height, current_height], "-k", linewidth=1.5)

                    # Add significance marker
                    marker = SignificanceMarker.pvalue_to_marker(result.get("p_value", 1.0))
                    ax.text(
                        (group1_idx + group2_idx) / 2,
                        current_height + 0.01 * y_range,
                        marker,
                        ha="center",
                        va="bottom",
                        fontsize=12,
                    )

                    current_height += height_increment

    @staticmethod
    def _add_within_group_markers(
        within_results: list[dict[str, Any]],
        data: pd.DataFrame,
        group_column: str,
        base_height: float,
        y_range: float,
        ax: matplotlib.axes.Axes,
    ) -> None:
        """
        Add within-group significance markers.

        Args:
            within_results: List of within-group test results
            data: DataFrame containing the data
            group_column: Name of group column
            base_height: Base height for markers
            y_range: Range of y values
            ax: Matplotlib axes to add markers to
        """
        within_height = base_height - 0.05 * y_range
        unique_groups = sorted(data[group_column].unique())

        for result in within_results:
            if result.get("p_value", 1.0) < 0.05:
                group = result.get("group", "")

                if group in unique_groups:
                    group_idx = unique_groups.index(group)
                    marker = SignificanceMarker.pvalue_to_marker(result.get("p_value", 1.0))

                    # Draw shorter vertical lines for within-group comparisons
                    x_left = group_idx - 0.2
                    x_right = group_idx + 0.2
                    ax.plot([x_left, x_right], [within_height, within_height], "-k", linewidth=1.5)
                    ax.plot([x_left, x_left], [within_height - 0.02 * y_range, within_height], "-k", linewidth=1.5)
                    ax.plot([x_right, x_right], [within_height - 0.02 * y_range, within_height], "-k", linewidth=1.5)

                    # Add significance marker
                    ax.text(group_idx, within_height + 0.01 * y_range, marker, ha="center", va="bottom", fontsize=12)

    @staticmethod
    def _customize_group_plot(
        ax: matplotlib.axes.Axes,
        title: Optional[str],
        value_label: str,
        group_label: str,
        binary_column: str,
        binary_labels: list[str],
        y_max: Optional[float],
    ) -> None:
        """
        Customize the appearance of the group plot.

        Args:
            ax: Matplotlib axes to customize
            title: Plot title
            value_label: Label for y-axis
            group_label: Label for x-axis
            binary_column: Name of binary column
            binary_labels: Labels for binary groups
            y_max: Maximum y-axis value
        """
        # Remove grid
        PlotStyler.remove_grid(ax)

        # Set labels and title
        ax.set_xlabel(group_label, fontsize=14)
        ax.set_ylabel(value_label, fontsize=14)

        if title:
            ax.set_title(title, fontsize=16, pad=20)

        # Set y-axis limit
        if y_max:
            ax.set_ylim(top=y_max)

        # Update legend
        handles = ax.get_legend_handles_labels()[0][:2]
        ax.legend(
            handles,
            binary_labels,
            title=binary_column.capitalize(),
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            title_fontsize=14,
            fontsize=12,
        )


# Backward compatibility aliases
def plot_cv(*args: Any, **kwargs: Any) -> matplotlib.figure.Figure:
    """Backward compatibility function for plot_cv."""
    return MethodPlotter.plot_cv(*args, **kwargs)


def plot_distribution_by_groups(*args: Any, **kwargs: Any) -> matplotlib.figure.Figure:
    """Backward compatibility function for plot_distribution_by_groups."""
    return MethodPlotter.plot_distribution_by_groups(*args, **kwargs)


def compute_cv_by_sample_type(*args: Any, **kwargs: Any) -> pd.DataFrame:
    """Backward compatibility function for compute_cv_by_sample_type."""
    return CVAnalyzer.compute_cv_by_sample_type(*args, **kwargs)


def add_significance_markers(pvalue: float) -> str:
    """Backward compatibility function for add_significance_markers."""
    return SignificanceMarker.pvalue_to_marker(pvalue)
