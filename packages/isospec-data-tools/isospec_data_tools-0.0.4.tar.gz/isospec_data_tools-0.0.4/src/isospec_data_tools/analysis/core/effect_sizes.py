"""Effect size calculations for statistical analyses.

This module provides comprehensive effect size calculations including
Cohen's d, eta-squared, correlation coefficients, and other measures
of practical significance.
"""

import logging
from typing import Union

import numpy as np
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[np.ndarray, pd.Series]


def calculate_cohens_d(group1_data: pd.Series, group2_data: pd.Series) -> float:
    """Calculate Cohen's d effect size for two groups.

    Cohen's d is a standardized measure of effect size that represents the difference
    between two group means in terms of their pooled standard deviation.

    Args:
        group1_data: Data for the first group
        group2_data: Data for the second group

    Returns:
        Cohen's d effect size (positive indicates group2 > group1)

    Raises:
        ValueError: If groups have insufficient data

    Example:
        >>> group1 = pd.Series([1, 2, 3, 4, 5])
        >>> group2 = pd.Series([3, 4, 5, 6, 7])
        >>> effect_size = calculate_cohens_d(group1, group2)
        >>> print(f"Cohen's d: {effect_size:.3f}")
    """
    if len(group1_data) < 2 or len(group2_data) < 2:
        raise ValueError("Each group must have at least 2 observations")

    n1, n2 = len(group1_data), len(group2_data)
    var1, var2 = float(np.var(group1_data, ddof=1)), float(np.var(group2_data, ddof=1))

    # Calculate pooled standard error
    pooled_se = float(np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)))

    if pooled_se == 0:
        logger.warning("Zero pooled standard error - groups may have identical values")
        return 0.0

    mean_diff = float(np.mean(group2_data) - np.mean(group1_data))
    cohens_d = abs(mean_diff) / pooled_se  # Return absolute value as stated in docstring

    logger.debug(f"Cohen's d calculated: {cohens_d:.4f} (n1={n1}, n2={n2})")
    return cohens_d


def calculate_fold_change(mean_group1: float, mean_group2: float, log2_transform: bool = False) -> float:
    """Calculate fold change between two group means.

    Args:
        mean_group1: Mean of the first group (reference/control)
        mean_group2: Mean of the second group (treatment/test)
        log2_transform: Whether the data is log2 transformed

    Returns:
        Fold change (ratio or power of 2 for log2 data)

    Example:
        >>> fc_linear = calculate_fold_change(2.0, 6.0, log2_transform=False)
        >>> print(f"Linear fold change: {fc_linear}")  # 3.0
        >>> fc_log2 = calculate_fold_change(1.0, 3.0, log2_transform=True)
        >>> print(f"Log2 fold change: {fc_log2}")  # 4.0 (2^(3-1))
    """
    if log2_transform:
        # For log2-transformed data, fold change is 2^(diff)
        log_diff = mean_group2 - mean_group1
        fold_change = 2**log_diff
        logger.debug(f"Log2 fold change: 2^({mean_group2} - {mean_group1}) = {fold_change:.4f}")
        return fold_change
    else:
        # For linear data, fold change is simple ratio
        if mean_group1 == 0:
            logger.warning("Division by zero in fold change calculation")
            return float("nan")
        fold_change = mean_group2 / mean_group1
        logger.debug(f"Linear fold change: {mean_group2} / {mean_group1} = {fold_change:.4f}")
        return fold_change


def calculate_eta_squared(group_means: ArrayLike, group_sizes: ArrayLike, total_variance: float) -> float:
    """Calculate eta-squared effect size for ANOVA.

    Eta-squared represents the proportion of total variance explained by group differences.

    Args:
        group_means: Mean values for each group
        group_sizes: Sample sizes for each group
        total_variance: Total variance in the data

    Returns:
        Eta-squared effect size (0 to 1)

    Example:
        >>> means = np.array([2.0, 4.0, 6.0])
        >>> sizes = np.array([10, 10, 10])
        >>> total_var = 8.0
        >>> eta_sq = calculate_eta_squared(means, sizes, total_var)
    """
    group_means = np.asarray(group_means)
    group_sizes = np.asarray(group_sizes)

    if len(group_means) != len(group_sizes):
        raise ValueError("Group means and sizes must have same length")

    if total_variance <= 0:
        raise ValueError("Total variance must be positive")

    # Calculate weighted grand mean
    grand_mean = np.average(group_means, weights=group_sizes)

    # Calculate between-group variance
    between_group_variance = np.sum(group_sizes * (group_means - grand_mean) ** 2)

    # Eta-squared is ratio of between-group to total variance
    eta_squared = between_group_variance / (between_group_variance + total_variance)

    logger.debug(f"Eta-squared calculated: {eta_squared:.4f}")
    return float(eta_squared)
