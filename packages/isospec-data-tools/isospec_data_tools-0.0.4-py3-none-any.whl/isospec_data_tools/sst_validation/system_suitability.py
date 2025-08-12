import logging
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from isospec_data_tools.io_utils.mzmine import convert_mzmine_feature_table
from isospec_data_tools.sst_validation.errors import (
    ValidationConfigurationError,
    ValidationDataError,
)
from isospec_data_tools.sst_validation.metrics.mass_accuracy import validate_mass_accuracy
from isospec_data_tools.sst_validation.metrics.peak_shape import validate_peak_shape
from isospec_data_tools.sst_validation.metrics.resolution import validate_resolution
from isospec_data_tools.sst_validation.metrics.retention_time import (
    validate_retention_time,
    validate_retention_time_differences,
)
from isospec_data_tools.sst_validation.metrics.sensitivity import validate_sensitivity
from isospec_data_tools.visualization.sst_plots import (
    NoAsymmetryDataError,
    NoMassAccuracyDataError,
    NoPeakAreaDataError,
    NoPeakShapeResultsError,
    NoRetentionTimeDifferenceDataError,
    NoSensitivityResultsError,
    plot_asymmetry_histogram,
    plot_mass_accuracy_distribution,
    plot_peak_areas,
    plot_rt_differences_pyramid,
)


@dataclass
class ValidationThresholds:
    """Configuration class for system suitability validation thresholds.

    This class defines all the thresholds used for validating various aspects of LC-MS system performance.
    Default values are provided but can be customized based on specific instrument requirements.

    Attributes:
        mz_tolerance: Tolerance for matching features in m/z units (default: 0.6)
        mass_accuracy_ppm: Maximum allowed mass error in parts per million (default: 350.0)
        resolution_threshold: Minimum resolution required at m/z 200 (default: 30000)
        sn_ratio_high: Minimum signal-to-noise ratio for high-abundance metabolites (default: 100)
        sn_ratio_low: Minimum signal-to-noise ratio for low-abundance metabolites (default: 10)
        intensity_rsd_standards: Maximum relative standard deviation (%) for standard compounds (default: 15.0)
        intensity_rsd_endogenous: Maximum relative standard deviation (%) for endogenous compounds (default: 20.0)
        rt_deviation_minutes: Maximum retention time deviation between replicates in minutes (default: 0.1)
        rt_deviation_rsd: Maximum relative standard deviation (%) for retention times (default: 1.0)
        peak_asymmetry_min: Minimum acceptable peak asymmetry factor (default: 0.9)
        peak_asymmetry_max: Maximum acceptable peak asymmetry factor (default: 1.35)
        peak_tailing_min: Minimum acceptable tailing factor (default: 0.9)
        peak_tailing_max: Maximum acceptable tailing factor (default: 1.35)
        rt_difference_rsd: Maximum relative standard deviation (%) for time differences between groups (default: 1.0)
        rt_difference_max: Maximum allowed difference in time differences between groups in minutes (default: 0.01)
    """

    mz_tolerance: float = 0.6  # Tolerance for matching features
    mass_accuracy_ppm: float = 350.0  # Maximum allowed mass error in ppm
    resolution_threshold: float = 30000  # Minimum resolution at m/z 200
    sn_ratio_high: float = 100  # Minimum S/N for high-abundance metabolites
    sn_ratio_low: float = 10  # Minimum S/N for low-abundance metabolites
    intensity_rsd_standards: float = 15.0  # Maximum RSD% for standards
    intensity_rsd_endogenous: float = 20.0  # Maximum RSD% for endogenous compounds
    rt_deviation_minutes: float = 0.1  # Maximum RT deviation in minutes
    rt_deviation_rsd: float = 1.0  # Maximum RT RSD%
    peak_asymmetry_min: float = 0.9  # Minimum peak asymmetry
    peak_asymmetry_max: float = 1.35  # Maximum peak asymmetry
    peak_tailing_min: float = 0.9  # Minimum tailing factor
    peak_tailing_max: float = 1.35  # Maximum tailing factor
    rt_difference_rsd: float = 1.0  # Maximum RSD% for time differences between groups
    rt_difference_max: float = 0.01  # Maximum allowed difference in time differences between groups


class SystemSuitability:
    def __init__(
        self,
        acquisition_list_path: str | Path,
        feature_table_path: str | Path,
        endogenous_compounds_path: str | Path,
        exogenous_compounds_path: str | Path,
        thresholds: ValidationThresholds | None = None,
    ) -> None:
        """Initialize the SystemSuitability checker.

        Args:
            acquisition_list_path: Path to the acquisition list CSV
            feature_table_path: Path to the MZmine feature table CSV
            endogenous_compounds_path: Path to endogenous compounds list CSV
            exogenous_compounds_path: Path to exogenous compounds list CSV
            thresholds: Optional custom validation thresholds
        """
        self.thresholds = thresholds or ValidationThresholds()
        self.acquisition_data = pd.read_csv(str(acquisition_list_path))
        self.feature_table = convert_mzmine_feature_table(pd.read_csv(str(feature_table_path)))
        self.endogenous_compounds = pd.read_csv(str(endogenous_compounds_path))
        self.exogenous_compounds = pd.read_csv(str(exogenous_compounds_path))
        self.validation_results: dict[str, dict] = {}

    def get_replicate_groups(self) -> dict[str, list[str]]:
        """Group samples by their replicates."""
        groups = self.acquisition_data.groupby("replicate_group")["sample"].apply(list).to_dict()
        return cast(dict[str, list[str]], groups)

    def validate_mass_accuracy(self) -> dict:
        """Validate mass accuracy for target compounds."""
        # Combine endogenous and exogenous compounds
        all_compounds = pd.concat([self.endogenous_compounds, self.exogenous_compounds]).reset_index(drop=True)

        return validate_mass_accuracy(
            feature_table=self.feature_table,
            target_compounds=all_compounds,
            replicate_groups=self.get_replicate_groups(),
            mass_accuracy_threshold=self.thresholds.mass_accuracy_ppm,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

    def validate_resolution(self) -> dict:
        """Validate mass resolution using FWHM."""
        # Combine endogenous and exogenous compounds
        all_compounds = pd.concat([self.endogenous_compounds, self.exogenous_compounds]).reset_index(drop=True)

        return validate_resolution(
            feature_table=self.feature_table,
            target_compounds=all_compounds,
            replicate_groups=self.get_replicate_groups(),
            resolution_threshold=self.thresholds.resolution_threshold,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

    def validate_sensitivity(self) -> dict:
        """Validate sensitivity and signal intensity."""
        # Process standards (exogenous compounds)
        exogenous_results = validate_sensitivity(
            feature_table=self.feature_table,
            target_compounds=self.exogenous_compounds,
            replicate_groups=self.get_replicate_groups(),
            sn_ratio_high=self.thresholds.sn_ratio_high,
            sn_ratio_low=self.thresholds.sn_ratio_low,
            intensity_rsd_threshold=self.thresholds.intensity_rsd_standards,
            is_standard=True,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

        # Process endogenous compounds
        endogenous_results = validate_sensitivity(
            feature_table=self.feature_table,
            target_compounds=self.endogenous_compounds,
            replicate_groups=self.get_replicate_groups(),
            sn_ratio_high=self.thresholds.sn_ratio_high,
            sn_ratio_low=self.thresholds.sn_ratio_low,
            intensity_rsd_threshold=self.thresholds.intensity_rsd_endogenous,
            is_standard=False,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

        # Combine results
        combined_results = {
            "passed": exogenous_results["passed"] and endogenous_results["passed"],
            "details": exogenous_results["details"] + endogenous_results["details"],
            "summary": {
                "average_sn_ratio": np.mean([
                    exogenous_results["summary"]["average_sn_ratio"],
                    endogenous_results["summary"]["average_sn_ratio"],
                ]),
                "sn_ratio_range": [
                    min(
                        exogenous_results["summary"]["sn_ratio_range"][0],
                        endogenous_results["summary"]["sn_ratio_range"][0],
                    ),
                    max(
                        exogenous_results["summary"]["sn_ratio_range"][1],
                        endogenous_results["summary"]["sn_ratio_range"][1],
                    ),
                ],
                "average_intensity_rsd": np.mean([
                    exogenous_results["summary"]["average_intensity_rsd"],
                    endogenous_results["summary"]["average_intensity_rsd"],
                ]),
                "intensity_rsd_range": [
                    min(
                        exogenous_results["summary"]["intensity_rsd_range"][0],
                        endogenous_results["summary"]["intensity_rsd_range"][0],
                    ),
                    max(
                        exogenous_results["summary"]["intensity_rsd_range"][1],
                        endogenous_results["summary"]["intensity_rsd_range"][1],
                    ),
                ],
                "compounds_checked": (
                    exogenous_results["summary"]["compounds_checked"]
                    + endogenous_results["summary"]["compounds_checked"]
                ),
                "compounds_passed": (
                    exogenous_results["summary"]["compounds_passed"] + endogenous_results["summary"]["compounds_passed"]
                ),
            },
        }

        # Combine failure reasons if any
        failure_reasons = []
        if "failure_reason" in exogenous_results["summary"]:
            failure_reasons.append(f"Standards: {exogenous_results['summary']['failure_reason']}")
        if "failure_reason" in endogenous_results["summary"]:
            failure_reasons.append(f"Endogenous: {endogenous_results['summary']['failure_reason']}")

        if failure_reasons:
            combined_results["summary"]["failure_reason"] = "; ".join(failure_reasons)

        return combined_results

    def validate_retention_time(self) -> dict:
        """Validate retention time stability."""
        # Combine endogenous and exogenous compounds
        all_compounds = pd.concat([self.endogenous_compounds, self.exogenous_compounds]).reset_index(drop=True)

        return validate_retention_time(
            feature_table=self.feature_table,
            target_compounds=all_compounds,
            replicate_groups=self.get_replicate_groups(),
            rt_deviation_threshold=self.thresholds.rt_deviation_minutes,
            rt_rsd_threshold=self.thresholds.rt_deviation_rsd,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

    def validate_retention_time_differences(self) -> dict:
        """Validate consistency of retention time differences between replicate groups."""
        # Combine endogenous and exogenous compounds
        all_compounds = pd.concat([self.endogenous_compounds, self.exogenous_compounds]).reset_index(drop=True)

        return validate_retention_time_differences(
            feature_table=self.feature_table,
            target_compounds=all_compounds,
            replicate_groups=self.get_replicate_groups(),
            rsd_threshold=self.thresholds.rt_difference_rsd,
            max_difference_threshold=self.thresholds.rt_difference_max,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

    def validate_peak_shape(self) -> dict:
        """Validate peak shape metrics."""
        # Combine endogenous and exogenous compounds
        all_compounds = pd.concat([self.endogenous_compounds, self.exogenous_compounds]).reset_index(drop=True)

        return validate_peak_shape(
            feature_table=self.feature_table,
            target_compounds=all_compounds,
            replicate_groups=self.get_replicate_groups(),
            asymmetry_min=self.thresholds.peak_asymmetry_min,
            asymmetry_max=self.thresholds.peak_asymmetry_max,
            tailing_min=self.thresholds.peak_tailing_min,
            tailing_max=self.thresholds.peak_tailing_max,
            mz_tolerance=self.thresholds.mz_tolerance,
        )

    def run_all_validations(self) -> dict:
        """Run all system suitability validations."""
        self.validation_results = {
            "mass_accuracy": self.validate_mass_accuracy(),
            "resolution": self.validate_resolution(),
            "sensitivity": self.validate_sensitivity(),
            "retention_time": self.validate_retention_time(),
            "retention_time_differences": self.validate_retention_time_differences(),
            "peak_shape": self.validate_peak_shape(),
        }

        # Overall pass/fail status
        all_passed = all(v["passed"] for v in self.validation_results.values())

        return {"passed": all_passed, "results": self.validation_results}

    def _format_summary_value(self, value: Any) -> str:
        """Format a summary value for display.

        Args:
            value: The value to format

        Returns:
            Formatted string representation of the value
        """
        if isinstance(value, int | float):
            return f"{value:.2f}"
        if isinstance(value, list):
            return f"[{value[0]:.2f}, {value[1]:.2f}]"
        return str(value)

    def _format_validation_details(self, details: list[dict[str, Any]]) -> list[str]:
        """Format validation details for display.

        Args:
            details: List of validation detail dictionaries

        Returns:
            List of formatted detail strings
        """
        formatted_details = []
        for detail in details:
            if "status" in detail and "message" in detail:
                formatted_details.append(f"- {detail['compound']}: {detail['status'].upper()} - {detail['message']}")
        return formatted_details

    def _format_thresholds(self) -> list[str]:
        """Format threshold values for display.

        Returns:
            List of formatted threshold strings
        """
        return [
            f"- {field.name.replace('_', ' ').title()}: {getattr(self.thresholds, field.name)}"
            for field in fields(self.thresholds)
        ]

    def _generate_validation_section(self, validation_type: str, results: dict[str, Any]) -> list[str]:
        """Generate a section of the validation report.

        Args:

            validation_type: Type of validation
            results: Validation results dictionary

        Returns:
            List of formatted section strings
        """
        sections = []
        status = "PASSED" if results["passed"] else "FAILED"
        sections.append(f"### {validation_type.replace('_', ' ').title()}: {status}\n")

        if "summary" in results:
            sections.append("#### Summary Statistics\n")
            for key, value in results["summary"].items():
                sections.append(f"- {key.replace('_', ' ').title()}: {self._format_summary_value(value)}")

        if results["details"]:
            sections.append("\n#### Detailed Results\n")
            sections.extend(self._format_validation_details(results["details"]))

        sections.append("\n")
        return sections

    def generate_report(self, output_path: str | None = None) -> str:
        """Generate a detailed report of the validation results.

        Args:
            output_path: Optional path to save the report. If None, returns the report as a string.

        Returns:
            A formatted string containing the validation report.

        Raises:
            ValidationDataError: If validation results are not available
            ValidationConfigurationError: If output path is invalid
        """
        if not self.validation_results:
            message = "No validation results available. Run run_all_validations() first."
            raise ValidationDataError(message)

        sections = []
        sections.append("# System Suitability Validation Report\n")
        sections.append(f"## Overall Status: {(self.validation_results['passed'] and 'PASSED') or 'FAILED'}\n")
        sections.append("## Validation Results\n")

        for validation_type, results in self.validation_results["results"].items():
            sections.extend(self._generate_validation_section(validation_type, results))

        sections.append("## Validation Thresholds\n")
        sections.extend(self._format_thresholds())

        report = "\n".join(sections)

        if output_path:
            try:
                with open(output_path, "w") as f:
                    f.write(report)
            except OSError as e:
                message = f"Failed to save report to {output_path}: {e!s}"
                raise ValidationConfigurationError(message) from e
            else:
                return f"Report saved to {output_path}"

        return report

    def _generate_peak_area_plot(self, output_dir: Path) -> None:
        """Generate peak area plot.

        Args:
            output_dir: Directory to save the plot
        """
        try:
            peak_area_path = str(output_dir / "peak_areas.png")
            plot_peak_areas(validation_results=self.validation_results, output_path=peak_area_path)
        except (NoSensitivityResultsError, NoPeakAreaDataError) as e:
            logging.warning(f"Could not generate peak areas plot: {e}")

    def _generate_asymmetry_plot(self, output_dir: Path) -> None:
        """Generate asymmetry histogram plot.

        Args:
            output_dir: Directory to save the plot
        """
        try:
            asymmetry_path = str(output_dir / "asymmetry_histogram.png")
            plot_asymmetry_histogram(validation_results=self.validation_results, output_path=asymmetry_path)
        except (NoPeakShapeResultsError, NoAsymmetryDataError) as e:
            logging.warning(f"Could not generate asymmetry histogram: {e}")

    def _generate_mass_accuracy_plot(self, output_dir: Path) -> None:
        """Generate mass accuracy distribution plot.

        Args:
            output_dir: Directory to save the plot
        """
        try:
            mass_accuracy_path = str(output_dir / "mass_accuracy_distribution.png")
            plot_mass_accuracy_distribution(validation_results=self.validation_results, output_path=mass_accuracy_path)
        except NoMassAccuracyDataError as e:
            logging.warning(f"Could not generate mass accuracy distribution plot: {e}")

    def _generate_rt_differences_plot(self, output_dir: Path) -> None:
        """Generate retention time differences pyramid plot.

        Args:
            output_dir: Directory to save the plot
        """
        try:
            rt_diff_pyramid_path = str(output_dir / "rt_differences_pyramid.png")
            plot_rt_differences_pyramid(validation_results=self.validation_results, output_path=rt_diff_pyramid_path)
        except NoRetentionTimeDifferenceDataError as e:
            logging.warning(f"Could not generate retention time differences pyramid plot: {e}")

    def generate_plots(self, output_dir: str | Path | None = None) -> None:
        """Generate visualization plots for the system suitability test results.

        Args:
            output_dir: Directory to save the plots. If None, plots will be displayed.
        """
        # Ensure we have validation results
        if not self.validation_results:
            self.run_all_validations()

        if output_dir is not None:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate all plots
            self._generate_peak_area_plot(output_dir)
            self._generate_asymmetry_plot(output_dir)
            self._generate_mass_accuracy_plot(output_dir)
            self._generate_rt_differences_plot(output_dir)

        else:
            # If no output_dir, display plots
            try:
                self._generate_peak_area_plot(Path("."))
            except (NoSensitivityResultsError, NoPeakAreaDataError) as e:
                logging.warning(f"Could not display peak areas plot: {e}")

            try:
                self._generate_asymmetry_plot(Path("."))
            except (NoPeakShapeResultsError, NoAsymmetryDataError) as e:
                logging.warning(f"Could not display asymmetry histogram: {e}")

            try:
                self._generate_mass_accuracy_plot(Path("."))
            except NoMassAccuracyDataError as e:
                logging.warning(f"Could not display mass accuracy distribution plot: {e}")

            try:
                self._generate_rt_differences_plot(Path("."))
            except NoRetentionTimeDifferenceDataError as e:
                logging.warning(f"Could not display retention time differences pyramid plot: {e}")
