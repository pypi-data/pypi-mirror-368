"""Module for validating peak shape metrics."""

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from isospec_data_tools.io_utils.mzmine import MZMineFeatureTable
from isospec_data_tools.sst_validation.errors import (
    InvalidDataFormatError,
    MissingRequiredColumnError,
    NoDataError,
    ValidationDataError,
)


@dataclass
class PeakShapeMetrics:
    """Container for peak shape validation metrics.

    Attributes:
        asymmetry: Peak asymmetry factor
        tailing: Peak tailing factor
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    asymmetry: float
    tailing: float
    status: str
    message: str


def _initialize_results() -> dict[str, Any]:
    """Initialize the results dictionary with default values."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_asymmetry": 0.0,
            "average_tailing": 0.0,
            "compounds_checked": 0,
            "compounds_passed": 0,
            "asymmetry_range": [0.0, 0.0],
            "tailing_range": [0.0, 0.0],
        },
    }


def _find_matching_features(
    feature_table: MZMineFeatureTable, theoretical_mz: float, mz_tolerance: float
) -> pd.DataFrame:
    """Find features matching the theoretical m/z within tolerance."""
    return feature_table.features[
        (feature_table.features["mz"] >= theoretical_mz - mz_tolerance)
        & (feature_table.features["mz"] <= theoretical_mz + mz_tolerance)
    ]


def _validate_input_data(feature_table: MZMineFeatureTable, target_compounds: pd.DataFrame) -> None:
    """Validate input data for peak shape validation.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information

    Raises:
        ValidationDataError: If input data is invalid or missing required columns
    """
    if feature_table.measurements.empty:
        message = "Feature table contains no measurements"
        raise NoDataError(message)

    if target_compounds.empty:
        message = "Target compounds list is empty"
        raise NoDataError(message)

    required_columns = ["mz"]
    missing_columns = [col for col in required_columns if col not in target_compounds.columns]
    if missing_columns:
        message = f"Missing required columns in target compounds: {missing_columns}"
        raise MissingRequiredColumnError(message)

    required_measurement_columns = ["asymmetry_factor", "tailing_factor"]
    missing_measurement_columns = [
        col for col in required_measurement_columns if col not in feature_table.measurements.columns
    ]
    if missing_measurement_columns:
        message = f"Missing required columns in feature table measurements: {missing_measurement_columns}"
        raise MissingRequiredColumnError(message)


def _evaluate_peak_shape(
    asymmetry: float,
    tailing: float,
    asymmetry_min: float,
    asymmetry_max: float,
    tailing_min: float,
    tailing_max: float,
) -> PeakShapeMetrics:
    """Evaluate peak shape metrics against thresholds."""
    status = "pass"
    messages = []

    if not (asymmetry_min <= asymmetry <= asymmetry_max):
        status = "fail"
        messages.append(f"Asymmetry {asymmetry:.2f} outside range [{asymmetry_min}-{asymmetry_max}]")

    if not (tailing_min <= tailing <= tailing_max):
        status = "fail"
        messages.append(f"Tailing {tailing:.2f} outside range [{tailing_min}-{tailing_max}]")

    return PeakShapeMetrics(
        asymmetry=asymmetry,
        tailing=tailing,
        status=status,
        message="; ".join(messages) if messages else "Peak shape metrics within acceptable ranges",
    )


def _process_replicate_group(
    group_data: pd.DataFrame,
    compound: str,
    group_name: str,
    asymmetry_min: float,
    asymmetry_max: float,
    tailing_min: float,
    tailing_max: float,
) -> dict[str, Any]:
    """Process a single replicate group for peak shape validation.

    Args:
        group_data: DataFrame containing peak shape data for a replicate group
        compound: Name of the compound being validated
        group_name: Name of the replicate group
        asymmetry_min: Minimum acceptable peak asymmetry
        asymmetry_max: Maximum acceptable peak asymmetry
        tailing_min: Minimum acceptable tailing factor
        tailing_max: Maximum acceptable tailing factor

    Returns:
        Dictionary containing validation results for the group

    Raises:
        InvalidDataFormatError: If data processing fails
    """
    try:
        # Calculate peak shape metrics
        asymmetry = group_data["asymmetry_factor"].mean()
        tailing = group_data["tailing_factor"].mean()
        asymmetry_rsd = group_data["asymmetry_factor"].std() / asymmetry * 100
        tailing_rsd = group_data["tailing_factor"].std() / tailing * 100

        # Check if metrics are within acceptable ranges
        asymmetry_passed = asymmetry_min <= asymmetry <= asymmetry_max
        tailing_passed = tailing_min <= tailing <= tailing_max

        # Determine status and message
        if asymmetry_passed and tailing_passed:
            status = "pass"
            message = "Peak shape metrics within acceptable ranges"
        else:
            status = "fail"
            message_parts = []
            if not asymmetry_passed:
                message_parts.append(
                    f"Peak asymmetry ({asymmetry:.2f}) outside range [{asymmetry_min:.2f}, {asymmetry_max:.2f}]"
                )
            if not tailing_passed:
                message_parts.append(
                    f"Peak tailing ({tailing:.2f}) outside range [{tailing_min:.2f}, {tailing_max:.2f}]"
                )
            message = "; ".join(message_parts)

    except (ValueError, TypeError) as err:
        message = f"Failed to process peak shape data for {compound}: {err!s}"
        raise InvalidDataFormatError(message) from err
    else:
        return {
            "compound": compound,
            "replicate_group": group_name,
            "status": status,
            "message": message,
            "asymmetry": asymmetry,  # Include directly for visualization
            "tailing": tailing,  # Include directly for visualization
            "metrics": {
                "asymmetry": asymmetry,
                "tailing": tailing,
                "asymmetry_rsd": asymmetry_rsd,
                "tailing_rsd": tailing_rsd,
            },
        }


def _update_summary_statistics(
    results: dict[str, Any],
    all_asymmetry_values: list[float],
    all_tailing_values: list[float],
    target_compounds: pd.DataFrame,
) -> None:
    """Update summary statistics in the results dictionary."""
    if all_asymmetry_values and all_tailing_values:
        results["summary"].update({
            "average_asymmetry": np.mean(all_asymmetry_values),
            "average_tailing": np.mean(all_tailing_values),
            "asymmetry_range": [np.min(all_asymmetry_values), np.max(all_asymmetry_values)],
            "tailing_range": [np.min(all_tailing_values), np.max(all_tailing_values)],
            "compounds_checked": len(target_compounds),
            "compounds_passed": sum(1 for d in results["details"] if d["status"] == "pass"),
        })

        results["passed"] = all(d["status"] == "pass" for d in results["details"] if "status" in d)


def validate_peak_shape(
    feature_table: MZMineFeatureTable,
    target_compounds: pd.DataFrame,
    replicate_groups: dict[str, list[str]],
    asymmetry_min: float = 0.9,
    asymmetry_max: float = 1.2,
    tailing_min: float = 0.9,
    tailing_max: float = 1.2,
    mz_tolerance: float = 0.1,
) -> dict[str, Any]:
    """Validate peak shape metrics for target compounds.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        asymmetry_min: Minimum acceptable peak asymmetry
        asymmetry_max: Maximum acceptable peak asymmetry
        tailing_min: Minimum acceptable tailing factor
        tailing_max: Maximum acceptable tailing factor
        mz_tolerance: Tolerance for matching features

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each measurement
            "summary": {  # Summary statistics
                "average_asymmetry": float,
                "average_tailing": float,
                "compounds_checked": int,
                "compounds_passed": int,
                "asymmetry_range": [float, float],
                "tailing_range": [float, float]
            }
        }

    Raises:
        ValidationDataError: If input data is invalid or missing required columns
        InvalidDataFormatError: If data format is invalid or cannot be processed
    """
    try:
        _validate_input_data(feature_table, target_compounds)
    except ValidationDataError as e:
        message = f"Invalid input data for peak shape validation: {e!s}"
        raise ValidationDataError(message) from e

    results = _initialize_results()

    all_asymmetry_values = []
    all_tailing_values = []

    for _, compound in target_compounds.iterrows():
        theoretical_mz = compound["mz"]
        compound_name = compound.get("name", f"m/z {theoretical_mz}")

        matching_features = _find_matching_features(feature_table, theoretical_mz, mz_tolerance)

        if matching_features.empty:
            results["details"].append({
                "compound": compound_name,
                "replicate_group": "unknown",
                "status": "not_found",
                "message": f"No matching feature found for {compound_name} (m/z {theoretical_mz})",
            })
            continue

        for _, feature in matching_features.iterrows():
            feature_measurements = feature_table.measurements[feature_table.measurements["feature_id"] == feature["id"]]

            for group_name, _ in replicate_groups.items():
                try:
                    group_results = _process_replicate_group(
                        feature_measurements,
                        compound_name,
                        group_name,
                        asymmetry_min,
                        asymmetry_max,
                        tailing_min,
                        tailing_max,
                    )

                    results["details"].append(group_results)

                    # Collect metrics for summary statistics
                    all_asymmetry_values.append(group_results["metrics"]["asymmetry"])
                    all_tailing_values.append(group_results["metrics"]["tailing"])
                except InvalidDataFormatError as e:
                    results["details"].append({
                        "compound": compound_name,
                        "replicate_group": group_name,
                        "status": "error",
                        "message": str(e),
                    })

    _update_summary_statistics(results, all_asymmetry_values, all_tailing_values, target_compounds)
    return results
