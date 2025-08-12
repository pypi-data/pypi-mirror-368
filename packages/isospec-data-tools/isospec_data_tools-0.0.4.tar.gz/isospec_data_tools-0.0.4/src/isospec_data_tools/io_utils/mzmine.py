"""Module for handling MZMine feature table conversion."""

from dataclasses import dataclass
from typing import Any

from pandas import DataFrame


@dataclass
class MZMineFeatureTable:
    """Container for MZMine feature table data.

    Attributes:
        features: DataFrame containing feature-level information (e.g., id, mz, rt)
        measurements: DataFrame containing per-file measurements
    """

    features: DataFrame
    measurements: DataFrame


def _extract_feature_columns(df: DataFrame) -> list[str]:
    """Extract columns that describe feature properties.

    Args:
        df: Input DataFrame

    Returns:
        List of column names that are feature descriptors
    """
    return [col for col in df.columns if not col.startswith("datafile:")]


def _extract_measurement_columns(df: DataFrame) -> list[str]:
    """Extract columns that contain per-file measurements.

    Args:
        df: Input DataFrame

    Returns:
        List of column names that contain file-specific measurements
    """
    return [col for col in df.columns if col.startswith("datafile:")]


def _parse_measurement_column(column: str) -> tuple[str, str, str]:
    """Parse a measurement column name into components.

    Args:
        column: Column name in format 'datafile:filename.mzML:property'

    Returns:
        Tuple of (prefix, filename, property_name)
    """
    parts = column.split(":")
    if len(parts) >= 3:
        return parts[0], parts[1], "_".join(parts[2:])
    return ("", "", "")  # Return empty strings as fallback


def convert_mzmine_feature_table(feature_table: DataFrame) -> MZMineFeatureTable:
    """Convert MZMine feature table to standardized format.

    The input feature table has two types of columns:
    1. Feature descriptors (e.g., id, mz, rt)
    2. Per-file measurements (e.g., datafile:filename.mzML:area)

    This function splits these into two separate tables for easier analysis.

    Args:
        feature_table: Raw feature table from MZMine

    Returns:
        MZMineFeatureTable containing:
            - features: DataFrame with feature-level information
            - measurements: DataFrame with one row per file per feature

    Example:
        >>> feature_table = pd.read_csv('mzmine_features.csv')
        >>> converted = convert_mzmine_feature_table(feature_table)
        >>> features = converted.features  # Get feature-level information
        >>> measurements = converted.measurements  # Get per-file measurements
    """
    # Extract feature descriptor columns
    feature_columns = _extract_feature_columns(feature_table)
    features = feature_table[feature_columns].copy()

    # Process file-specific measurements
    measurement_columns = _extract_measurement_columns(feature_table)
    measurements: list[dict[str, Any]] = []

    for _, row in feature_table.iterrows():
        feature_id = row["id"]

        # Group columns by file
        file_data: dict[str, dict[str, Any]] = {}

        for col in measurement_columns:
            prefix, filename, property_name = _parse_measurement_column(col)
            if not filename:  # Skip invalid columns
                continue

            if filename not in file_data:
                file_data[filename] = {"feature_id": feature_id, "filename": filename}

            # Remove .mzML extension from property name for cleaner column names
            clean_property = property_name.replace(".mzML", "")
            file_data[filename][clean_property] = row[col]

        # Convert to rows
        measurements.extend(file_data.values())

    measurements_df = DataFrame(measurements)

    return MZMineFeatureTable(features=features, measurements=measurements_df)
