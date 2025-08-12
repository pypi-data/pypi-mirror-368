"""Utility functions for SST validation metrics.

This module provides common utility functions used across different metric validators
for data preparation, validation, and result handling.
"""

from typing import Any

import pandas as pd

from .base import BaseMetricResult, ValidationResult


def initialize_validation_result(metric_results: list[BaseMetricResult]) -> ValidationResult:
    """Initialize a ValidationResult object with the provided metric results.

    Args:
        results: List of individual metric results to aggregate

    Returns:
        A ValidationResult object containing all provided results
    """
    return ValidationResult(results=metric_results)


def find_matching_features(
    data: pd.DataFrame,
    mz_query: float | None = None,
    rt_query: float | None = None,
    mz_tolerance: float = 0.01,
    rt_tolerance: float = 0.1,
) -> pd.DataFrame:
    """Find features within the defined mass-to-charge and retention time tolerance.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing feature data with 'mz' and 'rt' columns
    mz_query : float, optional
        Mass-to-charge value to search. If not provided, matches all m/z values.
    rt_query : float, optional
        Retention time value to search. If not provided, matches all RT values.
    mz_tolerance : float
        Mass-to-charge tolerance used in the search.
    rt_tolerance : float
        Retention time tolerance used in the search.

    Returns
    -------
    pd.DataFrame
        DataFrame containing matched features

    Raises
    ------
    ValueError
        If required columns are missing or data is invalid
    """
    if "mz" not in data.columns or "rt" not in data.columns:
        raise ValueError("Data must contain 'mz' and 'rt' columns")

    if mz_query is not None:
        mz_match = (data["mz"] - mz_query).abs() < mz_tolerance
        result = data[mz_match]
    else:
        result = data

    if rt_query is not None:
        rt_match = (result["rt"] - rt_query).abs() < rt_tolerance
        result = result[rt_match]

    return result


def validate_input_data(data: pd.DataFrame, required_columns: list[str]) -> None:
    """Validate input data meets requirements for metric calculation.

    Args:
        data: Input DataFrame to validate
        required_columns: List of column names that must be present
        numeric_columns: List of columns that must contain numeric data
        min_rows: Minimum number of rows required

    Raises:
        ValueError: If any validation checks fail
    """
    # Check DataFrame is not empty
    if data is None or data.empty:
        raise ValueError("Input data cannot be None or empty")

    # Check required columns exist
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")


def format_error_message(metric_name: str, error_type: str, details: dict[str, Any]) -> str:
    """Format an error message for metric validation failures.

    Args:
        metric_name: Name of the metric that failed
        error_type: Type of error that occurred
        details: Additional details about the error

    Returns:
        Formatted error message string
    """
    error_msg = f"[{metric_name}] {error_type}"
    if details:
        error_msg += ": " + ", ".join(f"{k}={v}" for k, v in details.items())
    return error_msg
