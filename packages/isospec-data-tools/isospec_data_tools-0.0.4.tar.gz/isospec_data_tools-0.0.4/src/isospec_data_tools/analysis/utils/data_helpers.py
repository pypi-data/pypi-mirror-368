"""Common data manipulation and helper utilities.

This module provides shared utility functions for data manipulation,
feature extraction, column operations, and other common tasks used
throughout the analysis pipeline.
"""

import logging
from typing import Optional, Union

import numpy as np
import pandas as pd

from ..utils.exceptions import DataValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[np.ndarray, pd.Series]
DataFrame = pd.DataFrame
Series = pd.Series


def _get_numeric_columns(data: pd.DataFrame, prefix: Optional[str] = None) -> list[str]:
    """
    Get numeric columns, optionally filtered by prefix.

    Args:
        data: Input DataFrame
        prefix: Optional prefix to filter columns

    Returns:
        List of numeric column names
    """
    numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()
    if prefix:
        numeric_cols = [col for col in numeric_cols if col.startswith(prefix)]
    return numeric_cols


def _validate_dataframe(data: pd.DataFrame, name: str = "data") -> None:
    """
    Validate that input is a non-empty DataFrame.

    Args:
        data: DataFrame to validate
        name: Name of the parameter for error messages

    Raises:
        DataValidationError: If data is not a DataFrame or is empty
    """
    if not isinstance(data, pd.DataFrame):
        raise DataValidationError(f"{name} must be a pandas DataFrame, got {type(data)}")

    if data.empty:
        raise DataValidationError(f"{name} cannot be empty")


def get_feature_columns(data: pd.DataFrame, prefix: str) -> list[str]:
    """Extract feature columns based on prefix.

    Args:
        data: Input DataFrame
        prefix: Column prefix to filter by

    Returns:
        List of column names that start with the prefix

    Raises:
        ValueError: If no columns match the prefix
    """
    feature_cols = [col for col in data.columns if col.startswith(prefix)]
    if not feature_cols:
        raise ValueError(f"No columns found with prefix '{prefix}'")
    return feature_cols


def get_numeric_columns(data: pd.DataFrame, prefix: Optional[str] = None) -> list[str]:
    """Get numeric columns, optionally filtered by prefix.

    Args:
        data: Input DataFrame
        prefix: Optional prefix to filter columns

    Returns:
        List of numeric column names
    """
    numeric_cols = data.select_dtypes(include=["float64", "int64"]).columns.tolist()
    if prefix:
        numeric_cols = [col for col in numeric_cols if col.startswith(prefix)]
    return numeric_cols


# Placeholder for additional helper functions to be added
# TODO: Move common utility functions from various analysis modules
