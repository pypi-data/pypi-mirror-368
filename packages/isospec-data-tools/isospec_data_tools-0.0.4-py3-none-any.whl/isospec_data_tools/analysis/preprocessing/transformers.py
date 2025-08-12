"""Data transformation utilities for analysis preparation.

This module provides data transformation functions including log transformations,
scaling, encoding, and other data preparation operations.
"""

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

# Import custom exceptions and validation functions
from ..utils.data_helpers import _get_numeric_columns, _validate_dataframe
from ..utils.exceptions import DataValidationError

# Configure logging
logger = logging.getLogger(__name__)


def log2_transform_numeric(
    df: pd.DataFrame, prefix: Optional[str] = None, inplace: bool = False
) -> Optional[pd.DataFrame]:
    """
    Apply log2 transformation to numeric columns (memory optimized).

    Args:
        df: Input DataFrame
        prefix: Optional prefix to filter columns. If None, all numeric columns are transformed
        inplace: If True, modify the DataFrame in place to save memory (default: False)

    Returns:
        DataFrame with log2-transformed numeric columns (or None if inplace=True)

    Raises:
        DataValidationError: If data is invalid or no numeric columns found

    Example:
        >>> df = pd.DataFrame({'FT1': [1, 2, 4], 'FT2': [8, 16, 32], 'meta': ['A', 'B', 'C']})
        >>> transformed = log2_transform_numeric(df, prefix='FT')
        >>> print(transformed)
           FT1   FT2 meta
        0  0.0   3.0    A
        1  1.0   4.0    B
        2  2.0   5.0    C

        # Memory-efficient version for large datasets:
        >>> log2_transform_numeric(df, prefix='FT', inplace=True)
    """
    logger.info(f"Applying log2 transformation with prefix: {prefix}")

    _validate_dataframe(df)

    numeric_cols = _get_numeric_columns(df, prefix)

    if len(numeric_cols) == 0:
        logger.error("No numeric columns found for transformation")
        raise DataValidationError("No numeric columns found for transformation")

    # Memory optimization: use inplace processing or copy
    df_logged = df if inplace else df.copy()

    try:
        # Handle negative or zero values by adding small constant
        for col in numeric_cols:
            min_val = df_logged[col].min()
            if min_val <= 0:
                offset = abs(min_val) + 1e-10
                df_logged[col] = df_logged[col] + offset
                logger.warning(f"Added offset {offset} to column {col} to handle non-positive values")

        df_logged[numeric_cols] = np.log2(df_logged[numeric_cols])
        logger.info(f"Log2 transformation applied to {len(numeric_cols)} numeric columns")

    except Exception as e:
        logger.exception("Error during log2 transformation")
        raise DataValidationError(f"Log2 transformation failed: {e}") from e

    logger.info("Log2 transformation completed successfully")
    return None if inplace else df_logged


def encode_categorical_column(df: pd.DataFrame, column: str, mapping: Optional[dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Encode a categorical column using a mapping dictionary.

    Args:
        df: Input DataFrame
        column: Column name to encode
        mapping: Dictionary mapping original values to encoded values

    Returns:
        DataFrame with new encoded column added

    Raises:
        DataValidationError: If data is invalid, column not found, or mapping is invalid

    Example:
        >>> df = pd.DataFrame({'sex': ['M', 'F', 'M']})
        >>> result = encode_categorical_column(df, 'sex', {'M': 1, 'F': 0})
        >>> print(result)
           sex  sex_encoded
        0    M            1
        1    F            0
        2    M            1
    """
    logger.info(f"Encoding categorical column: {column}")

    _validate_dataframe(df)

    if column not in df.columns:
        logger.error(f"Column '{column}' not found in data. Available columns: {list(df.columns)}")
        raise DataValidationError(f"Column '{column}' not found in data")

    if mapping is None:
        logger.error("Mapping dictionary is required for encoding")
        raise DataValidationError("Mapping dictionary is required for encoding")

    try:
        result = df.copy()
        result[f"{column}_encoded"] = result[column].map(mapping)

        # Check for unmapped values
        unmapped = result[result[f"{column}_encoded"].isna()][column].unique()
        if len(unmapped) > 0:
            logger.warning(f"Unmapped values found in column {column}: {unmapped}")

        logger.info(f"Categorical encoding completed for column {column}")

    except Exception as e:
        logger.exception("Error during categorical encoding")
        raise DataValidationError(f"Categorical encoding failed: {e}") from e

    return result


def filter_data_by_column_value(data: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    """
    Filter data to keep only rows where a column equals a specific value.

    Args:
        data: Input DataFrame
        column: Column name to filter on
        value: Value to filter for

    Returns:
        Filtered DataFrame

    Raises:
        DataValidationError: If data is invalid or column not found

    Example:
        >>> df = pd.DataFrame({'group': ['A', 'B', 'A'], 'value': [1, 2, 3]})
        >>> filtered = filter_data_by_column_value(df, 'group', 'A')
        >>> print(filtered)
          group  value
        0     A      1
        2     A      3
    """
    logger.info(f"Filtering data where {column} = {value}")

    _validate_dataframe(data)

    if column not in data.columns:
        logger.error(f"Column '{column}' not found in data. Available columns: {list(data.columns)}")
        raise DataValidationError(f"Column '{column}' not found in data")

    try:
        filtered_data: pd.DataFrame = data[data[column] == value].copy()
        logger.info(f"Filtered to {len(filtered_data)} rows from {len(data)} original rows")
        return filtered_data

    except Exception as e:
        logger.exception("Error during data filtering")
        raise DataValidationError(f"Data filtering failed: {e}") from e


def replace_column_values(
    data: pd.DataFrame,
    column: str,
    mapping: Optional[dict[Any, Any]] = None,
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
) -> pd.DataFrame:
    """
    Replace values in a specified column.

    Args:
        data: Input DataFrame
        column: Column name to modify
        mapping: Dictionary mapping old values to new values
        old_value: Single old value to replace
        new_value: Single new value to replace with

    Returns:
        DataFrame with replaced values

    Raises:
        DataValidationError: If data is invalid, column not found, or invalid parameters

    Example:
        >>> df = pd.DataFrame({'col': ['A', 'B', 'A']})
        >>> result = replace_column_values(df, 'col', mapping={'A': 'X'})
        >>> print(result)
           col
        0   X
        1   B
        2   X
    """
    logger.info(f"Replacing values in column: {column}")

    _validate_dataframe(data)

    if column not in data.columns:
        logger.error(f"Column '{column}' not found in data. Available columns: {list(data.columns)}")
        raise DataValidationError(f"Column '{column}' not found in data")

    try:
        result = data.copy()

        if mapping is not None:
            result[column] = result[column].replace(mapping)
            logger.info(f"Applied mapping replacement for {len(mapping)} values")
        elif old_value is not None and new_value is not None:
            result[column] = result[column].replace(old_value, new_value)
            logger.info(f"Replaced '{old_value}' with '{new_value}'")
        else:
            logger.error("Must provide either mapping dict or old/new value pair")
            raise DataValidationError("Must provide either mapping dict or old/new value pair")

        logger.info("Column value replacement completed successfully")

    except Exception as e:
        logger.exception("Error during column value replacement")
        raise DataValidationError(f"Column value replacement failed: {e}") from e

    return result


def join_sample_metadata(
    data: pd.DataFrame,
    metadata: pd.DataFrame,
    sample_id_col: str = "SampleID",
    sample_join_col: str = "sample",
    metadata_cols: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Join sample metadata with data using specified columns.

    Args:
        data: Main data DataFrame
        metadata: Metadata DataFrame
        sample_id_col: Column in metadata to use as index for joining
        sample_join_col: Column in data to use for joining
        metadata_cols: List of metadata columns to include. If None, includes all

    Returns:
        DataFrame with joined metadata

    Raises:
        DataValidationError: If data is invalid or required columns missing

    Example:
        >>> data_df = pd.DataFrame({'sample': ['A', 'B'], 'value': [1, 2]})
        >>> meta_df = pd.DataFrame({'SampleID': ['A', 'B'], 'group': ['G1', 'G2']})
        >>> joined = join_sample_metadata(data_df, meta_df)
    """
    logger.info("Joining sample metadata with data")

    _validate_dataframe(data, "data")
    _validate_dataframe(metadata, "metadata")

    if sample_join_col not in data.columns:
        logger.error(f"Sample join column '{sample_join_col}' not found in data")
        raise DataValidationError(f"Sample join column '{sample_join_col}' not found in data")

    if sample_id_col not in metadata.columns:
        logger.error(f"Sample ID column '{sample_id_col}' not found in metadata")
        raise DataValidationError(f"Sample ID column '{sample_id_col}' not found in metadata")

    try:
        if metadata_cols is None:
            metadata_cols = metadata.columns.tolist()
        else:
            # Validate that all specified columns exist
            missing_cols = set(metadata_cols) - set(metadata.columns)
            if missing_cols:
                logger.error(f"Metadata columns not found: {missing_cols}")
                raise DataValidationError(f"Metadata columns not found: {missing_cols}")

        result = data.merge(
            metadata[metadata_cols].set_index(sample_id_col),
            left_on=sample_join_col,
            right_index=True,
            how="left",
            suffixes=("", "_metadata"),
        )

        logger.info(f"Metadata joining completed successfully. Added {len(metadata_cols)} metadata columns")

    except Exception as e:
        logger.exception("Error during metadata joining")
        raise DataValidationError(f"Metadata joining failed: {e}") from e

    return result
