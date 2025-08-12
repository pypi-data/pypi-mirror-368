"""Integration utilities for the Glycowork library.

This module provides wrapper functions and utilities for integrating
with the Glycowork library for specialized glycan analysis, including
differential expression analysis and glycan motif analysis.
"""

import itertools
import logging
from typing import Any, Optional, cast

import glycowork.motif.analysis as gl_m
import pandas as pd

# Import custom exceptions
from ..utils.exceptions import GlycoworkIntegrationError

# Configure logging
logger = logging.getLogger(__name__)


class GlycoworkAnalyzer:
    """
    Provides utilities for glycan analysis using the Glycowork library.
    """

    @staticmethod
    def get_alpha_n(data_matrix: pd.DataFrame) -> float:
        """
        Get alpha N value based on the number of samples in the data matrix.

        Args:
            data_matrix (pd.DataFrame): Input data matrix.

        Returns:
            float: Alpha N value.
        """
        try:
            logger.debug(f"Computing alpha N for {data_matrix.shape[0]} samples")
            alpha_n = float(gl_m.get_alphaN(data_matrix.shape[0]))
            logger.info(f"Computed alpha N = {alpha_n}")
            return alpha_n
        except Exception as e:
            logger.exception("Failed to compute alpha N")
            raise GlycoworkIntegrationError(f"Failed to compute alpha N: {e}") from e

    @staticmethod
    def get_differential_expression(
        data_matrix_samples: pd.DataFrame,
        class_column: str = "class_final",
        sample_column: str = "sample",
        class_labels: Optional[list[str]] = None,
        prefix: str = "FT-",
    ) -> pd.DataFrame:
        """
        Get differential expression analysis results using Glycowork.

        Args:
            data_matrix_samples (pd.DataFrame): Data matrix with samples and features.
            class_column (str): Column name for class labels.
            class_labels (List[str], optional): List of two class labels. Defaults to ["Controls", "Lung Cancer"].
            prefix (str): Prefix for feature columns.

        Returns:
            pd.DataFrame: Differential expression results.
        """
        if class_labels is None:
            class_labels = ["Controls", "Lung Cancer"]
        df_glycowork, group_1, group_2 = GlycoworkAnalyzer.prepare_glycowork_data(
            data_matrix_samples, class_column, sample_column, class_labels, prefix
        )
        try:
            result = gl_m.get_differential_expression(df_glycowork, group_1, group_2)
            return cast(pd.DataFrame, result)
        except Exception as e:
            raise RuntimeError(f"Failed to compute differential expression: {e}") from e

    @staticmethod
    def compare_tuckey_glycowork(
        tuckey_df: pd.DataFrame, glycowork_df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compares and summarizes differences between Tuckey HSD and Glycowork analysis outputs.

        Args:
            tuckey_df (pd.DataFrame): DataFrame from Tuckey HSD analysis.
            glycowork_df (pd.DataFrame): DataFrame from Glycowork analysis.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]:
                - Summary DataFrame for overlapping glycans.
                - Merged DataFrame with all comparison details.
        """
        tuckey_df = GlycoworkAnalyzer._standardize_tuckey_df(tuckey_df)
        glycowork_df = GlycoworkAnalyzer._standardize_glycowork_df(glycowork_df)

        merged_df = pd.merge(
            tuckey_df,
            glycowork_df,
            on="glycan_id",
            how="outer",
            suffixes=("_tuckey", "_glycowork"),
        )

        GlycoworkAnalyzer._add_difference_columns(merged_df)

        overlapping_glycans, missing_in_tuckey, extra_in_tuckey = GlycoworkAnalyzer._identify_glycan_sets(merged_df)

        GlycoworkAnalyzer._print_comparison_summary(
            tuckey_df,
            glycowork_df,
            merged_df,
            overlapping_glycans,
            missing_in_tuckey,
            extra_in_tuckey,
        )

        summary_overlapping_glycans = GlycoworkAnalyzer._get_summary_overlapping_glycans(merged_df, overlapping_glycans)

        return summary_overlapping_glycans, merged_df

    @staticmethod
    def prepare_glycowork_data(
        data_matrix_samples: pd.DataFrame,
        class_column: str = "class_final",
        sample_column: str = "sample",
        class_labels: Optional[list[str]] = None,
        prefix: str = "FT-",
    ) -> tuple[pd.DataFrame, list[int], list[int]]:
        """
        Prepare data for Glycowork analysis.

        Args:
            data_matrix_samples (pd.DataFrame): Data matrix with samples and features.
            class_column (str): Column name for class labels.
            class_labels (List[str], optional): List of two class labels. Defaults to ["Controls", "Lung Cancer"].
            prefix (str): Prefix for feature columns.

        Returns:
            Tuple[pd.DataFrame, List[int], List[int]]: Glycowork-formatted DataFrame, indices for class 1, indices for class 2.
        """

        if class_labels is None:
            class_labels = ["Controls", "Lung Cancer"]
        try:
            class1_idx = (data_matrix_samples[data_matrix_samples[class_column] == class_labels[0]].index + 1).tolist()
            class2_idx = (data_matrix_samples[data_matrix_samples[class_column] == class_labels[1]].index + 1).tolist()
            cols = [col for col in data_matrix_samples.columns if col.startswith(prefix)]
            glycowork_df = (
                data_matrix_samples.rename(columns={sample_column: "glycan"})
                .set_index("glycan")[cols]
                .T.reset_index()
                .rename_axis(None, axis=1)
                .rename(columns={"index": "glycan"})
            )
        except Exception as e:
            raise ValueError(f"Failed to prepare Glycowork data: {e}") from e
        else:
            return glycowork_df, class1_idx, class2_idx

    @staticmethod
    def create_feature_groups(
        df: pd.DataFrame, feature_cols: list[str]
    ) -> tuple[dict[Any, int], dict[int, dict[str, Any]]]:
        """
        Create groups from combinations of feature values and map samples to group IDs.

        Args:
            df (pd.DataFrame): DataFrame containing samples and features.
            feature_cols (List[str]): List of feature column names to use for grouping.

        Returns:
            Tuple[Dict[Any, int], Dict[int, Dict[str, Any]]]:
                - sample_to_group: Dict mapping sample IDs to group IDs.
                - group_combinations: Dict mapping group IDs to feature value combinations.
        """
        feature_values = {col: sorted(df[col].unique()) for col in feature_cols}
        combinations = list(itertools.product(*[feature_values[col] for col in feature_cols]))
        sample_to_group: dict[Any, int] = {}
        group_combinations: dict[int, dict[str, Any]] = {}
        for group_id, combo in enumerate(combinations):
            group_combinations[group_id] = dict(zip(feature_cols, combo, strict=False))
            mask = pd.Series(True, index=df.index)
            for col, val in zip(feature_cols, combo, strict=False):
                mask &= df[col] == val
            matching_samples = df.index[mask].tolist()
            for sample in matching_samples:
                sample_to_group[sample] = group_id
        return sample_to_group, group_combinations

    # --- Private helper methods ---

    @staticmethod
    def _standardize_tuckey_df(tuckey_df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize Tuckey DataFrame column names and select relevant columns.
        """
        df = tuckey_df.copy()
        df = df.rename(
            columns={
                "glycan": "glycan_id",
                "adj_p_value": "tuckey_adj_p_value",
                "effect_size": "tuckey_effect_size",
            }
        )
        relevant_cols = ["glycan_id", "tuckey_adj_p_value", "tuckey_effect_size"]
        df = df[[col for col in relevant_cols if col in df.columns]]
        if len(df.columns) != len(relevant_cols):
            print("Warning: Not all expected columns found in Tuckey DataFrame after renaming.")
            print(f"Expected: {relevant_cols}, Found: {df.columns.tolist()}")
        return df

    @staticmethod
    def _standardize_glycowork_df(glycowork_df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize Glycowork DataFrame column names and select relevant columns.
        """
        df = glycowork_df.copy()
        df = df.rename(
            columns={
                "Glycan": "glycan_id",
                "corr p-val": "glycowork_adj_p_value",
                "Effect size": "glycowork_effect_size",
            }
        )
        relevant_cols = ["glycan_id", "glycowork_adj_p_value", "glycowork_effect_size"]
        df = df[[col for col in relevant_cols if col in df.columns]]
        if len(df.columns) != len(relevant_cols):
            print("Warning: Not all expected columns found in Glycowork DataFrame after renaming.")
            print(f"Expected: {relevant_cols}, Found: {df.columns.tolist()}")
        return df

    @staticmethod
    def _add_difference_columns(merged_df: pd.DataFrame) -> None:
        """
        Add columns for absolute differences in p-values and effect sizes.
        """
        if {
            "tuckey_adj_p_value",
            "glycowork_adj_p_value",
        }.issubset(merged_df.columns):
            merged_df["adj_p_value_diff"] = (merged_df["tuckey_adj_p_value"] - merged_df["glycowork_adj_p_value"]).abs()
        else:
            merged_df["adj_p_value_diff"] = pd.NA
        if {
            "tuckey_effect_size",
            "glycowork_effect_size",
        }.issubset(merged_df.columns):
            merged_df["effect_size_diff"] = (merged_df["tuckey_effect_size"] - merged_df["glycowork_effect_size"]).abs()
        else:
            merged_df["effect_size_diff"] = pd.NA

    @staticmethod
    def _identify_glycan_sets(
        merged_df: pd.DataFrame,
    ) -> tuple[list[Any], list[Any], list[Any]]:
        """
        Identify overlapping, missing, and extra glycans between Tuckey and Glycowork.
        """
        tuckey_pval_col = "tuckey_adj_p_value"
        glycowork_pval_col = "glycowork_adj_p_value"
        overlapping = merged_df[merged_df[tuckey_pval_col].notna() & merged_df[glycowork_pval_col].notna()][
            "glycan_id"
        ].tolist()
        missing_in_tuckey = merged_df[merged_df[tuckey_pval_col].isna() & merged_df[glycowork_pval_col].notna()][
            "glycan_id"
        ].tolist()
        extra_in_tuckey = merged_df[merged_df[tuckey_pval_col].notna() & merged_df[glycowork_pval_col].isna()][
            "glycan_id"
        ].tolist()
        return overlapping, missing_in_tuckey, extra_in_tuckey

    @staticmethod
    def _print_comparison_summary(
        tuckey_df: pd.DataFrame,
        glycowork_df: pd.DataFrame,
        merged_df: pd.DataFrame,
        overlapping_glycans: list[Any],
        missing_in_tuckey: list[Any],
        extra_in_tuckey: list[Any],
    ) -> None:
        """
        Print a summary of the comparison between Tuckey and Glycowork outputs.
        """
        print("--- Glycan Analysis Comparison Summary ---")
        print(f"Total unique glycans identified by Tuckey: {tuckey_df['glycan_id'].nunique()}")
        print(f"Total unique glycans identified by Glycowork: {glycowork_df['glycan_id'].nunique()}")
        print(f"Number of overlapping glycans: {len(overlapping_glycans)}")
        print(f"Number of glycans only in Glycowork (missing in Tuckey): {len(missing_in_tuckey)}")
        print(f"Number of glycans only in Tuckey (missing in Glycowork): {len(extra_in_tuckey)}")
        print("\\n--- Overlapping Glycans ---")
        if overlapping_glycans:
            print(f"List: {overlapping_glycans}")
            overlapping_df = merged_df[merged_df["glycan_id"].isin(overlapping_glycans)]
            GlycoworkAnalyzer._print_difference_stats(overlapping_df, "adj_p_value_diff", "adjusted p-values")
            GlycoworkAnalyzer._print_difference_stats(overlapping_df, "effect_size_diff", "effect sizes")
        else:
            print("No overlapping glycans found.")
        print("\\n--- Glycans only in Glycowork (missing in Tuckey) ---")
        print(f"List: {missing_in_tuckey}" if missing_in_tuckey else "No glycans found only in Glycowork output.")
        print("\\n--- Glycans only in Tuckey (missing in Glycowork) ---")
        print(f"List: {extra_in_tuckey}" if extra_in_tuckey else "No glycans found only in Tuckey output.")
        print("\\n--- Detailed Differences for Overlapping Glycans ---")
        if overlapping_glycans:
            summary_df = GlycoworkAnalyzer._get_summary_overlapping_glycans(merged_df, overlapping_glycans)
            print(summary_df.to_string())
        else:
            print("No overlapping glycans to show details for.")

    @staticmethod
    def _print_difference_stats(df: pd.DataFrame, col: str, label: str) -> None:
        """
        Print mean and median absolute differences for a given column.
        """
        if col in df.columns and df[col].notna().any():
            print(f"  Mean absolute difference in {label}: {df[col].mean():.4f}")
            print(f"  Median absolute difference in {label}: {df[col].median():.4f}")
        else:
            print(f"  {label.capitalize()} differences are not available for overlapping glycans.")

    @staticmethod
    def _get_summary_overlapping_glycans(merged_df: pd.DataFrame, overlapping_glycans: list[Any]) -> pd.DataFrame:
        """
        Get summary DataFrame for overlapping glycans.
        """
        cols_to_display = ["glycan_id"]
        for col in [
            "tuckey_adj_p_value",
            "glycowork_adj_p_value",
            "adj_p_value_diff",
            "tuckey_effect_size",
            "glycowork_effect_size",
            "effect_size_diff",
        ]:
            if col in merged_df.columns:
                cols_to_display.append(col)
        return merged_df[merged_df["glycan_id"].isin(overlapping_glycans)][cols_to_display]

    @staticmethod
    def get_significant_glycans(
        df: pd.DataFrame,
        significant_column: str = "significant",
        index_column: str = "Glycan",
    ) -> list[str]:
        significant_rows = df[df[significant_column] is True]
        result = significant_rows[index_column].astype(str).tolist()
        return cast(list[str], result)
