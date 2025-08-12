"""SST validation metrics package.

This package provides the core functionality for System Suitability Testing (SST)
validation metrics in mass spectrometry data analysis.
"""

from .base import (
    BaseMetricResult,
    BaseMetricValidator,
    ValidationResult,
)
from .exceptions import (
    CalculationError,
    ConfigurationError,
    FeatureMatchingError,
    InputDataError,
    MetricValidationError,
    ThresholdError,
)
from .utils import (
    find_matching_features,
    format_error_message,
    initialize_validation_result,
    validate_input_data,
)

__all__ = [
    # Base classes
    "BaseMetricResult",
    "BaseMetricValidator",
    "ValidationResult",
    # Utility functions
    "initialize_validation_result",
    "find_matching_features",
    "validate_input_data",
    "format_error_message",
    # Exceptions
    "MetricValidationError",
    "InputDataError",
    "ThresholdError",
    "CalculationError",
    "FeatureMatchingError",
    "ConfigurationError",
]
