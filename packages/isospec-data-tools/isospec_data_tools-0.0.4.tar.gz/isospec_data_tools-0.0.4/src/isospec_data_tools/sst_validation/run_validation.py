#!/usr/bin/env python3

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from isospec_data_tools.sst_validation.report.report_generator import ValidationReportGenerator
from isospec_data_tools.sst_validation.system_suitability import SystemSuitability


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def validate_inputs(
    acquisition_list_path: str | Path,
    feature_table_path: str | Path,
    endogenous_compounds_path: str | Path,
    exogenous_compounds_path: str | Path,
) -> bool:
    """Validate that all input files exist and are readable.

    Args:
        acquisition_list_path: Path to acquisition list CSV
        feature_table_path: Path to feature table CSV
        endogenous_compounds_path: Path to endogenous compounds CSV
        exogenous_compounds_path: Path to exogenous compounds CSV

    Returns:
        True if all files are valid, False otherwise
    """
    files_to_check = [
        (acquisition_list_path, "Acquisition list"),
        (feature_table_path, "Feature table"),
        (endogenous_compounds_path, "Endogenous compounds list"),
        (exogenous_compounds_path, "Exogenous compounds list"),
    ]

    all_valid = True
    for file_path, file_desc in files_to_check:
        path = Path(file_path)
        if not path.exists():
            logging.error(f"{file_desc} file not found: {file_path}")
            all_valid = False
        elif not path.is_file():
            logging.error(f"{file_desc} path is not a file: {file_path}")
            all_valid = False
        elif path.suffix.lower() != ".csv":
            logging.error(f"{file_desc} file is not a CSV file: {file_path}")
            all_valid = False

    return all_valid


def main() -> None:
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(description="Run system suitability validation for LC-MS data")

    parser.add_argument("--acquisition-list", required=True, help="Path to the acquisition list CSV file")
    parser.add_argument("--feature-table", required=True, help="Path to the MZmine feature table CSV file")
    parser.add_argument("--endogenous-compounds", required=True, help="Path to the endogenous compounds list CSV file")
    parser.add_argument("--exogenous-compounds", required=True, help="Path to the exogenous compounds list CSV file")
    parser.add_argument(
        "--output-dir",
        default="validation_reports",
        help="Directory to save validation reports (default: validation_reports)",
    )
    parser.add_argument(
        "--instrument-type",
        choices=["orbitrap", "qtof"],
        default="orbitrap",
        help="Type of mass spectrometer (default: orbitrap)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Validate input files
    if not validate_inputs(
        args.acquisition_list, args.feature_table, args.endogenous_compounds, args.exogenous_compounds
    ):
        sys.exit(1)

    try:
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize system suitability checker
        logging.info("Initializing system suitability validation...")
        validator = SystemSuitability(
            acquisition_list_path=args.acquisition_list,
            feature_table_path=args.feature_table,
            endogenous_compounds_path=args.endogenous_compounds,
            exogenous_compounds_path=args.exogenous_compounds,
        )

        # Run validation
        logging.info("Running validation checks...")
        validation_results = validator.run_all_validations()

        # Generate report
        logging.info("Generating validation report...")
        report_generator = ValidationReportGenerator(validation_results)

        # Create timestamped output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"system_suitability_report_{timestamp}.md"

        # Generate report and save to file
        report_generator.generate_report(str(report_path))
        validator.generate_plots(output_dir=str(output_dir))

        logging.info(f"Validation complete. Report saved to: {report_path}")
        logging.info(f"Results JSON saved to: {report_path.with_suffix('.json')}")

        # Exit with status code based on validation result
        sys.exit(0 if validation_results["passed"] else 1)

    except Exception as e:
        logging.error(f"An error occurred during validation: {e!s}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
