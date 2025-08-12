"""Tests for utility functions in SST validation module."""

import pandas as pd
import pytest

from isospec_data_tools.sst_validation.metrics.base import ValidationResult
from isospec_data_tools.sst_validation.metrics.utils import (
    find_matching_features,
    initialize_validation_result,
)


class TestInitializeResults:
    """Test suite for initialize_results utility."""

    def test_initialize_empty_results(self) -> None:
        """Test initialization of empty results dictionary."""
        results = initialize_validation_result([])
        assert isinstance(results, ValidationResult)
        assert len(results.results) == 0

    def test_initialize_with_metric_names(self) -> None:
        """Test initialization with specific metric names."""
        from isospec_data_tools.sst_validation.metrics.base import BaseMetricResult

        metric_results = [
            BaseMetricResult(metric_name="mass_accuracy", passed=True),
            BaseMetricResult(metric_name="resolution", passed=True),
            BaseMetricResult(metric_name="peak_shape", passed=True),
        ]
        results = initialize_validation_result(metric_results)
        assert isinstance(results, ValidationResult)
        assert len(results.results) == len(metric_results)
        for result in metric_results:
            assert result.metric_name in [r.metric_name for r in results.results]


class TestFindMatchingFeatures:
    """Test suite for find_matching_features utility."""

    @pytest.fixture
    def feature_table(self) -> pd.DataFrame:
        """Create sample features for testing."""
        return pd.DataFrame({
            "mz": [100.0, 200.0, 200.05, 300.0],
            "rt": [1.0, 2.0, 2.05, 3.0],
            "intensity": [1000.0, 2000.0, 3000.0, 4000.0],
            "id": ["1", "2", "3", "4"],
        })

    def test_exact_match(self, feature_table: pd.DataFrame) -> None:
        """Test finding exact matches between features."""
        reference = feature_table.iloc[0]
        matches = find_matching_features(
            feature_table, reference.mz, reference.rt, mz_tolerance=0.001, rt_tolerance=0.1
        )
        assert len(matches) == 1
        assert matches.iloc[0].id == "1"

    def test_no_matches(self, feature_table: pd.DataFrame) -> None:
        """Test when no matches are found."""
        mz = 150.0
        rt = 1.5
        matches = find_matching_features(feature_table, mz, rt, mz_tolerance=0.001, rt_tolerance=0.1)
        assert len(matches) == 0

    def test_multiple_matches(self, feature_table: pd.DataFrame) -> None:
        """Test handling of multiple potential matches."""
        reference = feature_table.iloc[1]
        matches = find_matching_features(feature_table, reference.mz, reference.rt, mz_tolerance=0.1, rt_tolerance=0.2)
        assert len(matches) >= 2
        # Should return closest match first
        assert matches.iloc[0].id == "2"
