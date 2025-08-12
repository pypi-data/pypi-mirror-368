"""Project configuration management for analysis workflows.

This module provides comprehensive project configuration management including
dataclass definitions, interactive configuration creation, and file I/O operations
for maintaining consistent analysis parameters across projects.
"""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION CLASSES - Simplified but maintaining user API compatibility
# =============================================================================


@dataclass
class DataStructureConfig:
    """
    Configuration for flexible data structure mapping.
    Maintains external API compatibility while using simplified internals.

    Attributes:
        sample_column: Column name containing sample identifiers
        sample_type_column: Optional column name containing sample type information
        feature_prefix: Prefix to identify feature columns
        qc_identifier: Identifier for QC samples (string, callable, or list of strings)
        qc_detection_method: Method to detect QC samples ('contains', 'equals', etc.)
        metadata_columns: List of metadata column names
    """

    sample_column: str = "sample"
    sample_type_column: Optional[str] = None
    feature_prefix: str = "FT-"
    qc_identifier: Union[str, Callable, list[str]] = "QC"
    qc_detection_method: str = "contains"
    biological_sample_identifier: str = "Biological Sample"
    metadata_columns: list[str] = field(default_factory=list)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize configuration with dataclass defaults and optional overrides."""
        # Initialize with dataclass defaults first
        self.sample_column = kwargs.get("sample_column", "sample")
        self.sample_type_column = kwargs.get("sample_type_column")
        self.feature_prefix = kwargs.get("feature_prefix", "FT-")
        self.qc_identifier = kwargs.get("qc_identifier", "QC")
        self.qc_detection_method = kwargs.get("qc_detection_method", "contains")
        self.metadata_columns = kwargs.get("metadata_columns", [])
        self.biological_sample_identifier = kwargs.get("biological_sample_identifier", "Biological Sample")

        # Set any additional attributes for backward compatibility
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def identify_qc_samples(self, data: pd.DataFrame) -> pd.Series:
        """Identify QC samples using simplified logic adapted to isospec patterns."""
        if self.sample_type_column and self.sample_type_column in data.columns:
            # Use dedicated sample type column
            sample_values = data[self.sample_type_column]
        elif self.sample_column in data.columns:
            # Fall back to sample column
            sample_values = data[self.sample_column]
        else:
            raise ValueError(
                f"Neither sample type column '{self.sample_type_column}' nor sample column '{self.sample_column}' found in data"
            )

        # Use existing isospec-data-tools pattern for QC detection
        if callable(self.qc_identifier):
            return sample_values.apply(self.qc_identifier)  # type: ignore[no-any-return]
        elif isinstance(self.qc_identifier, list):
            return sample_values.isin(self.qc_identifier)
        else:
            # Default to standard isospec pattern
            return sample_values.str.contains(str(self.qc_identifier), na=False)

    def __repr__(self) -> str:
        attrs = vars(self)
        attr_str = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
        return f"{self.__class__.__name__}({attr_str})"


@dataclass
class StatisticalConfig:
    """
    Configuration for statistical thresholds and categories.
    Simplified from original while maintaining user API.
    """

    cv_threshold: float = 30.0
    cv_ranges: list[tuple[float, float, str]] = field(
        default_factory=lambda: [(0, 10, "<10%"), (10, 20, "10-20%"), (20, 30, "20-30%"), (30, float("inf"), ">30%")]
    )
    percentile_thresholds: tuple[float, float] = (33.0, 67.0)
    improvement_categories: list[tuple[float, float, str, str]] = field(
        default_factory=lambda: [
            (5, float("inf"), "Highly\nImproved\n(>5pp)", "darkgreen"),
            (2, 5, "Moderately\nImproved\n(2-5pp)", "green"),
            (0, 2, "Slightly\nImproved\n(0-2pp)", "lightgreen"),
            (-float("inf"), 0, "No\nImprovement\n(≤0pp)", "orange"),
        ]
    )
    missing_data_threshold: int = 0
    histogram_bins: dict[str, int] = field(
        default_factory=lambda: {"default": 20, "cv_distribution": 25, "abundance": 30, "improvement": 15}
    )
    effect_size_threshold: float = 1.2
    p_value_threshold: float = 0.05
    alpha_level: float = 0.05
    model_params: dict[str, Any] = field(
        default_factory=lambda: {
            "param_grids": {
                "rf": {
                    "n_estimators": [100, 200, 300],
                    "max_depth": [3, 5, 7, None],
                    "min_samples_split": [2, 5, 10],
                    "min_samples_leaf": [1, 2, 4],
                    "max_features": ["sqrt", "log2"],
                    "class_weight": ["balanced", "balanced_subsample"],
                },
                "svm": {
                    "C": [0.001, 0.01, 0.1, 1, 10, 100, 1000],
                    "kernel": ["rbf", "linear", "poly", "sigmoid"],
                    "gamma": ["scale", "auto", 0.0001, 0.001, 0.01, 0.1, 1, 10],
                    "class_weight": ["balanced", None],
                    "degree": [2, 3, 4],
                    "coef0": [0.0, 0.1, 0.5, 1.0],
                },
                "lr": {
                    "C": [0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000],
                    "penalty": ["l2"],
                    "solver": ["liblinear", "saga", "newton-cg", "lbfgs"],
                    "class_weight": ["balanced", None, {0: 0.7, 1: 0.3}, {0: 0.3, 1: 0.7}],
                    "max_iter": [5000, 10000],
                    "tol": [1e-5, 1e-4, 1e-3],
                    "warm_start": [True, False],
                    "fit_intercept": [True, False],
                },
            },
            "random_search_params": {
                "n_iter": 100,
                "refit": "roc_auc",
                "n_jobs": -1,
                "verbose": 0,
                "return_train_score": True,
            },
        }
    )


@dataclass
class VisualizationConfig:
    """
    Configuration for visual customization.
    Simplified from original complex implementation.
    """

    figure_layouts: dict[str, tuple[int, int]] = field(
        default_factory=lambda: {
            "missing_data": (18, 12),
            "imputation_impact": (15, 5),
            "concentration_variation": (15, 5),
            "final_summary": (15, 6),
            "comprehensive_impact": (18, 12),
            "abundance_classification": (15, 5),
            "cv_improvement": (15, 5),
            "cv_distribution_shift": (12, 5),
            "comprehensive_cv": (20, 12),
            "transformation_comparison": (12, 5),
            "feature_performance": (12, 10),
        }
    )
    subplot_arrangements: dict[str, tuple[int, int]] = field(
        default_factory=lambda: {
            "missing_data": (2, 3),
            "imputation_impact": (1, 3),
            "concentration_variation": (1, 3),
            "final_summary": (1, 3),
            "comprehensive_impact": (2, 3),
            "abundance_classification": (1, 3),
            "cv_improvement": (1, 3),
            "cv_distribution_shift": (1, 2),
            "comprehensive_cv": (2, 4),
            "transformation_comparison": (1, 2),
            "feature_performance": (2, 2),
        }
    )

    color_schemes: dict[str, dict[str, str]] = field(
        default_factory=lambda: {
            "sample_types": {"qc": "red", "biological": "blue", "blank": "gray"},
            "improvements": {"improved": "green", "not_improved": "orange"},
            "abundance_levels": {"low": "lightcoral", "medium": "lightyellow", "high": "lightgreen"},
            "outcomes": {"default_positive": "lightgreen", "default_negative": "lightcoral"},
        }
    )

    style_config: dict[str, Any] = field(
        default_factory=lambda: {
            "font_size": 10,
            "title_fontsize": 12,
            "color_palette": "husl",
            "grid_alpha": 0.3,
            "alpha": 0.7,
            "marker_size": 50,
            "line_width": 2,
            "bar_width": 0.35,
        }
    )


@dataclass
class TransformationPipelineConfig:
    """Configuration for transformation pipeline support."""

    transformations: dict[str, pd.DataFrame]
    cv_data: dict[str, np.ndarray]
    stage_names: list[str]
    stage_colors: dict[str, str] = field(default_factory=dict)
    stage_descriptions: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set defaults for pipeline configuration."""
        if not self.stage_names:
            self.stage_names = list(self.transformations.keys())

        if not self.stage_colors:
            default_colors = ["red", "orange", "green", "blue", "purple", "brown"]
            self.stage_colors = {
                stage: default_colors[i % len(default_colors)] for i, stage in enumerate(self.stage_names)
            }

        if not self.stage_descriptions:
            self.stage_descriptions = {stage: stage.replace("_", " ").title() for stage in self.stage_names}


@dataclass
class NormalizationConfig:
    """Configuration for normalization method definitions."""

    method_name: str = "Normalization"
    method_description: str = "Normalization method"
    method_abbreviation: str = "NORM"

    @classmethod
    def tan_config(cls) -> "NormalizationConfig":
        """Configuration for Total Abundance Normalization."""
        return cls(
            method_name="Total Abundance Normalization",
            method_description="Corrects for differences in sample concentration by normalizing to total abundance",
            method_abbreviation="TAN",
        )

    @classmethod
    def mqn_config(cls) -> "NormalizationConfig":
        """Configuration for Median Quotient Normalization."""
        return cls(
            method_name="Median Quotient Normalization",
            method_description="Corrects for systematic analytical variation using QC median reference",
            method_abbreviation="MQN",
        )


@dataclass
class PlottingConfig:
    """Legacy plotting configuration for backward compatibility"""

    figure_size: tuple[int, int] = (12, 8)
    font_size: int = 10
    color_palette: str = "husl"
    qc_color: str = "red"
    sample_color: str = "blue"
    improvement_color: str = "green"
    no_improvement_color: str = "orange"
    grid_alpha: float = 0.3

    def setup_style(self) -> None:
        """Apply consistent plotting style"""
        plt.style.use("default")
        sns.set_palette(self.color_palette)
        plt.rcParams["figure.figsize"] = self.figure_size
        plt.rcParams["font.size"] = self.font_size


# =============================================================================
# CONFIGURATION FACTORY - Maintains user API compatibility
# =============================================================================


class ConfigFactory:
    """Factory for creating default configuration sets."""

    def __init__(
        self,
        data_config: Optional[DataStructureConfig] = None,
        stats_config: Optional[StatisticalConfig] = None,
        viz_config: Optional[VisualizationConfig] = None,
    ) -> None:
        """Initialize ConfigFactory with optional custom configurations."""
        self.data_config = data_config or DataStructureConfig()
        self.stats_config = stats_config or StatisticalConfig(
            cv_threshold=30.0,
            percentile_thresholds=(33.0, 67.0),
            improvement_categories=[
                (10, float("inf"), "Highly\nImproved\n(>10pp)", "darkgreen"),
                (5, 10, "Moderately\nImproved\n(5-10pp)", "green"),
                (2, 5, "Slightly\nImproved\n(2-5pp)", "lightgreen"),
                (float("-inf"), 2, "No\nImprovement\n(≤2pp)", "orange"),
            ],
        )
        self.viz_config = viz_config or VisualizationConfig()

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary format.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "data_config": self.data_config.__dict__,
            "stats_config": self.stats_config.__dict__,
            "viz_config": self.viz_config.__dict__,
        }

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        """Save configuration to JSON file.

        Args:
            file_path: Path where to save the JSON configuration file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

        logger.info(f"Configuration saved to {file_path}")

    @classmethod
    def from_json(cls, file_path: Union[str, Path]) -> "ConfigFactory":
        """Load configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file

        Returns:
            ConfigFactory instance loaded from the file

        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path) as f:
                config_dict = json.load(f)

            data_config = DataStructureConfig(**config_dict["data_config"])
            stats_config = StatisticalConfig(**config_dict["stats_config"])
            viz_config = VisualizationConfig(**config_dict["viz_config"])

            logger.info(f"Configuration loaded from {file_path}")
            return cls(data_config, stats_config, viz_config)

        except json.JSONDecodeError:
            logger.exception(f"Invalid JSON in configuration file: {file_path}")
            raise

    @staticmethod
    def colaus_defaults(
        project_config: Optional[Any] = None,
    ) -> tuple[DataStructureConfig, StatisticalConfig, VisualizationConfig]:
        """
        Create default configurations for COLAUS study.
        Maintains original API while using simplified internals.
        """
        # Create simplified configs that work with isospec-data-tools patterns
        data_config = DataStructureConfig(
            sample_column=getattr(project_config, "sample_column", "sample"),
            sample_type_column="SampleType",
            feature_prefix=getattr(project_config, "prefix", "FT-"),
            qc_identifier="QC",
            qc_detection_method="contains",
            metadata_columns=[
                "Age (years)",
                "Body mass index",
                "Diabetes using FPG>=7.0 mmol/L (Y/N)",
                "Dyslipidemia",
                "HDL cholesterol (mmol/L)",
                "History of AMI",
                "History of CVD",
                "Hypertension (>=140/90 or ttt)",
                "Hypolipidemic drug ttt",
                "LDL cholesterol (mmol/L)",
                "Sex, numeric, 1=male, 0=female",
                "Total cholesterol (mmol/L)",
                "Triglycerides (mmol/L)",
                "Any CVD",
                "Any AMI",
                "Examination date, follow-up 1",
                "Do you still have your menses",
            ],
            lipid_vars=[
                "HDL cholesterol (mmol/L)",
                "LDL cholesterol (mmol/L)",
                "Total cholesterol (mmol/L)",
                "Triglycerides (mmol/L)",
                "Body mass index",
            ],
            effect_size_threshold=0.5,
            p_value_threshold=0.05,
            alpha_level=0.05,
            include_effect_sizes=True,
            log2_transform=False,
            multiple_comparison_method="fdr_bh",
        )

        stats_config = StatisticalConfig(
            cv_threshold=30.0,
            percentile_thresholds=(33.0, 67.0),
            improvement_categories=[
                (10, float("inf"), "Highly\nImproved\n(>10pp)", "darkgreen"),
                (5, 10, "Moderately\nImproved\n(5-10pp)", "green"),
                (2, 5, "Slightly\nImproved\n(2-5pp)", "lightgreen"),
                (float("-inf"), 2, "No\nImprovement\n(≤2pp)", "orange"),
            ],
        )

        viz_config = VisualizationConfig()

        return data_config, stats_config, viz_config


def create_project_config(
    data_config: Optional[DataStructureConfig] = None,
    stats_config: Optional[StatisticalConfig] = None,
    viz_config: Optional[VisualizationConfig] = None,
) -> ConfigFactory:
    """Create a new project configuration.

    Args:
        data_config: Optional custom data structure configuration
        stats_config: Optional custom statistical configuration
        viz_config: Optional custom visualization configuration

    Returns:
        ConfigFactory instance with specified or default configurations
    """
    return ConfigFactory(data_config=data_config, stats_config=stats_config, viz_config=viz_config)


def load_project_config(file_path: Union[str, Path]) -> ConfigFactory:
    """Load project configuration from a JSON file.

    Args:
        file_path: Path to the JSON configuration file

    Returns:
        ConfigFactory instance loaded from the file

    Raises:
        FileNotFoundError: If configuration file doesn't exist
        json.JSONDecodeError: If JSON file is malformed
    """
    return ConfigFactory.from_json(file_path)


def save_project_config(config: ConfigFactory, file_path: Union[str, Path]) -> None:
    """Save project configuration to a JSON file.

    Args:
        config: ConfigFactory instance to save
        file_path: Path where to save the configuration file
    """
    config.save_to_json(file_path)
