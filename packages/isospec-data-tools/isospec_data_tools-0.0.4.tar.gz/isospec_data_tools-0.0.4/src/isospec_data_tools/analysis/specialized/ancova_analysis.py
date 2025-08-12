"""ANCOVA analysis utilities for glycan data.

This module provides specialized ANCOVA (Analysis of Covariance) analysis
tools for glycan abundance data with covariates control.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd
from pingouin import ancova

# Import core functions
from ..core.multiple_comparisons import adjust_p_values
from ..preprocessing.validators import validate_feature_columns, validate_statistical_analysis_data

# Import custom exceptions
from ..utils.exceptions import DataValidationError, StatisticalAnalysisError

# Configure logging
logger = logging.getLogger(__name__)


class ANCOVAAnalyzer:
    """
    Specialized ANCOVA analysis tools for glycan data with covariate control.

    This class provides methods for performing ANCOVA analysis on glycan abundance
    data while controlling for covariates, with proper multiple comparison
    correction and effect size calculations.
    """

    @staticmethod
    def analyze_glycans_ancova(
        data: pd.DataFrame,
        feature_prefix: str = "FT-",
        class_column: str = "class",
        covar_columns: Optional[list[str]] = None,
        alpha: float = 0.05,
        glycan_composition_map: Optional[dict[str, str]] = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        """
        Perform ANCOVA analysis for all glycans and filter for significant class effects.

        Args:
            data (pd.DataFrame): DataFrame containing glycan abundances and metadata. Must have columns:
                - Glycan abundance columns starting with feature_prefix
                - class_column: categorical variable for group comparison
                - covar_columns: continuous covariates
            feature_prefix (str): Prefix used to identify feature columns.
            class_column (str): Name of column containing class labels.
            covar_columns (List[str], optional): List of column names to use as covariates.
                Defaults to ["age"].
            alpha (float): Significance level for filtering results.
            glycan_composition_map (Dict[str, str], optional): Dictionary mapping feature IDs
                to glycan compositions.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
                - significant_results: DataFrame with significant glycans only
                - all_results: DataFrame with all glycans analyzed
                - significant_glycans: Array of significant glycan names

        Raises:
            DataValidationError: If input data is invalid or missing required columns.
            StatisticalAnalysisError: If ANCOVA analysis fails.
        """
        if covar_columns is None:
            covar_columns = ["age"]

        logger.info(f"Starting ANCOVA analysis for {len(data)} samples with covariates: {covar_columns}")

        try:
            # Validate input data
            ANCOVAAnalyzer._validate_input_data(data, class_column, covar_columns)

            # Get glycan features
            glycan_features = ANCOVAAnalyzer._get_glycan_features(data, feature_prefix)
            if not glycan_features:
                raise DataValidationError(f"No glycan features found with prefix '{feature_prefix}'")

            logger.info(f"Found {len(glycan_features)} glycan features for analysis")

            # Perform ANCOVA for each glycan
            results = []
            for glycan in glycan_features:
                try:
                    result = ANCOVAAnalyzer._analyze_single_glycan(
                        data, glycan, class_column, covar_columns, glycan_composition_map
                    )
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Error analyzing glycan {glycan}: {e}")
                    continue

            if not results:
                raise StatisticalAnalysisError("No valid ANCOVA results obtained")

            # Convert results to DataFrame
            results_df = pd.DataFrame(results)

            # Adjust p-values for multiple comparisons
            results_df["class_adj_p_value"] = ANCOVAAnalyzer._adjust_p_values(results_df["class_p_value"], alpha)

            # Add group statistics to all results
            ANCOVAAnalyzer._add_group_statistics(results_df, data, class_column)

            # Filter for significant class effects
            significant_results = results_df[results_df["class_adj_p_value"] < alpha].sort_values("class_adj_p_value")

            logger.info(f"Found {len(significant_results)} significant glycans after ANCOVA analysis")

            return (
                significant_results,
                results_df,
                significant_results.glycan.unique(),
            )

        except Exception as e:
            logger.exception("ANCOVA analysis failed")
            raise StatisticalAnalysisError(f"ANCOVA analysis failed: {e}") from e

    @staticmethod
    def _validate_input_data(data: pd.DataFrame, class_column: str, covar_columns: list[str]) -> None:
        """Validate input data for ANCOVA analysis."""
        validate_statistical_analysis_data(data, class_column, covar_columns)

    @staticmethod
    def _get_glycan_features(data: pd.DataFrame, feature_prefix: str) -> list[str]:
        """Extract glycan feature column names from data."""
        return validate_feature_columns(data, feature_prefix, min_features=1)

    @staticmethod
    def _adjust_p_values(p_values: pd.Series, alpha: float) -> pd.Series:
        """Adjust p-values using Benjamini-Hochberg method."""
        return adjust_p_values(p_values, alpha)

    @staticmethod
    def _analyze_single_glycan(
        data: pd.DataFrame,
        glycan: str,
        class_column: str,
        covar_columns: list[str],
        glycan_composition_map: Optional[dict[str, str]] = None,
    ) -> Optional[dict]:
        """
        Analyze a single glycan using ANCOVA.

        Args:
            data (pd.DataFrame): Input data.
            glycan (str): Glycan column name.
            class_column (str): Class column name.
            covar_columns (List[str]): Covariate column names.
            glycan_composition_map (Dict[str, str], optional): Glycan composition mapping.

        Returns:
            Optional[Dict]: ANCOVA results dictionary or None if analysis fails.
        """
        try:
            # Run ANCOVA
            ancova_result = ancova(data=data, dv=glycan, covar=covar_columns, between=class_column)

            # Extract class effect
            class_effect = ancova_result.loc[ancova_result["Source"] == class_column].iloc[0]

            result_dict = {
                "glycan": glycan,
                "class_p_value": class_effect["p-unc"],
                "class_effect_size": class_effect["np2"],  # partial eta squared
            }

            # Add glycan composition if mapping provided
            if glycan_composition_map and glycan in glycan_composition_map:
                result_dict["glycan_composition"] = glycan_composition_map[glycan]

            # Add effects for each covariate
            for covar in covar_columns:
                covar_effect = ancova_result.loc[ancova_result["Source"] == covar].iloc[0]
                result_dict[f"{covar}_p_value"] = covar_effect["p-unc"]
                result_dict[f"{covar}_effect_size"] = covar_effect["np2"]

            return result_dict

        except Exception as e:
            logger.debug(f"ANCOVA failed for glycan {glycan}: {e}")
            return None

    @staticmethod
    def _add_group_statistics(results_df: pd.DataFrame, data: pd.DataFrame, class_column: str) -> None:
        """Add group statistics (means, fold changes) to results DataFrame."""
        if results_df.empty:
            return

        for _, row in results_df.iterrows():
            glycan = row["glycan"]
            class_means = data.groupby(class_column)[glycan].mean()
            max_fold_change = class_means.max() / class_means.min() if class_means.min() > 0 else np.nan

            results_df.loc[results_df["glycan"] == glycan, "max_fold_change"] = max_fold_change

            # Add mean abundance per class as separate columns
            for class_name in data[class_column].unique():
                results_df.loc[
                    results_df["glycan"] == glycan,
                    f"mean_{class_name}",
                ] = data[data[class_column] == class_name][glycan].mean()

    @staticmethod
    def get_significant_glycans(
        results_df: pd.DataFrame,
        alpha: float = 0.05,
        adj_p_column: str = "class_adj_p_value",
    ) -> list[str]:
        """
        Extract list of significant glycans from ANCOVA results.

        Args:
            results_df (pd.DataFrame): ANCOVA results DataFrame.
            alpha (float): Significance threshold.
            adj_p_column (str): Column name for adjusted p-values.

        Returns:
            List[str]: List of significant glycan names.
        """
        significant_glycans = results_df[results_df[adj_p_column] < alpha]["glycan"].tolist()
        logger.info(f"Found {len(significant_glycans)} significant glycans at α={alpha}")
        return significant_glycans

    @staticmethod
    def get_top_glycans(
        results_df: pd.DataFrame,
        n_top: int = 10,
        sort_by: str = "class_adj_p_value",
        ascending: bool = True,
    ) -> pd.DataFrame:
        """
        Get top N glycans from ANCOVA results.

        Args:
            results_df (pd.DataFrame): ANCOVA results DataFrame.
            n_top (int): Number of top glycans to return.
            sort_by (str): Column name to sort by.
            ascending (bool): Sort order.

        Returns:
            pd.DataFrame: Top N glycans results.
        """
        return results_df.sort_values(sort_by, ascending=ascending).head(n_top)

    @staticmethod
    def calculate_covariate_effects(
        results_df: pd.DataFrame,
        covar_columns: list[str],
        alpha: float = 0.05,
    ) -> dict[str, int]:
        """
        Calculate number of glycans significantly affected by each covariate.

        Args:
            results_df (pd.DataFrame): ANCOVA results DataFrame.
            covar_columns (List[str]): List of covariate column names.
            alpha (float): Significance threshold.

        Returns:
            Dict[str, int]: Dictionary mapping covariate names to counts of significant glycans.
        """
        covariate_effects = {}

        for covar in covar_columns:
            p_column = f"{covar}_p_value"
            if p_column in results_df.columns:
                significant_count = (results_df[p_column] < alpha).sum()
                covariate_effects[covar] = significant_count
                logger.info(f"Covariate '{covar}' significantly affects {significant_count} glycans")

        return covariate_effects
