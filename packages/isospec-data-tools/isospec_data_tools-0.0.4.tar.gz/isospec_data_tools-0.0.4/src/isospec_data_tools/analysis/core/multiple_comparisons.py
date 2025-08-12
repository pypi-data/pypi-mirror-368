"""Multiple comparison corrections and p-value adjustments.

This module provides various methods for controlling family-wise error rate
and false discovery rate when performing multiple statistical tests.
"""

import logging
from typing import Union

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[np.ndarray, pd.Series]


def adjust_p_values(p_values: Union[ArrayLike, list[float]], alpha: float = 0.05, method: str = "fdr_bh") -> pd.Series:
    """Adjust p-values for multiple comparisons.

    Supports various methods for controlling family-wise error rate (FWER)
    or false discovery rate (FDR) when performing multiple statistical tests.

    Args:
        p_values: Array or Series of p-values to adjust
        alpha: Significance level for testing
        method: Correction method. Options include:
            - 'bonferroni': Bonferroni correction (FWER control)
            - 'holm': Holm-Bonferroni correction (FWER control)
            - 'fdr_bh': Benjamini-Hochberg FDR correction (default)
            - 'fdr_by': Benjamini-Yekutieli FDR correction
            - 'sidak': Sidak correction (FWER control)

    Returns:
        Series of adjusted p-values with same index as input

    Raises:
        ValueError: If invalid method or p-values provided

    Example:
        >>> p_vals = pd.Series([0.01, 0.05, 0.1, 0.2, 0.3])
        >>> adjusted = adjust_p_values(p_vals, alpha=0.05, method='fdr_bh')
        >>> significant = adjusted < 0.05
    """
    # Convert input to pandas Series if needed
    if isinstance(p_values, list | np.ndarray):
        p_values = pd.Series(p_values)
    elif not isinstance(p_values, pd.Series):
        raise TypeError("p_values must be a list, numpy array, or pandas Series")

    # Validate p-values
    if p_values.empty:
        logger.warning("Empty p-values provided")
        return pd.Series(dtype=float)

    if p_values.isna().any():
        logger.warning("NaN values found in p-values - they will be preserved")

    if (p_values < 0).any() or (p_values > 1).any():
        invalid_count = ((p_values < 0) | (p_values > 1)).sum()
        logger.warning(f"Found {invalid_count} p-values outside [0,1] range")

    # Validate method
    valid_methods = ["bonferroni", "holm", "fdr_bh", "fdr_by", "sidak"]
    if method not in valid_methods:
        raise ValueError(f"Method '{method}' not supported. Choose from: {valid_methods}")

    # Remove NaN values for correction, then restore them
    mask = p_values.notna()
    valid_p_values = p_values[mask]

    if len(valid_p_values) == 0:
        logger.warning("No valid p-values to adjust")
        return p_values.copy()

    # Perform correction
    try:
        _, adjusted_pvalues, _, _ = multipletests(valid_p_values, alpha=alpha, method=method, returnsorted=False)

        # Create result series with same index as input
        result = pd.Series(index=p_values.index, dtype=float)
        result[mask] = adjusted_pvalues
        result[~mask] = np.nan  # Restore NaN values

        logger.info(f"Adjusted {len(valid_p_values)} p-values using {method} method")
        logger.debug(f"Significant after correction: {(result < alpha).sum()}")

        return result

    except Exception as e:
        logger.exception("Failed to adjust p-values using %s", method)
        raise ValueError(f"P-value adjustment failed: {e}") from e


def calculate_q_values(p_values: ArrayLike) -> np.ndarray:
    """Calculate q-values (local false discovery rates) from p-values.

    Q-values provide the expected proportion of false positives among
    all features at least as significant as the observed one.

    Args:
        p_values: Array of p-values

    Returns:
        Array of q-values

    Example:
        >>> p_vals = np.array([0.001, 0.01, 0.05, 0.1, 0.2])
        >>> q_vals = calculate_q_values(p_vals)
    """
    p_values = np.asarray(p_values)

    if len(p_values) == 0:
        return np.array([])

    # Sort p-values and track original order
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]
    m = len(p_values)

    # Calculate q-values
    q_values = np.zeros_like(sorted_p)
    q_values[-1] = sorted_p[-1]  # Last q-value equals last p-value

    for i in range(m - 2, -1, -1):
        q_values[i] = min(sorted_p[i] * m / (i + 1), q_values[i + 1])

    # Restore original order
    original_order = np.empty_like(sorted_indices)
    original_order[sorted_indices] = np.arange(m)

    return q_values[original_order]


def bonferroni_correction(p_values: ArrayLike, alpha: float = 0.05) -> tuple[np.ndarray, float]:
    """Apply Bonferroni correction for multiple comparisons.

    The Bonferroni correction controls the family-wise error rate by
    dividing the significance level by the number of tests.

    Args:
        p_values: Array of p-values to correct
        alpha: Desired family-wise error rate

    Returns:
        Tuple of (significant_tests, corrected_alpha)

    Example:
        >>> p_vals = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
        >>> significant, alpha_corr = bonferroni_correction(p_vals, alpha=0.05)
    """
    p_values = np.asarray(p_values)

    if len(p_values) == 0:
        return np.array([], dtype=bool), alpha

    corrected_alpha = alpha / len(p_values)
    significant = p_values < corrected_alpha

    logger.info(f"Bonferroni correction: {significant.sum()}/{len(p_values)} tests significant")
    logger.debug(f"Corrected alpha: {corrected_alpha:.6f}")

    return significant, corrected_alpha
