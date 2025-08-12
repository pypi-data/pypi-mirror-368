"""Module for validating retention time metrics."""

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
class RetentionTimeMetrics:
    """Container for retention time validation metrics.

    Attributes:
        rt: Measured retention time
        rt_deviation: Deviation from expected retention time (if applicable)
        rt_rsd: Relative standard deviation of retention time (if applicable)
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    rt: float
    rt_deviation: float | None = None
    rt_rsd: float | None = None
    status: str = "pass"
    message: str = ""


@dataclass
class RetentionTimeDifferenceMetrics:
    """Container for retention time difference validation metrics.

    Attributes:
        time_differences: Dictionary mapping replicate groups to time differences from reference
        rsd: Relative standard deviation of time differences across groups
        max_difference: Maximum difference in time differences between groups
        status: Validation status ('pass' or 'fail')
        message: Detailed message about the validation result
    """

    time_differences: dict[str, float]
    rsd: float
    max_difference: float
    status: str = "pass"
    message: str = ""


def _initialize_results() -> dict[str, Any]:
    """Initialize the results dictionary with default values."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_rt_deviation": 0.0,
            "average_rt_rsd": 0.0,
            "rt_deviation_range": [0.0, 0.0],
            "rt_rsd_range": [0.0, 0.0],
            "compounds_checked": 0,
            "compounds_passed": 0,
        },
    }


def _initialize_rt_difference_results() -> dict[str, Any]:
    """Initialize the results dictionary for retention time difference validation."""
    return {
        "passed": True,
        "details": [],
        "summary": {
            "average_rsd": 0.0,
            "max_difference": 0.0,
            "compounds_checked": 0,
            "compounds_passed": 0,
            "reference_compound": "",
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


def calculate_rt_metrics(rt_values: list[float]) -> tuple[float, float]:
    """Calculate retention time deviation metrics.

    Args:
        rt_values: List of retention time values

    Returns:
        Tuple of (average_rt, rsd_percent)
    """
    if not rt_values:
        return 0.0, 0.0

    rt_array = np.array(rt_values)
    average_rt = np.mean(rt_array)

    rsd = np.std(rt_array, ddof=1) / average_rt * 100 if len(rt_values) > 1 else 0.0

    return average_rt, rsd


def _validate_input_data(feature_table: MZMineFeatureTable, target_compounds: pd.DataFrame) -> None:
    """Validate input data for retention time validation.

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

    if "rt" not in feature_table.measurements.columns:
        message = "Missing 'rt' column in feature table measurements"
        raise MissingRequiredColumnError(message)


def _evaluate_rt_metrics(
    rt: float,
    rt_rsd: float | None,
    rt_deviation: float | None,
    rt_rsd_threshold: float,
    rt_deviation_threshold: float,
    expected_rt_deviation_threshold: float,
) -> RetentionTimeMetrics:
    """Evaluate retention time metrics against thresholds."""
    status = "pass"
    messages = []

    if rt_rsd is not None and rt_rsd > rt_rsd_threshold:
        status = "fail"
        messages.append(f"RT RSD {rt_rsd:.2f}% exceeds threshold ({rt_rsd_threshold}%)")

    if rt_deviation is not None:
        if abs(rt_deviation) > rt_deviation_threshold:
            status = "fail"
            messages.append(f"RT deviation {rt_deviation:.2f} min exceeds threshold (±{rt_deviation_threshold} min)")
        if abs(rt_deviation) > expected_rt_deviation_threshold:
            status = "fail"
            messages.append(
                f"RT deviation from expected {rt_deviation:.2f} min exceeds threshold (±{expected_rt_deviation_threshold} min)"
            )

    return RetentionTimeMetrics(
        rt=rt,
        rt_deviation=rt_deviation,
        rt_rsd=rt_rsd,
        status=status,
        message="; ".join(messages) if messages else "Retention time metrics within acceptable ranges",
    )


def _evaluate_rt_difference_metrics(
    time_differences: dict[str, float],
    rsd: float,
    max_difference: float,
    rsd_threshold: float,
    max_difference_threshold: float,
) -> RetentionTimeDifferenceMetrics:
    """Evaluate retention time difference metrics against thresholds."""
    status = "pass"
    messages = []

    if rsd > rsd_threshold:
        status = "fail"
        messages.append(f"Time difference RSD {rsd:.2f}% exceeds threshold ({rsd_threshold}%)")

    if max_difference > max_difference_threshold:
        status = "fail"
        messages.append(
            f"Maximum time difference {max_difference:.2f} min exceeds threshold ({max_difference_threshold} min)"
        )

    return RetentionTimeDifferenceMetrics(
        time_differences=time_differences,
        rsd=rsd,
        max_difference=max_difference,
        status=status,
        message="; ".join(messages) if messages else "Time differences within acceptable ranges",
    )


def _process_replicate_group(
    measurements: pd.DataFrame,
    group_files: list[str],
    compound_name: str,
    group_name: str,
    expected_rt: float | None,
    thresholds: dict[str, float],
) -> tuple[list[dict[str, Any]], list[float], list[float], list[float]]:
    """Process retention time metrics for a replicate group."""
    group_results = []
    group_rt_values = []
    all_rt_deviations = []
    all_rt_rsds = []

    for file in group_files:
        file_metrics = measurements[measurements["filename"].str.contains(file)]

        if not file_metrics.empty and "rt" in file_metrics.columns:
            try:
                rt = float(file_metrics["rt"].iloc[0])
                group_rt_values.append(rt)
            except (ValueError, TypeError) as e:
                message = f"Error processing retention time for {compound_name} in {file}: {e!s}"
                raise InvalidDataFormatError(message) from e

    if group_rt_values:
        try:
            avg_rt, rt_rsd = calculate_rt_metrics(group_rt_values)
            rt_deviation = None if expected_rt is None else avg_rt - expected_rt

            metrics = _evaluate_rt_metrics(rt=avg_rt, rt_rsd=rt_rsd, rt_deviation=rt_deviation, **thresholds)

            group_results.append({
                "compound": compound_name,
                "replicate_group": group_name,
                "retention_time": metrics.rt,
                "rt_rsd": metrics.rt_rsd,
                "rt_deviation": metrics.rt_deviation,
                "status": metrics.status,
                "message": metrics.message,
            })

            if rt_deviation is not None:
                all_rt_deviations.append(abs(rt_deviation))
            if rt_rsd is not None:
                all_rt_rsds.append(rt_rsd)
        except (ValueError, TypeError) as e:
            message = f"Error calculating retention time metrics for {compound_name}: {e!s}"
            raise InvalidDataFormatError(message) from e

    return group_results, group_rt_values, all_rt_deviations, all_rt_rsds


def _update_summary_statistics(
    results: dict[str, Any],
    all_rt_deviations: list[float],
    all_rt_rsds: list[float],
    target_compounds: pd.DataFrame,
) -> None:
    """Update summary statistics in the results dictionary."""
    if all_rt_deviations or all_rt_rsds:
        if all_rt_deviations:
            results["summary"].update({
                "average_rt_deviation": np.mean(all_rt_deviations),
                "rt_deviation_range": [np.min(all_rt_deviations), np.max(all_rt_deviations)],
            })

        if all_rt_rsds:
            results["summary"].update({
                "average_rt_rsd": np.mean(all_rt_rsds),
                "rt_rsd_range": [np.min(all_rt_rsds), np.max(all_rt_rsds)],
            })

        results["summary"].update({
            "compounds_checked": len(target_compounds),
            "compounds_passed": sum(1 for d in results["details"] if d["status"] == "pass"),
        })

        results["passed"] = all(d["status"] == "pass" for d in results["details"] if "status" in d)


def validate_retention_time(
    feature_table: MZMineFeatureTable,
    target_compounds: pd.DataFrame,
    replicate_groups: dict[str, list[str]],
    mz_tolerance: float = 0.1,
    rt_deviation_threshold: float = 0.1,  # minutes
    rt_rsd_threshold: float = 1.0,  # percent
    expected_rt_deviation_threshold: float = 0.5,  # minutes
) -> dict[str, Any]:
    """Validate retention time stability for target compounds.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        mz_tolerance: Tolerance for matching features
        rt_deviation_threshold: Maximum allowed RT deviation between replicates
        rt_rsd_threshold: Maximum allowed RT RSD between replicates
        expected_rt_deviation_threshold: Maximum allowed deviation from expected RT

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each measurement
            "summary": {  # Summary statistics
                "average_rt_deviation": float,
                "average_rt_rsd": float,
                "rt_deviation_range": [float, float],
                "rt_rsd_range": [float, float],
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
        message = f"Invalid input data for retention time validation: {e!s}"
        raise ValidationDataError(message) from e

    results = _initialize_results()
    thresholds = {
        "rt_rsd_threshold": rt_rsd_threshold,
        "rt_deviation_threshold": rt_deviation_threshold,
        "expected_rt_deviation_threshold": expected_rt_deviation_threshold,
    }

    all_rt_deviations = []
    all_rt_rsds = []

    for _, compound in target_compounds.iterrows():
        theoretical_mz = compound["mz"]
        compound_name = compound.get("name", f"m/z {theoretical_mz}")
        expected_rt = compound.get("rt")

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
                    group_results, rt_values, rt_devs, rt_rsds = _process_replicate_group(
                        feature_measurements,
                        files,
                        compound_name,
                        group_name,
                        expected_rt,
                        thresholds,
                    )

                    results["details"].extend(group_results)
                    all_rt_deviations.extend(rt_devs)
                    all_rt_rsds.extend(rt_rsds)
                except InvalidDataFormatError as e:
                    results["details"].append({
                        "compound": compound_name,
                        "status": "error",
                        "message": str(e),
                    })

    _update_summary_statistics(results, all_rt_deviations, all_rt_rsds, target_compounds)
    return results


def _process_reference_compound(
    feature_table: MZMineFeatureTable,
    reference_compound: pd.Series,
    replicate_groups: dict[str, list[str]],
    mz_tolerance: float,
) -> tuple[dict[str, float], str]:
    """Process reference compound and get its retention times by group.

    Args:
        feature_table: MZMine feature table
        reference_compound: Reference compound data
        replicate_groups: Dictionary mapping replicate groups to file names
        mz_tolerance: Tolerance for matching features

    Returns:
        Tuple of (reference_rt_by_group, reference_name)
    """
    reference_name = reference_compound.get("name", f"m/z {reference_compound['mz']}")
    reference_rt_by_group = {}

    reference_features = _find_matching_features(feature_table, reference_compound["mz"], mz_tolerance)
    if reference_features.empty:
        return {}, reference_name

    for _, feature in reference_features.iterrows():
        feature_measurements = feature_table.measurements[feature_table.measurements["feature_id"] == feature["id"]]
        for group_name, files in replicate_groups.items():
            group_rt_values = []
            for file in files:
                file_metrics = feature_measurements[feature_measurements["filename"].str.contains(file)]
                if not file_metrics.empty and "rt" in file_metrics.columns:
                    group_rt_values.append(file_metrics["rt"].iloc[0])
            if group_rt_values:
                reference_rt_by_group[group_name] = np.mean(group_rt_values)

    return reference_rt_by_group, reference_name


def _process_target_compound(
    feature_table: MZMineFeatureTable,
    compound: pd.Series,
    reference_rt_by_group: dict[str, float],
    replicate_groups: dict[str, list[str]],
    mz_tolerance: float,
    rsd_threshold: float,
    max_difference_threshold: float,
) -> dict[str, Any]:
    """Process a target compound and calculate its time differences.

    Args:
        feature_table: MZMine feature table
        compound: Target compound data
        reference_rt_by_group: Reference compound retention times by group
        replicate_groups: Dictionary mapping replicate groups to file names
        mz_tolerance: Tolerance for matching features
        rsd_threshold: Maximum allowed RSD
        max_difference_threshold: Maximum allowed difference

    Returns:
        Dictionary containing compound validation results
    """
    compound_name = compound.get("name", f"m/z {compound['mz']}")
    matching_features = _find_matching_features(feature_table, compound["mz"], mz_tolerance)

    if matching_features.empty:
        return {
            "compound": compound_name,
            "status": "not_found",
            "message": f"No matching feature found for {compound_name} (m/z {compound['mz']})",
        }

    time_differences = {}
    for _, feature in matching_features.iterrows():
        feature_measurements = feature_table.measurements[feature_table.measurements["feature_id"] == feature["id"]]
        for group_name, files in replicate_groups.items():
            if group_name not in reference_rt_by_group:
                continue
            group_rt_values = []
            for file in files:
                file_metrics = feature_measurements[feature_measurements["filename"].str.contains(file)]
                if not file_metrics.empty and "rt" in file_metrics.columns:
                    group_rt_values.append(file_metrics["rt"].iloc[0])
            if group_rt_values:
                time_differences[group_name] = np.mean(group_rt_values) - reference_rt_by_group[group_name]

    if not time_differences:
        return {
            "compound": compound_name,
            "status": "not_found",
            "message": f"Compound {compound_name} not found in any replicate group",
        }

    time_diff_values = list(time_differences.values())
    rsd = np.std(time_diff_values, ddof=1) / np.mean(time_diff_values) * 100 if len(time_diff_values) > 1 else 0.0
    max_difference = max(time_diff_values) - min(time_diff_values)

    metrics = _evaluate_rt_difference_metrics(
        time_differences=time_differences,
        rsd=rsd,
        max_difference=max_difference,
        rsd_threshold=rsd_threshold,
        max_difference_threshold=max_difference_threshold,
    )

    return {
        "compound": compound_name,
        "time_differences": time_differences,
        "rsd": rsd,
        "max_difference": max_difference,
        "status": metrics.status,
        "message": metrics.message,
    }


def _update_rt_difference_summary(results: dict[str, Any], target_compounds: pd.DataFrame) -> None:
    """Update summary statistics for retention time difference validation.

    Args:
        results: Validation results dictionary
        target_compounds: DataFrame containing target compounds
    """
    if results["details"]:
        results["summary"].update({
            "average_rsd": np.mean([d["rsd"] for d in results["details"] if "rsd" in d]),
            "max_difference": max(d["max_difference"] for d in results["details"] if "max_difference" in d),
            "compounds_checked": len(target_compounds) - 1,  # Exclude reference compound
            "compounds_passed": sum(1 for d in results["details"] if d.get("status") == "pass"),
        })
        results["passed"] = all(d.get("status") == "pass" for d in results["details"])


def validate_retention_time_differences(
    feature_table: MZMineFeatureTable,
    target_compounds: pd.DataFrame,
    replicate_groups: dict[str, list[str]],
    mz_tolerance: float = 0.1,
    rsd_threshold: float = 1.0,  # percent
    max_difference_threshold: float = 0.2,  # minutes
) -> dict[str, Any]:
    """Validate consistency of retention time differences between replicate groups.

    This function checks if the time difference between compounds remains consistent
    across replicate groups by comparing against the first compound as reference.

    Args:
        feature_table: MZMine feature table in standardized format
        target_compounds: DataFrame containing reference compound information
        replicate_groups: Dictionary mapping replicate groups to file names
        mz_tolerance: Tolerance for matching features
        rsd_threshold: Maximum allowed RSD of time differences across groups
        max_difference_threshold: Maximum allowed difference in time differences between groups

    Returns:
        Dictionary containing validation results with the following structure:
        {
            "passed": bool,  # Overall validation status
            "details": List[dict],  # Detailed results for each compound
            "summary": {  # Summary statistics
                "average_rsd": float,
                "max_difference": float,
                "compounds_checked": int,
                "compounds_passed": int,
                "reference_compound": str
            }
        }
    """
    results = _initialize_rt_difference_results()

    if target_compounds.empty:
        results["passed"] = False
        results["summary"]["reference_compound"] = "none"
        return results

    # Process reference compound
    reference_compound = target_compounds.iloc[0]
    reference_rt_by_group, reference_name = _process_reference_compound(
        feature_table, reference_compound, replicate_groups, mz_tolerance
    )
    results["summary"]["reference_compound"] = reference_name

    if not reference_rt_by_group:
        results["passed"] = False
        results["details"].append({
            "compound": reference_name,
            "status": "not_found",
            "message": f"Reference compound {reference_name} not found in any replicate group",
        })
        return results

    # Process target compounds
    for _, compound in target_compounds.iloc[1:].iterrows():
        compound_result = _process_target_compound(
            feature_table,
            compound,
            reference_rt_by_group,
            replicate_groups,
            mz_tolerance,
            rsd_threshold,
            max_difference_threshold,
        )
        results["details"].append(compound_result)

    # Update summary statistics
    _update_rt_difference_summary(results, target_compounds)

    return results
