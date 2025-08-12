"""Base classes and interfaces for SST validation metrics.

This module provides the foundational classes for implementing System Suitability Testing (SST)
validation metrics. It defines the core interfaces and base implementations that specific
metric validators will extend.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

import pandas as pd


@dataclass
class BaseMetricResult:
    """Base class for storing metric validation results.

    This class serves as the foundation for all metric-specific result classes,
    providing common attributes and functionality for result storage and validation.

    Attributes:
        metric_name: Name of the metric
        passed: Whether the metric validation passed
        timestamp: When the validation was performed
        value: The calculated metric value
        threshold: The threshold used for validation
        details: Additional metric-specific details
        error: Error message if validation failed
    """

    metric_name: str
    passed: bool
    timestamp: datetime = field(default_factory=datetime.now)
    value: Optional[float] = None
    threshold: Optional[float] = None
    details: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


# Type variable for generic result type
R = TypeVar("R", bound=BaseMetricResult)


class BaseMetricValidator(Generic[R], ABC):
    """Abstract base class for metric validators.

    This class defines the interface that all metric validators must implement.
    It provides a consistent structure for implementing different validation metrics.

    Type Parameters:
        R: The specific result type this validator produces, must be a subclass
           of BaseMetricResult.
    """

    def __init__(self, name: str, threshold: float):
        """Initialize the metric validator.

        Args:
            name: Name of the metric
            threshold: Threshold value for pass/fail determination
        """
        self.name = name
        self.threshold = threshold

    @abstractmethod
    def validate(self, data: pd.DataFrame) -> R:
        """Validate the input data and produce a metric result.

        Args:
            data: Input DataFrame containing the data to validate

        Returns:
            A metric-specific result object containing validation results

        Raises:
            ValueError: If the input data is invalid or missing required columns
        """
        pass

    @abstractmethod
    def validate_input(self, data: pd.DataFrame) -> None:
        """Validate that the input data meets requirements.

        Args:
            data: Input DataFrame to validate

        Raises:
            ValueError: If the input data is invalid or missing required columns
        """
        pass

    @abstractmethod
    def calculate_metric(self, data: pd.DataFrame) -> float:
        """Calculate the metric value from the input data.

        Args:
            data: Input DataFrame containing the data to analyze

        Returns:
            The calculated metric value

        Raises:
            ValueError: If the metric cannot be calculated from the input data
        """
        pass


@dataclass
class ValidationResult:
    """Container for multiple metric validation results.

    This class aggregates results from multiple metric validations and provides
    methods for accessing and analyzing the combined results.

    Attributes:
        results: List of individual metric results
        timestamp: When the validation set was created
        metadata: Additional validation run metadata
    """

    results: list[BaseMetricResult]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Check if all metrics passed validation.

        Returns:
            True if all metrics passed, False otherwise
        """
        return all(result.passed for result in self.results)

    def get_result(self, metric_name: str) -> Optional[BaseMetricResult]:
        """Get the result for a specific metric.

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            The metric result if found, None otherwise
        """
        for result in self.results:
            if result.metric_name == metric_name:
                return result
        return None
