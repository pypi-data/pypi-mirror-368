"""Tests for base classes in SST validation module."""

import pandas as pd
import pytest

from isospec_data_tools.sst_validation.metrics.base import (
    BaseMetricResult,
    BaseMetricValidator,
)


class TestBaseMetricResult:
    """Test suite for BaseMetricResult class."""

    def test_base_metric_result_initialization(self) -> None:
        """Test that BaseMetricResult can be properly initialized."""
        with pytest.raises(TypeError):
            # Should raise TypeError as it's an abstract class
            BaseMetricResult()

    def test_base_metric_result_required_attributes(self) -> None:
        """Test that derived classes must implement required attributes."""

        class IncompleteResult(BaseMetricResult):
            pass

        with pytest.raises(TypeError):
            IncompleteResult()

    def test_base_metric_result_validation(self) -> None:
        """Test validation methods of BaseMetricResult."""

        class ValidResult(BaseMetricResult):
            def __init__(self):
                self.passed = True
                self.score = 0.95
                self.threshold = 0.9
                self.details = {"test": "value"}

        result = ValidResult()
        assert hasattr(result, "passed")
        assert hasattr(result, "score")
        assert hasattr(result, "threshold")
        assert hasattr(result, "details")


class TestBaseMetricValidator:
    """Test suite for BaseMetricValidator abstract class."""

    def test_base_validator_initialization(self) -> None:
        """Test that BaseMetricValidator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseMetricValidator(name="test", threshold=0.0)

    def test_validator_abstract_methods(self) -> None:
        """Test that derived classes must implement abstract methods."""

        class IncompleteValidator(BaseMetricValidator):
            pass

        with pytest.raises(TypeError):
            IncompleteValidator(name="test", threshold=0.0)

    def test_validator_concrete_implementation(self) -> None:
        """Test a concrete implementation of BaseMetricValidator."""

        class ConcreteValidator(BaseMetricValidator):
            def validate(self, data: pd.DataFrame) -> "BaseMetricResult":
                return MockResult()

            def validate_input(self, data: pd.DataFrame) -> None:
                pass

            def calculate_metric(self, data: pd.DataFrame) -> float:
                return 0.0

        validator = ConcreteValidator(name="test", threshold=0.0)
        assert isinstance(validator, BaseMetricValidator)

    def test_validator_input_validation(self) -> None:
        """Test input validation in BaseMetricValidator."""

        class ConcreteValidator(BaseMetricValidator):
            def validate(self, data: pd.DataFrame) -> "BaseMetricResult":
                if not isinstance(data, pd.DataFrame):
                    raise TypeError()
                return MockResult()

            def validate_input(self, data: pd.DataFrame) -> None:
                pass

            def calculate_metric(self, data: pd.DataFrame) -> float:
                return 0.0

        validator = ConcreteValidator(name="test", threshold=0.0)
        with pytest.raises(TypeError):
            validator.validate(None)

        result = validator.validate(pd.DataFrame())
        assert isinstance(result, BaseMetricResult)


class MockResult(BaseMetricResult):
    """Mock implementation of BaseMetricResult for testing."""

    def __init__(self):
        self.passed = True
        self.score = 1.0
        self.threshold = 0.8
        self.details = {}
