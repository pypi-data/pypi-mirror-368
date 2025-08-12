"""Module for validating mass resolution metrics."""

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
class ResolutionMetrics:
    """Container for resolution validation metrics.

    Attributes:
        resolution: Calculated resolution value
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    resolution: float
    status: str
    message: str


def _initialize_results() -> dict[str, Any]:
    """Initialize the results dictionary with default values."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_resolution": 0.0,
            "resolution_range": [0.0, 0.0],
            "compounds_checked": 0,
            "compounds_passed": 0,
        },
    }


def calculate_resolution_at_mz(
    resolution_ref: float, mz_ref: float, mz_target: float, instrument_type: str = "orbitrap"
) -> float:
    """Calculate expected resolution at a given m/z value.

    Args:
        resolution_ref: Reference resolution value
        mz_ref: Reference m/z value
        mz_target: Target m/z value
        instrument_type: Type of mass analyzer

    Returns:
        Expected resolution at target m/z
    """
    if instrument_type.lower() == "orbitrap":
        # Resolution scales with 1/sqrt(m/z) for Orbitrap
        return float(resolution_ref * np.sqrt(mz_ref / mz_target))
    else:
        # For other instruments (e.g., TOF), resolution scales with m/z
        return float(resolution_ref * (mz_ref / mz_target))


def _find_matching_features(
    feature_table: MZMineFeatureTable, theoretical_mz: float, mz_tolerance: float
) -> pd.DataFrame:
    """Find features matching the theoretical m/z within tolerance."""
    return feature_table.features[
        (feature_table.features["mz"] >= theoretical_mz - mz_tolerance)
        & (feature_table.features["mz"] <= theoretical_mz + mz_tolerance)
    ]


def _validate_input_data(feature_table: MZMineFeatureTable, target_compounds: pd.DataFrame) -> None:
    """Validate input data for resolution validation.

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

    if "fwhm" not in feature_table.measurements.columns:
        message = "Missing 'fwhm' column in feature table measurements"
        raise MissingRequiredColumnError(message)


def _evaluate_resolution(
    resolution: float,
    threshold: float,
) -> ResolutionMetrics:
    """Evaluate resolution against threshold."""
    status = "pass"
    message = f"Resolution {resolution:.0f} meets minimum requirement ({threshold:.0f})"

    if resolution < threshold:
        status = "fail"
        message = f"Resolution {resolution:.0f} below minimum requirement ({threshold:.0f})"

    return ResolutionMetrics(resolution=resolution, status=status, message=message)


def _process_replicate_group(
    measurements: pd.DataFrame,
    group_files: list[str],
    compound_name: str,
    group_name: str,
    resolution_threshold: float,
) -> tuple[list[dict[str, Any]], list[float]]:
    """Process resolution metrics for a replicate group."""
    group_results = []
    resolution_values = []

    for file in group_files:
        file_metrics = measurements[measurements["filename"].str.contains(file)]

        if not file_metrics.empty and "fwhm" in file_metrics.columns:
            try:
                mz = file_metrics["mz"].iloc[0]
                fwhm = file_metrics["fwhm"].iloc[0]
                resolution = mz / fwhm
                metrics = _evaluate_resolution(resolution, resolution_threshold)

                group_results.append({
                    "compound": compound_name,
                    "file": file,
                    "replicate_group": group_name,
                    "mz": mz,
                    "fwhm": fwhm,
                    "resolution": metrics.resolution,
                    "status": metrics.status,
                    "message": metrics.message,
                })

                resolution_values.append(resolution)
            except (ValueError, TypeError, ZeroDivisionError) as e:
                message = f"Error processing resolution for {compound_name} in {file}: {e!s}"
                raise InvalidDataFormatError(message) from e

    return group_results, resolution_values


def _update_summary_statistics(
    results: dict[str, Any],
    all_resolution_values: list[float],
    target_compounds: pd.DataFrame,
) -> None:
    """Update summary statistics in the results dictionary."""
    if all_resolution_values:
        results["summary"].update({
            "average_resolution": np.mean(all_resolution_values),
            "resolution_range": [np.min(all_resolution_values), np.max(all_resolution_values)],
            "compounds_checked": len(target_compounds),
            "compounds_passed": sum(1 for d in results["details"] if d["status"] == "pass"),
        })

        results["passed"] = all(d["status"] == "pass" for d in results["details"] if "status" in d)


def validate_resolution(
    feature_table: MZMineFeatureTable,
    target_compounds: pd.DataFrame,
    replicate_groups: dict[str, list[str]],
    resolution_threshold: float = 30000,
    instrument_type: str = "orbitrap",
    mz_tolerance: float = 0.1,
) -> dict[str, Any]:
    """Validate mass resolution using FWHM for target compounds.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        resolution_threshold: Minimum acceptable resolution
        instrument_type: Type of mass analyzer (affects resolution scaling)
        mz_tolerance: Tolerance for matching features

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each measurement
            "summary": {  # Summary statistics
                "average_resolution": float,
                "resolution_range": [float, float],
                "compounds_checked": int,
                "compounds_passed": int
            }
        }

    Raises:
        ValidationDataError: If input data is invalid or missing required columns
        InvalidDataFormatError: If data format is invalid or cannot be processed
    """
    try:
        _validate_input_data(feature_table, target_compounds)
    except ValidationDataError as e:
        message = f"Invalid input data for resolution validation: {e!s}"
        raise ValidationDataError(message) from e

    results = _initialize_results()
    all_resolution_values = []

    for _, compound in target_compounds.iterrows():
        theoretical_mz = compound["mz"]
        compound_name = compound.get("name", f"m/z {theoretical_mz}")

        matching_features = _find_matching_features(feature_table, theoretical_mz, mz_tolerance)

        if matching_features.empty:
            results["details"].append({
                "compound": compound_name,
                "status": "not_found",
                "message": f"No matching feature found for {compound_name} (m/z {theoretical_mz})",
            })
            continue

        for _, feature in matching_features.iterrows():
            feature_measurements = feature_table.measurements[feature_table.measurements["feature_id"] == feature["id"]]

            for group_name, files in replicate_groups.items():
                try:
                    group_results, resolution_values = _process_replicate_group(
                        feature_measurements,
                        files,
                        compound_name,
                        group_name,
                        resolution_threshold,
                    )

                    results["details"].extend(group_results)
                    all_resolution_values.extend(resolution_values)
                except InvalidDataFormatError as e:
                    results["details"].append({
                        "compound": compound_name,
                        "status": "error",
                        "message": str(e),
                    })

    _update_summary_statistics(results, all_resolution_values, target_compounds)
    return results


def _calculate_resolution(mz: float, fwhm: float) -> float:
    """Calculate mass resolution at m/z 200.

    Args:
        mz: Measured m/z value
        fwhm: Full width at half maximum

    Returns:
        Resolution at m/z 200
    """
    if fwhm <= 0:
        return 0.0

    # Calculate resolution at measured m/z
    resolution_at_mz = float(mz / fwhm)

    # Scale to m/z 200 using square root relationship
    resolution_at_200 = resolution_at_mz * float(np.sqrt(200.0 / mz))

    return float(resolution_at_200)
