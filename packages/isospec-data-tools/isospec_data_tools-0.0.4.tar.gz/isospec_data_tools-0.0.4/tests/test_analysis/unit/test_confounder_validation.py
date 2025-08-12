"""
Confounder analysis validation tests for statistical correctness.

This module validates confounder analysis implementations by testing
statistical methods, effect size calculations, correlation analysis,
and multiple comparison corrections for accuracy.
"""

import numpy as np
import pandas as pd
import pytest
import scipy.stats as stats

# Import the confounder analyzer we need to test
from isospec_data_tools.analysis.specialized.confounder_analysis import ConfounderAnalyzer


class TestConfounderStatisticalCorrectness:
    """Test confounder analysis statistical methods for correctness."""

    @pytest.fixture
    def categorical_confounder_data(self) -> pd.DataFrame:
        """Create data with known categorical confounder effects."""
        np.random.seed(42)

        # Create glycan data where sex has a real effect on some glycans
        n_samples = 100

        data = []
        for _i in range(n_samples):
            sex = np.random.choice([0, 1], p=[0.5, 0.5])  # 0=Female, 1=Male
            age = np.random.uniform(20, 80)

            # FT-001: Strong sex effect (males have higher values)
            ft001 = 10 + 3 * sex + np.random.normal(0, 1)

            # FT-002: Weak sex effect
            ft002 = 8 + 0.5 * sex + np.random.normal(0, 1.5)

            # FT-003: No sex effect (null case)
            ft003 = 12 + np.random.normal(0, 2)

            data.append({
                "FT-001": ft001,
                "FT-002": ft002,
                "FT-003": ft003,
                "sex": sex,
                "age": age,
                "class_final": "Control",  # Single class for confounder analysis
            })

        return pd.DataFrame(data)

    @pytest.fixture
    def continuous_confounder_data(self) -> pd.DataFrame:
        """Create data with known continuous confounder effects."""
        np.random.seed(123)

        n_samples = 80

        data = []
        for _i in range(n_samples):
            age = np.random.uniform(20, 80)

            # FT-001: Strong positive correlation with age
            ft001 = 5 + 0.2 * age + np.random.normal(0, 1)

            # FT-002: Negative correlation with age
            ft002 = 15 - 0.1 * age + np.random.normal(0, 1.2)

            # FT-003: No correlation with age
            ft003 = 10 + np.random.normal(0, 2)

            data.append({"FT-001": ft001, "FT-002": ft002, "FT-003": ft003, "age": age, "class_final": "Control"})

        return pd.DataFrame(data)

    def test_categorical_confounder_analysis_correctness(self, categorical_confounder_data: pd.DataFrame) -> None:
        """Test categorical confounder analysis against scipy reference."""
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            categorical_confounder_data, glycan_prefix="FT-", confounders=["sex"], alpha=0.05, min_glycans=1
        )

        # Should detect sex as significant confounder (if sex has enough effect)
        assert "sex" in results
        sex_results = results["sex"]

        # Verify against scipy t-test for FT-001 (should have strongest effect)
        males = categorical_confounder_data[categorical_confounder_data["sex"] == 1]["FT-001"].dropna()
        females = categorical_confounder_data[categorical_confounder_data["sex"] == 0]["FT-001"].dropna()

        # Only test if we have sufficient data
        if len(males) > 1 and len(females) > 1:
            expected_t, expected_p = stats.ttest_ind(males, females, nan_policy="omit")

            # Find FT-001 in results
            ft001_idx = sex_results["glycans"].index("FT-001")
            our_p = sex_results["p_values"][ft001_idx]

            # Should match scipy result (if not NaN)
            if not np.isnan(our_p):
                assert abs(our_p - expected_p) < 1e-10, f"P-value mismatch: {our_p} vs {expected_p}"

                # Verify Cohen's d calculation
                our_effect_size = sex_results["effect_sizes"][ft001_idx]

                # Calculate expected Cohen's d manually
                pooled_std = np.sqrt(
                    ((len(males) - 1) * males.var(ddof=1) + (len(females) - 1) * females.var(ddof=1))
                    / (len(males) + len(females) - 2)
                )
                expected_cohens_d = abs(males.mean() - females.mean()) / pooled_std if pooled_std > 0 else 0.0

                assert abs(our_effect_size - expected_cohens_d) < 1e-10, (
                    f"Effect size mismatch: {our_effect_size} vs {expected_cohens_d}"
                )

    def test_continuous_confounder_analysis_correctness(self, continuous_confounder_data: pd.DataFrame) -> None:
        """Test continuous confounder analysis against scipy reference."""
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            continuous_confounder_data, glycan_prefix="FT-", confounders=["age"], alpha=0.05, min_glycans=1
        )

        # Should detect age as significant confounder
        assert "age" in results
        age_results = results["age"]

        # Verify against scipy correlation for FT-001 (strongest correlation)
        ft001_data = continuous_confounder_data[["FT-001", "age"]].dropna()
        expected_r, expected_p = stats.pearsonr(ft001_data["age"], ft001_data["FT-001"])

        # Find FT-001 in results
        ft001_idx = age_results["glycans"].index("FT-001")
        our_p = age_results["p_values"][ft001_idx]
        our_correlation = age_results["correlations"][ft001_idx]

        # Should match scipy results
        assert abs(our_p - expected_p) < 1e-10, f"P-value mismatch: {our_p} vs {expected_p}"
        assert abs(our_correlation - expected_r) < 1e-10, f"Correlation mismatch: {our_correlation} vs {expected_r}"

    def test_multiple_comparison_correction_accuracy(self, categorical_confounder_data: pd.DataFrame) -> None:
        """Test multiple comparison correction implementation."""
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            categorical_confounder_data,
            glycan_prefix="FT-",
            confounders=["sex"],
            alpha=0.05,
            correction_method="fdr_bh",
        )

        sex_results = results["sex"]
        raw_p_values = [p for p in sex_results["p_values"] if not np.isnan(p)]
        adj_p_values = [p for p in sex_results["adj_p_values"] if not np.isnan(p)]

        # Adjusted p-values should be >= raw p-values
        for raw_p, adj_p in zip(raw_p_values, adj_p_values, strict=False):
            assert adj_p >= raw_p, f"Adjusted p-value {adj_p} less than raw {raw_p}"

        # Test different correction methods
        results_bonf, _ = ConfounderAnalyzer.analyze_confounders(
            categorical_confounder_data,
            glycan_prefix="FT-",
            confounders=["sex"],
            alpha=0.05,
            correction_method="bonferroni",
        )

        # Bonferroni should be more conservative than FDR-BH
        bonf_adj_p = [p for p in results_bonf["sex"]["adj_p_values"] if not np.isnan(p)]
        fdr_adj_p = adj_p_values

        for bonf_p, fdr_p in zip(bonf_adj_p, fdr_adj_p, strict=False):
            # Account for floating point precision
            assert bonf_p >= fdr_p - 1e-15, f"Bonferroni ({bonf_p}) should be more conservative than FDR-BH ({fdr_p})"


class TestConfounderUtilityFunctions:
    """Test confounder analysis utility functions."""

    def test_get_confounded_features_extraction(self) -> None:
        """Test extraction of confounded features with correct structure."""
        # Mock results structure
        mock_results = {
            "age": {
                "glycans": ["FT-001", "FT-002", "FT-003"],
                "p_values": [0.001, 0.08, 0.15],
                "adj_p_values": [0.003, 0.12, 0.15],
                "effect_sizes": [0.8, 0.3, 0.1],
                "correlations": [0.7, 0.25, 0.05],
            },
            "sex": {
                "glycans": ["FT-001", "FT-002", "FT-003"],
                "p_values": [0.02, 0.04, 0.9],
                "adj_p_values": [0.06, 0.12, 0.9],
                "effect_sizes": [0.6, 0.5, 0.01],
                "correlations": [0.0, 0.0, 0.0],  # Categorical confounders have 0 correlation
            },
        }

        confounded_df = ConfounderAnalyzer.get_confounded_features(mock_results, alpha=0.05)

        # Should only include features with adj_p_value <= 0.05
        # From age: none (adj_p_values are 0.003, 0.12, 0.15)
        # From sex: none (adj_p_values are 0.06, 0.12, 0.9)
        # Actually FT-001 from age should be significant (0.003 < 0.05)

        actual_features = confounded_df["feature"].tolist()

        assert "FT-001" in actual_features
        assert confounded_df[confounded_df["feature"] == "FT-001"]["confounder"].iloc[0] == "age"

    def test_find_glycan_confounders_mapping(self) -> None:
        """Test mapping of glycans to their confounders."""
        glycan_list = ["FT-001", "FT-002", "FT-003", "FT-004"]
        confounder_dict = {"age": ["FT-001", "FT-003"], "sex": ["FT-001", "FT-002"], "bmi": ["FT-004"]}

        glycan_confounders = ConfounderAnalyzer.find_glycan_confounders(glycan_list, confounder_dict)

        expected = {"FT-001": ["age", "sex"], "FT-002": ["sex"], "FT-003": ["age"], "FT-004": ["bmi"]}

        assert glycan_confounders == expected

    def test_filter_significant_glycans_functionality(self) -> None:
        """Test filtering of significant glycans by adjusted p-values."""
        mock_results = {
            "age": {"glycans": ["FT-001", "FT-002", "FT-003"], "adj_p_values": [0.01, 0.08, 0.15]},
            "sex": {"glycans": ["FT-001", "FT-002", "FT-003"], "adj_p_values": [0.03, 0.02, 0.9]},
        }

        # Convert to DataFrame format as expected by the function
        results_as_df = {}
        for confounder, data in mock_results.items():
            results_as_df[confounder] = {
                "glycans": data["glycans"],
                "adj_p_values": data["adj_p_values"],
                "Glycan": data["glycans"],  # Add expected column name
            }

        significant_glycans = ConfounderAnalyzer.filter_significant_glycans(
            results_as_df, alpha=0.05, label_column="Glycan"
        )

        expected = {
            "age": ["FT-001"],  # Only 0.01 < 0.05
            "sex": ["FT-001", "FT-002"],  # 0.03 and 0.02 < 0.05
        }

        assert significant_glycans == expected


class TestConfounderEdgeCases:
    """Test confounder analysis edge cases and error handling."""

    def test_missing_confounder_columns(self) -> None:
        """Test handling of missing confounder columns."""
        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "class_final": ["A"] * 5,
            # Missing 'age' and 'sex' columns
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data,
            glycan_prefix="FT-",
            confounders=["age", "sex"],  # These columns don't exist
            alpha=0.05,
        )

        # Should handle missing columns gracefully
        assert len(results) == 0  # No confounders analyzed
        assert len(significant_confounders) == 0

    def test_single_category_confounder(self) -> None:
        """Test handling of confounder with only one category."""
        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "sex": [1, 1, 1, 1, 1],  # All same category
            "class_final": ["A"] * 5,
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["sex"], alpha=0.05
        )

        # Should handle single category appropriately
        # Implementation may return empty results or NaN p-values
        if "sex" in results:
            sex_results = results["sex"]
            # P-values should be NaN or test should be skipped
            assert all(np.isnan(p) for p in sex_results["p_values"])

    def test_insufficient_data_per_group(self) -> None:
        """Test handling of insufficient data per confounder group."""
        data = pd.DataFrame({
            "FT-001": [1, 2],
            "sex": [0, 1],  # Only one observation per group
            "class_final": ["A", "A"],
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["sex"], alpha=0.05
        )

        # Should handle insufficient data appropriately
        if "sex" in results:
            # May produce valid results or NaN depending on implementation
            assert isinstance(results["sex"], dict)

    def test_all_nan_glycan_values(self) -> None:
        """Test handling of glycan with all NaN values."""
        data = pd.DataFrame({
            "FT-001": [np.nan, np.nan, np.nan, np.nan],
            "age": [20, 30, 40, 50],
            "class_final": ["A"] * 4,
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["age"], alpha=0.05
        )

        # Should handle all-NaN glycan appropriately
        if "age" in results:
            age_results = results["age"]
            # Should have NaN p-value for FT-001
            ft001_idx = age_results["glycans"].index("FT-001")
            assert np.isnan(age_results["p_values"][ft001_idx])

    def test_zero_variance_glycan(self) -> None:
        """Test handling of glycan with zero variance."""
        data = pd.DataFrame({
            "FT-001": [5.0, 5.0, 5.0, 5.0, 5.0],  # Zero variance
            "age": [20, 30, 40, 50, 60],
            "sex": [0, 1, 0, 1, 0],
            "class_final": ["A"] * 5,
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["age", "sex"], alpha=0.05
        )

        # Should handle zero variance appropriately
        for confounder in ["age", "sex"]:
            if confounder in results:
                confounder_results = results[confounder]
                ft001_idx = confounder_results["glycans"].index("FT-001")

                # Correlation should be 0 or NaN for zero variance
                if confounder == "age":
                    correlation = confounder_results["correlations"][ft001_idx]
                    assert np.isnan(correlation) or correlation == 0.0

                # Effect size should be 0 for categorical
                if confounder == "sex":
                    effect_size = confounder_results["effect_sizes"][ft001_idx]
                    assert effect_size == 0.0


class TestConfounderInputValidation:
    """Test confounder analysis input validation."""

    def test_empty_dataframe_handling(self) -> None:
        """Test handling of empty DataFrame."""
        empty_data = pd.DataFrame()

        # Should handle empty dataframe gracefully
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            empty_data, glycan_prefix="FT-", confounders=["age"], alpha=0.05
        )

        # Should return empty results rather than crash
        assert len(results) == 0
        assert len(significant_confounders) == 0

    def test_no_matching_glycans(self) -> None:
        """Test handling when no glycans match the prefix."""
        data = pd.DataFrame({
            "XYZ-001": [1, 2, 3],  # Different prefix
            "age": [20, 30, 40],
            "class_final": ["A"] * 3,
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data,
            glycan_prefix="FT-",  # No matching glycans
            confounders=["age"],
            alpha=0.05,
        )

        # Should handle no matching glycans gracefully
        assert len(results) == 0 or all(len(res["glycans"]) == 0 for res in results.values())

    def test_invalid_alpha_values(self) -> None:
        """Test handling of invalid alpha values."""
        data = pd.DataFrame({"FT-001": [1, 2, 3, 4, 5], "age": [20, 30, 40, 50, 60], "class_final": ["A"] * 5})

        # Test alpha = 0 (very strict)
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["age"], alpha=0.0, min_glycans=1
        )

        # Should produce results but likely no significant confounders
        assert len(significant_confounders) == 0

        # Test alpha = 1 (very permissive)
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["age"], alpha=1.0, min_glycans=1
        )

        # Should include confounders if any effects detected
        assert isinstance(significant_confounders, list)

    def test_min_glycans_threshold(self) -> None:
        """Test min_glycans threshold parameter."""
        data = pd.DataFrame({
            "FT-001": np.random.normal(10, 2, 50),
            "FT-002": np.random.normal(8, 1.5, 50),
            "age": np.random.uniform(20, 70, 50),
            "class_final": ["A"] * 50,
        })

        # Set high min_glycans threshold
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data,
            glycan_prefix="FT-",
            confounders=["age"],
            alpha=0.05,
            min_glycans=10,  # Require 10 significant glycans
        )

        # Should not find significant confounders due to high threshold
        assert len(significant_confounders) == 0

        # Set low min_glycans threshold
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data,
            glycan_prefix="FT-",
            confounders=["age"],
            alpha=0.05,
            min_glycans=1,  # Require only 1 significant glycan
        )

        # More likely to find significant confounders
        # (Depends on random data, but at least should not crash)
        assert isinstance(significant_confounders, list)


class TestConfounderPerformanceAndStability:
    """Test confounder analysis performance and numerical stability."""

    def test_large_dataset_handling(self) -> None:
        """Test handling of large datasets."""
        np.random.seed(42)

        # Create larger dataset
        n_samples = 1000
        n_glycans = 50

        data = {
            "age": np.random.uniform(20, 80, n_samples),
            "sex": np.random.choice([0, 1], n_samples),
            "class_final": ["A"] * n_samples,
        }

        # Add many glycans
        for i in range(n_glycans):
            # Some glycans correlated with age, some with sex, some random
            if i < 10:  # Age-correlated
                data[f"FT-{i:03d}"] = 10 + 0.1 * data["age"] + np.random.normal(0, 1, n_samples)
            elif i < 20:  # Sex-correlated
                data[f"FT-{i:03d}"] = 8 + 2 * data["sex"] + np.random.normal(0, 1.5, n_samples)
            else:  # Random
                data[f"FT-{i:03d}"] = np.random.normal(10, 2, n_samples)

        df = pd.DataFrame(data)

        # Should handle large dataset efficiently
        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            df, glycan_prefix="FT-", confounders=["age", "sex"], alpha=0.05, min_glycans=3
        )

        # Should detect both confounders
        assert "age" in significant_confounders
        assert "sex" in significant_confounders

        # Results should be well-structured
        assert len(results["age"]["glycans"]) == n_glycans
        assert len(results["sex"]["glycans"]) == n_glycans

    def test_extreme_correlation_values(self) -> None:
        """Test handling of extreme correlation values."""
        # Create data with perfect correlation
        np.random.seed(42)
        n_samples = 50

        age = np.random.uniform(20, 80, n_samples)

        data = pd.DataFrame({
            "FT-001": 2 * age + 10,  # Perfect correlation
            "FT-002": -0.5 * age + 50,  # Perfect negative correlation
            "age": age,
            "class_final": ["A"] * n_samples,
        })

        results, significant_confounders = ConfounderAnalyzer.analyze_confounders(
            data, glycan_prefix="FT-", confounders=["age"], alpha=0.05, min_glycans=1
        )

        # Should handle perfect correlations appropriately
        age_results = results["age"]

        # FT-001 should have correlation close to 1.0
        ft001_idx = age_results["glycans"].index("FT-001")
        ft001_corr = age_results["correlations"][ft001_idx]
        assert abs(ft001_corr - 1.0) < 1e-10

        # FT-002 should have correlation close to -1.0
        ft002_idx = age_results["glycans"].index("FT-002")
        ft002_corr = age_results["correlations"][ft002_idx]
        assert abs(ft002_corr - (-1.0)) < 1e-10
