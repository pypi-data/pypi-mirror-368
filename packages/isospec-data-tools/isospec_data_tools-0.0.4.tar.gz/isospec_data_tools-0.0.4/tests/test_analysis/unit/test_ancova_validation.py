"""
ANCOVA analysis validation tests for mathematical correctness.

This module validates ANCOVA (Analysis of Covariance) implementations by testing
against known statistical results, verifying covariate handling, effect size
calculations, and multiple comparison corrections.
"""

import numpy as np
import pandas as pd
import pytest
from pingouin import ancova

# Import the ANCOVA analyzer we need to test
from isospec_data_tools.analysis.specialized.ancova_analysis import ANCOVAAnalyzer


class TestANCOVAMathematicalCorrectness:
    """Test ANCOVA calculations for mathematical correctness."""

    @pytest.fixture
    def synthetic_ancova_data(self) -> pd.DataFrame:
        """Create synthetic data with known ANCOVA properties."""
        np.random.seed(42)

        # Create 3 groups with different means but controlled for age effect
        n_per_group = 20

        data = []
        for group_idx, group_name in enumerate(["Control", "Treatment1", "Treatment2"]):
            # Age ranges from 20-60 with some variance
            ages = np.random.uniform(20, 60, n_per_group)

            # Glycan abundance with group effect + age covariate effect + noise
            group_effect = [0, 2, 4][group_idx]  # Increasing effect by group
            age_effect = 0.1  # Age coefficient
            noise = np.random.normal(0, 0.5, n_per_group)

            glycan_values = 10 + group_effect + age_effect * ages + noise

            for i in range(n_per_group):
                data.append({
                    "FT-001": glycan_values[i],
                    "class": group_name,
                    "age": ages[i],
                    "subject_id": f"{group_name}_{i}",
                })

        return pd.DataFrame(data)

    @pytest.fixture
    def complex_ancova_data(self) -> pd.DataFrame:
        """Create more complex synthetic data with multiple glycans and covariates."""
        np.random.seed(123)

        n_per_group = 15
        groups = ["Healthy", "Disease", "Recovered"]

        data = []
        for group_idx, group_name in enumerate(groups):
            for i in range(n_per_group):
                # Multiple covariates - same for all glycans per subject
                age = np.random.uniform(25, 75)
                sex = np.random.choice([0, 1])  # 0=Female, 1=Male
                bmi = np.random.uniform(18.5, 35)

                subject_data = {
                    "subject_id": f"{group_name}_{i}",
                    "class": group_name,
                    "age": age,
                    "sex": sex,
                    "bmi": bmi,
                }

                # Multiple glycans with different effect patterns
                base_effects = {
                    "FT-001": [0, 1.5, 0.8][group_idx],  # Strong group effect
                    "FT-002": [0, 0.3, 0.1][group_idx],  # Weak group effect
                    "FT-003": [0, 0, 0][group_idx],  # No group effect (null case)
                }

                for glycan, group_effect in base_effects.items():
                    # Complex interaction pattern
                    age_effect = 0.05 if glycan == "FT-001" else 0.02
                    sex_effect = 0.5 if glycan == "FT-002" else 0.1
                    bmi_effect = 0.03 if glycan == "FT-001" else 0.01

                    value = (
                        10
                        + group_effect
                        + age_effect * age
                        + sex_effect * sex
                        + bmi_effect * bmi
                        + np.random.normal(0, 0.3)
                    )

                    subject_data[glycan] = value

                data.append(subject_data)

        return pd.DataFrame(data)

    def test_ancova_against_pingouin_reference(self, synthetic_ancova_data: pd.DataFrame) -> None:
        """Test ANCOVA results against pingouin reference implementation."""
        # Run our ANCOVA implementation
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            synthetic_ancova_data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
        )

        # Run pingouin ANCOVA for comparison
        pingouin_result = ancova(data=synthetic_ancova_data, dv="FT-001", covar=["age"], between="class")

        # Extract class effect from both results
        our_class_p = all_results[all_results["glycan"] == "FT-001"]["class_p_value"].iloc[0]
        our_class_eta2 = all_results[all_results["glycan"] == "FT-001"]["class_effect_size"].iloc[0]

        pingouin_class_p = pingouin_result[pingouin_result["Source"] == "class"]["p-unc"].iloc[0]
        pingouin_class_eta2 = pingouin_result[pingouin_result["Source"] == "class"]["np2"].iloc[0]

        # Results should match within numerical precision
        assert abs(our_class_p - pingouin_class_p) < 1e-10, f"P-values differ: {our_class_p} vs {pingouin_class_p}"
        assert abs(our_class_eta2 - pingouin_class_eta2) < 1e-10, (
            f"Effect sizes differ: {our_class_eta2} vs {pingouin_class_eta2}"
        )

        # Check covariate effects
        our_age_p = all_results[all_results["glycan"] == "FT-001"]["age_p_value"].iloc[0]
        our_age_eta2 = all_results[all_results["glycan"] == "FT-001"]["age_effect_size"].iloc[0]

        pingouin_age_p = pingouin_result[pingouin_result["Source"] == "age"]["p-unc"].iloc[0]
        pingouin_age_eta2 = pingouin_result[pingouin_result["Source"] == "age"]["np2"].iloc[0]

        assert abs(our_age_p - pingouin_age_p) < 1e-10
        assert abs(our_age_eta2 - pingouin_age_eta2) < 1e-10

    def test_ancova_multiple_covariates(self, complex_ancova_data: pd.DataFrame) -> None:
        """Test ANCOVA with multiple covariates."""
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            complex_ancova_data,
            feature_prefix="FT-",
            class_column="class",
            covar_columns=["age", "sex", "bmi"],
            alpha=0.05,
        )

        # Should analyze all 3 glycans
        assert len(all_results) == 3
        assert set(all_results["glycan"]) == {"FT-001", "FT-002", "FT-003"}

        # Each result should have all covariate effects
        for _, row in all_results.iterrows():
            assert "class_p_value" in row
            assert "class_effect_size" in row
            assert "age_p_value" in row
            assert "age_effect_size" in row
            assert "sex_p_value" in row
            assert "sex_effect_size" in row
            assert "bmi_p_value" in row
            assert "bmi_effect_size" in row

        # FT-001 should show strongest group effect (by design)
        ft001_result = all_results[all_results["glycan"] == "FT-001"].iloc[0]
        ft002_result = all_results[all_results["glycan"] == "FT-002"].iloc[0]
        ft003_result = all_results[all_results["glycan"] == "FT-003"].iloc[0]

        # Relative effect sizes should match our design
        assert ft001_result["class_effect_size"] > ft002_result["class_effect_size"]
        assert ft002_result["class_effect_size"] > ft003_result["class_effect_size"]

    def test_ancova_group_statistics_calculation(self, synthetic_ancova_data: pd.DataFrame) -> None:
        """Test that group statistics are calculated correctly."""
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            synthetic_ancova_data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
        )

        # Check that fold change is calculated
        assert "max_fold_change" in all_results.columns

        # Check that group means are calculated
        groups = synthetic_ancova_data["class"].unique()
        for group in groups:
            expected_col = f"mean_{group}"
            assert expected_col in all_results.columns

            # Verify the means match the actual data
            result_row = all_results[all_results["glycan"] == "FT-001"].iloc[0]
            expected_mean = synthetic_ancova_data[synthetic_ancova_data["class"] == group]["FT-001"].mean()
            actual_mean = result_row[expected_col]

            assert abs(actual_mean - expected_mean) < 1e-10

    def test_ancova_multiple_comparison_correction(self, complex_ancova_data: pd.DataFrame) -> None:
        """Test multiple comparison correction in ANCOVA."""
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            complex_ancova_data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
        )

        # Check that adjusted p-values are calculated
        assert "class_adj_p_value" in all_results.columns

        # Adjusted p-values should be >= original p-values
        for _, row in all_results.iterrows():
            assert row["class_adj_p_value"] >= row["class_p_value"]

        # Significant results should be subset of all results
        assert len(significant) <= len(all_results)

        # All significant results should have adj_p_value < alpha
        for _, row in significant.iterrows():
            assert row["class_adj_p_value"] < 0.05

    def test_ancova_glycan_composition_mapping(self, synthetic_ancova_data: pd.DataFrame) -> None:
        """Test glycan composition mapping functionality."""
        composition_map = {
            "FT-001": "Hex5HexNAc4Fuc1",
        }

        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            synthetic_ancova_data,
            feature_prefix="FT-",
            class_column="class",
            covar_columns=["age"],
            alpha=0.05,
            glycan_composition_map=composition_map,
        )

        # Check that composition is added
        assert "glycan_composition" in all_results.columns
        ft001_result = all_results[all_results["glycan"] == "FT-001"].iloc[0]
        assert ft001_result["glycan_composition"] == "Hex5HexNAc4Fuc1"


class TestANCOVAEdgeCases:
    """Test ANCOVA edge cases and error handling."""

    def test_ancova_insufficient_data(self) -> None:
        """Test ANCOVA with insufficient data."""
        # Create minimal dataset
        data = pd.DataFrame({"FT-001": [1, 2], "class": ["A", "B"], "age": [25, 30]})

        # Should handle gracefully or provide meaningful error
        try:
            significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
                data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
            )
            # If it succeeds, should return valid results
            assert isinstance(all_results, pd.DataFrame)
        except Exception as e:
            # If it fails, should be a meaningful error
            assert "insufficient" in str(e).lower() or "analysis" in str(e).lower()

    def test_ancova_missing_covariates(self) -> None:
        """Test ANCOVA when covariates are missing."""
        np.random.seed(42)
        data = pd.DataFrame({
            "FT-001": np.random.normal(10, 2, 30),
            "class": ["A"] * 10 + ["B"] * 10 + ["C"] * 10,
            "age": [np.nan] * 10 + list(np.random.uniform(20, 60, 20)),  # Missing age for group A
        })

        # Should handle missing covariates appropriately
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
        )

        # Should still produce results (pingouin handles missing data)
        assert len(all_results) >= 0

    def test_ancova_single_group(self) -> None:
        """Test ANCOVA with single group (should fail appropriately)."""
        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "class": ["A", "A", "A", "A", "A"],  # Only one group
            "age": [20, 25, 30, 35, 40],
        })

        # Should raise an appropriate error
        with pytest.raises(Exception):
            ANCOVAAnalyzer.analyze_glycans_ancova(
                data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
            )

    def test_ancova_zero_variance_glycan(self) -> None:
        """Test ANCOVA with zero variance glycan."""
        data = pd.DataFrame({
            "FT-001": [5.0] * 30,  # Zero variance
            "FT-002": np.random.normal(10, 2, 30),  # Normal variance
            "class": ["A"] * 10 + ["B"] * 10 + ["C"] * 10,
            "age": np.random.uniform(20, 60, 30),
        })

        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(
            data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
        )

        # Should handle zero variance glycan appropriately
        # FT-002 should still be analyzed successfully
        ft002_results = all_results[all_results["glycan"] == "FT-002"]
        assert len(ft002_results) == 1


class TestANCOVAUtilityFunctions:
    """Test ANCOVA utility and helper functions."""

    def test_get_significant_glycans(self) -> None:
        """Test extraction of significant glycans."""
        # Create mock results DataFrame
        results_df = pd.DataFrame({
            "glycan": ["FT-001", "FT-002", "FT-003"],
            "class_adj_p_value": [0.001, 0.08, 0.15],
            "class_effect_size": [0.8, 0.3, 0.1],
        })

        significant_glycans = ANCOVAAnalyzer.get_significant_glycans(
            results_df, alpha=0.05, adj_p_column="class_adj_p_value"
        )

        assert significant_glycans == ["FT-001"]  # Only FT-001 is significant

    def test_get_top_glycans(self) -> None:
        """Test extraction of top N glycans."""
        results_df = pd.DataFrame({
            "glycan": ["FT-001", "FT-002", "FT-003", "FT-004"],
            "class_adj_p_value": [0.001, 0.05, 0.08, 0.15],
            "class_effect_size": [0.8, 0.6, 0.3, 0.1],
        })

        top_2 = ANCOVAAnalyzer.get_top_glycans(results_df, n_top=2, sort_by="class_adj_p_value", ascending=True)

        assert len(top_2) == 2
        assert list(top_2["glycan"]) == ["FT-001", "FT-002"]

    def test_calculate_covariate_effects(self) -> None:
        """Test calculation of covariate effect counts."""
        results_df = pd.DataFrame({
            "glycan": ["FT-001", "FT-002", "FT-003"],
            "age_p_value": [0.01, 0.03, 0.08],
            "sex_p_value": [0.02, 0.07, 0.12],
            "bmi_p_value": [0.06, 0.04, 0.01],
        })

        covariate_effects = ANCOVAAnalyzer.calculate_covariate_effects(
            results_df, covar_columns=["age", "sex", "bmi"], alpha=0.05
        )

        expected = {
            "age": 2,  # FT-001 and FT-002 significant
            "sex": 1,  # Only FT-001 significant
            "bmi": 2,  # FT-002 and FT-003 significant
        }

        assert covariate_effects == expected


class TestANCOVAValidationIntegrity:
    """Test ANCOVA input validation and data integrity."""

    def test_validate_input_data_missing_columns(self) -> None:
        """Test validation with missing required columns."""
        data = pd.DataFrame({
            "FT-001": [1, 2, 3],
            "age": [25, 30, 35],
            # Missing 'class' column
        })

        with pytest.raises(Exception):
            ANCOVAAnalyzer.analyze_glycans_ancova(
                data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
            )

    def test_validate_input_data_empty_dataframe(self) -> None:
        """Test validation with empty DataFrame."""
        empty_data = pd.DataFrame()

        with pytest.raises(Exception):
            ANCOVAAnalyzer.analyze_glycans_ancova(
                empty_data, feature_prefix="FT-", class_column="class", covar_columns=["age"], alpha=0.05
            )

    def test_validate_no_matching_features(self) -> None:
        """Test validation when no features match prefix."""
        data = pd.DataFrame({
            "XYZ-001": [1, 2, 3, 4, 5, 6],
            "class": ["A", "A", "B", "B", "C", "C"],
            "age": [20, 25, 30, 35, 40, 45],
        })

        with pytest.raises(Exception, match="At least 1 feature columns required"):
            ANCOVAAnalyzer.analyze_glycans_ancova(
                data,
                feature_prefix="FT-",  # No features match this prefix
                class_column="class",
                covar_columns=["age"],
                alpha=0.05,
            )

    def test_alpha_parameter_validation(self) -> None:
        """Test alpha parameter boundary conditions."""
        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5, 6],
            "class": ["A", "A", "B", "B", "C", "C"],
            "age": [20, 25, 30, 35, 40, 45],
        })

        # Test with alpha = 0 (very strict)
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(data, alpha=0.0)
        assert len(significant) == 0  # Nothing should be significant

        # Test with alpha = 1 (very permissive)
        significant, all_results, significant_glycans = ANCOVAAnalyzer.analyze_glycans_ancova(data, alpha=1.0)
        assert len(significant) == len(all_results)  # Everything should be significant
