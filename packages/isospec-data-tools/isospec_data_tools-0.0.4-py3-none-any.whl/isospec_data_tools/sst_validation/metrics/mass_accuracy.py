"""Module for validating mass accuracy metrics."""

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
class MassAccuracyMetrics:
    """Container for mass accuracy validation metrics.

    Attributes:
        mass_error: Mass error in ppm
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    mass_error: float
    status: str
    message: str


def _initialize_results() -> dict[str, Any]:
    """Initialize the results dictionary with default values."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_mass_error": 0.0,
            "mass_error_range": [0.0, 0.0],
            "compounds_checked": 0,
            "compounds_passed": 0,
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


def calculate_mass_error(theoretical_mz: float, observed_mz: float) -> float:
    """Calculate mass error in ppm.

    Args:
        theoretical_mz: Theoretical m/z value
        observed_mz: Observed m/z value

    Returns:
        Mass error in parts per million (ppm)
    """
    return ((observed_mz - theoretical_mz) / theoretical_mz) * 1e6


def _validate_input_data(feature_table: MZMineFeatureTable, target_compounds: pd.DataFrame) -> None:
    """Validate input data for mass accuracy validation.

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

    if "mz" not in feature_table.measurements.columns:
        message = "Missing 'mz' column in feature table measurements"
        raise MissingRequiredColumnError(message)


def _evaluate_mass_accuracy(
    mass_error: float,
    threshold: float,
) -> MassAccuracyMetrics:
    """Evaluate mass accuracy against threshold."""
    status = "pass"
    message = f"Mass error {abs(mass_error):.2f} ppm within threshold (±{threshold} ppm)"

    if abs(mass_error) > threshold:
        status = "fail"
        message = f"Mass error {abs(mass_error):.2f} ppm exceeds threshold (±{threshold} ppm)"

    return MassAccuracyMetrics(mass_error=mass_error, status=status, message=message)


def _process_replicate_group(
    measurements: pd.DataFrame,
    group_files: list[str],
    compound_name: str,
    group_name: str,
    theoretical_mz: float,
    mass_accuracy_threshold: float,
) -> tuple[list[dict[str, Any]], list[float]]:
    """Process mass accuracy metrics for a replicate group."""
    group_results = []
    mass_errors = []

    for file in group_files:
        file_metrics = measurements[measurements["filename"].str.contains(file)]

        if not file_metrics.empty and "mz" in file_metrics.columns:
            try:
                observed_mz = file_metrics["mz"].iloc[0]
                mass_error = calculate_mass_error(theoretical_mz, observed_mz)
                metrics = _evaluate_mass_accuracy(mass_error, mass_accuracy_threshold)

                group_results.append({
                    "compound": compound_name,
                    "file": file,
                    "replicate_group": group_name,
                    "theoretical_mz": theoretical_mz,
                    "observed_mz": observed_mz,
                    "mass_error": metrics.mass_error,
                    "status": metrics.status,
                    "message": metrics.message,
                })

                mass_errors.append(abs(mass_error))
            except (ValueError, TypeError) as e:
                message = f"Error processing mass accuracy for {compound_name} in {file}: {e!s}"
                raise InvalidDataFormatError(message) from e

    return group_results, mass_errors


def _update_summary_statistics(
    results: dict[str, Any],
    all_mass_errors: list[float],
    target_compounds: pd.DataFrame,
) -> None:
    """Update summary statistics in the results dictionary."""
    if all_mass_errors:
        results["summary"].update({
            "average_mass_error": np.mean(all_mass_errors),
            "mass_error_range": [np.min(all_mass_errors), np.max(all_mass_errors)],
            "compounds_checked": len(target_compounds),
            "compounds_passed": sum(1 for d in results["details"] if d["status"] == "pass"),
        })

        results["passed"] = all(d["status"] == "pass" for d in results["details"] if "status" in d)


def validate_mass_accuracy(
    feature_table: MZMineFeatureTable,
    target_compounds: pd.DataFrame,
    replicate_groups: dict[str, list[str]],
    mass_accuracy_threshold: float = 10.0,
    mz_tolerance: float = 0.1,
) -> dict[str, Any]:
    """Validate mass accuracy for target compounds.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        mass_accuracy_threshold: Maximum allowed mass error in ppm
        mz_tolerance: Tolerance for matching features

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each measurement
            "summary": {  # Summary statistics
                "average_mass_error": float,
                "mass_error_range": [float, float],
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
        message = f"Invalid input data for mass accuracy validation: {e!s}"
        raise ValidationDataError(message) from e

    results = _initialize_results()
    all_mass_errors = []

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
                    group_results, mass_errors = _process_replicate_group(
                        feature_measurements,
                        files,
                        compound_name,
                        group_name,
                        theoretical_mz,
                        mass_accuracy_threshold,
                    )

                    results["details"].extend(group_results)
                    all_mass_errors.extend(mass_errors)
                except InvalidDataFormatError as e:
                    results["details"].append({
                        "compound": compound_name,
                        "status": "error",
                        "message": str(e),
                    })

    _update_summary_statistics(results, all_mass_errors, target_compounds)
    return results
