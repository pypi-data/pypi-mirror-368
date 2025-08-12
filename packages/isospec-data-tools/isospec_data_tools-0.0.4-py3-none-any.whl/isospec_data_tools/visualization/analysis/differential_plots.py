"""
Differential expression and model evaluation plotting utilities.

This module provides comprehensive plotting functionality for differential expression
analysis and machine learning model evaluation, with support for various visualization
types including box plots, circular bar plots, volcano plots, and ROC curves.
"""

import math
from collections.abc import Sequence
from typing import Any, ClassVar, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from sklearn.metrics import confusion_matrix, roc_curve

from isospec_data_tools.io_utils import save_fig

# TODO: Add data_config to the class and use it for the plot instead of the hardcoded values


class DifferentialExpressionPlotter:
    """Plotting functions for differential expression analysis."""

    # Color palettes and constants
    DEFAULT_COLORS: ClassVar = sns.color_palette("Set2", 3)
    SIGNIFICANCE_THRESHOLDS: ClassVar[dict[float, str]] = {0.001: "***", 0.01: "**", 0.05: "*"}

    @staticmethod
    def _get_significance_symbol(p_value: float) -> str:
        """Get significance symbol based on p-value threshold."""
        for threshold, symbol in DifferentialExpressionPlotter.SIGNIFICANCE_THRESHOLDS.items():
            if p_value < threshold:
                return symbol
        return "ns"

    @staticmethod
    def _create_subplot_grid(n_glycans: int, n_cols: int = 3) -> tuple[Figure, np.ndarray]:
        """Create subplot grid for multiple glycan plots."""
        if n_glycans == 0:
            raise ValueError("No glycans to plot")

        n_rows = math.ceil(n_glycans / n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 6 * n_rows))

        # Ensure axes is always 2D array
        if n_rows == 1:
            axes = np.array([axes])
        if n_cols == 1:
            axes = axes.reshape(-1, 1)

        return fig, axes

    @staticmethod
    def _plot_single_glycan_boxplot(
        ax: Axes, data: pd.DataFrame, glycan: str, class_column: str, colors: Sequence, log_transform: bool = True
    ) -> None:
        """Create a single glycan box plot with individual data points."""
        # Create box plot without outliers
        boxplot = sns.boxplot(
            data=data,
            x=class_column,
            y=glycan,
            ax=ax,
            boxprops={"facecolor": "none"},
            showfliers=False,
        )

        # Add individual points
        sns.stripplot(
            data=data,
            x=class_column,
            y=glycan,
            ax=ax,
            palette=colors,
            alpha=0.7,
            size=4,
            jitter=True,
        )

        # Match box plot colors with strip plot
        for j, (box, color) in enumerate(zip(boxplot.artists, colors, strict=False)):
            if hasattr(box, "set_edgecolor"):
                box.set_edgecolor(color)
            if hasattr(box, "set_facecolor"):
                box.set_facecolor("none")

            # Color whiskers, caps, and median lines
            start_idx = j * 6
            end_idx = start_idx + 6
            for line in boxplot.lines[start_idx:end_idx]:
                line.set_color(color)
                if hasattr(line, "set_mfc"):
                    line.set_mfc(color)
                if hasattr(line, "set_mec"):
                    line.set_mec(color)

        # Set y-axis label
        ylabel = f"{glycan} {'log2 ' if log_transform else ''}intensity"
        ax.set_ylabel(ylabel)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    @staticmethod
    def _create_plot_title(glycan: str, row: pd.Series, value_col: str, mode: str) -> str:
        """Create title for glycan plot with optional significance information."""
        title = glycan

        if value_col and value_col in row:
            if mode == "p_value":
                p_value = row[value_col]
                significance = DifferentialExpressionPlotter._get_significance_symbol(p_value)
                title += f"\np={p_value:.2e} {significance}"
            elif mode == "effect_size":
                effect_size = row[value_col]
                title += f"\nEffect size: {effect_size:.2f}"

        return title

    @staticmethod
    def visualize_significant_glycans(
        significant_results: pd.DataFrame,
        data: pd.DataFrame,
        value_col: str = "adj_p_value",
        class_column: str = "class_final",
        feature_col: str = "glycan",
        mode: str = "p_value",
        log_transform: bool = True,
        path: Optional[str] = None,
    ) -> Optional[Figure]:
        """
        Create visualizations for significant glycans using box plots with individual data points.

        Parameters:
        -----------
        significant_results : pd.DataFrame
            Results from analyze_glycans_ancova containing significant glycans
        data : pd.DataFrame
            Original data containing glycan abundances and metadata
        value_col : str, default='adj_p_value'
            Name of the column containing p-values or effect sizes
        class_column : str, default='class_final'
            Name of the column containing class labels
        mode : str, default='p_value'
            Display mode: 'p_value' or 'effect_size'
        log_transform : bool, default=True
            Whether the data is log-transformed
        path : str, optional
            Path to save the figure. If None, figure is not saved

        Returns:
        --------
        matplotlib.figure.Figure or None
            The generated figure, or None if no significant glycans found

        Raises:
        -------
        ValueError
            If no significant glycans are found or invalid parameters provided
        """
        n_glycans = len(significant_results)
        if n_glycans == 0:
            print("No significant glycans found")
            return None

        try:
            fig, axes = DifferentialExpressionPlotter._create_subplot_grid(n_glycans)
            axes_flat = axes.flatten()

            for i, (_, row) in enumerate(significant_results.iterrows()):
                glycan = row[feature_col]
                ax = axes_flat[i]

                # Create the box plot
                DifferentialExpressionPlotter._plot_single_glycan_boxplot(
                    ax, data, glycan, class_column, DifferentialExpressionPlotter.DEFAULT_COLORS, log_transform
                )

                # Set title
                title = DifferentialExpressionPlotter._create_plot_title(glycan, row, value_col, mode)
                ax.set_title(title)

            # Hide empty subplots
            for j in range(i + 1, len(axes_flat)):
                axes_flat[j].set_visible(False)

            plt.tight_layout()

            if path:
                save_fig(fig, name="significant_glycans", path=path)
            else:
                plt.show()

            return fig

        except Exception as e:
            plt.close(fig) if "fig" in locals() else None
            raise RuntimeError(f"Error creating glycan visualization: {e}") from e

    @staticmethod
    def _normalize_bar_heights(values: np.ndarray, min_bar_length: float, max_bar_length: float) -> np.ndarray:
        """Normalize bar heights to specified range."""
        min_val = min(-1, values.min())
        max_val = values.max()

        if max_val > min_val:
            return min_bar_length + (values - min_val) / (max_val - min_val) * (max_bar_length - min_bar_length)  # type: ignore[no-any-return]
        return np.full_like(values, min_bar_length, dtype=np.float64)

    @staticmethod
    def _determine_bar_colors(
        df: pd.DataFrame,
        pval_col: str,
        value_col: str,
        alpha: float,
        fc_threshold: float,
        glycans_to_check: Optional[list[str]],
        color_scheme: dict[str, str],
    ) -> list[str]:
        """Determine colors for bars based on significance and fold change."""
        colors = []

        for p_val, val, glycan in zip(df[pval_col], df[value_col], df.index, strict=False):
            is_significant = p_val < alpha

            if glycans_to_check is not None:
                is_significant = is_significant and glycan in glycans_to_check

            if not is_significant:
                colors.append(color_scheme["non_significant"])
            else:
                if val > fc_threshold:
                    colors.append(color_scheme["up"])
                else:
                    colors.append(color_scheme["down"])

        return colors

    @staticmethod
    def _add_bar_labels(
        ax: plt.Axes,
        angles: list[float],
        heights: np.ndarray,
        df: pd.DataFrame,
        pval_col: str,
        alpha: float,
        fc_threshold: float,
        glycans_to_check: Optional[list[str]],
        label_col: str,
    ) -> None:
        """Add labels to significant bars."""
        for i, (angle, label, p_val, _val) in enumerate(
            zip(angles, df[label_col], df[pval_col], df.iloc[:, 0], strict=False)
        ):
            is_significant = p_val < alpha

            if glycans_to_check is not None:
                is_significant = is_significant and label in glycans_to_check

            if is_significant:
                # Clean label
                clean_label = str(label).replace("FT-", "")
                clean_label = "_".join(clean_label.split("_")[:-1])

                # Determine text alignment
                rotation = np.rad2deg(angle)
                alignment = "left"
                if np.pi / 2 < angle < 3 * np.pi / 2:
                    alignment = "right"
                    rotation += 180

                ax.text(
                    angle,
                    heights[i] + 0.1,
                    str(clean_label),
                    ha=alignment,
                    va="center",
                    rotation=rotation,
                    rotation_mode="anchor",
                    fontsize=8,
                )

    @staticmethod
    def circular_bar_plot(
        df: pd.DataFrame,
        value_col: str,
        label_col: str,
        pval_col: str,
        alpha: float = 0.05,
        fc_threshold: float = 0,
        color_up: str = "#FFB366",
        color_down: str = "#69b3a2",
        color_non_significant: str = "#D3D3D3",
        figsize: tuple[int, int] = (8, 8),
        title: str = "Circular Bar Plot",
        min_bar_length: float = 0.5,
        max_bar_length: float = 2.5,
        n_ticks: int = 5,
        axis_label: Optional[str] = None,
        glycans_to_check: Optional[list[str]] = None,
        path: Optional[str] = None,
    ) -> plt.Figure:
        """
        Create a circular bar plot with significance highlighting and vertical fold change scale.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame containing the data to plot
        value_col : str
            Column name for values (e.g., 'class_effect_size' or 'log2_fc')
        label_col : str
            Column name for labels (e.g., 'glycan')
        pval_col : str
            Column name for p-values (e.g., 'class_p_value' or 'p_value')
        alpha : float, default=0.05
            Significance threshold
        fc_threshold : float, default=0
            Fold change threshold to distinguish up/down regulation
        color_up : str, default='#FFB366'
            Color for upregulated significant bars
        color_down : str, default='#69b3a2'
            Color for downregulated significant bars
        color_non_significant : str, default='#D3D3D3'
            Color for non-significant bars
        figsize : Tuple[int, int], default=(8, 8)
            Figure size
        title : str, default='Circular Bar Plot'
            Plot title
        min_bar_length : float, default=0.5
            Minimum bar length
        max_bar_length : float, default=2.5
            Maximum bar length
        n_ticks : int, default=5
            Number of ticks on the radial axis
        axis_label : str, optional
            Label for the axis
        glycans_to_check : List[str], optional
            Optional list of glycans to check for significance
        path : str, optional
            Path to save the figure

        Returns:
        --------
        matplotlib.figure.Figure
            The generated circular bar plot
        """
        try:
            # Sort for aesthetics
            df = df.sort_values(value_col, ascending=False).reset_index(drop=True)
            N = len(df)
            angles = np.linspace(0.0, 2.0 * np.pi, N, endpoint=False).tolist()

            # Normalize heights
            heights = DifferentialExpressionPlotter._normalize_bar_heights(
                df[value_col].to_numpy(), min_bar_length, max_bar_length
            )

            # Determine colors
            color_scheme = {
                "up": color_up,
                "down": color_down,
                "non_significant": color_non_significant,
            }

            colors = DifferentialExpressionPlotter._determine_bar_colors(
                df, pval_col, value_col, alpha, fc_threshold, glycans_to_check, color_scheme
            )

            # Create plot
            fig, ax = plt.subplots(figsize=figsize, subplot_kw={"polar": True})

            bars = ax.bar(
                x=angles,
                height=heights,
                width=2 * np.pi / N * 0.9,
                bottom=0,
                color=colors,
                edgecolor="white",
                linewidth=1,
                alpha=0.8,
            )

            # Add labels
            DifferentialExpressionPlotter._add_bar_labels(
                ax,
                angles,  # type: ignore[arg-type]
                heights,
                df,
                pval_col,
                alpha,
                fc_threshold,
                glycans_to_check,
                label_col,
            )

            # Add radial scale
            min_val = min(-1, df[value_col].min())
            max_val = df[value_col].max()
            tick_vals = np.linspace(min_val, max_val, n_ticks)
            tick_heights = min_bar_length + (tick_vals - min_val) / (max_val - min_val) * (
                max_bar_length - min_bar_length
            )

            ax.set_yticks(tick_heights)
            ax.set_yticklabels([f"{v:.2f}" for v in tick_vals], fontsize=10)
            ax.yaxis.grid(True, color="gray", linestyle="dashed", alpha=0.5)
            if hasattr(ax, "set_rlabel_position"):
                ax.set_rlabel_position(90)

            ax.set_xticks([])
            ax.xaxis.grid(False)
            ax.set_axisbelow(True)
            plt.title(title, y=1.08)

            # Add legend
            legend_elements = []
            if any(p < alpha for p in df[pval_col]):
                legend_elements.extend([
                    Patch(facecolor=color_up, edgecolor="white", label=f"Upregulated (p < {np.round(alpha, 2)})"),
                    Patch(facecolor=color_down, edgecolor="white", label=f"Downregulated (p < {np.round(alpha, 2)})"),
                ])

            legend_elements.append(
                Patch(
                    facecolor=color_non_significant,
                    edgecolor="white",
                    label=f"Non-significant (p ≥ {np.round(alpha, 2)})",
                )
            )

            ax.legend(handles=legend_elements, loc="center left", bbox_to_anchor=(1.2, 0.5))

            # Add axis label
            if axis_label is None:
                axis_label = value_col
            fig.text(0.5, 0.92, axis_label, va="center", ha="center", fontsize=10, fontweight="bold")

            plt.tight_layout()

            if path:
                save_fig(fig, name="circular_bar_plot", path=path)

            return fig

        except Exception as e:
            plt.close(fig) if "fig" in locals() else None
            raise RuntimeError(f"Error creating circular bar plot: {e}") from e

    @staticmethod
    def _transform_effect_size(
        df: pd.DataFrame, effect_col: str, effect_is_fold_change: bool, effect_threshold: float, log_transform: bool
    ) -> tuple[pd.Series, str, float, float]:
        """Transform effect size and return appropriate labels and thresholds."""
        if effect_is_fold_change:
            df["effect"] = np.log2(df[effect_col]) if log_transform else df[effect_col]
            effect_label = "log2(Fold Change)" if log_transform else "Fold Change"
            transformed_threshold = np.log2(effect_threshold)  # Default threshold
            negative_threshold = -np.log2(effect_threshold)
        else:
            df["effect"] = df[effect_col]
            effect_label = "Cohen's d"
            transformed_threshold = effect_threshold
            negative_threshold = -effect_threshold

        return df["effect"], effect_label, transformed_threshold, negative_threshold

    @staticmethod
    def _create_significance_categories(
        df: pd.DataFrame, p_value_col: str, p_threshold: float, transformed_threshold: float, negative_threshold: float
    ) -> pd.Series:
        """Create significance categories for volcano plot."""
        significance = pd.Series("Not Significant", index=df.index)

        significant_up = (df[p_value_col] < p_threshold) & (df["effect"] > transformed_threshold)
        significant_down = (df[p_value_col] < p_threshold) & (df["effect"] < negative_threshold)

        significance[significant_up] = f"Up-regulated (p < {p_threshold:.2f})"
        significance[significant_down] = f"Down-regulated (p < {p_threshold:.2f})"

        return significance

    @staticmethod
    def create_volcano_plot(
        data: pd.DataFrame,
        p_value_col: str = "adj_p_value",
        effect_col: str = "fold_change",
        log_transform: bool = False,
        feature_col: str = "glycan_composition",
        p_threshold: float = 0.05,
        effect_threshold: float = 1.2,
        effect_is_fold_change: bool = True,
        figure_size: tuple[int, int] = (10, 8),
        point_size: int = 60,
        text_offset: float = 0.1,
        path: Optional[str] = None,
        y_limit: Optional[float] = None,
        x_range: Optional[tuple[float, float]] = None,
        y_range: Optional[tuple[float, float]] = None,
        legend_position: str = "upper right",
    ) -> plt.Figure:
        """
        Create a volcano plot from statistical test results.

        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame containing the statistical test results
        p_value_col : str, default='adj_p_value'
            Column name for p-values
        effect_col : str, default='fold_change'
            Column name for effect size values
        log_transform : bool, default=False
            Whether to log-transform fold change values
        feature_col : str, default='glycan_composition'
            Column name for feature identifiers
        p_threshold : float, default=0.05
            P-value significance threshold
        effect_threshold : float, default=1.2
            Effect size significance threshold
        effect_is_fold_change : bool, default=True
            Whether the effect size is a fold change
        figure_size : Tuple[int, int], default=(10, 8)
            Size of the figure (width, height)
        point_size : int, default=60
            Size of scatter points
        text_offset : float, default=0.1
            Offset for text labels
        path : str, optional
            Path to save the figure
        y_limit : float, optional
            Upper limit for y-axis

        Returns:
        --------
        matplotlib.figure.Figure
            The generated volcano plot
        """
        try:
            df = data.copy()

            # Calculate -log10(p-value)
            df["log_pvalue"] = -np.log10(df[p_value_col])

            # Transform effect size
            effect_series, effect_label, transformed_threshold, negative_threshold = (
                DifferentialExpressionPlotter._transform_effect_size(
                    df, effect_col, effect_is_fold_change, effect_threshold, log_transform
                )
            )
            df["effect"] = effect_series

            # Create significance categories
            df["Significance"] = DifferentialExpressionPlotter._create_significance_categories(
                df, p_value_col, p_threshold, transformed_threshold, negative_threshold
            )

            # Create color mapping
            color_map = {
                f"Up-regulated (p < {p_threshold:.2f})": "green",
                f"Down-regulated (p < {p_threshold:.2f})": "red",
                "Not Significant": "grey",
            }

            # Create the plot
            fig = plt.figure(figsize=figure_size)

            # Create scatter plot
            sns.scatterplot(data=df, x="effect", y="log_pvalue", hue="Significance", palette=color_map, s=point_size)

            # Move legend to top right
            plt.legend(title="Significance", loc=legend_position)

            # Add feature labels for significant
            significant_features = df[
                df["Significance"].isin([
                    f"Up-regulated (p < {p_threshold:.2f})",
                    f"Down-regulated (p < {p_threshold:.2f})",
                ])
            ]

            for idx, row in significant_features.iterrows():
                # Clean label
                label = row[feature_col].replace("FT-", "")
                label = label.rsplit("_", 1)[0]
                plt.annotate(
                    label + " ",
                    (row["effect"], row["log_pvalue"]),
                    xytext=(text_offset + 5, text_offset + 5),
                    textcoords="offset points",
                    fontsize=8,
                    ha="left",
                    va="bottom",
                    rotation=45 if isinstance(idx, int) and idx % 2 == 0 else 0,
                )

            # Customize the plot
            plt.xlabel(effect_label)
            plt.ylabel("-log10(Adjusted P-value)")
            plt.title("Volcano Plot of Differential Expression")
            plt.grid(False)

            # Add threshold lines
            plt.axhline(y=-np.log10(p_threshold), color="gray", linestyle="--", alpha=0.5)
            plt.axvline(x=transformed_threshold, color="gray", linestyle="--", alpha=0.5)
            plt.axvline(x=negative_threshold, color="gray", linestyle="--", alpha=0.5)

            # Set y-axis limit if provided
            if y_range is not None:
                plt.ylim(y_range)
            if x_range is not None:
                plt.xlim(x_range)

            if path:
                save_fig(fig, name="volcano", path=path)

            return fig

        except Exception as e:
            plt.close(fig) if "fig" in locals() else None
            raise RuntimeError(f"Error creating volcano plot: {e}") from e


class ModelPlotter:
    """Plotting functions for model evaluation."""

    @staticmethod
    def _calculate_roc_curves(
        fold_data: dict[str, list[dict[str, Any]]], model_name: str
    ) -> tuple[list[np.ndarray], list[float], np.ndarray]:
        """Calculate ROC curves and AUCs for all folds."""
        tprs = []
        aucs = []
        mean_fpr = np.linspace(0, 1, 100)
        n_folds = len(fold_data[model_name])

        for i in range(n_folds):
            fold = fold_data[model_name][i]
            test_score = fold["metrics"]["roc_auc"]
            aucs.append(test_score)

            y_true = fold["y_true"]
            y_prob = fold["y_prob"][:, 1]

            fpr, tpr, _ = roc_curve(y_true, y_prob)
            tprs.append(np.interp(mean_fpr, fpr, tpr))
            tprs[-1][0] = 0.0

        return tprs, aucs, mean_fpr

    @staticmethod
    def plot_roc_curves_all_folds(
        fold_data: dict[str, list[dict[str, Any]]], model_name: str, path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create ROC curves figure for all folds of a single model.

        Parameters:
        -----------
        fold_data : Dict[str, List[Dict[str, Any]]]
            Dictionary containing fold-specific predictions for each model
        model_name : str
            Name of the model to plot
        path : str, optional
            Path to save the figure

        Returns:
        --------
        matplotlib.figure.Figure
            Figure containing ROC curves plot
        """
        try:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111)

            # Calculate ROC curves
            tprs, aucs, mean_fpr = ModelPlotter._calculate_roc_curves(fold_data, model_name)
            n_folds = len(fold_data[model_name])

            # Plot individual fold curves
            for i in range(n_folds):
                fold = fold_data[model_name][i]
                test_score = fold["metrics"]["roc_auc"]
                y_true = fold["y_true"]
                y_prob = fold["y_prob"][:, 1]

                fpr, tpr, _ = roc_curve(y_true, y_prob)
                ax.plot(fpr, tpr, lw=1, alpha=0.7, label=f"Fold {i + 1} (AUC = {test_score:.2f})")

            # Plot mean ROC curve
            mean_tpr = np.mean(tprs, axis=0)
            mean_tpr[-1] = 1.0
            mean_auc = np.mean(aucs)
            std_auc = np.std(aucs)

            ax.plot(
                mean_fpr, mean_tpr, color="b", label=f"Mean ROC (AUC = {mean_auc:.2f} ± {std_auc:.2f})", lw=2, alpha=0.8
            )

            # Plot chance line
            ax.plot([0, 1], [0, 1], "k--", lw=2)
            ax.set_xlim((0.0, 1.0))
            ax.set_ylim((0.0, 1.05))
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_title(f"ROC Curves for {model_name} Across All Folds")
            ax.legend(loc="lower right")
            ax.grid(True)

            if path:
                save_fig(fig, name=f"roc_curves_{model_name}", path=path)

            return fig

        except Exception as e:
            plt.close(fig) if "fig" in locals() else None
            raise RuntimeError(f"Error creating ROC curves plot: {e}") from e

    @staticmethod
    def plot_confusion_matrix(
        fold_data: dict[str, list[dict[str, Any]]], model_name: str, fold_idx: int = 0, path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot confusion matrix for a specific model and fold.

        Parameters:
        -----------
        fold_data : Dict[str, List[Dict[str, Any]]]
            Dictionary containing fold-specific predictions
        model_name : str
            Name of the model to plot
        fold_idx : int, default=0
            Index of the fold to plot
        path : str, optional
            Path to save the figure

        Returns:
        --------
        matplotlib.figure.Figure
            The generated confusion matrix plot
        """
        try:
            fold = fold_data[model_name][fold_idx]
            y_true = fold["y_true"]
            y_pred = fold["y_pred"]

            cm = confusion_matrix(y_true, y_pred)
            fig = plt.figure(figsize=(8, 6))

            sns.heatmap(
                cm,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=["Not Sick", "Sick"],
                yticklabels=["Not Sick", "Sick"],
            )

            plt.title(f"Confusion Matrix - {model_name} (Fold {fold_idx + 1})")
            plt.ylabel("Actual")
            plt.xlabel("Predicted")

            if path:
                save_fig(fig, name=f"confusion_matrix_{model_name}_fold{fold_idx}", path=path)

            return fig

        except Exception as e:
            if "fig" in locals():
                plt.close(fig)
            raise RuntimeError(f"Error creating confusion matrix plot: {e}") from e
