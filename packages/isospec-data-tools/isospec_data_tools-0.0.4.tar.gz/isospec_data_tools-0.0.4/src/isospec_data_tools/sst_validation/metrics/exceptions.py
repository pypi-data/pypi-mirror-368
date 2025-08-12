"""Custom exceptions for SST validation metrics.

This module defines custom exceptions used throughout the SST validation module
to provide more specific error handling and messaging.
"""


class MetricValidationError(Exception):
    """Base exception for all metric validation errors."""

    pass


class InputDataError(MetricValidationError):
    """Raised when input data fails validation requirements."""

    pass


class ThresholdError(MetricValidationError):
    """Raised when a metric value fails to meet the required threshold."""

    pass


class CalculationError(MetricValidationError):
    """Raised when a metric calculation fails."""

    pass


class FeatureMatchingError(MetricValidationError):
    """Raised when feature matching fails."""

    pass


class ConfigurationError(MetricValidationError):
    """Raised when validator configuration is invalid."""

    pass
