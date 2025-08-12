import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        """Convert numpy types to Python native types.

        Args:
            obj: Object to convert

        Returns:
            Converted object
        """
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if np.isnan(obj):
            return None
        return super().default(obj)


class ValidationReportGenerator:
    def __init__(self, validation_results: dict[str, Any]) -> None:
        """Initialize the report generator.

        Args:
            validation_results: Dictionary containing validation results from all checks
        """
        self.validation_results = validation_results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report_sections: list[str] = []

    def generate_summary_section(self) -> str:
        """Generate the summary section of the report."""
        overall_status = "✅ PASSED" if self.validation_results["passed"] else "❌ FAILED"

        summary = [
            "# System Suitability Report",
            f"Generated on: {self.timestamp}",
            f"\n## Overall Status: {overall_status}\n",
            "### Summary of Validation Checks",
        ]

        for check_name, check_results in self.validation_results["results"].items():
            status = "✅ PASSED" if check_results["passed"] else "❌ FAILED"
            summary.append(f"- {check_name.replace('_', ' ').title()}: {status}")
            if not check_results["passed"] and "failure_reason" in check_results["summary"]:
                summary.append(f"  - Reason: {check_results['summary']['failure_reason']}")

        return "\n".join(summary)

    def generate_mass_accuracy_section(self) -> str:
        """Generate the mass accuracy section of the report."""
        results = self.validation_results["results"].get("mass_accuracy", {})
        if not results:
            return ""

        section = ["\n## Mass Accuracy Validation", f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n"]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- Average Mass Error: {summary['average_mass_error']:.2f} ppm",
            f"- Mass Error Range: {summary['mass_error_range'][0]:.2f} - {summary['mass_error_range'][1]:.2f} ppm",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']} ({detail['file']}): {detail['message']}")

        return "\n".join(section)

    def generate_resolution_section(self) -> str:
        """Generate the resolution section of the report."""
        results = self.validation_results["results"].get("resolution", {})
        if not results:
            return ""

        section = ["\n## Mass Resolution Validation", f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n"]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- Average Resolution: {summary['average_resolution']:.0f}",
            f"- Resolution Range: {summary['resolution_range'][0]:.0f} - {summary['resolution_range'][1]:.0f}",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']} ({detail['file']}): {detail['message']}")

        return "\n".join(section)

    def generate_sensitivity_section(self) -> str:
        """Generate the sensitivity section of the report."""
        results = self.validation_results["results"].get("sensitivity", {})
        if not results:
            return ""

        section = [
            "\n## Sensitivity and Signal Intensity Validation",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n",
        ]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- Average S/N Ratio: {summary['average_sn_ratio']:.1f}",
            f"- S/N Ratio Range: {summary['sn_ratio_range'][0]:.1f} - {summary['sn_ratio_range'][1]:.1f}",
            f"- Average Intensity RSD: {summary['average_intensity_rsd']:.1f}%",
            f"- Intensity RSD Range: {summary['intensity_rsd_range'][0]:.1f}% - {summary['intensity_rsd_range'][1]:.1f}%",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']}: {detail['message']}")

        return "\n".join(section)

    def generate_retention_time_section(self) -> str:
        """Generate the retention time section of the report."""
        results = self.validation_results["results"].get("retention_time", {})
        if not results:
            return ""

        section = [
            "\n## Retention Time Stability Validation",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n",
        ]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- RT Deviation Range: {summary['rt_deviation_range'][0]:.3f} - {summary['rt_deviation_range'][1]:.3f} min",
            f"- RT RSD Range: {summary['rt_rsd_range'][0]:.1f}% - {summary['rt_rsd_range'][1]:.1f}%",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']} ({detail['replicate_group']}): {detail['message']}")

        return "\n".join(section)

    def generate_retention_time_differences_section(self) -> str:
        """Generate the retention time differences section of the report."""
        results = self.validation_results["results"].get("retention_time_differences", {})
        if not results:
            return ""

        section = [
            "\n## Retention Time Differences Validation",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n",
        ]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- Reference Compound: {summary['reference_compound']}",
            f"- Average RSD of Time Differences: {summary['average_rsd']:.2f}%",
            f"- Maximum Difference Between Groups: {summary['max_difference']:.3f} min",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']}: {detail['message']}")
                    if "time_differences" in detail:
                        section.append("  Time Differences by Group:")
                        for group, diff in detail["time_differences"].items():
                            section.append(f"    - {group}: {diff:.3f} min")

        return "\n".join(section)

    def generate_peak_shape_section(self) -> str:
        """Generate the peak shape section of the report."""
        results = self.validation_results["results"].get("peak_shape", {})
        if not results:
            return ""

        section = ["\n## Peak Shape Validation", f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}\n"]

        # Add summary statistics
        summary = results["summary"]
        section.extend([
            "### Summary Statistics",
            f"- Average Asymmetry Factor: {summary['average_asymmetry']:.2f}",
            f"- Asymmetry Range: {summary['asymmetry_range'][0]:.2f} - {summary['asymmetry_range'][1]:.2f}",
            f"- Average Tailing Factor: {summary['average_tailing']:.2f}",
            f"- Tailing Range: {summary['tailing_range'][0]:.2f} - {summary['tailing_range'][1]:.2f}",
            f"- Compounds Checked: {summary['compounds_checked']}",
            f"- Compounds Passed: {summary['compounds_passed']}",
        ])

        # Add detailed results
        if results["details"]:
            section.append("\n### Detailed Results")
            for detail in results["details"]:
                if detail["status"] == "not_found":
                    section.append(f"- ⚠️ {detail['message']}")
                else:
                    icon = "✅" if detail["status"] == "pass" else "❌"
                    section.append(f"- {icon} {detail['compound']} ({detail['replicate_group']}): {detail['message']}")

        return "\n".join(section)

    def generate_report(self, output_path: str | None = None) -> str:
        """Generate the complete validation report.

        Args:
            output_path: Optional path to save the report to

        Returns:
            The complete report as a string
        """
        report_sections = [
            self.generate_summary_section(),
            self.generate_mass_accuracy_section(),
            self.generate_resolution_section(),
            self.generate_sensitivity_section(),
            self.generate_retention_time_section(),
            self.generate_retention_time_differences_section(),
            self.generate_peak_shape_section(),
        ]

        report = "\n".join(section for section in report_sections if section)

        if output_path:
            Path(output_path).write_text(report)

            # Also save the raw results as JSON for potential further processing
            json_path = Path(output_path).with_suffix(".json")
            json_path.write_text(json.dumps(self.validation_results, indent=2, cls=NumpyEncoder))

        return report
