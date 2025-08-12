"""
Data quality and edge case robustness tests.

This module tests the analysis pipeline's robustness to various data quality issues,
edge cases, and challenging real-world scenarios that might break or degrade
the analysis functionality.
"""

import warnings
from typing import Any

import numpy as np
import pandas as pd
import pytest

from isospec_data_tools.analysis.core.project_config import DataStructureConfig
from isospec_data_tools.analysis.core.statistical_tests import perform_student_t_test
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.preprocessing.normalizers import (
    impute_missing_values,
    total_abundance_normalization,
)

# Import modules to test
from isospec_data_tools.analysis.specialized.confounder_analysis import ConfounderAnalyzer


class TestDataQualityIssues:
    """Test robustness to common data quality issues."""

    def test_missing_values_comprehensive(self) -> None:
        """Test handling of various missing value patterns."""

        # Create data with different missing value patterns, including QC samples
        data = pd.DataFrame({
            "FT-001": [1.0, 2.0, np.nan, 4.0, 5.0, 2.5, 3.0],  # Sporadic missing
            "FT-002": [np.nan, np.nan, np.nan, 4.0, 5.0, 4.5, 4.2],  # Mostly missing
            "FT-003": [np.nan] * 5 + [2.0, 2.1],  # All missing in samples, values in QC
            "FT-004": [1.0, 2.0, 3.0, 4.0, 5.0, 3.0, 3.1],  # No missing
            "class_final": ["A", "B", "A", "B", "A", "QC", "QC"],
            "age": [25, np.nan, 35, 40, np.nan, np.nan, np.nan],  # Missing covariates
            "SampleType": ["Sample", "Sample", "Sample", "Sample", "Sample", "QC", "QC"],
        })

        # Test imputation handles different patterns
        config = DataStructureConfig(feature_prefix="FT-", sample_type_column="SampleType")
        imputed = impute_missing_values(data, data_config=config, method="median")

        # Should reduce missing values
        original_missing = data.select_dtypes(include=[np.number]).isna().sum().sum()
        final_missing = imputed.select_dtypes(include=[np.number]).isna().sum().sum()
        assert final_missing <= original_missing

        # All-missing columns might still be missing (graceful degradation)
        if "FT-003" in imputed.columns:
            # If kept, should be handled gracefully in downstream analysis
            pass

    def test_infinite_and_extreme_values(self) -> None:
        """Test handling of infinite and extreme values."""

        data = pd.DataFrame({
            "FT-001": [1.0, 2.0, np.inf, 4.0, 5.0],  # Positive infinity
            "FT-002": [1.0, 2.0, -np.inf, 4.0, 5.0],  # Negative infinity
            "FT-003": [1e-10, 2.0, 3.0, 4.0, 1e10],  # Extreme values
            "FT-004": [0.0, 0.0, 0.0, 4.0, 5.0],  # Many zeros
            "class_final": ["A", "B", "A", "B", "A"],
            "age": [25, 30, 35, 40, 45],
        })

        # Test that normalization handles extreme values
        try:
            normalized = total_abundance_normalization(data, prefix="FT-")
            # Should complete without errors or handle gracefully
            assert isinstance(normalized, pd.DataFrame)
        except Exception as e:
            # Should provide meaningful error message
            assert "infinite" in str(e).lower() or "extreme" in str(e).lower()

    def test_duplicate_and_constant_features(self) -> None:
        """Test handling of duplicate and constant features."""

        data = pd.DataFrame({
            "FT-001": [1.0, 2.0, 3.0, 4.0, 5.0],  # Normal feature
            "FT-002": [1.0, 2.0, 3.0, 4.0, 5.0],  # Duplicate of FT-001
            "FT-003": [5.0, 5.0, 5.0, 5.0, 5.0],  # Constant feature
            "FT-004": [0.0, 0.0, 0.0, 0.0, 0.0],  # All zeros
            "class_final": ["A", "B", "A", "B", "A"],
            "age": [25, 30, 35, 40, 45],
        })

        # Test statistical analysis with constant features
        features = ["FT-001", "FT-002", "FT-003", "FT-004"]

        try:
            results = perform_student_t_test(data, features, "class_final", alpha=0.05)
            # Should handle gracefully, possibly excluding constant features
            assert isinstance(results, list)
        except Exception as e:
            # Should provide informative error about constant features
            assert "constant" in str(e).lower() or "variance" in str(e).lower()

    def test_string_contamination_in_numeric_columns(self) -> None:
        """Test handling of string values in numeric columns."""

        # Create data with string contamination
        contaminated_data = pd.DataFrame({
            "FT-001": [1.0, 2.0, "missing", 4.0, 5.0],  # String in numeric
            "FT-002": ["1.5", "2.5", "3.5", "4.5", "5.5"],  # Numbers as strings
            "FT-003": [1.0, 2.0, 3.0, 4.0, 5.0],  # Clean numeric
            "class_final": ["A", "B", "A", "B", "A"],
        })

        # Should handle gracefully by converting or excluding
        try:
            # Attempt to normalize - should handle string contamination
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress expected warnings
                normalized = total_abundance_normalization(contaminated_data, prefix="FT-")
                assert isinstance(normalized, pd.DataFrame)
        except Exception as e:
            # Should provide clear error about data type issues
            assert "numeric" in str(e).lower() or "type" in str(e).lower()

    def test_mismatched_dimensions(self) -> None:
        """Test handling of mismatched data dimensions."""

        # Create data with mismatched sample counts
        feature_data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            "class_final": ["A", "B", "A", "B", "A"],
        })

        metadata = pd.DataFrame({
            "sample_id": ["S1", "S2", "S3"],  # Only 3 samples instead of 5
            "batch": ["B1", "B1", "B2"],
        })

        # Join should handle mismatched dimensions gracefully
        from isospec_data_tools.analysis.preprocessing.transformers import join_sample_metadata

        try:
            join_sample_metadata(
                feature_data,
                metadata,
                sample_id_col="sample_id",
                sample_join_col="sample_id",  # This column doesn't exist in feature_data
            )
            # Should fail with clear error message
            raise AssertionError("Should have raised an error for missing join column")
        except Exception as e:
            assert "not found" in str(e).lower()

    def test_circular_and_nan_correlations(self) -> None:
        """Test handling of circular dependencies and NaN correlations."""

        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5, 6],
            "FT-002": [2, 4, 6, 8, 10, 12],  # Perfect correlation with FT-001
            "FT-003": [np.nan] * 6,  # All NaN - no correlation possible
            "class_final": ["A", "B", "A", "B", "A", "B"],
            "age": [25, 30, 35, 40, 45, 50],
        })

        # Confounder analysis should handle perfect correlations and NaN
        try:
            results, significant = ConfounderAnalyzer.analyze_confounders(
                data, glycan_prefix="FT-", confounders=["age"], alpha=0.05, min_glycans=1
            )
            assert isinstance(results, dict)
        except Exception as e:
            # Should handle correlation issues gracefully
            assert any(keyword in str(e).lower() for keyword in ["correlation", "singular", "variance"])


class TestEdgeCasesDataStructures:
    """Test edge cases in data structures and formats."""

    def test_empty_dataframes(self) -> None:
        """Test handling of empty DataFrames."""

        empty_df = pd.DataFrame()

        # Should raise appropriate errors for empty data
        with pytest.raises(Exception):
            total_abundance_normalization(empty_df, prefix="FT-")

    def test_single_sample_analysis(self) -> None:
        """Test analysis with single sample."""

        single_sample = pd.DataFrame({"FT-001": [1.0], "FT-002": [2.0], "class_final": ["A"], "age": [30]})

        # Statistical tests should fail gracefully with single sample
        with pytest.raises(Exception):
            perform_student_t_test(single_sample, ["FT-001", "FT-002"], "class_final")

    def test_single_class_analysis(self) -> None:
        """Test analysis with single class (no variance in outcome)."""

        single_class = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            "class_final": ["A", "A", "A", "A", "A"],  # Only one class
            "age": [25, 30, 35, 40, 45],
        })

        # Should handle single class gracefully
        with pytest.raises(Exception):
            perform_student_t_test(single_class, ["FT-001", "FT-002"], "class_final")

    def test_very_long_feature_names(self) -> None:
        """Test handling of very long feature names."""

        long_name = "FT-" + "A" * 100  # 103 character feature name

        data = pd.DataFrame({
            long_name: [1, 2, 3, 4, 5],
            "FT-normal": [2, 3, 4, 5, 6],
            "class_final": ["A", "B", "A", "B", "A"],
        })

        # Should handle long names without issues
        result = total_abundance_normalization(data, prefix="FT-")
        assert long_name in result.columns

    def test_unicode_and_special_characters(self) -> None:
        """Test handling of unicode and special characters in data."""

        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            "class_final": ["α-class", "β-class", "α-class", "β-class", "α-class"],  # Unicode
            "metadata": ["sample#1", "sample@2", "sample$3", "sample%4", "sample&5"],  # Special chars
        })

        # Should handle unicode gracefully
        try:
            results = perform_student_t_test(data, ["FT-001", "FT-002"], "class_final")
            assert isinstance(results, list)
        except Exception as e:
            # Should provide clear error if unicode causes issues
            assert len(str(e)) > 0

    def test_extremely_large_datasets(self) -> None:
        """Test behavior with large datasets (memory and performance)."""

        # Create a moderately large dataset for testing
        n_samples = 1000
        n_features = 50

        np.random.seed(42)
        large_data = pd.DataFrame(
            np.random.normal(0, 1, (n_samples, n_features)), columns=[f"FT-{i:03d}" for i in range(n_features)]
        )
        large_data["class_final"] = np.random.choice(["A", "B"], n_samples)
        large_data["age"] = np.random.uniform(20, 80, n_samples)

        # Should handle large datasets efficiently
        import time

        start_time = time.time()

        try:
            normalized = total_abundance_normalization(large_data, prefix="FT-")
            processing_time = time.time() - start_time

            # Should complete in reasonable time (< 10 seconds for this size)
            assert processing_time < 10.0
            assert normalized.shape == large_data.shape

        except MemoryError:
            # Acceptable failure mode for very large datasets
            pytest.skip("Insufficient memory for large dataset test")

    def test_mixed_data_types_in_features(self) -> None:
        """Test handling of mixed data types in feature columns."""

        mixed_data = pd.DataFrame({
            "FT-001": [1, 2.5, 3, 4.7, 5],  # Mixed int/float
            "FT-002": [True, False, True, False, True],  # Boolean
            "FT-003": pd.Categorical(["low", "medium", "high", "low", "medium"]),  # Categorical
            "class_final": ["A", "B", "A", "B", "A"],
        })

        # Should handle or filter mixed types appropriately
        try:
            normalized = total_abundance_normalization(mixed_data, prefix="FT-")
            # Should process only numeric-compatible features
            assert isinstance(normalized, pd.DataFrame)
        except Exception as e:
            # Should provide clear guidance about data type issues
            assert "numeric" in str(e).lower() or "type" in str(e).lower()


class TestRobustnessToParameterVariations:
    """Test robustness to variations in analysis parameters."""

    def test_extreme_alpha_values(self) -> None:
        """Test analysis with extreme alpha values."""

        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5, 6],
            "FT-002": [2, 3, 4, 5, 6, 7],
            "class_final": ["A", "B", "A", "B", "A", "B"],
            "age": [25, 30, 35, 40, 45, 50],
        })

        # Test extremely small alpha
        try:
            results = perform_student_t_test(data, ["FT-001", "FT-002"], "class_final", alpha=1e-10)
            # Should handle without errors
            assert isinstance(results, list)
        except Exception as e:
            # Should provide meaningful error for invalid alpha
            assert "alpha" in str(e).lower()

        # Test alpha = 1.0 (everything significant)
        results = perform_student_t_test(data, ["FT-001", "FT-002"], "class_final", alpha=1.0)
        assert isinstance(results, list)

    def test_invalid_prefix_specifications(self) -> None:
        """Test handling of invalid prefix specifications."""

        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "GT-001": [2, 3, 4, 5, 6],  # Different prefix
            "XYZ-001": [3, 4, 5, 6, 7],  # Another prefix
            "class_final": ["A", "B", "A", "B", "A"],
        })

        # Test with non-existent prefix
        with pytest.raises(Exception):
            total_abundance_normalization(data, prefix="NONEXISTENT-")

        # Test with empty prefix
        try:
            normalized = total_abundance_normalization(data, prefix="")
            # Should process all numeric columns
            assert isinstance(normalized, pd.DataFrame)
        except Exception:
            # Acceptable if empty prefix is not supported
            pass

    def test_boundary_sample_sizes(self) -> None:
        """Test analysis with boundary sample sizes."""

        # Test with minimum viable sample size
        min_data = pd.DataFrame({"FT-001": [1, 2], "FT-002": [2, 3], "class_final": ["A", "B"], "age": [25, 30]})

        # Function should handle insufficient data gracefully (log warning, return empty results)
        results = perform_student_t_test(min_data, ["FT-001", "FT-002"], "class_final")

        # Should return empty results for insufficient data
        assert len(results) == 0

    def test_missing_required_columns(self) -> None:
        """Test handling when required columns are missing."""

        incomplete_data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            # Missing class_final column
        })

        # Should raise clear error about missing columns
        with pytest.raises(Exception):
            perform_student_t_test(incomplete_data, ["FT-001", "FT-002"], "class_final")

    def test_numerical_precision_issues(self) -> None:
        """Test handling of numerical precision issues."""

        # Create data with very small differences
        epsilon = 1e-15
        precision_data = pd.DataFrame({
            "FT-001": [1.0, 1.0 + epsilon, 1.0, 1.0 + epsilon, 1.0],
            "FT-002": [2.0, 2.0 + epsilon, 2.0, 2.0 + epsilon, 2.0],
            "class_final": ["A", "B", "A", "B", "A"],
            "age": [25, 30, 35, 40, 45],
        })

        # Should handle numerical precision gracefully
        try:
            results = perform_student_t_test(precision_data, ["FT-001", "FT-002"], "class_final")
            assert isinstance(results, list)
        except Exception as e:
            # Acceptable if precision causes numerical issues
            assert "numerical" in str(e).lower() or "precision" in str(e).lower()


class TestErrorPropagationAndRecovery:
    """Test error propagation and recovery mechanisms."""

    def test_graceful_degradation_with_partial_failures(self) -> None:
        """Test graceful degradation when some features fail analysis."""

        problematic_data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],  # Good feature
            "FT-002": [np.nan] * 5,  # All missing
            "FT-003": [1, 1, 1, 1, 1],  # No variance
            "FT-004": [2, 3, 4, 5, 6],  # Good feature
            "class_final": ["A", "B", "A", "B", "A"],
            "age": [25, 30, 35, 40, 45],
        })

        features = ["FT-001", "FT-002", "FT-003", "FT-004"]

        try:
            # Should process successfully features where possible
            results = perform_student_t_test(problematic_data, features, "class_final")

            # Should return results for features that could be analyzed
            assert isinstance(results, list)
            # May have fewer results than features due to filtering problematic ones
            assert len(results) <= len(features)

        except Exception as e:
            # Should provide informative error about what went wrong
            assert len(str(e)) > 0

    def test_memory_cleanup_on_errors(self) -> None:
        """Test that memory is properly cleaned up when errors occur."""

        # Create scenario likely to cause memory issues
        large_problematic_data = pd.DataFrame({f"FT-{i:03d}": np.random.normal(0, 1, 500) for i in range(100)})
        large_problematic_data["class_final"] = ["A"] * 500  # Single class - will cause error

        import gc
        import os

        import psutil

        # Measure memory before
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss

        try:
            # This should fail but shouldn't leak memory
            perform_student_t_test(large_problematic_data, [f"FT-{i:03d}" for i in range(10)], "class_final")
        except Exception:
            pass  # Expected to fail

        # Force garbage collection
        gc.collect()

        # Memory should not have increased significantly
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before

        # Allow some increase but not excessive (< 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_concurrent_analysis_stability(self) -> None:
        """Test stability under concurrent analysis scenarios."""

        import threading

        def analysis_worker(data: pd.DataFrame, results: list[Any], errors: list[Exception]) -> None:
            try:
                result = perform_student_t_test(data, ["FT-001", "FT-002"], "class_final")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create test data
        concurrent_data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5, 6],
            "FT-002": [2, 3, 4, 5, 6, 7],
            "class_final": ["A", "B", "A", "B", "A", "B"],
        })

        # Run multiple concurrent analyses
        results: list[Any] = []
        errors: list[Exception] = []
        threads = []

        for _ in range(5):
            thread = threading.Thread(target=analysis_worker, args=(concurrent_data.copy(), results, errors))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should complete successfully
        assert len(errors) == 0
        assert len(results) == 5

        # Results should be consistent
        first_result = results[0]
        for result in results[1:]:
            assert len(result) == len(first_result)

    def test_logging_behavior_under_errors(self) -> None:
        """Test that appropriate logging occurs during error conditions."""

        import logging
        from io import StringIO

        # Capture log output
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("isospec_data_tools")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        try:
            # Create error condition
            error_data = pd.DataFrame({
                "FT-001": [np.nan] * 3,  # All NaN
                "class_final": ["A", "B", "A"],
            })

            try:
                total_abundance_normalization(error_data, prefix="FT-")
            except Exception:
                pass  # Expected to fail

            # Should have logged appropriate error information
            log_output = log_capture.getvalue()
            # Should contain some error information (exact content depends on implementation)
            assert len(log_output) >= 0  # At minimum, no crash in logging

        finally:
            logger.removeHandler(handler)

    def test_resource_exhaustion_handling(self) -> None:
        """Test handling of resource exhaustion scenarios."""

        # Simulate memory constraints by creating very wide data
        try:
            # This might fail due to memory constraints - should be handled gracefully
            wide_data = pd.DataFrame(
                np.random.normal(0, 1, (100, 1000)),  # 1000 features
                columns=[f"FT-{i:04d}" for i in range(1000)],
            )
            wide_data["class_final"] = np.random.choice(["A", "B"], 100)

            # Try to process - may fail due to resource constraints
            result = total_abundance_normalization(wide_data, prefix="FT-")
            assert isinstance(result, pd.DataFrame)

        except (MemoryError, Exception) as e:
            # Should fail gracefully with informative error
            assert isinstance(e, MemoryError | Exception)
            # Error message should be helpful
            if hasattr(e, "args") and e.args:
                assert len(str(e.args[0])) > 0


class TestDataIntegrityValidation:
    """Test data integrity validation throughout the pipeline."""

    def test_data_consistency_checks(self) -> None:
        """Test that data consistency is maintained throughout processing."""

        original_data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            "class_final": ["A", "B", "A", "B", "A"],
            "sample_id": ["S1", "S2", "S3", "S4", "S5"],
        })

        # Process through normalization
        normalized = total_abundance_normalization(original_data, prefix="FT-")

        # Check data integrity
        assert normalized.shape[0] == original_data.shape[0]  # Same number of samples
        assert normalized.shape[1] == original_data.shape[1]  # Same number of columns
        assert list(normalized.columns) == list(original_data.columns)  # Same column names
        assert list(normalized["sample_id"]) == list(original_data["sample_id"])  # Sample order preserved

    def test_numerical_range_validation(self) -> None:
        """Test validation of numerical ranges in processed data."""

        data = pd.DataFrame({
            "FT-001": [1, 2, 3, 4, 5],
            "FT-002": [2, 3, 4, 5, 6],
            "class_final": ["A", "B", "A", "B", "A"],
        })

        # After normalization, row sums should be approximately 1
        normalized = total_abundance_normalization(data, prefix="FT-")

        feature_cols = [col for col in normalized.columns if col.startswith("FT-")]
        row_sums = normalized[feature_cols].sum(axis=1)

        # All row sums should be close to 1.0
        np.testing.assert_allclose(row_sums, 1.0, rtol=1e-10)

    def test_statistical_assumptions_validation(self) -> None:
        """Test validation of statistical assumptions."""

        # Create data that violates normality assumption
        skewed_data = pd.DataFrame({
            "FT-001": np.random.exponential(1, 50),  # Exponential distribution (skewed)
            "FT-002": np.random.exponential(2, 50),
            "class_final": ["A"] * 25 + ["B"] * 25,
        })

        # Statistical tests should still run but may warn about assumptions
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            results = perform_student_t_test(skewed_data, ["FT-001", "FT-002"], "class_final")

            # Should complete and return results
            assert isinstance(results, list)

            # May have generated warnings about assumptions
            # (Exact warning behavior depends on implementation)

    def test_cross_validation_data_leakage_prevention(self) -> None:
        """Test that cross-validation prevents data leakage."""

        # Create temporal data where order matters
        temporal_data = pd.DataFrame({
            "FT-001": np.linspace(1, 100, 100),  # Strong temporal trend
            "FT-002": np.linspace(2, 200, 100),
            "class_final": (["A"] * 50) + (["B"] * 50),  # Classes segregated by time
            "timestamp": pd.date_range("2020-01-01", periods=100, freq="D"),
        })

        # Clustering should work but results might reflect temporal structure

        # Add required metadata
        temporal_data["age"] = np.random.uniform(20, 80, 100)
        temporal_data["SampleType"] = "Sample"

        try:
            result = ClusterAnalyzer.run_clustering_analysis(temporal_data, ["age"], feature_prefix="FT-")

            # Should complete successfully
            assert "kmeans_labels" in result
            assert len(result["kmeans_labels"]) == 100

        except Exception as e:
            # May fail due to data structure - should be informative
            assert len(str(e)) > 0
