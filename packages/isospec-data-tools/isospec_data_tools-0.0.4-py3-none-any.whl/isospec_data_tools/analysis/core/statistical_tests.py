"""Core statistical tests and operations.

This module provides fundamental statistical test implementations including
t-tests, ANOVA, chi-square tests, and other statistical operations used
throughout the analysis pipeline.
"""

import logging
from collections.abc import Callable
from enum import Enum
from typing import Any, Optional, TypedDict, Union

import numpy as np
import pandas as pd
import scipy.stats as stats

from .effect_sizes import calculate_cohens_d, calculate_fold_change
from .multiple_comparisons import adjust_p_values

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases
ArrayLike = Union[np.ndarray, pd.Series]
DataFrame = pd.DataFrame
Series = pd.Series
StatisticalTestFunc = Callable[[pd.Series, pd.Series, float], dict[str, Any]]


# Type definitions
class TestType(Enum):
    """Enumeration of statistical test types."""

    STUDENT_T = "student_t"
    WELCH_T = "welch_t"
    CHI_SQUARE = "chi_square"
    TUKEY_HSD = "tukey_hsd"


class BaseTestResult(TypedDict):
    """Base result structure for statistical tests."""

    feature: str
    group1: str
    group2: str
    p_value: float
    statistic: float


class TTestResult(BaseTestResult):
    """Result structure for t-tests."""

    mean_group1: float
    mean_group2: float
    mean_diff: float
    degrees_freedom: float
    ci_lower: float
    ci_upper: float
    t_statistic: float
    effect_size: Optional[float]
    fold_change: Optional[float]


class IndependenceTestResult(TypedDict):
    """Result structure for independence tests."""

    statistic: float
    p_value: float
    test_type: str


# Helper functions for common operations
def _extract_group_data(
    data: DataFrame, class_column: str, group1: str, group2: str, feature: str
) -> tuple[pd.Series, pd.Series]:
    """Extract and validate data for two groups.

    Args:
        data: DataFrame containing the data
        class_column: Column containing class labels
        group1: First group label
        group2: Second group label
        feature: Feature column to extract

    Returns:
        Tuple of (group1_data, group2_data) as pandas Series

    Raises:
        ValueError: If insufficient data in either group
    """
    group1_data = data[data[class_column] == group1][feature].dropna()
    group2_data = data[data[class_column] == group2][feature].dropna()

    if len(group1_data) < 2 or len(group2_data) < 2:
        raise ValueError(f"Insufficient data for comparison: {feature}, {group1}-{group2}")

    return group1_data, group2_data


def _add_effect_sizes_to_result(
    result_dict: dict[str, Any],
    group1_data: pd.Series,
    group2_data: pd.Series,
    mean_group1: float,
    mean_group2: float,
    include_effect_sizes: bool,
    log2_transform: bool,
) -> None:
    """Add effect sizes and fold changes to result dictionary in-place.

    Args:
        result_dict: Dictionary to update with effect sizes
        group1_data: Data for first group
        group2_data: Data for second group
        mean_group1: Mean of first group
        mean_group2: Mean of second group
        include_effect_sizes: Whether to include effect sizes
        log2_transform: Whether data is log2 transformed
    """
    if not include_effect_sizes:
        return

    from .effect_sizes import calculate_cohens_d, calculate_fold_change

    # Calculate Cohen's d effect size
    cohens_d = calculate_cohens_d(group1_data, group2_data)
    result_dict["effect_size"] = cohens_d

    # Calculate fold change
    fold_change = calculate_fold_change(mean_group1, mean_group2, log2_transform)
    result_dict["fold_change"] = fold_change


def _perform_pairwise_comparisons(
    data: DataFrame,
    feature_columns: list[str],
    class_column: str,
    test_func: Callable[..., dict[str, Any]],
    alpha: float = 0.05,
    include_effect_sizes: bool = True,
    log2_transform: bool = False,
    **test_kwargs: Any,
) -> list[dict[str, Any]]:
    """Generic function to perform pairwise comparisons between classes.

    Args:
        data: DataFrame containing the data
        feature_columns: List of feature columns to test
        class_column: Column containing class labels
        test_func: Statistical test function to use
        alpha: Significance level
        include_effect_sizes: Whether to include effect sizes
        log2_transform: Whether data is log2 transformed
        **test_kwargs: Additional arguments for the test function

    Returns:
        List of test results
    """
    classes = sorted(data[class_column].unique())
    if len(classes) < 2:
        raise ValueError(f"Need at least 2 classes for comparison, got {len(classes)}")

    results = []

    for feature in feature_columns:
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                group1, group2 = classes[i], classes[j]

                try:
                    # Extract and validate data
                    group1_data, group2_data = _extract_group_data(data, class_column, group1, group2, feature)

                    # Perform the statistical test
                    test_result = test_func(group1_data, group2_data, alpha=alpha, **test_kwargs)

                    # Build result dictionary
                    result_dict = {
                        "feature": feature,
                        "group1": group1,
                        "group2": group2,
                        **test_result,  # Unpack test-specific results
                    }

                    # Add effect sizes if requested
                    _add_effect_sizes_to_result(
                        result_dict,
                        group1_data,
                        group2_data,
                        test_result["mean_group1"],
                        test_result["mean_group2"],
                        include_effect_sizes,
                        log2_transform,
                    )

                    results.append(result_dict)

                except ValueError as e:
                    logger.warning(str(e))
                    continue
                except Exception:
                    logger.exception(f"Error in pairwise comparison for {feature}, {group1}-{group2}")
                    continue

    return results


def _perform_student_t_test_core(
    group1_data: pd.Series,
    group2_data: pd.Series,
    alpha: float = 0.05,
    equal_var: bool = True,
) -> dict[str, Any]:
    """Core Student's t-test logic.

    Args:
        group1_data: Data for first group
        group2_data: Data for second group
        alpha: Significance level
        equal_var: Whether to assume equal variances

    Returns:
        Dictionary with test results
    """
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(group1_data, group2_data, equal_var=equal_var)

    # Calculate statistics
    mean_group1, mean_group2 = np.mean(group1_data), np.mean(group2_data)
    n1, n2 = len(group1_data), len(group2_data)
    var1, var2 = np.var(group1_data, ddof=1), np.var(group2_data, ddof=1)

    if equal_var:
        # Student's t-test with pooled variance
        pooled_se = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        se_diff = pooled_se * np.sqrt(1 / n1 + 1 / n2)
        df = n1 + n2 - 2
    else:
        # Welch's t-test
        se_diff = np.sqrt(var1 / n1 + var2 / n2)
        df = ((var1 / n1 + var2 / n2) ** 2) / ((var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1))

    # Confidence intervals
    t_critical = stats.t.ppf(1 - alpha / 2, df)
    margin_error = t_critical * se_diff
    mean_diff = mean_group2 - mean_group1
    ci_lower = mean_diff - margin_error
    ci_upper = mean_diff + margin_error

    result = {
        "mean_group1": mean_group1,
        "mean_group2": mean_group2,
        "mean_diff": mean_diff,
        "t_statistic": t_stat,
        "p_value": p_value,
        "degrees_freedom": df,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }

    if not equal_var:
        result["welch_df"] = df

    return result


def _perform_chi_square_test_core(
    data: DataFrame,
    group_column: str,
    value_column: str,
    groups: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Core chi-square test logic for categorical data.

    Args:
        data: DataFrame containing the data
        group_column: Column containing group labels
        value_column: Column containing categorical values
        groups: Optional list of groups to include (if None, use all)

    Returns:
        Dictionary with test results
    """
    if groups:
        data = data[data[group_column].isin(groups)]

    # Create contingency table
    contingency = pd.crosstab(data[group_column], data[value_column])

    if contingency.size <= 1:
        raise ValueError("Insufficient categories for chi-square test")

    # Perform chi-square test
    result = stats.chi2_contingency(contingency)
    chi2_stat = result[0]
    p_value = result[1]
    dof = result[2]
    expected = result[3]

    return {
        "statistic": float(chi2_stat),
        "p_value": float(p_value),
        "degrees_freedom": int(dof),
        "contingency_table": contingency,
        "expected_frequencies": expected,
    }


def perform_tukey_hsd_test(
    data: DataFrame,
    feature_columns: list[str],
    class_column: str,
    alpha: float = 0.05,
    include_effect_sizes: bool = True,
    log2_transform: bool = False,
    return_format: str = "dataframe",
) -> Union[pd.DataFrame, str]:
    """Perform Tukey's HSD test for pairwise comparisons between classes.

    This function conducts Tukey's Honestly Significant Difference test to compare
    means across multiple groups while controlling for family-wise error rate.

    Args:
        data: DataFrame containing the data to analyze
        feature_columns: List of feature column names to test
        class_column: Name of the column containing class labels
        alpha: Significance level for testing
        include_effect_sizes: Whether to calculate Cohen's d effect sizes
        log2_transform: Whether the data is log2 transformed (affects fold change calculation)
        return_format: Format for results - "dataframe" (default) or "string" for legacy compatibility

    Returns:
        DataFrame with test results (default) or formatted string (legacy mode)

        BREAKING CHANGE: Previously returned string format by default.
        Now returns DataFrame by default for better programmatic access.
        Use return_format="string" for legacy string format during migration.

    Raises:
        ValueError: If insufficient data or invalid parameters

    Example:
        >>> import pandas as pd
        >>> data = pd.DataFrame({
        ...     'feature1': [1, 2, 3, 4, 5, 6],
        ...     'group': ['A', 'A', 'B', 'B', 'C', 'C']
        ... })

        # New default: DataFrame format (recommended)
        >>> results_df = perform_tukey_hsd_test(data, ['feature1'], 'group')
        >>> isinstance(results_df, pd.DataFrame)
        True

        # Legacy compatibility: String format (deprecated)
        >>> results_str = perform_tukey_hsd_test(data, ['feature1'], 'group', return_format="string")
        >>> isinstance(results_str, str)
        True

    Migration Guide:
        # Before (legacy string format)
        results = perform_tukey_hsd_test(data, features, groups)
        print(results)  # Was a formatted string

        # After - Option 1: Use DataFrame (recommended)
        results_df = perform_tukey_hsd_test(data, features, groups)
        print(results_df.to_string())  # Convert to string if needed

        # After - Option 2: Temporary compatibility mode
        results = perform_tukey_hsd_test(data, features, groups, return_format="string")
        print(results)  # Same as before, but deprecated
    """
    from statsmodels.stats.multicomp import pairwise_tukeyhsd

    results = []

    for feature in feature_columns:
        try:
            # Extract data for this feature and remove any NaN values
            valid_data = DataFrame({"value": data[feature], "group": data[class_column]}).dropna()

            if len(valid_data) < 3 or valid_data["group"].nunique() < 2:
                logger.warning(f"Insufficient data for Tukey HSD test on feature {feature}")
                continue

            # Perform Tukey's HSD test
            tukey = pairwise_tukeyhsd(
                endog=valid_data["value"],
                groups=valid_data["group"],
                alpha=alpha,
            )

            # Extract results for each comparison
            if tukey.pvalues is not None and tukey.confint is not None:
                for idx in range(len(tukey.pvalues)):
                    group1 = tukey.groupsunique[tukey._multicomp.pairindices[0][idx]]
                    group2 = tukey.groupsunique[tukey._multicomp.pairindices[1][idx]]

                    # Get data for both groups
                    group1_data = valid_data[valid_data["group"] == group1]["value"]
                    group2_data = valid_data[valid_data["group"] == group2]["value"]

                    # Calculate statistics
                    mean_group1, mean_group2 = np.mean(group1_data), np.mean(group2_data)
                    mean_diff = mean_group2 - mean_group1

                    # Prepare result dictionary
                    result_dict = {
                        "feature": feature,
                        "group1": group1,
                        "group2": group2,
                        "mean_group1": mean_group1,
                        "mean_group2": mean_group2,
                        "mean_diff": mean_diff,
                        "p_value": tukey.pvalues[idx],
                        "ci_lower": tukey.confint[idx][0],
                        "ci_upper": tukey.confint[idx][1],
                    }

                    # Add effect sizes and fold changes if requested
                    if include_effect_sizes:
                        # Calculate Cohen's d effect size
                        cohens_d = calculate_cohens_d(group1_data, group2_data)
                        result_dict["effect_size"] = cohens_d

                    # Calculate fold change
                    fold_change = calculate_fold_change(mean_group1, mean_group2, log2_transform)
                    result_dict["fold_change"] = fold_change

                    results.append(result_dict)

        except Exception:
            logger.exception("Error in Tukey HSD test for feature %s", feature)
            continue

    # Create result DataFrame and adjust p-values
    if results:
        result_df = pd.DataFrame(results)
        # Adjust p-values for multiple comparisons
        result_df["adj_p_value"] = adjust_p_values(result_df["p_value"], alpha)
    else:
        result_df = pd.DataFrame()

    logger.info(
        f"Completed Tukey HSD tests for {len(feature_columns)} features, generated {len(results)} pairwise comparisons"
    )

    # Handle return format (with backward compatibility)
    if return_format == "string":
        import warnings

        warnings.warn(
            "String return format for perform_tukey_hsd_test() is deprecated. "
            "DataFrame format is now the default and provides better programmatic access. "
            "Please update your code to use the DataFrame format. "
            "This compatibility mode will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _format_tukey_results_as_string(result_df)
    elif return_format == "dataframe":
        return result_df
    else:
        raise ValueError(f"Invalid return_format '{return_format}'. Must be 'dataframe' or 'string'.")


def _format_tukey_results_as_string(result_df: pd.DataFrame) -> str:
    """
    Format Tukey HSD results as a formatted string (legacy compatibility).

    Args:
        result_df: DataFrame containing Tukey HSD results

    Returns:
        Formatted string representation of the results
    """
    if result_df.empty:
        return "No significant results found in Tukey HSD analysis."

    # Create a formatted string representation
    output_lines = ["Tukey HSD Test Results", "=" * 50, ""]

    # Group by feature for better organization
    for feature in result_df["feature"].unique():
        feature_results = result_df[result_df["feature"] == feature]

        output_lines.append(f"Feature: {feature}")
        output_lines.append("-" * 30)

        for _, row in feature_results.iterrows():
            group1, group2 = row["group1"], row["group2"]
            p_val = row.get("adj_p_value", row.get("p_value", "N/A"))
            mean_diff = row.get("mean_diff", "N/A")

            # Format p-value
            p_str = f"{p_val:.6f}" if isinstance(p_val, int | float) else str(p_val)

            # Format mean difference
            diff_str = f"{mean_diff:.4f}" if isinstance(mean_diff, int | float) else str(mean_diff)

            # Add effect size if available
            effect_size_str = ""
            if "effect_size" in row and pd.notna(row["effect_size"]):
                effect_size_str = f" (Cohen's d: {row['effect_size']:.3f})"

            # Add fold change if available
            fold_change_str = ""
            if "fold_change" in row and pd.notna(row["fold_change"]):
                fold_change_str = f" (FC: {row['fold_change']:.3f})"

            significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""

            output_lines.append(
                f"  {group1} vs {group2}: "
                f"mean_diff={diff_str}, p={p_str}{significance}"
                f"{effect_size_str}{fold_change_str}"
            )

        output_lines.append("")  # Empty line between features

    # Add summary statistics
    total_comparisons = len(result_df)
    significant_05 = len(result_df[result_df.get("adj_p_value", result_df.get("p_value", pd.Series())) < 0.05])

    output_lines.extend([
        "Summary:",
        f"Total comparisons: {total_comparisons}",
        f"Significant (p < 0.05): {significant_05}",
        "",
        "Note: This string format is deprecated. Use DataFrame format for better programmatic access.",
    ])

    return "\n".join(output_lines)


def perform_student_t_test(
    data: DataFrame,
    feature_columns: list[str],
    class_column: str,
    alpha: float = 0.05,
    include_effect_sizes: bool = True,
    log2_transform: bool = False,
) -> list[dict[str, Any]]:
    """Perform Student's t-test for pairwise comparisons between classes.

    Conducts independent samples t-tests assuming equal variances between groups.
    For unequal variances, consider using Welch's t-test instead.

    Args:
        data: DataFrame containing the data to analyze
        feature_columns: List of feature column names to test
        class_column: Name of the column containing class labels
        alpha: Significance level for testing
        include_effect_sizes: Whether to calculate Cohen's d effect sizes
        log2_transform: Whether the data is log2 transformed

    Returns:
        List of dictionaries containing test results for each feature comparison

    Example:
        >>> data = pd.DataFrame({
        ...     'feature1': [1, 2, 3, 4, 5, 6],
        ...     'group': ['A', 'A', 'A', 'B', 'B', 'B']
        ... })
        >>> results = perform_student_t_test(data, ['feature1'], 'group')
    """
    results = _perform_pairwise_comparisons(
        data=data,
        feature_columns=feature_columns,
        class_column=class_column,
        test_func=_perform_student_t_test_core,
        alpha=alpha,
        include_effect_sizes=include_effect_sizes,
        log2_transform=log2_transform,
        equal_var=True,  # Student's t-test assumes equal variance
    )

    logger.info(
        f"Completed Student's t-tests for {len(feature_columns)} features, "
        f"generated {len(results)} pairwise comparisons"
    )
    return results


def perform_welch_t_test(
    data: DataFrame,
    feature_columns: list[str],
    class_column: str,
    alpha: float = 0.05,
    include_effect_sizes: bool = True,
    log2_transform: bool = False,
) -> list[dict[str, Any]]:
    """Perform Welch's t-test for pairwise comparisons between classes.

    Conducts Welch's t-test which does not assume equal variances between groups.
    This is more robust than Student's t-test when variances are unequal.

    Args:
        data: DataFrame containing the data to analyze
        feature_columns: List of feature column names to test
        class_column: Name of the column containing class labels
        alpha: Significance level for testing
        include_effect_sizes: Whether to calculate Cohen's d effect sizes
        log2_transform: Whether the data is log2 transformed (affects fold change calculation)

    Returns:
        List of dictionaries containing test results for each feature comparison

    Example:
        >>> data = pd.DataFrame({
        ...     'feature1': [1, 2, 3, 10, 11, 12],  # Different variances
        ...     'group': ['A', 'A', 'A', 'B', 'B', 'B']
        ... })
        >>> results = perform_welch_t_test(data, ['feature1'], 'group')
    """
    results = _perform_pairwise_comparisons(
        data=data,
        feature_columns=feature_columns,
        class_column=class_column,
        test_func=_perform_student_t_test_core,
        alpha=alpha,
        include_effect_sizes=include_effect_sizes,
        log2_transform=log2_transform,
        equal_var=False,  # Welch's t-test does not assume equal variance
    )

    logger.info(
        f"Completed Welch's t-tests for {len(feature_columns)} features, generated {len(results)} pairwise comparisons"
    )
    return results


def perform_independence_test(
    data: DataFrame,
    target_column: str,
    value_column: str,
    binary_split_column: Optional[str] = None,
) -> dict[str, list[dict[str, Union[str, float]]]]:
    """Perform independence tests for data analysis.

    Automatically selects the appropriate test based on data type:
    - Chi-square test for categorical data
    - T-test for numerical data

    Conducts tests with options for within-group and between-group comparisons.

    Args:
        data: DataFrame containing the data to analyze
        target_column: Column name for the grouping variable
        value_column: Column name for the values to compare
        binary_split_column: Optional column for binary grouping within target groups

    Returns:
        Dictionary containing within-group and between-group test results

    Example:
        >>> # Categorical example
        >>> data = pd.DataFrame({
        ...     'group': ['A', 'A', 'B', 'B'],
        ...     'outcome': ['success', 'failure', 'success', 'success'],
        ...     'gender': ['M', 'F', 'M', 'F']
        ... })
        >>> results = perform_independence_test(data, 'group', 'outcome', 'gender')

        >>> # Numerical example
        >>> data = pd.DataFrame({
        ...     'group': ['A', 'A', 'B', 'B'],
        ...     'value': [1.2, 2.3, 3.4, 4.5],
        ...     'gender': ['M', 'F', 'M', 'F']
        ... })
        >>> results = perform_independence_test(data, 'group', 'value', 'gender')
    """
    results: dict[str, list[dict[str, Union[str, float]]]] = {"within_group": [], "between_group": []}

    # Within-group tests (if binary split specified)
    if binary_split_column:
        binary_split_values = data[binary_split_column].unique()
        if len(binary_split_values) == 2:
            for group in sorted(data[target_column].unique()):
                group_data = data[data[target_column] == group]

                try:
                    result = _perform_group_comparison(
                        group_data,
                        binary_split_column,
                        value_column,
                        binary_split_values[0],
                        binary_split_values[1],
                    )

                    if result:
                        results["within_group"].append({"group": group, **result})

                except Exception:
                    logger.exception(f"Error in within-group test for {group}")
                    continue

    # Between-group tests
    groups = sorted(data[target_column].unique())
    for i, group1 in enumerate(groups):
        for group2 in groups[i + 1 :]:
            try:
                result = _perform_group_comparison(
                    data,
                    target_column,
                    value_column,
                    group1,
                    group2,
                )

                if result:
                    results["between_group"].append({"group1": group1, "group2": group2, **result})

            except Exception:
                logger.exception(f"Error in between-group test for {group1}-{group2}")
                continue

    logger.info(
        f"Completed independence tests: {len(results['within_group'])} within-group, "
        f"{len(results['between_group'])} between-group comparisons"
    )
    return results


def _perform_group_comparison(
    data: DataFrame,
    group_column: str,
    value_column: str,
    group1: Any,
    group2: Any,
) -> Optional[dict[str, Any]]:
    """Perform comparison between two groups, selecting appropriate test.

    Args:
        data: DataFrame containing the data
        group_column: Column containing group labels
        value_column: Column containing values to compare
        group1: First group label
        group2: Second group label

    Returns:
        Dictionary with test results or None if insufficient data
    """
    # Extract data for both groups
    values1 = data[data[group_column] == group1][value_column].dropna()
    values2 = data[data[group_column] == group2][value_column].dropna()

    if len(values1) == 0 or len(values2) == 0:
        return None

    # Check data type and perform appropriate test
    if pd.api.types.is_numeric_dtype(values1):
        # For numeric data, use t-test
        stat, pval = stats.ttest_ind(values1, values2)
        test_type = "t-test"
    else:
        # For categorical data, use chi-square
        # Need to use the full data subset for contingency table
        mask = data[group_column].isin([group1, group2])
        subset_data = data[mask]
        contingency = pd.crosstab(subset_data[group_column], subset_data[value_column])

        if contingency.size <= 1:
            return None

        result = stats.chi2_contingency(contingency)
        stat = result[0]
        pval = result[1]
        test_type = "chi-square"

    return {
        "statistic": float(stat),
        "p_value": float(pval),
        "test_type": test_type,
    }


# Backward compatibility alias
perform_chi_square_test = perform_independence_test
