"""Custom exception classes for the analysis module.

This module defines domain-specific exception classes that provide
clear error messages and context for various analysis operations.
"""


class AnalysisError(Exception):
    """Base exception for analysis-related errors."""

    pass


class DataValidationError(AnalysisError):
    """Exception raised when data validation fails."""

    pass


class StatisticalAnalysisError(AnalysisError):
    """Exception raised during statistical analysis operations."""

    pass


class ClusteringError(AnalysisError):
    """Exception raised during clustering operations."""

    pass


class ModelTrainingError(AnalysisError):
    """Exception raised during model training operations."""

    pass


class NormalizationError(AnalysisError):
    """Exception raised during data normalization operations."""

    pass


class ConfounderAnalysisError(AnalysisError):
    """Exception raised during confounder analysis operations."""

    pass


class GlycoworkIntegrationError(AnalysisError):
    """Exception raised during Glycowork library integration."""

    pass
