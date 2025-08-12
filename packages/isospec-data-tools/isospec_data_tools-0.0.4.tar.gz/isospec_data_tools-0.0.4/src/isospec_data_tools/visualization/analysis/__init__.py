"""Visualization module for analysis results.

This module provides comprehensive tools for visualization of analysis results.
"""

from isospec_data_tools.analysis.core.project_config import (
    ConfigFactory,
    DataStructureConfig,
    NormalizationConfig,
    StatisticalConfig,
    TransformationPipelineConfig,
    VisualizationConfig,
)
from isospec_data_tools.visualization.analysis.cluster_plots import (
    ClusteringPlotter,
)
from isospec_data_tools.visualization.analysis.confounder_plots import ConfounderPlotter
from isospec_data_tools.visualization.analysis.differential_plots import (
    DifferentialExpressionPlotter,
    ModelPlotter,
)
from isospec_data_tools.visualization.analysis.method_plot import (
    CVAnalyzer,
    MethodPlotter,
    PlotStyler,
    SignificanceMarker,
)
from isospec_data_tools.visualization.analysis.preprocessing_plots import (
    CVAnalysisPlotter,
    FeatureAbundanceClassifier,
    FeatureAnalyzer,
    PreprocessingPlotter,
)

__all__ = [
    "ConfounderPlotter",
    "CVAnalyzer",
    "MethodPlotter",
    "SignificanceMarker",
    "PlotStyler",
    "ClusteringPlotter",
    "DifferentialExpressionPlotter",
    "ModelPlotter",
    # Preprocessing visualization classes
    "PreprocessingPlotter",
    "FeatureAbundanceClassifier",
    "CVAnalysisPlotter",
    "ConfigFactory",
    "DataStructureConfig",
    "StatisticalConfig",
    "VisualizationConfig",
    "NormalizationConfig",
    "TransformationPipelineConfig",
    # Feature analysis
    "FeatureAnalyzer",
]
