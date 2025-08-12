"""Analysis module for data normalization and method evaluation.

This module provides comprehensive tools for data wrangling operations and
statistical analysis including normalization, filtering, imputation, and
visualization of analytical results.

The module is organized into modular domains:
- core: Basic statistical building blocks
- preprocessing: Data normalization and transformation functions
- specialized: Domain-specific analysis tools (ANCOVA, confounders, glycowork)
- modeling: Machine learning utilities (clustering, classification)
"""

# Import from specialized domains for direct access
# Import backward compatibility wrappers
from isospec_data_tools.analysis.classifiers import ModelTrainer as LegacyModelTrainer
from isospec_data_tools.analysis.clustering import ClusterAnalyzer as LegacyClusterAnalyzer
from isospec_data_tools.analysis.confounder_analyzer import ConfounderAnalyzer as LegacyConfounderAnalyzer
from isospec_data_tools.analysis.core.multiple_comparisons import adjust_p_values

# Import project configuration functions
from isospec_data_tools.analysis.core.project_config import (
    DataStructureConfig,
    NormalizationConfig,
    StatisticalConfig,
    VisualizationConfig,
    create_project_config,
    load_project_config,
    save_project_config,
)

# Import core statistical functions for direct access
from isospec_data_tools.analysis.core.statistical_tests import (
    perform_chi_square_test,
    perform_independence_test,
    perform_student_t_test,
    perform_tukey_hsd_test,
    perform_welch_t_test,
)
from isospec_data_tools.analysis.glycowork_wrapper import GlycoworkAnalyzer as LegacyGlycoworkAnalyzer
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer

# Import preprocessing functions directly (no wrapper classes)
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
from isospec_data_tools.analysis.specialized.ancova_analysis import ANCOVAAnalyzer
from isospec_data_tools.analysis.specialized.confounder_analysis import ConfounderAnalyzer
from isospec_data_tools.analysis.specialized.glycowork_integration import GlycoworkAnalyzer
from isospec_data_tools.analysis.utils.data_helpers import get_feature_columns

__all__ = [
    # Specialized domain classes
    "ANCOVAAnalyzer",
    "ConfounderAnalyzer",
    "GlycoworkAnalyzer",
    "ClusterAnalyzer",
    "ModelTrainer",
    # Specialized config classes
    "DataStructureConfig",
    "NormalizationConfig",
    "StatisticalConfig",
    "VisualizationConfig",
    # Preprocessing functions
    "total_abundance_normalization",
    "median_quotient_normalization",
    "filter_data_matrix_samples",
    "impute_missing_values",
    "join_sample_metadata",
    "replace_column_values",
    "log2_transform_numeric",
    "encode_categorical_column",
    "filter_data_by_column_value",
    "adjust_p_values",
    # Core statistical functions
    "perform_tukey_hsd_test",
    "perform_student_t_test",
    "perform_welch_t_test",
    "perform_chi_square_test",
    "perform_independence_test",
    # Project configuration
    "create_project_config",
    "load_project_config",
    "save_project_config",
    # Data helpers
    "get_feature_columns",
    # Legacy compatibility (deprecated)
    "LegacyModelTrainer",
    "LegacyClusterAnalyzer",
    "LegacyConfounderAnalyzer",
    "LegacyGlycoworkAnalyzer",
]
