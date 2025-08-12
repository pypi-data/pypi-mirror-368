"""
Mathematical correctness tests for core statistical functions.

This module validates that statistical calculations produce mathematically
correct results by comparing against known values and reference implementations.
Tests focus on numerical accuracy, edge cases, and statistical validity.
"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

# Import the core statistical functions we need to test
from isospec_data_tools.analysis.core.effect_sizes import (
    calculate_cohens_d,
    calculate_eta_squared,
    calculate_fold_change,
)
from isospec_data_tools.analysis.core.multiple_comparisons import (
    adjust_p_values,
    bonferroni_correction,
    calculate_q_values,
)
from isospec_data_tools.analysis.core.statistical_tests import (
    perform_chi_square_test,
    perform_student_t_test,
    perform_tukey_hsd_test,
    perform_welch_t_test,
)


class TestCohensD:
    """Test Cohen's d effect size calculations for mathematical correctness."""

    def test_cohens_d_known_values(self) -> None:
        """Test Cohen's d with hand-calculated known values."""
        # Example from Cohen (1988): group1 mean=100, sd=15; group2 mean=115, sd=15
        # Expected Cohen's d = (115-100)/15 = 1.0
        group1 = pd.Series([85, 90, 95, 100, 105, 110, 115])  # mean=100, sd≈10.8
        group2 = pd.Series([100, 105, 110, 115, 120, 125, 130])  # mean=115, sd≈10.8

        cohens_d = calculate_cohens_d(group1, group2)

        # Calculate expected value manually
        mean1, mean2 = group1.mean(), group2.mean()
        pooled_std = np.sqrt(
            ((len(group1) - 1) * group1.var(ddof=1) + (len(group2) - 1) * group2.var(ddof=1))
            / (len(group1) + len(group2) - 2)
        )
        expected_d = abs(mean2 - mean1) / pooled_std

        assert abs(cohens_d - expected_d) < 1e-10, f"Expected {expected_d}, got {cohens_d}"

    def test_cohens_d_identical_groups(self) -> None:
        """Test Cohen's d returns 0 for identical groups."""
        group1 = pd.Series([1, 2, 3, 4, 5])
        group2 = pd.Series([1, 2, 3, 4, 5])

        cohens_d = calculate_cohens_d(group1, group2)
        assert cohens_d == 0.0

    def test_cohens_d_zero_variance(self) -> None:
        """Test Cohen's d handles zero variance correctly."""
        group1 = pd.Series([5, 5, 5, 5, 5])  # No variance
        group2 = pd.Series([3, 3, 3, 3, 3])  # No variance

        cohens_d = calculate_cohens_d(group1, group2)
        assert cohens_d == 0.0  # Should return 0 when pooled std is 0

    def test_cohens_d_single_values(self) -> None:
        """Test Cohen's d with single values (edge case)."""
        group1 = pd.Series([5])
        group2 = pd.Series([3])

        # This should raise ValueError for insufficient data
        with pytest.raises(ValueError, match="Each group must have at least 2 observations"):
            calculate_cohens_d(group1, group2)

    def test_cohens_d_large_effect(self) -> None:
        """Test Cohen's d with large effect size (d > 0.8)."""
        # Create groups with large separation
        group1 = pd.Series([1, 1.5, 2, 2.5, 3])  # mean=2, sd≈0.79
        group2 = pd.Series([8, 8.5, 9, 9.5, 10])  # mean=9, sd≈0.79

        cohens_d = calculate_cohens_d(group1, group2)
        assert cohens_d > 0.8, f"Expected large effect (>0.8), got {cohens_d}"

    def test_cohens_d_with_nan_values(self) -> None:
        """Test Cohen's d handles NaN values correctly."""
        group1 = pd.Series([1, 2, np.nan, 4, 5])
        group2 = pd.Series([6, 7, 8, np.nan, 10])

        # Function should handle NaN by dropping them
        cohens_d = calculate_cohens_d(group1, group2)
        assert not np.isnan(cohens_d), "Cohen's d should not return NaN"


class TestFoldChange:
    """Test fold change calculations for mathematical correctness."""

    def test_fold_change_basic_calculation(self) -> None:
        """Test basic fold change calculation."""
        # 2x fold change
        fold_change = calculate_fold_change(10.0, 20.0, log2_transform=False)
        assert abs(fold_change - 2.0) < 1e-10

        # 0.5x fold change (downregulation)
        fold_change = calculate_fold_change(20.0, 10.0, log2_transform=False)
        assert abs(fold_change - 0.5) < 1e-10

    def test_fold_change_log2_transform(self) -> None:
        """Test fold change with log2 transformed data."""
        # For log2 data: fold_change = 2^(value2 - value1)
        # log2(4) = 2, log2(8) = 3, so fold_change = 2^(3-2) = 2
        fold_change = calculate_fold_change(2.0, 3.0, log2_transform=True)
        assert abs(fold_change - 2.0) < 1e-10

        # log2(8) = 3, log2(4) = 2, so fold_change = 2^(2-3) = 0.5
        fold_change = calculate_fold_change(3.0, 2.0, log2_transform=True)
        assert abs(fold_change - 0.5) < 1e-10

    def test_fold_change_edge_cases(self) -> None:
        """Test fold change edge cases."""
        # Division by zero should return NaN
        fold_change = calculate_fold_change(0.0, 5.0, log2_transform=False)
        assert np.isnan(fold_change)

        # Negative values
        fold_change = calculate_fold_change(-2.0, -4.0, log2_transform=False)
        assert abs(fold_change - 2.0) < 1e-10

        # Very small numbers
        fold_change = calculate_fold_change(1e-10, 2e-10, log2_transform=False)
        assert abs(fold_change - 2.0) < 1e-10

    def test_fold_change_zero_values(self) -> None:
        """Test fold change with zero values."""
        # Zero in denominator
        fold_change = calculate_fold_change(0.0, 10.0, log2_transform=False)
        assert np.isnan(fold_change)

        # Zero in numerator
        fold_change = calculate_fold_change(10.0, 0.0, log2_transform=False)
        assert fold_change == 0.0

        # Both zero
        fold_change = calculate_fold_change(0.0, 0.0, log2_transform=False)
        assert np.isnan(fold_change)


class TestEtaSquared:
    """Test eta-squared effect size calculations."""

    def test_eta_squared_basic_calculation(self) -> None:
        """Test eta-squared calculation with known values."""
        # Create ANOVA scenario with 3 groups
        group_means = np.array([2.0, 4.0, 6.0])  # Different means
        group_sizes = np.array([10, 10, 10])  # Equal sizes
        total_variance = 8.0  # Within-group variance

        eta_squared = calculate_eta_squared(group_means, group_sizes, total_variance)

        # Calculate expected value manually
        grand_mean = np.average(group_means, weights=group_sizes)  # 4.0
        between_variance = np.sum(
            group_sizes * (group_means - grand_mean) ** 2
        )  # 10*(4-4)^2 + 10*(2-4)^2 + 10*(6-4)^2 = 80
        expected = between_variance / (between_variance + total_variance)  # 80 / (80 + 8) = 80/88

        assert abs(eta_squared - expected) < 1e-10

    def test_eta_squared_edge_cases(self) -> None:
        """Test eta-squared edge cases."""
        # Perfect effect (groups very different, minimal within-group variance)
        group_means = np.array([0.0, 10.0])
        group_sizes = np.array([10, 10])
        total_variance = 0.1  # Very small within-group variance

        eta_squared = calculate_eta_squared(group_means, group_sizes, total_variance)
        assert eta_squared > 0.9  # Should be close to 1.0

        # No effect (all groups identical)
        group_means = np.array([5.0, 5.0, 5.0])
        group_sizes = np.array([10, 10, 10])
        total_variance = 2.0

        eta_squared = calculate_eta_squared(group_means, group_sizes, total_variance)
        assert eta_squared == 0.0  # No between-group variance

    def test_eta_squared_unequal_groups(self) -> None:
        """Test eta-squared with unequal group sizes."""
        group_means = np.array([1.0, 3.0, 5.0])
        group_sizes = np.array([5, 10, 15])  # Unequal sizes
        total_variance = 4.0

        eta_squared = calculate_eta_squared(group_means, group_sizes, total_variance)

        # Should handle unequal groups correctly
        assert 0.0 <= eta_squared <= 1.0
        assert eta_squared > 0  # Should detect differences


class TestMultipleComparisons:
    """Test multiple comparison correction methods."""

    def test_benjamini_hochberg_known_values(self) -> None:
        """Test Benjamini-Hochberg correction with known values."""
        # Known example from literature
        p_values = pd.Series([0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205])
        alpha = 0.05

        adjusted = adjust_p_values(p_values, alpha=alpha, method="fdr_bh")

        # For BH correction: adjusted_p = p * m / i where m=length, i=rank
        # Check first few values manually
        assert adjusted.iloc[0] < alpha  # Should be significant
        assert len(adjusted) == len(p_values)
        assert all(adjusted >= p_values)  # Adjusted should be >= original

    def test_bonferroni_correction_known_values(self) -> None:
        """Test Bonferroni correction with known values."""
        p_values = np.array([0.001, 0.01, 0.02, 0.03, 0.04])
        alpha = 0.05

        significant, corrected_alpha = bonferroni_correction(p_values, alpha)

        expected_alpha = alpha / len(p_values)  # 0.05 / 5 = 0.01
        assert abs(corrected_alpha - expected_alpha) < 1e-10

        # Only p-values < 0.01 should be significant
        expected_significant = p_values < expected_alpha
        np.testing.assert_array_equal(significant, expected_significant)

    def test_q_values_calculation(self) -> None:
        """Test q-value calculation."""
        p_values = np.array([0.001, 0.01, 0.05, 0.1, 0.2])
        q_values = calculate_q_values(p_values)

        # Q-values should be monotonic and >= p-values
        assert len(q_values) == len(p_values)
        assert all(q_values >= p_values)

        # Last q-value should equal last p-value
        assert abs(q_values[-1] - p_values[-1]) < 1e-10

    def test_multiple_comparisons_edge_cases(self) -> None:
        """Test multiple comparison methods with edge cases."""
        # Empty p-values
        empty_series = pd.Series(dtype=float)
        result = adjust_p_values(empty_series)
        assert len(result) == 0

        # Single p-value
        single_p = pd.Series([0.05])
        result = adjust_p_values(single_p)
        assert len(result) == 1
        assert result.iloc[0] == 0.05  # Should be unchanged

        # P-values with NaN
        p_with_nan = pd.Series([0.01, np.nan, 0.05])
        result = adjust_p_values(p_with_nan)
        assert len(result) == 3
        assert np.isnan(result.iloc[1])  # NaN should be preserved


class TestStatisticalTests:
    """Test statistical test implementations for correctness."""

    @pytest.fixture
    def known_t_test_data(self) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Create data with known t-test results."""
        # Create data where we know the expected t-statistic and p-value
        data = pd.DataFrame({
            "feature1": [1, 2, 3, 4, 5, 8, 9, 10, 11, 12],
            "group": ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B"],
        })

        # Manual calculation for verification
        group_a = np.array([1, 2, 3, 4, 5])
        group_b = np.array([8, 9, 10, 11, 12])

        # Calculate expected t-statistic using scipy
        expected_t, expected_p = stats.ttest_ind(group_a, group_b)

        expected = {
            "t_statistic": expected_t,
            "p_value": expected_p,
            "mean_a": np.mean(group_a),
            "mean_b": np.mean(group_b),
            "mean_diff": np.mean(group_b) - np.mean(group_a),
        }

        return data, expected

    def test_student_t_test_correctness(self, known_t_test_data: tuple[pd.DataFrame, dict[str, Any]]) -> None:
        """Test Student's t-test mathematical correctness."""
        data, expected = known_t_test_data

        results = perform_student_t_test(data, ["feature1"], "group", alpha=0.05, include_effect_sizes=True)

        assert len(results) == 1
        result = results[0]

        # Check t-statistic (should match scipy exactly)
        assert abs(result["t_statistic"] - expected["t_statistic"]) < 1e-10

        # Check p-value
        assert abs(result["p_value"] - expected["p_value"]) < 1e-10

        # Check means
        assert abs(result["mean_group1"] - expected["mean_a"]) < 1e-10
        assert abs(result["mean_group2"] - expected["mean_b"]) < 1e-10

        # Check mean difference
        assert abs(result["mean_diff"] - expected["mean_diff"]) < 1e-10

        # Check that effect size is calculated
        assert "effect_size" in result
        assert "fold_change" in result

    def test_welch_t_test_unequal_variances(self) -> None:
        """Test Welch's t-test with unequal variances."""
        # Create data with different variances
        np.random.seed(42)
        group1 = np.random.normal(loc=0, scale=1, size=20)
        group2 = np.random.normal(loc=2, scale=3, size=15)  # Different variance

        data = pd.DataFrame({"feature1": np.concatenate([group1, group2]), "group": ["A"] * 20 + ["B"] * 15})

        results = perform_welch_t_test(data, ["feature1"], "group", alpha=0.05)

        assert len(results) == 1
        result = results[0]

        # Compare with scipy's Welch test
        expected_t, expected_p = stats.ttest_ind(group1, group2, equal_var=False)

        assert abs(result["t_statistic"] - expected_t) < 1e-10
        assert abs(result["p_value"] - expected_p) < 1e-10

        # Check Welch degrees of freedom
        assert "welch_df" in result
        assert result["welch_df"] > 0

    def test_tukey_hsd_multiple_groups(self) -> None:
        """Test Tukey HSD with multiple groups."""
        # Create three-group data
        data = pd.DataFrame({
            "feature1": [1, 2, 3, 5, 6, 7, 9, 10, 11],
            "group": ["A", "A", "A", "B", "B", "B", "C", "C", "C"],
        })

        results = perform_tukey_hsd_test(data, ["feature1"], "group", alpha=0.05, include_effect_sizes=True)

        # Should have 3 pairwise comparisons: A-B, A-C, B-C
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3

        # Check that all pairwise comparisons are present
        comparisons = {tuple(row) for row in results[["group1", "group2"]].values}
        expected_comparisons = {("A", "B"), ("A", "C"), ("B", "C")}
        assert comparisons == expected_comparisons

        # DataFrame should have all required columns
        required_columns = [
            "feature",
            "group1",
            "group2",
            "mean_diff",
            "p_value",
            "ci_lower",
            "ci_upper",
            "effect_size",
            "fold_change",
        ]
        for column in required_columns:
            assert column in results.columns

    def test_chi_square_test_categorical(self) -> None:
        """Test chi-square test with categorical data."""
        # Create data for chi-square test
        data = pd.DataFrame({
            "group": ["A", "A", "A", "B", "B", "B", "A", "A", "B", "B"],
            "outcome": [
                "success",
                "success",
                "failure",
                "success",
                "failure",
                "failure",
                "success",
                "failure",
                "success",
                "failure",
            ],
            "gender": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        })

        results = perform_chi_square_test(data, "group", "outcome", "gender")

        assert "within_group" in results
        assert "between_group" in results

        # Should have between-group comparison
        assert len(results["between_group"]) > 0

        # Each result should have required fields
        for result in results["between_group"]:
            assert "group1" in result
            assert "group2" in result
            assert "statistic" in result
            assert "p_value" in result


class TestNumericalStability:
    """Test numerical stability of statistical calculations."""

    def test_very_small_p_values(self) -> None:
        """Test handling of very small p-values."""
        # Create p-values near machine epsilon
        very_small_p = pd.Series([1e-300, 1e-200, 1e-100, 0.001, 0.05])

        adjusted = adjust_p_values(very_small_p, method="fdr_bh")

        # Should not overflow or underflow
        assert all(np.isfinite(adjusted))
        assert all(adjusted >= very_small_p)

    def test_large_effect_sizes(self) -> None:
        """Test calculations with very large effect sizes."""
        # Create groups with extreme separation
        group1 = pd.Series([1e-6, 2e-6, 3e-6])
        group2 = pd.Series([1e6, 2e6, 3e6])

        cohens_d = calculate_cohens_d(group1, group2)
        fold_change = calculate_fold_change(float(group1.mean()), float(group2.mean()))

        # Should be finite and very large
        assert np.isfinite(cohens_d)
        assert np.isfinite(fold_change)
        assert cohens_d > 2  # Should be large effect (Cohen's d uses pooled variance, so not as extreme)
        assert fold_change > 1e6

    def test_precision_near_boundaries(self) -> None:
        """Test precision near statistical boundaries."""
        # Test near p = 0.05 boundary
        p_values = pd.Series([0.049999, 0.050000, 0.050001])
        adjusted = adjust_p_values(p_values, alpha=0.05, method="bonferroni")

        # Small differences should be preserved
        assert adjusted.iloc[0] < adjusted.iloc[1] < adjusted.iloc[2]

        # Test near effect size boundaries (small/medium/large)
        # Cohen's conventions: 0.2 (small), 0.5 (medium), 0.8 (large)
        group1 = pd.Series([0, 1, 2, 3, 4])

        # Create groups for exactly medium effect (d = 0.5)
        # d = (mean2 - mean1) / pooled_sd
        # If pooled_sd ≈ 1.58, then mean_diff = 0.5 * 1.58 ≈ 0.79
        group2 = pd.Series([0.8, 1.8, 2.8, 3.8, 4.8])  # mean diff ≈ 0.8

        cohens_d = calculate_cohens_d(group1, group2)
        assert 0.4 < cohens_d < 0.6  # Should be around medium effect


class TestStatisticalAssumptions:
    """Test that statistical tests handle assumption violations gracefully."""

    def test_non_normal_data(self) -> None:
        """Test statistical tests with non-normal data."""
        # Create highly skewed data
        np.random.seed(42)
        skewed_data = np.random.exponential(scale=2, size=50)

        data = pd.DataFrame({"feature1": skewed_data, "group": ["A"] * 25 + ["B"] * 25})

        # Tests should still run and return valid results
        results = perform_student_t_test(data, ["feature1"], "group")
        assert len(results) == 1
        assert np.isfinite(results[0]["t_statistic"])
        assert 0 <= results[0]["p_value"] <= 1

    def test_unbalanced_groups(self) -> None:
        """Test with highly unbalanced group sizes."""
        data = pd.DataFrame({
            "feature1": [1, 2, 3, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            "group": ["A", "A", "A"] + ["B"] * 9,  # 3 vs 9 samples
        })

        results = perform_student_t_test(data, ["feature1"], "group")
        welch_results = perform_welch_t_test(data, ["feature1"], "group")

        # Both should handle unbalanced data
        assert len(results) == 1
        assert len(welch_results) == 1

        # Welch test should be more appropriate for unbalanced data
        assert np.isfinite(welch_results[0]["welch_df"])

    def test_outlier_resistance(self) -> None:
        """Test effect of outliers on statistical calculations."""
        # Data without outliers
        normal_data = pd.DataFrame({"feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "group": ["A"] * 5 + ["B"] * 5})

        # Data with extreme outlier
        outlier_data = pd.DataFrame({
            "feature1": [1, 2, 3, 4, 1000, 6, 7, 8, 9, 10],  # 1000 is outlier
            "group": ["A"] * 5 + ["B"] * 5,
        })

        normal_results = perform_student_t_test(normal_data, ["feature1"], "group")
        outlier_results = perform_student_t_test(outlier_data, ["feature1"], "group")

        # Outlier should dramatically affect results
        normal_p = normal_results[0]["p_value"]
        outlier_p = outlier_results[0]["p_value"]

        # P-values should be different (outlier effect)
        assert abs(normal_p - outlier_p) > 0.01
