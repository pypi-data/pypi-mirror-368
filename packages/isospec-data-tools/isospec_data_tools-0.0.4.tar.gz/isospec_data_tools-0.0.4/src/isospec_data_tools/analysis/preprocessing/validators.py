"""Input validation utilities for data quality assurance.

This module provides comprehensive validation functions to ensure data quality
and consistency before analysis, including type checking, missing value detection,
and data integrity validation.
"""

import logging
from typing import Any, Optional

import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)


def validate_dataframe(data: Any, name: str = "data", min_rows: int = 1, min_cols: int = 1) -> None:
    """Validate that input is a non-empty DataFrame with minimum dimensions.

    Args:
        data: Input to validate
        name: Name of the parameter for error messages
        min_rows: Minimum number of rows required
        min_cols: Minimum number of columns required

    Raises:
        TypeError: If data is not a DataFrame
        ValueError: If data doesn't meet size requirements

    Example:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> validate_dataframe(df, "test_data", min_rows=2, min_cols=2)
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame, got {type(data)}")

    if data.empty:
        raise ValueError(f"{name} cannot be empty")

    if len(data) < min_rows:
        raise ValueError(f"{name} must have at least {min_rows} rows, got {len(data)}")

    if len(data.columns) < min_cols:
        raise ValueError(f"{name} must have at least {min_cols} columns, got {len(data.columns)}")

    logger.debug(f"DataFrame '{name}' validated: {data.shape}")


def validate_columns_exist(data: pd.DataFrame, required_columns: list[str], data_name: str = "data") -> None:
    """Validate that required columns exist in the DataFrame.

    Args:
        data: DataFrame to check
        required_columns: List of column names that must exist
        data_name: Name of the DataFrame for error messages

    Raises:
        ValueError: If any required columns are missing

    Example:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> validate_columns_exist(df, ['a', 'b'], "test_data")
    """
    missing_cols = [col for col in required_columns if col not in data.columns]
    if missing_cols:
        available_cols = list(data.columns)
        raise ValueError(
            f"Missing required columns in {data_name}: {missing_cols}. Available columns: {available_cols}"
        )

    logger.debug(f"All required columns found in '{data_name}': {required_columns}")


def validate_statistical_analysis_data(
    data: pd.DataFrame,
    class_column: str,
    covar_columns: Optional[list[str]] = None,
    min_classes: int = 2,
    min_samples_per_class: int = 1,
) -> None:
    """Validate input data for statistical analysis.

    Args:
        data: DataFrame containing analysis data
        class_column: Name of the column containing class labels
        covar_columns: List of covariate column names
        min_classes: Minimum number of unique classes required
        min_samples_per_class: Minimum samples required per class

    Raises:
        ValueError: If data doesn't meet statistical analysis requirements

    Example:
        >>> df = pd.DataFrame({
        ...     'value': [1, 2, 3, 4],
        ...     'class': ['A', 'A', 'B', 'B'],
        ...     'age': [25, 30, 35, 40]
        ... })
        >>> validate_statistical_analysis_data(df, 'class', ['age'])
    """
    # Basic DataFrame validation
    validate_dataframe(data, "analysis data")

    # Check required columns
    required_cols = [class_column]
    if covar_columns:
        required_cols.extend(covar_columns)
    validate_columns_exist(data, required_cols, "analysis data")

    # Check class column requirements
    unique_classes = data[class_column].nunique()
    if unique_classes < min_classes:
        class_counts = data[class_column].value_counts()
        raise ValueError(
            f"At least {min_classes} unique classes required in '{class_column}', "
            f"got {unique_classes}. Class distribution: {class_counts.to_dict()}"
        )

    # Check minimum samples per class
    class_counts = data[class_column].value_counts()
    insufficient_classes = class_counts[class_counts < min_samples_per_class]
    if not insufficient_classes.empty:
        raise ValueError(
            f"Each class must have at least {min_samples_per_class} samples. "
            f"Classes with insufficient samples: {insufficient_classes.to_dict()}"
        )

    # Check for missing values in critical columns
    if data[class_column].isna().any():
        missing_count = data[class_column].isna().sum()
        raise ValueError(f"Class column '{class_column}' contains {missing_count} missing values")

    logger.info(
        f"Statistical analysis data validated: {data.shape}, "
        f"{unique_classes} classes, covariates: {covar_columns or 'none'}"
    )


def validate_feature_columns(
    data: pd.DataFrame, prefix: str, min_features: int = 1, require_numeric: bool = True
) -> list[str]:
    """Validate and return feature columns based on prefix.

    Args:
        data: DataFrame to check
        prefix: Column prefix to identify features
        min_features: Minimum number of features required
        require_numeric: Whether features must be numeric

    Returns:
        List of validated feature column names

    Raises:
        ValueError: If insufficient features found or invalid types

    Example:
        >>> df = pd.DataFrame({'FT-1': [1, 2], 'FT-2': [3, 4], 'meta': ['A', 'B']})
        >>> features = validate_feature_columns(df, 'FT-', min_features=2)
        >>> print(features)  # ['FT-1', 'FT-2']
    """
    feature_cols = [col for col in data.columns if col.startswith(prefix)]

    if len(feature_cols) < min_features:
        raise ValueError(
            f"At least {min_features} feature columns required with prefix '{prefix}', "
            f"found {len(feature_cols)}: {feature_cols}"
        )

    if require_numeric:
        non_numeric = [col for col in feature_cols if not pd.api.types.is_numeric_dtype(data[col])]
        if non_numeric:
            raise ValueError(f"Non-numeric feature columns found: {non_numeric}")

    logger.debug(f"Validated {len(feature_cols)} feature columns with prefix '{prefix}'")
    return feature_cols


def validate_normalization_data(
    data: pd.DataFrame,
    feature_prefix: str,
    sample_type_col: Optional[str] = None,
    qc_samples: Optional[list[str]] = None,
) -> None:
    """Validate data for normalization operations.

    Args:
        data: DataFrame to validate
        feature_prefix: Prefix for feature columns
        sample_type_col: Column containing sample type information
        qc_samples: List of QC sample types (if applicable)

    Raises:
        ValueError: If data is invalid for normalization

    Example:
        >>> df = pd.DataFrame({
        ...     'FT-1': [1, 2, 3], 'FT-2': [4, 5, 6],
        ...     'SampleType': ['QC', 'Sample', 'QC']
        ... })
        >>> validate_normalization_data(df, 'FT-', 'SampleType', ['QC'])
    """
    # Basic validation
    validate_dataframe(data, "normalization data")

    # Validate features
    feature_cols = validate_feature_columns(data, feature_prefix, min_features=1, require_numeric=True)

    # Check for all-zero or all-negative features
    for col in feature_cols:
        if (data[col] <= 0).all():
            logger.warning(f"Feature '{col}' has all non-positive values - may cause normalization issues")

    # Validate QC sample requirements
    if sample_type_col and qc_samples:
        validate_columns_exist(data, [sample_type_col], "normalization data")

        qc_mask = data[sample_type_col].isin(qc_samples)
        qc_count = qc_mask.sum()

        if qc_count == 0:
            available_types = data[sample_type_col].unique().tolist()
            raise ValueError(f"No QC samples found with types {qc_samples}. Available sample types: {available_types}")

        logger.info(f"Found {qc_count} QC samples for normalization")

    logger.info(f"Normalization data validated: {len(feature_cols)} features, {len(data)} samples")


def validate_sample_groups(data: pd.DataFrame, group_column: str, min_group_size: int = 2) -> dict:
    """Validate sample grouping for analysis.

    Args:
        data: DataFrame containing sample data
        group_column: Column name for grouping samples
        min_group_size: Minimum number of samples per group

    Returns:
        Dictionary with group information

    Raises:
        ValueError: If grouping is invalid

    Example:
        >>> df = pd.DataFrame({'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]})
        >>> group_info = validate_sample_groups(df, 'group', min_group_size=2)
    """
    validate_dataframe(data, "sample data")
    validate_columns_exist(data, [group_column], "sample data")

    group_counts = data[group_column].value_counts()
    insufficient_groups = group_counts[group_counts < min_group_size]

    if not insufficient_groups.empty:
        raise ValueError(
            f"Each group must have at least {min_group_size} samples. "
            f"Groups with insufficient samples: {insufficient_groups.to_dict()}"
        )

    group_info = {
        "total_groups": len(group_counts),
        "group_sizes": group_counts.to_dict(),
        "total_samples": len(data),
        "min_group_size": group_counts.min(),
        "max_group_size": group_counts.max(),
    }

    logger.info(
        f"Sample groups validated: {group_info['total_groups']} groups, "
        f"sizes range {group_info['min_group_size']}-{group_info['max_group_size']}"
    )

    return group_info
