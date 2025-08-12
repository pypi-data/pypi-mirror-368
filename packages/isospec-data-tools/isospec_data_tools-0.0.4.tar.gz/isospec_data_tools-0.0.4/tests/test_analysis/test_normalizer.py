"""Tests for preprocessing functions (formerly DataWrangler class)."""

import numpy as np
import pandas as pd
import pytest

# Import individual preprocessing functions from new modular structure
from isospec_data_tools.analysis.core.project_config import DataStructureConfig
from isospec_data_tools.analysis.preprocessing.normalizers import (
    filter_data_matrix_samples,
    impute_missing_values,
    median_quotient_normalization,
    total_abundance_normalization,
)
from isospec_data_tools.analysis.preprocessing.transformers import (
    encode_categorical_column,
    filter_data_by_column_value,
    join_sample_metadata,
    log2_transform_numeric,
    replace_column_values,
)
from isospec_data_tools.analysis.preprocessing.validators import validate_dataframe


class TestPreprocessingFunctions:
    """Test cases for preprocessing functions (formerly DataWrangler)."""

    def test_validate_dataframe_valid(self) -> None:
        """Test that valid DataFrames pass validation."""
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        # Should not raise any exception
        validate_dataframe(df, "test data")

    def test_validate_dataframe_invalid_type(self) -> None:
        """Test that non-DataFrame inputs raise TypeError."""
        with pytest.raises(TypeError, match="must be a pandas DataFrame"):
            validate_dataframe([1, 2, 3], "test data")  # type: ignore[arg-type]

    def test_validate_dataframe_empty(self) -> None:
        """Test that empty DataFrames raise ValueError."""
        df = pd.DataFrame()
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_dataframe(df, "test data")

    # Note: Tests for private functions _get_feature_columns and _get_numeric_columns
    # have been removed as these are now internal implementation details.
    # The functionality is tested through the public API functions that use them.

    def test_total_abundance_normalization(self) -> None:
        """Test total abundance normalization."""
        df = pd.DataFrame({"FT-1": [10, 20], "FT-2": [5, 15], "meta": ["A", "B"]})
        normalized = total_abundance_normalization(df, prefix="FT-")

        # Check that metadata is preserved
        assert "meta" in normalized.columns
        assert list(normalized["meta"]) == ["A", "B"]

        # Check normalization (should sum to 1 for each row)
        feature_cols = ["FT-1", "FT-2"]
        row_sums = normalized[feature_cols].sum(axis=1)
        np.testing.assert_allclose(row_sums, [1.0, 1.0])

    def test_total_abundance_normalization_no_prefix(self) -> None:
        """Test total abundance normalization without prefix."""
        df = pd.DataFrame({"A": [10, 20], "B": [5, 15], "meta": ["A", "B"]})
        normalized = total_abundance_normalization(df)

        # Check that metadata is preserved
        assert "meta" in normalized.columns

        # Check normalization
        numeric_cols = ["A", "B"]
        row_sums = normalized[numeric_cols].sum(axis=1)
        np.testing.assert_allclose(row_sums, [1.0, 1.0])

    def test_median_quotient_normalization(self) -> None:
        """Test median quotient normalization."""
        df = pd.DataFrame({"FT-1": [10, 20, 15], "FT-2": [5, 15, 10], "SampleType": ["QC", "Sample", "QC"]})
        normalized = median_quotient_normalization(df)

        # Check that metadata is preserved
        assert "SampleType" in normalized.columns
        assert list(normalized["SampleType"]) == ["QC", "Sample", "QC"]

        # Check that features are present
        assert "FT-1" in normalized.columns
        assert "FT-2" in normalized.columns

    def test_filter_data_matrix_samples(self) -> None:
        """Test sample filtering."""
        df = pd.DataFrame({"sample": ["Sample1", "QC1", "Sample2"], "value": [1, 2, 3]})
        filtered = filter_data_matrix_samples(df)

        # Should filter out QC1
        assert len(filtered) == 2
        assert "QC1" not in filtered["sample"].values

    def test_impute_missing_values(self) -> None:
        """Test QC-based missing value imputation."""
        # Create test data with NaN values and QC samples
        df = pd.DataFrame({
            "FT1": [2, np.nan, 3, np.nan],  # NaN in sample positions
            "FT2": [4, 5, np.nan, np.nan],  # NaN in QC and sample
            "SampleType": ["QC", "Sample", "QC", "Sample"],
        })

        config = DataStructureConfig(feature_prefix="FT", sample_type_column="SampleType")
        imputed = impute_missing_values(df, data_config=config, method="qc_min")

        # Check that metadata is preserved
        assert "SampleType" in imputed.columns

        # Check that features are present
        assert "FT1" in imputed.columns
        assert "FT2" in imputed.columns

        # Check that NaN values were imputed with QC minimums
        # FT1 QC values are [2, 3], minimum is 2
        assert imputed.loc[1, "FT1"] == 2  # Sample NaN becomes 2
        assert imputed.loc[3, "FT1"] == 2  # Sample NaN becomes 2
        # FT2 QC values are [4, NaN], minimum is 4 (NaN ignored)
        assert imputed.loc[2, "FT2"] == 4  # QC NaN becomes 4
        assert imputed.loc[3, "FT2"] == 4  # Sample NaN becomes 4

    def test_impute_missing_values_median_method(self) -> None:
        """Test median-based missing value imputation."""
        df = pd.DataFrame({
            "FT1": [1, np.nan, 3, 4],
            "FT2": [2, 5, np.nan, 8],
            "SampleType": ["QC", "Sample", "QC", "Sample"],
        })

        config = DataStructureConfig(feature_prefix="FT", sample_type_column="SampleType")
        imputed = impute_missing_values(df, data_config=config, method="median")

        # Check that missing values were imputed with median of QC samples
        # FT1: QC values are [1, 3], median is 2
        assert imputed.loc[1, "FT1"] == 2
        # FT2: QC values are [2, NaN], median is 2 (NaN ignored)
        assert imputed.loc[2, "FT2"] == 2

    def test_impute_missing_values_with_qc_nan(self) -> None:
        """Test QC-based imputation when QC samples contain NaN values."""
        # Create test data where QC samples have NaN values
        df = pd.DataFrame({
            "FT1": [np.nan, 2, 3, np.nan],  # QC has NaN
            "FT2": [5, np.nan, np.nan, 8],  # Both QC and sample have NaN
            "SampleType": ["QC", "Sample", "QC", "Sample"],
        })

        config = DataStructureConfig(feature_prefix="FT", sample_type_column="SampleType")
        imputed = impute_missing_values(df, data_config=config, method="qc_min")

        # FT1 QC values are [NaN, 3], minimum is 3 (NaN ignored)
        assert imputed.loc[0, "FT1"] == 3  # QC NaN becomes 3
        assert imputed.loc[3, "FT1"] == 3  # Sample NaN becomes 3

        # FT2 QC values are [5, NaN], minimum is 5 (NaN ignored)
        assert imputed.loc[1, "FT2"] == 5  # Sample NaN becomes 5
        assert imputed.loc[2, "FT2"] == 5  # QC NaN becomes 5

    def test_join_sample_metadata(self) -> None:
        """Test metadata joining."""
        data_df = pd.DataFrame({"sample": ["A", "B"], "value": [1, 2]})
        meta_df = pd.DataFrame({"SampleID": ["A", "B"], "group": ["G1", "G2"]})

        joined = join_sample_metadata(data_df, meta_df)

        # Check that all columns are present
        assert "sample" in joined.columns
        assert "value" in joined.columns
        assert "group" in joined.columns

        # Check that metadata was joined correctly
        assert joined.loc[joined["sample"] == "A", "group"].iloc[0] == "G1"
        assert joined.loc[joined["sample"] == "B", "group"].iloc[0] == "G2"

    def test_replace_column_values(self) -> None:
        """Test column value replacement."""
        df = pd.DataFrame({"col": ["A", "B", "A"]})
        result = replace_column_values(df, "col", mapping={"A": "X"})

        # Check replacement
        assert list(result["col"]) == ["X", "B", "X"]

    def test_log2_transform_numeric(self) -> None:
        """Test log2 transformation."""
        df = pd.DataFrame({"FT1": [1, 2, 4], "FT2": [8, 16, 32], "meta": ["A", "B", "C"]})
        transformed = log2_transform_numeric(df, prefix="FT")

        # Check that metadata is preserved
        assert "meta" in transformed.columns

        # Check log2 transformation
        assert transformed.loc[0, "FT1"] == 0.0  # log2(1) = 0
        assert transformed.loc[1, "FT1"] == 1.0  # log2(2) = 1
        assert transformed.loc[2, "FT1"] == 2.0  # log2(4) = 2

    def test_encode_categorical_column(self) -> None:
        """Test categorical column encoding."""
        df = pd.DataFrame({"sex": ["M", "F", "M"]})
        result = encode_categorical_column(df, "sex", {"M": 1, "F": 0})

        # Check that original column is preserved
        assert "sex" in result.columns

        # Check that encoded column is added
        assert "sex_encoded" in result.columns

        # Check encoding
        assert list(result["sex_encoded"]) == [1, 0, 1]

    def test_filter_data_by_column_value(self) -> None:
        """Test data filtering by column value."""
        df = pd.DataFrame({"group": ["A", "B", "A"], "value": [1, 2, 3]})
        filtered = filter_data_by_column_value(df, "group", "A")

        # Should only keep rows where group == 'A'
        assert len(filtered) == 2
        assert all(filtered["group"] == "A")
