from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


class ValidationDataError(ValueError):
    """Exception raised for errors in the validation data."""

    pass


class NoSensitivityResultsError(ValidationDataError):
    """Exception raised when no sensitivity results are found in validation data."""

    def __init__(self) -> None:
        super().__init__("No sensitivity results found in validation data")


class NoPeakAreaDataError(ValidationDataError):
    """Exception raised when no valid peak area data is found in validation results."""

    def __init__(self) -> None:
        super().__init__("No valid peak area data found in validation results")


class NoPeakShapeResultsError(ValidationDataError):
    """Exception raised when no peak shape results are found in validation data."""

    def __init__(self) -> None:
        super().__init__("No peak shape results found in validation data")


class NoAsymmetryDataError(ValidationDataError):
    """Exception raised when no valid asymmetry data is found in validation results."""

    def __init__(self) -> None:
        super().__init__("No valid asymmetry data found in validation results")


class NoMassAccuracyDataError(ValidationDataError):
    """Exception raised when no valid mass accuracy data is found in validation results."""

    def __init__(self) -> None:
        super().__init__("No valid mass accuracy data found in validation results")


class NoRetentionTimeDifferenceDataError(ValidationDataError):
    """Exception raised when no valid retention time difference data is found in validation results."""

    def __init__(self) -> None:
        super().__init__("No valid retention time difference data found in validation results")


class PyramidPlotGroupCountError(ValidationDataError):
    """Exception raised when pyramid plot is called with incorrect number of replicate groups."""

    def __init__(self) -> None:
        super().__init__("Pyramid plot requires exactly two replicate groups")


def _collect_peak_area_data(details: list[dict[str, Any]]) -> dict[str, list[tuple[str, float]]]:
    """Collect peak area data from validation details.

    Args:
        details: List of validation detail dictionaries

    Returns:
        Dictionary mapping replicate groups to lists of (compound_name, rsd) tuples
    """
    replicate_data: dict[str, list[tuple[str, float]]] = {}

    for detail in details:
        if detail["status"] == "not_found":
            continue

        compound_name = detail["compound"]
        replicate_group = detail.get("replicate_group", "Unknown")

        # Check for intensity_rsd in both root and metrics
        intensity_rsd = detail.get("intensity_rsd")
        if intensity_rsd is None and "metrics" in detail:
            intensity_rsd = detail["metrics"].get("intensity_rsd")

        if intensity_rsd is not None:
            rsd = float(intensity_rsd)
            if replicate_group not in replicate_data:
                replicate_data[replicate_group] = []
            replicate_data[replicate_group].append((compound_name, rsd))

    return replicate_data


def _create_dataframe(replicate_data: dict[str, list[tuple[str, float]]]) -> pd.DataFrame:
    """Create a pandas DataFrame from replicate data.

    Args:
        replicate_data: Dictionary mapping replicate groups to lists of (compound_name, rsd) tuples

    Returns:
        DataFrame with Compound, Replicate Group, and RSD (%) columns
    """
    data = []
    labels = []
    values = []

    for group, group_data in replicate_data.items():
        for compound, rsd in group_data:
            data.append(compound)
            labels.append(group)
            values.append(rsd)

    return pd.DataFrame({"Compound": data, "Replicate Group": labels, "RSD (%)": values})


def plot_peak_areas(validation_results: dict[str, Any], output_path: str | None = None) -> None:
    """Generate a bar plot of peak areas for each detected compound, grouped by replicate group.

    Args:
        validation_results: Dictionary containing validation results
        output_path: Optional path to save the plot
    """
    sensitivity_results = validation_results.get("sensitivity", {})
    if not sensitivity_results:
        raise NoSensitivityResultsError()

    # Collect peak area data
    replicate_data = _collect_peak_area_data(sensitivity_results.get("details", []))
    if not replicate_data:
        # Create an empty plot with a message
        plt.figure(figsize=(15, 8))
        plt.text(0.5, 0.5, "No valid peak area data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.title("Peak Intensity RSD by Compound and Replicate Group")
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, bbox_inches="tight")
        else:
            plt.show()
        plt.close()
        return

    # Create DataFrame for plotting
    df = _create_dataframe(replicate_data)

    # Create the plot
    plt.figure(figsize=(15, 8))

    # Plot bars using seaborn
    sns.barplot(data=df, x="Compound", y="RSD (%)", hue="Replicate Group", dodge=True)

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Intensity RSD (%)")
    plt.title("Peak Intensity RSD by Compound and Replicate Group")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


def _collect_asymmetry_data(details: list[dict[str, Any]]) -> dict[str, list[float]]:
    """Collect asymmetry values from validation details.

    Args:
        details: List of validation detail dictionaries

    Returns:
        Dictionary mapping replicate groups to lists of asymmetry values
    """
    replicate_data: dict[str, list[float]] = {}

    for detail in details:
        if detail["status"] == "not_found":
            continue

        # Extract asymmetry value if available (check both root and metrics)
        asymmetry = detail.get("asymmetry")
        if asymmetry is None and "metrics" in detail:
            asymmetry = detail["metrics"].get("asymmetry")

        if asymmetry is not None:
            replicate_group = detail.get("replicate_group", "Unknown")
            if replicate_group not in replicate_data:
                replicate_data[replicate_group] = []
            replicate_data[replicate_group].append(float(asymmetry))

    return replicate_data


def _create_empty_asymmetry_plot() -> None:
    """Create an empty plot with a message when no asymmetry data is available."""
    plt.figure(figsize=(12, 8))
    plt.text(0.5, 0.5, "No valid asymmetry data available", ha="center", va="center", fontsize=14)
    plt.axis("off")
    plt.title("Distribution of Peak Asymmetry Factors by Replicate Group")
    plt.tight_layout()


def _create_asymmetry_histogram(replicate_data: dict[str, list[float]]) -> None:
    """Create a histogram plot of asymmetry factors.

    Args:
        replicate_data: Dictionary mapping replicate groups to lists of asymmetry values
    """
    plt.figure(figsize=(12, 8))

    # Convert data to format suitable for seaborn
    data = []
    labels = []
    for group, values in replicate_data.items():
        data.extend(values)
        labels.extend([group] * len(values))

    # Create DataFrame for seaborn
    df = pd.DataFrame({"Asymmetry": data, "Replicate Group": labels})

    # Plot histogram using seaborn
    sns.histplot(data=df, x="Asymmetry", hue="Replicate Group", multiple="layer", alpha=0.5)

    plt.xlabel("Asymmetry Factor")
    plt.ylabel("Frequency")
    plt.title("Distribution of Peak Asymmetry Factors by Replicate Group")

    # Add vertical lines for acceptable range (0.9 - 1.35)
    plt.axvline(x=0.9, color="r", linestyle="--", label="Lower limit (0.9)")
    plt.axvline(x=1.35, color="r", linestyle="--", label="Upper limit (1.35)")

    plt.tight_layout()


def plot_asymmetry_histogram(validation_results: dict[str, Any], output_path: str | None = None) -> None:
    """Generate a histogram of asymmetry factors, with different colors for each replicate group.

    Args:
        validation_results: Dictionary containing validation results
        output_path: Optional path to save the plot
    """
    peak_shape_results = validation_results.get("peak_shape", {})
    if not peak_shape_results:
        raise NoPeakShapeResultsError()

    # Collect asymmetry values from the detailed results
    replicate_data = _collect_asymmetry_data(peak_shape_results.get("details", []))

    if not replicate_data:
        _create_empty_asymmetry_plot()
    else:
        _create_asymmetry_histogram(replicate_data)

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


def plot_mass_accuracy_distribution(validation_results: dict[str, Any], output_path: str | None = None) -> None:
    """Generate a histogram of mass accuracy values, with different colors for each replicate group.

    Args:
        validation_results: Dictionary containing validation results
        output_path: Optional path to save the plot
    """
    mass_accuracy_results = validation_results.get("mass_accuracy", {})
    if not mass_accuracy_results:
        raise NoMassAccuracyDataError()

    # Collect mass accuracy values from the detailed results, grouped by replicate
    replicate_data: dict[str, list[float]] = {}
    details = mass_accuracy_results.get("details", [])

    # Process each compound's data
    for detail in details:
        # Skip compounds that weren't found
        if detail["status"] == "not_found":
            continue

        # Extract mass accuracy value if available
        if "mass_error" in detail:
            replicate_group = detail.get("replicate_group", "Unknown")
            if replicate_group not in replicate_data:
                replicate_data[replicate_group] = []
            replicate_data[replicate_group].append(float(detail["mass_error"]))

    if not replicate_data:
        # Create an empty plot with a message
        plt.figure(figsize=(12, 8))
        plt.text(0.5, 0.5, "No valid mass accuracy data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.title("Distribution of Mass Accuracy by Replicate Group")
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, bbox_inches="tight")
        else:
            plt.show()
        plt.close()
        return

    # Create a single histogram plot
    plt.figure(figsize=(12, 8))

    # Convert data to format suitable for seaborn
    data = []
    labels = []
    for group, values in replicate_data.items():
        data.extend(values)
        labels.extend([group] * len(values))

    # Create DataFrame for seaborn
    df = pd.DataFrame({"Mass Accuracy": data, "Replicate Group": labels})

    # Plot histogram using seaborn
    sns.histplot(data=df, x="Mass Accuracy", hue="Replicate Group", multiple="layer", alpha=0.5)

    plt.xlabel("Mass Accuracy (ppm)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Mass Accuracy by Replicate Group")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
    else:
        plt.show()

    plt.close()


def _collect_rt_difference_data(details: list[dict[str, Any]]) -> tuple[list[str], list[str], list[float]]:
    """Collect retention time difference data from validation details.

    Args:
        details: List of validation detail dictionaries

    Returns:
        Tuple of (compound_names, group_names, time_differences)
    """
    compound_names = []
    group_names = []
    time_differences = []

    for detail in details:
        if detail["status"] == "not_found":
            continue

        compound_name = detail["compound"]
        time_diffs = detail.get("time_differences", {})

        for group_name, diff in time_diffs.items():
            compound_names.append(compound_name)
            group_names.append(group_name)
            time_differences.append(diff)

    return compound_names, group_names, time_differences


def plot_rt_differences_pyramid(validation_results: dict[str, Any], output_path: str | None = None) -> None:
    """Generate a symmetrical pyramid plot showing retention time differences from reference compound.

    The pyramid plot shows time differences as bars extending in opposite directions for each replicate group,
    creating a symmetrical pyramid shape. Compounds where the difference between groups exceeds the threshold
    are highlighted with a red outline.

    Args:
        validation_results: Dictionary containing validation results
        output_path: Optional path to save the plot
    """
    rt_diff_results = validation_results.get("retention_time_differences", {})
    if not rt_diff_results:
        raise NoRetentionTimeDifferenceDataError()

    # Collect data
    compound_names, group_names, time_diffs = _collect_rt_difference_data(rt_diff_results.get("details", []))

    if not compound_names:
        # Create an empty plot with a message
        plt.figure(figsize=(12, 8))
        plt.text(0.5, 0.5, "No valid retention time difference data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.title("Retention Time Differences Pyramid Plot")
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, bbox_inches="tight")
        else:
            plt.show()
        plt.close()
        return

    # Create DataFrame for plotting
    df = pd.DataFrame({
        "Compound": compound_names,
        "Replicate Group": group_names,
        "Time Difference (min)": [abs(x) for x in time_diffs],
    })

    # Calculate differences between groups for each compound
    group_differences = df.pivot_table(index="Compound", columns="Replicate Group", values="Time Difference (min)")
    groups = df["Replicate Group"].unique()
    if len(groups) != 2:
        raise PyramidPlotGroupCountError()

    group_differences["Between_Group_Diff"] = abs(group_differences[groups[0]] - group_differences[groups[1]])

    # Get threshold from validation results
    threshold = rt_diff_results.get("summary", {}).get(
        "max_difference_threshold", 0.01
    )  # Default to 0.01 if not specified

    # Identify compounds exceeding threshold
    compounds_exceeding = group_differences[group_differences["Between_Group_Diff"] > threshold].index

    # Sort compounds by their mean absolute time difference
    compound_means = df.groupby("Compound")["Time Difference (min)"].mean().sort_values(ascending=False)
    df["Compound"] = pd.Categorical(df["Compound"], categories=compound_means.index, ordered=True)

    # Split data by replicate group
    group1_data = df[df["Replicate Group"] == groups[0]].copy()
    group2_data = df[df["Replicate Group"] == groups[1]].copy()

    # Create the pyramid plot
    plt.figure(figsize=(15, 10))

    # Create the main axis
    ax = plt.gca()

    # Plot bars for first group (left side, negative values)
    bars1 = ax.barh(
        y=group1_data["Compound"],
        width=-group1_data["Time Difference (min)"],
        color=[
            "#FF0000" if compound in compounds_exceeding else "#2ecc71" for compound in group1_data["Compound"]
        ],  # Red if exceeding, else Green
        alpha=0.8,
        label=groups[0],
    )

    # Plot bars for second group (right side, positive values)
    bars2 = ax.barh(
        y=group2_data["Compound"],
        width=group2_data["Time Difference (min)"],
        color=[
            "#FF0000" if compound in compounds_exceeding else "#e67e22" for compound in group2_data["Compound"]
        ],  # Red if exceeding, else Orange
        alpha=0.8,
        label=groups[1],
    )

    # Add annotations for compounds exceeding threshold
    for bar1, _ in zip(bars1, bars2, strict=False):
        compound = bar1.get_y()
        if compound in compounds_exceeding:
            # Add annotation with the difference value
            diff_value = group_differences.loc[compound, "Between_Group_Diff"]
            ax.annotate(
                f"Δ = {diff_value:.2f} min",
                xy=(max(ax.get_xlim()) * 0.5, compound),  # Position at 50% of max x
                xytext=(5, 0),  # Small offset
                textcoords="offset points",
                va="center",
                color="red",
                fontweight="bold",
            )

    # Customize the plot
    plt.title(
        f"Retention Time Differences from Reference Compound\n(Red bars: difference between groups > {threshold:.2f} min)"
    )

    # Set up the axis
    max_diff = max(df["Time Difference (min)"].max(), 0.2)  # At least 0.2 for visibility
    max_rounded = np.ceil(max_diff * 1.2 * 10) / 10  # Round up to nearest 0.1

    # Create tick values (positive numbers for both sides)
    tick_values = np.linspace(0, max_rounded, 5)  # 5 ticks on each side

    # Set up x-axis with both negative and positive ticks
    ax.set_xlim(-max_rounded, max_rounded)

    # Create custom tick labels that show positive values on both sides
    tick_positions = np.concatenate([-tick_values[1:][::-1], tick_values])
    tick_labels = [f"{abs(x):.1f}" for x in tick_positions]  # Show one decimal place
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels)

    # Add labels
    ax.set_xlabel("Time Difference (min)")

    # Add grid for better readability
    ax.grid(True, linestyle="--", alpha=0.3, zorder=0)

    # Add vertical line at x=0
    ax.axvline(x=0, color="black", linestyle="-", linewidth=0.5, zorder=1)

    # Move legend to the right side
    ax.legend(title="Replicate Group", bbox_to_anchor=(1.15, 1), loc="upper left")

    # Add reference compound information
    reference = rt_diff_results.get("summary", {}).get("reference_compound", "Unknown")
    plt.figtext(0.02, 0.02, f"Reference compound: {reference}\nThreshold: {threshold:.2f} min", fontsize=10)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
