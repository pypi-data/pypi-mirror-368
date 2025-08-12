"""Tests for the method plotting utilities."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from isospec_data_tools.visualization.analysis.method_plot import (
    CVAnalyzer,
    MethodPlotter,
    PlotStyler,
    SignificanceMarker,
)


class TestSignificanceMarker:
    """Test cases for SignificanceMarker class."""

    def test_pvalue_to_marker_highly_significant(self) -> None:
        """Test p-value to marker conversion for highly significant values."""
        assert SignificanceMarker.pvalue_to_marker(0.0001) == "***"
        assert SignificanceMarker.pvalue_to_marker(0.0009) == "***"

    def test_pvalue_to_marker_significant(self) -> None:
        """Test p-value to marker conversion for significant values."""
        assert SignificanceMarker.pvalue_to_marker(0.005) == "**"
        assert SignificanceMarker.pvalue_to_marker(0.009) == "**"

    def test_pvalue_to_marker_marginally_significant(self) -> None:
        """Test p-value to marker conversion for marginally significant values."""
        assert SignificanceMarker.pvalue_to_marker(0.01) == "*"
        assert SignificanceMarker.pvalue_to_marker(0.04) == "*"

    def test_pvalue_to_marker_not_significant(self) -> None:
        """Test p-value to marker conversion for non-significant values."""
        assert SignificanceMarker.pvalue_to_marker(0.06) == "ns"
        assert SignificanceMarker.pvalue_to_marker(0.5) == "ns"


class TestCVAnalyzer:
    """Test cases for CVAnalyzer class."""

    def test_compute_cv_by_sample_type(self) -> None:
        """Test CV computation by sample type."""
        data = pd.DataFrame({
            "FT-1": [10, 12, 8, 15, 18, 12],
            "FT-2": [5, 6, 4, 7, 8, 6],
            "SampleType": ["QC", "QC", "QC", "Sample", "Sample", "Sample"],
        })

        cv_results = CVAnalyzer.compute_cv_by_sample_type(data)

        # Check structure
        assert "SampleType" in cv_results.columns
        assert "Feature" in cv_results.columns
        assert "CV" in cv_results.columns

        # Check that we have results for both sample types
        sample_types = cv_results["SampleType"].unique()
        assert len(sample_types) == 2
        assert "QC" in sample_types
        assert "Sample" in sample_types

        # Check that we have results for both features
        features = cv_results["Feature"].unique()
        assert len(features) == 2
        assert "FT-1" in features
        assert "FT-2" in features

    def test_compute_cv_by_sample_type_empty_data(self) -> None:
        """Test CV computation with empty data."""
        data = pd.DataFrame()
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            CVAnalyzer.compute_cv_by_sample_type(data)

    def test_compute_cv_by_sample_type_missing_column(self) -> None:
        """Test CV computation with missing sample type column."""
        data = pd.DataFrame({"FT-1": [10, 12, 8], "FT-2": [5, 6, 4]})
        with pytest.raises(ValueError, match="Sample type column"):
            CVAnalyzer.compute_cv_by_sample_type(data)

    def test_compute_cv_by_sample_type_no_features(self) -> None:
        """Test CV computation with no feature columns."""
        data = pd.DataFrame({"A": [10, 12, 8], "SampleType": ["QC", "QC", "QC"]})
        with pytest.raises(ValueError, match="No feature columns found"):
            CVAnalyzer.compute_cv_by_sample_type(data)


class TestPlotStyler:
    """Test cases for PlotStyler class."""

    def test_setup_seaborn_style(self) -> None:
        """Test seaborn style setup."""
        # Should not raise any exception
        PlotStyler.setup_seaborn_style()

    def test_remove_grid(self) -> None:
        """Test grid removal."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.grid(True)

        # Should not raise any exception
        PlotStyler.remove_grid(ax)

        plt.close(fig)

    def test_apply_despine(self) -> None:
        """Test despine application."""
        # Should not raise any exception
        PlotStyler.apply_despine()


class TestMethodPlotter:
    """Test cases for MethodPlotter class."""

    def test_plot_cv_valid_data(self) -> None:
        """Test CV plotting with valid data."""
        cv_results = pd.DataFrame({
            "CV": [10, 15, 20, 25, 30, 35],
            "SampleType": ["QC", "QC", "QC", "Sample", "Sample", "Sample"],
            "Feature": ["FT-1", "FT-2", "FT-3", "FT-1", "FT-2", "FT-3"],
        })

        fig = MethodPlotter.plot_cv(cv_results)

        # Check that figure was created
        assert fig is not None
        assert hasattr(fig, "axes")

        plt.close(fig)

    def test_plot_cv_empty_data(self) -> None:
        """Test CV plotting with empty data."""
        cv_results = pd.DataFrame()
        with pytest.raises(ValueError, match="CV results DataFrame is empty"):
            MethodPlotter.plot_cv(cv_results)

    def test_plot_cv_missing_columns(self) -> None:
        """Test CV plotting with missing columns."""
        cv_results = pd.DataFrame({
            "CV": [10, 15, 20],
            "SampleType": ["QC", "QC", "QC"],
            # Missing 'Feature' column
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            MethodPlotter.plot_cv(cv_results)

    def test_plot_distribution_by_groups_valid_data(self) -> None:
        """Test distribution plotting with valid data."""
        data = pd.DataFrame({
            "age": [25, 30, 35, 40, 45, 50],
            "class_final": ["Control", "Control", "Control", "Disease", "Disease", "Disease"],
            "sex": ["M", "F", "M", "F", "M", "F"],
        })

        fig = MethodPlotter.plot_distribution_by_groups(data)

        # Check that figure was created
        assert fig is not None
        assert hasattr(fig, "axes")

        plt.close(fig)

    def test_plot_distribution_by_groups_empty_data(self) -> None:
        """Test distribution plotting with empty data."""
        data = pd.DataFrame()
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            MethodPlotter.plot_distribution_by_groups(data)

    def test_plot_distribution_by_groups_missing_columns(self) -> None:
        """Test distribution plotting with missing columns."""
        data = pd.DataFrame({
            "age": [25, 30, 35],
            "class_final": ["Control", "Control", "Control"],
            # Missing 'sex' column
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            MethodPlotter.plot_distribution_by_groups(data)

    def test_add_cv_legend_and_threshold(self) -> None:
        """Test legend and threshold addition to CV plot."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        # Add some dummy data to create a legend
        ax.plot([1, 2, 3], [1, 2, 3], label="Test")
        ax.legend()

        # Should not raise any exception
        MethodPlotter._add_cv_legend_and_threshold(ax)

        plt.close(fig)

    def test_create_group_boxplot(self) -> None:
        """Test group boxplot creation."""
        import matplotlib.pyplot as plt

        data = pd.DataFrame({
            "age": [25, 30, 35, 40],
            "class_final": ["Control", "Control", "Disease", "Disease"],
            "sex": ["M", "F", "M", "F"],
        })
        fig, ax = plt.subplots()

        # Should not raise any exception
        MethodPlotter._create_group_boxplot(data, "age", "class_final", "sex", ax)

        plt.close(fig)

    def test_add_significance_markers(self) -> None:
        """Test significance marker addition."""
        import matplotlib.pyplot as plt

        data = pd.DataFrame({
            "age": [25, 30, 35, 40],
            "class_final": ["Control", "Control", "Disease", "Disease"],
            "sex": ["M", "F", "M", "F"],
        })
        test_results = {
            "between_group": [{"group1": "Control", "group2": "Disease", "pvalue": 0.01}],
            "within_group": [{"group": "Control", "pvalue": 0.05}],
        }
        fig, ax = plt.subplots()

        # Should not raise any exception
        MethodPlotter._add_significance_markers(data, test_results, "age", "class_final", ax)

        plt.close(fig)

    def test_customize_group_plot(self) -> None:
        """Test group plot customization."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()

        # Should not raise any exception
        MethodPlotter._customize_group_plot(ax, "Test Title", "Age", "Group", "sex", ["Male", "Female"], None)

        plt.close(fig)
