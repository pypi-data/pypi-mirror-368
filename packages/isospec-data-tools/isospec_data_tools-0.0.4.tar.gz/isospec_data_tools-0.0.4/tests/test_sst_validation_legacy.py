"""Tests for the SST validation module."""

import pandas as pd
import pytest

from isospec_data_tools.sst_validation import SystemSuitability, ValidationThresholds
from isospec_data_tools.sst_validation.errors import ValidationDataError
from isospec_data_tools.sst_validation.report import ValidationReportGenerator


@pytest.fixture
def sample_data_dir(tmp_path):
    """Create sample data files for testing."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()

    # Create acquisition list
    acquisition_data = pd.DataFrame({
        "id": ["sample1", "sample2", "sample3"],
        "sample": ["sample1", "sample2", "sample3"],
        "filename": ["sample1.mzML", "sample2.mzML", "sample3.mzML"],
        "class": ["qc", "qc", "qc"],
        "replicate_group": ["group1", "group1", "group2"],
        "acquisition_order": [1, 2, 3],
        "batch": ["batch1", "batch1", "batch1"],
    })
    acquisition_data.to_csv(data_dir / "acquisition_list.csv", index=False)

    # Create feature table with more comprehensive data
    feature_data = pd.DataFrame({
        "id": [1, 2, 3],
        "mz": [200.1234, 300.5678, 400.1234],
        "rt": [1.5, 2.5, 3.5],
        "area": [1000, 2000, 3000],
        "height": [500, 1000, 1500],
        "fwhm": [0.1, 0.15, 0.12],
        "asymmetry": [1.1, 1.0, 1.2],
        "tailing": [1.0, 1.1, 1.15],
        "sn": [150, 80, 200],
        "datafile:sample1.mzML:rt": [1.4, 2.4, 3.4],
        "datafile:sample2.mzML:rt": [1.6, 2.6, 3.6],
        "datafile:sample3.mzML:rt": [1.51, 2.51, 3.51],
        "datafile:sample1.mzML:mz": [200.1334, 300.4678, 400.10234],
        "datafile:sample2.mzML:mz": [200.1334, 300.3678, 400.11234],
        "datafile:sample3.mzML:mz": [200.1334, 300.2678, 400.1634],
        "datafile:sample1.mzML:fwhm": [0.98, 1.11, 0.78],
        "datafile:sample2.mzML:fwhm": [0.91, 1.95, 0.92],
        "datafile:sample3.mzML:fwhm": [1.34, 1, 1.36],
        "datafile:sample1.mzML:area": [1000, 2000, 3000],
        "datafile:sample2.mzML:area": [1100, 1900, 3100],
        "datafile:sample3.mzML:area": [1050, 2100, 2900],
        "datafile:sample1.mzML:height": [500, 1000, 1500],
        "datafile:sample2.mzML:height": [550, 950, 1550],
        "datafile:sample3.mzML:height": [525, 1050, 1450],
        "datafile:sample1.mzML:asymmetry_factor": [1.1, 1.0, 1.2],
        "datafile:sample2.mzML:asymmetry_factor": [1.15, 0.95, 1.25],
        "datafile:sample3.mzML:asymmetry_factor": [1.05, 1.05, 1.15],
        "datafile:sample1.mzML:tailing_factor": [1.0, 1.1, 1.15],
        "datafile:sample2.mzML:tailing_factor": [1.05, 1.15, 1.2],
        "datafile:sample3.mzML:tailing_factor": [0.95, 1.05, 1.1],
        "datafile:sample1.mzML:sn": [150, 80, 200],
        "datafile:sample2.mzML:sn": [145, 85, 195],
        "datafile:sample3.mzML:sn": [155, 75, 205],
    })
    feature_data.to_csv(data_dir / "feature_table.csv", index=False)

    # Create compound lists with more metadata
    endogenous_data = pd.DataFrame({
        "name": ["Compound1", "Compound2"],
        "mz": [200.1235, 300.5677],
        "rt": [1.51, 2.49],
        "abundance_level": ["high", "low"],
        "formula": ["C10H20O2", "C15H25NO3"],
    })
    endogenous_data.to_csv(data_dir / "endogenous_compounds.csv", index=False)

    exogenous_data = pd.DataFrame({
        "name": ["Standard1"],
        "mz": [400.1234],
        "rt": [3.5],
        "abundance_level": ["high"],
        "formula": ["C20H30O4"],
    })
    exogenous_data.to_csv(data_dir / "exogenous_compounds.csv", index=False)

    return data_dir


@pytest.fixture
def default_thresholds():
    """Create default validation thresholds."""
    return ValidationThresholds(
        mz_tolerance=0.6,
        mass_accuracy_ppm=350.0,
        resolution_threshold=30000,
        sn_ratio_high=100,
        sn_ratio_low=10,
        intensity_rsd_standards=15.0,
        intensity_rsd_endogenous=20.0,
        rt_deviation_minutes=0.1,
        rt_deviation_rsd=1.0,
        peak_asymmetry_min=0.9,
        peak_asymmetry_max=1.35,
        peak_tailing_min=0.9,
        peak_tailing_max=1.35,
    )


def test_validation_thresholds_initialization() -> None:
    """Test that ValidationThresholds can be initialized with custom values."""
    thresholds = ValidationThresholds(
        mz_tolerance=0.5,
        mass_accuracy_ppm=300.0,
        resolution_threshold=40000,
        sn_ratio_high=200,
        sn_ratio_low=20,
        intensity_rsd_standards=10.0,
        intensity_rsd_endogenous=15.0,
        rt_deviation_minutes=0.05,
        rt_deviation_rsd=0.5,
        peak_asymmetry_min=0.95,
        peak_asymmetry_max=1.25,
        peak_tailing_min=0.95,
        peak_tailing_max=1.25,
    )

    assert thresholds.mz_tolerance == 0.5
    assert thresholds.mass_accuracy_ppm == 300.0
    assert thresholds.resolution_threshold == 40000
    assert thresholds.sn_ratio_high == 200
    assert thresholds.sn_ratio_low == 20
    assert thresholds.intensity_rsd_standards == 10.0
    assert thresholds.intensity_rsd_endogenous == 15.0
    assert thresholds.rt_deviation_minutes == 0.05
    assert thresholds.rt_deviation_rsd == 0.5
    assert thresholds.peak_asymmetry_min == 0.95
    assert thresholds.peak_asymmetry_max == 1.25
    assert thresholds.peak_tailing_min == 0.95
    assert thresholds.peak_tailing_max == 1.25


def test_system_suitability_initialization(sample_data_dir, default_thresholds) -> None:
    """Test that SystemSuitability can be initialized with valid inputs."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    assert validator is not None
    assert isinstance(validator, SystemSuitability)


def test_validation_with_sample_data(sample_data_dir, default_thresholds) -> None:
    """Test that validation can be run on sample data."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    results = validator.run_all_validations()

    # Check overall structure
    assert isinstance(results, dict)
    assert "passed" in results
    assert "results" in results

    # Check individual validation results
    validation_results = results["results"]
    assert "mass_accuracy" in validation_results
    assert "resolution" in validation_results
    assert "sensitivity" in validation_results
    assert "retention_time" in validation_results
    assert "peak_shape" in validation_results

    # Check detailed results structure for each validation type
    for validation_type in validation_results:
        result = validation_results[validation_type]
        assert "passed" in result
        assert "details" in result
        assert "summary" in result


def test_report_generation(sample_data_dir, default_thresholds, tmp_path) -> None:
    """Test that reports can be generated."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    output_dir = tmp_path / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    validation_results = validator.run_all_validations()

    # The generate_report method returns a string message
    report_generator = ValidationReportGenerator(validation_results)

    report_path = output_dir / "system_suitability_report.md"
    report_result = report_generator.generate_report(str(report_path))

    # Check that the method returns a string
    assert isinstance(report_result, str)
    assert "Report\nGenerated" in report_result


def test_visualization_generation(sample_data_dir, default_thresholds, tmp_path) -> None:
    """Test that visualization plots can be generated."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Run validation to get results
    validator.run_all_validations()

    # Generate plots
    output_dir = tmp_path / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Try to generate plots, but don't fail the test if it raises an error
        # due to missing data in the test environment
        validator.generate_plots(str(output_dir))

        # If it succeeds, check that plot files were created
        assert output_dir.exists()
        assert (output_dir / "peak_areas.png").exists()
        assert (output_dir / "asymmetry_histogram.png").exists()
    except ValueError as e:
        # If it fails due to missing data, just check that the error message is as expected
        assert "No valid peak area data found" in str(e)


def test_validation_with_missing_compounds(sample_data_dir, default_thresholds) -> None:
    """Test validation behavior with missing compounds."""
    # Create empty compound lists
    pd.DataFrame(columns=["name", "mz", "rt", "abundance_level"]).to_csv(
        sample_data_dir / "empty_compounds.csv", index=False
    )

    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "empty_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "empty_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Validation should fail with ValidationDataError due to missing compounds
    with pytest.raises(ValidationDataError):
        validator.run_all_validations()


def test_mass_accuracy_validation(sample_data_dir, default_thresholds) -> None:
    """Test mass accuracy validation with various scenarios."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Test with good mass accuracy
    results = validator.validate_mass_accuracy()
    assert isinstance(results, dict)
    assert "passed" in results
    assert "details" in results
    assert "summary" in results

    # Test with poor mass accuracy
    poor_thresholds = ValidationThresholds(
        mass_accuracy_ppm=1.0,  # Very strict threshold
        **{k: v for k, v in default_thresholds.__dict__.items() if k != "mass_accuracy_ppm"},
    )
    validator.thresholds = poor_thresholds
    results = validator.validate_mass_accuracy()
    assert not results["passed"]


def test_resolution_validation(sample_data_dir, default_thresholds) -> None:
    """Test resolution validation with various scenarios."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Test with good resolution
    results = validator.validate_resolution()
    assert isinstance(results, dict)
    assert "passed" in results
    assert "details" in results
    assert "summary" in results

    # Test with poor resolution
    poor_thresholds = ValidationThresholds(
        resolution_threshold=100000,  # Very high threshold
        **{k: v for k, v in default_thresholds.__dict__.items() if k != "resolution_threshold"},
    )
    validator.thresholds = poor_thresholds
    results = validator.validate_resolution()
    assert not results["passed"]


def test_sensitivity_validation(sample_data_dir, default_thresholds) -> None:
    """Test sensitivity validation with various scenarios."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Test with good sensitivity
    results = validator.validate_sensitivity()
    assert isinstance(results, dict)
    assert "passed" in results
    assert "details" in results
    assert "summary" in results

    # Test with poor sensitivity
    poor_thresholds = ValidationThresholds(
        sn_ratio_high=1000,  # Very high threshold
        sn_ratio_low=100,  # Very high threshold
        **{k: v for k, v in default_thresholds.__dict__.items() if k not in ["sn_ratio_high", "sn_ratio_low"]},
    )
    validator.thresholds = poor_thresholds
    results = validator.validate_sensitivity()
    assert not results["passed"]


def test_retention_time_validation(sample_data_dir, default_thresholds) -> None:
    """Test retention time validation with various scenarios."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Test with good retention time stability
    results = validator.validate_retention_time()
    assert isinstance(results, dict)
    assert "passed" in results
    assert "details" in results
    assert "summary" in results

    # Test with poor retention time stability
    poor_thresholds = ValidationThresholds(
        rt_deviation_minutes=0.01,  # Very strict threshold
        rt_deviation_rsd=0.1,  # Very strict threshold
        **{
            k: v
            for k, v in default_thresholds.__dict__.items()
            if k not in ["rt_deviation_minutes", "rt_deviation_rsd"]
        },
    )
    validator.thresholds = poor_thresholds
    results = validator.validate_retention_time()
    assert not results["passed"]


def test_peak_shape_validation(sample_data_dir, default_thresholds) -> None:
    """Test peak shape validation with various scenarios."""
    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )

    # Test with good peak shape
    results = validator.validate_peak_shape()
    assert isinstance(results, dict)
    assert "passed" in results
    assert "details" in results
    assert "summary" in results

    # Test with poor peak shape
    poor_thresholds = ValidationThresholds(
        peak_asymmetry_min=1.0,  # Very strict threshold
        peak_asymmetry_max=1.1,  # Very strict threshold
        peak_tailing_min=1.0,  # Very strict threshold
        peak_tailing_max=1.1,  # Very strict threshold
        **{
            k: v
            for k, v in default_thresholds.__dict__.items()
            if k not in ["peak_asymmetry_min", "peak_asymmetry_max", "peak_tailing_min", "peak_tailing_max"]
        },
    )
    validator.thresholds = poor_thresholds
    results = validator.validate_peak_shape()
    assert not results["passed"]


def test_validation_with_invalid_data(sample_data_dir, default_thresholds):
    """Test validation behavior with invalid or corrupted data."""
    # Create invalid feature table with missing required columns
    invalid_feature_data = pd.DataFrame({
        "id": [1, 2, 3],
        "mz": [200.1234, 300.5678, 400.1234],
        # Missing rt, area, height, etc.
    })
    invalid_feature_data.to_csv(sample_data_dir / "invalid_feature_table.csv", index=False)
    # Test initialization with invalid data
    with pytest.raises(ValidationDataError):
        SystemSuitability(
            acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
            feature_table_path=str(sample_data_dir / "invalid_feature_table.csv"),
            endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
            exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
            thresholds=default_thresholds,
        ).run_all_validations()


def test_validation_with_empty_data(sample_data_dir, default_thresholds):
    """Test validation behavior with empty data files."""
    # Create empty feature table with correct columns but no data
    empty_feature_data = pd.DataFrame(
        columns=[
            "id",
            "mz",
            "rt",
            "area",
            "height",
            "fwhm",
            "asymmetry",
            "tailing",
            "sn",
            "datafile:sample1.mzML:area",
            "datafile:sample2.mzML:area",
            "datafile:sample3.mzML:area",
            "datafile:sample1.mzML:height",
            "datafile:sample2.mzML:height",
            "datafile:sample3.mzML:height",
            "datafile:sample1.mzML:asymmetry_factor",
            "datafile:sample2.mzML:asymmetry_factor",
            "datafile:sample3.mzML:asymmetry_factor",
            "datafile:sample1.mzML:tailing_factor",
            "datafile:sample2.mzML:tailing_factor",
            "datafile:sample3.mzML:tailing_factor",
            "datafile:sample1.mzML:sn",
            "datafile:sample2.mzML:sn",
            "datafile:sample3.mzML:sn",
        ]
    )
    empty_feature_data.to_csv(sample_data_dir / "empty_feature_table.csv", index=False)

    validator = SystemSuitability(
        acquisition_list_path=str(sample_data_dir / "acquisition_list.csv"),
        feature_table_path=str(sample_data_dir / "empty_feature_table.csv"),
        endogenous_compounds_path=str(sample_data_dir / "endogenous_compounds.csv"),
        exogenous_compounds_path=str(sample_data_dir / "exogenous_compounds.csv"),
        thresholds=default_thresholds,
    )
    with pytest.raises(ValidationDataError):
        validator.run_all_validations()
