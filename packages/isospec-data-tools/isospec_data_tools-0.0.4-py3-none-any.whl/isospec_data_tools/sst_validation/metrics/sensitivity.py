"""Module for validating sensitivity metrics."""

from dataclasses import dataclass
from typing import Any

import numpy as np
from pandas import DataFrame

from isospec_data_tools.io_utils.mzmine import MZMineFeatureTable
from isospec_data_tools.sst_validation.errors import (
    InvalidDataFormatError,
    MissingRequiredColumnError,
    NoDataError,
    ValidationDataError,
)


@dataclass
class SensitivityMetrics:
    """Container for sensitivity validation metrics.

    Attributes:
        sn_ratio: Signal-to-noise ratio
        intensity_rsd: Relative standard deviation of intensity (if applicable)
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    sn_ratio: float
    intensity_rsd: float | None = None
    status: str = "pass"
    message: str = ""


def _initialize_results() -> dict[str, Any]:
    """Initialize the results dictionary with default values."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_sn_ratio": 0.0,
            "average_intensity_rsd": 0.0,
            "sn_ratio_range": [0.0, 0.0],
            "intensity_rsd_range": [0.0, 0.0],
            "compounds_checked": 0,
            "compounds_passed": 0,
        },
    }


def _find_matching_features(feature_table: MZMineFeatureTable, theoretical_mz: float, mz_tolerance: float) -> DataFrame:
    """Find features matching the theoretical m/z within tolerance."""
    return feature_table.features[
        (feature_table.features["mz"] >= theoretical_mz - mz_tolerance)
        & (feature_table.features["mz"] <= theoretical_mz + mz_tolerance)
    ]


def calculate_rsd(values: list[float]) -> float:
    """Calculate Relative Standard Deviation (RSD) as a percentage.

    Args:
        values: List of numeric values

    Returns:
        RSD as a percentage
    """
    if not values or len(values) < 2:
        return 0.0

    values_array = np.array(values)
    return float((np.std(values_array, ddof=1) / np.mean(values_array)) * 100)


def _validate_input_data(feature_table: MZMineFeatureTable, target_compounds: DataFrame) -> None:
    """Validate input data for sensitivity validation.

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

    required_columns = ["mz", "abundance_level"]
    missing_columns = [col for col in required_columns if col not in target_compounds.columns]
    if missing_columns:
        message = f"Missing required columns in target compounds: {missing_columns}"
        raise MissingRequiredColumnError(message)


def _calculate_snr_from_intensity(intensity: float, noise_mean: float = 5.0, noise_std: float = 0.5) -> float:
    """Calculate signal-to-noise ratio from intensity using white noise assumption.

    Args:
        intensity: Signal intensity value
        noise_mean: Mean of white noise (default: 5.0)
        noise_std: Standard deviation of white noise (default: 0.5)

    Returns:
        Calculated signal-to-noise ratio
    """
    return float(intensity / (noise_mean + 3 * noise_std))  # Using mean + 3sigma as noise baseline


def _evaluate_sensitivity(
    sn_ratio: float,
    intensity_rsd: float | None,
    sn_ratio_high: float,
    sn_ratio_low: float,
    intensity_rsd_threshold: float,
    is_standard: bool,
) -> SensitivityMetrics:
    """Evaluate sensitivity metrics against thresholds."""
    status = "pass"
    messages = []

    # For standards, use high S/N threshold
    sn_threshold = sn_ratio_high if is_standard else sn_ratio_low

    if sn_ratio < sn_threshold:
        status = "fail"
        messages.append(f"S/N ratio {sn_ratio:.1f} below threshold ({sn_threshold})")

    if intensity_rsd is not None and intensity_rsd > intensity_rsd_threshold:
        status = "fail"
        messages.append(f"Intensity RSD {intensity_rsd:.1f}% exceeds threshold ({intensity_rsd_threshold}%)")

    return SensitivityMetrics(
        sn_ratio=sn_ratio,
        intensity_rsd=intensity_rsd,
        status=status,
        message="; ".join(messages) if messages else "Sensitivity metrics within acceptable ranges",
    )


def _process_replicate_group(
    measurements: DataFrame,
    group_files: list[str],
    compound_name: str,
    group_name: str,
    thresholds: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[float], list[float]]:
    """Process sensitivity metrics for a replicate group."""
    group_results = []
    group_sn_ratios = []
    group_intensities = []

    for file in group_files:
        file_metrics = measurements[measurements["filename"].str.contains(file)]

        if not file_metrics.empty:
            try:
                intensity = float(file_metrics["area"].iloc[0])
                group_intensities.append(intensity)

                # Calculate SNR either from column or from intensity
                if "sn" in file_metrics.columns:
                    sn_ratio = float(file_metrics["sn"].iloc[0])
                else:
                    sn_ratio = _calculate_snr_from_intensity(intensity)

                group_sn_ratios.append(sn_ratio)
            except (ValueError, TypeError) as e:
                message = f"Error processing sensitivity data for {compound_name} in {file}: {e!s}"
                raise InvalidDataFormatError(message) from e

    # Calculate metrics only if we have both intensities and S/N ratios
    if group_intensities and group_sn_ratios:
        try:
            avg_sn_ratio = float(np.mean(group_sn_ratios))
            intensity_rsd = calculate_rsd(group_intensities)

            metrics = _evaluate_sensitivity(
                sn_ratio=avg_sn_ratio,
                intensity_rsd=intensity_rsd,
                sn_ratio_high=float(thresholds["sn_ratio_high"]),
                sn_ratio_low=float(thresholds["sn_ratio_low"]),
                intensity_rsd_threshold=float(thresholds["intensity_rsd_threshold"]),
                is_standard=bool(thresholds["is_standard"]),
            )

            group_results.append({
                "compound": compound_name,
                "replicate_group": group_name,
                "sn_ratio": metrics.sn_ratio,
                "intensity_rsd": metrics.intensity_rsd,
                "status": metrics.status,
                "message": metrics.message,
                "metrics": {
                    "sn_ratio": metrics.sn_ratio,
                    "intensity_rsd": metrics.intensity_rsd,
                },
            })

        except (ValueError, TypeError) as e:
            message = f"Error calculating sensitivity metrics for {compound_name}: {e!s}"
            raise InvalidDataFormatError(message) from e
        else:
            return group_results, group_sn_ratios, [intensity_rsd]

    # Return empty lists if no valid measurements were found
    return [], [], []


def _update_summary_statistics(
    results: dict[str, Any],
    all_sn_ratios: list[float],
    all_intensity_rsds: list[float],
    target_compounds: DataFrame,
) -> None:
    """Update summary statistics in the results dictionary."""
    if all_sn_ratios or all_intensity_rsds:
        if all_sn_ratios:
            results["summary"].update({
                "average_sn_ratio": float(np.mean(all_sn_ratios)),
                "sn_ratio_range": [float(np.min(all_sn_ratios)), float(np.max(all_sn_ratios))],
            })

        if all_intensity_rsds:
            results["summary"].update({
                "average_intensity_rsd": float(np.mean(all_intensity_rsds)),
                "intensity_rsd_range": [float(np.min(all_intensity_rsds)), float(np.max(all_intensity_rsds))],
            })

        results["summary"].update({
            "compounds_checked": len(target_compounds),
            "compounds_passed": sum(1 for d in results["details"] if d["status"] == "pass"),
        })

        results["passed"] = all(d["status"] == "pass" for d in results["details"] if "status" in d)


def validate_sensitivity(
    feature_table: MZMineFeatureTable,
    target_compounds: DataFrame,
    replicate_groups: dict[str, list[str]],
    sn_ratio_high: float = 100,
    sn_ratio_low: float = 10,
    intensity_rsd_threshold: float = 15.0,
    is_standard: bool = True,
    mz_tolerance: float = 0.1,
) -> dict[str, Any]:
    """Validate sensitivity and signal intensity for target compounds.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        sn_ratio_high: Minimum S/N ratio for high-abundance compounds
        sn_ratio_low: Minimum S/N ratio for low-abundance compounds
        intensity_rsd_threshold: Maximum allowed RSD for intensities
        is_standard: Whether the compounds are standards
        mz_tolerance: Tolerance for matching features

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each measurement
            "summary": {  # Summary statistics
                "average_sn_ratio": float,
                "average_intensity_rsd": float,
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
        message = f"Invalid input data for sensitivity validation: {e!s}"
        raise ValidationDataError(message) from e

    results = _initialize_results()
    thresholds = {
        "sn_ratio_high": sn_ratio_high,
        "sn_ratio_low": sn_ratio_low,
        "intensity_rsd_threshold": intensity_rsd_threshold,
        "is_standard": is_standard,
    }

    all_sn_ratios = []
    all_intensity_rsds = []

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
                    group_results, sn_ratios, intensity_rsds = _process_replicate_group(
                        feature_measurements,
                        files,
                        compound_name,
                        group_name,
                        thresholds,
                    )

                    results["details"].extend(group_results)
                    all_sn_ratios.extend(sn_ratios)
                    all_intensity_rsds.extend(intensity_rsds)
                except InvalidDataFormatError as e:
                    results["details"].append({
                        "compound": compound_name,
                        "status": "error",
                        "message": str(e),
                    })

    _update_summary_statistics(results, all_sn_ratios, all_intensity_rsds, target_compounds)
    return results
